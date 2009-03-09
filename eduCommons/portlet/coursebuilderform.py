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

from zope.interface import Interface
from zope.schema import TextLine, Choice, Tuple
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.app.form.base import AddForm
from plone.app.form.validators import null_validator
from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget
from zope.formlib.form import FormFields, action, applyChanges
from zope.app.form.browser import DropdownWidget, FileWidget
from zope.app.form.browser.widget import renderElement
from zope.app.form.interfaces import WidgetInputError
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from Products.IMSTransport.browser.imstransportform import ZipFileLine
from Products.IMSTransport.utilities.interfaces import IIMSTransportUtility
from Products.CMFDefault.formlib.widgets import ChoiceRadioWidget
from zope import schema
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility

def divisionsvocab(context):
    """ Get the list of current divisions and return it as a vocabulary. """
    path = {'query':('/'), }
    brains = context.portal_catalog.searchResults(path=path, Type='Division', sort_on='sortable_title')
    terms = [SimpleTerm(x.getId, title=x.Title) for x in brains]
    return SimpleVocabulary(terms)

def coursetemplatevocab(context):
    """ Get list of course templates and return them as a vocabulary. """
    templates = context.portal_actions.template_buttons
    terms = []
    for x in templates.items():
        # Only get templates related to courses
        if 'object/search_view/isPageInEduCourse' == x[1].available_expr:
            terms.append(SimpleTerm(x[0], title=x[1].title))
    return SimpleVocabulary(terms)


def validate_coursebuilder(form, action, data):
    """ Validate the course builder form. """

    division = form.request.form['form.division']
    newdivision = form.request.form['form.newdivision']
    if not division and not newdivision:
        dw = form.widgets.get('division')
        dw._error = WidgetInputError(form.context.__name__, dw.label, _('Missing division.'))
        return dw._error

    if newdivision:
        brains = form.context.portal_catalog.searchResults(Type='Division')
        if brains:
            if newdivision in [x.Title for x in brains]:
                dw = form.widgets.get('division')
                dw._error = WidgetInputError(form.context.__name__, 
                                             dw.label, 
                                             _('Division with the same title already exists.'))
                return dw._error

    coursename = form.request.form['form.coursename']
    if not coursename:
        cnw = form.widgets.get('coursename')
        cnw._error = WidgetInputError(form.context.__name__, cnw.label, _('Missing course name.'))
        return cnw._error


class MultiPreSelectCheckBoxVocabularyWidget(MultiCheckBoxVocabularyWidget):
    """ A Multi check box widget that pre selects options. """

    def __init__(self, field, request):
        super(MultiPreSelectCheckBoxVocabularyWidget, self).__init__(field, request)
        self.templates = field.value_type.vocabulary.by_value.keys()

    def _getFormValue(self):
        return self.templates


class EitherOrWidget(DropdownWidget):
    """ A widget that allows you to choose from a drop down, or type in an entry. """

    _messageNoValue = _(u'(Choose one)')

    def __init__(self, field, request):
        super(EitherOrWidget, self).__init__(field, field.vocabulary, request)

    def __call__(self):
        value = ''
        contents = []
        have_results = False

        # Render the Drop Down
        contents.append(self._div('formHelp', _(u'Select from below:'))) 
        contents.append(self._div('value', self.renderValue(value)))

        # Render the edit box
        contents.append(self._div('formHelp', _(u'If not found, type in the name below to create a new one:')))
        contents.append(self._div('value', renderElement('input',
                                                         type='text',
                                                         name='form.newdivision',
                                                         id='form.division.textfield')))
                                                      
        contents.append(self._emptyMarker())

        return self._div(self.cssClass, "\n".join(contents))
    

class ICourseBuilderForm(Interface):
    """ Interface for Course Builder Display form """

    division = Choice(title=u'Division',
                      required=False,
                      vocabulary='eduCommons.divisionsvocab')

    coursename = TextLine(title=u'Title')
    
    courseid = TextLine(title=u'Course ID',
                        description=_(u'The course identifier or catalog number.'),
                        required=False)
    
    courseterm = TextLine(title=u'Term',
                          description=_(u'The term the course was taught in.'),
                          required=False)

    templates = Tuple(title=_(u'Templates'),
                      description=_(u'Choose from the following templates:'),
                      required=False,
                      missing_value=tuple(),
                      value_type=Choice(vocabulary='eduCommons.coursetemplatevocab'))


    filename = ZipFileLine(title=u"IMS File Import",
                           description=u"The name of the ims package on your local machine.",
                           required=False)

    packagetype = schema.Choice(title=u"Package Type",
                                description=u"The type of the ims package being uploaded",
                                required=True,
                                default='Default',
                                vocabulary="imsvocab")



class CourseBuilderForm(AddForm):
    """ Adapter to adapt a Portlet renderer to a Page form """

    form_fields = FormFields(ICourseBuilderForm)
    form_fields['division'].custom_widget = EitherOrWidget
    form_fields['templates'].custom_widget = MultiPreSelectCheckBoxVocabularyWidget
    form_fields['filename'].custom_widget = FileWidget
    form_fields['packagetype'].custom_widget = ChoiceRadioWidget


    label = _(u'Build a Course')
    description = _(u'Create a new course using the fields below.')

    def __init__(self, context, request):
        super(CourseBuilderForm, self).__init__(context, request)
        tmps = context.portal_actions.template_buttons
        self.templates = dict([(x[0],x[1].title) for x in tmps.objectItems()])
        self.plone_utils = getToolByName(self.context, 'plone_utils')
        self.ims_util = getUtility(IIMSTransportUtility)

    def createObject(self, parent, objtype, title, templateid, **kw):
        objid = self.plone_utils.normalizeString(title)
        objid = self.context.generateUniqueId(objid)
        objid = parent.invokeFactory(objtype, id=objid, title=title)
        context = getattr(parent, objid)
        template = context.restrictedTraverse('@@' + str(templateid))
        context.edit(title=title,
                     Text=template(context),
                     text=template(context),
                     **kw)
        context._renameAfterCreation()
        if templateid in ['syllabus_view']:
            context.setPresentation(True)
        context.reindexObject()
        return context

    @action(_(u'label_submit', default=u'Submit'), 
            validator=validate_coursebuilder,
            name=u'Submit')
    def action_submit(self, action, data): 
        """ Create a course. """

        # Get existing division, or create a new one
        divname = self.request.form['form.division']
        newdivision = self.request.form['form.newdivision']
        if newdivision:
            portal = self.context.portal_url
            division = self.createObject(portal, 'Division', newdivision, 'division_view')
        else:
            division = None
            path = {'query':('/'), }
            brains = self.context.portal_catalog.searchResults(path=path, id=divname)
            if brains and len(brains) > 0:
                division = brains[0].getObject()

        if not division:
            self.status = _(u'Could not create/find existing division.')
            return

        # Create a new course
        course = self.createObject(division, 
                                   'Course', 
                                   self.request.form['form.coursename'],
                                   'course_view',
                                   courseId=self.request.form['form.courseid'],
                                   term=self.request.form['form.courseterm'])

        if not course:
            self.status = _(u'Could not create course.')
            return

        # Create default templates
        templates = ''
        if self.request.form.has_key('form.templates'):
            templates = self.request.form['form.templates']

        #Determine if a singular or multiple templates are returned
        if type(templates) == type(u''):
            self.createObject(course, 'Document', self.templates[templates], templates)
        elif type(templates) == type([]):            
            for x in self.request.form['form.templates']:
                self.createObject(course, 'Document', self.templates[x], x)

        filename = ''
        packagetype = ''

        if self.request.form.has_key('form.filename'):
            filename = self.request.form['form.filename']

        if self.request.form.has_key('form.packagetype'):
            packagetype = self.request.form['form.packagetype']

            
        if filename != '' and packagetype != '':
            imsvocab = getUtility(IVocabularyFactory, name='imsvocab')(self.context)
            package_xform = imsvocab.getTermByToken(packagetype).value
            self.ims_util.importZipfile(course,filename,package_xform,rtype='eduCommons')            

        # Redirect to the course edit page
        self.request.RESPONSE.redirect(course.absolute_url() + '/edit')

