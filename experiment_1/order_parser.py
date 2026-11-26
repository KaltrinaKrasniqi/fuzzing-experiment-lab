"""Demonstrative order parser. Monetary amounts are integer cents."""
import json

class OrderValidationError(ValueError):
    pass

def parse_order(raw: bytes, fixed: bool = False) -> dict:
    try:
        order = json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OrderValidationError('Invalid JSON') from exc
    if not isinstance(order, dict) or not isinstance(order.get('items'), list):
        raise OrderValidationError('Order must contain an items list')
    if len(order['items']) > 30:
        raise OrderValidationError('Too many items')
    total = 0
    for item in order['items']:
        if not isinstance(item, dict):
            raise OrderValidationError('Item must be an object')
        quantity = item.get('quantity')
        price = item.get('unit_price_cents')
        if fixed:
            if type(quantity) is not int or type(price) is not int:
                raise OrderValidationError('Quantity and price must be integers')
        else:
            # Deliberate defect: checks the quantity but forgets to check price type.
            if type(quantity) is not int:
                raise OrderValidationError('Quantity must be an integer')
        if quantity <= 0 or quantity > 100 or (type(price) is int and (price < 0 or price > 1_000_000)):
            raise OrderValidationError('Quantity/price outside allowed range')
        total += quantity * price
    return {'total_cents': total, 'item_lines': len(order['items'])}
