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
$Id: rdf.py 43824 2007-06-15 17:08:16Z glenfant $
"""

__author__  = ''
__docformat__ = 'restructuredtext'

# Python imports
import re
from xml.sax.saxutils import escape as basic_xml_escape
from xml.sax.handler import ContentHandler
from xml.sax import parseString
from types import StringType, UnicodeType

# Quote strings in rdf 
def xml_quote(text):
    """XML quoting as recommended in http://dublincore.org/documents/dcmes-xml/"""
    
    if text not in (StringType, UnicodeType):
        return text
    return basic_xml_escape(text, {"'": '&apos;', '"': '&quot;'})

# Constants used by RDF writer
RDF_HEADER = """<?xml version="1.0" encoding="%(charset)s"?>"""
RDF_BODY = """<rdf:RDF%(attrs)s>%(items)s</rdf:RDF>"""
RDF_NAMESPACE = '%(id)s="%(value)s"'
RDF_DESCRIPTION = """<rdf:Description rdf:about="%(field_url)s">%(items)s</rdf:Description>"""
RDF_PROP = """<%(id)s>%(value)s</%(id)s>"""

# This class helps you to create easily rdf
class RDFWriter:
    def __init__(self, charset, namespaces, field_url, field_props):
        """Initialize RDF Builder
        
        @param charset: charset of RDF
        @param namespaces: namespaces used in the used in RDF. 
                           List of dict {'id' : ..., 'value', ...}
        @param field_url: field url
        @param field_props: Field properties added in RDF description.
                            List of dict {'id' : ..., 'value', ...}
        """
        
        self.charset = charset
        self.namespaces = namespaces 
        self.field_url = field_url
        self.field_props = field_props

    def getRDF(self):
        """Returns a rdf text rendered from constructor parameters"""
        
        rdf = ''
        
        # Add header
        rdf += RDF_HEADER % {'charset': self.charset,}
        
        # Add namespaces
        namespaces_string = ''
        if self.namespaces:
            namespaces_string = ' %s' % '\n         '.join([RDF_NAMESPACE % {'id': x['id'], 'value': x['value']} for x in self.namespaces])
        
        # Add rdf items
        field_props_string = ''
        if self.field_props:
            field_props_string = '\n    '.join([RDF_PROP % {'id': x['id'], 'value': xml_quote(x['value'])} for x in self.field_props])
            field_props_string = '\n    %s\n  ' % field_props_string
        
        # Add rdf description
        rdf_description = RDF_DESCRIPTION % {'field_url': self.field_url, 'items': field_props_string}
        rdf_description = '\n  %s\n' % rdf_description
        rdf_body = RDF_BODY % {'attrs': namespaces_string, 'items': rdf_description}
        rdf_body = '\n%s' % rdf_body
        rdf += rdf_body
        return rdf

# This class helps you to read easily rdf
FIND_ENCODING = r"<\?xml[^>]+encoding=['\"]([-\w]+)['\"]"
FIND_ENCODING_RE = re.compile(FIND_ENCODING)

class RDFHandler(ContentHandler):
    
    def __init__(self):
        self.info = {}
        self.info['namespaces'] = []
        self.info['field_url'] = ''
        self.info['field_props'] = []
        self.current_node = ''
        self.current_value = ''
    
    def characters(self, content):
        if self.current_node:
            self.current_value += content
            
    def startElement(self, name, attrs):
        if name == 'rdf:RDF':
            # Get namespaces
            self.info['namespaces'] = [{'id': k, 'value': v} for k, v in attrs.items()]
        elif name == 'rdf:Description':
            for k, v in attrs.items():
                if k == 'rdf:about':
                    self.info['field_url'] = v
        else:
            self.current_node = name
            
    def endElement(self, name):
        if name == self.current_node:
            self.info['field_props'].append({'id': self.current_node, 'value': self.current_value})
        
        self.current_node = ''
        self.current_value = ''
                
class RDFReader:
    def __init__(self, rdf_text):
        """Initialize RDF Reader
        
        @param rdf_text: RDF text
        """
        
        self.rdf_text = rdf_text
        
        # Parse rdf
        self.rdf_info = self._parseRDF()
    
    def _parseRDF(self):
        """Parse RDF text"""
        result = {}
        
        # Get encoding
        charset = None
        match = FIND_ENCODING_RE.match(self.rdf_text)
        if match:
            charset = match.group(1)
        result['charset'] = charset
        
        # Parse XML
        handler = RDFHandler()
        parseString(self.rdf_text, handler)
        result.update(handler.info)
        return result
    
    def getRDFInfo(self):
        """Returns all parsed information about RDF"""

        return self.rdf_info
    
    def getCharset(self):
        """Returns charset of RDF"""
        
        return self.rdf_info['charset']
    
    def getNamespaces(self):
        """Returns namespaces used in RDF.
        
        Returns a list of dict {'id' : ..., 'value', ...}"""
        
        return self.rdf_info['namespaces']
        
    def getFieldUrl(self):
        """Returns field url in RDF"""
        
        return self.rdf_info['field_url']
    
    def getFieldProperties(self):
        """Returns namespaces used in RDF
        
        Returns a list of dict {'id' : ..., 'value', ...}"""
        
        return self.rdf_info['field_props']
    
    def getFieldProperty(self, property):
        """Returns namespaces used in RDF
        
        Returns a list of value.
        
        @param property: Id of the property"""
        
        props = self.rdf_info['field_props']
        result = []
        for prop in props:
            if prop['id'] == property:
                result.append(prop['value'])
        return result