from zope.component import getUtility, getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.annotation.interfaces import IAnnotations
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName
from Products.eduCommons import portlet
from Products.eduCommons.utilities.interfaces import IECUtility
from Products.eduCommons.interfaces import IClearCopyrightable, IClearCopyright, ICourseUpdateEvent, IDeleteCourseObjectEvent, IAccessibilityCompliantable, IAccessibilityCompliant
from zope.component.interfaces import ObjectEvent
from zope.interface import implements


def add_course_portlets(obj, evt):
    """ add Course Summary portlet and OER Recommender portlet upon Course Creation  """
    rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=obj)
    right = getMultiAdapter((obj, rightColumn), IPortletAssignmentMapping, context=obj)

    #This code breaks the course object when the server has no outbound access to the web
    if u'OER Recommender' not in right:
        right[u'OER Recommender'] = portlet.oerrecommenderportlet.Assignment()

    if u'Course Summary' not in right:
        right[u'Course Summary'] = portlet.courseinfoportlet.Assignment()

    if u'Reuse Course' not in right:
        right[u'Reuse Course'] = portlet.reusecourseportlet.Assignment()


def set_default_creators(obj, evt):
    """ sets default value for Creator for newly created objects within a Course  """
    #Try block for instantiating Plone site
    try:
        ecutils = getUtility(IECUtility)
    except ComponentLookupError: 
        return

    creators = obj.Schema()['creators']

    if hasattr(obj, 'getECParent'):
        parent = obj.getECParent()

        #Check to see if this is a temp obj and within a course
        if obj.isTemporary() and parent.meta_type == 'Course' and obj.Type() != 'Course':
            creators.set(obj, ('(course_default)', ))

def set_default_excludefromnav(obj, evt):
    """ sets the default value for excludeFromNav or image, file, and document to True  """
    exclude = obj.Schema()['excludeFromNav']
    if obj.isTemporary() and obj.Type() not in ['Division', 'Course']:
        exclude.set(obj, True)

def update_clear_copyright(obj, evt):
    """ update clear copyright annotation  """
    if IClearCopyrightable.providedBy(evt.object):
	if hasattr(evt.object.REQUEST, 'clearedCopyright'):
	    if hasattr(evt.object.REQUEST, 'id'):
	        if evt.object.id == evt.object.REQUEST['id']:
                    IAnnotations(evt.object)['eduCommons.clearcopyright'] = evt.object.REQUEST['clearedCopyright']
                    evt.object.reindexObject()
        else:
	    IAnnotations(evt.object)['eduCommons.clearcopyright'] = False
            evt.object.reindexObject()

def update_accessibility_compliant(obj, evt):
    """ update accessibility compliant annotation  """
    if IAccessibilityCompliantable.providedBy(evt.object):
	if hasattr(evt.object.REQUEST, 'accessibilitycompliant'):
	    if hasattr(evt.object.REQUEST, 'id'):
	        if evt.object.id == evt.object.REQUEST['id']:
                    IAnnotations(evt.object)['eduCommons.accessible'] = evt.object.REQUEST['accessibilitycompliant']
                    evt.object.reindexObject()
        else:
	    IAnnotations(evt.object)['eduCommons.accessible'] = False
            evt.object.reindexObject()

def reindexOnReorder(obj, event):
    obj.reindexObject()



class CourseUpdate(ObjectEvent):
    """ Set namespace information in manifest. """
    implements(ICourseUpdateEvent)

    def __init__(self, object, workflow_action, bulkChange, initial_state=None):
        super(CourseUpdate, self).__init__(object)
        self.object = object
        self.target = workflow_action
        self.bulkChange = bulkChange
        self.initial_state = initial_state

class DeleteObjectEvent(ObjectEvent):
    """ Set namespace information in manifest. """
    implements(IDeleteCourseObjectEvent)

    def __init__(self, object, bulkChange, contains_published):
        super(DeleteObjectEvent, self).__init__(object)
        self.object = object
        self.bulkChange = bulkChange
        self.contains_published = contains_published

