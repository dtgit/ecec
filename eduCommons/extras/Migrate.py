from Products.CMFPlone.utils import _createObjectByType
from StringIO import StringIO
from zope.component import getUtility, getMultiAdapter
from Products.CMFPlone.factory import addPloneSite
from Products.CMFCore.utils import getToolByName
from Products.eduCommons import portlet
from Products.eduCommons.setupHandlers import setupTransforms, setupKupu, publishObject
from Products.eduCommons.browser.packagecourseview import appendObjPosition
from Products.IMSTransport.utilities.interfaces import IIMSTransportUtility
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping

def migrate_2_3_1_to_3_0_4(self):
    out = StringIO()
    print >> out, '<h3>Starting Migration</h3>\n'
    print >> out, '<ul>\n'

    oldsite = self.eduCommons

    # If we have a previous attempt, erase it
    if getattr(self, 'mig_ec', None):
        self.manage_delObjects(['mig_ec'])

    # Create a new plone site
    addPloneSite(self, 
                 'mig_ec', 
                 extension_ids = ('Products.ContentLicensing:default',
                                  'Products.IMSTransport:default',
                                  'Products.PloneBookmarklets:default',
                                  'Products.ZipFileTransport:default',
                                  'Products.eduCommons:default',
                                  'Products.leftskin:default',
                                  ))

    newsite = self.mig_ec
    print >> out, '  <li>New eduCommons site Created</li>\n'

    # Copy MailHost Settings
    newsite.MailHost = oldsite.MailHost

    # Copy about folder contents

    newsite.about.manage_delObjects(['abouttext_text',
                                     'terms-of-use',
                                     'privacy-policy'])
    objs = oldsite.about.manage_copyObjects(oldsite.about.objectIds())
    newsite.about.manage_pasteObjects(objs)
    newsite.about.manage_renameObjects(['copy_of_index_html'], ['abouttext_text'])
    setWorkflow(self, newsite.about, oldsite.about, {'index_html':'abouttext_text'}, False)
    print >> out, '  <li>Migrated the About folder</li>\n'
    
    # Copy Help folder contents

    newsite.help.manage_delObjects(['help_text'])
    objs = oldsite.help.manage_copyObjects(oldsite.help.objectIds())
    newsite.help.manage_pasteObjects(objs)
    newsite.help.manage_renameObjects(['copy_of_index_html'], ['help_text'])
    setWorkflow(self, newsite.help, oldsite.help, {'index_html':'help_text'}, False)
    print >> out, '  <li>Migrated the Help folder</li>\n'

    # Copy the old feedback contents

    objs = oldsite.feedback.manage_copyObjects(oldsite.feedback.objectIds())
    newsite.feedback.manage_pasteObjects(objs)
    newsite.feedback.manage_renameObjects(['copy_of_index_html'], ['feedback'])
    setWorkflow(self, newsite.feedback, oldsite.feedback, {'index_html':'feedback'}, False)
    print >> out, '  <li>Migrated the Feedback folder</li>\n'

    # Migrate other top level content

    objs = oldsite.portal_catalog.searchResults(portal_type=['File', 'Image', 'Document'],
                                                path={'query':'/',
                                                      'depth':2,})
    newsite.manage_delObjects(['front-page'])
    obj_ids = [x.id for x in objs]
    co = oldsite.manage_copyObjects(obj_ids)
    newsite.manage_pasteObjects(co)
    for x in obj_ids:
        obj = getattr(oldsite, x)
        newobj = getattr(newsite, x)
        if x != 'front-page':
            newobj.setExcludeFromNav(True)
        if obj.__annotations__.has_key('review_state'):
            moveWorkflow(self, newobj, obj.__annotations__['review_state'])

    # Copy OCW content

    depts = oldsite.portal_catalog.searchResults(Type='Folder', 
                                                 path={'query':'/',
                                                       'depth':2,})
    print >> out, '  <li>Migrating Divisions</li>\n'
    print >> out, '  <ul>\n'

    for dept in depts:
        obj = dept.getObject()
        if obj.__annotations__.has_key('dept.text'):
            migrateDivision(self, newsite, obj)
            print >> out, '    <li>Migrated %s</li>\n' %obj.Title()
        elif dept.id not in ['help', 'about', 'feedback']:
            co = oldsite.manage_copyObjects(obj.id)
            newsite.manage_pasteObjects(co)
            setWorkflow(self, getattr(newsite, obj.id), obj)
            
    print >> out, '  </ul>\n'

    print >> out, '  <li>Migrated Content</li>\n'



    # Migrate Theme
    if getattr(oldsite.portal_skins.custom, 'base_properties', None):
        oldprops = oldsite.portal_skins.custom.base_properties
        newprops = newsite.portal_skins.custom.base_properties

        ns = newsite.portal_skins
        os = oldsite.portal_skins

        copyProperty(os, ns, 'logoName', 'logoName', True)
        copyProperty(os, ns, 'headerColor', 'portalHeaderBackgroundColor')
        copyProperty(os, ns, 'bannerImage', 'portalHeaderBackgroundImage', True)
        copyProperty(os, ns, 'topNavBackground', 'portalTopNavBackgroundColor')
        copyProperty(os, ns, 'topNavBarBgImage', 'portalTopNavBackgroundImage', True)
        #copyProperty(os, ns, 'leftNavColor', 'portalColumnOneBackgroundColor') 
        copyProperty(os, ns, 'leftBgName', 'portalColumnOneBackgroundImage', True)
        copyProperty(os, ns, 'favicon', 'faviconName', True)
                                         
    print >> out, '  <li>Migrated theme</li>\n'

    # Properties
    #Migrate ContentLicensing Propertiese
    old_cl_props = oldsite.portal_properties.contentlicensing_properties
    new_cl_props = newsite.portal_properties.content_licensing_properties
    for prop in old_cl_props.propertyMap():
        #Overwrite default new values with default old values
        if prop['id'] in new_cl_props.propertyIds():
            id = prop['id']
            if id != 'Jurisdiction':
                key_value = {id : old_cl_props.getProperty(id) }
                new_cl_props.manage_changeProperties(**key_value)
            else:
                for value in new_cl_props.jurisdiction_options:
                    if old_cl_props.getProperty(id) in value:
                        new_cl_props.manage_changeProperties(Jurisdiction=value)
        #Add properties if they don't exist in new
        else:
            id = prop['id']
            type = prop['type']
            value = old_cl_props.getProperty(id)
            new_cl_props.manage_addProperty(id=id, type=type, value=value)
            
    print >> out, '  <li>Migrated ContentLicensing Properties</li>\n'

    #Migrate IMSTransport Properties
    old_ims_props = oldsite.portal_properties.ims_properties
    new_ims_props = newsite.portal_properties.ims_transport_properties
    for prop in old_ims_props.propertyMap():
        #Overwrite default new values with default old values
        if prop['id'] in new_ims_props.propertyIds():
            id = prop['id']
            key_value = {id : old_ims_props.getProperty(id) }
            new_ims_props.manage_changeProperties(**key_value)
        #Add if doesn't exist in new (different engines)
        else:
            id = prop['id']
            type = prop['type']
            value = old_ims_props.getProperty(id)
            new_ims_props.manage_addProperty(id=id, type=type, value=value)
            

    print >> out, '  <li>Migrated IMSTransport Properties</li>\n'

    #Migrate relevant old site properties
    old_site_props = oldsite.portal_properties.migrateable_properties
    newsite.manage_changeProperties(title=old_site_props.site_title,
                                    description=old_site_props.description,
                                    email_from_address=old_site_props.email_from_address,
                                    email_from_name=old_site_props.email_from_name
                                    )
    ec_props = newsite.portal_properties.educommons_properties
    ec_props.manage_changeProperties(division_descriptor=old_site_props.division_descriptor,
                                     course_descriptor=old_site_props.course_descriptor
                                     )
  
    print >> out, '  <li>Migrated Site properties</li>\n'

    #Migrate Users
    old_users = oldsite.acl_users.manage_copyObjects(['local_roles', 
                                                      'mutable_properties', 
                                                      'portal_role_manager',
                                                      'source_groups', 
                                                      'source_users'])
    newsite.acl_users.manage_delObjects(['local_roles', 
                                         'mutable_properties', 
                                         'portal_role_manager',
                                         'source_groups', 
                                         'source_users'])
    newsite.acl_users.manage_pasteObjects(old_users)

    #Activate plugins for each copied object
    acl_users = newsite.acl_users
    acl_users.local_roles.manage_activateInterfaces(['ILocalRolesPlugin',
                                                     'IRolesPlugin'])
    acl_users.mutable_properties.manage_activateInterfaces(['IPropertiesPlugin',
                                                            'IUserEnumerationPlugin'])
    acl_users.portal_role_manager.manage_activateInterfaces(['IRoleAssignerPlugin',
                                                             'IRoleEnumerationPlugin',
                                                             'IRolesPlugin'])
    acl_users.source_groups.manage_activateInterfaces(['IGroupEnumerationPlugin',
                                                       'IGroupIntrospection',
                                                       'IGroupManagement',
                                                       'IGroupsPlugin'])
    acl_users.source_users.manage_activateInterfaces(['IAuthenticationPlugin', 
                                                      'IUserAdderPlugin', 
                                                      'IUserEnumerationPlugin', 
                                                      'IUserIntrospection', 
                                                      'IUserManagement'])

    old_pgd = oldsite.portal_groupdata
    newsite.portal_groupdata = old_pgd

    old_pmd = oldsite.portal_memberdata
    newsite.portal_memberdata = old_pmd

    #Set all users default editor to Kupu
    users = newsite.acl_users.getUsers()
    for user in users:
        user.setProperties(wysiwyg_editor = 'Kupu')

    print >> out, '  <li>Migrated Users</li>\n'

    # Move new site into place

    self.manage_delObjects(oldsite.getId())
    self.manage_renameObject(newsite.getId(), 'eduCommons', REQUEST=None)


    print >> out, '</ul>\n'
    print >> out, 'Done.\n'
    return out.getvalue()



def copyProperty(src, dest, srcprop, destprop, doImage=False):
    prop = src.custom.base_properties.getProperty(srcprop)
    if prop:
        if not doImage:
            dest.custom.base_properties.manage_changeProperties(**{destprop:prop})
            return True
        elif getattr(src.custom, prop, None):
            dest.custom.base_properties.manage_changeProperties(**{destprop:prop})
            try:
                co = src.custom.manage_copyObjects([prop])
            except AttributeError:
                pass
            else:
                dest.custom.manage_pasteObjects(co)
            return True
    return False
    

def migrateDivision(self, newsite, dobj):
    """ Migrate a division from the old site to the new. """
    # Create a new division
    _createObjectByType('Division',
                        newsite,
                        id=dobj.getId(),
                        title=dobj.Title(),
                        description=dobj.Description(),
                        subject=dobj.Subject(),
                        contributors=dobj.Contributors(),
                        creators=dobj.Creators(),
                        language=dobj.Language(),
                        rights=dobj.Rights(),
                        creation_date=dobj.CreationDate(),
                        )
    # Copy over remaining division attributes
    div = getattr(newsite, dobj.getId())
    div.setText(dobj.__annotations__['dept.text'])
    #div.syndication_information = dobj.syndication_information
    for x in dobj.__annotations__.keys():
        if 'review_state' == x:
            moveWorkflow(self, div, dobj.__annotations__[x])
        if x != 'dept.text':
            div.__annotations__[x] = dobj.__annotations__[x]

    # Copy Course sub objects
    oc = []
    for oid,obj in dobj.objectItems():
        if 'Folder' == obj.Type():
            ann = getattr(obj, '__annotations__', None)
            if ann and ann.has_key('course.text'):
                migrateCourse(self, div, obj)
            elif oid != 'syndication_information':
                oc.append(oid)
        else:
            oc.append(oid)

    # Copy all other sub objects
    co = dobj.manage_copyObjects(oc)
    div.manage_pasteObjects(co)

    for oid,obj in div.objectItems():
        if 'Course' != obj.Type() and 'syndication_information' != oid:
            moveWorkflow(self, obj, getattr(dobj, oid).__annotations__['review_state'])
            obj.workflow_history = getattr(dobj, oid).workflow_history

def migrateCourse(self, div, cobj):
    """ Migrate a course from the old site to the new. """
    
    # Create a new course
    _createObjectByType('Course',
                        div,
                        id=cobj.getId(),
                        title=cobj.Title(),
                        description=cobj.Description(),
                        subject=cobj.Subject(),
                        contributors=cobj.Contributors(),
                        creators=cobj.Creators(),
                        language=cobj.Language(),
                        rights=cobj.Rights(),
                        creation_date=cobj.CreationDate(),
                        )
    
    # Copy over remaining course attributes
    course = getattr(div, cobj.getId())
    course.setText(cobj.__annotations__['course.text'])
    #course.syndication_information = cobj.syndication_information
    a2f = {'course.term':'term',
           'course.courseid':'courseId',
           'course.instructorname':'instructorName',
           'course.instructor_principal':'instructorAsCreator',
           'course.instructoremail':'instructorEmail',
           'course.displayInstructorEmail':'displayInstEmail'}
    for x in cobj.__annotations__:
        if x in a2f:
            mut = course.getField(a2f[x]).getMutator(course)
            mut(cobj.__annotations__[x])
        elif 'review_state' == x:
            moveWorkflow(self, course, cobj.__annotations__[x])
        else:
            course.__annotations__[x] = cobj.__annotations__[x]
                
    # Copy Course Objects
    ids = cobj.objectIds()    

    if '.LogFiles' in ids:
        ids.remove('.LogFiles')

    if 'syndication_information' in ids:
        ids.remove('syndication_information')

    co = cobj.manage_copyObjects(ids)

    course.manage_pasteObjects(co)
    #ensure each object has correct position in course
    for oid in ids:
        olditem = getattr(cobj, oid)
        if olditem.__annotations__.has_key('eduCommons.objPositionInCourse'):
            pos = olditem.__annotations__['eduCommons.objPositionInCourse']

            newitem = getattr(course, oid)
            newitem.__annotations__['eduCommons.objPositionInCourse'] = pos

    setWorkflow(self, course, cobj)


def setWorkflow(self, new, old, omappings={}, retainHistory=True):
    for oldid,olditem in old.objectItems():
        if oldid in omappings:
            oldid = omappings[oldid]
        if oldid != '.LogFiles':
            newitem = getattr(new.aq_explicit, oldid)
            try:
                if olditem.__annotations__.has_key('review_state'):
                    moveWorkflow(self, newitem, olditem.__annotations__['review_state'])
                    if retainHistory:
                        newitem.workflow_history = olditem.workflow_history
                    if 'Folder' == olditem.Type():
                        setWorkflow(self, newitem, olditem)
            except AttributeError:
                pass

        
def moveWorkflow(self, newobj, ostate):
    wt = newobj.portal_workflow
    nstate = wt.getInfoFor(newobj, 'review_state')
    result = False
    if 'Visible' == ostate:
        ostate = 'Published'
    if nstate == ostate:
        result = True
    elif 'InProgress' == nstate:
        wt.doActionFor(newobj, 'submit', comment='', include_subfolders=False)
        result = moveWorkflow(self, newobj, ostate)
    elif 'QA' == nstate:
        wt.doActionFor(newobj, 'release', comment='', include_subfolders=False)
        result = moveWorkflow(self, newobj, ostate)
    elif 'Released' == nstate:
        wt.doActionFor(newobj, 'publish', comment='', include_subfolders=False)
        result = moveWorkflow(self, newobj, ostate)
    elif 'Published' == nstate:
        result = True
    return result
                    
                                
                               
            
