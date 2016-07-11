import os
import json
from setuptools import setup
from setuptools import find_packages

# python3 setup.py register -r pypitest

# python3 setup.py sdist bdist_wheel
# twine upload dist/cauldron_notebook-0.0.1*

MY_DIRECTORY = os.path.dirname(__file__)
with open(os.path.join(MY_DIRECTORY, 'package_data.json'), 'r+') as f:
    package_data = json.load(f)

setup(
    name='cauldron-notebook',
    version=package_data['version'],
    description='The Un-Notebook Notebook: Scientific Analysis Environment',
    url='https://github.com/sernst/cauldron',
    author='Scott Ernst',
    author_email='swernst@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    zip_safe=False,
    scripts=[
        'bin/cauldron',
        'bin/cauldron-server'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.5',

        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    install_requires=[
        'pandas',
        'numpy',
        'jinja2',
        'markdown',
        'pygments',
        'beautifulsoup4',
        'flask'
    ],
    extras_require={
        'plotly': ['plotly'],
        'matplotlib': ['matplotlib'],
        'bokeh': ['bokeh'],
        'seaborn': ['seaborn']
    },
    test_suite='nose.collector',
    tests_require=['nose', 'nose-cover3']
)
