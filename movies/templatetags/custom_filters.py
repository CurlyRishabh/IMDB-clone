from django import template

register = template.Library()


@register.filter(name='split_by_comma')
def split_by_comma(value):
    return value.split(', ')


@register.filter(name='times') 
def times(number):
    return range(number)
