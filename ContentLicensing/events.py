##################################################################################
#    Copyright (C) 2004-2007 Utah State University, All rights reserved.          
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

__author__ = 'Brent Lambert, David Ray, Jon Thomas'
__docformat__ = 'restructuredtext'
__version__ = "$Revision: 1 $"[11:-2]

from zope.component import getUtility
from Products.ContentLicensing.utilities.interfaces import IContentLicensingUtility


def recursive_license(obj, evt):
    if not getattr(obj, 'REQUEST', None) or not obj.REQUEST.has_key('recurse_folders'):
        return
    #Recursively Licenses objects
    clutil = getUtility(IContentLicensingUtility)
    brains = obj.portal_catalog.searchResults(path={'query':('/'.join(obj.getPhysicalPath())+'/'), })
    for brain in brains:
        object = brain.getObject()
        if clutil.isLicensable(object):
            clutil.setObjLicense(object)
    
