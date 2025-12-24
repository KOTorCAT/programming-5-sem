from sqlalchemy.orm import Session
from models import Term
import schemas

def get_all_terms(db: Session):
    """Получить все термины"""
    return db.query(Term).all()

def get_term(db: Session, term_name: str):
    """Получить термин по названию"""
    return db.query(Term).filter(Term.term == term_name).first()

def create_term(db: Session, term: schemas.TermCreate):
    """Создать новый термин"""
    db_term = Term(**term.dict())
    db.add(db_term)
    db.commit()
    db.refresh(db_term)
    return db_term

def update_term(db: Session, term_name: str, term_update: schemas.TermUpdate):
    """Обновить существующий термин"""
    db_term = get_term(db, term_name)
    if not db_term:
        return None
    
    update_data = term_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_term, key, value)
    
    db.commit()
    db.refresh(db_term)
    return db_term

def delete_term(db: Session, term_name: str):
    """Удалить термин"""
    db_term = get_term(db, term_name)
    if not db_term:
        return False
    
    db.delete(db_term)
    db.commit()
    return True