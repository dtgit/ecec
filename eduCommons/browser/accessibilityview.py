from zope.publisher.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from Products.eduCommons.interfaces import IAccessibilityCompliantable
from Products.CMFPlone import PloneMessageFactory as _


class AccessibilityCompliantView(BrowserView):
    """ Provides view of object with access to annotations in placeless environments"""
    def changeAccessibility(self, value):
        """ Provides annotation to placeless script """
        context = self.context
        message = ''        
        if IAccessibilityCompliantable.providedBy(context):
            anno = IAnnotations(context)
            if value == 'True':
                anno['eduCommons.accessible'] = True
                message=_(u'Accessibility Compliant set to True')
            elif value == 'False':
                anno['eduCommons.accessible'] = False
                message=_(u'Accessibility Compliant set to False')
        return message


