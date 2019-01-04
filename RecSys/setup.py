#!/usr/bin/env python

from distutils.core import setup

setup(name='explicitmf',
      version='1.0',
      description='Explict Matrix Factorization',
      author='CAH',
      author_email='cah@slalom.com',
      url='https://www.github.com/Intellagent/ds-notebooks/',
      packages=['explicitfm' ],
      package_dir={'explicitfm' : 'src/explicitmf' }
)
