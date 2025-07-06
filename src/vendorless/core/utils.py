import os
from contextlib import contextmanager

@contextmanager
def change_cwd(new_cwd):
    prev_dir = os.getcwd()
    try:
        os.chdir(new_cwd)
        yield
    finally:
        os.chdir(prev_dir)