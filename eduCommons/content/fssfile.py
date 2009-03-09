from AccessControl import ClassSecurityInfo
from zope.interface import implements

# Archetypes imports
try:
    from Products.LinguaPlone.public import *
except ImportError: 
    # No multilingual support
    from Products.Archetypes.public import *

# Products imports
from Products.FileSystemStorage.FileSystemStorage import FileSystemStorage
from Products.ATContentTypes.atct import ATFile, ATFileSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.eduCommons.interfaces import IFSSFile
from Products.eduCommons.config import PROJECTNAME


from Products.CMFPlone import PloneMessageFactory as _

FSSFileSchema = ATFileSchema.copy() + Schema((
    FileField('file',
              required=False,
              primary=True,
              storage=FileSystemStorage(),
              widget = FileWidget(
                        description = u"Select the file to be added by clicking the 'Browse' button.",
                        description_msgid = "help_file",
                        label= "Large File",
                        label_msgid = "label_large_file",
                        i18n_domain = "eduCommons",
                        show_content_type = False,)),
    ), 
    marshall=RFC822Marshaller()
)
                                           
finalizeATCTSchema(FSSFileSchema)

class FSSFile(ATFile):
    """A storage item for IMS/ZIP copies of courses using FileSystemStorage"""

    implements(IFSSFile)
    
    security = ClassSecurityInfo()
    schema = FSSFileSchema
    portal_type = 'Large File'
    
    _at_rename_after_creation = True

    def initializeArchetype(self, **kwargs):
        ATFile.initializeArchetype(self, **kwargs)


registerATCT(FSSFile, PROJECTNAME)
