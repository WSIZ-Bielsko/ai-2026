import json
from random import shuffle

from pydantic import BaseModel

class SentencePair(BaseModel):
    sentence_good: str
    sentence_bad: str
    field: str
    linguistics_term: str
    UID: str
    simple_LM_method: bool
    one_prefix_method: bool
    two_prefix_method: bool
    lexically_identical: bool
    pairID: str

def read_jsonl(path: str) -> list[SentencePair]:
    with open(path) as f:
        return [SentencePair.model_validate(json.loads(line)) for line in f if line.strip()]



if __name__ == '__main__':
    xx = read_jsonl('assets/causative.jsonl')

    n_positive = 10
    n_negative = 10

    answers = [True] * n_positive + [False] * n_negative
    shuffle(answers)

    sentences = []
    for i,x in enumerate(xx):
        if answers[i]:
            sentences.append(x.sentence_good)
        else:
            sentences.append(x.sentence_bad)
        if len(sentences) == n_positive + n_negative:
            break

    for sentence in sentences:
        print(sentence)





