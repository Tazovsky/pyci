from setuptools import setup

setup(
    name='pyci',
    version='0.1.1',
    author='Tazovsky',
    license='MIT',
    packages=['pyci'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    zip_safe=False,
    include_package_data=True
)
