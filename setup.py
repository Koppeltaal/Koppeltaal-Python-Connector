from setuptools import setup, find_packages

version = '1.1.dev0'

setup(
    name='koppeltaal',
    version=version,
    license='AGPL',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'lxml',
        'python-dateutil',
        'requests >= 2.5.1',
        'zope.interface >= 3.7.0',
        ],
    extras_require={
        'test': [
            'PyHamcrest',
            'mock',
            'selenium',
            ],
        },
    entry_points={
        'console_scripts': [
            'koppeltaal = koppeltaal.console:console'
            ],
        }
    )
