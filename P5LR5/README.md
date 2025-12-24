# Python Glossary API

REST API для управления глоссарием терминов Python.

##  Быстрый запуск

```bash
docker-compose up --build
```
```bash
docker-compose down --remove-orphans
```


##  API Endpoints

| Метод | Путь | Описание | curl пример |
|-------|------|----------|-------------|
| `GET` | `/` | Проверка работы API | `curl http://localhost:8000/` |
| `GET` | `/terms` | Все термины | `curl http://localhost:8000/terms` |
| `GET` | `/terms/{term}` | Конкретный термин | `curl http://localhost:8000/terms/декоратор` |
| `POST` | `/terms` | Добавить термин | `curl -X POST http://localhost:8000/terms -H "Content-Type: application/json" -d '{"term": "декоратор", "description": "..."}'` |
| `PUT` | `/terms/{term}` | Обновить термин | `curl -X PUT http://localhost:8000/terms/декоратор -H "Content-Type: application/json" -d '{"description": "Новое описание"}'` |
| `DELETE` | `/terms/{term}` | Удалить термин | `curl -X DELETE http://localhost:8000/terms/декоратор` |

##  Примеры использования curl

### 1. Проверка API
```bash
curl http://localhost:8000/
```

### 2. Получить все термины
```bash
curl http://localhost:8000/terms
```

### 3. Добавить новый термин
```bash
curl -X POST "http://localhost:8000/terms" \
  -H "Content-Type: application/json" \
  -d '{
    "term": "декоратор",
    "description": "Функция, которая принимает другую функцию и расширяет её функциональность",
    "category": "Функции",
    "example": "@app.route(\"/\")"
  }'
```

### 4. Получить конкретный термин
```bash
curl http://localhost:8000/terms/декоратор
```

### 5. Обновить термин
```bash
curl -X PUT "http://localhost:8000/terms/декоратор" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Обновленное описание декоратора",
    "category": "Продвинутые функции"
  }'
```

### 6. Удалить термин
```bash
curl -X DELETE "http://localhost:8000/terms/декоратор"
```



