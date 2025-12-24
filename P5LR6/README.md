
## Описание

Приложение для отслеживания изменений курсов валют в реальном времени с использованием паттерна проектирования "Наблюдатель". Сервер периодически опрашивает API Центробанка.

## Архитектура

### Паттерн "Наблюдатель"
- **Субъект (Subject)**: `CurrencyRateSubject` - отслеживает изменения курсов валют
- **Наблюдатель (Observer)**: `CurrencyWebSocketHandler` - WebSocket обработчик для каждого клиента

### Технологический стек
- **Веб-сервер**: Tornado (асинхронный)
- **Клиентский интерфейс**: HTML + JavaScript + WebSocket
- **API данных**: Центробанк РФ (JSON API)
- **Язык**: Python 3.8+

## Структура проекта

```
currency-observer/
├── app.py                 # Основной сервер
├── config.py             # Конфигурация приложения
├── test_client.py        # Тестовый клиент
├── requirements.txt      # Зависимости Python
├── templates/
│   └── index.html       # HTML клиент
├── static/
│   └── style.css        # Стили
└── README.md            # Документация
```

## Установка и запуск

### 1. Установка зависимостей

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка библиотек
pip install -r requirements.txt
```

### 2. Запуск сервера

```bash
# Режим по умолчанию (обновление каждые 5 минут)
python app.py

# Тестовый режим (обновление каждую минуту)
python app.py --test_mode=true

# С указанием порта
python app.py --port=8899
```

### 3. Доступ к приложению

Откройте браузер и перейдите по адресу:
```
http://localhost:8888
```

Каждое новое окно браузера будет отдельным наблюдателем с уникальным идентификатором.

## Конфигурация

Основные настройки находятся в файле `config.py`:

```python
API_CONFIG = {
    "url": "https://www.cbr-xml-daily.ru/daily_json.js",
    "update_interval_ms": 300000,  # 5 минут
    "poll_interval_ms": 60000,     # 1 минута (для тестового режима)
}

CURRENCIES_TO_TRACK = ["USD", "EUR", "GBP", "CNY", "JPY"]
```

## API и протоколы

### WebSocket соединение
```
ws://localhost:8888/ws
```

### Сообщения от сервера

1. **Приветственное сообщение** (при подключении):
```json
{
  "type": "welcome",
  "client_id": "abc123",
  "message": "Connected to Currency Rate Observer",
  "currencies": ["USD", "EUR", "GBP"],
  "current_rates": {...}
}
```

2. **Обновление курсов**:
```json
{
  "type": "rates_updated",
  "timestamp": "2023-12-01T10:30:00",
  "changes": [
    {
      "code": "USD",
      "name": "US Dollar",
      "new_rate": 92.4567,
      "old_rate": 92.1234,
      "change": 0.3333,
      "change_percent": 0.36,
      "type": "increase"
    }
  ],
  "all_rates": {...}
}
```

### Сообщения от клиента

1. **Подписка на валюты**:
```json
{"type": "subscribe", "currencies": ["USD", "EUR"]}
```

2. **Запрос текущих курсов**:
```json
{"type": "get_rates"}
```

3. **Пинг**:
```json
{"type": "ping"}
```

## Тестирование

### Тестовый клиент

```bash
# Базовый тест
python test_client.py --test=basic

# Тест с несколькими клиентами
python test_client.py --test=multiple

# Тест имитации изменений (требует test_mode)
python test_client.py --test=simulation
```

### HTTP endpoints

```bash
# Проверка здоровья приложения
curl http://localhost:8888/health

# Главная страница
curl http://localhost:8888/

# Документация API
curl http://localhost:8888/api/docs
```

### Визуальное тестирование
1. Откройте несколько вкладок браузера с адресом `http://localhost:8888`
2. Каждая вкладка получит уникальный Client ID
3. В тестовом режиме нажмите "Simulate Change" для имитации изменений
4. Убедитесь, что все вкладки получают уведомления

## Аннотации типов

Проект использует аннотации типов Python для улучшения читаемости кода и статического анализа. Примеры:

```python
def attach(self, observer: WebSocketHandler) -> None:
    """Подписать нового наблюдателя"""
    pass

async def notify(self, data: Dict[str, Any]) -> None:
    """Уведомить всех наблюдателей об изменении"""
    pass

def get_current_rates(self) -> Dict[str, Dict[str, Any]]:
    """Получить текущие курсы валют"""
    pass
```



### Порт уже используется
```bash
# Найдите процесс, использующий порт
sudo lsof -i :8888

# Завершите процесс
kill <PID>
```

#