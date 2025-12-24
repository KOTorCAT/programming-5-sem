# Глоссарий терминов Python API

Простое REST API для управления глоссарием Python-терминов с возможностью добавления, обновления, поиска и удаления терминов.

##  Запуск проекта

```bash
# Остановить все контейнеры (если запущены)
docker-compose down
```
```bash
# Собрать и запустить контейнеры в фоновом режиме
docker-compose up -d --build
После запуска API будет доступно по адресу: http://localhost:8000
```
```bash
API Endpoints
Метод	Путь	Описание
GET	/	Проверка работы API
GET	/terms	Получить все термины
GET	/terms/{term}	Получить конкретный термин
POST	/terms	Добавить новый термин
PUT	/terms/{term}	Обновить существующий термин
DELETE	/terms/{term}	Удалить термин
Примеры использования (curl)
1. Проверка работы API
bash
curl http://localhost:8000/
2. Получить все термины
bash
curl http://localhost:8000/terms
3. Добавить новый термин
bash
curl -X POST "http://localhost:8000/terms" \
  -H "Content-Type: application/json" \
  -d '{
    "term": "декоратор",
    "description": "Функция, которая принимает другую функцию и расширяет её функциональность",
    "category": "Функции",
    "example": "@app.route(\"/\")"
  }'
4. Получить конкретный термин
bash
curl http://localhost:8000/terms/декоратор
5. Обновить термин
bash
curl -X PUT "http://localhost:8000/terms/декоратор" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Обновленное описание декоратора",
    "category": "Продвинутые функции"
  }'
6. Удалить термин
bash
curl -X DELETE "http://localhost:8000/terms/декоратор"