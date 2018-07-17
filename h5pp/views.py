from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    FormView,
    CreateView,
    UpdateView,
    TemplateView
)

from .forms import LibrariesForm, CreateForm
from .models import h5p_libraries, h5p_contents, h5p_content_user_data, h5p_points
from h5pp.h5p.h5pmodule import (
    includeH5p,
    h5pSetStarted,
    h5pSetFinished,
    h5pGetContentId,
    h5pGetListContent,
    h5pLoad,
    h5pDelete,
    getUserScore,
    uninstall
)
from h5pp.h5p.h5pclasses import H5PDjango
from h5pp.h5p.editor.h5peditormodule import (
    h5peditorContent,
    handleContentUserData
)
from h5pp.h5p.editor.library.h5peditorfile import H5PEditorFile


def librariesView(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        libraries = h5p_libraries.objects.all()
        if request.method == 'POST':
            form = LibrariesForm(request.user, request.POST, request.FILES)
            if form.is_valid():
                if 'h5p' in request.FILES and request.FILES['h5p'] is not None:
                    return render(request, 'h5p/libraries.html',
                                  {'form': form, 'libraries': libraries, 'status': 'Upload complete'})
                elif 'download' in request.POST:
                    return render(request, 'h5p/libraries.html',
                                  {'form': form, 'libraries': libraries, 'status': 'Update complete'})
                else:
                    status = uninstall()
                    return render(request, 'h5p/libraries.html',
                                  {'form': form, 'libraries': libraries, 'status': status})
            return render(request, 'h5p/libraries.html', {'form': form, 'libraries': libraries})

        form = LibrariesForm(request.user)
        return render(request, 'h5p/libraries.html', {'form': form, 'libraries': libraries})

    return HttpResponseRedirect('/h5p/login/?next=/h5p/libraries/')


class CreateContentView(CreateView):
    template_name = "h5p/create.html"
    success_url = "h5pcontent"
    form_class = CreateForm

    def get_form_kwargs(self):
        kwargs = {
            'request': self.request,
        }
        return kwargs

    def get_success_url(self, pk):
        return reverse("h5pp:h5pcontent", args=[pk])

    def get_context_data(self, **kwargs):
        """
        Get the editor for the template

        """
        ctx = super(CreateContentView, self).get_context_data(**kwargs)
        ctx["data"] = h5peditorContent(self.request)

        return ctx

    def post(self, request, *args, **kwargs):
        form = CreateForm(self.request, self.request.POST, self.request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # this is hacky and needs to be corrected in the form.
        newId = h5p_contents.objects.all().order_by('-content_id')[0]

        return HttpResponseRedirect(
            self.get_success_url(str(newId.content_id))
        )


class UpdateContentView(FormView):
    template_name = "h5p/create.html"
    success_url = "h5pcontent"
    form_class = CreateForm

    def get_form_kwargs(self):
        framework = H5PDjango(self.request.user)
        edit = framework.loadContent(self.kwargs.get("content_id"))
        self.request.GET = self.request.GET.copy()
        self.request.GET['contentId'] = self.kwargs.get("content_id")
        self.request.GET["title"] = edit["title"]
        self.request.GET["language"] = "en"
        self.request.GET["filtered"] = edit['filtered']
        self.request.GET['json_content'] = edit['params']
        self.request.GET['h5p_slug'] = edit['slug']
        self.request.GET['h5p_library'] = edit['library_name'] + ' ' + \
            str(edit['library_major_version']) + '.' + \
            str(edit['library_minor_version'])
        #self.request.GET['main_library'] = self.request.GET["h5p_library"]

        kwargs = {
            'request': self.request,
        }
        return kwargs

    def get_success_url(self, pk):
        return reverse("h5pcontent", args=[pk])

    def get_context_data(self, **kwargs):
        """
        Get the editor for the template

        """
        ctx = super(UpdateContentView, self).get_context_data(**kwargs)
        ctx["data"] = h5peditorContent(self.request)

        return ctx

    def post(self, request, *args, **kwargs):
        form = CreateForm(self.request, self.request.POST, self.request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):

        return HttpResponseRedirect(
            self.get_success_url(self.pk_url_kwarg)
        )


def createView(request, contentId=None):
    if request.user.is_authenticated():
        editor = h5peditorContent(request, contentId)
        if request.method == 'POST':
            if contentId is not None:
                request.POST = request.POST.copy()
                request.POST['contentId'] = contentId
            form = CreateForm(request, request.POST, request.FILES)
            if form.is_valid():
                if contentId is not None:
                    return HttpResponseRedirect(
                        reverse("h5pp:h5pcontent", args=[contentId])
                    )
                else:
                    newId = h5p_contents.objects.all().order_by('-content_id')[0]
                    return HttpResponseRedirect(
                        reverse("h5pp:h5pcontent", args=[newId.content_id])
                    )
            return render(
                request,
                'h5p/create.html',
                {'form': form, 'data': editor}
            )

        elif contentId is not None:
            framework = H5PDjango(request.user)
            edit = framework.loadContent(contentId)
            request.GET = request.GET.copy()
            request.GET['contentId'] = contentId
            request.GET['json_content'] = edit['params']
            request.GET['h5p_library'] = edit['library_name'] + ' ' + \
                                         str(edit['library_major_version']) + '.' + \
                                         str(edit['library_minor_version'])

        form = CreateForm(request)

        return render(
            request,
            'h5p/create.html',
            {'form': form, 'data': editor}
        )

    return HttpResponseRedirect('/h5p/login/?next=/h5p/create/')


class ContentDetailView(TemplateView):
    template_name = "h5p/content.html"

    def get_context_data(self, **kwargs):
        ctx = super(ContentDetailView, self).get_context_data(**kwargs)

        self.request.GET = self.request.GET.copy()
        self.request.GET["contentId"] = self.kwargs.get("content_id")
        h5pLoad(self.request)
        content = includeH5p(self.request)
        h5pSetStarted(self.request.user, self.kwargs.get("content_id"))
        score = getUserScore(self.kwargs.get("content_id"), self.request.user)

        if "html" not in content:
            ctx["html"] = "<div>Sorry, preview of H5P content is not yet available.</div>"
        else:
            ctx["html"] = content["html"]

        ctx["html"] = content["html"]
        ctx["data"] = content["data"]
        ctx["score"] = score[0]
        ctx["content_id"] = self.kwargs.get("content_id")

        return ctx


def contentsView(request):
    if 'contentId' in request.GET:
        try:
            owner = h5p_contents.objects.get(content_id=h5pGetContentId(request))
        except:
            raise Http404
        h5pLoad(request)
        content = includeH5p(request)
        score = None

        if "html" not in content:
            html = '<div>Sorry, preview of H5P content is not yet available.</div>'
            return render(request, 'h5p/content.html', {'html': html})
        else:
            if request.user.is_authenticated():
                h5pSetStarted(request.user, h5pGetContentId(request))
                score = getUserScore(h5pGetContentId(request), request.user)

                return render(request, 'h5p/content.html',
                              {'html': content['html'], 'data': content['data'], 'owner': owner.author,
                               'score': score[0]})
            return render(request, 'h5p/content.html',
                          {'html': content['html'], 'data': content['data'], 'owner': owner.author})

    return HttpResponseRedirect('/h5p/listContents')


def listView(request):
    if request.method == 'POST':
        if request.user.is_superuser and 'contentId' in request.GET:
            h5pDelete(request)
            return HttpResponseRedirect('/h5p/listContents')
        return render(
            request,
            'h5p/listContents.html',
            {'status': 'You do not have the necessary rights to delete a video.'}
        )

    listContent = h5pGetListContent(request)
    if listContent and len(listContent) > 0:
        return render(
            request,
            'h5p/listContents.html',
            {'listContent': listContent}
        )

    return render(
        request,
        'h5p/listContents.html',
        {'status': 'No contents installed.'}
    )


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
        if listScore['data'] and listScore['data'].count() > 0:
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
