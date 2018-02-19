from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from h5pp.forms import LibrariesForm, CreateForm
from h5pp.models import h5p_libraries, h5p_contents, h5p_content_user_data, h5p_points
from h5pp.h5p.h5pmodule import *
from h5pp.h5p.h5pclasses import H5PDjango
from h5pp.h5p.editor.h5peditormodule import h5peditorContent, handleContentUserData
from h5pp.h5p.editor.h5peditorclasses import H5PDjangoEditor
from h5pp.h5p.editor.library.h5peditorfile import H5PEditorFile


def home(request):
    return render(request, 'h5p/home.html')


def librariesView(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        libraries = h5p_libraries.objects.all()
        if request.method == 'POST':
            form = LibrariesForm(request.user, request.POST, request.FILES)
            if form.is_valid():
                if 'h5p' in request.FILES and request.FILES['h5p'] != None:
                    return render(request, 'h5p/libraries.html', {'form': form, 'libraries': libraries, 'status': 'Upload complete'})
                elif 'download' in request.POST:
                    return render(request, 'h5p/libraries.html', {'form': form, 'libraries': libraries, 'status': 'Update complete'})
                else:
                    status = uninstall()
                    return render(request, 'h5p/libraries.html', {'form': form, 'libraries': libraries, 'status': status})
            return render(request, 'h5p/libraries.html', {'form': form, 'libraries': libraries})

        form = LibrariesForm(request.user)
        return render(request, 'h5p/libraries.html', {'form': form, 'libraries': libraries})

    return HttpResponseRedirect('/h5p/login/?next=/h5p/libraries/')


def createView(request, contentId=None):
    if request.user.is_authenticated():
        editor = h5peditorContent(request, contentId)
        if request.method == 'POST':
            if contentId != None:
                request.POST['contentId'] = contentId
            form = CreateForm(request, request.POST, request.FILES)
            if form.is_valid():
                if contentId != None:
                    return HttpResponseRedirect('/h5p/content/?contentId=' + contentId)
                else:
                    newId = h5p_contents.objects.all(
                    ).order_by('-content_id')[0]
                    return HttpResponseRedirect('/h5p/content/?contentId=' + str(newId.content_id))
            return render(request, 'h5p/create.html', {'form': form, 'data': editor})

        elif contentId != None:
            framework = H5PDjango(request.user)
            edit = framework.loadContent(contentId)
            request.GET = request.GET.copy()
            request.GET['contentId'] = contentId
            request.GET['json_content'] = edit['params']
            request.GET['h5p_library'] = edit['library_name'] + ' ' + \
                str(edit['library_major_version']) + '.' + \
                str(edit['library_minor_version'])

        form = CreateForm(request)

        return render(request, 'h5p/create.html', {'form': form, 'data': editor})

    return HttpResponseRedirect('/h5p/login/?next=/h5p/create/')


def contentsView(request):
    if 'contentId' in request.GET:
        try:
            owner = h5p_contents.objects.get(content_id=h5pGetContentId(request))
        except:
            raise Http404
        h5pLoad(request)
        content = includeH5p(request)
        score = None

        if not 'html' in content:
            html = '<div>Sorry, preview of H5P content is not yet available.</div>'
            return render(request, 'h5p/content.html', {'html': html})
        else:
            if request.user.is_authenticated():
                h5pSetStarted(request.user, h5pGetContentId(request))
                score = getUserScore(h5pGetContentId(request), request.user)

                return render(request, 'h5p/content.html', {'html': content['html'], 'data': content['data'], 'owner': owner.author, 'score': score[0]})
            return render(request, 'h5p/content.html', {'html': content['html'], 'data': content['data'], 'owner': owner.author})

    return HttpResponseRedirect('/h5p/listContents')


def listView(request):
    if request.method == 'POST':
        if request.user.is_superuser and 'contentId' in request.GET:
            h5pDelete(request)
            return HttpResponseRedirect('/h5p/listContents')
            
        return render(request, 'h5p/listContents.html', {'status': 'You do not have the necessary rights to delete a video.'})

    listContent = h5pGetListContent(request)
    if listContent > 0:
        return render(request, 'h5p/listContents.html', {'listContent': listContent})

    return render(request, 'h5p/listContents.html', {'status': 'No contents installed.'})

def scoreView(request, contentId):
    try:
        content = h5p_contents.objects.get(content_id=contentId)
    except:
        raise Http404
    if request.user.is_authenticated():
        if request.method == 'POST' and (request.user.username == content.author or request.user.is_superuser):
            userData = h5p_content_user_data.objects.filter(content_main_id=content.content_id)
            if userData:
                userData.delete()
            userPoints = h5p_points.objects.filter(content_id=content.content_id)
            if userPoints:
                userPoints.delete()

            return HttpResponseRedirect('/h5p/score/%s' % content.content_id, {'status': "Scores has been reset !"})

        if 'user' in request.GET and (request.user.username == content.author or request.user.is_superuser):
            user = User.objects.get(username=request.GET['user'])
            userData = h5p_content_user_data.objects.filter(user_id=user.id, content_main_id=content.content_id)
            if userData:
                userData.delete()
            userPoints = h5p_points.objects.filter(uid=user.id, content_id=content.content_id)
            if userPoints:
                userPoints.delete()

            return HttpResponseRedirect('/h5p/score/%s' % content.content_id, {'status': "%s's score has been reset !" % user.username})

        if 'download' in request.GET and request.user.is_superuser:
            if request.GET['download'] == 'all':
                scores = exportScore()
                scores = ContentFile(scores)
                response = HttpResponse(scores, 'text/plain')
                response['Content-Length'] = scores.size
                response['Content-Disposition'] = 'attachment; filename="h5pp_users_score.txt"'
            else:
                scores = exportScore(request.GET['download'])
                scores = ContentFile(scores)
                response = HttpResponse(scores, 'text/plain')
                response['Content-Length'] = scores.size
                response['Content-Disposition'] = 'attachment; filename="content_%s_users_score.txt"' % request.GET['download']

            return response

        listScore = dict()
        if request.user.username == content.author or request.user.is_superuser:
            listScore['owner'] = True

        listScore['data'] = getUserScore(content.content_id)
        if listScore['data'] > 0:
            return render(request, 'h5p/score.html', {'listScore': listScore, 'content': content})

        return render(request, 'h5p/score.html', {'status': 'No score available yet.', 'content': content})

    return HttpResponseRedirect('/h5p/login/?next=/h5p/score/' + contentId + '/')

def embedView(request):
    if 'contentId' in request.GET:
        h5pLoad(request)
        embed = h5pEmbed(request)
        score = None
        if request.user.is_authenticated():
            h5pSetStarted(request.user, h5pGetContentId(request))
            score = getUserScore(request.GET['contentId'], request.user)[0]
        return render(request, 'h5p/embed.html', {'embed': embed, 'score': score})

    return HttpResponseForbidden()

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
        name = request.GET[
            'machineName'] if 'machineName' in request.GET else ''
        major = request.GET[
            'majorVersion'] if 'majorVersion' in request.GET else 0
        minor = request.GET[
            'minorVersion'] if 'minorVersion' in request.GET else 0

        framework = H5PDjango(request.user)
        editor = framework.h5pGetInstance('editor')
        if name != '':
            data = editor.getLibraryData(
                name, major, minor, settings.H5P_LANGUAGE)
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

        elif 'setFinished' in request.GET:
            data = h5pSetFinished(request)
            return HttpResponse(
                data,
                content_type='application/json'
            )

    if 'content-user-data' in request.GET:
        data = handleContentUserData(request)
        return HttpResponse(
            data,
            content_type='application/json'
        )

    elif 'user-scores' in request.GET:
        score = getUserScore(request.GET['user-scores'], None, True)
        return HttpResponse(
            score,
            content_type='application/json'
        )
    return HttpResponseRedirect('/h5p/create')
