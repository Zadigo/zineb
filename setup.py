#!/usr/bin/env python

from os import path

import setuptools



ROOT = path.abspath(path.dirname(__file__))

def read_files(filename):
    with open(path.join(ROOT, filename), 'r', encoding='utf-8') as f:
        data = f.read()
        return data


classifiers = [
    'Development Status :: 2 - Pre-Alpha',

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
    'numpy==1.19.3',
    'requests>=2.25.1',
    'Pillow>=8.0.1',
    'jupyter>=4.7.0',
    'pandas>=1.1.5',
    'PyDispatcher>=2.0.5',
    'w3lib>=1.22.0',
    'nltk>=3.4.4'
]


setuptools.setup(
    name='zineb',
    # packages: [],
    version='1.0.3',
    author='John Pendenque',
    author_email='pendenquejohn@gmail.com',
    description='Advanced web scrapper for machine learning and data science',
    license='MIT',
    long_description=read_files('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/Zadigo/zineb/releases/tag/1.0.3-pre-alpha',
    classifiers=classifiers,
    keywords=['python', 'web scrapping', 'scrapping'],
    python_requires='>=3.9'
)
