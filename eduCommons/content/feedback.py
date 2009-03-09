from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.atct import ATFolder, ATFolderSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import AddPortalContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.eduCommons.interfaces import IFeedback
from Products.eduCommons.config import PROJECTNAME



FeedbackSchema = ATFolderSchema.copy()

finalizeATCTSchema(FeedbackSchema)
        


class Feedback(ATFolder):
    """ The Feedback content object. """

    implements(IFeedback)
    security = ClassSecurityInfo()
    schema = FeedbackSchema
    portal_type = "Feedback"

    _at_rename_after_creation = True


    def initializeArchetype(self, **kwargs):
        ATFolder.initializeArchetype(self, **kwargs)
        self.setLayout('feedback_view')

registerATCT(Feedback, PROJECTNAME)
