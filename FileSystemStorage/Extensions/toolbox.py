## -*- coding: utf-8 -*-
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
"""
$Id: toolbox.py 43824 2007-06-15 17:08:16Z glenfant $
"""

__author__  = ''
__docformat__ = 'restructuredtext'

# Python imports
from StringIO import StringIO
import Globals
import sys
import os

# CMF imports
from Products.CMFCore.utils import getToolByName

def check_filesystem(self, types=None, path=None):
    """Check all files. Is a file associated with an ATCT.
    Warning: Make sure uid_catalog is ok.
    """
    
    out = StringIO()
    portal_uids = []
    fs_uids = []
    utool = getToolByName(self, 'uid_catalog')
    
    if path is None:
        path = os.path.join(Globals.INSTANCE_HOME, 'var')
    
    if types is None:
        types = ['File', 'PloneExFile']
    
    out.write('Begin analyze in %s.\n' % path)
    
    # Get all uids from portal
    brains = utool(portal_type=types)
    
    for brain in brains:
        portal_uids.append(brain.UID)
    
    # Walk into filesystem
    for root, dirs, files in os.walk(path):
        if root == path:
            # Loop on files
            for item in files:
                words = item.split('_')
                
                if len(words) == 2 and len(words[0]) == 32:
                    uid = words[0]
                    fs_uids.append(uid)
    
    # Check portal uids not in fs uids
    out.write('Check portal uids not in filesystem uids.\n')
    errors_count = 0
    
    for uid in portal_uids:
        if uid not in fs_uids:
            out.write('%s failed.\n' % uid)
            errors_count += 1
    
    oks_count = len(portal_uids) - errors_count
    out.write('%d OK, %d FAILED.\n\n' % (oks_count, errors_count))
    
    
    # Check fs uids not in portal uids
    out.write('Check filesystem uids not in portal uids.\n')
    errors_count = 0
    
    for uid in fs_uids:
        if uid not in portal_uids:
            out.write('%s failed.\n' % uid)
            errors_count += 1
    
    oks_count = len(fs_uids) - errors_count
    out.write('%d OK, %d FAILED.\n\n' % (oks_count, errors_count))
    
    out.write('Analyze completed.\n')
    return out.getvalue()
