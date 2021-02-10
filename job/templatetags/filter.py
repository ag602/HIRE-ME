from django import template

register = template.Library()

@register.filter(name='split')
def split(value):
  print(value.split("hello, bello"))
  """
    Returns the value turned into a list.
  """
  return value.split(value)