## Controller Python Script "translate_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id=''

REQUEST = context.REQUEST

new_context = context.portal_factory.doCreate(context, id)
new_context.processForm()

portal_status_message = REQUEST.get('portal_status_message', 'Content changes saved.')

# handle navigation for multi-page edit forms
next = not REQUEST.get('form_next',None) is None
previous = not REQUEST.get('form_previous',None) is None
if next or previous:
    fieldset = REQUEST.get('fieldset', None)

    schematas = [s for s in new_context.Schemata().keys() if s != 'metadata']

    if previous:
        schematas.reverse()

    next_schemata = None
    try:
        index = schematas.index(fieldset)
    except ValueError:
        raise 'Non-existing fieldset: %s' % fieldset
    else:
        index += 1
        if index < len(schematas):
            next_schemata = schematas[index]
            return state.set(status='next_schemata', \
                             context=new_context, \
                             fieldset=next_schemata, \
                             portal_status_message=portal_status_message)

    if next_schemata == None:
        raise 'Unable to find next field set after %s' % fieldset

lp_translating_from = REQUEST.get('lp_translating_from')
new_context.getCanonical().setLanguage(lp_translating_from)
lp_translating_to = REQUEST.get('lp_translating_to')
new_context.setLanguage(lp_translating_to)

new_context = new_context.getTranslation(lp_translating_to)

return state.set(status='success',\
                 set_language=lp_translating_to,\
                 context=new_context,\
                 portal_status_message=portal_status_message)
