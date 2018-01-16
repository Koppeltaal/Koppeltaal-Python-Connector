import sys

from setuptools import setup, find_packages


version = '1.2.2.dev0'


with open('README.md') as file:
    long_description = file.read()


tests_require = [
    'PyHamcrest >= 1.9',
    'selenium >= 3.8',
    ]


if sys.version_info.major == 2:
    tests_require.append('mock==1.0.1')


setup(
    name='koppeltaal',
    version=version,
    license='AGPL',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    long_description=long_description,
    author='Koppeltaal community',
    url='https://github.com/Koppeltaal/Koppeltaal-Python-Connector',
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
        'configparser',
        'future',
        'lxml',
        'python-dateutil',
        'requests',
        'setuptools',
        'zope.interface >= 4.4',
        ],
    extras_require={'test': tests_require},
    entry_points={
        'console_scripts': [
            'koppeltaal = koppeltaal.console:console'
            ],
        }
    )
