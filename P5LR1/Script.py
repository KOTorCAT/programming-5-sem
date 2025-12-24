# test_final_fixed.py
import sys
import os
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

import requests
from importlib.abc import MetaPathFinder
from importlib.util import spec_from_loader
import re
from urllib.parse import urlparse

class SimpleURLLoader:
    def create_module(self, spec):
        return None
    
    def exec_module(self, module):
        print(f"[Loader] Загружаю {module.__spec__.origin}")
        r = requests.get(module.__spec__.origin, timeout=5)
        r.raise_for_status()
        exec(compile(r.text, module.__spec__.origin, 'exec'), module.__dict__)

class UniversalURLFinder(MetaPathFinder):
    def __init__(self):
        self.cache = {}  # Кэш для проверенных URL
        
    def _try_url(self, url):
        """Проверяет, доступен ли URL и возвращает статус"""
        if url in self.cache:
            return self.cache[url]
        
        try:
            r = requests.get(url, timeout=2)
            status = r.status_code == 200
            self.cache[url] = status
            return status
        except:
            self.cache[url] = False
            return False
    
    def find_spec(self, fullname, path, target=None):
        print(f"\n[UniversalFinder] Ищем: '{fullname}', path: {path}")
        
        # Если path передан (например, при поиске внутри пакета), используем его
        search_paths = []
        if path is not None:
            search_paths.extend(path)
        search_paths.extend(sys.path)
        
        # Ищем URL пути
        for p in search_paths:
            if isinstance(p, str) and p.startswith(('http://', 'https://')):
                base_url = p.rstrip('/')
                print(f"[UniversalFinder] Проверяем базовый URL: {base_url}")
                
                # Разбиваем полное имя на части
                parts = fullname.split('.')
                
                # Генерируем возможные URL для проверки
                urls_to_try = []
                
                # 1. Прямой файл .py
                urls_to_try.append(f"{base_url}/{fullname.replace('.', '/')}.py")
                
                # 2. Пакет с __init__.py
                urls_to_try.append(f"{base_url}/{fullname.replace('.', '/')}/__init__.py")
                
                # 3. Для подмодулей: если полное имя содержит точки,
                #    пробуем найти файл в соответствующей структуре директорий
                if len(parts) > 1:
                    # Например, для mypackage.submodule пробуем:
                    # http://localhost:8000/mypackage/submodule.py
                    module_path = '/'.join(parts)
                    urls_to_try.append(f"{base_url}/{module_path}.py")
                    
                    # Или если это под-пакет:
                    urls_to_try.append(f"{base_url}/{module_path}/__init__.py")
                
                # Проверяем каждый URL
                for url in urls_to_try:
                    print(f"[UniversalFinder] Проверяем URL: {url}")
                    if self._try_url(url):
                        print(f"[UniversalFinder] ✓ Найден: {url}")
                        
                        # Определяем, это пакет или модуль
                        is_package = '/__init__.py' in url or url.endswith('/__init__.py')
                        
                        return spec_from_loader(
                            fullname, 
                            SimpleURLLoader(), 
                            origin=url,
                            is_package=is_package
                        )
        
        print(f"[UniversalFinder] ✗ Не найден: {fullname}")
        return None

# Очищаем sys.path_hooks и добавляем наш finder
sys.path_hooks.clear()
sys.meta_path = [finder for finder in sys.meta_path if not isinstance(finder, UniversalURLFinder)]
sys.meta_path.insert(0, UniversalURLFinder())

print("=== ТЕСТ ИМПОРТА ИЗ URL ===")

# Добавляем URL пути
sys.path.insert(0, "http://localhost:8000/")

print("\n1. Импортируем remotemodule:")
import remotemodule
print(f"   ✓ remotemodule.myfoo() = {remotemodule.myfoo()}")

print("\n2. Импортируем mypackage:")
import mypackage
print(f"   ✓ mypackage.greet() = {mypackage.greet()}")

print("\n3. Импортируем submodule через 'from mypackage import':")
try:
    from mypackage import submodule
    print(f"   ✓ submodule.hello() = {submodule.hello()}")
except ImportError as e:
    print(f"   ✗ Ошибка: {e}")
    print("   Пробуем альтернативный способ...")
    
    # Альтернатива: добавить путь к пакету
    sys.path.insert(0, "http://localhost:8000/mypackage")
    import submodule
    print(f"   ✓ submodule.hello() = {submodule.hello()}")

print("\n4. Импортируем с полным именем:")
try:
    import mypackage.submodule
    print(f"   ✓ mypackage.submodule.hello() = {mypackage.submodule.hello()}")
except ImportError as e:
    print(f"   ✗ Ошибка: {e}")

print("\n5. Дополнительные тесты:")
print(f"   remotemodule.add_numbers(10, 5) = {remotemodule.add_numbers(10, 5)}")
print(f"   remotemodule.get_version() = {remotemodule.get_version()}")

print("\n=== ТЕСТ ЗАВЕРШЕН ===")