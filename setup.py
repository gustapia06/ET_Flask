from setuptools import setup, find_packages, Extension

ext = Extension('ET_Flask.ETlib', sources = ['ET_Flask/ETlib.c'])

setup(
      name='ET_Flask',
      version='0.1',
      description='Eagar Tsai Solver website',
      author='Gustavo Tapia',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
                        'flask',
                        'pandas',
                        'numpy',
                        'gunicorn',
                        'scipy',
                        ],
      setup_requires=[
                      'pytest-runner',
                      ],
      ext_modules=[ext],
      tests_require=[
                     'pytest',
                     ],
      )
