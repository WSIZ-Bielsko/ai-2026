from ai_2026.student.processor import AsyncProcessor
import os
from asyncio import sleep, run

from dotenv import load_dotenv
from loguru import logger
from anthropic import AsyncAnthropic

from ai_2026.student.common import rnd_id
from ai_2026.student.processor import AsyncProcessor


class AnthropicProcessor(AsyncProcessor):

    def __init__(self, model_name: str, api_key: str):
        self.sys = "Be very brief."
        self.model_name = model_name
        self.client = AsyncAnthropic(api_key=api_key)
        logger.debug("Connected to Anthropic API")

    async def process_prompts(self, prompts: list[str]) -> list[str]:
        requests_map = {}
        n = len(prompts)

        for i, p in enumerate(prompts):
            rid = rnd_id()
            requests_map[rid] = {
                "id": rid,
                "system": self.sys,
                "user": p,
                "position": i,
            }

        logger.debug("creating batch")

        batch_requests = []
        for rid, dd in requests_map.items():
            batch_requests.append({
                "custom_id": rid,
                "params": {
                    "model": self.model_name,
                    "max_tokens": 256,
                    "system": dd["system"],
                    "messages": [
                        {
                            "role": "user",
                            "content": dd["user"],
                        }
                    ],
                },
            })

        batch = await self.client.messages.batches.create(
            requests=batch_requests
        )
        batch_id = batch.id
        logger.debug(f"batch created: {batch_id}")

        logger.debug(f"waiting for completion of batch {batch_id}")
        while True:
            batch = await self.client.messages.batches.retrieve(batch_id)
            counts = batch.request_counts
            pending = counts.processing
            logger.debug(
                f"Progress: still {pending}/{len(batch_requests)} processing "
                f"(ok={counts.succeeded}, err={counts.errored}, canceled={counts.canceled}, expired={counts.expired})"
            )
            if batch.processing_status == "ended":
                break
            await sleep(1.0)

        all_results = []
        result_stream = await self.client.messages.batches.results(batch_id)

        async for entry in result_stream:
            if entry.result.type == "succeeded":
                text = "".join(
                    block.text for block in entry.result.message.content
                    if block.type == "text"
                )
                usage = entry.result.message.usage
                all_results.append({
                    "id": entry.custom_id,
                    "content": text,
                    "tokens": usage.input_tokens + usage.output_tokens,
                })
            else:
                all_results.append({
                    "id": entry.custom_id,
                    "content": f"[{entry.result.type}]",
                    "tokens": 0,
                })

        if all_results:
            print(all_results[0])

        response = [""] * n
        for res in all_results:
            rid = res["id"]
            response[requests_map[rid]["position"]] = res["content"]

        return response


async def main():
    load_dotenv()
    proc = AnthropicProcessor(
        model_name="claude-sonnet-4-5-20250929",
        api_key=os.getenv("ANTHROPIC_KEY"),
    )

    prompts = [
        "capital of Poland",
        "president of United States of Mexico",
        "how many senators are the in polish senate",
    ]
    res = await proc.process_prompts(prompts)
    print(res)


if __name__ == "__main__":
    run(main())