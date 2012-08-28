#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='xbob.db.mobio',
    version='1.0.0a1',
    description='MOBIO Database Access API for Bob',
    url='http://github.com/bioidiap/xbob.db.mobio',
    license='GPLv3',
    author='Laurent El Shafey',
    author_email='laurent.el-shafey@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=[
      'setuptools',
      'bob',  # base signal proc./machine learning library
    ],

    namespace_packages = [
      'xbob',
      'xbob.db',
      ],

    entry_points = {
      # bob database declaration
      'bob.db': [
        'mobio = xbob.db.mobio.driver:Interface',
        ],

      # bob unittest declaration
      'bob.test': [
        'mobio = xbob.db.mobio.test:MobioDatabaseTest',
        ],
      },

    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Database :: Front-Ends',
      ],
)