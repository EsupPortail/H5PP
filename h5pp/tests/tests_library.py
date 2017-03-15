from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from h5pp.h5p.h5pclasses import H5PDjango
from h5pp.models import *

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
		print('setUp of ValidatorTestCase ---- Ready')

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
