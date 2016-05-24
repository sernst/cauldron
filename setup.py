import os
import json
from setuptools import setup

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
    packages=['cauldron'],
    zip_safe=False,
    scripts=['bin/cauldron'],
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
