import os
import json
import logging
from datetime import datetime

from celery import shared_task
from django.core.exceptions import ValidationError

from .models import Order, UserMessage, OrderStatus

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_mobile_orders(self):
    jsonl_path = os.path.join(
        os.path.dirname(__file__), "streaming", "stream_orders.jsonl"
    )
    processed_records = []
    errored_records = []

    if not os.path.exists(jsonl_path):
        logger.warning(f"JSONL file not found: {jsonl_path}")
        return 0

    with open(jsonl_path, "r") as file:
        records = file.readlines()

    for record_str in records:
        try:
            record = json.loads(record_str)

            # Generate dynamic title with created_by_id --> user_id pattern
            created_by_id = record["created_by_id"]
            user_id = record["user_id"]
            title = f"New order created: {created_by_id} --> {user_id} {datetime.now().isoformat()}"

            # Create order
            order = Order.objects.create(
                title=title,
                created_by_id=created_by_id,
                user_id=user_id,
                status=OrderStatus.DRAFT,
                comment=record.get("comment", ""),
            )

            processed_records.append(record_str)

        except (KeyError, ValidationError) as e:
            # Log the error and mark for user notification
            logger.error(f"Failed to process mobile order: {str(e)}")
            errored_records.append(record_str)

            # Create user message for failure
            UserMessage.objects.create(
                user_id=record.get(
                    "created_by_id", 1
                ),  # Default to first admin if no user_id
                message=f"Failed to process mobile order: {str(e)}",
                is_error=True,
            )

    # Rewrite the file, excluding processed and errored records
    with open(jsonl_path, "w") as file:
        for record in records:
            if record not in processed_records and record not in errored_records:
                file.write(record)

    # Log results
    logger.info(
        f"Processed {len(processed_records)} records, "
        f"encountered {len(errored_records)} errors"
    )

    return len(processed_records)
