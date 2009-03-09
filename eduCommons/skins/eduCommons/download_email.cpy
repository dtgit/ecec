## Controller Python Script "Download Email"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Generate CSV File of Emails 
##

email_file = context.restrictedTraverse('@@search_view').generateEmailList()

return email_file


