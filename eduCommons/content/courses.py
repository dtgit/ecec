from Products.Archetypes.atapi import registerType
from Products.ATContentTypes.atct import ATTopic, ATTopicSchema
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.eduCommons.interfaces import ICoursesTopic
from Products.eduCommons.config import PROJECTNAME

CoursesTopicSchema = ATTopicSchema.copy()

class CoursesTopic(ATTopic):
    
    implements(ICoursesTopic)
    security = ClassSecurityInfo()
    schema = CoursesTopicSchema
    portal_type = "CoursesTopic"

    _at_rename_after_creation = True

registerType(CoursesTopic, PROJECTNAME)
