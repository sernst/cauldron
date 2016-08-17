import os
import json
import glob
from setuptools import setup
from setuptools import find_packages

# python3 setup.py register -r pypitest

# rm -rf ./dist
# python3 setup.py sdist bdist_wheel
# twine upload dist/cauldron*

MY_DIRECTORY = os.path.dirname(__file__)
with open(os.path.join(MY_DIRECTORY, 'cauldron', 'settings.json'), 'r+') as f:
    settings = json.load(f)


def populate_extra_files():
    """
    Creates a list of non-python data files to include in package distribution
    """

    out = ['cauldron/settings.json']

    for entry in glob.iglob('cauldron/resources/examples/**/*', recursive=True):
        out.append(entry)

    for entry in glob.iglob('cauldron/resources/templates/**/*', recursive=True):
        out.append(entry)

    for entry in glob.iglob('cauldron/resources/web/**/*', recursive=True):
        out.append(entry)

    return out

setup(
    name='cauldron-notebook',
    version=settings['version'],
    description='The Un-Notebook Notebook: Scientific Analysis Environment',
    url='https://github.com/sernst/cauldron',
    author='Scott Ernst',
    author_email='swernst@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    package_data={'': populate_extra_files()},
    include_package_data=True,
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
