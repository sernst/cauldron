import glob
import json
import os

from setuptools import find_packages
from setuptools import setup

MY_DIRECTORY = os.path.dirname(__file__)
with open(os.path.join(MY_DIRECTORY, 'cauldron', 'settings.json'), 'r') as f:
    settings = json.load(f)


def readme():
    """Returns the contents of the package README.rst."""
    path = os.path.realpath(os.path.join(
        os.path.dirname(__file__),
        'README.rst'
    ))
    with open(path) as f:
        return f.read()


def populate_extra_files():
    """
    Creates a list of non-python data files to include in package distribution
    """
    out = ['cauldron/settings.json']

    for entry in glob.iglob('cauldron/resources/**/*', recursive=True):
        out.append(entry)

    return out


setup(
    name='cauldron-notebook',
    version=settings['version'],
    description='The Unnotebook: Data Analysis Environment',
    long_description=readme(),
    keywords=[
        'Data', 'Analysis', 'Visualization',
        'Interactive', 'Interpreter', 'Shell'
    ],
    url='https://github.com/sernst/cauldron',
    author='Scott Ernst',
    author_email='swernst@gmail.com',
    license='MIT',
    platforms='Linux, Mac OS X, Windows',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    package_data={'': populate_extra_files()},
    include_package_data=True,
    zip_safe=False,
    entry_points=dict(
        console_scripts=['cauldron=cauldron.invoke:run']
    ),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',

        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',

        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Scientific/Engineering :: Information Analysis'
    ],
    install_requires=[
        'pandas',
        'numpy',
        'jinja2',
        'markdown',
        'pygments',
        'beautifulsoup4',
        'flask',
        'requests',
        'waitress',
    ],
    extras_require={
        'plotly': ['plotly'],
        'matplotlib': ['matplotlib', 'beautifulsoup4'],
        'bokeh': ['bokeh'],
        'seaborn': ['seaborn'],
        'plotting': [
            'plotly',
            'matplotlib',
            'beautifulsoup4',
            'bokeh',
            'seaborn',
        ],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov']
)
