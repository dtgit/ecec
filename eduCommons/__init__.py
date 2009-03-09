from Products.CMFCore.utils import ContentInit
from config import PROJECTNAME, GLOBALS
from Products.CMFCore.permissions import AddPortalContent
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore.DirectoryView import registerDirectory
from AccessControl import allow_module, allow_class
from collective.captcha.browser.captcha import Captcha

allow_module('collective.captcha.browser.captcha')
allow_class(Captcha) 

def initialize(context):

    import content

    content_types, constructors, ftis = process_types(listTypes(PROJECTNAME), PROJECTNAME)

    ContentInit(PROJECTNAME + ' Content',
                content_types=content_types,
                permission=AddPortalContent,
                extra_constructors=constructors,
                fti=ftis,
                ).initialize(context)

registerDirectory('skins', GLOBALS)
