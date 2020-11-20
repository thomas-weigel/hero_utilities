# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


setup(
        name='hdconvert',
        version='0.3.3',
        description='A collection of command line utilities for HERO system.',
        long_description=readme,

        packages=find_packages(),
        scripts=['bin/hd-convert',],

        author='Thomas Weigel',
        author_email='thomas.weigel@chantofwaves.com',
        url='https://github.com/thomas-weigel/hero_utilities',
        license=license
    )
