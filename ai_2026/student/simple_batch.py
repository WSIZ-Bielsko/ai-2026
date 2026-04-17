import os
import time
from abc import ABC, abstractmethod
from datetime import datetime

from dotenv import load_dotenv
from loguru import logger
from xai_sdk import Client
from xai_sdk.chat import system, user

load_dotenv()

def get_client() -> Client:
    client = Client(api_key=os.getenv("XAI_KEY"))
    return client


def create_batch(client: Client, batch_name: str = "eval_job"):
    batch = client.batch.create(batch_name=batch_name)
    return batch


def add_requests(client: Client, batch_id: str, prompts: list[dict]):
    """
    prompts: list of {"id": str, "system": str, "user": str}
    """
    batch_requests = []
    for p in prompts:
        chat = client.chat.create(
            model="grok-4-1-fast-non-reasoning",
            batch_request_id=p["id"],
        )
        if p.get("system"):
            chat.append(system(p["system"]))
        chat.append(user(p["user"]))
        batch_requests.append(chat)

    client.batch.add(batch_id=batch_id, batch_requests=batch_requests)
    return batch_requests


def wait_for_completion(client: Client, batch_id: str, poll_interval: float = 1):
    logger.info("Waiting for batch to complete...")
    while True:
        batch = client.batch.get(batch_id=batch_id)
        pending = batch.state.num_pending
        completed = batch.state.num_success + batch.state.num_error
        total = batch.state.num_requests
        logger.info(f"Progress: {completed}/{total} complete, {pending} pending")
        if pending == 0:
            break
        time.sleep(poll_interval)
    return batch


def get_results(client: Client, batch_id: str) -> list[dict]:
    all_results = []
    pagination_token = None

    while True:
        page = client.batch.list_batch_results(
            batch_id=batch_id,
            limit=100,
            pagination_token=pagination_token,
        )
        for result in page.succeeded:
            all_results.append({
                "id": result.batch_request_id,
                "content": result.response.content,
                "tokens": result.response.usage.total_tokens,
            })
        for result in page.failed:
            all_results.append({
                "id": result.batch_request_id,
                "error": result.error_message,
            })
        if page.pagination_token is None:
            break
        pagination_token = page.pagination_token

    return all_results


def ts():
    return datetime.now().timestamp()

def process_batch(prompts: list[dict], batch_id: str = None) -> list[dict]:
    client = get_client()
    logger.info("Client connected")

    st = ts()

    if batch_id is None:
        logger.info("Creating batch")
        batch = create_batch(client)
        batch_id = batch.batch_id
        logger.info(f"Batch created: {batch_id}")

        add_requests(client, batch_id, prompts)
        logger.info(f"Added {len(prompts)} requests")

    wait_for_completion(client, batch_id)
    results = get_results(client, batch_id)
    logger.info(f"Retrieved {len(results)} results in {ts() - st:.3f}s")
    return results






if __name__ == "__main__":
    load_dotenv()

    sys_ = 'Be very brief.'
    sample_prompts = [
        {"id": "request-1", "system": sys_, "user": 'write 10 sentence text on "Immunological memory: Role in Vaccination"; assume good understanding of immunology'},
        {"id": "request-2", "system": sys_, "user": 'best practices for cassandra DB'},
        {"id": "request-3", "system": sys_, "user": 'future of polish politics'},
        {"id": "request-4", "system": sys_, "user": 'are RAM prices going to go up'},
    ]

    results = process_batch(sample_prompts)
    for r in results:
        print(r)