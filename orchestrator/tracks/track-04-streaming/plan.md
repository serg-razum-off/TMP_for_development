# Plan: track-04-streaming

## Objective
Implement a simplified FastAPI backend that receives order drafts via a REST API (`create_order`) and stores them in a JSON Lines (`.jsonl`) file. This service will run in a separate Docker container managed by `docker-compose`.

## Features
- **Endpoint**: `POST /create_order`
- **Payload**: JSON matching partial `Order` model (`user_id`, `created_by_id`, `comment`).
- **Storage**: Append to `./orders/streaming/stream_orders.jsonl`.
- **Validation**: Pydantic models for request validation.

## Architecture
- **FastAPI**: Lightweight web framework for the microservice.
- **Microservice Pattern**: Decoupled from the main Django app, running as its own service.
- **Docker**: Containerized deployment for consistency.

## Verification
- **Manual**: Test endpoint with `curl` or Swagger UI.
- **Automated**: Verify file creation and content format.
