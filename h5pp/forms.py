from django import forms
from django.conf import settings
from h5pp.h5p.h5pclasses import H5PDjango
from h5pp.h5p.h5pmodule import h5pInsert, h5pGetContent
from h5pp.h5p.editor.h5peditormodule import createContent
from h5pp.models import h5p_libraries
import json
import os

##
# Function who handle uploading h5p file
##
def handleUploadedFile(files, filename):
		if not os.path.exists(settings.MEDIA_ROOT + '/tmp'):
			os.mkdir(settings.MEDIA_ROOT + '/tmp')

		with open(settings.MEDIA_ROOT + '/tmp/' + filename, 'wb+') as destination:
			for chunk in files.chunks():
				destination.write(chunk)

		return {'folderPath': settings.MEDIA_ROOT + '/tmp', 'path': settings.MEDIA_ROOT + '/tmp/' + filename}

##
# Form for upload/update h5p libraries
##
class LibrariesForm(forms.Form):
	h5p = forms.FileField()
	uninstall = forms.BooleanField(widget=forms.CheckboxInput())

	def __init__(self, user, *args, **kwargs):
		super(LibrariesForm, self).__init__(*args, **kwargs)
		self.user = user

	def clean(self):
		h5pfile = self.cleaned_data.get('h5p')
		if h5pfile != None:
			interface = H5PDjango(self.user)
			paths = handleUploadedFile(h5pfile, h5pfile.name)
			validator = interface.h5pGetInstance('validator', paths['folderPath'], paths['path'])
			
			if not validator.isValidPackage(True, False):
				raise forms.ValidationError('The uploaded file was not a valid h5p package.')

			storage = interface.h5pGetInstance('storage')
			if not storage.savePackage(None, None, True):
				raise forms.ValidationError('Error during library save.')
		else:
			raise forms.ValidationError('You need to select a h5p package before uploading.')

		return self.cleaned_data

##
# Form for upload h5p file
##
CHOICES = [('upload', 'Upload'),
			('create', 'Create')]

class CreateForm(forms.Form):
	title = forms.CharField(label='Title ')
	h5p_type = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())
	h5p = forms.FileField(label='HTML 5 Package ', help_text='Select a .h5p file to upload and create interactive content from. You may start with the <a href="http://h5p.org/content-types-and-applications" target="_blank">example files</a> on H5P.org', required=False)
	json_content = forms.CharField(widget=forms.HiddenInput())
	disable = forms.IntegerField(widget=forms.HiddenInput())
	h5p_library = forms.CharField(widget=forms.HiddenInput())

	def __init__(self, request, *args, **kwargs):
		super(CreateForm, self).__init__(*args, **kwargs)
		self.request = request
		self.fields['json_content'].initial = self.getJsonContent()
		self.fields['disable'].initial = self.getDisable()
		self.fields['h5p_library'].initial = self.getLibrary()

	def clean(self):
		if self.request.POST['h5p_type'] == 'upload':
			h5pfile = self.cleaned_data.get('h5p')
			interface = H5PDjango(self.request.user)
			paths = handleUploadedFile(h5pfile, h5pfile.name)
			validator = interface.h5pGetInstance('validator', paths['folderPath'], paths['path'])
			
			if not validator.isValidPackage(False, False):
				raise forms.ValidationError('The uploaded file was not a valid h5p package.')

			self.request.POST['h5p_upload'] = paths['path']
			self.request.POST['h5p_upload_folder'] = paths['folderPath']
			if not h5pInsert(self.request, interface):
				raise forms.ValidationError('Error during saving the content.')
		else:
			interface = H5PDjango(self.request.user)
			core = interface.h5pGetInstance('core')
			content = dict()
			content['disable'] = 0
			libraryData = core.libraryFromString(self.request.POST['h5p_library'])
			if not libraryData:
				raise forms.ValidationError('You must choose an H5P content type or upload an H5P file.')
			else:
				content['library'] = libraryData
				runnable = h5p_libraries.objects.filter(machine_name=libraryData['machineName'], major_version=libraryData['majorVersion'], minor_version=libraryData['minorVersion']).values('runnable')
				if not len(runnable) > 0 and runnable[0]['runnable'] == 0:
					raise forms.ValidationError('Invalid H5P content type')

				content['library']['libraryId'] = core.h5pF.getLibraryId(content['library']['machineName'], content['library']['majorVersion'], content['library']['minorVersion'])
				if not content['library']['libraryId']:
					raise forms.ValidationError('No such library')

				content['title'] = self.request.POST['title']
				content['params'] = self.request.POST['json_content']
				params = json.loads(content['params'])
				content['id'] = core.saveContent(content)

				if not createContent(self.request, content, params):
					raise forms.ValidationError('Impossible to create the content')

		return self.cleaned_data

	def getJsonContent(self):
		if 'json_content' in self.request.GET or 'translation_source' in self.request.GET and 'json_content' in self.request.GET['translation_source']:
			filteredParams = self.request.GET['json_content'] if not 'translation_source' in self.request.GET else self.request.GET['translation_source']['json_content']
		else:
			filteredParams = '{}'

		return filteredParams

	def getLibrary(self):
		if 'h5p_library' in self.request.GET:
			return self.request.GET['h5p_library']
		else:
			return 0

	def getDisable(self):
		if 'disable' in self.request.GET:
			return self.request.GET['disable']
		else:
			return 0




