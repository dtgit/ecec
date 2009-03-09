

from zope.viewlet.interfaces import IViewletManager
from plone.theme.interfaces import IDefaultPloneLayer 

class IContentTop(IViewletManager):
    """ A viewlet manager that sits on top of the middle and right columns. """

class ILeftSkinTheme(IDefaultPloneLayer):
    """ Marker interface that defines a zope 3 layer for use witht the Left Skin Theme. """

