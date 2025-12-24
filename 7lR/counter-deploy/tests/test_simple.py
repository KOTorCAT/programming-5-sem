# tests/test_simple.py (дополнительный файл для проверки)
def test_pytest_works():
    """Простой тест чтобы убедиться что pytest работает"""
    assert 1 + 1 == 2
    print("✓ Pytest is working")

def test_fakeredis_works():
    """Проверяем что fakeredis установлен и работает"""
    import fakeredis
    r = fakeredis.FakeStrictRedis(decode_responses=True)
    r.set('test', '123')
    assert r.get('test') == '123'
    print("✓ Fakeredis is working")

def test_import_path():
    """Проверяем можем ли импортировать app.py"""
    import sys
    import os
    
    # Путь к backend
    backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
    
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    
    try:
        import app
        print(f"✓ app.py imported from: {backend_path}")
        
        # Проверяем ключевые атрибуты
        assert hasattr(app, 'app'), "No 'app' attribute"
        assert hasattr(app, 'r'), "No 'r' attribute (Redis client)"
        print("✓ App has required attributes")
        
    except ImportError as e:
        print(f"✗ Cannot import app.py: {e}")
        print(f"Current sys.path: {sys.path}")
        raise