from django import forms
from django.conf import settings
from h5pp.models import h5p_libraries
from h5pp.h5p.h5pclasses import H5PDjango
from h5pp.h5p.h5pmodule import h5pInsert, h5pGetContent
from h5pp.h5p.editor.h5peditormodule import createContent
import json
import os

##
# Function who handle uploading h5p file
##


def handleUploadedFile(files, filename):
    tmpdir = os.path.join(settings.MEDIA_ROOT, 'h5pp', 'tmp')

    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)

    with open(os.path.join(tmpdir, filename), 'wb+') as destination:
        for chunk in files.chunks():
            destination.write(chunk)

    return {'folderPath': tmpdir, 'path': os.path.join(tmpdir, filename)}

##
# Form for upload/update h5p libraries
##


class LibrariesForm(forms.Form):
    h5p = forms.FileField(required=False)
    download = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    uninstall = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False)

    def __init__(self, user, *args, **kwargs):
        super(LibrariesForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        h5pfile = self.cleaned_data.get('h5p')
        down = self.cleaned_data.get('download')
        unins = self.cleaned_data.get('uninstall')

        if h5pfile != None:
            if down != False or unins != False:
                raise forms.ValidationError(
                    'Too many choices selected.')
            interface = H5PDjango(self.user)
            paths = handleUploadedFile(h5pfile, h5pfile.name)
            validator = interface.h5pGetInstance(
                'validator', paths['folderPath'], paths['path'])

            if not validator.isValidPackage(True, False):
                raise forms.ValidationError(
                    'The uploaded file was not a valid h5p package.')

            storage = interface.h5pGetInstance('storage')
            if not storage.savePackage(None, None, True):
                raise forms.ValidationError('Error during library save.')
        elif down != False:
            if unins != False:
                raise forms.ValidationError(
                    'Too many choices selected.')
            libraries = h5p_libraries.objects.values()
            if not len(libraries) > 0:
                raise forms.ValidationError(
                    'You cannot update libraries when you don\'t have libraries installed !.')

            interface = H5PDjango(self.user)
            interface.updateTutorial()
        elif unins == False:
            raise forms.ValidationError(
                'No actions selected.')

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
        self.fields['title'].initial = self.getTitle()
        self.fields['json_content'].initial = self.getJsonContent()
        self.fields['disable'].initial = self.getDisable()
        self.fields['h5p_library'].initial = self.getLibrary()

    def clean(self):
        if self.request.POST['h5p_type'] == 'upload':
            h5pfile = self.cleaned_data.get('h5p')
            if not h5pfile:
                raise forms.ValidationError(
                    'You need to choose a valid h5p package.')

            interface = H5PDjango(self.request.user)
            paths = handleUploadedFile(h5pfile, h5pfile.name)
            validator = interface.h5pGetInstance(
                'validator', paths['folderPath'], paths['path'])

            if not validator.isValidPackage(False, False):
                raise forms.ValidationError(
                    'The uploaded file was not a valid h5p package.')

            self.request.POST['h5p_upload'] = paths['path']
            self.request.POST['h5p_upload_folder'] = paths['folderPath']
            if not h5pInsert(self.request, interface):
                raise forms.ValidationError('Error during saving the content.')
        else:
            interface = H5PDjango(self.request.user)
            core = interface.h5pGetInstance('core')
            content = dict()
            content['disable'] = 0
            libraryData = core.libraryFromString(
                self.request.POST['h5p_library'])
            if not libraryData:
                raise forms.ValidationError(
                    'You must choose an H5P content type or upload an H5P file.')
            else:
                content['library'] = libraryData
                runnable = h5p_libraries.objects.filter(machine_name=libraryData['machineName'], major_version=libraryData[
                                                        'majorVersion'], minor_version=libraryData['minorVersion']).values('runnable')
                if not len(runnable) > 0 and runnable[0]['runnable'] == 0:
                    raise forms.ValidationError('Invalid H5P content type')

                content['library']['libraryId'] = core.h5pF.getLibraryId(content['library'][
                                                                         'machineName'], content['library']['majorVersion'], content['library']['minorVersion'])
                if not content['library']['libraryId']:
                    raise forms.ValidationError('No such library')

                content['title'] = self.request.POST['title']
                content['params'] = self.request.POST['json_content']
                content['author'] = self.request.user.username
                params = json.loads(content['params'])
                if 'contentId' in self.request.POST:
                    content['id'] = self.request.POST['contentId']
                content['id'] = core.saveContent(content)

                if not createContent(self.request, content, params):
                    raise forms.ValidationError(
                        'Impossible to create the content')

                return content['id']

        return self.cleaned_data

    def getJsonContent(self):
        if 'json_content' in self.request.GET or 'translation_source' in self.request.GET and 'json_content' in self.request.GET['translation_source']:
            filteredParams = self.request.GET['json_content'] if not 'translation_source' in self.request.GET else self.request.GET[
                'translation_source']['json_content']
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

    def getTitle(self):
        if 'title' in self.request.GET:
            return self.request.GET['title']
        else:
            return ''
