## Controller Python Script "navigation_remove"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=paths=[]
##title=Show in Nav

objs = context.getObjectsFromPathList(paths)
nav_action = 'hide'
message=''

for obj in objs:
    message = obj.restrictedTraverse('@@search_view').changeNav(nav_action)


context.plone_utils.addPortalMessage(message)

return state.set(context=context)


