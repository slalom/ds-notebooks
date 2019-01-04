#!/usr/bin/env python

from distutils.core import setup

setup(name='explicitmf',
      version='1.0',
      description='Explict Matrix Factorization',
      author='CAH',
      author_email='cah@slalom.com',
      url='https://www.github.com/Intellagent/ds-notebooks/',
      packages=[
		'boto3',
		'cufflinks==0.8.2',
		'matplotlib', 
		'numpy', 
		'plotly',
		'scipy', 
		'sagemaker'
     ],
)
