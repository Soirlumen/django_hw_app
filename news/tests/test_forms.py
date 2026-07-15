from hw.tests.setUp import BaseHWTestCase
from news.forms import CreateEditPost

class TestNewsPostForm(BaseHWTestCase):
     def test_valid_form(self):
          f_data={
               "announcement":"AAAAAA",}
          form=CreateEditPost(data=f_data)
          self.assertTrue(form.is_valid())
     