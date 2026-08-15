from sqlalchemy.orm import Session
from modules.auth.models import User

def get_user_by_phone(db: Session, phone: str):
    return db.query(User).filter(User.phone == phone).first()

def deactivate_user(db: Session, user_id: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
    return user
