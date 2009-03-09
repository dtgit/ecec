"""
$Id: __init__.py,v 1.2 2003/05/09 10:51:01 hazmat Exp $
"""

import ProxyIndex

def initialize(context):

    context.registerClass(
        ProxyIndex.ProxyIndex,
        permission = 'Add Pluggable Index',
        constructors = (ProxyIndex.manage_addProxyIndexForm,
                        ProxyIndex.manage_addProxyIndex,
                        ProxyIndex.getIndexTypes,
                        ),
        icon='www/index.gif',
        visibility=None
        )
    
