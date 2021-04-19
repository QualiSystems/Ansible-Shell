from unittest import TestCase
from cloudshell.cm.ansible.domain.output.unixToHtmlConverter import UnixToHtmlColorConverter


class TestUnixToHtmlColorConverter(TestCase):
    def setUp(self):
        self.color_converter = UnixToHtmlColorConverter()

    def test_convert_all_colors(self):
        text = 'i am white'
        expectedText = '<html><body><font>i am white'
        for key,value in self.color_converter.unixToHtml.items():
            representing_text = 'i am '
            text += key.replace("\\","") + representing_text + value
            expectedText+='</font><font color=' + value + '>' + representing_text + value
        expectedText+='</font></body></html>'
        self.assertEqual(self.color_converter.convert(text),expectedText)

    def test_convert_no_color(self):
        text='i am text with no colors'
        expectedText = '<html><body><font>' + text + '</font></body></html>'
        self.assertEqual(self.color_converter.convert(text), expectedText)

    def test_convert_empty_text(self):
        text = ''
        expectedText = '<html><body><font></font></body></html>'
        self.assertEqual(self.color_converter.convert(text), expectedText)
