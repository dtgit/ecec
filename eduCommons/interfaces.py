from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager
from zope.annotation.interfaces import IAnnotatable
from zope.app.event.interfaces import IObjectEvent

class IPortalObject(Interface):
    """  Marker interface for the Portal Object """

class ICoursesTopic(Interface):
    """ Marker interface for Courses Topic, which implements the course list. """

class IDivision(Interface):
    """ Marker interface for Division object type. """

class ICourse(Interface):
    """ Marker interface for Course object type. """

class IFSSFile(Interface):
    """ Marker interface for FSSFile object type. """

class IFeedback(Interface):
    """ Marker interface for Feedback object type.  """

class IClearCopyrightable(IAnnotatable):
    """ Marker interface  """

class IAccessibilityCompliantable(IAnnotatable):
    """ Marker interface  """

class ICourseOrderable(IAnnotatable):
    """ Marker interface """

class IClearCopyright(Interface):
    """ Cleared Copyright interface  """

    def getClearedCopyright():
        """ Get the Cleared Copyright value  """

    def setClearedCopyright():
        """ Set the Cleared Copyright value  """

class IAccessibilityCompliant(Interface):
    """ Accessibility Compliant interface  """

    def getAccessibilityCompliant():
        """ Get the accessibility Compliant value  """

    def setAccessibilityCompliant():
        """ Set the accessibility Compliant value  """

class IOpenOCWSite(Interface):
    """ Marker interface to mark eduCommons site as an OpenOCW site. """

class ICourseUpdateEvent(IObjectEvent):
    """ Fire a Course Update Event """

class IDeleteCourseObjectEvent(IObjectEvent):
    """ Fire an event when an object is deleted """
