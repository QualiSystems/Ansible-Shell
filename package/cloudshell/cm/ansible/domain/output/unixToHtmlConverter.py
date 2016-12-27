import os
import re


class UnixToHtmlColorConverter(object):
    def __init__(self):
        self.unixToHtml = dict([
            (re.escape('\033[0m'), 'white'),

            (re.escape('\033[0;30m'), 'gray'),
            (re.escape('\033[0;31m'), 'red'),
            (re.escape('\033[0;32m'), 'green'),
            (re.escape('\033[0;33m'), 'brown'),
            (re.escape('\033[0;34m'), 'blue'),
            (re.escape('\033[0;35m'), 'purple'),
            (re.escape('\033[0;36m'), 'cyan'),
            (re.escape('\033[0;37m'), 'gray'),

            (re.escape('\033[1;30m'), 'gray'),
            (re.escape('\033[1;31m'), 'red'),
            (re.escape('\033[1;32m'), 'green'),
            (re.escape('\033[1;33m'), 'brown'),
            (re.escape('\033[1;34m'), 'blue'),
            (re.escape('\033[1;35m'), 'purple'),
            (re.escape('\033[1;36m'), 'cyan'),
            (re.escape('\033[1;37m'), 'gray'),
        ])
        self.is_first_color = True

    def _add_font_tag(self, x):
        return '</font><font color=' + self.unixToHtml[re.escape(x.group(0))] + '>'

    def convert(self, text):
        result = '<html><body><font color=white>'
        p_object = re.compile('|'.join(self.unixToHtml.keys()))
        result += p_object.sub(lambda x: self._add_font_tag(x), text)
        result += '</font></body></html>'
        result = '<br />'.join([line for line in result.split(os.linesep) if line])
        return result;