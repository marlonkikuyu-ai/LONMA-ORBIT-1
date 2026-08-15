from sqlalchemy.orm import Session
def ban_user(db: Session, user_id: str):
    return {"status": "banned"}
def resolve_dispute(db: Session, order_id: str):
    return {"status": "resolved"}
