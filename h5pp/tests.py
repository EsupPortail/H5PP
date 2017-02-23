from django.test import TestCase
from django.conf import settings
from h5pp.library.h5pclasses import H5PDjango

# Create your tests here.

class H5pClassesTestCase(TestCase):
	def test_getPlatformInfo(self):
		framework = H5PDjango()
		result = framework.getPlatformInfo()

		self.assertEqual(result['version'], '1.8')
		self.assertEqual(result['h5pVersion'], settings.H5P_VERSION)

		print('test_getPlatformInfo - OK')

	def test_fetchExternalData(self):
		framework = H5PDjango()
		result200 = framework.fetchExternalData('https://h5p.org')

		self.assertEqual(result200.status_code, 200)

		print('test_fetchExternalData - OK')