from setuptools import setup

setup(
    name='pyci',
    version='0.3.0',
    author='Tazovsky',
    license='MIT',
    packages=['pyci'],
    package_data={
        'pyci': ['data/scripts/*.sh'],
        'pyci': ['data/scripts/*.py']
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    zip_safe=False,
    include_package_data=True
)
