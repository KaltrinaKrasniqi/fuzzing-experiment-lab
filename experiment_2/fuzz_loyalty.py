import sys
import atheris
from loyalty_rules import test_order

FIXED=sys.argv[1]=='fixed'
def TestOneInput(data:bytes):
    test_order(data,FIXED)
atheris.instrument_all()
atheris.Setup([sys.argv[0], *sys.argv[2:]],TestOneInput)
atheris.Fuzz()
