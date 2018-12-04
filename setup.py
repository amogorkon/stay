
import sys
sys.path.append("src")
from setuptools import setup, find_packages

from stay import load

with open("META.stay") as f:
    for meta in load(f):
        pass

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()
    
setup(
    PACKAGES=find_packages(where="src"),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    zip_safe=False,
    packages=['stay'],
    **meta
)
