from django.conf.urls import url
from django.contrib.auth.views import login, logout

app_name = 'h5pp'
urlpatterns = [
	# Base
    url(r'^home/$', 'h5pp.views.home', name='h5phome'),

    # Authentification
    url(r'^login/', login, {'template_name': 'h5p/login.html'}, name='login'),
    url(r'^logout/', logout, {'next_page': '/h5p/home'}, name='logout'),

    # Contents and Libraries
    url(r'^libraries/$', 'h5pp.views.librariesView', name='h5plibraries'),
    url(r'^listContents/$', 'h5pp.views.listView', name='h5plistContents'),
    url(r'^content/$', 'h5pp.views.contentsView', name='h5pcontent'),

    # Contents creation / upload
    url(r'^create/$', 'h5pp.views.createView', name='h5pcreate'),
    url(r'^create/(?P<contentId>\d+)/$', 'h5pp.views.createView', name='h5pedit'),

    # Users score
    url(r'^score/(?P<contentId>\d+)/$', 'h5pp.views.scoreView', name='h5pscore'),

    # Embed page
    url(r'^embed/$', 'h5pp.views.embedView', name='h5pembed'),

    # Ajax
    url(r'^ajax/$', 'h5pp.views.ajax', name='h5pajax'),
    url(r'^editorajax/(?P<contentId>\d+)/$', 'h5pp.views.editorAjax', name='h5peditorAjax'),
]