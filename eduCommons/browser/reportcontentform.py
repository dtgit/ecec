##################################################################################
#    Copyright (C) 2007 Utah State University, All rights reserved.          
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

__author__ = 'Brent Lambert'
__docformat__ = 'restructuredtext'
__version__ = "$Revision: 1 $"[11:-2]


from zope.formlib.form import FormFields, action
from plone.app.form.base import AddForm
from zope.app.form.interfaces import WidgetInputError
from zope.component import getMultiAdapter
from Products.PageTemplates import PageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from Products.MailHost.MailHost import MailHostError
from Products.statusmessages.interfaces import IStatusMessage
from interfaces import IReportContentForm
from Products.SecureMailHost.mail import Mail


def validate_report(form, action, data):
    """ Validate the from email address, if it exists. """
    errors = form.validate(action, data)
    if errors:
        return errors
    if data.has_key('email') and data['email']:
        email = data['email'].encode('ascii')
        if not form.context.MailHost.validateSingleEmailAddress(email):
            ew = form.widgets.get('email')
            ew._error = WidgetInputError(form.context.__name__, ew.label, _('Invalid email address'))
            return ew._error
    

class ReportContentForm(AddForm):
    """ A form for getting feedback from end users. """

    form_fields = FormFields(IReportContentForm)
    label = u'Report Content'
    description = u'Please complete the following form to send a report to the site administrator.'

    @action(_(u'label_submit', default=u'Submit'), 
            validator=validate_report,
            name=u'Submit')
    def action_submit(self, action, data):
        # Convert post variables into email fields
        message = ''
        mto = self.context.email_from_address
        if data.has_key('email') and data['email']:
            mfrom='%s' %data['email'].encode('ascii')
        else:
            # If no return email is provided, use the TO address.
            # Do this so that the from field will pass validation.
            mfrom = mto
        if data['name'] != None:
            name = data['name']
            message += '%s has reported the following content as inappropriate, please review: \n\n' % name
        else:
            message += 'The following content has been reported as inappropriate, please review: \n\n'
        subject = 'Content Reported as Inappropriate'
        message += '\t %s \n\n' % self.context.absolute_url()
        message += data['body']
        # Post the message
        try:
            self.context.MailHost.secureSend(message, mto=mto, mfrom=mfrom, subject=subject, charset='utf8')
        except MailHostError, e:
            IStatusMessage(self.request).addStatusMessage(_('Report Content request failed.'), type='error')
            url = getMultiAdapter((self.context, self.request), name='absolute_url')()
            self.request.response.redirect(url)
            return ''

        self.request.response.redirect('content_reported')
        return ''
