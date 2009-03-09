##################################################################################
#
#    Copyright (C) 2004-2006 Utah State University, All rights reserved.
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

__author__ = '''Brent Lambert, David Ray, Jon Thomas'''
__docformat__ = 'plaintext'
__version__   = '$ Revision 0.0 $'[11:-2]



from zope.event import notify
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from config import WWW_DIR
from ManifestEvents import ObjectWriteContributeNode, ObjectReadContributeNode, ObjectTransformPackage
from IMS_exceptions import ManifestError
import string
import mimetypes
import re
from xml.dom import minidom
from xml.xpath import Evaluate
import os
from libxslt import parseStylesheetDoc
from libxml2 import readFile, parseDoc
import mimetypes
from zope.component import getUtility
from Products.IMSTransport.utilities.interfaces import IIMSTransportUtility


class WebCTTransform:
    """ Transform WebCT content. """
    
    def __call__(self, event):
        if 'WebCT CE 6.0' == event.package_type[0]:
            self.doTransform(event.context, event.manifest, event.package_type, event.xformdata)

    def doTransform(self, context, manifest, package_type, xformdata):
        self.getFileData(manifest, xformdata, context)
        xformdata['manifest'] = context.performTransform(manifest, package_type)
        
    def evaluateExpressionNs(self,doc,nslist,expression):

        xc = doc.xpathNewContext()
        
        for ns in nslist:
            xc.xpathRegisterNs(ns[0],ns[1])        
            
        mods = xc.xpathEval(expression)
            
        return mods

    def getFileData(self, manifest, xformdata, context):
        
        doc = parseDoc(manifest)
        xc = doc.xpathNewContext()
        xc.xpathRegisterNs("imsct","http://www.imsproject.org/content")
        xc.xpathRegisterNs("lom","http://www.imsproject.org/metadata")
        
        modules = xc.xpathEval('/imsct:manifest/imsct:manifest')
        
        fdata = {}
        filename = ''

        
        for module in modules:
           
            xc.setContextNode(module)
            manifest_type = xc.xpathEval('.//lom:learningresourcetype/lom:value/lom:langstring')[0].getContent()
            manifest_title = xc.xpathEval('.//lom:general/lom:title/lom:langstring')[0].getContent()
            manifest_id = xc.xpathEval('.')[0].hasProp('identifier').getContent()
            
            if manifest_type == 'Content Module':
                
                tabletitle = manifest_title
                items = []

                xc.setContextNode(module)
                web_nodes = xc.xpathEval('imsct:resources//imsct:resource[@type=\"webcontent\"]')

                for web_node in web_nodes:
                    
                    
                    id = web_node.hasProp('identifier').getContent()
                    refname = ''
                    
                    xc.setContextNode(web_node)
                    file_node = xc.xpathEval("imsct:file")
                    title = xc.xpathEval("//imsct:item[@identifierref=\"" + id + "\"]/imsct:title")[0].getContent()
                    
                    if file_node:
                        refname = file_node[0].hasProp('href').getContent()
                                              
                        if not title:
                            title = refname
    
                        items.append((refname, title))

                ims_util = getUtility(IIMSTransportUtility)
                body = ims_util.tocpage(tabletitle=tabletitle, tocitems=items)
                fdata[manifest_id + '.html'] = body
                    
                
            elif manifest_type == 'URL':
                data = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                xc.setContextNode(module)
                url_title = xc.xpathEval("imsct:metadata//lom:title/lom:langstring")[0].getContent()
                url_filename = xc.xpathEval("imsct:resources/imsct:resource")[0].hasProp('identifier').getContent() + '.html'
                refname = xc.xpathEval("imsct:resources/imsct:resource/imsct:file")[0].hasProp('href').getContent() 
                
                data += "<a href =\"%s\">%s</a>" %(refname,url_title)
                
                fdata[url_filename] = data
                
                
            elif manifest_type == 'Glossary':
                xc.setContextNode(module)
                res_node = xc.xpathEval('imsct:resources//imsct:resource')[0]
                xc.setContextNode(res_node)
                hrefname = xc.xpathEval('imsct:file')[0].hasProp('href').getContent()

                data = context.source.readFile(hrefname)
                data = context.performTransform(data, ['WebCT Glossary', 'WebCT_glossary_xform.xsl'])
                filename = string.join(hrefname.split('.')[:-1],'.') + '.html'

                fdata[filename] = data
                
                
            elif manifest_type == 'Image Database':

                xc.setContextNode(module)
                web_nodes = xc.xpathEval('imsct:resources//imsct:resource')

                for web_node in web_nodes:
                    db_path = web_node.hasProp('href').getContent()
                    xc.setContextNode(web_node)
                    file_nodes = xc.xpathEval('imsct:file')
                    
                    for file_node in file_nodes:
                        hrefname = file_node.hasProp('href').getContent()
                        
                        if db_path == hrefname:
                            
                            items=[]
                            data = context.source.readFile(hrefname)
                            doc = parseDoc(data)
                            xcim = doc.xpathNewContext()
                            xcim.xpathRegisterNs("didl","http://www.mpeg.org/mpeg-21/2002/01-DIDL-NS")
                            tabletitle = xcim.xpathEval('/didl:DIDL/didl:CONTAINER/didl:DESCRIPTOR/didl:STATEMENT')[0].getContent()
                            containers = xcim.xpathEval('/didl:DIDL/didl:CONTAINER/didl:CONTAINER')

                            
                            for container in containers:
                                xcim.setContextNode(container)
                                title = xcim.xpathEval('didl:DESCRIPTOR/didl:STATEMENT')
                                if title:
                                    title = title[0].getContent()
                                refs = xcim.xpathEval('didl:REFERENCE')
                                
                                if refs:
                                    for ref in refs:
                                        urifile = string.replace(ref.hasProp('URI').getContent(),'.xml','.html')
                                        items.append((urifile, title))
                                    
                            filename = string.join(hrefname.split('.')[:-1],'.') + '.html'
                            ims_util = getUtility(IIMSTransportUtility)
                            body = ims_util.tocpage(tabletitle=tabletitle, tocitems=items)
                            
                            fdata[filename] = body
                            
                        elif re.compile('\.xml$').search(hrefname,1):
                            data = context.source.readFile(hrefname)
                            data = context.performTransform(data, ['WebCT Images', 'WebCT_image_xform.xsl'])
                            filename = string.join(hrefname.split('.')[:-1],'.') + '.html'

                            fdata[filename] = data
                    
        xformdata['filedata'] = fdata


WebCTTransformHandler = WebCTTransform()


class BlackboardTransform:
    """ Transfrom Blackboard content. """

    def __call__(self, event):
        if 'Blackboard 6.1/7.0' == event.package_type[0]:
            self.doTransform(event.context, event.manifest, event.package_type, event.xformdata)

    def doTransform(self, context, manifest, package_type, xformdata):
        """ Transform the blackboard package into something we can consume. """
        xformdata['filedata'] = {}
        self.getFileData(context, manifest, xformdata['filedata'])
        self.getNavigationData(context, manifest, xformdata['filedata'])
        xformdata['manifest'] = context.performTransform(manifest, package_type)

    def getFileData(self, context, manifest, filedata):
        """ Blackboard stores all its documents in XML format. Get these
            documents and transform them into HTML. """
        files = context.source.listFiles()
        for fn in files:
            if 'dat' == fn.split('.')[-1]:
                data = context.source.readFile(fn)
                doc = parseDoc(data)
                root = doc.getRootElement()
                if 'CONTENT' == root.name:
                    id = fn.split('.')[0]
                    docfn = id + '.html'
                    data = context.performTransform(data, ['Blackboard Content', 'Blackboard_content_import_xform.xsl'])
                    data = data.replace('@X@EmbeddedFile.location@X@', '%s/embedded/' %id)
                    filedata[docfn] = data.replace('@X@LOCALFOLDERLOCATION@X@', '%s/' %id)

    def getNavigationData(self, context, manifest, filedata):
        """ Blackboard embeds its navigation structure in the Organizations section
            of the manifest. Create documents with links to the resources so that
            eduCommons can recreate the navigation structure. """
        doc = parseDoc(manifest)
        nodes = doc.xpathEval('/manifest/organizations/organization/item')
        for n in nodes:
            tabletitle = n.xpathEval('title')[0].get_content()
            items = []
            for item in n.xpathEval('.//item'):
                id = '%s.html' %(item.prop('identifierref'))
                title = item.xpathEval('title')[0].get_content()
                if filedata.has_key(id) and filedata[id]:
                    items.append((id, title))
            if items:
                ims_util = getUtility(IIMSTransportUtility)
                body = ims_util.tocpage(tabletitle=tabletitle, tocitems=items)
                filedata[n.prop('identifierref') + '.html'] = body
    

BlackboardTransformHandler = BlackboardTransform()

#Currently not supported
class eXeTransform:
    """ Transform eXe content. """

    def __call__(self, event):
        if 'eXe' == event.package_type[0]:
            self.doTransform(event.context, event.manifest, event.package_type, event.xformdata)

    def doTransform(self, context, manifest, package_type, xformdata):
        xformdata['manifest'] = context.performTransform(manifest, package_type)

eXeTransformHandler = eXeTransform()

#Currently not supported
class MITTransform:
    """ Transform MIT content. """

    def __init__(self):
        self.toc = []
        self.base = ''

    def __call__(self, event):
        if 'MIT OCW' == event.package_type[0]:
            self.toc = []
            self.base = ''
            self.doTransform(event.context, event.manifest, event.package_type, event.xformdata)

    def doTransform(self, context, manifest, package_type, xformdata):
        xformdata['filedata'] = {}
        manifest = self.parseMITManifest(context, manifest, xformdata['filedata'])
        self.setMITPageBody(context, xformdata['filedata'])
        xformdata['manifest'] = context.performTransform(manifest, package_type)

    def setMITPageBody(self, context, fdata):
        """ Set the body text for a file. Strips out MIT header and navigation bar """
        fns = context.source.listFiles()
        for fn in fns:
            import os
            mimetype = mimetypes.guess_type(fn)
            textDoc = ''
            if mimetype:
                if mimetype[0]:
                    textDoc = mimetype[0].split('/')[0]

            if fn[-1] != os.sep and textDoc == 'text':
                data = context.source.readFile(fn)
                from BeautifulSoup import BeautifulSoup
                soup = BeautifulSoup(data)
                
                ftext = ''
                if soup.findAll('div',attrs={'class':'maincontent'}):
                    bc = soup.findAll('div',attrs={'class':'bread-crumb'})
                    if bc:
                        titleTag = bc[0].nextSibling.nextSibling
                        bc[0].extract()
                        if titleTag.name == 'h1':
                            titleTag.extract()
                        ftext = str(soup.findAll('div',attrs={'class':'maincontent'})[0])
                
                if not ftext:
                    tbls = soup('table')
                    for tbl in tbls:
                        if tbl.has_key('summary'):
                            summary = tbl['summary']
                            if summary.find('Main Content Header') > 0:
                                ftext = str(tbl)

                if ftext:
                    fdata[fn] = ftext
            
    def parseMITManifest(self, context, manifest, fdata):
        """ Parses and modifies MITManifest where necessary """
        
        title = ''
        doc = parseDoc(manifest)
        xc = doc.xpathNewContext()
        self.setMITNamespaces(xc)
        self.parseMITResources(context, xc, fdata)

        return doc.serialize()

    def setMITNamespaces(self,xc):
        """ Set the MIT specific namespaces """
        xc.xpathRegisterNs("mitcp","http://www.imsglobal.org/xsd/imscp_v1p1")
        xc.xpathRegisterNs("adlcp","http://www.adlnet.org/xsd/adlcp_rootv1p2")
        xc.xpathRegisterNs("ocw","http://ocw.mit.edu/xmlns/ocw_imscp")
        xc.xpathRegisterNs("lom","http://ocw.mit.edu/xmlns/LOM")

    def parseMITResources(self, context, xc, fdata):
        """ Parse each of the MIT Resource objects """
        resources = xc.xpathEval('/mitcp:manifest/mitcp:resources/mitcp:resource')
        self.base = xc.xpathEval("//@xml:base")[0].getContent()
        for resource in resources:
            xc.setContextNode(resource)
            resid = resource.hasProp('identifier').getContent()
            self.addMITTocEntry(xc,resid)
            self.updateMITMetadata(xc,context,resid)

        self.createMITTocPage(context, "Table of Contents", self.toc,  fdata)

    def updateMITMetadata(self,xc,context,resid):
        """ Updates the MIT Manifest with lom object contained in separate xml files """
        resources = xc.xpathEval("//mitcp:resource[@identifier='" + resid +"']")
        if resources:
            xc.setContextNode(resources[0])
            locations = xc.xpathEval("./mitcp:metadata/adlcp:location")
            if locations:
                location = self.base + locations[0].getContent()
                zf = context.source.readFile(location)

                if zf:
                    zfdoc = parseDoc(zf)
                    zfxc = zfdoc.xpathNewContext()
                    self.setMITNamespaces(zfxc)
                    mdQuery = xc.xpathEval('//mitcp:resource[@identifier="'+resid+'"]/mitcp:metadata')
                    if mdQuery:
                        mdNode = mdQuery[0]
                        lomNode = zfxc.xpathEval('//lom:lom')
                        if lomNode:
                            mdNode.addChild(lomNode[0])
                    
#                    self.setMITKeywords(mdNode,zfxcring"))
#                    self.setMITTerm(xc,self.getMITMetadata(zfxc,"//lom:lifeCycle/lom:version/lom:string"))
#                    self.setMITCreators(mdNode,zfxc,"//[contains(text(),'Author')]/parent::node()/parent::node()/lom:entity"))
#                    self.setMITCreators(mdNode,zfxc)
#                    self.setMITDescription(xc,self.getMITMetadata(zfxc,"//lom:general/lom:description/lom:string"))
                             
    def addMITTocEntry(self,xc,resid):
        """ Add a table of contents entry """
        tocref = ''
        files = xc.xpathEval("./mitcp:file")

        if len(files) == 1:
            thref = xc.xpathEval("./mitcp:file/@href")
            if thref:
                tocref = self.base + thref[0].getContent()
                    
        items = xc.xpathEval('/mitcp:manifest/mitcp:organizations//mitcp:item[@identifierref="' + resid + '"]')

        for item in items:
            xc.setContextNode(item)
            title = self.getMITItemTitle(xc,item,resid)
            # All files that have  ocw:sectionTemplateType are visible
            isvis = xc.xpathEval('@ocw:sectionTemplateType')
            if isvis and tocref:
                if isvis[0].getContent() != '':
                    self.toc.append((tocref,title))
                
    def createMITTocPage(self, context, tabletitle, tocitems, fdata):
        """ Creates the MIT Table of Contents Page """
        if not tocitems:
            tocitems.append(('','Home'))

        ims_util = getUtility(IIMSTransportUtility)
        body = ims_util.tocpage(tabletitle="Table of Contents", tocitems=tocitems)
        fdata['index.html'] = body

    def getMITItemTitle(self,xc,item,id):
        """ Get the title of the item, if there is none, then return the id """
        
        titles = xc.xpathEval("mitcp:title")
        title = ''
        if titles:
            title = titles[0].getContent()
        else:
            title = id

        return title
        
    def getMITMetadata(self, xc, xpathQuery):
        mds = xc.xpathEval(xpathQuery)
        if mds:
            return [md.getContent() for md in mds]
        else:
            return []

MITTransformHandler = MITTransform()

