import os
import json
from setuptools import setup
from setuptools import find_packages

MY_DIRECTORY = os.path.dirname(__file__)
with open(os.path.join(MY_DIRECTORY, 'package_data.json'), 'r+') as f:
    package_data = json.load(f)

setup(
    name='cauldron',
    version=package_data['version'],
    description='Un-Notebook Data Science',
    url='https://github.com/sernst/cauldron',
    author='Scott Ernst',
    author_email='swernst@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    zip_safe=False,
    scripts=['bin/cauldron'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.5',

        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    install_requires=[
        'plotly',
        'pandas',
        'numpy',
        'six',
        'jinja2',
        'markdown',
        'pygments',
        'pyquery'
    ]
)
