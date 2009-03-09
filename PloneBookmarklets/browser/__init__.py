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

from Products.Five.browser import BrowserView
from zope.component import getUtility
from zope.interface import implements
from urlparse import urlsplit
from xml.dom import minidom
from string import split, find


class BookmarkletsView(BrowserView):
    """ Render the bookmarklets view """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.props = self.context.portal_url.portal_properties.bookmarklets_properties

    def getSites(self):
        """ returns bookmarking sites. """
        page = self.aq_parent
        page_url = page.absolute_url()
        page_title = page.title.replace(' ', '+')
        page_descr = page.Description()
    
        
        displayed_sites = []
        sites = []       
    
        displayed_sites = self.props.displayed_sites 
    
        for x in displayed_sites: 
            sites.append(getattr(self.props, x)) 
        return sites

