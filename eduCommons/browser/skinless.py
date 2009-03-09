

if context.Type() == 'Page':
    title = context.Title()
    content = context.CookedBody(stx_level=2)
elif context.Type() == 'Division':
    title = context.Title()
    content = context.text()
else:
    title = context.portal_ECObjectTool.getFullCourseTitle(context)
    content = context.text()
return title, content
