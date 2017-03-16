from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from h5pp.h5p.h5pclasses import H5PDjango
from h5pp.h5p.library.h5pdefaultstorage import H5PDefaultStorage
from h5pp.h5p.editor.library.h5peditorstorage import H5PEditorStorage
from h5pp.models import *
import shutil
import os

##
# Tests for h5p library classes
##
class CoreTestCase(TestCase):

	def setUp(self):
		library = h5p_libraries.objects.create(
			library_id='1',
			machine_name='H5P.Test',
			title='Test',
			major_version=1,
			minor_version=1,
			patch_version=2,
			runnable=1,
			fullscreen=0,
			embed_types='',
			preloaded_js="[u'scripts/test.js']",
			preloaded_css="[u'styles/test.css']",
			drop_library_css=None,
			semantics='',
			restricted=0,
			tutorial_url=''
		)
		test = User.objects.create(
			username='titi'
		)
		print('setUp of CoreTestCase ---- Ready')

	def test_save_content(self):
		user = User.objects.get(username='titi')
		interface = H5PDjango(user)
		core = interface.h5pGetInstance('core')
		content = {
			'id': 1,
			'title': 'ContentTest',
			'params': '',
			'library': {
				'libraryId': 1,
				'machineName': 'H5P.Test',
				'majorVersion': 1,
				'minorVersion': 1
			},
			'disable': 0,
		}

		core.saveContent(content)
		result = h5p_contents.objects.values()

		self.assertTrue(result.exists())

		del(content['id'])
		content['title'] = 'ContentTest2'

		core.saveContent(content)
		result = h5p_contents.objects.values()

		self.assertTrue(result[1]['title'] == 'ContentTest2')
		print('test_save_content ---- Check')

	def test_load_content(self):
		user = User.objects.get(username='titi')
		interface = H5PDjango(user)
		core = interface.h5pGetInstance('core')
		content = {
			'id': 1,
			'title': 'ContentTest',
			'params': '',
			'library': {
				'libraryId': 1,
				'machineName': 'H5P.Test',
				'majorVersion': 1,
				'minorVersion': 1
			},
			'disable': 0,
		}

		interface.insertContent(content)
		result = core.loadContent(1)

		self.assertTrue(result['library']['contentId'] == 1)
		self.assertTrue(result['library']['id'] == 1)
		self.assertTrue(result['library']['name'] == 'H5P.Test')
		self.assertFalse('library_id' in result)
		print('test_load_content ---- Check')

	def test_load_library(self):
		user = User.objects.get(username='titi')
		interface = H5PDjango(user)
		core = interface.h5pGetInstance('core')

	def test_load_library(self):
		user = User.objects.get(username='titi')
		interface = H5PDjango(user)
		core = interface.h5pGetInstance('core')

		result = core.loadLibrary('H5P.Test', 1, 1)

		self.assertEqual(1, result['library_id'])
		print('test_load_library ---- Check')

class StorageTestCase(TestCase):

	def setUp(self):
		library = h5p_libraries.objects.create(
			library_id=1,
			machine_name='H5P.Test',
			title='Test',
			major_version=1,
			minor_version=1,
			patch_version=2,
			runnable=1,
			fullscreen=0,
			embed_types='',
			preloaded_js="[u'scripts/test.js']",
			preloaded_css="[u'styles/test.css']",
			drop_library_css=None,
			semantics='',
			restricted=0,
			tutorial_url=''
		)
		content = h5p_contents.objects.create(
			content_id=1,
			title='ContentTest',
			json_contents='',
			main_library_id=1,
			filtered='',
			slug='contenttest'
		)
		test = User.objects.create(
			username='titi'
		)
		print('setUp of StorageTestCase ---- Ready')

	def test_save_library(self):
		storage = H5PDefaultStorage(settings.MEDIA_ROOT)
		lib = h5p_libraries.objects.filter(library_id=1).values()[0]
		os.makedirs('/home/pod/H5PP/media/tmp/H5P.Test')
		lib['uploadDirectory'] = '/home/pod/H5PP/media/tmp/H5P.Test'

		storage.saveLibrary(lib)

		self.assertTrue(os.path.exists('/home/pod/H5PP/media/libraries/H5P.Test-1.1'))

		os.rmdir('/home/pod/H5PP/media/libraries/H5P.Test-1.1')
		os.rmdir('/home/pod/H5PP/media/tmp/H5P.Test')
		print('test_save_library ---- Check')

	def test_save_content(self):
		storage= H5PDefaultStorage(settings.MEDIA_ROOT)
		cont = h5p_contents.objects.filter(content_id=1).values()[0]
		os.makedirs('/home/pod/H5PP/media/tmp/ContentTest')

		storage.saveContent('/home/pod/H5PP/media/tmp/ContentTest', 1)

		self.assertTrue(os.path.exists('/home/pod/H5PP/media/content/1'))

		os.rmdir('/home/pod/H5PP/media/tmp/ContentTest')
		shutil.rmtree('/home/pod/H5PP/media/content/1', ignore_errors=True)
		print('test_save_content ---- Check')

class EditorStorageTestCase(TestCase):

	def setUp(self):
		library = h5p_libraries.objects.create(
			library_id=1,
			machine_name='H5P.Test',
			title='Test',
			major_version=1,
			minor_version=1,
			patch_version=2,
			runnable=1,
			fullscreen=0,
			embed_types='',
			preloaded_js="[u'scripts/test.js']",
			preloaded_css="[u'styles/test.css']",
			drop_library_css=None,
			semantics='',
			restricted=0,
			tutorial_url=''
		)
		test = User.objects.create(
			username='titi'
		)
		print('setUp of EditorStorageTestCase ---- Ready')

	def test_get_libraries(self):
		editor = H5PEditorStorage()
		result = editor.getLibraries()

		self.assertTrue(result[0]['name'] == 'H5P.Test')

		libraries = [{
			'name': 'H5P.Test',
			'majorVersion': 1,
			'minorVersion': 1
		}]
		result = editor.getLibraries(libraries)

		self.assertTrue(result[0]['title'] == 'Test')
		print('test_get_libraries ---- Check')
##
# TODO
# Place request-based test
##