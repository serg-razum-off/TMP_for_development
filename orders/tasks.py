import os
import json
import logging
import time
from datetime import datetime, timezone

from celery import shared_task
from django.core.exceptions import ValidationError

from .models import Order, UserMessage, OrderStatus

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_mobile_orders(self):
    base_dir = os.path.dirname(__file__)
    jsonl_path = os.path.join(base_dir, "..", "streaming_server", "stream_orders.jsonl")

    if not os.path.exists(jsonl_path):
        return 0

    # 1. Create target processing directory if it doesn't exist
    processing_dir = os.path.join(base_dir, "..", "streaming_server", "processing")
    os.makedirs(processing_dir, exist_ok=True)

    # 2. Rename to atomically claim the file and move it to the processing folder.
    # The source file is inherently removed, which is safe since your other
    # script recreates it on demand.
    processing_path = os.path.join(
        processing_dir, f"processing_{int(time.time())}.jsonl"
    )

    try:
        os.rename(jsonl_path, processing_path)
    except OSError as e:
        logger.warning(f"Could not rename file (might be locked by streamer): {e}")
        return 0

    processed_count = 0
    errored_count = 0
    failed_records = []

    try:
        with open(processing_path, "r") as file:
            for record_str in file:
                record_str = record_str.strip()
                if not record_str:
                    continue

                try:
                    record = json.loads(record_str)

                    created_by_id = record["created_by_id"]
                    user_id = record["user_id"]
                    title = f"AUTO: [{created_by_id} --> {user_id}] {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}"

                    Order.objects.create(
                        title=title,
                        created_by_id=created_by_id,
                        user_id=user_id,
                        status=OrderStatus.DRAFT,
                        comment=record.get("comment", ""),
                    )
                    processed_count += 1

                except json.JSONDecodeError as e:
                    logger.error(f"Malformed JSON line, skipping: {str(e)}")
                    failed_records.append(record_str)
                    errored_count += 1
                except (KeyError, ValidationError) as e:
                    logger.error(f"Failed to process mobile order: {str(e)}")
                    UserMessage.objects.create(
                        user_id=record.get("created_by_id", 1),
                        message_body=f"Failed to process mobile order: {str(e)}",
                        is_error=True,
                    )
                    failed_records.append(record_str)
                    errored_count += 1

        # 3. DLQ / Cleanup Logic
        if failed_records:
            # Overwrite the processing file with ONLY the failed records
            with open(processing_path, "w") as file:
                for failed_record in failed_records:
                    file.write(failed_record + "\n")

            # Safely replace the prefix only on the filename, not the full path
            dlq_filename = os.path.basename(processing_path).replace(
                "processing_", "dlq_"
            )
            dlq_path = os.path.join(processing_dir, dlq_filename)

            os.rename(processing_path, dlq_path)
            logger.warning(
                f"Retained {errored_count} failed records in DLQ: {dlq_path}"
            )
        else:
            # 100% success rate: remove the processing file in base_dir/processing entirely
            os.remove(processing_path)

    except Exception as e:
        # If the whole task crashes, the processing file is left untouched
        # so the entire remaining batch can be retried.
        logger.exception(f"Unexpected catastrophic error processing orders: {e}")

    finally:
        logger.info(
            f"Processed {processed_count} records, encountered {errored_count} errors"
        )

    return processed_count
