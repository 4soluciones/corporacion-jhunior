from django import template
import decimal

register = template.Library()


@register.filter(name='thousands_separator')
def thousands_separator(value):
    if value is not None and value != '':
        return '{:,}'.format(value)
    return ''


@register.filter(name='replace_round')
def replace_round(value):
    if value is not None and value != '':
        return str(round(value, 2)).replace(',', '.')
    return value


@register.filter(name='zfill')
def zfill(value):
    if value is not None and value != '':
        return str(value).zfill(3)
    return value


@register.filter(name='get')
def get(d, k):
    return d.get(k, None)


@register.filter(name='get_sub_total')
def get_sub_total(value):
    if value is not None and value != '':
        return str(round(decimal.Decimal(value) / decimal.Decimal(1.18), 6))
    return value


@register.filter(name='get_igv')
def get_igv(value):
    if value is not None and value != '':
        sub_total = round(decimal.Decimal(value) / decimal.Decimal(1.18), 6)
        return str(value - sub_total)
    return value


@register.filter(name='multiply_6')
def multiply_6(value, arg):
    try:
        result = decimal.Decimal(value) * decimal.Decimal(arg)
        return str(round(result, 6))
    except (decimal.InvalidOperation, TypeError, ValueError):
        return ''
