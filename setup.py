""" Setup file.
"""
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

setup(name='semantica_rt_py',
      version=0.1,
      description='semantica_rt_py',
      long_description=README,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pylons",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
      ],
      keywords="web services",
      author='',
      author_email='',
      url='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'cornice',
          'waitress',
          'redis',
          'pymongo',
          'gevent',
          'pastegevent',
          'colander',
          'facebook-sdk'],
      entry_points="""\
    [paste.app_factory]
    main = semantica_rt_py:main
    """,
      paster_plugins=['pyramid'],
)
