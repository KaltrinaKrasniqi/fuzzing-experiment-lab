"""Zero external dependencies; check both versions and boundary behavior."""
from pathlib import Path
import sys, json
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'experiment_1'))
sys.path.insert(0,str(ROOT/'experiment_2'))
from order_parser import parse_order, OrderValidationError
from loyalty_rules import decode_order, test_order, calculate, reference, OracleMismatch, BusinessInputError

def check():
    valid=b'{"items":[{"quantity":2,"unit_price_cents":1550}]}'
    assert parse_order(valid, True)=={'total_cents':3100,'item_lines':1}
    trigger=b'{"items":[{"quantity":2,"unit_price_cents":null}]}'
    try: parse_order(trigger,False)
    except TypeError: pass
    else: raise AssertionError('Experiment 1 buggy defect not reproduced')
    try: parse_order(trigger,True)
    except OrderValidationError: pass
    else: raise AssertionError('Experiment 1 fixed version did not reject input')
    for raw in (b'{', b'[]', b'{"items":{}}',b'{"items":[{"quantity":0,"unit_price_cents":200}]}'):
        for fixed in (False,True):
            try: parse_order(raw,fixed)
            except OrderValidationError: pass
            else: raise AssertionError(f'Unexpected accepted input {raw}')
    trigger2=b'{"quantity":3,"unit_price_cents":1000,"coupon":"NONE"}'
    try: test_order(trigger2,False)
    except OracleMismatch: pass
    else: raise AssertionError('Experiment 2 buggy defect not reproduced')
    test_order(trigger2,True)
    for q in [1,2,3,4,5,6,9,10,12,49,50]:
        for coupon in ('NONE','SAVE10'):
            order=decode_order(json.dumps({'quantity':q,'unit_price_cents':1000,'coupon':coupon}).encode())
            assert calculate(order,True)==reference(order)
    print('PASS: Python E1/E2: buggy triggers, fixed behavior and boundary cases')
if __name__=='__main__':check()
