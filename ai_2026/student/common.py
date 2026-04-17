import string
from random import choices


def rnd_id():
    return 'request-' + ''.join(choices(string.ascii_lowercase, k=8))