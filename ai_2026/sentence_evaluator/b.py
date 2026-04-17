from random import shuffle


def foo():
    original_sentences = [
        "The quick brown fox jumps over the lazy dog.",
        "She enjoys reading books in the park.",
        "A strong wind blew down the old oak tree.",
        "He is saving money to buy a new car.",
        "They arrived at the station just in time.",
        "The chef prepared a delicious meal for the guests.",
        "I need to finish this project by tomorrow.",
        "The children are playing happily in the backyard.",
        "She found a rare coin on the beach.",
        "Learning a new language takes time and patience."
    ]

    synonymous_sentences = [
        "The swift brown fox leaps above the sluggish hound.",
        "She loves going through novels outdoors.",
        "The ancient oak was toppled by a fierce gale.",
        "He is setting aside cash to purchase a new vehicle.",
        "They reached the depot at the exact right moment.",
        "The cook crafted a tasty dinner for the attendees.",
        "This assignment must be completed by me before the next day.",
        "The kids are joyfully frolicking behind the house.",
        "She discovered an uncommon piece of currency by the ocean.",
        "Acquiring a foreign tongue requires dedication and endurance."
    ]
    dd = synonymous_sentences.copy()
    shuffle(dd)

    print(f'a={original_sentences}')
    print(f'b={dd}')
    print(sum([x == y for (x,y) in zip(dd, synonymous_sentences)]))

if __name__ == '__main__':
    foo()