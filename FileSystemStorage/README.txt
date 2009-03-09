#################
FileSystemStorage
#################

By Ingeniweb_.

--------------------------

.. contents:: **Table of contents**

--------------------------


About FileSystemStorage
#######################

FileSystemStorage (FSS) is an Archetypes storage for storing fields
raw values on the file system. This storage is used to avoid
unnecessary growth of the ZODB's FileStorage (Data.fs) when using a
lot of large files.

Please note that FSS is a Plone component for **content types
developers**. Do not expect anything more in your Plone site if you
don't use Plone components that may use FSS, such as AttachmentField_.


Copyright and license
#####################

Copyright (c) 2005 - 2007 Ingeniweb_ SAS

This software is subject to the provisions of the GNU General Public License,
Version 2.0 (GPL).  A copy of the GPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE

See the `LICENSE` file that comes with this product.


Requirements
############

* `Zope 2.7.4+ <http://www.zope.org/>`_
* `Plone 2.0+ <http://plone.org/>`_
* `Archetypes 1.3+ <http://plone.org/products/archetypes>`_ if you run
  Plone 2.0, otherwise use Archetypes that comes with the Plone bundle.
* A Plone component that requires or may use FSS, like
  AttachmentField_. Perhaps your custom Archetypes based content types
  (see `Developer's corner`_).


Migration
#########

From FSS 2.5.x and older
========================

The way we configure the storage and backup paths as well as the
storage strategies **HAVE CHANGED IN DEPTH**. There's no automatic
migration from this version. Please create a configuration file that
clones your old configlet preferences as indicated in `FSS main
configuration`_.

Installation
############

* Put FileSystemStorage product in your zope instance Products directory.
* Remove `configure.zcml` if you're running a Zope version older than
  2.9.6.
* **Read carefully** `Storage strategies`_ and `FSS main
  configuration`_ below and configure your instance in
  `plone-filesystemstorage.conf` accordingly.
* Start your Zope instance
* In ZMI, go into your plone site and install the product using
  portal_quickinstaller
* Optionally, tweak some - self explained - preferences in the
  FileSystemStorage configuration panel of your Plone site.


Storage strategies
##################

A storage strategy defines how field values will be stored in your
files system.


Strategies overview
===================

FSS comes with 4 storage strategies. Each strategy requires two directories:

* The storage directory stores the values of relevant fields in files
  according to the selected strategy.
* The backup directory that keeps the values of the fields of deleted
  contents for "Undo" purpose.
* Only one storage strategy can be selected on a given Plone site,
  but different Plone site in the same Zope instance may have distinct
  storage strategies.
* You need the best performances: choose the `Flat storage strategy`_
  or `Directory storage strategy`_.
* You need a storage that looks like your Plone site (in example to
  publish the storage directory in a read only samba share): choose
  the `Site storage strategy 1`_ or the `Site storage strategy 2`_.

See `FSS main configuration`_ to configure the best suited strategy on
your Zope instance and Plone sites.


Flat storage strategy
=====================

All field values are stored in a flat structure. This strategy is the
default one.
        
* Filename of these stored values: `<uid of content>_<field name>`
* Filename of rdf file: `<uid of content>_<field name>.rdf`
* Filename of backup values: `<uid of content>_<field name>.bak`

Rdf files are not backed up. They are automatically generated.

Example of storage::

  fssDirectory
  |
  |- f42ad00adb7d4580f929d734bf1ed3ab_image
  |
  |- f42ad00adb7d4580f929d734bf1ed3ab_image.rdf
  |
  |- f42ad00adb7d4580f929d734bf1ed3ab_file
  |
  |- f42ad00adb7d4580f929d734bf1ed3ab_file.rdf
    
  fssBackupDirectory
  |
  |- 9efeb7638fb35f5f9b9955da3e2dbfec_file.bak


Directory storage strategy
==========================

All field values are stored in a directory structure. Sub directories
are defined on two level. First level of directory uses the 2
characters of content uid.  Second level of directory uses the 4
characters of content uid. Backup files are stored in a flat
structure.

* Filename of these stored values: `<uid of content>_<field name>`
* Filename of rdf file: `<uid of content>_<field name>.rdf`
* Filename of backup values: `<uid of content>_<field name>.bak`

RDF files are not backed up. They are automatically generated
 
Example of storage::

  fssDirectory
  |
  |- f42
     |
     |- f42ad
        |
        |- f42ad00adb7d4580f929d734bf1ed3ab_image
        |
        |- f42ad00adb7d4580f929d734bf1ed3ab_image.rdf
        |
        |- f42ad00adb7d4580f929d734bf1ed3ab_file
        |
        |- f42ad00adb7d4580f929d734bf1ed3ab_file.rdf
    
  fssBackupDirectory
  |
  |- 9efeb7638fb35f5f9b9955da3e2dbfec_file.bak

Depending in one hand on your file system performances facing a huge
amount of files in the same directory, and in the other hand on the
number of contents relying on FSS, you might choose this strategy or
the `Flat storage strategy`_.


Site storage strategy 1
=======================

All field values are stored in a directory structure mirroring
structure of PloneSite.  Backup files are stored in a flat structure.

* Filename of these stored values: Filename of field value or field
  name if not defined
* Filename of rdf file: `<field name>.rdf`
* Filename of backup values: `<uid of content>_<field name>.bak`

Rdf files are not backed up. They are automatically generated

Example of storage::

  fssDirectory
  |
  |- members
     |
     |- john
        |
        |- dummy-document
           |
           |- image
           |  |
           |  |- moutain.jpg
           |  |
           |  |- image.rdf
           |
           |- file
              |
              |- diary.odt
              |
              |- file.rdf
  
  fssBackupDirectory
  |
  |- 9efeb7638fb35f5f9b9955da3e2dbfec_file.bak


Site storage strategy 2
=======================

All field values are stored in a directory structure mirroring
structure of PloneSite. Backup files are stored in a flat structure.

* Filename of these stored values: Filename of field value or field
  name if not defined
* Filename of rdf file: `<field filename>.rdf`
* Filename of backup values: `<uid of content>_<field name>.bak`

Rdf files are not backed up. They are automatically generated

Example of storage::

  fssDirectory
  |
  |- members
     |
     |- john
        |
        |- dummy-document
           |
           |- fss.cfg
           |
           |- moutain.jpg
           |
           |- mountain.jpg.rdf
           |
           |- diary.odt
           |
           |- diary.odt.rdf
  
  fssBackupDirectory
  |
  |- 9efeb7638fb35f5f9b9955da3e2dbfec_file.bak


FSS main configuration
######################

FSS is mainly configured the ZConfig way. At startup, the
configuration file will be searched (in that order) in:

* $INSTANCE_HOME/etc/plone-filesystemstorage.conf
* /path/to/FileSystemStorage/etc/plone-filesystemstorage.conf
* /path/to/FileSystemStorage/etc/plone-filesystemstorage.conf.in

A sample working configuration in provided in this last file. It
assumes you have $INSTANCE_HOME/var/fss_storage and
$INSTANCE_HOME/var/fss_backup directories, both being read/write
enabled to the user that runs the Zope process, unless Zope will raise
an error at startup.

All configuration doc you need is in `plone-filesystemstorage.conf.in`
comments.

Inconsistent configuration features raise explicit error messages at
Zope startup.

Note that we didn't include this in `zope.conf` in order to keep Zope
2.7 and Zope 2.8 compatibility.


Configuration panel
###################

FSS and RDF
===========

As mentioned above in `Storage strategies`_, FSS can optionally store
RDF files in the back-end storage. These RDF files conform the
`DCMES-XML standard`_ on XML expression of DublinCore elements.

If you select the `Flat storage strategy`_, the RDF files may be used
to build a files tree as close as possible of the Plone tree structure
from the storage back-end, with the `build_fs_tree.py` utility::

  $ cd /path/to/FileSystemStorage/bin
  $ python build_fs_tree.py --help


FSS maintenance
===============

The "Maintenance" tab of FSS configuration panel shows some statistics
about the amount of files managed by FSS.

In addition 2 additional buttons are provided:

* **Update FSS files** : Cleans up the back-end storage
  directories. Files not referenced from a content object are removed.

* **Update RDF files** : Builds all RDF files, in the event you chose
  to select the generetion of RDF files after having inserted relevant
  contents.


Zope backups
############

Of course, you need to synch your Data.fs backups with the storage
paths backups, unless you may restore corrupted/incomplete sites.


Caveats and pittfalls
#####################

Note that whatever's the selected strategies, **DO NEVER CHANGE ANY
FILE IN THE STORAGE PATHS UNLESS YOU KNOW WHAT YOU DO**, otherwise
you'll loose your contents, your job, your money, your friends, your
wife/husband and children.

**DO NEVER CHANGE THE STRATEGY FOR A PLONE SITE ONCE THIS SITE HAS
FIELDS STORED IN ITS FSS STORAGE PATH** unless you're loose your
contents, your job, ... FSS has no utility to convert a storage format
to another one. Sponsorship is welcome - as indicated in `Support and
feedback`_ - if you need such a feature.

Thought it is possible to share the same storage path and backup path
within various Plone sites, since you don't mind of your data in
development sites, you should really configure FSS such each Plone
site has its own private storage path and backup path. In cas you
ignore this warning, **DO NEVER CLICK ANY BUTTON IN THE MAINTENANCE
TAB OF THE FSS CONFIGURATION PANEL** otherwise you'll loose your
contents, your job, ...

Zexp exports **don't embed the associated FSS storage**. So don't move
your Plone site within Zope instances using zexp exports unless you
move the storage and backup directories along with the zexp file.

After changing your configuration (see `FSS main configuration`_),
always restart your Zope instance in foreground since configuration
errors are not reported when Zope is started as daemon or Windows
service.

Developer's corner
##################

Using FSS in your content types
===============================

We assume that creating AT based content types is a familiar activity.

When creating the schema of a content type, you usually don't mention
the storage of your fields since AT provides a default ZODB
storage. You can choose another storage, either another one that ships
in the Archetypes bundle, or a third party storage like FSS.

Here is a small example that doesn't need much comments::

  # Usual Zope/CMF/Plone/Archetypes imports
  ...
  from Products.FileSystemStorage.FileSystemStorage import FileSystemStorage
  ...
  my_schema = Schema((
      FileField('file',
                ...
                storage=FileSystemStorage(),
                widget=FileWidget(...)
		),
      ...
      ))
   ...

You may have a look at `examples/FSSItem.py` to see a demo content
type using FSS. If you want to play with this content type::

  $ $INSTANCE_HOME/bin/zopectl stop
  $ export FSS_INSTALL_EXAMPLE_TYPES=1
  $ $INSTANCE_HOME/bin/zopectl start


Monkey patching a third party content type
==========================================

This simple example shows how to plug the ATFile standard type from
any custom product. Let's say we're in the `__init__.py` of your
custom product::

  ...
  from Products.FileSystemStorage.FileSystemStorage import FileSystemStorage
  from Products.ATContentTypes import atct
  ...
  field = atct.ATFile.schema['file']
  field.storage = FileSystemStorage()
  field.registerLayer('storage', field.storage)
  ...

Customize RDF info set
======================

You can add data to the RDF info set via a FSS dedicated - and
optional - hook.

Open the FSS configuration panel and give the name of your personal
RDF data script, let's call it `fss_custom_rdf` for this example. This
script will add or change the RDF default data set.


RDF script interface
++++++++++++++++++++

The script may be in any Plone layer like `custom` or any other in the
skins path.

Such script is expected to have 4 parameters:

* `name`: the name of the field
* `instance`: the content object being processed
* `properties`: FSS field properties mapping, depending on the type of
  field associated to FSS storage.
* `default_rdf`: a mapping structure of the RDF data, including the
  namespaces, and the elements.

Such script is expected to return an updated `default_rdf` mapping
structure.

Please read the source of classes `FSSInfo`, `FSSFileInfo` and
`FSSImageInfo` from module `FileSystemStorage.py`, `RDFWriter` from
module `rdf.py` for detailed information on formats of expected data.


Simple example
++++++++++++++

We need to add the date of RDF file generation in an element like
this::

  <fss:rdf_date>2007-05-13 13:21:00</fss:rdf_date>  

Here's the script::

    ## Script (Python) "fss_custom_rdf"
    ##bind container=container
    ##bind context=context
    ##bind namespace=
    ##bind script=script
    ##bind subpath=traverse_subpath
    ##parameters=name, instance, properties, default_rdf
    ##title=
    ##
    """We add the date of RDF file generation"""
    
    rdf_args = default_rdf.copy()
    
    # Add the date of RDF generation
    new_props = []
    new_props.extend(rdf_args['field_props'])
    new_props.append({'id': 'fss:rdf_date', 'value': DateTime().ISO()})
    rdf_args['field_props'] = new_props
    
    return rdf_args


More complex example
++++++++++++++++++++

In this more complex (and stupid - don't do this ;) example, we remove
the elements from `fss` namespace and simulate the standard behaviour
for other elements (`dc` and `rdf` elements).

Here's the code::

    ## Script (Python) "fss_custom_rdf"
    ##bind container=container
    ##bind context=context
    ##bind namespace=
    ##bind script=script
    ##bind subpath=traverse_subpath
    ##parameters=name, instance, properties, default_rdf
    ##title=
    ##
    from Products.CMFCore.utils import getToolByName
    
    rdf_args = {}
    
    # Set RDF charset
    ptool = getToolByName(instance, 'portal_properties')
    rdf_args['charset'] = ptool.site_properties.default_charset
    
    # Set RDF namespaces
    rdf_args['namespaces'] = (
        {'id': 'xmlns:rdf', 'value': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'},
        {'id': 'xmlns:dc', 'value': 'http://purl.org/dc/elements/1.1/'},
        {'id': 'xmlns:fss', 'value': 'http://namespace.ingeniweb.com/fss'},) 
    
    # Set field url
    utool = getToolByName(instance, 'portal_url')
    portal_path = utool.getPortalObject().getPhysicalPath()
    portal_path_len = len(portal_path)
    rel_path = '/'.join(instance.getPhysicalPath()[portal_path_len:])
    fss_path = '%s/fss_get/%s' % (rel_path, name)
    rdf_args['field_url'] = fss_path
    
    # Set RDF properties
    props = (
       {'id': 'dc:title', 'value': instance.title_or_id()},
       {'id': 'dc:description', 'value': instance.Description()},
       {'id': 'dc:language', 'value': instance.Language()},
       {'id': 'dc:creator', 'value': instance.Creator()},
       {'id': 'dc:date', 'value': instance.modified()},
       {'id': 'dc:format', 'value': properties.get('mimetype', 'text/plain')},
       )
    rdf_args['field_props'] = props
    
    # Returns the RDF structure
    return rdf_args


Recommanded practices on custom RDF
+++++++++++++++++++++++++++++++++++

Do not change the existing elements under `fss` namespace unless the
`bin/build_fs_tree.py` utility won't work. In other terms, do not use
the script of the `More complex example`_.

Adding or changing elements to the `dc` and `rdf` namespaces may screw up
external utilities based on canonical `DCMES-XML standard`_.

Consider adding your own namespace for your custom extra elements.


Testing
#######

Please read `./tests/README.txt`.


Other documentation
###################

See `FileSystemStorage/doc`. 


Downloads
#########

You may find newer stable versions of FSS and pointers to related
informations (tracker, doc, ...) from
http://plone.org/products/filesystemstorage


Subversion repository
#####################

Stay in tune with the freshest (maybe unstable) versions or participate to
the FileSystemStorage evolutions:

https://svn.plone.org/svn/collective/FileSystemStorage


Support and feedback
####################

Please read all the documentation that comes with this product before
asking for support, unless you might get a RTFM reply ;)

Localisation issues - other than french - should be reported to the
relevant translators (see Credits_ below).

Report bugs using the tracker (the `Tracker` link from
http://plone.org/products/filesystemstorage). Please provide in your
bug report:

* Your configuration (Operating system+Zope+Plone+Products/versions).
* The storage strategy in use.
* The full traceback if available.
* One or more scenario that triggers the bug.

Note that we do not support bug reports on Subversion trunk or
branches checkouts.

`Mail to Ingeniweb support <mailto:support@ingeniweb.com>`_ in English or
French to ask for specific support.

`Donations are welcome for new features requests
<http://sourceforge.net/project/project_donations.php?group_id=74634>`_


Credits
#######

* Main developer: `Cyrille Lebeaupin <mailto:cyrille.lebeaupin@ingeniweb.com>`_
* ZConfig support: `Gilles Lenfant <mailto:gilles.lenfant@ingeniweb.com>`_
* Czeck (cs) translation: `Radim Novotny <novotny.radim@gmail.com>`_

--------------------------

.. sectnum::
.. _Ingeniweb: http://www.ingeniweb.com/
.. _AttachmentField: http://plone.org/products/attachmentfield
.. _DCMES-XML standard: http://dublincore.org/documents/dcmes-xml/
.. $Id: README.txt 51757 2007-10-15 15:01:00Z glenfant $
