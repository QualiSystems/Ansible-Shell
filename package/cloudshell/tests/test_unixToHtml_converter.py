from unittest import TestCase
from cloudshell.cm.ansible.domain.output.unixToHtmlConverter import UnixToHtmlColorConverter

class TestUnixToHtmlColorConverter(TestCase):
    def setUp(self):
        self.color_converter = UnixToHtmlColorConverter()

    def test_convert_all_colors(self):
        text = 'i am white'
        expectedText = '<font color=white>i am white'
        for key,value in self.color_converter.unixToHtml.iteritems():
            representing_text = 'i am '
            text += key.replace("\\","") + representing_text + value
            expectedText+='</font><font color=' + value + '>' + representing_text + value
        expectedText+='</font>'
        self.assertEqual(self.color_converter.convert(text),expectedText)

    def test_convert_no_color(self):
        text='i am text with no colors'
        expectedText = '<font color=white>' + text + '</font>'
        self.assertEqual(self.color_converter.convert(text), expectedText)

    def test_convert_empty_text(self):
        text = ''
        expectedText = '<font color=white></font>'
        self.assertEqual(self.color_converter.convert(text), expectedText)
