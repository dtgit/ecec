# -*- coding: utf-8 -*-
## Copyright (C) 2007 Ingeniweb

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
FSS configuration schema factory
$Id: schema.py 43824 2007-06-15 17:08:16Z glenfant $
"""

__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

import os

from ZConfig.datatypes import Registry
from ZConfig.loader import SchemaLoader

import datatypes

_this_dir = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE = os.path.join(_this_dir, "schema.xml")

# Our registry
fssRegistry = Registry(stock=None)
fssRegistry.register('existing-storage-path', datatypes.existingStoragePath)
fssRegistry.register('existing-backup-path', datatypes.existingBackupPath)
fssRegistry.register('strategy', datatypes.strategy)

# Our configuration schema
fssSchema = None
def loadSchema(filepath, registry=fssRegistry, overwrite=False):
    """Sets up fssSchema
    @param filepath: path to schema xml file
    @param registry: ZConfig.datatypes.Registry
    @param overwrite: True to change fss
    """

    global fssSchema
    if fssSchema is not None and not overwrite:
        raise RuntimeError, 'Schema already loaded'
    schemaLoader = SchemaLoader(registry=registry)
    fssSchema = schemaLoader.loadURL(filepath)
    return fssSchema

loadSchema(SCHEMA_FILE)

__all__ = ('fssSchema')
