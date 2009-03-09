from zope.component import getUtility
from zope.publisher.browser import BrowserView
from Products.eduCommons.utilities.interfaces import IECUtility
from Products.Archetypes.utils import contentDispositionHeader

class SearchView(BrowserView):
    """
    """
    def isInEduContainer(self):
        """ test to see if the object is in a eduCommons container """
        parent = self.findEduParent()
        
        if parent.Type() in ['Course','Division'] and self.context.Type() not in ['Course','Division']:
            return True
        else:
            return False

    def isInEduCourse(self):
        """ tests to see if the object is in a Course """
        parent = self.findEduParent()

        if parent.Type() == 'Course' and self.context.Type() != 'Course':
            return True
        else:
            return False


    def isInEduDept(self):
        """ tests to see if the object is in a Department (but not a course) """
        parent = self.findEduParent()
        
        if parent.Type() == 'Department' and self.context.Type() != 'Department':
            return True
        else:
            return False
        
    def isInEduSite(self):
        """ tests to see if the object is in a Site (but not in a department) """
        parent = self.findEduParent()
        
        if parent.Type() == 'Plone Site' and self.context.Type() != 'Plone Site':
            return True
        else:
            return False

    def isPageInEduContainer(self):
        """ test to see if the page is in a eduCommons container """
        if self.isInEduContainer() and self.context.Type() == 'Page':
            return True
        else:
            return False

    def isPageInEduCourse(self):
        """ tests to see if the page is in a Course """
        if self.isInEduCourse() and self.context.Type() == 'Page':
            return True
        else:
            return False


    def isPageInEduDept(self):
        """ tests to see if the object is in a Department (but not a course) """
        if self.isInEduDept() and self.context.Type() == 'Page':
            return True
        else:
            return False
        
    def isPageInEduSite(self):
        """ tests to see if the page is in a Site (but not in a department) """
        if self.isInEduSite() and self.context.Type() == 'Page':
            return True
        else:
            return False

        
    def findEduParent(self):
        """
        """
        ecutil = getUtility(IECUtility)
        parent = ecutil.FindECParent(self.context)
        
        return parent
       
    def isEduContainer(self): 
        """
	Tests to see if the object is an eduCommons container 
	"""

        if self.context.Type() in ['Course','Division','Course List'] or self.context.id == 'front-page':
            return True
        else:
            return False


    def generateEmailList(self):
        """ returns a CSV file of users' emails"""
        email_list = ''
        pas = self.context.acl_users
        
        users = pas.getUsers()    


        for user in users:
            roles = ''

    
        for portal_role in user.getRoles():
            roles += portal_role + ','
                
            roles = '"%s"' %(roles)                 
        
        email_list += unicode(user.getProperty('fullname'),'UTF-8') + ',' + user.getProperty('email') + ',' + user.getUserName() + ',' + roles + '\n'


        RESPONSE = self.context.REQUEST.RESPONSE
        filename = 'email_list.csv'
        header_value = contentDispositionHeader('attachment', 'UTF-8',filename=filename)
        RESPONSE.setHeader("Content-disposition", header_value)
        return email_list        

