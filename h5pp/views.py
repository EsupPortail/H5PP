from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from h5pp.forms import LibrariesForm, CreateForm
from h5pp.h5p.h5pmodule import includeH5p, h5pSetStarted, h5pGetContentId, h5pGetListContent, h5pLoad, h5pDelete, uninstall
from h5pp.h5p.h5pclasses import H5PDjango
from h5pp.h5p.editor.h5peditormodule import h5peditorContent, handleContentUserData
from h5pp.h5p.editor.h5peditorclasses import H5PDjangoEditor
from h5pp.h5p.editor.library.h5peditorfile import H5PEditorFile

def home(request):
	return render(request, 'h5p/home.html')

def librariesView(request):
	if request.user.is_authenticated():
		if request.method == 'POST':
			form = LibrariesForm(request.user, request.POST, request.FILES)
			if form.is_valid():
				if 'h5p' in request.POST and request.POST['h5p'] != '':
					return render(request, 'h5p/libraries.html', {'form': form, 'status': 'Upload complete'})
				else:
					status = uninstall()
					return render(request, 'h5p/libraries.html', {'form': form, 'status': status})
			return render(request, 'h5p/libraries.html', {'form' : form})
		else:
			form = LibrariesForm(request.user)
			return render(request, 'h5p/libraries.html', {'form': form})

	return HttpResponseRedirect('/h5p/login')

def createView(request, contentId=None):
	if request.user.is_authenticated():
		editor = h5peditorContent(request)
		if request.method == 'POST':
			form = CreateForm(request, request.POST, request.FILES)
			if form.is_valid():
					return HttpResponseRedirect('/h5p/listContents')
			return render(request, 'h5p/create.html', {'form': form, 'data': editor})
		
		elif contentId != None:
			framework = H5PDjango(request.user)
			edit = framework.loadContent(contentId)
			request.GET = request.GET.copy()
			request.GET['json_content'] = edit['params']
			request.GET['h5p_library'] = edit['library_name'] + ' ' + str(edit['library_major_version']) + '.' + str(edit['library_minor_version'])
		
		form = CreateForm(request)

		return render(request, 'h5p/create.html', {'form': form, 'data': editor})

	return HttpResponseRedirect('/h5p/login')

def contentsView(request):
	if 'contentId' in request.GET:
		h5pLoad(request)
		content = includeH5p(request)

		if not 'html' in content:
			html = '<div>Sorry, preview of H5P content is not yet available.</div>'
			return render(request, 'h5p/content.html', {'html': html})
		else:
			h5pSetStarted(request.user, h5pGetContentId(request))
			return render(request, 'h5p/content.html', {'html': content['html'], 'data': content['data']})
	
	return HttpResponseRedirect('/h5p/listContents')

def listView(request):
	if request.method == 'POST':
		if request.user.is_authenticated():
			h5pDelete(request)
			return HttpResponseRedirect('/h5p/listContents')

	listContent = h5pGetListContent(request)
	if listContent > 0:
		return render(request, 'h5p/listContents.html', {'listContent': listContent})

	return render(request, 'h5p/listContents.html', {'status': 'No contents installed.'})

@csrf_exempt
def editorAjax(request, contentId):
	data = None
	if request.method == 'POST':
		if 'libraries' in request.GET:
			framework = H5PDjango(request.user)
			editor = framework.h5pGetInstance('editor')
			data = editor.getLibraries(request)
			return HttpResponse(
				data,
				content_type='application/json'
			)
		elif 'file' in request.FILES:
			framework = H5PDjango(request.user)
			f = H5PEditorFile(request, request.FILES, framework)
			if not f.isLoaded():
				return HttpResponse(
					'File Not Found',
					content_type='application/json'
				)

			if f.validate():
				core = framework.h5pGetInstance('core')
				fileId = core.fs.saveFile(f, request.POST['contentId'])

			data = f.printResult()
			return HttpResponse(
				data,
				content_type='application/json'
			)
		return HttpResponseRedirect('h5p/')
	if 'libraries' in request.GET:
		name = request.GET['machineName'] if 'machineName' in request.GET else ''
		major = request.GET['majorVersion'] if 'majorVersion' in request.GET else 0
		minor = request.GET['minorVersion'] if 'minorVersion' in request.GET else 0

		framework = H5PDjango(request.user)
		editor = framework.h5pGetInstance('editor')
		if name != '':
			data = editor.getLibraryData(name, major, minor, settings.H5P_LANGUAGE)
			return HttpResponse(
				data,
				content_type='application/json'
			)
		else:
			data = editor.getLibraries(request)
			return HttpResponse(
				data,
				content_type='application/json'
			)
	return HttpResponse(
		data,
		content_type='application/json'
	)

@csrf_exempt
def ajax(request):
	if request.method == 'POST':
		if 'content-user-data' in request.GET:
			data = handleContentUserData(request)
			return HttpResponse(
				data,
				content_type='application/json'
			)
		return HttpResponseRedirect('h5p/create')

	if 'content-user-data' in request.GET:
		data = handleContentUserData(request)
		return HttpResponse(
			data,
			content_type='application/json'
		)
	return HttpResponseRedirect('/h5p/create')
		
