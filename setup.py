#!/usr/bin/python3
# -*- coding=utf-8 -*-
r"""

"""
import sys; sys.path.append('./src')  # noqa
import setuptools
from debuglib import __author__, __version__, __description__, __license__


install_requires = []

dev_requires = ["better-exceptions"]  # better exceptions formatting
# msgpack_requires = ["msgpack"]  # faster transmission
orjson_requires = ["orjson"]  # fast packing/unpacking
cli_requires = ["textual"]  # CLI-Interface
all_requires = [dev_requires, orjson_requires, cli_requires]

extras_require = {
    'dev': dev_requires,
    # 'msgpack': msgpack_requires,
    'orjson': orjson_requires,
    'cli': cli_requires,
    'all': all_requires,
}


setuptools.setup(
    name="debuglib",
    version=__version__,
    description=__description__,
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author=__author__,
    license=__license__,
    url="https://github.com/utility-libraries/debuglib-py",
    project_urls={
        "Author Github": "https://github.com/PlayerG9",
        "Homepage": "https://github.com/utility-libraries/debuglib-py",
        # "Documentation": "https://utility-libraries.github.io/debuglib-py/",
        "Bug Tracker": "https://github.com/utility-libraries/debuglib-py/issues",
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "debuglib = debuglib.__main__:main"
        ]
    },
)
