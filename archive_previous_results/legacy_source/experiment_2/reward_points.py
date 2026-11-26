def points_buggy(items: int) -> int:
    return items + (items // 3 if items > 3 else 0)


def points_fixed(items: int) -> int:
    return items + items // 3


def points_reference(items: int) -> int:
    total = 0
    for position in range(1, items + 1):
        total += 1
        if position % 3 == 0:
            total += 1
    return total


def decode_items(data: bytes) -> int:
    return data[0] if data else 0
