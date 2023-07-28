import json
from django import template

register = template.Library()

@register.filter
def as_json(data):
    return json.dumps(data)