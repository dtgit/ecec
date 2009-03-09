## -*- coding: utf-8 -*-
## Copyright (C) 2006 Ingeniweb

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
This is copied from ExternalFile to handle storage of data on the fs

File handling routines called from multiple modules are collected
here to avoid duplication.

Author: <a href="mailto:cstrong@arielpartners.com">Craeg Strong</a>
Release: 1.2
$Id: FileUtils.py 47877 2007-08-23 15:42:04Z encolpe $
"""

# Python builtins
import os, os.path, string, types, urllib

def rm_file(path):
    """
    Delete file from a path
    """

    os.remove(path)

def move_file(infile, outfile):
    """
    Move file to another place
    """

    if infile == outfile:
        # SiteStorageStrategy can send equals infile and outfile
        return

    if os.path.exists(outfile) and infile != outfile:
        os.remove(outfile)

    os.rename(infile, outfile)


def copy_file(infile, outfile):
    """

    Read binary data from infile and write it to outfile. infile and
    outfile my be strings, in which case a file with that name is
    opened, or filehandles, in which case they are accessed directly.

    """

    if type(infile) is types.StringType:
        instream = open(infile, 'rb')
        close_in = 1
    else:
        close_in = 0
        instream = infile

    if type(outfile) is types.StringType:
        outstream = open(outfile, 'wb')
        close_out = 1
    else:
        close_out = 0
        outstream = outfile
    try:
        blocksize = 2<<16
        block = instream.read(blocksize)
        outstream.write(block)
        while len(block)==blocksize:
            block = instream.read(blocksize)
            outstream.write(block)
        instream.seek(0)
    finally:
        if close_in: instream.close()
        if close_out: outstream.close()

def create_file(contents_file, target_filepath):
    """
    Creates a physical file on the filesystem at target_filepath.  If
    contents_file is not None, it points to a file whose contents will
    be copied into the target file.  Otherwise, a zero length file
    will be created.  This method will raise an exception if there are
    any problems writing to the target file (or reading
    contents_file).
    """

    if contents_file:
        copy_file(contents_file, target_filepath)
    else:
        touchfile = open(target_filepath, 'wb') # create zero-length file
        touchfile.close()

# EOF FileUtils.py
