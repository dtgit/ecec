## Controller Python Script "object_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a folder
##

from AccessControl import Unauthorized
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

REQUEST = context.REQUEST
if REQUEST.get('REQUEST_METHOD', 'GET').upper() == 'GET':
    raise Unauthorized, 'This method can not be accessed using a GET request'

parent = context.aq_inner.aq_parent
title = safe_unicode(context.title_or_id())

lock_info = context.restrictedTraverse('@@plone_lock_info')
if lock_info.is_locked():
    message = _(u'${title} is locked and cannot be deleted.',
            mapping={u'title' : title})
    context.plone_utils.addPortalMessage(message, type='error')
    return state.set(status = 'failure')
else:
    parent.manage_delObjects(context.getId())
    message = _(u'${title} has been deleted.',
                mapping={u'title' : title})
    context.restrictedTraverse('@@search_view').notifyDeleteObjectEvent(context,bulkChange=False,contains_published=True)
    transaction_note('Deleted %s' % context.absolute_url())
    context.plone_utils.addPortalMessage(message)
    return state.set(status = 'success')
