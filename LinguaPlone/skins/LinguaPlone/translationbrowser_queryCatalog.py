## Script (Python) "referencebrowser_queryCatalog"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None,show_all=0,quote_logic=0,quote_logic_indexes=['SearchableText'],search_catalog=None
##title=wraps the portal_catalog with a rules qualified query
##
from ZODB.POSException import ConflictError
from Products.ZCTextIndex.ParseTree import ParseError

results=[]
if not search_catalog: search_catalog = 'portal_catalog'
catalog=getattr(context, search_catalog, context.portal_catalog)
if not hasattr(catalog, 'searchResults'):
    catalog= context.portal_catalog

indexes=catalog.indexes()
query={}
show_query=show_all
second_pass = {}

if REQUEST is None:
    REQUEST = context.REQUEST

def quotestring(s):
    return '"%s"' % s

def quotequery(s):
    if not s:
        return s
    try:
        terms = s.split()
    except ConflictError:
        raise
    except:
        return s
    tokens = ('OR', 'AND', 'NOT')
    s_tokens = ('OR', 'AND')
    check = (0, -1)
    for idx in check:
        if terms[idx].upper() in tokens:
            terms[idx] = quotestring(terms[idx])
    for idx in range(1, len(terms)):
        if (terms[idx].upper() in s_tokens and
            terms[idx-1].upper() in tokens):
            terms[idx] = quotestring(terms[idx])
    return ' '.join(terms)

for k, v in REQUEST.items():
    if v and k in indexes:
        if quote_logic and k in quote_logic_indexes:
            v = quotequery(v)
        query.update({k:v})
        show_query=1
    elif k.endswith('_usage'):
        key = k[:-6]
        param, value = v.split(':')
        second_pass[key] = {param:value}
    elif k=='sort_on' or k=='sort_order' or k=='sort_limit':
        query.update({k:v})

for k, v in second_pass.items():
    qs = query.get(k)
    if qs is None:
        continue
    query[k] = q = {'query':qs}
    q.update(v)

# doesn't normal call catalog unless some field has been queried
# against. if you want to call the catalog _regardless_ of whether
# any items were found, then you can pass show_all=1.

if show_query:
    try:
        results=catalog(query)
    except ParseError:
        pass

return results
