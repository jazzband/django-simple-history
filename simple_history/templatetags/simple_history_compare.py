from __future__ import unicode_literals

import difflib
from django import template

register = template.Library()


@register.simple_tag
def diff_table(a, b, line_split="\n"):
    differ = difflib.HtmlDiff(wrapcolumn=80)
    try:
        return differ.make_table(a.split(line_split), b.split(line_split))
    except AttributeError:
        if a != b:
            a = '<span class="diff_sub">{a}</span>'.format(a=a)
            b = '<span class="diff_add">{b}</span>'.format(b=b)
        return """<table class="diff" id="difflib_chg_to0__top" cellspacing="0" cellpadding="0" rules="groups">
    <colgroup></colgroup> <colgroup></colgroup> <colgroup></colgroup>
    <colgroup></colgroup> <colgroup></colgroup> <colgroup></colgroup>

    <tbody>
        <tr><td class="diff_next"><a href="#difflib_chg_to0__top">t</a></td><td class="diff_header" id="from0_1">1</td><td nowrap="nowrap">{a}</td><td class="diff_next"><a href="#difflib_chg_to0__top">t</a></td><td class="diff_header" id="to0_1">1</td><td nowrap="nowrap">{b}</td></tr>
    </tbody>
</table>
""".format(a=a, b=b)
