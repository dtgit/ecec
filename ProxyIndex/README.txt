Copyright (c) 2003 Infrae. All rights reserved.
See also LICENSE.txt

Meta::
  
  Valid for:  ProxyIndex 1.2
  Author:     Kapil Thangavelu 
  Email:      k_vertigo@objectrealms.net 
  CVS:        $Revision: 1.5 $

Proxy Index

  Purpose
  
    Proxy Index, is a plugin catalog index. it uses a tales
    expression to retrieve a value to index from an object.
    the value retrieved can then be indexed by any available
    plugin index.
 
    Primary Use Case

     for indexing attributes of subobjects when indexing
     a container, like a composite elements of a compound
     document, or object annotations.

  Usage
 
    from the zcatalog indexes tab, add a index of type proxy
    index.

    on the add form the following fields are defined

     - id 

	 pick any valid id you like

     - delegated type 

	 the type of index you'd like to use for the value

     - tales expression 

	 a tales expression evaluated for the value to index
 	
 	 the default context includes the following

	  - object 
	
	    the object being indexed

	 and the following standard tales objects

	  - nothing
	
	  - request

	  - modules

     - Key Value Pairs, are input forms for passing
       values to the index constructor, if any are 
       needed. (as with zctextindex for example).
       for most index types this can be left blank

     as an example here's how to fill out a form for zctextindex::

       key value pair: lexicon_id  my_lexicon
       key value pair: index_type  Cosine Measure
       key value pair: doc_attr    proxy_value
       

     the last key value pair could use a little explanation..
     internally the proxy index stores the index as an index
     named 'proxy_value', the behavior for most indexes is
     to index an attribute name thats equivalent to the index's
     id. proxy index, constructs a wrapper object for the indexing
     setting the value of the tales expression equal to that
     of the index name. in this case, zctextindex must be
     treated slightly differently as it can index an arbitrary
     attribute independent of its name, for most other index types
     this is not needed. 


