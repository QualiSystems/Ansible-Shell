import re

class UnixToHtmlColorConverter(object):
    def __init__(self):
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


    def _addFontTag(self,x):
        return '</font><font color=' + self.unixToHtml[re.escape(x.group(0))] + '>'

    def convert(self, text):
        result = '<font color=white>'
        p_object = re.compile('|'.join(self.unixToHtml.keys()))
        result+= p_object.sub(lambda x: self._addFontTag(x), text)
        result += '</font>'
        return result;