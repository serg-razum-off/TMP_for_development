from fastapi import APIRouter, HTTPException
from fin_app.db.db_manager import DBManager

users_router = APIRouter()


@users_router.post("/users")
def add_user(name: str, email: str):
    with DBManager() as db:
        user = db.add_user(name, email)
    return user


@users_router.get("/user/{user_id}")
def get_user(user_id: int):
    with DBManager() as db:
        user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@users_router.get("/users")
def get_list_users():
    with DBManager() as db:
        users = db.list_users()
    return users


@users_router.put("/users/{user_id}")
def update_user(user_id: int, name: str, email: str):
    with DBManager() as db:
        user = db.update_user(user_id, name, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@users_router.delete("/users/{user_id}")
def delete_user(user_id: int):
    with DBManager() as db:
        success = db.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully", "user_id": user_id}
