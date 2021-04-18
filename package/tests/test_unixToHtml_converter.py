from unittest import TestCase
from cloudshell.cm.ansible.domain.output.unixToHtmlConverter import UnixToHtmlColorConverter


class TestUnixToHtmlColorConverter(TestCase):
    def setUp(self):
        self.color_converter = UnixToHtmlColorConverter()

    def test_convert_all_colors(self):
        text = 'i am white'
        expectedText = '<html><body>i am white'
        for key,value in self.color_converter.unixToHtml.items():
            representing_text = 'i am '
            text += key.replace("\\","") + representing_text + value
            expectedText+='<font color=' + value + '>' + representing_text + value +'</font>'
        expectedText+='</body></html>'
        self.assertEqual(self.color_converter.convert(text),expectedText)

    def test_convert_no_color(self):
        text='i am text with no colors'
        expectedText = '<html><body>' + text + '</body></html>'
        self.assertEqual(self.color_converter.convert(text), expectedText)

    def test_convert_empty_text(self):
        text = ''
        expectedText = '<html><body></body></html>'
        self.assertEqual(self.color_converter.convert(text), expectedText)
