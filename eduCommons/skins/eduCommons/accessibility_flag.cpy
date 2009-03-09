## Controller Python Script "accessibility_flag"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=paths=[],include_children=False, accessibility_action=''
##title=Clear copyright for objects

objs = context.getObjectsFromPathList(paths)

message=''

for obj in objs:
    if obj.isPrincipiaFolderish and include_children:
        message = obj.restrictedTraverse('@@change_accessibility_view').changeAccessibility(accessibility_action)

        subobject_paths = ["%s/%s" % ('/'.join(obj.getPhysicalPath()), id) for id in obj.objectIds()]

        if len(subobject_paths) > 0:
            obj.accessibility_flag(subobject_paths,
                                  include_children=include_children,
                                  accessibility_action=accessibility_action)

    else:
        message = obj.restrictedTraverse('@@change_accessibility_view').changeAccessibility(accessibility_action)


context.plone_utils.addPortalMessage(message)

return state.set(context=context)

