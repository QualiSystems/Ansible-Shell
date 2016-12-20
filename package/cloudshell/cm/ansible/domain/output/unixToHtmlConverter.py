import re

class UnixToHtmlColorConverter(object):
    def __init__(self, text):
        self.unixToHtml = dict([
            (re.escape('\033[0;32m'), 'green'),
            (re.escape('\033[0;36m'), 'cyan'),
            (re.escape('\033[0;31m'), 'red'),
            (re.escape('\033[1;33m'), 'red'),
            (re.escape('\033[0;35m'), 'purple'),
            (re.escape('\033[1;35m'), 'purple flower'),
            (re.escape('\033[0m'), 'white')
        ])
        self.isFirstColor = True
        self.text = text

    def _addFontTag(self,x):
        result = ''
        if not self.isFirstColor:
            result = '</font><font color=' + self.unixToHtml[re.escape(x.group(0))] + '>'
        else:
            result = '<font color=' + self.unixToHtml[re.escape(x.group(0))] + '>'
            self.isFirstColor = False
        return result;

    def convert(self):
        p_object = re.compile('|'.join(self.unixToHtml.keys()))
        result = p_object.sub(lambda x: self._addFontTag(x), self.text)
        if not self.isFirstColor:
            result += '</font>'
        return result;