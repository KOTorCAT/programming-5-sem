import unittest
from unittest.mock import patch, Mock
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simple_openweather_client import OpenWeatherClient

class TestOpenWeatherClient(unittest.TestCase):
    
    def setUp(self):
        self.api_key = "test_api_key"
        self.client = OpenWeatherClient(api_key=self.api_key)
    
    @patch('simple_openweather_client.client.requests.get')
    def test_get_current_weather_success(self, mock_get):
        """Тест успешного получения текущей погоды"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "Moscow",
            "sys": {"country": "RU"},
            "main": {
                "temp": 15.5,
                "feels_like": 14.0,
                "humidity": 65,
                "pressure": 1013
            },
            "weather": [{"description": "ясно"}],
            "wind": {"speed": 3.5, "deg": 180}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get_current_weather("Moscow", "RU")
        
        self.assertEqual(result['город'], "Moscow")
        self.assertEqual(result['страна'], "RU")
        self.assertEqual(result['температура'], "15.5°C")
        self.assertEqual(result['погода'], "Ясно")
    
    def test_missing_api_key(self):
        """Тест отсутствия API ключа"""
        with self.assertRaises(ValueError) as context:
            OpenWeatherClient(api_key=None)
        
        self.assertIn("API ключ не указан", str(context.exception))
    
    @patch('simple_openweather_client.client.requests.get')
    def test_api_error_handling(self, mock_get):
        """Тест обработки ошибок API"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            self.client.get_current_weather("Moscow")
        
        self.assertIn("API Error", str(context.exception))
    
    def test_wind_direction_conversion(self):
        """Тест конвертации направления ветра"""
        test_cases = [
            (0, 'С'), (45, 'СВ'), (90, 'В'),
            (135, 'ЮВ'), (180, 'Ю'), (225, 'ЮЗ'),
            (270, 'З'), (315, 'СЗ'), (360, 'С')
        ]
        
        for degrees, expected in test_cases:
            result = self.client._get_wind_direction(degrees)
            self.assertEqual(result, expected, f"Для {degrees}° ожидалось {expected}, получено {result}")
    
    def test_forecast_days_validation(self):
        """Тест валидации количества дней прогноза"""
        with self.assertRaises(ValueError) as context:
            self.client.get_forecast("Moscow", days=0)
        
        self.assertIn("Допустимое количество дней", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.client.get_forecast("Moscow", days=6)
        
        self.assertIn("Допустимое количество дней", str(context.exception))

if __name__ == '__main__':
    unittest.main()