from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
from database import get_db, init_db
import uvicorn

# Инициализация БД при старте приложения
init_db()

app = FastAPI(
    title="Глоссарий терминов Python",
    description="API для управления глоссарием терминов Python",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    """Вызывается при старте приложения"""
    init_db()
    print("✅ База данных инициализирована")

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в глоссарий терминов Python!"}

@app.get("/terms", response_model=List[schemas.TermResponse])
def get_all_terms(db: Session = Depends(get_db)):
    """Получить список всех терминов"""
    try:
        terms = crud.get_all_terms(db)
        return terms
    except Exception as e:
        print(f"Ошибка при получении терминов: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/terms/{term_name}", response_model=schemas.TermResponse)
def get_term(term_name: str, db: Session = Depends(get_db)):
    """Получить информацию о конкретном термине"""
    term = crud.get_term(db, term_name)
    if term is None:
        raise HTTPException(status_code=404, detail="Термин не найден")
    return term

@app.post("/terms", response_model=schemas.TermResponse, status_code=201)
def create_term(term: schemas.TermCreate, db: Session = Depends(get_db)):
    """Добавить новый термин"""
    # Проверяем, существует ли уже такой термин
    existing = crud.get_term(db, term.term)
    if existing:
        raise HTTPException(status_code=400, detail="Термин уже существует")
    
    return crud.create_term(db, term)

@app.put("/terms/{term_name}", response_model=schemas.TermResponse)
def update_term(term_name: str, term_update: schemas.TermUpdate, db: Session = Depends(get_db)):
    """Обновить существующий термин"""
    term = crud.update_term(db, term_name, term_update)
    if term is None:
        raise HTTPException(status_code=404, detail="Термин не найден")
    return term

@app.delete("/terms/{term_name}", status_code=204)
def delete_term(term_name: str, db: Session = Depends(get_db)):
    """Удалить термин из глоссария"""
    success = crud.delete_term(db, term_name)
    if not success:
        raise HTTPException(status_code=404, detail="Термин не найден")
    return

# Для запуска без Docker
if __name__ == "__main__":
    print(" Запуск сервера на http://localhost:8000")
    print(" Swagger UI: http://localhost:8000/docs")
    print(" ReDoc: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)