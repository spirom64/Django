from django import template
from django.conf import settings
import os

register = template.Library()

@register.filter
def getdict_update_date(getdict, post):
    getdict = getdict.copy()
    getdict['date'] = f'{post.published_at:%Y-%m-%d}'
    return '&'.join([f'{key}={getdict[key]}' for key in getdict.keys()])

@register.filter
def getdict_update_tag(getdict, tag):
    getdict = getdict.copy()
    getdict['tag'] = tag.strip()
    return '&'.join([f'{key}={getdict[key]}' for key in getdict.keys()])

@register.filter
def get_basename(path):
    return os.path.basename(path)

@register.filter
def get_media_url(filename):
    return os.path.join(settings.MEDIA_URL, filename)