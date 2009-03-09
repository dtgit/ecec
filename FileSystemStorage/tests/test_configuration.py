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
Testing configuration schema and default configuration file
$Id: test_configuration.py 52733 2007-10-30 21:59:03Z encolpe $
"""

__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

import unittest
from Testing.ZopeTestCase import ZopeTestCase
import os
from StringIO import StringIO
import ZConfig

from Products.FileSystemStorage.configuration import datatypes

# Test configurations
GOOD_CONFIG1 = """# Two distinct directories
storage-path $$INSTANCE_HOME/var
backup-path $$INSTANCE_HOME/etc
storage-strategy directory
"""

GOOD_CONFIG2 = """# Two distinct directories, two plone sites
storage-path $$INSTANCE_HOME/var/fss_storage
backup-path $$INSTANCE_HOME/var/fss_backup
# default storage-strategy (flat)
<site /foo/bar>
  storage-path $$INSTANCE_HOME/bin
  backup-path $$INSTANCE_HOME/log
  storage-strategy directory
</site>
<site /YO/stuff>
  storage-path $$INSTANCE_HOME/etc
  backup-path $$INSTANCE_HOME/Products
  # default storage-strategy (flat)
</site>
"""

GOOD_CONFIG3 = """# Empty config file ;-)
# Assumes that $INSTANCE/var/fss_storage and $INSTANCE/var/fss_backup
"""

_good_configs = (GOOD_CONFIG1, GOOD_CONFIG2, GOOD_CONFIG3)

BAD_CONFIG1 = """# Non existing storage directory
storage-path /foo/bar
"""

BAD_CONFIG2 = """# No write access to storage directory (Unix)
storage-path /etc
"""

BAD_CONFIG3 = """# Duplicated directories
storage-path $$INSTANCE_HOME/var/fss_storage
backup-path $$INSTANCE_HOME/var/fss_storage
"""

BAD_CONFIG4 = """# No such strategy
storage-strategy foo
"""

_bad_configs = (BAD_CONFIG1, BAD_CONFIG2, BAD_CONFIG3, BAD_CONFIG4)


class ConfigSchemaTest(unittest.TestCase):
    """Testing configuration schema conformance"""


    def testSchemaConformance(self):
        """Our schema.xml conforms ZConfig schema"""

        from Products.FileSystemStorage.configuration import schema
        self.schema = schema.fssSchema
        # self.schema = ZConfig.loadSchema(self.schema_path)
        return


class BaseConfigTest(unittest.TestCase):
    """Common resources for testing FSS configuration"""

    def setUp(self):

        from Products.FileSystemStorage.configuration import schema
        self.schema = schema.fssSchema
        return


class ConfigFilesValidityTest(BaseConfigTest):
    """Testing some configuration files"""


    def testGoodConfigLoad(self):
        """A bunch of correct configuration files"""

        global _good_configs
        for config in _good_configs:
            good_config = StringIO(config)
            conf, handler = ZConfig.loadConfigFile(self.schema, good_config)
            datatypes._paths = []
        return

    def testBadConfigLoad(self):
        """A bunch of incorrect configuration files"""

        global _bad_configs
        for config in _bad_configs:
            bad_config = StringIO(config)
            self.failUnlessRaises(Exception, ZConfig.loadConfigFile, self.schema, bad_config)
            datatypes._paths = []
        return

class ConfigObjectTest(BaseConfigTest):
    """Testing configuration classes"""

    def setUp(self):

        super(ConfigObjectTest, self).setUp()
        self.zconf, handler = ZConfig.loadConfigFile(self.schema, StringIO(GOOD_CONFIG2))
        datatypes._paths = []
        return

    def testGlobalAttrs(self):
        """Attributes of global config"""

        self.assertEqual(self.zconf.storage_path, os.path.expandvars('$INSTANCE_HOME/var/fss_storage'))
        self.assertEqual(self.zconf.backup_path, os.path.expandvars('$INSTANCE_HOME/var/fss_backup'))
        self.assertEqual(self.zconf.storage_strategy, 'flat')
        self.assertEqual(len(self.zconf.sites), 2)
        return

    def testSitesAttrs(self):
        """Attributes of site specific settings"""

        expected = {'storage_path': os.path.expandvars('$INSTANCE_HOME/bin'),
                    'backup_path': os.path.expandvars('$INSTANCE_HOME/log'),
                    'storage_strategy': 'directory',
                    'name': '/foo/bar'}
        self._testSiteAttrs(self.zconf.sites[0], expected)

        expected = {'storage_path': os.path.expandvars('$INSTANCE_HOME/etc'),
                    'backup_path': os.path.expandvars('$INSTANCE_HOME/Products'),
                    'storage_strategy': 'flat',
                    'name': '/YO/stuff'}
        self._testSiteAttrs(self.zconf.sites[1], expected)
        return

    def _testSiteAttrs(self, siteconf, expected):
        for attrname, value in expected.items():
            if attrname == 'name':
                self.assertEqual(getattr(siteconf, attrname), value.lower())
            else:
                self.assertEqual(getattr(siteconf, attrname), value)
        return

    def testConfigServices(self):
        """Canonical config API"""

        # Default config for /any/site
        self.assertEqual(self.zconf.storagePathForSite('/any/site'),
                         os.path.expandvars('$INSTANCE_HOME/var/fss_storage'))
        self.assertEqual(self.zconf.backupPathForSite('/any/site'),
                         os.path.expandvars('$INSTANCE_HOME/var/fss_backup'))
        self.assertEqual(self.zconf.storageStrategyForSite('/any/site'), 'flat')

        # /foo/bar specific config
        self.assertEqual(self.zconf.storagePathForSite('/foo/bar'),
                         os.path.expandvars('$INSTANCE_HOME/bin'))
        self.assertEqual(self.zconf.backupPathForSite('/foo/bar'),
                         os.path.expandvars('$INSTANCE_HOME/log'))
        self.assertEqual(self.zconf.storageStrategyForSite('/foo/bar'), 'directory')

        # /YO/stuff specific config
        self.assertEqual(self.zconf.storagePathForSite('/YO/stuff'),
                         os.path.expandvars('$INSTANCE_HOME/etc'))
        self.assertEqual(self.zconf.backupPathForSite('/YO/stuff'),
                         os.path.expandvars('$INSTANCE_HOME/Products'))
        self.assertEqual(self.zconf.storageStrategyForSite('/YO/stuff'), 'flat')
        return


class DefaultConfigTest(unittest.TestCase):
    """Checking the default configuration file
    (etc/plone-filesystemstorage.conf.in)"""

    def testDefaultConfig(self):
        from Products.FileSystemStorage.config import ZCONFIG

        self.assertEqual(ZCONFIG.storagePathForSite('/any/site'),
                         os.path.normpath(os.path.expandvars('$INSTANCE_HOME/var/fss_storage')))
        self.assertEqual(ZCONFIG.backupPathForSite('/any/site'),
                         os.path.normpath(os.path.expandvars('$INSTANCE_HOME/var/fss_backup')))
        self.assertEqual(ZCONFIG.storageStrategyForSite('/any/site'), 'flat')
        self.assertEqual(len(ZCONFIG.sites), 0)
        return


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ConfigSchemaTest))
    suite.addTest(makeSuite(ConfigFilesValidityTest))
    suite.addTest(makeSuite(ConfigObjectTest))
    suite.addTest(makeSuite(DefaultConfigTest))
    return suite
