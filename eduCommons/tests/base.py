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

from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite
from Testing import ZopeTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite, ZopeDocFileSuite, Functional
from Testing.ZopeTestCase import ZopeDocFileSuite
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase, setupPloneSite, installProduct

installProduct('ContentLicensing')
installProduct('ZipFileTransport')
installProduct('IMSTransport')
installProduct('PloneBookmarklets')
installProduct('leftskin')
installProduct('ProxyIndex')
installProduct('eduCommons')
installProduct('LinguaPlone')


setupPloneSite(with_default_memberarea=0,
               extension_profiles=['Products.ContentLicensing:default',
                                   'Products.ZipFileTransport:default',
                                   'Products.IMSTransport:default',
                                   'Products.PloneBookmarklets:default',
                                   'Products.LinguaPlone:LinguaPlone',
                                   'Products.leftskin:default',
                                   'Products.eduCommons:default'])

               

oflags = (doctest.ELLIPSIS |
          doctest.NORMALIZE_WHITESPACE)

prod = 'Products.eduCommons'


class eduCommonsTestCase(PloneTestCase):
    """ Base class for integration tests. """

    def _setupHomeFolder(self):
        """ Ugly hack to keep the underlying testing framework from trying to create
            a user folder. """
        pass


class eduCommonsFunctionalTestCase(Functional, eduCommonsTestCase):
    """ Base class for functional integration tests. """


