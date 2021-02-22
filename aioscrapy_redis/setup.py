# encoding=utf-8
import os
import sys
from os.path import dirname, join
try:
    from pip.req import parse_requirements
except:
    from pip._internal.req import parse_requirements


from setuptools import (
    find_packages,
    setup,
)


with open(join(dirname(__file__), './README.md')) as f:
    long_description = f.read()

with open(join(dirname(__file__), './VERSION.txt'), 'rb') as f:
    version = f.read().decode('ascii').strip()
setup(
    name='aioscrapy_redis',
    version=version,
    description='A mini spider framework, Integrate aiohttp into scrapy',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=[]),
    author='道法自然_Tor',
    author_email='1540310556@qq.com',
    license='Apache License v2',
    package_data={'': ['*.*']},
    url='https://github.com/pythonlw/aioscrapy_redis',
    install_requires=[str(ir.req) for ir in parse_requirements("requirements.txt", session=False)],
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
    ],
)
