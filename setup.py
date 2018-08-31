from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='ctqa',
    version='0.9.2',
    url='https://github.com/brikwerk/ctqa',
    license='GNU General Public License (GPL)',
    author='Reece Walsh',
    setup_requires=["pytest-runner"],
    tests_require=['pytest'],
    install_requires=['httplib2>=0.11.1',
                    'numpy>=1.14.3',
                    'pydicom>=1.0.2',
                    'pillow>=5.1.0',
                    'pytest>=3.6.3',
                    'pyinstaller>=3.3.1',
                    'matplotlib>=2.2.2',
                    'sphinx>=1.7.7',
                    'sphinx-rtd-theme>=0.4.1',
                    'exchangelib>=1.11.4',
                    'cryptography>=2.3.1'
                    ],
    cmdclass={'test': PyTest},
    author_email='reece@brikwerk.com',
    description='Automated auditing and report generation for CT quality assurance',
    long_description=long_description,
    packages=['ctqa'],
    include_package_data=True,
    platforms='any',
    test_suite='test.test_ctqa',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 2 - Beta',
        'Natural Language :: English',
        'Environment :: Other Environment',
        'Intended Audience :: Healthcare Industry',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
        ],
    extras_require={
        'testing': ['pytest'],
    }
)