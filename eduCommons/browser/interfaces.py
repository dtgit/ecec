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

__author__ = 'David Ray, Jon Thomas, Brent Lambert'
__docformat__ = 'restructuredtext'
__version__ = "$Revision: 1 $"[11:-2]


from zope.publisher.interfaces.browser import IBrowserView
from zope.viewlet.interfaces import IViewletManager
from zope.interface import Interface
from zope import schema
from zope.schema import Iterable

class ITemplateForm(Interface):
    """ Template form. """

    template = schema.Choice(title=u'Template Selector',
                           description=u'Choose a template to apply to your object.',
                           required=True,
                           vocabulary="Template Choices")

class IFeedbackForm(Interface):
    """ Feedback form for end users. """

    name = schema.TextLine(title=u'Name',
                           description=u'Please Provide us with your name so we know who you are.',
                           required=False)

    email = schema.TextLine(title=u'Email',
                            description=u'Please provide us with your email so that we can contact you if necessary.',
                            required=False)

    subject = schema.TextLine(title=u'Subject',
                              description=u'A simple statement indicating the nature of your feedback.',
                              required=False)

    body = schema.Text(title=u'Comments',
                       description=u'Please include any comments you would like us to hear.',
                       required=True)

class IReportContentForm(Interface):
    """ Report Content form for end users. """

    name = schema.TextLine(title=u'Name',
                           description=u'Please provide us with your name so we know who you are.',
                           required=False)

    email = schema.TextLine(title=u'Email',
                            description=u'Please provide us with your email so that we can contact you if necessary.',
                            required=False)

    body = schema.Text(title=u'Comments',
                       description=u'Please provide comments regarding the nature of the inappropriate content.',
                       required=True)



class IAfterTitle(IViewletManager):
    """ Marker interface for after title viewlet manager. """


class IeduCommonsSharingPageRole(Interface):
    """A named utility providing information about roles that are managed
    by the sharing page.
    
    Utility names should correspond to the role name.
    """
    
    title = schema.TextLine(title=u"A friendly name for the role")
    
    required_permission = schema.TextLine(title=u"Permission required to manag this local role",
                                          required=False)
