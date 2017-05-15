from setuptools import setup, find_packages

version = '1.1'

with open('README.md') as file:
    long_description = file.read()

setup(
    name='koppeltaal',
    version=version,
    license='AGPL',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: Dutch',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
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
