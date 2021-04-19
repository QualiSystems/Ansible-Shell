import os
import re


class UnixToHtmlColorConverter(object):
    def __init__(self):
        self.unixToHtml = dict([
            (re.escape('\033[0m'), ''),

            (re.escape('\033[0;30m'), '#B0B0B0'),  # Black (gray)
            (re.escape('\033[0;31m'), '#C75646'),  # Red
            (re.escape('\033[0;32m'), '#8EB33B'),  # Green
            (re.escape('\033[0;33m'), '#D0B03C'),  # Yellow
            (re.escape('\033[0;34m'), '#72B3CC'),  # Blue
            (re.escape('\033[0;35m'), '#C8A0D1'),  # Purple
            (re.escape('\033[0;36m'), '#218693'),  # Cyan
            (re.escape('\033[0;37m'), '#B0B0B0'),  # Gray

            (re.escape('\033[1;30m'), '#5D5D5D'),  # Bright Black (gray)
            (re.escape('\033[1;31m'), '#E09690'),  # Bright Red
            (re.escape('\033[1;32m'), '#CDEE69'),  # Bright Green
            (re.escape('\033[1;33m'), '#FFE377'),  # Bright Yellow
            (re.escape('\033[1;34m'), '#9CD9F0'),  # Bright Blue
            (re.escape('\033[1;35m'), '#FBB1F9'),  # Bright Purple
            (re.escape('\033[1;36m'), '#77DFD8'),  # Bright Cyan
            (re.escape('\033[1;37m'), '#F7F7F7'),  # Bright Gray
        ])
        self.is_first_color = True

    def _add_font_tag(self, x):
        return '</font><font color=' + self.unixToHtml[re.escape(x.group(0))] + '>'

    def convert(self, text):
        result = '<html><body><font>'
        p_object = re.compile('|'.join(list(self.unixToHtml.keys())))
        result += p_object.sub(lambda x: self._add_font_tag(x), text)
        result += '</font></body></html>'
        # result = '<br />'.join([line for line in result.split(os.linesep) if line])
        result = '<br />'.join(result.replace(os.linesep + os.linesep, os.linesep).split(os.linesep))
        return result

    def remove_strike(self, raw_text):
        return re.sub(r"<S[^>]*>|<[^>]S>", "", raw_text)
