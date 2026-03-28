import json

if __name__ == '__main__':
    s = '[False, False, True, False, True, False, True, False, True, True, True, False, True, True, True, False, False, True, True, False]'
    g = '{"answers": ' + s.lower() + '}'
    w = json.loads(g)
    print(g)

    print(w)
    gg = w['answers']
    print(type(gg[0]))