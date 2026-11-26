def average_word_length_buggy(text: str) -> float:
    words = text.split()
    return sum(map(len, words)) / len(words)


def average_word_length(text: str) -> float:
    words = text.split()
    if not words:
        return 0.0
    return sum(map(len, words)) / len(words)
