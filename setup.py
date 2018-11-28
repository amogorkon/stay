
import sys
sys.path.append("src")
from setuptools import setup, find_packages

from stay import load

with open("META.stay") as f:
    for meta in load(f):
        pass

with open("README.rst") as f:
    LONG_DESCRIPTION = f.read()
    
def setup(*args, **kwargs):
    print(args)
    print(kwargs)

setup(
    PACKAGES=find_packages(where="src"),
    long_description=LONG_DESCRIPTION,
    package_dir={"": "src"},
    zip_safe=False,
    **meta
)