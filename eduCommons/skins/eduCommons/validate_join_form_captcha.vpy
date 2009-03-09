## Script (Python) "validate_join_form_captcha"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=workflow_action='', captcha=''
##title=Validates content publishing
##

from Products.CMFPlone import PloneMessageFactory as _
from collective.captcha.browser.captcha import Captcha

captcha_view = Captcha(context, context.REQUEST)
captcha_valid = captcha_view.verify(captcha)

if not captcha_valid:
    state.setError('captcha', _(u'This field is required, please enter the word below.'), 'captcha_missing')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state

