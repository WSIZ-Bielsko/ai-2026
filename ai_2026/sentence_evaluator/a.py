import json
from random import randint, choices


def foo():
    w = [randint(100,200) for _ in range(50)]
    print(w)
    print(sum(w))

if __name__ == '__main__':
    N = 10
    a, b = choices([0,1,2], k=N), choices([0,1,2], k=N)
    print(f'{a=}')
    print(f'{b=}')
    print(sum(aa == bb for (aa,bb) in zip(a,b)))