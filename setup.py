"""
    Setup library for the package.
"""
from setuptools import find_packages, setup

setup(
    name='discobra',
    packages=find_packages(include=['discord']),
    version='0.0.1',
    description='A fast, easy to use Discord API wrapper.',
    author='mounderfod, mjk134',
    license='MIT',
)
