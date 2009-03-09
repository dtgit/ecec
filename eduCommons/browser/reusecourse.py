import string, xmlrpclib, httplib

from StringIO import StringIO
from base64 import encodestring, decodestring

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.IMSTransport.utilities.interfaces import IIMSTransportUtility
from Products.eduCommons.portlet.coursebuilderform import EitherOrWidget

from plone.app.form.base import AddForm
from zope.app.form.browser import PasswordWidget
from zope.formlib.form import FormFields, action, applyChanges
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema import TextLine, Choice
from zope.component import getUtility
from zope.publisher.browser import BrowserView


class BasicAuthTransport(xmlrpclib.Transport):
    """ taken from http://www.zope.org/Members/Amos/XML-RPC """
    def __init__(self, username=None, password=None, verbose=0):
        self.username=username
        self.password=password
        self.verbose=verbose

    def request(self, host, handler, request_body, verbose=0):
        h = httplib.HTTP(host)
        h.putrequest("POST", handler)
        h.putheader("Host", host)
        h.putheader("User-Agent", self.user_agent)
        h.putheader("Content-Type", "text/xml")
        h.putheader("Content-Length", str(len(request_body)))

        # basic auth
        if self.username is not None and self.password is not None:
            h.putheader("AUTHORIZATION", "Basic %s" % string.replace(
                    encodestring("%s:%s" % (self.username, self.password)),
                    "\012", ""))
        h.endheaders()

        if request_body:
            h.send(request_body)

        errcode, errmsg, headers = h.getreply()

        if errcode != 200:
            raise xmlrpclib.ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )

        return self.parse_response(h.getfile())

class XMLRPC(BrowserView):
    
    def importPackage(self, div_id, div_title, zip_title, zip_file, pkg_type, rtype):
        if hasattr(self.context, div_id):
            div = getattr(self.context, div_id)
        else:
            self.context.invokeFactory('Division', id=div_id, title=div_title)
            div = getattr(self.context, div_id)

        zip_title = self.context.generateUniqueId(zip_title)
        div.invokeFactory('Course', zip_title)
        course = getattr(div, zip_title)

        zip_file = StringIO(decodestring(zip_file))

        ims_util = getUtility(IIMSTransportUtility)
        ims_util.importZipfile(course, zip_file, pkg_type, rtype=rtype)

    def retrieveDivisions(self):
        """ Returns the ID and Title for each Division in the target instance  """
        brains = self.context.portal_catalog.searchResults(Type='Division')
        return [(x.id, x.Title) for x in brains]

        


def remotedivisionsvocab(context):
    """ Get the list of current divisions from OpenOCW and return it as a vocabulary """
    ecprops = context.portal_url.portal_properties.educommons_properties
    remote_url = ecprops.reusecourse_instance
    remote = xmlrpclib.Server(remote_url)
    try:
        terms = remote.retrieveDivisions()
        return SimpleVocabulary([SimpleTerm(x[0], x[1]) for x in terms])
    except xmlrpclib.Fault:
        message = _('The remote site is unavailable of configured incorrectly. Please contact an administrator.')
        url = '%s/folder_contents' % context.absolute_url()
        context.plone_utils.addPortalMessage(message)
        context.request.response.redirect(url)





class ICourseExportForm(Interface):
    """ Interface for Course Export Display form """

    remote_division = Choice(title=u'Division',
                             required=False,
                             vocabulary="eduCommons.remotedivisionsvocab")


    open_ocw_username = TextLine(title=u'OpenOCW User Name',
                                 description=_(u'Your user name on OpenOCW'),
                                 required=True)

    open_ocw_password = TextLine(title=u'OpenOCW User Password',
                                 description=_(u'Your user password on OpenOCW'),
                                 required=True)

    
class CourseExportForm(AddForm):
    """ Renderer for Course Export Form """

    form_fields = FormFields(ICourseExportForm)
    form_fields['remote_division'].custom_widget = EitherOrWidget
    form_fields['open_ocw_password'].custom_widget = PasswordWidget

    label = _(u'Export a Course to OpenOCW')
    description = _(u'Reuse this course on OpenOCW. In order to do so, you must have an account at OpenOCW.org.')

    def __init__(self, context, request):
        super(CourseExportForm, self).__init__(context, request)
        self.plone_utils = getToolByName(self.context, 'plone_utils')

    @action(_(u'label_reuse', default=u'Reuse'), 
            name=u'Reuse')

    def action_submit(self, action, data): 
        """ Reuse a course. """
        ecprops = self.context.portal_url.portal_properties.educommons_properties
        remote_url = ecprops.reusecourse_instance
        rtype = 'eduCommons'

        username = self.request.form['form.open_ocw_username']
        password = self.request.form['form.open_ocw_password']
        div_title = self.request.form['form.remote_division']
        newdivision = self.request.form['form.newdivision']

        remote=xmlrpclib.Server(remote_url,
                           BasicAuthTransport(username, password) )

        course = self.context.getECParent()

        zip_title = '%s.zip' % course.getId()
        zip_file = getattr(course, zip_title).data
        zip_file = encodestring(zip_file)
        pkg_type = 'Default'
        
        if not newdivision:
            remotedivvocab = getUtility(IVocabularyFactory, name='eduCommons.remotedivisionsvocab')(self.context)
            div_id = remotedivvocab.getTermByToken(div_title).value
        else:
            div_id = self.plone_utils.normalizeString(newdivision)
            div_title = newdivision
            

        remote.importPackage(div_id, div_title, zip_title, zip_file, pkg_type, rtype)
 
        del zip_file
        del remote

        # Redirect to the the login page at the remote instance, with the appropriate came_form var
        new_course_url = '%s/login_form' % remote_url
        self.request.RESPONSE.redirect(new_course_url)

