====================
H5PP 
HTML5 Package Python
====================

H5PP is a port of H5P to the Python language and the web framework Django.
H5P makes it easy to create, share and reuse HTML5 content and applications. Authors may create and edit interactive videos, presentations, games, advertisements and more. Content may be imported and exported. All that is needed to view or edit H5P content is a web browser. 

Quick start
-----------

1. Add 'H5PP' to your INSTALLED_APPS setting like this::

	INSTALLED_APPS = [
		...
		'H5PP',
	]

2. Include the H5PP URLconf in your project urls.py like this::

	url(r'^h5p/', include('h5pp.urls'))

3. Run `python manage.py migrate` to create the H5PP models.

4. Start the development server and visit http://127.0.0.1:8000/h5p/home to acces to the control panel of H5PP. Go to '/h5p/libraries' and install the H5P content libraries. You can find official release of H5P at https://h5p.org/update-all-content-types at the end of the document.

5. Visit http://127.0.0.1:8000/h5p/create to create new H5P contents.