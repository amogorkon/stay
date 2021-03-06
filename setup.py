
from setuptools import setup, find_packages

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()
  
setup(
	name="stay",
    py_modules=["stay"],
	description="Simple, even Trivial Alternative to Yaml",
	license="MIT",
	url="https://github.com/amogorkon/stay",
	version="0.3.3post4",
	author="Anselm Kiefner",
	author_email="stay-pypi@anselm.kiefner.de",
	python_requires=">3.6",
	keywords=["json", "yaml", "toml", "config", "simple", "alternative"],
	classifiers=[
	"Development Status :: 4 - Beta",
	"Intended Audience :: Developers",
	"Natural Language :: English",
	"License :: OSI Approved :: MIT License",
	"Operating System :: OS Independent",
	"Programming Language :: Python :: 3 :: Only",
	"Programming Language :: Python :: Implementation :: CPython",
	"Topic :: Text Processing :: Markup"],
    packages=find_packages(where="src/stay"),
	package_dir={"": "src/stay",},
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    zip_safe=False,
)
