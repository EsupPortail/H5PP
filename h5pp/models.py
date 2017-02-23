from django.db import models

# Stores information about what h5p uses what libraries 
class h5p_contents_libraries(models.Model):
	content_id = models.PositiveIntegerField(null=False)
	library_id = models.PositiveIntegerField(null=False)
	dependency_type = models.CharField(null=False, default='preloaded', max_length=31)
	drop_css = models.PositiveSmallIntegerField(null=False, default=0)
	weight = models.PositiveIntegerField(null=False, default=999999)

	class Meta:
		db_table = 'h5p_contents_libraries'
		unique_together = (('content_id', 'library_id', 'dependency_type'))

# Stores information about libraries
class h5p_libraries(models.Model):
	library_id = models.AutoField(primary_key=True)
	machine_name = models.CharField(null=False, default='', max_length=127)
	title = models.CharField(null=False, default='', max_length=255)
	major_version = models.PositiveIntegerField(null=False)
	minor_version = models.PositiveIntegerField(null=False)
	patch_version = models.PositiveIntegerField(null=False)
	runnable = models.PositiveSmallIntegerField(null=False, default=1)
	fullscreen = models.PositiveSmallIntegerField(null=False, default=0)
	embed_types = models.CharField(null=False, default='', max_length=255)
	preloaded_js = models.TextField(null=True)
	preloaded_css = models.TextField(null=True)
	drop_library_css = models.TextField(null=True)
	semantics = models.TextField(null=False)
	restricted = models.PositiveSmallIntegerField(null=False, default=0)
	tutorial_url = models.CharField(null=True, max_length=1000)

	class Meta:
		db_table = 'h5p_libraries'

# Stores information about library dependencies
class h5p_libraries_libraries(models.Model):
	library_id = models.PositiveIntegerField(null=False)
	required_library_id = models.PositiveIntegerField(null=False)
	dependency_type = models.CharField(null=False, max_length=31)

	class Meta:
		db_table = 'h5p_libraries_libraries'
		unique_together = (('library_id', 'required_library_id'))

# Stores translations for the languages
class h5p_libraries_languages(models.Model):
	library_id = models.PositiveIntegerField(null=False)
	language_code = models.CharField(null=False, max_length=31)
	language_json = models.TextField(null=False)

	class Meta:
		db_table = 'h5p_libraries_languages'
		unique_together = (('library_id', 'language_code'))

# Stores information about where the h5p content is stored
class h5p_contents(models.Model):
	content_id = models.AutoField(primary_key=True)
	title = models.CharField(null=False, max_length=255)
	json_contents = models.TextField(null=False)
	embed_type = models.CharField(null=False, default='', max_length=127)
	disable = models.PositiveIntegerField(null=False, default=0)
	main_library_id = models.PositiveIntegerField(null=False)
	content_type = models.CharField(null=True, max_length=127)
	author = models.CharField(null=True, max_length=127)
	license = models.CharField(null=True, max_length=7)
	meta_keywords = models.TextField(null=True)
	meta_description = models.TextField(null=True)
	filtered = models.TextField(null=False)
	slug = models.CharField(null=False, max_length=127)

	class Meta:
		db_table = 'h5p_contents'

# Stores user statistics
class h5p_points(models.Model):
	content_id = models.PositiveIntegerField(null=False)
	uid = models.PositiveIntegerField(null=False)
	started = models.PositiveIntegerField(null=False)
	finished = models.PositiveIntegerField(null=False, default=0)
	points = models.PositiveIntegerField(null=True)
	max_points = models.PositiveIntegerField(null=True)

	class Meta:
		db_table = 'h5p_points'
		unique_together = (('content_id', 'uid'))

# Stores user data about the content
class h5p_content_user_data(models.Model):
	user_id = models.PositiveIntegerField(null=False)
	content_main_id = models.PositiveIntegerField(null=False)
	sub_content_id = models.PositiveIntegerField(null=False)
	data_id = models.CharField(null=False, max_length=127)
	timestamp = models.PositiveIntegerField(null=False)
	data = models.TextField(null=False)
	preloaded = models.PositiveSmallIntegerField(null=True)
	delete_on_content_change = models.PositiveSmallIntegerField(null=True)

	class Meta:
		db_table = 'h5p_content_user_data'
		unique_together = (('user_id', 'content_main_id', 'sub_content_id', 'data_id'))

# Keeps track of what happens in the H5p system
class h5p_events(models.Model):
	user_id = models.PositiveIntegerField(null=False)
	created_at = models.IntegerField(null=False)
	type = models.CharField(null=False, max_length=63)
	sub_type = models.CharField(null=False, max_length=63)
	content_id = models.PositiveIntegerField(null=False)
	content_title = models.CharField(null=False, max_length=255)
	library_name = models.CharField(null=False, max_length=127)
	library_version = models.CharField(null=False, max_length=31)

	class Meta:
		db_table = 'h5p_events'

# Global counters for the H5P system
class h5p_counters(models.Model):
	type = models.CharField(null=False, max_length=63)
	library_name = models.CharField(null=False, max_length=127)
	library_version = models.CharField(null=False, max_length=31)
	num = models.PositiveIntegerField(null=False)

	class Meta:
		db_table = 'h5p_counters'
		unique_together = (('type', 'library_name', 'library_version'))