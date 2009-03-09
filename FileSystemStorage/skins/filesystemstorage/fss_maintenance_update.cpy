## Controller Python Script "fss_maintenance_update"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title= Update FileSystem storage
# Copyright (c) Ingeniweb 2007
# $Id: fss_maintenance_update.cpy 45387 2007-07-10 17:10:32Z glenfant $

try:
    from Products.CMFPlone.utils import getFSVersionTuple
    PLONE_VERSION = getFSVersionTuple()[:2]
except ImportError, e:
    PLONE_VERSION = (2, 0)

from Products.CMFCore.utils import getToolByName

fss_tool = getToolByName(context, 'portal_fss')

# Update filesystem storage
fss_tool.updateFSS()

message = 'message_filesystem_storage_updated'
if PLONE_VERSION >= (2, 5):
    from Products.CMFPlone import PloneMessageFactory as _
    context.plone_utils.addPortalMessage(_(unicode(message)))
    return state.set(status='success')
else:
    return state.set(status='success', portal_status_message=message)
