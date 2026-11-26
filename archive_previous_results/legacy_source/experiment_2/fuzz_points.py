import sys

import atheris

with atheris.instrument_imports():
    from reward_points import decode_items, points_buggy, points_fixed, points_reference


class OracleMismatch(AssertionError):
    pass


def main():
    target = {"buggy": points_buggy, "fixed": points_fixed}[sys.argv.pop(1)]

    def test_one_input(data):
        items = decode_items(data)
        actual = target(items)
        expected = points_reference(items)
        if actual != expected:
            raise OracleMismatch(f"items={items}, actual={actual}, expected={expected}")

    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
