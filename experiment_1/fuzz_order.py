import sys
import atheris
from order_parser import parse_order, OrderValidationError

FIXED = sys.argv[1] == 'fixed'

def TestOneInput(data: bytes) -> None:
    try:
        parse_order(data, fixed=FIXED)
    except OrderValidationError:
        return  # Expected input rejection, not a crash.

atheris.instrument_all()
atheris.Setup([sys.argv[0], *sys.argv[2:]], TestOneInput)
atheris.Fuzz()
