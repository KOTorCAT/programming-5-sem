"""
Конфигурация приложения для отслеживания курсов валют
"""
from typing import List, Dict, Any

# Конфигурация API Центробанка
API_CONFIG: Dict[str, Any] = {
    "url": "https://www.cbr-xml-daily.ru/daily_json.js",
    "update_interval_ms": 300000,  # 5 минут
    "poll_interval_ms": 60000,     # 1 минута для тестового режима
}

# Валюты для отслеживания
CURRENCIES_TO_TRACK: List[str] = ["USD", "EUR", "GBP", "CNY", "JPY"]

# Конфигурация сервера
SERVER_CONFIG: Dict[str, Any] = {
    "port": 8888,
    "host": "localhost",
    "debug": True,
}

# Конфигурация WebSocket
WEBSOCKET_CONFIG: Dict[str, Any] = {
    "ping_interval": 30,
    "ping_timeout": 60,
    "max_message_size": 10485760,  # 10MB
}