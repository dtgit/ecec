"""
Purpose:
    A pluggable index which proxies for another index
    and utilizes tales to extract an indexable attribute
    from an object.
    
Author:
    kapil thangavelu <k_vertigo@objectrealms.net>
    Copyright @2003 kapil thangavelu
Date:
    3/4/3
    
License:
    X11, see LICENSE.txt for details

$Id: ProxyIndex.py,v 1.15 2004/08/17 15:01:20 guido Exp $    
"""

import types
from UserDict import UserDict

from AccessControl import ClassSecurityInfo
from Acquisition import Implicit, aq_inner, aq_parent, aq_base
from ComputedAttribute import ComputedAttribute
from ExtensionClass import Base
from Globals import DTMLFile
from Interface.Implements import objectImplements
from Interface import Interface
from OFS.SimpleItem import SimpleItem
from zLOG import LOG, PROBLEM

from Products.PluginIndexes.common.PluggableIndex import PluggableIndexInterface
from Products.ZCatalog.IZCatalog import IZCatalog
from Products.ZCatalog.Catalog import CatalogSearchArgumentsMap
from Expression import Expression, createExprContext

_marker = ()

DEBUG_LOG_ERRORS = 0
PROXIED_INDEX_ID='proxy_value'
PROXY_EXTRA = ('idx_type', 'value_expr', 'idx_context', 'idx_caller')
CMF_FOUND = 0

# used latter when constructing an object wrapper to determine if the
# object is already wrapped.
try:
    from Products.CMFCore.CatalogTool import IndexableObjectWrapper, ICatalogTool
    CMF_FOUND = 1    
except ImportError:
    class ICatalogTool(Interface): pass
    IndexableObjectWrapper = None

class IndexableWrapper:
    def __init__(self, ob):
        self._ob = ob
    def __getattr__(self, name):
        return getattr(self._ob, name)

class RecordStyle(UserDict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, e:
            raise AttributeError, e
    
manage_addProxyIndexForm = DTMLFile('ui/ProxyIndexAddForm', globals())

def manage_addProxyIndex(self, id, extra=None, REQUEST=None, RESPONSE=None, URL3=None, **kw):
    """Add a proxy index"""

    rec = RecordStyle()
    if extra is not None:
        rec.update( extra )
    rec.update( kw )

    # a little bit of foo, so we can have a catalog context during
    # index construction
    rec['idx_context']=self # factory dispatcher context
    
    return self.manage_addIndex(id,
                                'ProxyIndex',
                                extra=rec, 
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)

        
class ProxyIndex(SimpleItem):

    __implements__ = PluggableIndexInterface

    meta_type = 'ProxyIndex'

    manage_options = (
        
        {'label':'Overview',
         'action':'index_overview'},
        
        {'label':'Index',
         'action':'idx/manage_workspace'}
        
        )

    index_overview = DTMLFile('ui/ProxyIndexView', globals())

    security = ClassSecurityInfo()

    def __init__(self, id, extra, caller=None):
        self.id = id

        extra['idx_caller'] = caller # save the caller for lexicon lookup
        idx_type = extra['idx_type']
        value_expr = extra['value_expr']

        self._idx_type = idx_type
        self.idx  = getIndexForType(self, idx_type, extra)
        self._expr = Expression(value_expr)

    def getId(self):
        return self.id

    def clear(self):
        clear = self.getProxyAttribute('clear')
        return clear()

    def getExpressionText(self):
        return self._expr.text

    def getIndexType(self):
        return self._idx_type

    def keyForDocument(self):
        return self.getProxyAttribute('keyForDocument')

    keyForDocument = ComputedAttribute(keyForDocument)

    def documentToKeyMap(self):
        # replaces keyForDocument in Zope 2.7.x
        return self.getProxyAttribute('documentToKeyMap')

    documentToKeyMap = ComputedAttribute(documentToKeyMap)
    
    def index_object(self, documentId, obj, threshold=None):
        index_object = self.getProxyAttribute('index_object')
        try:
            ctx = createExprContext(obj)
            value = self._expr(ctx)
            wrapper = prepareObject(obj, value)
        except Exception, e:
            # gulp... the expression could raise many different types of errors.
            if DEBUG_LOG_ERRORS:
                LOG('ProxyIndex',PROBLEM,'%s tales error while indexing'%self.id)
            return 0
        except:
            return 0
        return index_object(documentId, wrapper, threshold)

    def unindex_object(self, documentId):
        unindex_object = self.getProxyAttribute('unindex_object')
        return unindex_object(documentId)

    def _apply_index(self, request, cid=''):
        apply_index = self.getProxyAttribute('_apply_index')

        # implicit pluggable interface contract 
        if not request.has_key(self.id):
            return None
        else:
            request.keywords[PROXIED_INDEX_ID]=request.get(self.id)
        
        res = apply_index(request, cid)
        return res
        
    def numObjects(self):
        numObjects = self.getProxyAttribute('numObjects')
        if callable(numObjects):
            return numObjects()
        else:
            return numObjects
    
    def __len__(self):
        """ len """
        return self.numObjects()

    def uniqueValues(self, name=None, withLength=0):
        uniqueValues = self.getProxyAttribute('uniqueValues')
        return uniqueValues(name, withLength)

    def getEntryForObject(self, documentId, default=_marker):
        getEntryForObject = self.getProxyAttribute('getEntryForObject')
        entry = getEntryForObject(documentId, default)
        if entry is _marker:
            return None
        return entry

    def getProxyAttribute(self, name):
        if hasattr(aq_base(self.idx), name):
            return getattr(self.idx, name)

        raise AttributeError, "%s not found"%str(name)

    def items(self):
        return self.getProxyAttribute('items')()

def prepareObject(obj, value):
    """
    prepare a wrapper for indexing using obj and value
    """

    # check if it obj is already wrapped
    # via cmf catalog mechanism
    wrapper = None
    if CMF_FOUND and isinstance(obj, IndexableObjectWrapper):
        wrapper = obj

    if wrapper is None:
        wrapper = IndexableWrapper(obj)

    setattr(wrapper, PROXIED_INDEX_ID, value)
        
    return wrapper

def getIndexTypes(self, names_only=1):
    " returns a list of plugin indexes for use in a zcatalog "

    obj = self
    found = 0

    while obj is not None:
        ifaces = objectImplements(obj)
        if IZCatalog in ifaces or ICatalogTool in ifaces:
            found = 1
            break
        newobj = aq_parent(obj)
        if newobj is obj:
            obj = None
        else:
            obj = newobj

    if not found:
        return []
    
    res = obj.all_meta_types(interfaces=(PluggableIndexInterface,))
    
    if names_only:
        return [r['name'] for r in res]

    return res

def getIndexForType(self, idx_type, extra):
    # we expect to get context from extra
    ctx = extra['idx_context']
    idx_caller = extra['idx_caller']
    
    # clean up the context of our values
    for pe in PROXY_EXTRA:
        del extra[pe]
        
    # set up key values pairs for the constructor
    keys = [k for k in extra.keys() if k.startswith('key')]
    keys.sort()
    vals = [v for v in extra.keys() if v.startswith('value')]
    vals.sort()

    pairs = zip(keys, vals)
        
    for k,v in pairs:
        extra[extra[k]]=extra[v]
        del extra[k], extra[v]

    p = None
    indexes = getIndexTypes(ctx, names_only=0)    

    for i in indexes:
        if i['name'] == idx_type:
            p = i
            break

    if p is None:
        raise ValueError("Index of type %s not found"%str(idx_type))

    klass = p['instance']

    if 'extra' in klass.__init__.func_code.co_varnames:
        index = klass(PROXIED_INDEX_ID, extra=extra, caller=aq_base(idx_caller))
    else:
        index = klass(PROXIED_INDEX_ID, aq_base(idx_caller))    

    return index
