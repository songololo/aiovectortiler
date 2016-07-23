from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
from os import path

import aiovectortiler

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def is_pkg(line):
    return line and not line.startswith(('--', 'git', '#'))

with open('requirements.txt', encoding='utf-8') as reqs:
    install_requires = [l for l in reqs.read().split('\n') if is_pkg(l)]

setup(
    name='aiovectortiler',
    version=aiovectortiler.__version__,
    description=aiovectortiler.__doc__,
    long_description=long_description,
    url=aiovectortiler.__homepage__,
    author=aiovectortiler.__author__,
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: GIS',

        'Programming Language :: Python :: 3.5',
    ],
    keywords='openstreetmap vectortile postgis asyncio',
    packages=find_packages(exclude=['tests']),
    install_requires=install_requires,
    extras_require={'test': ['pytest'], 'docs': 'mkdocs'},
    include_package_data=True,
)
