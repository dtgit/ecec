IMS Transport Tool 
------------------ 
by the `Center for Open Sustainable Learning`_ at Utah State University. 

.. _`Center for Open Sustainable Learning`: http://cosl.usu.edu 

The IMS Transport Tool allows Plone users to upload content in the form of an IMS package.
Although preliminary support is included for popular proprietary
learning management system packages, support for extending this product
to handle the import or export of any IMS package is also included.

What's New
---------- 


Installation 
------------ 

For full installation instructions see the "INSTALL.txt" file.



Features 
-------- 

  * Experimental support for importing MIT CP into Plone.

  * Experimental support for importing Web CT and Blackboard IMS packages into Plone. 
  
  * Uses Zope 3 events. 
  
  * Uses a two stage processing engine, which allows transforms over existing IMS
    package manifests to be rewritten into a common format. 

  * Maps LOM metadata to Dublin Core fields used in Plone objects. 

  * Easily extensible. 

Requires 
-------- 

  * Plone 3.0.0 and greater
  
  * Zope 2.10.4 and greater

  * BeautifulSoup 3.0.4



