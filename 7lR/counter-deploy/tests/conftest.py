# tests/conftest.py
import pytest
import fakeredis
import sys
import os
from unittest.mock import patch

# 1. СНАЧАЛА мокаем Redis, ПОТОМ импортируем app
fake_redis = fakeredis.FakeStrictRedis(decode_responses=True)
fake_redis.set('counter:value', 0)

# 2. Мокаем функцию get_redis_client ДО импорта
with patch('redis.Redis', return_value=fake_redis):
    # Добавляем backend в путь
    backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
    sys.path.insert(0, backend_path)
    
    # Теперь импортируем
    from app import app as flask_app

@pytest.fixture
def app():
    """Приложение с мокнутым Redis"""
    flask_app.config['TESTING'] = True
    
    # Убедимся что Redis мокнут
    from app import r
    print(f"Redis client type: {type(r)}")
    
    return flask_app

@pytest.fixture
def client(app):
    """Тестовый клиент Flask"""
    return app.test_client()