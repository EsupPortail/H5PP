from django.contrib import admin
from h5pp.models import *

class LibrariesAdmin(admin.ModelAdmin):
	list_display = ('title', 'library_id')
	ordering = ('title', 'library_id')
	readonly_fields = ('library_id', 'major_version', 'minor_version', 'patch_version')
	exclude = ('restricted', 'runnable')

admin.site.register(h5p_libraries, LibrariesAdmin)

class LibrariesLanguageAdmin(admin.ModelAdmin):
	list_display = ('library_id', 'language_code')
	ordering = ('library_id', 'language_code')
	readonly_fields = ('library_id',)

admin.site.register(h5p_libraries_languages, LibrariesLanguageAdmin)

class ContentsAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'content_type')
	ordering = ('title', 'author')
	readonly_fields = ('content_id', 'main_library_id')
	exclude = ('disable',)

admin.site.register(h5p_contents, ContentsAdmin)

class PointsAdmin(admin.ModelAdmin):
	list_display = ('content_id', 'uid', 'points', 'max_points')
	ordering = ('content_id', 'uid')
	readonly_fields = ('content_id', 'uid')
	exclude = ('started', 'finished')

admin.site.register(h5p_points, PointsAdmin)

class EventsAdmin(admin.ModelAdmin):
	list_display = ('user_id', 'type', 'sub_type')
	ordering = ('type', 'sub_type')
	readonly_fields = ('user_id', 'created_at', 'type', 'sub_type', 'content_id', 'content_title', 'library_name', 'library_version')

admin.site.register(h5p_events, EventsAdmin)