import requests
import json
import sys
from datetime import datetime, timedelta
import os
from pathlib import Path

class OpenWeatherClient:
    """Простой клиент для OpenWeather API"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("API ключ не указан. Установите OPENWEATHER_API_KEY или передайте в конструктор")
        
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.cache_dir = Path.home() / ".openweather_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
    def get_current_weather(self, city, country=None, units="metric"):
        """Получить текущую погоду для города"""
        query = f"{city},{country}" if country else city
        cache_key = f"current_{query}_{units}"
        
        # Проверка кеша
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        # API запрос
        url = f"{self.base_url}/weather"
        params = {
            "q": query,
            "appid": self.api_key,
            "units": units,
            "lang": "ru"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Сохранение в кеш
        self._save_to_cache(cache_key, data)
        
        return self._format_current_weather(data)
    
    def get_forecast(self, city, country=None, units="metric", days=1):
        """Получить прогноз погоды на несколько дней"""
        if days < 1 or days > 5:
            raise ValueError("Допустимое количество дней: от 1 до 5")
            
        query = f"{city},{country}" if country else city
        cache_key = f"forecast_{query}_{units}_{days}"
        
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        url = f"{self.base_url}/forecast"
        params = {
            "q": query,
            "appid": self.api_key,
            "units": units,
            "lang": "ru",
            "cnt": days * 8  # 8 записей в день (каждые 3 часа)
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        self._save_to_cache(cache_key, data)
        
        return self._format_forecast(data, days)
    
    def _get_from_cache(self, key):
        """Получить данные из кеша"""
        cache_file = self.cache_dir / f"{hash(key)}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Проверяем, не устарели ли данные (кеш на 10 минут)
                    cache_time = datetime.fromisoformat(data['_cached_at'])
                    if datetime.now() - cache_time < timedelta(minutes=10):
                        return data['data']
            except (json.JSONDecodeError, KeyError):
                # Если файл поврежден, игнорируем кеш
                pass
        return None
    
    def _save_to_cache(self, key, data):
        """Сохранить данные в кеш"""
        cache_file = self.cache_dir / f"{hash(key)}.json"
        cache_data = {
            '_cached_at': datetime.now().isoformat(),
            'data': data
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    def _format_current_weather(self, data):
        """Форматирование текущей погоды в читаемый вид"""
        weather_info = {
            'город': data['name'],
            'страна': data['sys']['country'],
            'температура': f"{round(data['main']['temp'], 1)}°C",
            'ощущается': f"{round(data['main']['feels_like'], 1)}°C",
            'влажность': f"{data['main']['humidity']}%",
            'давление': f"{data['main']['pressure']} hPa",
            'погода': data['weather'][0]['description'].capitalize(),
            'ветер': f"{data['wind']['speed']} м/с"
        }
        
        if 'wind' in data and 'deg' in data['wind']:
            weather_info['направление ветра'] = self._get_wind_direction(data['wind']['deg'])
            
        return weather_info
    
    def _format_forecast(self, data, days):
        """Форматирование прогноза погоды"""
        forecasts = []
        
        # Группируем по дням
        daily_forecasts = {}
        for item in data['list'][:days * 8]:
            date = item['dt_txt'].split()[0]  # Берем только дату
            if date not in daily_forecasts:
                daily_forecasts[date] = []
            daily_forecasts[date].append(item)
        
        for date, items in list(daily_forecasts.items())[:days]:
            # Средняя температура за день
            temps = [item['main']['temp'] for item in items]
            avg_temp = sum(temps) / len(temps)
            
            # Наиболее частое описание погоды
            weather_counts = {}
            for item in items:
                desc = item['weather'][0]['description']
                weather_counts[desc] = weather_counts.get(desc, 0) + 1
            
            most_common_weather = max(weather_counts.items(), key=lambda x: x[1])[0]
            
            forecasts.append({
                'дата': date,
                'средняя температура': f"{round(avg_temp, 1)}°C",
                'погода': most_common_weather.capitalize(),
                'количество прогнозов': len(items)
            })
        
        return {
            'город': data['city']['name'],
            'страна': data['city']['country'],
            'прогнозы': forecasts
        }
    
    def _get_wind_direction(self, degrees):
        """Преобразовать градусы в направление ветра"""
        directions = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
        index = round(degrees / 45) % 8
        return directions[index]

def main():
    """Консольный интерфейс для работы с погодой"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Получить текущую погоду или прогноз с OpenWeather',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  get-weather Moscow --country RU
  get-weather "New York" --api-key ваш_ключ
  get-weather London --forecast 3 --units metric
  get-weather Tokyo --forecast 2 --units imperial
        """
    )
    
    parser.add_argument('city', help='Название города (например: "Moscow")')
    parser.add_argument('--country', help='Код страны (например: RU, US, GB)')
    parser.add_argument('--api-key', help='API ключ OpenWeather. Можно также установить через OPENWEATHER_API_KEY')
    parser.add_argument('--forecast', type=int, help='Прогноз на N дней (от 1 до 5)')
    parser.add_argument('--units', choices=['metric', 'imperial'], default='metric',
                       help='Единицы измерения: metric (метрические) или imperial (имперские)')
    parser.add_argument('--no-cache', action='store_true', help='Не использовать кеширование')
    
    args = parser.parse_args()
    
    try:
        client = OpenWeatherClient(api_key=args.api_key)
        
        if args.no_cache:
            client.cache_dir = None  # Отключаем кеширование
        
        if args.forecast:
            result = client.get_forecast(
                city=args.city,
                country=args.country,
                units=args.units,
                days=args.forecast
            )
            
            print(f"\n{'='*50}")
            print(f"Прогноз погоды для {result['город']}, {result['страна']}")
            print(f"На {args.forecast} дней:")
            print('='*50)
            
            for forecast in result['прогнозы']:
                print(f"\n📅 {forecast['дата']}:")
                print(f"   🌡  Температура: {forecast['средняя температура']}")
                print(f"   ☁️  Погода: {forecast['погода']}")
                print(f"   📊 Прогнозов в день: {forecast['количество прогнозов']}")
                
        else:
            result = client.get_current_weather(
                city=args.city,
                country=args.country,
                units=args.units
            )
            
            print(f"\n{'='*50}")
            print(f"Текущая погода в {result['город']}, {result['страна']}:")
            print('='*50)
            
            for key, value in result.items():
                if key not in ['город', 'страна']:
                    # Иконки для разных параметров погоды
                    icons = {
                        'температура': '🌡',
                        'ощущается': '🤔',
                        'влажность': '💧',
                        'давление': '📊',
                        'погода': '☁️',
                        'ветер': '💨',
                        'направление ветра': '🧭'
                    }
                    icon = icons.get(key, '•')
                    print(f"   {icon} {key.replace('_', ' ').title()}: {value}")
            
        print(f"\n{'='*50}")
        print("Данные предоставлены OpenWeather")
        
    except ValueError as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(f"\n❌ Ошибка авторизации: Неверный API ключ")
            print("   Получите ключ на: https://openweathermap.org/api")
        elif e.response.status_code == 404:
            print(f"\n❌ Город не найден: {args.city}")
            print("   Проверьте правильность названия города и страны")
        else:
            print(f"\n❌ Ошибка API: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()