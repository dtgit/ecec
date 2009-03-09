
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

__author__  = '''Brent Lambert, David Ray, Jon Thomas'''
__docformat__ = 'plaintext'
__version__   = '$ Revision 0.0 $'[11:-2]

from zope.formlib.form import FormFields, action
from zope.interface import Interface
from zope import schema


from zope.interface import Interface, Attribute
from zope.component import getUtility
from Products.IMSTransport.utilities.interfaces import IIMSTransportUtility
from zope.schema.vocabulary import SimpleVocabulary
from Products.Five.formlib.formbase import EditForm
from zope.schema._bootstrapinterfaces import WrongType
from zope.schema.interfaces import IVocabularyFactory
from zope.schema import TextLine

from Products.CMFDefault.formlib.widgets import ChoiceRadioWidget

from zope.interface import implements
from zope.app.file.file import File
from zope.app.file.interfaces import IFile
from zope.app.form.browser.textwidgets import FileWidget
from Products.IMSTransport.Manifest import ZipfileReader, ZipfileWriter
from zipfile import ZipFile, BadZipfile
from StringIO import StringIO



class ZipFileLine(TextLine):

    def _validate(self, value):
        try:
            ZipFile(StringIO(value))
        except BadZipfile, e:
            raise WrongType(e)

def transportVocabulary(self):

    imstransport_prop = self.context.portal_properties.ims_transport_properties
    import_xforms = imstransport_prop.import_xforms

    items = [('Default','Default'),]
    for xform in import_xforms:
        xform_info = getattr(imstransport_prop,xform)
        id = xform
        title = str(xform_info[0])
        value = (title,id)
        items.append(value) 
        
    return SimpleVocabulary.fromItems(items)

class IImport(Interface):
    """ Import Form """

    filename = ZipFileLine(title=u"IMS File Import",
                           description=u"The name of the ims package on your local machine.",
                           required=True)


    packagetype = schema.Choice(title=u"Package Type",
                                description=u"The type of the ims package being uploaded",
                                required=True,
                                default='Default',
                                vocabulary="imsvocab")

class IExport(Interface):
    """ Export Form """

    filename = TextLine(title=u"IMS File Export",
                           description=u"The name of the zip file where you want to export the ims package.",
                           required=True)


class ImportFormAdapter(object):
    """ Adapter for the import form """

    implements(IImport)

    def __init__(self,context):
        self.context = context

    def get_zipfile_name(self):
        pass

    def set_zipfile_name(self, title):
        pass

    def get_type(self):
        return 'Default'

    def set_type(self):
        pass
    
    filename = property(get_zipfile_name, set_zipfile_name)
    packagetype = property(get_type, set_type)

class ExportFormAdapter(object):
    """ Adapter for the export form """

    implements(IExport)

    def __init__(self,context):
        self.context = context

    def get_zipfile_name(self):
        return self.context.id + '.zip'

    def set_zipfile_name(self, title):
        pass

    filename = property(get_zipfile_name, set_zipfile_name)

class ImportForm(EditForm):
    """ Render the import form  """
    form_fields = FormFields(IImport)
    form_fields['filename'].custom_widget = FileWidget

    form_fields['packagetype'].custom_widget = ChoiceRadioWidget
    label = u'Import Content'
    description = u'Import IMS content package'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.ims_util = getUtility(IIMSTransportUtility)

    @action('Upload')
    def action_import(self, action, data):
        
        filename = self.context.REQUEST['form.filename']
        packagetype = self.context.REQUEST['form.packagetype']

        imsvocab = getUtility(IVocabularyFactory, name='imsvocab')(self.context)
        package_xform = imsvocab.getTermByToken(packagetype).value


        self.ims_util.importZipfile(self.context,filename,package_xform)

        self.request.response.redirect('.')


class ExportForm(EditForm):
    """ Render the export form  """
    form_fields = FormFields(IExport)
    label = u'Export Content'
    description = u'Export IMS content package'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.ims_util = getUtility(IIMSTransportUtility)

    @action('Export')
    def action_export(self, action, data):

        container = self.context
        filename = self.context.REQUEST['form.filename']
        content, fn = self.ims_util.exportZipfile(self.context,filename)

        if content:
            container.REQUEST.RESPONSE.setHeader('content-type', 'application/zip')
            container.REQUEST.RESPONSE.setHeader('content-length', len(content))
            container.REQUEST.RESPONSE.setHeader('Content-Disposition',
                                                 ' attachment; filename=%s' %filename)
            container.REQUEST.RESPONSE.write(str(content))



