from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from Products.ATContentTypes.migration.walker import CatalogWalker
from Products.ATContentTypes.migration.migrator import CMFFolderMigrator, CMFItemMigrator
from zope.app.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from zope.interface import directlyProvidedBy, directlyProvides
from Products.CMFPlone import transaction

# base class to migrate objects and retain their license annotations
class ObjectMigrator(CMFItemMigrator):
    """Persist annotations to new object"""

    def migrate_annotations(self):
        """Persist annotations"""
        if hasattr(self.old, '__annotations__'):
            annotations = self.old.__annotations__
            self.new.__annotations__ = annotations

    def migrate_clearcopyright(self):
        """Migrate clear copyright status to annotation """
        if hasattr(self.old, 'clearedCopyright'):
            copyright_status = self.old.getClearedCopyright()
            """ Manually append field to default content type  """
            self.new.__annotations__['eduCommons.clearcopyright'] = copyright_status

    def migrate_current_workflow(self):
        """Annotate the current workflow state"""
        wft = self.old.portal_url.portal_workflow
        cur_state = wft.getInfoFor(self.old, 'review_state')
        self.new.__annotations__['review_state'] = cur_state

class eduCommonsFoldersMigrator(CMFFolderMigrator):
    """Persist annotations to new object"""

    def migrate_annotations(self):
        """Persist annotations"""
        if hasattr(self.old, '__annotations__'):
            annotations = self.old.__annotations__
            self.new.__annotations__ = annotations
            
    def migrate_clearcopyright(self):
        """Migrate clear copyright status to annotation """
        if hasattr(self.old, 'clearedCopyright'):
            copyright_status = self.old.getClearedCopyright()
            """ Manually append field to default content type  """
            self.new.__annotations__['eduCommons.clearcopyright'] = copyright_status

    def migrate_current_workflow(self):
        """Annotate the current workflow state"""
        wft = self.old.portal_url.portal_workflow
        cur_state = wft.getInfoFor(self.old, 'review_state')
        self.new.__annotations__['review_state'] = cur_state



class ECCourseMigrator(eduCommonsFoldersMigrator):
    """Base class to migrate to Folder """
    
    def migrate_courseproperties(self):
        """Place course specific fields in an annotation, to be used post-install of 3.0.1 """
        if hasattr(self.old, 'Term'):
            self.new.__annotations__['course.term'] = self.old.Term
        if hasattr(self.old, 'CourseId'):
            self.new.__annotations__['course.courseid'] = self.old.CourseId
        if hasattr(self.old, 'InstructorName'):
            self.new.__annotations__['course.instructorname'] = self.old.InstructorName
        if hasattr(self.old, 'instructorAsPrincipalCreator'):
            self.new.__annotations__['course.instructor_principal'] = self.old.instructorAsPrincipalCreator
        if hasattr(self.old, 'InstructorEmail'):
            self.new.__annotations__['course.instructoremail'] = self.old.InstructorEmail
        if hasattr(self.old, 'displayInstructorEmail'):
            self.new.__annotations__['course.displayInstructorEmail'] = self.old.displayInstructorEmail

        text = self.old.getText()
        self.new.__annotations__['course.text'] = text

        #Remove right_slots portlets
        self.old.manage_delProperties(['right_slots',])


    walkerClass = CatalogWalker
    src_meta_type = 'ECCourse'
    src_portal_type = 'ECCourse'
    dst_meta_type = 'ATFolder'
    dst_portal_type = 'Folder'

class ECDepartmentMigrator(eduCommonsFoldersMigrator):
    """Base class to migrate to Folder """

    def migrate_deptproperties(self):
        """Place course specific fields in an annotation, to be used post-install of 3.0.1 """
        text = self.old.getText()
        self.new.__annotations__['dept.text'] = text


    walkerClass = CatalogWalker
    src_meta_type = 'ECDepartment'
    src_portal_type = 'ECDepartment'
    dst_meta_type = 'ATFolder'
    dst_portal_type = 'Folder'

class ECFolderMigrator(eduCommonsFoldersMigrator):
    """Base class to migrate to Folder """

    walkerClass = CatalogWalker
    src_meta_type = 'ECFolder'
    src_portal_type = 'ECFolder'
    dst_meta_type = 'ATFolder'
    dst_portal_type = 'Folder'

    map = {'getExcludeFromNav' : 'setExcludeFromNav'}



# Object migrators
class GFolderMigrator(CMFFolderMigrator):
    """Base class to migrate to Folder """

    walkerClass = CatalogWalker
    src_meta_type = 'GFolder'
    src_portal_type = 'GFolder'
    dst_meta_type = 'ATFolder'
    dst_portal_type = 'Folder'

    def migrate_current_workflow(self):
        """Annotate the current workflow state"""
        wft = self.old.portal_url.portal_workflow
        cur_state = wft.getInfoFor(self.old, 'review_state')
        self.new.__annotations__['review_state'] = cur_state

    map = {'getExcludeFromNav' : 'setExcludeFromNav'}


class ECDocumentMigrator(ObjectMigrator):
    """Base class to migrate to Document """

    walkerClass = CatalogWalker
    src_meta_type = 'ECDocument'
    src_portal_type = 'ECDocument'
    dst_meta_type = 'ATDocument'
    dst_portal_type = 'Document'
    map = {'getRawText' : 'setText',
           'getExcludeFromNav' : 'setExcludeFromNav'}

class GDocumentMigrator(ObjectMigrator):
    """Base class to migrate to Document """

    walkerClass = CatalogWalker
    src_meta_type = 'GDocument'
    src_portal_type = 'GDocument'
    dst_meta_type = 'ATDocument'
    dst_portal_type = 'Document'
    map = {'getRawText' : 'setText',
           'Format' : 'setFormat',
           'getExcludeFromNav' : 'setExcludeFromNav'}

class ECFileMigrator(ObjectMigrator):
    """Base class to migrate to File """

    walkerClass = CatalogWalker
    src_meta_type = 'ECFile'
    src_portal_type = 'ECFile'
    dst_meta_type = 'ATFile'
    dst_portal_type = 'File'
    map = {'getFile' : 'setFile',
           'getExcludeFromNav' : 'setExcludeFromNav'}

class GFileMigrator(ObjectMigrator):
    """Base class to migrate to File """

    walkerClass = CatalogWalker
    src_meta_type = 'GFile'
    src_portal_type = 'GFile'
    dst_meta_type = 'ATFile'
    dst_portal_type = 'File'
    map = {'getFile' : 'setFile',
           'getExcludeFromNav' : 'setExcludeFromNav'}

class ECImageMigrator(ObjectMigrator):
    """Base class to migrate to default Image """

    walkerClass = CatalogWalker
    src_meta_type = 'ECImage'
    src_portal_type = 'ECImage'
    dst_meta_type = 'ATImage'
    dst_portal_type = 'Image'
    map = {'getImage' : 'setImage',
           'getExcludeFromNav' : 'setExcludeFromNav'}

class GImageMigrator(ObjectMigrator):
    """Base class to migrate to default Image """

    walkerClass = CatalogWalker
    src_meta_type = 'GImage'
    src_portal_type = 'GImage' 
    dst_meta_type = 'ATImage'
    dst_portal_type = 'Image'
    map = {'getImage' : 'setImage',
           'getExcludeFromNav' : 'setExcludeFromNav'}

class ECLinkMigrator(ObjectMigrator):
    """Base class to migrate to default Link"""

    walkerClass = CatalogWalker
    src_meta_type = 'ECLink'
    src_portal_type = 'ECLink'
    dst_meta_type = 'ATLink'
    dst_portal_type = 'Link'
    map = {'getRemoteUrl' : 'setRemoteUrl',
           'getExcludeFromNav' : 'setExcludeFromNav'}

def pre_migrate_2_3_1_to_3_0_4(self):
    """Run the migration"""
     
    out = StringIO()
    print >> out, "Starting migration"
         
    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()


    #create migrateable_properties to migrate old site props
    site_props = portal.portal_properties.site_properties
    portal.portal_properties.addPropertySheet('migrateable_properties', 'Old Site Properties')
    m_props = portal.portal_properties.migrateable_properties
    
    m_props.manage_addProperty(id='site_title', type='string', value=portal.title)
    m_props.manage_addProperty(id='description', type='string', value=portal.description)
    m_props.manage_addProperty(id='email_from_address', type='string', value=portal.email_from_address)
    m_props.manage_addProperty(id='email_from_name', type='string', value=portal.email_from_name)
    m_props.manage_addProperty(id='division_descriptor', type='string', value=site_props.institution_object)
    m_props.manage_addProperty(id='course_descriptor', type='string', value=site_props.institution_sub_object)

    #create ims_properties to migrate out of tool
    portal.portal_properties.addPropertySheet('ims_properties', 'IMS Transport Properties')
    ims_props = portal.portal_properties.ims_properties
    IMStool = portal.portal_IMSTransportTool
    for prop in IMStool.propertyMap():
        if prop['id'] != 'title':
            #make an ims_properties entry
            id = prop['id']
            type = prop['type']        
            value = IMStool.getProperty(id)
            ims_props.manage_addProperty(id=id, type=type, value=value)

    #create contentlicensing_properties to capture tool props that need to migrate
    portal.portal_properties.addPropertySheet('contentlicensing_properties', 'Content Licensing Properties')
    cl_props = portal.portal_properties.contentlicensing_properties
    CLtool = portal.portal_contentlicensing
    for prop in CLtool.propertyMap():
        if prop['id'] != 'title':
            id = prop['id']
            type = prop['type']
            value = CLtool.getProperty(id)
            if id == 'Jurisdiction':
                type = 'string'
            cl_props.manage_addProperty(id=id, type=type, value=value)

    transaction.commit()

    #create annotation for position in course, as one cannot access it properly in the migrators
    brains = portal.portal_catalog.searchResults(portal_type=['ECFolder', 
                                                              'ECImage',
                                                              'ECDocument',
                                                              'ECFile',
                                                              'ECLink'],
                                                 path='/')
    for brain in brains:
        obj = brain.getObject()
        #Only annotate those objects set to show in Navigation
        if obj.getExcludeFromNav() == False: 
            if not hasattr(obj, '__annotations__') and obj.portal_type != 'ECLink':
                annotations = IAnnotations(obj)
                annotations['eduCommons.objPositionInCourse'] = ''            
            if obj.portal_type in ['ECFolder', 'ECImage', 'ECDocument', 'ECFile']:
                pos = obj.getNavPosition()            
                obj.__annotations__['eduCommons.objPositionInCourse'] = pos + 2
            elif obj.portal_type == 'ECLink':
                #Links are not annotatable by default, allow each Link to be annotatable
                directly = directlyProvidedBy(obj)
                directlyProvides(obj, directly + IAttributeAnnotatable)
                annotations = IAnnotations(obj)
                pos = obj.getNavPosition()
                annotations['eduCommons.objPositionInCourse'] = pos + 2

    transaction.commit()

    migrators = ( 
                 GDocumentMigrator, ECDocumentMigrator, 
                 GFileMigrator, ECFileMigrator,
                 GImageMigrator, ECImageMigrator,
                 ECLinkMigrator, ECFolderMigrator,
                 ECDepartmentMigrator, ECCourseMigrator,
                 GFolderMigrator,)

    for migrator in migrators:
        walker = migrator.walkerClass(portal, migrator)
        walker.go(out=out)
        transaction.commit()
        print >> out, walker.getOutput()


    #Refresh catalog indices
    self.portal_catalog.reindexIndex(self.portal_catalog.indexes(),None)

    #remove display_view from front_page
    fp = getattr(self, 'front-page', None)

    if fp:
        fp.manage_delProperties(['layout',])
        print >> out, "Removed layout from front-page"    


    #remove caching policy
    self.caching_policy_manager.removePolicy('ECImageAndECFilePolicy')
    print >> out, "Removed Image and File Caching Policy"

    #uninstall FCKEditor
    if self.portal_quickinstaller.isProductInstalled('FCKeditor'):        
        self.portal_quickinstaller.uninstallProducts(products=['FCKeditor'])
        print >> out, "Uninstalled FCKEditor"
    if not self.portal_quickinstaller.isProductInstalled('Kupu'):
        self.portal_quickinstaller.installProducts(products=['Kupu'])
        self.portal_properties.site_properties.available_editors = ('None', 'Kupu')
        print >> out, "Installed Kupu"
        
    #Rename default objects
    #Need to add Folder back to addable for Plone Site first....
    pt = self.portal_types
    plone_site = pt.getTypeInfo('Plone Site')
    plone_site.allowed_content_types += ('Folder',)
    
    ap = getattr(self, 'About', None)
    if ap:
        ap.setId('about')

    hp = getattr(self, 'Help', None)
    if hp:
        hp.setId('help')

    fp = getattr(self, 'Feedback', None)
    if fp:
        fp.setId('feedback')

    print >> out, "Migration finished"
    return out.getvalue()


