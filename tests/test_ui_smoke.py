"""Dependency-free structural smoke test of all app routes.

The fake Streamlit verifies Python routing and access to data and callbacks.
It does not emulate Streamlit's actual widget rendering or a browser.
"""
from __future__ import annotations
import contextlib
import runpy
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ('Overview', 'Explore experiments', 'Run lab', 'Research connection')

class FakeWidget:
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def __getattr__(self, name):
        if name in {'NumberColumn'}: return lambda **kw: None
        return lambda *a, **kw: None

class FakeStreamlit(types.ModuleType):
    def __init__(self, page, experiment=1, stage=0):
        super().__init__('streamlit')
        self.page = page
        self.experiment = experiment
        self.stage = stage
        self.session_state = {}
        self.column_config = FakeWidget()
        self.calls = []
    def __getattr__(self, name):
        def call(*args, **kwargs):
            self.calls.append((name, args[:1]))
            if name in ('columns','tabs'):
                count = len(args[0]) if isinstance(args[0], (list,tuple)) else args[0]
                return [FakeWidget() for _ in range(count)]
            if name in ('container','expander','status','spinner'):
                return FakeWidget()
            if name == 'radio':
                if kwargs.get('key') == 'main_page': return self.page
                return args[1][0] if len(args)>1 else kwargs['options'][0]
            if name in ('selectbox','select_slider'):
                options = args[1] if len(args)>1 else kwargs['options']
                return options[(self.stage if args and args[0]=='Paper A phase' else self.experiment-1 if args and args[0]=='Select a target' else kwargs.get('index', 0))]
            if name == 'slider': return kwargs.get('value', 3)
            if name == 'number_input': return kwargs.get('value', 2)
            if name in ('checkbox','button'): return False
            return None
        return call

def main():
    sys.path.insert(0, str(ROOT))
    for page in PAGES:
        fake = FakeStreamlit(page)
        sys.modules['streamlit'] = fake
        runpy.run_path(str(ROOT/'app.py'), run_name='__main__')
        print(f'PASS fake-route: {page} ({len(fake.calls)} mocked widget calls)')
    for experiment in (2, 3, 4):
        fake = FakeStreamlit('Explore experiments', experiment=experiment)
        sys.modules['streamlit'] = fake
        runpy.run_path(str(ROOT/'app.py'), run_name='__main__')
        print(f'PASS fake-route: Explore experiment {experiment}')
    for stage in range(1, 5):
        fake = FakeStreamlit('Research connection', stage=stage)
        sys.modules['streamlit'] = fake
        runpy.run_path(str(ROOT/'app.py'), run_name='__main__')
        print(f'PASS fake-route: Research stage {stage+1}')
    sys.modules.pop('streamlit', None)

if __name__ == '__main__': main()
