from base import eduCommonsTestCase

class TestPortlet(eduCommonsTestCase):

    def after_setup(self):
        self.setRoles(('Manager',))

    def testTests(self):
        self.assertEqual(1, 1)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    return suite
