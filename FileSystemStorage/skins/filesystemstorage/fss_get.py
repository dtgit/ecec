## Script (Python) "fss_get"
##title=Get content stored by FileSystemStorage
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
# Copyright (c) Ingeniweb 2007
# $Id: fss_get.py 43824 2007-06-15 17:08:16Z glenfant $

from Products.CMFCore.utils import getToolByName

NotFound = "NotFound"

if len(traverse_subpath) < 1:
    raise NotFound, "Unknown page."

# Get FSS Item
name = traverse_subpath[0]
fsstool = getToolByName(context, 'portal_fss')
obj = fsstool.getFSSItem(context, name)

if obj is None:
    raise NotFound, "Unknown page."

if len(traverse_subpath) > 1:
    # Maybe call method of object
    cmd_name = traverse_subpath[1]
    cmd = getattr(obj, 'evalCmd')
    return cmd(cmd_name)
else:
    REQUEST = context.REQUEST
    return obj.index_html(REQUEST)
