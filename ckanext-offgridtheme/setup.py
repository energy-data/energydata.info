#!/usr/bin/env/python
from setuptools import setup

setup(
    name='ckanext-offgridtheme',
    version='0.1',
    description='',
    license='AGPL3',
    author='',
    author_email='',
    url='',
    namespace_packages=['ckanext'],
    packages=['ckanext.offgridtheme'],
    zip_safe=False,
    entry_points = """
        [ckan.plugins]
        offgrid_theme = ckanext.offgridtheme.plugins:CustomTheme
        offgridpages = ckanext.offgridtheme.plugins:OffgridPages
    """
)
