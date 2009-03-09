##################################################################################
#    Copyright (C) 2006-2007 Utah State University, All rights reserved.          
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

from interfaces import IIMSTransportUtility
from OFS.SimpleItem import SimpleItem
from zope.interface import implements
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.IMSTransport.config import *
from Products.IMSTransport.interfaces import IIMSManifestWriter, IIMSManifestReader
from Products.IMSTransport.Manifest import ZipfileReader, ZipfileWriter
from zipfile import BadZipfile
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

class IMSTransportUtility(SimpleItem):
    """ IMS Transport Utility """

    tocpage = PageTemplateFile('tableofcontents', WWW_DIR)

    implements(IIMSTransportUtility)
    
    def importZipfile(self, object, file, package_type, mdVersions=None, rtype='IMSTransport'):
        """ Import a zip file. """

        reader = IIMSManifestReader(object)
        reader.setReaderType(rtype)
        try:
            zfr = ZipfileReader(file)
        except BadZipfile, e:
            return False, 'Zip', e
        reader.setSource(zfr)
        if mdVersions:
            reader.setRequiredMetadataSections(mdVersions)

	imstransport = object.portal_properties.ims_transport_properties
        pt = getattr(imstransport, package_type, None)
        return reader.readManifest(pt)

    def exportZipfile(self, object, filename, wtype='IMSTransport'):
        """ Export a zip file. """
        writer = IIMSManifestWriter(object)
        writer.setWriterType(wtype)
        writer.setDestination(ZipfileWriter(filename, object.getId()))
        return writer.writeManifest()
