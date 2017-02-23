## ====================
# H5PP
## HTML5 Package Python
## ====================
H5PP is a port of H5P by Joubel to the Python language and the web framework Django. H5P makes it easy to create, share and reuse HTML5 content and applications. Authors may create and edit interactive video, presentations, games, advertisements and more. Content may be imported and exported. All that is needed to view or edit H5P content is a web browser.

## Quick start
1. Add 'h5pp' to your INSTALLED_APPS settings like this :
<pre><code>
INSTALLED_APPS = [
  ...
  'h5pp',
]
</code></pre>

2. Include the h5pp Urlconf in your project urls.py like this :
<pre><code>
url(r'^h5p/', include('h5pp.urls'))
</code></pre>

3. Include these variables into the settings.py file of your Django project :
<pre><code>
\# Login related settings
LOGIN_URL = '/h5p/login'
LOGIN_REDIRECT_URL = '/h5p'

\# H5P Version
H5P_VERSION = '7.x'
\# H5P : Enable development mode or not
H5P_DEV_MODE = 0
\# H5P path and url
H5P_PATH = os.path.join(BASE_DIR, 'h5pp/static/h5p')
H5P_URL = '/h5p/'
\# H5P save frequency
H5P_SAVE = 30
\# H5P export content path
H5P_EXPORT = '/exports/'
\# H5P language
H5P_LANGUAGE = 'en'
</code></pre>

4. If not already done. Make a 'media' directory at the root of your Django project.

5. Run 'python manage.py migrate' to create the h5pp models.

6. Start the development server and visit http://127.0.0.1:8000/h5p/home/ to access to the main menu of h5pp. Go to libraries to install the officiel H5P Release from h5p.org.

7. Visit http://127.0.0.1:8000/h5p/create/ to create or upload new H5P contents.

## Beta version
This version of H5P is a beta. Many things have to be corrected, code need to be optimized and currently the project is being tested. So we can not ensure the stability of the project until the end of the beta phase.

## Docs

The documentation of this port of H5P is being writted. For the moment here is the official documentation of the original version of H5P : https://h5p.org/documentation

## ====================

H5P git repositories : https://github.com/h5p <br>
H5P official website : https://h5p.org/ <br>
Joubel officiel website : https://joubel.com/ 
