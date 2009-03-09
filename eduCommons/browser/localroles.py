from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole
from Products.eduCommons.browser.interfaces import IeduCommonsSharingPageRole

from Products.CMFPlone import PloneMessageFactory as _

# These are for everyone

class ProducerRole(object):
    implements(IeduCommonsSharingPageRole)
    
    title = _(u"title_producer", default=u"Producer")
    required_permission = None
    
class QARole(object):
    implements(IeduCommonsSharingPageRole)
    
    title = _(u"title_QA", default=u"QA")
    required_permission = None
    
class PublisherRole(object):
    implements(IeduCommonsSharingPageRole)
    
    title = _(u"title_publisher", default=u"Publisher")
    required_permission = None

class ViewerRole(object):
    implements(IeduCommonsSharingPageRole)

    title = _(u"title_viewer", default=u"Viewer")
    required_permission = None
