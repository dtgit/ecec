##################################################################################
#
#    Copyright (C) 2006 Utah State University, All rights reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##################################################################################

__author__  = '''David Ray, Shane Graber'''
__docformat__ = 'plaintext'
__version__   = '$ Revision 0.0 $'[11:-2]

import logging

logger = logging.getLogger('PloneBookmarklets')

from config import GLOBALS
from Products.CMFCore.DirectoryView import registerDirectory

def initialize(context):
    pass

registerDirectory('skins', GLOBALS)


