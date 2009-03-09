from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import TextField, RichWidget
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import RFC822Marshaller
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.atct import ATFolder, ATFolderSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import AddPortalContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.eduCommons.interfaces import IDivision
from Products.eduCommons.config import PROJECTNAME

from Products.CMFPlone import PloneMessageFactory as _


DivisionSchema = ATFolderSchema.copy() + Schema((
    TextField('text',
              required=False,
              searchable=True,
              primary=True,
              storage = AnnotationStorage(migrate=True),
              validators = ('isTidyHtmlWithCleanup',),
              #validators = ('isTidyHtml',),
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                        description = '',
                        label = _(u'label_body_text', default=u'Body Text'),
                        rows = 25,
                        allow_file_upload = zconf.ATDocument.allow_document_upload),
              ),
    ),
    marshall=RFC822Marshaller()
    )

finalizeATCTSchema(DivisionSchema)
        


class Division(ATFolder):
    """ The Department/Division content object. """

    implements(IDivision)
    security = ClassSecurityInfo()
    schema = DivisionSchema
    portal_type = "Division"

    _at_rename_after_creation = True


    def initializeArchetype(self, **kwargs):
        ATFolder.initializeArchetype(self, **kwargs)
        deftext = self.restrictedTraverse('@@division_view')
        self.setText(deftext())

    def getECParent(self):
        """ Determine by acquisition if an object is a child of a course. """
        return self

registerATCT(Division, PROJECTNAME)
