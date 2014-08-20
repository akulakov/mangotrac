from django import template
from django.conf import settings

register = template.Library()

def getattribute(value, arg):
    """Gets an attribute of an object dynamically from a string name"""
    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, 'has_key') and value.has_key(arg):
        return value[arg]
    else:
        return settings.TEMPLATE_STRING_IF_INVALID

def get(value, arg):
    return value[arg]

def concat(value, arg):
    return value + arg

def val_or_rel_manager(value):
    if hasattr(value, "all"):
        return ' '.join( [unicode(i) for i in value.all()] )
    else:
        return value


register.filter("val_or_rel_manager", val_or_rel_manager)
register.filter("getattribute", getattribute)
register.filter("get", get)
register.filter("concat", concat)
