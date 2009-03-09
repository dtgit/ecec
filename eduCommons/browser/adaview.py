from zope.publisher.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from Products.eduCommons.interfaces import IADACompliantable


class ADACompliantView(BrowserView):
    """ Provides view of object with access to annotations in placeless environments"""
    def changeADA(self, value):
        """ Provides annotation to placeless script """
        context = self.context
        message = ''        
        if IADACompliantable.providedBy(context):
            anno = IAnnotations(context)
            if value == 'True':
                anno['eduCommons.ADA'] = True
                message=_(u'ADA Compliant set to True')
            elif value == 'False':
                anno['eduCommons.ADA'] = False
                message=_(u'ADA Compliant set to False')
        return message


