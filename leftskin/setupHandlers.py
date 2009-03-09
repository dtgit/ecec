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


from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from Products.CMFCore.interfaces import ISkinsTool

def importFinalSteps(context):
    site = context.getSite()

    # Setup left navigation
    leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=site)
    left = getMultiAdapter((site, leftColumn), IPortletAssignmentMapping, context=site)
    if u'navigation' in left:
        left[u'navigation'].topLevel = 0

    # Setup custom properties for skin
    stool = site.portal_skins
    if not stool.getSkinPath('custom/baseProperties'):
        stool.leftskin.base_properties.manage_doCustomize(folder_path='custom')
