from random import randint

from loguru import logger

from ai_2026.common import prompt_for_json, call_ai_model

if __name__ == '__main__':
    n_prompts = 1
    # numbers = [randint(100,200) for _ in range(50)]
    # task = '+'.join([str(k) for k in numbers]) + '='

    prompt = 'is this sentence correct: "Some guys are corresponded by Angela"; answer with single boolean'


    results = []
    prompt = prompt_for_json(prompt, required_key='answer')
    for _ in range(n_prompts):
        try:
            answer, usage = call_ai_model('grok-simple', prompt, 'answer')
            logger.info(f'answer: [{answer}]')
            results.append(answer)
            # logger.info(f'correct: [{sum(numbers)}]')
            logger.info(f'cost: {usage}')
        except Exception as e:
            logger.error(e)

    logger.warning(f'all answers: {results}')


