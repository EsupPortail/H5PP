from django.contrib import admin
from h5pp.models import *

class LibrariesAdmin(admin.ModelAdmin):
	list_display = ('title', 'machine_name', 'library_id')
	ordering = ('title', 'machine_name')

admin.site.register(h5p_libraries, LibrariesAdmin)

class LibrariesLanguageAdmin(admin.ModelAdmin):
	list_display = ('library_id', 'language_code')
	ordering = ('library_id', 'language_code')

admin.site.register(h5p_libraries_languages, LibrariesLanguageAdmin)

class LibrariesLibrariesAdmin(admin.ModelAdmin):
	list_display = ('library_id', 'required_library_id', 'dependency_type')
	ordering = ('library_id', 'required_library_id')

admin.site.register(h5p_libraries_libraries, LibrariesLibrariesAdmin)

class ContentsAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'content_type')
	ordering = ('title', 'author')

admin.site.register(h5p_contents, ContentsAdmin)

class ContentsLibrariesAdmin(admin.ModelAdmin):
	list_display = ('content_id', 'library_id', 'dependency_type')
	ordering = ('content_id', 'library_id')

admin.site.register(h5p_contents_libraries, ContentsLibrariesAdmin)

class PointsAdmin(admin.ModelAdmin):
	list_display = ('content_id', 'uid', 'points', 'max_points')
	ordering = ('content_id', 'uid')

admin.site.register(h5p_points, PointsAdmin)

class ContentUserAdmin(admin.ModelAdmin):
	list_display = ('user_id', 'content_main_id')
	ordering = ('user_id', 'content_main_id')

admin.site.register(h5p_content_user_data, ContentUserAdmin)

class EventsAdmin(admin.ModelAdmin):
	list_display = ('user_id', 'type', 'sub_type', 'library_name')
	ordering = ('user_id', 'type')

admin.site.register(h5p_events, EventsAdmin)

class CountersAdmin(admin.ModelAdmin):
	list_display = ('type', 'library_name', 'num')
	ordering = ('type', 'library_name')

admin.site.register(h5p_counters, CountersAdmin)