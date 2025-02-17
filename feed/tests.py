from django.test import TestCase
from .fields import CommonmarkField

# Create your tests here.
class CommonmarkFieldTest(TestCase):
    def test_md_to_txt(self):
        self.assertEqual("commentary", CommonmarkField.md_to_txt("commentary"))
        