# -*- coding: utf-8 -*-
## FileSystemStorage
## 
## Copyright (C) 2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import StringIO
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.Field import FileField, StringField, TextField
from Products.Archetypes.Storage import AttributeStorage
from Products.FileSystemStorage.FileSystemStorage import FileSystemStorage

#
# This method is here for giving an example of storage migration.
# It asserts that you have set storage of FileField of 'Image' and 'File'
# content types to FileSystemStorage. It also asserts that old storage was
# AttributeStorage.
#
# This script is mainly here to give hints about storage migration
# It may not fulfill your needs, but the main idea is here.
# 

def migrateToFSStorage(self):
    """
    Migrate File and Images FileFields to FSStorage
    
    /!\ Assertion is made that the schema definition has been migrated to define
    FSS as storage for interested fields
    """
    try:
        fss_tool = getToolByName(self, 'portal_fss')
    except AttributeError:
        raise ValueError, "install and configure FileSystemStorage first!"
    
    out = StringIO.StringIO()
    cat = getToolByName(self, 'portal_catalog')
    brains = cat({'portal_type': ['File', 'Image']})

    # this defines are here to avoid instantiating a new one for each file
    # it is known to be harmless with those storages
    attr_storage = AttributeStorage()
    fss_storage = FileSystemStorage()
    
    for b in brains:
        o = b.getObject()
        print >> out, '/'.join(o.getPhysicalPath()), ":",

        # ensure we have an UID
        # it should not happen on a standard plone site, but I've met the case
        # with some weird custom types
        # the UID code was valid on a Plone 2.1.2 bundle (AT 1.3.7)
        if o.UID() is None:
            o._register()
            o._updateCatalog(o.aq_parent)
            print >> out, "UID was None, set to: ", o.UID(),

            
        for f in o.Schema().fields():
            # visit only FileFields with FileSystemStorage
            if not isinstance(f, FileField):
                continue
            storage = f.getStorage()
            if not isinstance(storage, FileSystemStorage):
                continue
            
            name = f.getName()
            print >> out, "'%s'" % name,
            
            # skip if field has already a content
            if f.get_size(o) != 0:
                print >> out, "already set",
                continue

            # get content from old storage and delete old storage
            try:
                content = attr_storage.get(name, o)
            except AttributeError:
                print >> out, "no old value",
                continue
            attr_storage.unset(name, o)
            
            fss_storage.initializeField(o, f) #FIXME: really needed?
            f.set(o, content)

            # unset empty files, this avoid empty files on disk
            if f.get_size(o) == 0:
                print >> out, "unset",
                f.set(o, "DELETE_FILE")
                
            print >> out, ",",

        # new line for next object
        print >> out, ""

    return out.getvalue()
