from abc import ABC, abstractmethod


class AsyncProcessor(ABC):

    @abstractmethod
    async def process_prompts(self, prompts: list[str]) -> list[str]:
        """
        Processes a list of prompts asynchronously, returns answers in the same order as the prompts.
        :param prompts:
        :return:
        """