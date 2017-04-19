# python setup.py sdist upload
from setuptools import setup

setup(
    name='canister',
    version='1.4.3',
    description='A bottle wrapper to provide logging, sessions and authentication.',
    url='https://github.com/dagnelies/canister',
    author='Arnaud Dagnelies',
    author_email='arnaud.dagnelies@gmail.com',
    license='MIT',
    keywords='bottle server webserver session logging authentication',
    py_modules=['canister'],
    scripts=['canister.py'],
    install_requires=[
        'bottle',
        'PyJWT'
    ],
)