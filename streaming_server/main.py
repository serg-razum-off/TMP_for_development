import json
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from schemas import OrderDraft

app = FastAPI(title="Order Streaming API")

STORAGE_FILE = os.path.join(os.path.dirname(__file__), "stream_orders.jsonl")

@app.post("/create_order", status_code=201)
async def create_order(order: OrderDraft):
    try:
        # Prepare data for storage
        order_data = order.dict()
        if not order_data.get("created_at"):
            order_data["created_at"] = datetime.now().isoformat()
        else:
            order_data["created_at"] = order_data["created_at"].isoformat()

        # Append to JSONL file
        with open(STORAGE_FILE, "a") as f:
            f.write(json.dumps(order_data) + "\n")
        
        return {"status": "success", "message": "Order draft saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
