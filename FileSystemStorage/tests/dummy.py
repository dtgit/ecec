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
Stubs for testing
$Id: dummy.py 43824 2007-06-15 17:08:16Z glenfant $
"""

from OFS.SimpleItem import SimpleItem
from ZPublisher.HTTPRequest import FileUpload


class FileUpload(FileUpload):
    """Dummy upload object.

    Used to fake uploaded files and images.
    """

    __allow_access_to_unprotected_subobjects__ = 1

    filename = 'dummy.gif'
    headers = {}

    def __init__(self, filename=None, headers=None, file=None):
        self.file = file
        if filename is not None:
            self.filename = filename
        if headers is not None:
            self.headers = headers

    def seek(self,*args):
        return self.file.seek(*args)

    def tell(self,*args):
        return self.file.tell(*args)

    def read(self,*args):
        return self.file.read(*args)
