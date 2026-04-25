import json
import os
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from schemas import OrderDraft

app = FastAPI(title="Order Streaming API")
logger = logging.getLogger(__name__)

STORAGE_FILE = os.path.join(os.path.dirname(__file__), "stream_orders.jsonl")

@app.post("/create_order", status_code=201)
async def create_order(order: OrderDraft):
    try:
        # Prepare data for storage
        order_data = order.dict()
        if not order_data.get("created_at"):
            order_data["created_at"] = datetime.now(timezone.utc).isoformat()
        else:
            order_data["created_at"] = order_data["created_at"].isoformat()

        # Append to JSONL file
        with open(STORAGE_FILE, "a") as f:
            f.write(json.dumps(order_data) + "\n")
        
        return {"status": "success", "message": "Order draft saved"}
    except OSError as e:
        logger.error("Failed to write order to JSONL: %s", e)
        raise HTTPException(status_code=500, detail="Storage error. Please try again later.")
    except Exception as e:
        logger.error("Unexpected error in create_order: %s", e)
        raise e

@app.get("/health")
async def health_check():
    return {"status": "ok"}
