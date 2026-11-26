import math
import sys

import atheris

with atheris.instrument_imports():
    from text_stats import average_word_length, average_word_length_buggy


def main():
    version = sys.argv.pop(1)
    functions = {"buggy": average_word_length_buggy, "fixed": average_word_length}
    target = functions[version]
    calls = 0

    def test_one_input(data):
        nonlocal calls
        calls += 1
        try:
            text = data.decode("utf-8", errors="replace")
            result = target(text)
            assert math.isfinite(result) and 0 <= result <= len(text)
        except Exception:
            print(f"Callbacks on failure: {calls}", file=sys.stderr, flush=True)
            raise

    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
