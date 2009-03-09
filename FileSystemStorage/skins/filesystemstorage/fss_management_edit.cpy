## Controller Python Script "fss_management_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=rdf_enabled=0, rdf_script=''
##title= Manage FileSystem storage
# Copyright (c) Ingeniweb 2007
# $Id: fss_management_edit.cpy 45387 2007-07-10 17:10:32Z glenfant $

try:
    from Products.CMFPlone.utils import getFSVersionTuple
    PLONE_VERSION = getFSVersionTuple()[:2]
except ImportError, e:
    PLONE_VERSION = (2, 0)

from Products.CMFCore.utils import getToolByName

fss_tool = getToolByName(context, 'portal_fss')

# Save properties
fss_tool.enableRDF(rdf_enabled)
fss_tool.setRDFScript(rdf_script)

message = 'message_properties_saved'
if PLONE_VERSION >= (2, 5):
    from Products.CMFPlone import PloneMessageFactory as _
    context.plone_utils.addPortalMessage(_(unicode(message)))
    return state.set(status='success')
else:
    return state.set(status='success', portal_status_message=message)

