from zope.publisher.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
from Products.eduCommons.interfaces import IClearCopyrightable
from Products.CMFPlone import PloneMessageFactory as _


class CopyrightView(BrowserView):
    """ Provides view of object with access to annotations in placeless environments"""
    def changeCopyright(self, value):
        """ Provides annotation to placeless script """
        context = self.context
        message = ''        
        if IClearCopyrightable.providedBy(context):
            anno = IAnnotations(context)
            if value == 'True':
                anno['eduCommons.clearcopyright'] = True
                message= _(u'Copyright Cleared')
            elif value == 'False':
                anno['eduCommons.clearcopyright'] = False
                message= _(u'Copyright Revoked')
        return message


