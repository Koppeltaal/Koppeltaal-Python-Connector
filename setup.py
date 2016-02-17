from setuptools import setup, find_packages

version = '1.0dev'

setup(
    name='koppeltaal',
    version=version,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'feedgen == 0.3.1.dev',
        'feedreader',
        'koppeltaal_schema',
        'lxml',
        'requests >= 2.5.1',
        'zope.interface >= 3.7.0',
        ],
    entry_points={
        'console_scripts': [
            'koppeltaal = koppeltaal.cli:cli'
            ],
        }
    )
