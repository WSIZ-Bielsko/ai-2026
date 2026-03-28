import json
from random import shuffle

from loguru import logger

from ai_2026.common import call_ai_model, prompt_for_json
from ai_2026.sentence_evaluator.model import read_jsonl


def evaluate_sentences(sentencs: list[str], answers: list[bool], model: str = 'grok-simple' ):
    prompt = 'evaluate the sentences below; for each answer True or False depending on whether the sentence is grammatically correct or not; output a python list of these boolean answers'

    prompt = prompt + '\n\n' + '\n'.join(sentencs)
    logger.info(prompt)

    n_prompts = 1
    prompt = prompt_for_json(prompt, required_key='answer')

    n_positives = sum(answers)
    n_negatives = len(answers) - n_positives

    n_proper_positives = 0
    n_proper_negatives = 0

    for _ in range(n_prompts):
        try:
            res, usage = call_ai_model(model, prompt, 'answer')
            logger.info(f'answer: `{res}`')

            # g = '{"answers": ' + res.lower() + '}'
            # w = json.loads(g)

            for r, a in zip(res, answers):
                if a is True and r is True:
                    n_proper_positives += 1
                if not a and not r:
                    n_proper_negatives += 1
        except Exception as e:
            logger.error(e)

        logger.info(f'model: {model}; positives: {n_proper_positives}/{n_positives}, negatives: {n_proper_negatives}/{n_negatives}')



def create_challenge(files: list[str], n_positive: int, n_negative: int) -> tuple[list[str], list[bool]]:
    xx = read_jsonl('assets/causative.jsonl')

    answers = [True] * n_positive + [False] * n_negative
    shuffle(answers)

    sentences = []
    for i, x in enumerate(xx):
        if answers[i]:
            sentences.append(x.sentence_good)
        else:
            sentences.append(x.sentence_bad)
        if len(sentences) == n_positive + n_negative:
            break

    return sentences, answers

if __name__ == '__main__':
    sentences, answers = create_challenge(files=['assets/causative.jsonl'], n_positive=50, n_negative=50)
    evaluate_sentences(sentences, answers, model='gpt')