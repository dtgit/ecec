# -*- coding: utf-8 -*-
## Copyright (C) 2007 Ingeniweb

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
Configuration schema resources
$Id: datatypes.py 52733 2007-10-30 21:59:03Z encolpe $
"""

__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

import os
import types
from ZConfig.datatypes import stock_datatypes
from ZConfig.substitution import substitute

def existingStoragePath(value):
    """Validating/converting a storage path
    @param value: a storage path
    @return: valid (translated?) storage path
    """

    return _existingPath(value, 'fss_storage')

def existingBackupPath(value):
    """Validating/converting a backup path
    @param value: a backup path
    @return: valid (translated?) storage path
    """

    return _existingPath(value, 'fss_backup')


# ZConfig.substitution.substitute requires lowercase keys in mapping
_environ = dict([(k.lower(), v) for k, v in os.environ.items()])

# For checking duplicate paths
_paths = []

def _existingPath(value, default):

    global _environ, _paths

    # Getting the real path
    if not value:
        value = os.path.join(os.environ['INSTANCE_HOME'], 'var', default)
    else:
        value = substitute(value, _environ)

    # Check existence through ZConfig datatypes
    existing_directory = stock_datatypes['existing-directory']
    value = existing_directory(value)

    # Read/write enabled ?
    if not os.access(value, os.R_OK | os.W_OK):
        raise ValueError, "Zope process user cannot read+write in %s." % value

    # Must be unique
    if value in _paths:
        raise ValueError, "Path %s is used twice" % value
    _paths.append(value)
    return value


def strategy(value):
    """Validating/converting a storage strategy
    @param value: as sent from ZConfig
    @return: valid strategy name
    """
    
    possible_values = ('flat', 'directory', 'site1', 'site2')
    value = str(value).lower()
    if value not in possible_values:
        raise ValueError("'%s' is not a valid storage strategy" % value)
    return value


class BaseConfig(object):
    """Configuration section
    """

    def __init__(self, section):
        """New (Plone) site config
        @param section: ZConfig.matcher.SectionValue obj
        """

        self._section = section
        self.name = section.getSectionName()
        self._section_attr_names = section.getSectionAttributes()
        return


    def __getattr__(self, attrname):
        """attributes are found in self.section"""
        
        if attrname in self._section_attr_names:
            return getattr(self._section, attrname)
        else:
            raise AttributeError, attrname


class GlobalConfig(BaseConfig):
    """Instance wide zconfig object"""
    
    def storagePathForSite(self, site_or_path):
        """Specific or global storage path
        @param site_or_path: Plone site obje or its path
        @return: storage path
        """

        return self._configForPath(site_or_path).storage_path


    def backupPathForSite(self, site_or_path):
        """Specific or global backup path
        @param site_or_path: Plone site obje or its path
        @return: backup path
        """

        return self._configForPath(site_or_path).backup_path


    def storageStrategyForSite(self, site_or_path):
        """Specific or global storage strategy
        @param site_or_path: Plone site obje or its path
        @return: storage policy
        """

        return self._configForPath(site_or_path).storage_strategy


    def _configForPath(self, site_or_path):
        """A configuration obj suitable to the site or path
        @param site_or_path: Plone site object or path to a Plone site
        This should be a decorator func but we need to run with Python 2.3
        """
        
        if type(site_or_path) is types.StringType:
            path = site_or_path.lower()
        else:
            path = '/'.join(site_or_path.getPhysicalPath()).lower()

        # Accelerator mapping for further calls
        if not hasattr(self, '__path_conf_map__'):
            self.__path_conf_map__ = dict([(site.name, site)
                                           for site in self.sites])

        # Specific config if found or flobal one
        return self.__path_conf_map__.get(path, self)


class SiteConfig(BaseConfig):
    """Site wide zconfig object"""

    # Don't need more than basic stuff
    pass
