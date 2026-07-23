from django import template
from django.template.defaultfilters import stringfilter
import nh3
from django.utils.safestring import mark_safe
import markdown as md
# povolené značky
ALLOWED_TAGS = {
    'p', 'div', 'span', 'br', 'hr',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'em', 'b', 'i', 'u', 's', 'code', 'pre', 'blockquote',
    'ul', 'ol', 'li', 'a', 'img',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
}
# povolené atributy ke značkám
ALLOWED_ATTRIBUTES = {
    'a': {'href', 'title', 'target'},
    'img': {'src', 'alt', 'title', 'width', 'height'},
    'code': {'class'},
    'pre': {'class'},
}
register = template.Library()


@register.filter()
@stringfilter
def markdown(value):
    code=md.markdown(value,extensions=["markdown.extensions.fenced_code"])
    sanitize_code=nh3.clean(code, tags=ALLOWED_TAGS,attributes=ALLOWED_ATTRIBUTES)
    return mark_safe(sanitize_code)