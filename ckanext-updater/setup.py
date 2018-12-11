# -*- coding: utf-8 -*-
from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='''ckanext-updater''',

    version='0.0.1',

    description='''Automatic updating for CKAN resources with reports''',
    long_description=long_description,

    url='https://github.com/sandermi/ckanext-updater',

    author='''Laastutabloo''',
    author_email='''no@email.sry''',

    license='AGPL',

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='''CKAN update''',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    namespace_packages=['ckanext'],
    install_requires=[],
    include_package_data=True,
    package_data={
    },
    data_files=[],
    entry_points='''
        [ckan.plugins]
        updater=ckanext.updater.plugin:UpdaterPlugin

        [babel.extractors]
        ckan = ckan.lib.extract:extract_ckan
    ''',
    message_extractors={
        'ckanext': [
            ('**.py', 'python', None),
            ('**.js', 'javascript', None),
            ('**/templates/**.html', 'ckan', None),
        ],
    }
)

#update_report = ckanext.updater.plugin:UpdaterReportPlugin
