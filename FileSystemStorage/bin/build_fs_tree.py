# -*- coding: utf-8 -*-
## ProductName
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Export FileSystemStorage tree in a site like tree
"""

__version__ = "$Revision: 1.31 $"
__docformat__ = 'restructuredtext'

# Python imports
import re
import os
import sys
import getopt
from StringIO import StringIO


MAN = """python build_fs_tree.py SOURCE_PATH DEST_PATH LIB_PATH

SOURCE_PATH
    Path where fss and rdf files are stored.

DEST_PATH
    Path where filesystem tree are built.

LIB_PATH
    Path where FileSystemStorage is installed.
"""

def usage():
    print MAN

SEARCH_RDF = r'^(?P<uid>.{32})_(?P<field>[^.]*).rdf$'
SEARCH_RDF_RE = re.compile(SEARCH_RDF)

def build_fs_tree(src_path, dst_path, lib_path):
    """Build FS tree"""

# Rdf imports
    sys.path.append(lib_path)
    from rdf import RDFReader
    from FileUtils import move_file, copy_file

    print "Build filesystem data in %s from %s" % (src_path, dst_path)
    sys_encoding = sys.getfilesystemencoding()
    
    # Store rdf files
    # List of dictionnary {'field': ..., 'uid': ...}
    rdf_files = []
    
    # Walk into filesystem
    for root, dirs, files in os.walk(src_path):
        if root == src_path:
            # Loop on files
            for item in files:
                match = SEARCH_RDF_RE.match(item)
                if match is None:
                    continue
                
                # Get field name and content uid 
                uid = match.group('uid')
                field = match.group('field')
                rdf_files.append({'uid': uid, 'field': field})
    
    # Processing collected rdf files
    print "Processing %s rdf files" % str(len(rdf_files))
    file_paths = []
    for rdf_file in rdf_files:
        uid = rdf_file['uid']
        field = rdf_file['field']
        
        # Get RDF file
        rdf_filename = '%s_%s.rdf' % (uid, field)
        rdf_path = os.path.join(src_path, rdf_filename)
        rdf_file = StringIO()
        rdf_text = ''
        try:
            copy_file(rdf_path, rdf_file)
            rdf_file.seek(0)
            rdf_text = rdf_file.getvalue()
        finally:
            rdf_file.close()
        
        # Read RDF properties
        try:
            rdf_reader = RDFReader(rdf_text)
        except:
            try:
                # XXX known bug to fix
                rdf_text = rdf_text.replace('&', '&amp;')
                rdf_reader = RDFReader(rdf_text)
            except:
                print rdf_path
                print rdf_text
                raise
        field_url = rdf_reader.getFieldUrl()
        field_url = field_url.encode(sys_encoding, 'replace')
        
        # Create tree directories
        content_path_array = field_url.split('/')[:-2]
        content_path = dst_path
        for content_dir in content_path_array:
            content_path = os.path.join(content_path, content_dir)
            if os.path.exists(content_path):
                continue
            print "Create path: %s" % content_path
            os.mkdir(content_path)
        
        # Get source file
        src_filename = '%s_%s' % (uid, field)
        src_file_path = os.path.join(src_path, src_filename)
        
        if not os.path.exists(src_file_path):
            print "Source file doesn't exist, we continue: %s" % src_file_path
            continue

        # Get destination file
        dst_filename = field
        dst_filenames = rdf_reader.getFieldProperty('fss:filename')
        if dst_filenames:
            dst_filename = dst_filenames[0]
            if not dst_filename: 
                dst_filename = field
            else:
                dst_filename = dst_filename.encode(sys_encoding, 'replace')
        dst_file_path = os.path.join(content_path, dst_filename)
        
        # In some cases, you can have a content having 2 fss fields with
        # 2 files with the same name
        orig_dst_filename = dst_filename
        dst_file_path_ok = False
        index = 0
        while not dst_file_path_ok:
            if dst_file_path not in file_paths:
                dst_file_path_ok = True
                file_paths.append(dst_file_path)
            else:  
                index += 1    
                dst_filename = '%s-%s' % (str(index), orig_dst_filename)
                print dst_filename
                dst_file_path = os.path.join(content_path, dst_filename)
        
        print "Create file: %s" % dst_file_path
        copy_file(src_file_path, dst_file_path)
        print "Create RDF file: %s.rdf" % dst_file_path
        copy_file(rdf_path, dst_file_path + '.rdf')
        
    print "Filesystem data built complete"
    
def main():
    """Build FS tree"""
    
    # Parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    
    # Process options
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
    
    # Check args
    if len(args) != 3:
        print "for help use --help"
        usage()
        sys.exit(2)
    
    # Check paths
    src_path = args[0]
    dst_path = args[1]
    lib_path = args[2]
    
    if not os.path.exists(src_path):
        print "source path is not valid: %s" % src_path
        sys.exit(2)
    
    if not os.path.exists(src_path):
        print "destination path is not valid: %s" % dst_path
        sys.exit(2)
    
    if not os.path.exists(lib_path):
        print "lib path is not valid: %s" % lib_path
        sys.exit(2)

    # Process files
    build_fs_tree(src_path, dst_path, lib_path)
    
if __name__ == "__main__":
    main()
