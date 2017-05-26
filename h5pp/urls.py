from django.conf.urls import url
from django.contrib.auth.views import login, logout
from h5pp.views import (
    home,
    createView,
    editorAjax,
    librariesView,
    listView,
    contentsView,
    ajax
)

# app_name = 'h5pp'
urlpatterns = [
    # Base
    url(r'^home/$', home, name="h5phome"),

    # Authentification
    url(r'^login/', login, {'template_name': 'h5p/login.html'}, name='login'),
    url(r'^logout/', logout, {'next_page': '/h5p/home'}, name='logout'),

    # Contents and Libraries
    url(r'^libraries/$', librariesView, name='h5plibraries'),
    url(r'^listContents/$', listView, name='h5plistContents'),
    url(r'^content/$', contentsView, name='h5pcontent'),

    # Contents creation / upload
    url(r'^create/$', createView, name='h5pcreate'),
    url(r'^create/(?P<contentId>\d+)/$', createView, name='h5pedit'),

    # Ajax
    url(r'^ajax/$', ajax, name='h5pajax'),
    url(r'^editorajax/(?P<contentId>\d+)/$', editorAjax, name='h5peditorAjax'),
]
