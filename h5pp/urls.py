from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from h5pp.views import (
    librariesView,
    CreateContentView,
    UpdateContentView,
    ContentDetailView,
    createView,
    editorAjax,
    listView,
    ajax,
    scoreView,
    embedView
)


urlpatterns = [
    # Base
    url(r'^home/$', TemplateView.as_view(template_name="h5p/home.html"), name="h5phome"),

    # Contents and Libraries
    url(r'^libraries/$', librariesView, name="h5plibraries"),
    url(r'^listContents/$', listView, name="h5plistContents"),
    url(r'^content/(?P<content_id>\d+)/$', login_required(ContentDetailView.as_view()), name="h5pcontent"),

    # Contents creation / upload
    url(r'^create/$', login_required(CreateContentView.as_view()), name="h5pcreate"),
    # url(r'^update/(?P<content_id>\d+)/$', login_required(UpdateContentView.as_view()), name="h5pedit"),
    url(r'^create/(?P<contentId>\d+)/$', createView, name='h5pedit'),

    # Users score
    url(r'^score/(?P<contentId>\d+)/$', scoreView, name='h5pscore'),
    # Embed page
    url(r'^embed/$', embedView, name='h5pembed'),
    
    # Ajax
    url(r'^ajax/$', ajax, name="h5pajax"),
    url(r'^editorajax/(?P<contentId>\d+)/$', editorAjax, name="h5peditorAjax"),
]
