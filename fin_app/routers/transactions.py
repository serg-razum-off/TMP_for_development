from fastapi import APIRouter, HTTPException
from fin_app.db.db_manager import DBManager

transaction_router = APIRouter()


@transaction_router.post("/transaction")
def add_transaction(user_id: int, amount: float, category: str, description: str):
    with DBManager() as db:
        transaction = db.add_transaction(user_id, amount, category, description)
    return transaction


@transaction_router.get("/transaction/{transaction_id}")
def get_transaction(transaction_id: int):
    with DBManager() as db:
        transaction = db.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@transaction_router.get("/transactions")
def list_transactions():
    with DBManager() as db:
        transactions = db.list_transactions()
    return transactions


@transaction_router.put("/transaction/{transaction_id}")
def update_transaction(
    transaction_id: int, user_id: int, amount: float, category: str, description: str
):
    with DBManager() as db:
        transaction = db.update_transaction(
            transaction_id, user_id, amount, category, description
        )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@transaction_router.delete("/transaction/{transaction_id}")
def delete_transaction(transaction_id: int):
    with DBManager() as db:
        success = db.delete_transaction(transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {
        "message": "Transaction deleted successfully",
        "transaction_id": transaction_id,
    }
