"""Loyalty points and discounts; fixed integer-cent business rules."""
import json

class BusinessInputError(ValueError):
    pass

class OracleMismatch(AssertionError):
    pass

def decode_order(data: bytes) -> dict:
    try:
        order = json.loads(data.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BusinessInputError('Invalid JSON') from exc
    if not isinstance(order, dict):
        raise BusinessInputError('Expected object')
    qty, price, coupon = order.get('quantity'), order.get('unit_price_cents'), order.get('coupon', 'NONE')
    if type(qty) is not int or not 1 <= qty <= 50 or type(price) is not int or not 1 <= price <= 100_000:
        raise BusinessInputError('Invalid quantity or price')
    if coupon not in ('NONE', 'SAVE10'):
        raise BusinessInputError('Unknown coupon')
    return {'quantity':qty, 'unit_price_cents':price, 'coupon':coupon}

def reference(order:dict) -> dict:
    qty = order['quantity']; subtotal = qty * order['unit_price_cents']
    discount = subtotal // 10 if order['coupon'] == 'SAVE10' and subtotal >= 2000 else 0
    return {'total_cents':subtotal-discount, 'points':qty+(qty//3)}

def calculate(order:dict, fixed=False)->dict:
    qty = order['quantity']; subtotal = qty*order['unit_price_cents']
    discount = subtotal // 10 if order['coupon']=='SAVE10' and subtotal >= 2000 else 0
    # Deliberate off-by-one defect at bonus thresholds.
    bonus = qty//3 if fixed else max(0,(qty-1)//3)
    return {'total_cents':subtotal-discount, 'points':qty+bonus}

def test_order(data:bytes,fixed=False):
    try:
        order = decode_order(data)
    except BusinessInputError:
        return
    actual = calculate(order,fixed)
    expected = reference(order)
    if actual != expected:
        raise OracleMismatch(f'order={order}; actual={actual}; expected={expected}')
