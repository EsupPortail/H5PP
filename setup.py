import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
	README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
	name='H5PP',
	version='0.1',
	packages=find_packages(),
	include_package_data=True,
	license='GPL License',
	description='A Python version of H5P software.',
	long_description=README,
	author='OBLED Joel',
<<<<<<< HEAD
	author_email='joel.obled@univ-lille1.fr',
=======
	author_email='obled.joel@gmail.com',
>>>>>>> f7d4fe8dedacadf4f816963a06e5237e92fc36ed
	classifiers=[
		'Environment :: Web Environment',
		'Framework :: Django',
		'Framework :: Django :: 1.8',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GPL License',
		'Operating System :: Linux',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.7.9',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet :: WWWW/HTTP :: Dynamic Content',
	],
)