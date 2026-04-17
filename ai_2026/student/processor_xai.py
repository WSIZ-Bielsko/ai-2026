import os
from asyncio import sleep, run

from dotenv import load_dotenv
from loguru import logger
from xai_sdk import AsyncClient
from xai_sdk.chat import system, user

from ai_2026.student.common import rnd_id
from ai_2026.student.processor import AsyncProcessor


class XAIProcessor(AsyncProcessor):

    def __init__(self, model_name: str, api_key: str,):
        self.sys = 'Be very brief.'
        self.model_name = model_name
        self.client = AsyncClient(api_key=api_key)
        logger.debug(f"Connected to XAI API")

    async def process_prompts(self, prompts: list[str]) -> list[str]:
        reqests = dict()
        n = len(prompts)
        for i,p in enumerate(prompts):
            rid = rnd_id()
            reqests[rid] = {"id": rid, "system": self.sys, "user": p , "position": i}

        logger.debug('creating batch')
        batch = await self.client.batch.create(batch_name="eval_job")
        batch_id = batch.batch_id
        logger.debug(f"batch created: {batch_id}, adding requests")

        batch_requests = []
        for (rid, dd) in reqests.items():
            chat = self.client.chat.create(
                model=self.model_name,
                batch_request_id=rid,
            )
            chat.append(system(dd["system"]))
            chat.append(user(dd["user"]))
            batch_requests.append(chat)

        await self.client.batch.add(batch_id=batch_id, batch_requests=batch_requests)

        # having batch_requests

        # wait for completion
        logger.debug(f"waiting for completion of batch {batch_id}")
        while True:
            batch = await self.client.batch.get(batch_id=batch_id)
            pending = batch.state.num_pending
            logger.debug(f"Progress: still {pending}/{len(batch_requests)} pending")
            if pending == 0:
                break
            await sleep(1.0)

        # pull results
        all_results = []
        pagination_token = None
        while True:
            page = await self.client.batch.list_batch_results(
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
            if page.pagination_token is None:
                break
            pagination_token = page.pagination_token

        # have "all_results"
        print(all_results[0])

        response = [''] * n
        for res in all_results:
            rid = res["id"]
            response[reqests[rid]["position"]] = res["content"]

        return response



async def main():
    load_dotenv()
    proc = XAIProcessor(model_name="grok-4-1-fast-non-reasoning", api_key=os.getenv("XAI_KEY"))

    prompts = ['capital of Poland', 'president of United States of Mexico', 'how many senators are the in polish senate']
    res = await proc.process_prompts(prompts)
    print(res)



if __name__ == '__main__':
    run(main())
