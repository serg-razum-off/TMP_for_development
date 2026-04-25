import os
import json
import logging
import tempfile
from datetime import datetime, timezone

from celery import shared_task
from django.core.exceptions import ValidationError

from .models import Order, UserMessage, OrderStatus

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_mobile_orders(self):
    jsonl_path = os.path.join(
        os.path.dirname(__file__), "..", "streaming_server", "stream_orders.jsonl"
    )
    processed_count = 0
    errored_count = 0

    if not os.path.exists(jsonl_path):
        logger.warning(f"JSONL file not found: {jsonl_path}")
        return 0

    temp_file = tempfile.NamedTemporaryFile(
        mode="w", delete=False, dir=os.path.dirname(jsonl_path)
    )

    try:
        with open(jsonl_path, "r") as file:
            for record_str in file:
                try:
                    record = json.loads(record_str)

                    # Generate dynamic title with created_by_id --> user_id pattern
                    created_by_id = record["created_by_id"]
                    user_id = record["user_id"]
                    title = f"AUTO: [{created_by_id} --> {user_id}] {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}"
                    # .isoformat()}"

                    # Create order
                    Order.objects.create(
                        title=title,
                        created_by_id=created_by_id,
                        user_id=user_id,
                        status=OrderStatus.DRAFT,
                        comment=record.get("comment", ""),
                    )
                    processed_count += 1
                except (KeyError, ValidationError, json.JSONDecodeError) as e:
                    # Log the error and mark for user notification
                    logger.error(f"Failed to process mobile order: {str(e)}")
                    errored_count += 1

                    # Create user message for failure
                    UserMessage.objects.create(
                        user_id=record.get("created_by_id", 1)
                        if "record" in locals()
                        else 1,
                        message=f"Failed to process mobile order: {str(e)}",
                        is_error=True,
                    )
                    # Keep errored records in the file to avoid silent loss, or remove based on business logic.
                    # The plan says "rewrite the file, excluding processed and errored records" in original code,
                    # but typical optimization is to keep only what wasn't processed.
                    # Original logic: if record not in processed_records and record not in errored_records: write.
                    # This means processed and errored are REMOVED.

        # In the original code, processed and errored records were both removed from the file.
        # To mimic this with line-by-line: we simply don't write them to the temp file.
        # Since we are reading and processing in one pass, we just don't write successful or errored ones.
        # Actually, the original code reads all lines, then filters.
        # If we want to remove processed and errored, we write nothing.
        # Wait, if we remove everything that was either processed or errored, the file becomes empty?
        # Let's re-read original logic:
        # if record not in processed_records and record not in errored_records: file.write(record)
        # This means it removes everything it attempted to process.

        os.replace(temp_file.name, jsonl_path)
    finally:
        temp_file.close()
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    # Log results
    logger.info(
        f"Processed {processed_count} records, encountered {errored_count} errors"
    )

    return processed_count
