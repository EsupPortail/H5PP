from django.conf import settings
from django.contrib.sites.models import Site



def get_media_url():
    if "://" in settings.MEDIA_ROOT and not "site_media" in MEDIA_ROOT:
        return "{}{}".format(settings.MEDIA_ROOT, settings.MEDIA_URL)
    else:
        return settings.MEDIA_URL