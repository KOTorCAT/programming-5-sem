"""
Основное приложение для отслеживания курсов валют с использованием паттерна Наблюдатель
"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Callable
import logging

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.options import define, options

from config import (
    API_CONFIG,
    CURRENCIES_TO_TRACK,
    SERVER_CONFIG,
    WEBSOCKET_CONFIG
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Определение опций командной строки
define("port", default=SERVER_CONFIG["port"], help="Порт для запуска сервера")
define("host", default=SERVER_CONFIG["host"], help="Хост для запуска сервера")
define("debug", default=SERVER_CONFIG["debug"], help="Режим отладки")
define("test_mode", default=False, help="Тестовый режим (ускоренные обновления)")


# ========== Интерфейсы паттерна Наблюдатель ==========
class ObserverProtocol:
    """Протокол для наблюдателя"""
    async def update(self, data: Dict[str, Any]) -> None:
        """Метод обновления данных"""
        raise NotImplementedError


class SubjectProtocol:
    """Протокол для субъекта"""
    def attach(self, observer: ObserverProtocol) -> None:
        """Подписать наблюдателя"""
        raise NotImplementedError
    
    def detach(self, observer: ObserverProtocol) -> None:
        """Отписать наблюдателя"""
        raise NotImplementedError
    
    async def notify(self, data: Dict[str, Any]) -> None:
        """Уведомить всех наблюдателей"""
        raise NotImplementedError


# ========== Реализация Субъекта ==========
class CurrencyRateSubject(SubjectProtocol):
    """
    Субъект (Subject) для отслеживания курсов валют.
    Отслеживает изменения курсов и уведомляет наблюдателей.
    """
    
    def __init__(self, test_mode: bool = False) -> None:
        """Инициализация субъекта"""
        self._observers: Set[WebSocketHandler] = set()
        self._rates_cache: Dict[str, Dict[str, Any]] = {}
        self._previous_rates: Dict[str, Dict[str, Any]] = {}
        self._http_client = AsyncHTTPClient()
        self._test_mode = test_mode
        
        logger.info("CurrencyRateSubject initialized")
        if test_mode:
            logger.info("Test mode enabled - using accelerated update intervals")
    
    def attach(self, observer: WebSocketHandler) -> None:
        """Подписать нового наблюдателя"""
        if observer not in self._observers:
            self._observers.add(observer)
            logger.info(f"Observer attached. Total observers: {len(self._observers)}")
    
    def detach(self, observer: WebSocketHandler) -> None:
        """Отписать наблюдателя"""
        if observer in self._observers:
            self._observers.remove(observer)
            logger.info(f"Observer detached. Total observers: {len(self._observers)}")
    
    async def notify(self, data: Dict[str, Any]) -> None:
        """Уведомить всех наблюдателей об изменении"""
        if not self._observers:
            logger.debug("No observers to notify")
            return
        
        # Создаем копию списка наблюдателей для безопасной итерации
        observers_copy = list(self._observers)
        
        # Рассылаем сообщение всем наблюдателям
        message_json = json.dumps(data, ensure_ascii=False)
        
        notification_tasks = []
        for observer in observers_copy:
            if hasattr(observer, 'write_message'):
                try:
                    # Для WebSocketHandler используем write_message
                    notification_tasks.append(
                        observer.write_message(message_json)
                    )
                except Exception as e:
                    logger.error(f"Failed to notify WebSocket observer: {e}")
            elif hasattr(observer, 'update'):
                # Для обычных наблюдателей используем метод update
                try:
                    notification_tasks.append(
                        asyncio.create_task(observer.update(data))
                    )
                except Exception as e:
                    logger.error(f"Failed to notify observer: {e}")
        
        # Ждем завершения всех уведомлений
        if notification_tasks:
            await asyncio.gather(*notification_tasks, return_exceptions=True)
    
    def get_current_rates(self) -> Dict[str, Dict[str, Any]]:
        """Получить текущие курсы валют"""
        return self._rates_cache.copy()
    
    def get_previous_rates(self) -> Dict[str, Dict[str, Any]]:
        """Получить предыдущие курсы валют"""
        return self._previous_rates.copy()
    
    async def fetch_rates_from_api(self) -> Optional[Dict[str, Any]]:
        """Запросить курсы валют с API Центробанка"""
        try:
            request = HTTPRequest(
                API_CONFIG["url"],
                connect_timeout=10,
                request_timeout=15
            )
            response = await self._http_client.fetch(request)
            
            if response.code == 200:
                data = json.loads(response.body.decode('utf-8'))
                logger.info(f"Successfully fetched rates from API at {data.get('Date', 'N/A')}")
                return data
            else:
                logger.error(f"API request failed with status: {response.code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching rates from API: {e}")
            return None
    
    async def check_for_rate_changes(self) -> None:
        """Проверить изменения курсов валют"""
        logger.debug("Checking for rate changes...")
        
        # Сохраняем предыдущие курсы для сравнения
        self._previous_rates = self._rates_cache.copy()
        
        # Получаем данные с API
        api_data = await self.fetch_rates_from_api()
        
        if not api_data:
            logger.warning("No data received from API")
            return
        
        # Извлекаем валюты для отслеживания
        new_rates = {}
        changes = []
        
        for currency_code in CURRENCIES_TO_TRACK:
            if currency_code in api_data.get("Valute", {}):
                currency_data = api_data["Valute"][currency_code]
                new_rates[currency_code] = {
                    "code": currency_code,
                    "name": currency_data.get("Name", currency_code),
                    "value": currency_data.get("Value", 0.0),
                    "previous": currency_data.get("Previous", 0.0),
                    "nominal": currency_data.get("Nominal", 1),
                    "timestamp": api_data.get("Date", "")
                }
        
        # Сравниваем с кэшем
        for currency_code, currency_info in new_rates.items():
            old_info = self._rates_cache.get(currency_code)
            new_value = currency_info["value"]
            
            if old_info is None:
                # Новая валюта
                change_info = {
                    "code": currency_code,
                    "name": currency_info["name"],
                    "new_rate": new_value,
                    "old_rate": None,
                    "change": 0.0,
                    "change_percent": 0.0,
                    "type": "new",
                    "nominal": currency_info["nominal"]
                }
                changes.append(change_info)
                logger.info(f"New currency added: {currency_code} = {new_value} RUB")
                
            else:
                old_value = old_info["value"]
                change_amount = new_value - old_value
                
                # Проверяем значимость изменения (больше 0.001 для избежания float ошибок)
                if abs(change_amount) > 0.001:
                    change_percent = (change_amount / old_value) * 100 if old_value != 0 else 0
                    
                    change_info = {
                        "code": currency_code,
                        "name": currency_info["name"],
                        "new_rate": new_value,
                        "old_rate": old_value,
                        "change": change_amount,
                        "change_percent": change_percent,
                        "type": "increase" if change_amount > 0 else "decrease",
                        "nominal": currency_info["nominal"]
                    }
                    changes.append(change_info)
                    
                    logger.info(
                        f"Rate changed: {currency_code} {old_value:.4f} → {new_value:.4f} "
                        f"(Δ {change_amount:+.4f}, {change_percent:+.2f}%)"
                    )
        
        # Обновляем кэш
        self._rates_cache = new_rates
        
        # Если есть изменения - уведомляем наблюдателей
        if changes:
            message = {
                "type": "rates_updated",
                "timestamp": datetime.now().isoformat(),
                "api_timestamp": api_data.get("Date", ""),
                "changes": changes,
                "all_rates": {
                    code: info["value"] 
                    for code, info in self._rates_cache.items()
                }
            }
            
            await self.notify(message)
            logger.info(f"Notified {len(self._observers)} observers about {len(changes)} changes")
        else:
            logger.debug("No significant rate changes detected")
    
    async def simulate_rate_change(self) -> None:
        """Имитация изменения курса для тестирования"""
        logger.info("Simulating rate change for testing...")
        
        # Создаем тестовые изменения
        test_changes = []
        
        for currency_code in CURRENCIES_TO_TRACK[:3]:  # Только первые 3 валюты
            current_info = self._rates_cache.get(currency_code)
            
            if current_info:
                old_value = current_info["value"]
                # Имитируем небольшое изменение (±1%)
                change_percent = 1.0 if currency_code == "USD" else -0.5
                new_value = old_value * (1 + change_percent / 100)
                change_amount = new_value - old_value
                
                # Обновляем кэш
                self._rates_cache[currency_code]["value"] = new_value
                
                change_info = {
                    "code": currency_code,
                    "name": current_info["name"],
                    "new_rate": new_value,
                    "old_rate": old_value,
                    "change": change_amount,
                    "change_percent": change_percent,
                    "type": "increase" if change_amount > 0 else "decrease",
                    "nominal": current_info["nominal"],
                    "simulated": True
                }
                test_changes.append(change_info)
                
                logger.info(
                    f"Simulated change: {currency_code} {old_value:.4f} → {new_value:.4f} "
                    f"(Δ {change_amount:+.4f}, {change_percent:+.2f}%)"
                )
        
        if test_changes:
            message = {
                "type": "rates_updated",
                "timestamp": datetime.now().isoformat(),
                "api_timestamp": datetime.now().isoformat(),
                "changes": test_changes,
                "all_rates": {
                    code: info["value"] 
                    for code, info in self._rates_cache.items()
                },
                "simulated": True
            }
            
            await self.notify(message)
            logger.info(f"Notified {len(self._observers)} observers about simulated changes")


# ========== Реализация Наблюдателя (WebSocket) ==========
class CurrencyWebSocketHandler(WebSocketHandler, ObserverProtocol):
    """
    Наблюдатель (Observer) в виде WebSocket соединения.
    Каждое подключение - отдельный наблюдатель.
    """
    
    def initialize(self, subject: CurrencyRateSubject) -> None:
        """Инициализация обработчика WebSocket"""
        self.subject = subject
        self.client_id = str(uuid.uuid4())[:8]  # Короткий уникальный ID
        self.connected_at = datetime.now()
        self.message_count = 0
        self.subscribed_currencies = set(CURRENCIES_TO_TRACK)  # Подписаны на все валюты
        
        logger.info(f"Initialized WebSocket handler for client {self.client_id}")
    
    def check_origin(self, origin: str) -> bool:
        """Проверка origin для CORS"""
        return True  # В продакшене нужно настроить правильно
    
    def open(self) -> None:
        """Вызывается при установке WebSocket соединения"""
        logger.info(f"WebSocket connection opened: {self.client_id}")
        
        # Регистрируем как наблюдателя
        self.subject.attach(self)
        
        # Отправляем приветственное сообщение
        welcome_message = {
            "type": "welcome",
            "client_id": self.client_id,
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to Currency Rate Observer",
            "currencies": CURRENCIES_TO_TRACK,
            "current_rates": self.subject.get_current_rates()
        }
        
        try:
            self.write_message(json.dumps(welcome_message, ensure_ascii=False))
            logger.info(f"Sent welcome message to client {self.client_id}")
        except Exception as e:
            logger.error(f"Failed to send welcome message to {self.client_id}: {e}")
    
    async def update(self, data: Dict[str, Any]) -> None:
        """Метод обновления данных (реализация ObserverProtocol)"""
        try:
            # Проверяем, интересует ли клиента эта валюта
            if "changes" in data:
                # Фильтруем изменения по подписанным валютам
                filtered_changes = [
                    change for change in data["changes"]
                    if change["code"] in self.subscribed_currencies
                ]
                
                if filtered_changes:
                    # Создаем отфильтрованное сообщение
                    filtered_data = data.copy()
                    filtered_data["changes"] = filtered_changes
                    filtered_data["client_id"] = self.client_id
                    
                    message_json = json.dumps(filtered_data, ensure_ascii=False)
                    self.write_message(message_json)
                    self.message_count += 1
                    
                    if self.message_count % 10 == 0:
                        logger.debug(f"Sent {self.message_count} messages to {self.client_id}")
        except Exception as e:
            logger.error(f"Failed to update client {self.client_id}: {e}")
    
    def on_message(self, message: str) -> None:
        """Обработка входящих сообщений от клиента"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            logger.debug(f"Message from {self.client_id}: {message_type}")
            
            if message_type == "subscribe":
                # Подписка на определенные валюты
                currencies = data.get("currencies", [])
                if currencies == "all":
                    self.subscribed_currencies = set(CURRENCIES_TO_TRACK)
                else:
                    self.subscribed_currencies = set(
                        c for c in currencies if c in CURRENCIES_TO_TRACK
                    )
                
                response = {
                    "type": "subscription_updated",
                    "currencies": list(self.subscribed_currencies),
                    "timestamp": datetime.now().isoformat()
                }
                self.write_message(json.dumps(response, ensure_ascii=False))
                logger.info(f"Client {self.client_id} subscribed to {list(self.subscribed_currencies)}")
                
            elif message_type == "get_rates":
                # Запрос текущих курсов
                response = {
                    "type": "current_rates",
                    "rates": self.subject.get_current_rates(),
                    "timestamp": datetime.now().isoformat()
                }
                self.write_message(json.dumps(response, ensure_ascii=False))
                
            elif message_type == "ping":
                # Ответ на ping
                response = {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat(),
                    "client_id": self.client_id
                }
                self.write_message(json.dumps(response, ensure_ascii=False))
                
            elif message_type == "simulate_change":
                # Запрос на имитацию изменения (для тестов)
                if options.test_mode:
                    IOLoop.current().add_callback(self.subject.simulate_rate_change)
                    response = {
                        "type": "simulation_started",
                        "message": "Rate change simulation started",
                        "timestamp": datetime.now().isoformat()
                    }
                    self.write_message(json.dumps(response, ensure_ascii=False))
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from {self.client_id}: {e}")
            error_response = {
                "type": "error",
                "message": "Invalid JSON format",
                "timestamp": datetime.now().isoformat()
            }
            self.write_message(json.dumps(error_response))
        except Exception as e:
            logger.error(f"Error processing message from {self.client_id}: {e}")
    
    def on_close(self) -> None:
        """Вызывается при закрытии соединения"""
        logger.info(f"WebSocket connection closed: {self.client_id}")
        
        # Отписываемся от субъекта
        self.subject.detach(self)
        
        duration = (datetime.now() - self.connected_at).total_seconds()
        logger.info(
            f"Client {self.client_id} was connected for {duration:.1f} seconds, "
            f"received {self.message_count} messages"
        )


# ========== HTTP Обработчики ==========
class MainHandler(RequestHandler):
    """Главная страница"""
    
    def initialize(self, subject: CurrencyRateSubject) -> None:
        self.subject = subject
    
    def get(self) -> None:
        """Отображение главной страницы"""
        current_rates = self.subject.get_current_rates()
        
        self.render(
            "templates/index.html",
            client_id="N/A",
            currencies=CURRENCIES_TO_TRACK,
            current_rates=current_rates,
            port=options.port,
            host=options.host,
            test_mode=options.test_mode,
            json=json  # Эта строка может быть проблемой
        )


class APIDocumentationHandler(RequestHandler):
    """Документация API"""
    
    def get(self) -> None:
        self.write("""
        <h1>Currency Observer API</h1>
        <p>WebSocket endpoint: ws://localhost:8888/ws</p>
        <p>Available WebSocket messages:</p>
        <ul>
            <li><code>{"type": "subscribe", "currencies": ["USD", "EUR"]}</code></li>
            <li><code>{"type": "get_rates"}</code></li>
            <li><code>{"type": "ping"}</code></li>
        </ul>
        """)


class HealthCheckHandler(RequestHandler):
    """Проверка здоровья приложения"""
    
    def initialize(self, subject: CurrencyRateSubject) -> None:
        self.subject = subject
    
    def get(self) -> None:
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "observers_count": len(self.subject._observers),
            "tracked_currencies": CURRENCIES_TO_TRACK,
            "rates_count": len(self.subject.get_current_rates())
        }
        self.write(status)


# ========== Настройка и запуск приложения ==========
def make_app(subject: CurrencyRateSubject) -> Application:
    """Создание и настройка приложения Tornado"""
    
    # Настраиваем маршруты с переданным subject
    return Application(
        [
            (r"/", MainHandler, {"subject": subject}),
            (r"/ws", CurrencyWebSocketHandler, {"subject": subject}),
            (r"/api/docs", APIDocumentationHandler),
            (r"/health", HealthCheckHandler, {"subject": subject}),
            (r"/static/(.*)", StaticFileHandler, {"path": "static"}),
        ],
        template_path=".",
        debug=options.debug,
        websocket_ping_interval=WEBSOCKET_CONFIG["ping_interval"],
        websocket_ping_timeout=WEBSOCKET_CONFIG["ping_timeout"],
        websocket_max_message_size=WEBSOCKET_CONFIG["max_message_size"],
        autoreload=options.debug
    )


async def main() -> None:
    """Основная функция запуска приложения"""
    
    # Парсим аргументы командной строки
    options.parse_command_line()
    
    logger.info("Starting Currency Rate Observer Server...")
    logger.info(f"Server: {options.host}:{options.port}")
    logger.info(f"Debug mode: {options.debug}")
    logger.info(f"Test mode: {options.test_mode}")
    logger.info(f"Tracking currencies: {CURRENCIES_TO_TRACK}")
    
    # СОЗДАЕМ SUBJECT ДО СОЗДАНИЯ ПРИЛОЖЕНИЯ
    subject = CurrencyRateSubject(test_mode=options.test_mode)
    
    # Создаем приложение с готовым subject
    app = make_app(subject)
    
    # Запускаем сервер
    app.listen(options.port, options.host)
    logger.info(f"Server started at http://{options.host}:{options.port}")
    
    # Настраиваем интервал обновления
    update_interval = (
        API_CONFIG["poll_interval_ms"] 
        if options.test_mode 
        else API_CONFIG["update_interval_ms"]
    )
    
    logger.info(f"Update interval: {update_interval/1000} seconds")
    
    # Запускаем периодическую проверку курсов
    scheduler = PeriodicCallback(
        lambda: IOLoop.current().add_callback(subject.check_for_rate_changes),
        update_interval
    )
    scheduler.start()
    
    # Запускаем начальную проверку
    await subject.check_for_rate_changes()
    
    logger.info("Currency Rate Observer is ready!")
    
    # Бесконечный цикл
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    finally:
        scheduler.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")