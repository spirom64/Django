from django import template

register = template.Library()

@register.filter
def getdict_update_date(getdict, news):
    getdict = getdict.copy()
    getdict['date'] = f'{news.published_at:%Y-%m-%d}'
    return '&'.join([f'{key}={getdict[key]}' for key in getdict.keys()])

@register.filter
def getdict_update_tag(getdict, tag):
    getdict = getdict.copy()
    getdict['tag'] = tag.strip()
    return '&'.join([f'{key}={getdict[key]}' for key in getdict.keys()])
