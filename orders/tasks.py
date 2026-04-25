import os
import json
import logging
from datetime import datetime, timezone

from celery import shared_task
from django.core.exceptions import ValidationError

from .models import Order, UserMessage, OrderStatus

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_mobile_orders(self):
    base_dir = os.path.dirname(__file__)

    # Define directories
    incoming_dir = os.path.join(base_dir, "..", "streaming_server", "incoming")
    processing_dir = os.path.join(base_dir, "..", "streaming_server", "processing")

    # If the incoming directory doesn't exist yet, there are no files to process
    if not os.path.exists(incoming_dir):
        return 0

    # Ensure target processing directory exists
    os.makedirs(processing_dir, exist_ok=True)

    total_processed = 0
    total_errors = 0

    # Loop over all files in the incoming directory
    for filename in os.listdir(incoming_dir):
        if not filename.endswith(".jsonl"):
            continue  # Skip any non-jsonl files just in case

        incoming_path = os.path.join(incoming_dir, filename)

        # Prepend 'processing_' to the original filename
        # (e.g., stream_orders_123.jsonl -> processing_stream_orders_123.jsonl)
        processing_filename = f"processing_{filename}"
        processing_path = os.path.join(processing_dir, processing_filename)

        # 1. Rename to atomically claim the file
        try:
            os.rename(incoming_path, processing_path)
        except OSError as e:
            logger.warning(
                f"Could not claim file {filename} (might be locked/moved): {e}"
            )
            continue  # Skip to the next file if we can't move this one

        # Per-file tracking
        file_processed_count = 0
        file_errored_count = 0
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
                        file_processed_count += 1

                    except json.JSONDecodeError as e:
                        logger.error(f"Malformed JSON line, skipping: {str(e)}")
                        failed_records.append(record_str)
                        file_errored_count += 1
                    except (KeyError, ValidationError) as e:
                        logger.error(f"Failed to process mobile order: {str(e)}")
                        UserMessage.objects.create(
                            user_id=record.get("created_by_id", 1),
                            message_body=f"Failed to process mobile order: {str(e)}",
                            is_error=True,
                        )
                        failed_records.append(record_str)
                        file_errored_count += 1

            # 2. DLQ / Cleanup Logic for this specific file
            if failed_records:
                # Overwrite the processing file with ONLY the failed records
                with open(processing_path, "w") as file:
                    for failed_record in failed_records:
                        file.write(failed_record + "\n")

                # Safely replace the prefix only on the filename
                dlq_filename = processing_filename.replace("processing_", "dlq_")
                dlq_path = os.path.join(processing_dir, dlq_filename)

                os.rename(processing_path, dlq_path)
                logger.warning(
                    f"Retained {file_errored_count} failed records in DLQ: {dlq_path}"
                )
            else:
                # 100% success rate: remove the temporary processing file entirely
                os.remove(processing_path)

        except Exception as e:
            # If processing crashes completely for a file, log it and leave the file in /processing/
            logger.exception(
                f"Unexpected catastrophic error processing {filename}: {e}"
            )

        # Add to total counts
        total_processed += file_processed_count
        total_errors += file_errored_count

    # Final summary log after looping through all files
    logger.info(
        f"Batch Complete: Processed {total_processed} records total, encountered {total_errors} errors"
    )

    return total_processed
