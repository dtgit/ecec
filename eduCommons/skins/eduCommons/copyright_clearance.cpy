## Controller Python Script "copyright_clear"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=paths=[],include_children=False, copyright_action=''
##title=Clear copyright for objects

objs = context.getObjectsFromPathList(paths)

message=''

for obj in objs:
    if obj.isPrincipiaFolderish and include_children:
        message = obj.restrictedTraverse('@@change_copyright_view').changeCopyright(copyright_action)

        subobject_paths = ["%s/%s" % ('/'.join(obj.getPhysicalPath()), id) for id in obj.objectIds()]

        if len(subobject_paths) > 0:
            obj.copyright_clearance(subobject_paths,
                                  include_children=include_children,
                                  copyright_action=copyright_action)

    else:
        message = obj.restrictedTraverse('@@change_copyright_view').changeCopyright(copyright_action)


context.plone_utils.addPortalMessage(message)

return state.set(context=context)

