from zope.interface import implements
from zope.component import adapts, queryUtility

from zope.app.container.interfaces import INameChooser

from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser

from plone.portlets.interfaces import IPortletManager
from plone.portlets.constants import USER_CATEGORY

from plone.app.portlets.interfaces import IDefaultDashboard
from plone.app.portlets import portlets

from plone.app.portlets.storage import UserPortletAssignmentMapping
    
class DefaultDashboard(object):
    """The default default dashboard.
    """
    
    implements(IDefaultDashboard)
    adapts(IPropertiedUser)
    
    def __init__(self, principal):
        self.principal = principal
    
    def __call__(self):
        return {
            'plone.dashboard1' : (portlets.news.Assignment(), portlets.events.Assignment(),),
            'plone.dashboard2' : (portlets.recent.Assignment(),),
            'plone.dashboard3' : (),
            'plone.dashboard4' : (),
        }
