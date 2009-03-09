from Products.CMFPlone import MigrationTool
try:
    from Products.contentmigration.migrator import InlineFieldActionMigrator, BaseInlineMigrator
    from Products.contentmigration.walker import CustomQueryWalker
    haveContentMigrations = True
except ImportError:
    haveContentMigrations = False

import types

from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.Archetypes import transaction
from Products.Archetypes.BaseUnit import BaseUnit
from Products.CMFPlone.utils import safe_hasattr

from Products.ContentLicensing.tool import ContentLicensingTool
from Acquisition import aq_base
from Products.ContentLicensing.Extensions import Install


def GenericToUnported (self, out):
    """ Change Jurisdiction to valid attribute
    """
    print >> out, "Changing Jurisdiction from Generic to Unported"
    if self.portal_contentlicensing.Jurisdiction == 'Generic':
        self.portal_contentlicensing._updateProperty('Jurisdiction','Unported')

def migrate(self):
    """Run migrations
    """
    out = StringIO()
    print >> out, "Starting Content Licensing Migration"
    GenericToUnported(self, out)
    print >> out, "Content Licensing Migration Completed"
    return out.getvalue()


