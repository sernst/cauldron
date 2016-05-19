from setuptools import setup

setup(
    name='cauldron',
    version='0.1',
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
