import json
import os
import re

from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI
from openai.types import CompletionUsage
from pydantic import BaseModel


# MODEL


class AI_Model(BaseModel):
    name: str
    model_name: str
    base_url: str
    key_name: str


class CallCost(BaseModel):
    prompt_tokens: int
    completion_tokens: int

    @staticmethod
    def from_response(response):
        u: CompletionUsage = response.usage
        return CallCost(prompt_tokens=u.prompt_tokens, completion_tokens=u.completion_tokens)


AI_MODELS: dict[str, AI_Model] = {
    "gemini": AI_Model(
        name="gemini",
        model_name="gemini-3-flash-preview",
        # model_name="gemini-2.5-pro-preview-03-25",
        # model_name="gemini-2.5-pro-exp-03-25",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        key_name="GEMINI_KEY"
    ),
    "gemini-simple": AI_Model(
        name="gemini",
        # model_name="gemini-2.0-flash",
        # model_name="gemini-2.5-flash-preview-04-17",
        # model_name="gemini-2.5-flash-preview-05-20",
        model_name="gemini-3.1-flash-lite-preview",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        key_name="GEMINI_KEY"
    ),
    "grok": AI_Model(
        name="grok",
        base_url="https://api.x.ai/v1",
        # model_name="grok-2-1212",
        model_name="grok-3-fast-latest",
        key_name="XAI_KEY"
    ),
    "grok-simple": AI_Model(
        name="grok-simple",
        base_url="https://api.x.ai/v1",
        model_name="grok-3-mini-latest",
        key_name="XAI_KEY"
    ),
    "grok-4.2": AI_Model(
        name="grok-4.2",
        base_url="https://api.x.ai/v1",
        model_name="grok-4.20-0309-non-reasoning",
        key_name="XAI_KEY"
    ),
    "sonar": AI_Model(
        name="sonar",
        base_url="https://api.perplexity.ai",
        model_name="sonar",
        key_name="PPLX_KEY"
    ),
    "claude": AI_Model(
        name="claude",
        base_url="https://api.anthropic.com/v1",
        # model_name="claude-3-7-sonnet-20250219",
        # model_name="claude-sonnet-4-20250514",
        model_name="claude-sonnet-4-5-20250929",
        key_name="ANTHROPIC_KEY"
    ),
    "claude-opus": AI_Model(
        name="claude",
        base_url="https://api.anthropic.com/v1",
        # model_name="claude-3-7-sonnet-20250219",
        model_name="claude-opus-4-1-20250805",
        key_name="ANTHROPIC_KEY"
    ),
    "qwen": AI_Model(
        name="qwen-max",
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        model_name="qwen-max",  # qwen-max, qwen-plus, qwq-plus
        key_name="QWEN_KEY"
    ),
    "gpt": AI_Model(
        name="gpt",
        base_url="https://api.openai.com/v1/",
        # model_name="gpt-4o-mini",
        # model_name="gpt-4o",  #
        model_name="gpt-4o",  # beware, $$$; check 4.1 first
        key_name="GPT_KEY"
    ),
    "gpt-simple": AI_Model(
        name="gpt-simple",
        base_url="https://api.openai.com/v1/",
        model_name="gpt-4.1-2025-04-14",
        key_name="GPT_KEY"
    ),
    "gpt-5": AI_Model(
        name="gpt-5",
        base_url="https://api.openai.com/v1/",
        model_name="gpt-5-2025-08-07",
        key_name="GPT_KEY"
    ),
}


# HELPERS


def call_model(api_key: str, base_url: str, model_name: str, messages: list[dict]) -> tuple[str, CallCost]:
    client = OpenAI(api_key=api_key, base_url=base_url)
    logger.info(f'calling {model_name}')
    # .....
    res = client.chat.completions.create(model=model_name, messages=messages)
    content = res.choices[0].message.content
    cost = CallCost.from_response(res)
    return content, cost


def content_to_structure(content: str, structure_key: str = 'answer'):
    cleaned_content = re.sub(r'```json\s*|\s*```', '', content).strip()
    try:
        xx = json.loads(cleaned_content)
    except ValueError:
        logger.error(f'not json-parseable: [{content}]')
        raise RuntimeError('Error parsing JSON')
    try:
        answer = xx[structure_key]
    except KeyError:
        logger.error(f'structure key {structure_key} not found in answer')
        raise RuntimeError(f'structure key {structure_key} not found in answer')
    return answer


def call_ai_model(model_name: str, prompt: list[dict], required_key: str):
    load_dotenv()

    config = AI_MODELS[model_name]
    key = os.getenv(config.key_name)

    content, usage = call_model(
        api_key=key,
        base_url=config.base_url,
        model_name=config.model_name,
        messages=prompt
    )

    answer = content_to_structure(content, structure_key=required_key)
    return answer, usage





def prompt_for_json(message: str, required_key: str) -> list[dict]:
    """
    Creates a openai prompt that explicitly calls for returning only a JSON object with the only key `required_key`.
    :param message:
    :param required_key:
    :return:
    """
    messages = [
        {
            "role": "system",
            "content": "You are a concise assistant. Provide responses in a structured JSON format. "
                       "Return only a JSON object with proper keys"
        },
        {
            "role": "user",
            "content": message + f". Return _only_ the json structure with key `{required_key}`. "
        }
    ]
    return messages
