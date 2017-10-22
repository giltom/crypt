from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'Test app',
  ext_modules = cythonize("loadstats.pyx"),
)
