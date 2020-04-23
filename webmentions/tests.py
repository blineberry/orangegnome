from django.test import TestCase
from .models import Webmention
from unittest import skip

# Create your tests here.
class WebmentionTestCase(TestCase):
    def setUp(self):
        pass

    def test_send__http_link_header_unquoted_rel_relative_url__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/1"))

    def test_send__http_link_header_unquoted_rel_absolute_url__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/2"))

    def test_send__html_link_tag_relative_url__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/3"))

    def test_send__html_link_tag_absolute_url__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/4"))

    def test_send__html_a_tag_relative_url__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/5"))

    def test_send__html_a_tag_absolute_url__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/6"))

    def test_send__http_link_header_with_strange_casing__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/7"))

    def test_send__http_link_header_quoted_rel__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/8"))

    def test_send__multiple_rel_values_on_a_link_tag__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/9"))

    def test_send__multiple_rel_values_on_a_link_header__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/10"))

    def test_send__multiple_webmention_endpoints_advertised_link_link_a__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/11"))

    def test_send__checking_for_exact_match_of_rel_webmention__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/12"))

    def test_send__false_endpoint_inside_an_HTML_comment__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/13"))

    def test_send__false_endpoint_in_escaped_HTML__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/14"))

    def test_send__webmention_href_is_an_empty_string__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/15"))

    def test_send__multiple_webmention_endpoints_advertised_a_link__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/16"))

    def test_send__multiple_2ebmention_endpoints_advertised_link_a__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/17"))
    
    def test_send__multiple_http_link_headers__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/18"))

    def test_send__single_http_link_header_with_multiple_values__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/19"))

    def test_send__link_tag_with_no_href_attribute__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/20"))

    def test_send__webmention_endpoint_has_query_string_parameters__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/21"))

    def test_send__webmention_endpoint_is_relative_to_the_path__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/22"))

    def test_send__webmention_target_is_a_redirect_and_the_endpoint_is_relative__returns_true(self):
        self.assertTrue(Webmention.send("https://orangegnome.com/posts/88/implementing-web-mentions","https://webmention.rocks/test/23/page"))