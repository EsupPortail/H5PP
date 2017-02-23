# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='h5p_content_user_data',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.PositiveIntegerField()),
                ('content_main_id', models.PositiveIntegerField()),
                ('sub_content_id', models.PositiveIntegerField()),
                ('data_id', models.CharField(max_length=127)),
                ('timestamp', models.PositiveIntegerField()),
                ('data', models.TextField()),
                ('preloaded', models.PositiveSmallIntegerField(null=True)),
                ('delete_on_content_change', models.PositiveSmallIntegerField(null=True)),
            ],
            options={
                'db_table': 'h5p_content_user_data',
            },
        ),
        migrations.CreateModel(
            name='h5p_contents',
            fields=[
                ('content_id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('json_contents', models.TextField()),
                ('embed_type', models.CharField(default=b'', max_length=127)),
                ('disable', models.PositiveIntegerField(default=0)),
                ('main_library_id', models.PositiveIntegerField()),
                ('content_type', models.CharField(max_length=127, null=True)),
                ('author', models.CharField(max_length=127, null=True)),
                ('license', models.CharField(max_length=7, null=True)),
                ('meta_keywords', models.TextField(null=True)),
                ('meta_description', models.TextField(null=True)),
                ('filtered', models.TextField()),
                ('slug', models.CharField(max_length=127)),
            ],
            options={
                'db_table': 'h5p_contents',
            },
        ),
        migrations.CreateModel(
            name='h5p_contents_libraries',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_id', models.PositiveIntegerField()),
                ('library_id', models.PositiveIntegerField()),
                ('dependency_type', models.CharField(default=b'preloaded', max_length=31)),
                ('drop_css', models.PositiveSmallIntegerField(default=0)),
                ('weight', models.PositiveIntegerField(default=999999)),
            ],
            options={
                'db_table': 'h5p_contents_libraries',
            },
        ),
        migrations.CreateModel(
            name='h5p_counters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=63)),
                ('library_name', models.CharField(max_length=127)),
                ('library_version', models.CharField(max_length=31)),
                ('num', models.PositiveIntegerField()),
            ],
            options={
                'db_table': 'h5p_counters',
            },
        ),
        migrations.CreateModel(
            name='h5p_events',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.PositiveIntegerField()),
                ('created_at', models.IntegerField()),
                ('type', models.CharField(max_length=63)),
                ('sub_type', models.CharField(max_length=63)),
                ('content_id', models.PositiveIntegerField()),
                ('content_title', models.CharField(max_length=255)),
                ('library_name', models.CharField(max_length=127)),
                ('library_version', models.CharField(max_length=31)),
            ],
            options={
                'db_table': 'h5p_events',
            },
        ),
        migrations.CreateModel(
            name='h5p_libraries',
            fields=[
                ('library_id', models.AutoField(serialize=False, primary_key=True)),
                ('machine_name', models.CharField(default=b'', max_length=127)),
                ('title', models.CharField(default=b'', max_length=255)),
                ('major_version', models.PositiveIntegerField()),
                ('minor_version', models.PositiveIntegerField()),
                ('patch_version', models.PositiveIntegerField()),
                ('runnable', models.PositiveSmallIntegerField(default=1)),
                ('fullscreen', models.PositiveSmallIntegerField(default=0)),
                ('embed_types', models.CharField(default=b'', max_length=255)),
                ('preloaded_js', models.TextField(null=True)),
                ('preloaded_css', models.TextField(null=True)),
                ('drop_library_css', models.TextField(null=True)),
                ('semantics', models.TextField()),
                ('restricted', models.PositiveSmallIntegerField(default=0)),
                ('tutorial_url', models.CharField(max_length=1000, null=True)),
            ],
            options={
                'db_table': 'h5p_libraries',
            },
        ),
        migrations.CreateModel(
            name='h5p_libraries_languages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('library_id', models.PositiveIntegerField()),
                ('language_code', models.CharField(max_length=31)),
                ('language_json', models.TextField()),
            ],
            options={
                'db_table': 'h5p_libraries_languages',
            },
        ),
        migrations.CreateModel(
            name='h5p_libraries_libraries',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('library_id', models.PositiveIntegerField()),
                ('required_library_id', models.PositiveIntegerField()),
                ('dependency_type', models.CharField(max_length=31)),
            ],
            options={
                'db_table': 'h5p_libraries_libraries',
            },
        ),
        migrations.CreateModel(
            name='h5p_points',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_id', models.PositiveIntegerField()),
                ('uid', models.PositiveIntegerField()),
                ('started', models.PositiveIntegerField()),
                ('finished', models.PositiveIntegerField(default=0)),
                ('points', models.PositiveIntegerField(null=True)),
                ('max_points', models.PositiveIntegerField(null=True)),
            ],
            options={
                'db_table': 'h5p_points',
            },
        ),
        migrations.AlterUniqueTogether(
            name='h5p_points',
            unique_together=set([('content_id', 'uid')]),
        ),
        migrations.AlterUniqueTogether(
            name='h5p_libraries_libraries',
            unique_together=set([('library_id', 'required_library_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='h5p_libraries_languages',
            unique_together=set([('library_id', 'language_code')]),
        ),
        migrations.AlterUniqueTogether(
            name='h5p_counters',
            unique_together=set([('type', 'library_name', 'library_version')]),
        ),
        migrations.AlterUniqueTogether(
            name='h5p_contents_libraries',
            unique_together=set([('content_id', 'library_id', 'dependency_type')]),
        ),
        migrations.AlterUniqueTogether(
            name='h5p_content_user_data',
            unique_together=set([('user_id', 'content_main_id', 'sub_content_id', 'data_id')]),
        ),
    ]
