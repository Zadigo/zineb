#!/usr/bin/env python

import re
from os import path

import setuptools

ROOT = path.abspath(path.dirname(__file__))

def read_files(filename):
    try:
        with open(path.join(ROOT, filename), 'rb', encoding='utf-8') as f:
            data = f.read()
            return data.strip()
    except:
        pass


classifiers = [
    'Development Status :: 3 - Alpha',

    'Environment :: Console',

    'License :: OSI Approved :: MIT License',

    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows :: Windows 10',

    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.9',

    'Natural Language :: English',

    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',

    'Topic :: Internet',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

install_requires = [
    'beautifulsoup4>=4.9.3',
    'jupyter',
    'numpy',
    'Pillow>=8.0.1',
    'pyyaml',
    'requests',
    'w3lib',
    # 'pandas',
    # 'numpy==1.19.3',
    # 'PyDispatcher',
    # 'nltk',
    # 'scikit-learn'
]

setuptools.setup(
    name='zineb-scrapper',
    # packages: [],
    version='6.0.2',
    # version=read_files('version.txt'),
    author='John Pendenque',
    author_email='pendenquejohn@gmail.com',
    classifiers=classifiers,
    description='Advanced web scrapper for machine learning and data science buit around BeautifulSoup and Pandas',
    install_requires=install_requires,
    keywords=['python', 'web scrapping', 'scrapping'],
    license='MIT',
    long_description=read_files('README.md'),
    long_description_content_type='text/markdown',
    python_requires='>=3.9',
    project_urls={
        'Source': 'https://github.com/Zadigo/zineb/',
        'Tracker': 'https://github.com/Zadigo/zineb/issues'
    }
)
