from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def tr(context, obj, field):
    """Render a bilingual model field in the visitor's current language."""
    lang = context.get("LANG", "ka")
    return obj.t(field, lang)


@register.filter
def gel(value):
    """Format a Decimal as GEL: 150 ₾ / 149.50 ₾."""
    if value is None:
        return ""
    value = float(value)
    if value == int(value):
        return f"{int(value)} ₾"
    return f"{value:.2f} ₾"
