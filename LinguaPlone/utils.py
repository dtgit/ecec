# Plone Solutions AS <info@plonesolutions.com>
# http://www.plonesolutions.com

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""
Utilities.
"""

from types import FunctionType as function

# Method generation for ITranslatable content with language independent fields
from Products.Archetypes.ClassGen import GeneratorError, _modes
from Products.Archetypes.ClassGen import Generator as ATGenerator
from Products.Archetypes.ClassGen import ClassGenerator as ATClassGenerator
from Products.Archetypes.ArchetypeTool import registerType as registerATType

from Products.LinguaPlone.config import KWARGS_TRANSLATION_KEY, RELATIONSHIP

AT_GENERATE_METHOD = []
_modes.update({
    't' : { 'prefix'   : 'setTranslation',
            'attr'     : 'translation_mutator',
            'security' : 'write_permission',
            },
})


class Generator(ATGenerator):
    """Generates methods for language independent fields."""

    def makeMethod(self, klass, field, mode, methodName):
        name = field.getName()
        method = None
        if mode == "r":
            def generatedAccessor(self, **kw):
                """Default Accessor."""
                if kw.has_key('schema'):
                    schema = kw['schema']
                else:
                    schema = self.Schema()
                    kw['schema'] = schema
                return schema[name].get(self, **kw)
            method = generatedAccessor
        elif mode == "m":
            def generatedEditAccessor(self, **kw):
                """Default Edit Accessor."""
                if kw.has_key('schema'):
                    schema = kw['schema']
                else:
                    schema = self.Schema()
                    kw['schema'] = schema
                return schema[name].getRaw(self, **kw)
            method = generatedEditAccessor
        elif mode == "w":
            # the generatedMutator doesn't actually mutate, but calls a
            # translation mutator on all translations, including self.
            def generatedMutator(self, value, **kw):
                """Default Mutator."""
                if kw.has_key('schema'):
                    schema = kw['schema']
                else:
                    schema = self.Schema()
                    kw['schema'] = schema
                # translationMethodName is always present, as it is set in the generator
                translationMethodName = getattr(getattr(self, schema[name].mutator, None), '_lp_mutator', None)
                if translationMethodName is None: # Houston, we have a problem
                    return schema[name].set(self, value, **kw)
                # Instead of additional classgen magic, we check the language independent
                if not schema[name].languageIndependent:
                    return getattr(self, translationMethodName)(value, **kw)
                # Look up the actual mutator and delegate to it.
                translations = [t[0] for t in \
                                hasattr(self, 'getTranslations') and \
                                self.getTranslations().values() or []]
                # reverse to return the result of the canonical mutator
                translations.reverse()
                res = None
                for t in translations:
                    res = getattr(t, translationMethodName)(value, **kw)
                return res
            method = generatedMutator
        elif mode == "t":
            # The translation mutator that changes data
            def generatedTranslationMutator(self, value, **kw):
                """Delegated Mutator."""
                if kw.has_key('schema'):
                    schema = kw['schema']
                else:
                    schema = self.Schema()
                    kw['schema'] = schema
                return schema[name].set(self, value, **kw)
            method = generatedTranslationMutator
        else:
            raise GeneratorError("""Unhandled mode for method creation:
            %s:%s -> %s:%s""" %(klass.__name__,
                                name,
                                methodName,
                                mode))

        # Zope security requires all security protected methods to have a
        # function name. It uses this name to determine which roles are allowed
        # to access the method.
        # This code is renaming the internal name from e.g. generatedAccessor to
        # methodName.
        method = function(method.func_code,
                          method.func_globals,
                          methodName,
                          method.func_defaults,
                          method.func_closure,
                         )
        method._lp_generated = True # Note that we generated this method
        method._lp_generated_by = klass.__name__
        if mode == 'w': # The method to delegate to
            method._lp_mutator = self.computeMethodName(field, 't')
        setattr(klass, methodName, method)


class ClassGenerator(ATClassGenerator):
    """Generates methods for language independent fields."""

    def generateClass(self, klass):
        # We are going to assert a few things about the class here
        # before we start, set meta_type, portal_type based on class
        # name, but only if they are not set yet
        if (not getattr(klass, 'meta_type', None) or
            'meta_type' not in klass.__dict__):
            klass.meta_type = klass.__name__
        if (not getattr(klass, 'portal_type', None) or
            'portal_type' not in klass.__dict__):
            klass.portal_type = klass.__name__
        klass.archetype_name = getattr(klass, 'archetype_name',
                                       self.generateName(klass))

        self.checkSchema(klass)
        fields = klass.schema.fields()
        # Find the languageIndependent fields.
        fields = [field for field in fields if field.languageIndependent]
        self.generateMethods(klass, fields)

    def generateMethods(self, klass, fields):
        generator = Generator()
        for field in fields:
            assert not 'm' in field.mode, 'm is an implicit mode'
            assert not 't' in field.mode, 't is an implicit mode'

            # Make sure we want to muck with the class for this field
            if 'c' not in field.generateMode:
                continue
            typ = getattr(klass, 'type')
            # (r, w)
            for mode in field.mode:
                self.handle_mode(klass, generator, typ, field, mode)
                if mode == 'w':
                    self.handle_mode(klass, generator, typ, field, 'm')
                    self.handle_mode(klass, generator, typ, field, 't')

    def handle_mode(self, klass, generator, typ, field, mode):
        attr = _modes[mode]['attr']
        # Did the field request a specific method name?
        methodName = getattr(field, attr, None)
        if not methodName:
            methodName = generator.computeMethodName(field, mode)

        # If there is already a mutator, make that the translation mutator
        # NB: Use of __dict__ means base class attributes are ignored
        if mode == 'w' and klass.__dict__.has_key(methodName):
            method = getattr(klass, methodName).im_func
            method._lp_renamed = True # Note that we renamed this method
            method._lp_renamed_by = klass.__name__
            setattr(klass, generator.computeMethodName(field, 't'), method)
            delattr(klass, methodName)

        # Avoid name space conflicts
        def want_generated_method(klass, methodName, mode):
            if getattr(klass, methodName, None) is AT_GENERATE_METHOD:
                return True
            if mode == 'r':
                return not hasattr(klass, methodName)
            else: # mode == w|m|t
                return not klass.__dict__.has_key(methodName)

        if want_generated_method(klass, methodName, mode):
            if typ.has_key(methodName):
                raise GeneratorError("There is a conflict"
                                     "between the Field(%s) and the attempt"
                                     "to generate a method of the same name on"
                                     "class %s" % (
                    methodName,
                    klass.__name__))

            # Make a method for this klass/field/mode
            generator.makeMethod(klass, field, mode, methodName)

        # Update security regardless of the method being generated or
        # not. Not protecting the method by the permission defined on
        # the field may leave security open and lead to misleading
        # bugs.
        self.updateSecurity(klass, field, mode, methodName)

        # Note on the class what we did (even if the method existed)
        attr = _modes[mode]['attr']
        setattr(field, attr, methodName)


_cg = ClassGenerator()
generateClass = _cg.generateClass
generateMethods = _cg.generateMethods


def registerType(klass, package=None):
    """Overrides the AT registerType to enable method generation for language independent fields"""
    # Generate methods for language independent fields
    generateClass(klass)

    # Pass on to the regular AT registerType
    registerATType(klass, package)


def generateCtor(name, module):
    ctor = """
def add%(name)s(self, id, **kwargs):
    o = %(name)s(id)
    self._setObject(id, o)
    o = self._getOb(id)
    canonical = None
    if kwargs.has_key('%(KWARGS_TRANSLATION_KEY)s'):
        canonical = kwargs.get('%(KWARGS_TRANSLATION_KEY)s')
        del kwargs['%(KWARGS_TRANSLATION_KEY)s']
    o.initializeArchetype(**kwargs)
    if canonical is not None:
        o.addReference(canonical, '%(RELATIONSHIP)s')
    return o.getId()
""" % {'name':name, 'KWARGS_TRANSLATION_KEY':KWARGS_TRANSLATION_KEY, 'RELATIONSHIP':RELATIONSHIP}

    exec ctor in module.__dict__
    return getattr(module, 'add%s' % name)


# Exact copy of ArchetypeTool.process_type, but with new generateCtor
import sys
from copy import deepcopy
from Products.Archetypes.ArchetypeTool import base_factory_type_information, modify_fti
def process_types(types, pkg_name):
    content_types = ()
    constructors  = ()
    ftis = ()

    for rti in types:
        typeName = rti['name']
        klass = rti['klass']
        module = rti['module']

        if hasattr(module, 'factory_type_information'):
            fti = module.factory_type_information
        else:
            fti = deepcopy(base_factory_type_information)
            modify_fti(fti, klass, pkg_name)

        # Add a callback to modifty the fti
        if hasattr(module, 'modify_fti'):
            module.modify_fti(fti[0])
        else:
            m = None
            for k in klass.__bases__:
                base_module = sys.modules[k.__module__]
                if hasattr(base_module, 'modify_fti'):
                    m = base_module
                    break
            if m is not None:
                m.modify_fti(fti[0])

        ctor = getattr(module, 'add%s' % typeName, None)
        if ctor is None:
            ctor = generateCtor(typeName, module)

        content_types += (klass,)
        constructors += (ctor,)
        ftis += fti

    return content_types, constructors, ftis

# Language tag splitting
def splitLanguage(tag):
    """Split a language tag (RFC 1766) into components
    
    Currently, this splits a language tag on the first dash *only*, and will 
    not split i- and x- language tags, as these prefixes denote non-standard
    languages.
    
    """
    try:
        tag = tag.lower()
        if tag[:2] in ('i-', 'x-'):
            return (tag, None)
        tags = tag.split('-', 1)
    except AttributeError:
        # not a string
        tags = []
    tags.extend((None, None))
    return tuple(tags[:2]) # returns (main, sub), (main, None) or (None, None)


def linkTranslations(context, todo):
    """Make content objects in translations of eachother.

    The objects to link are passed in the form an iterable sequence
    of things to connect. The things to connect are specified as a list
    of tuples containing the physical path of the object and the language.
    For example:

      [ [ (["FrontPage"], "en"), (["FrontPage-no"], "no") ],
        [ (["images", "logo"], "en"), (["bilder", "logo"], "no") ] ]

    That will link the FrontPage and FrontPage-no objects together as
    English and Norwegian translation as well as the images/logo and
    bilder/logo objects.
    """

    for task in todo:
        task = [(context.unrestrictedTraverse("/".join(path)), lang)
                    for (path, lang) in task]

        types=set()
        for (object, lang) in task:
            object.setLanguage(lang)
            types.add(object.portal_type)

        if len(types)>1:
            raise ValueError("Not all translations have the same portal type")

        task = [t[0] for t in task]
        if len(task)<=1:
            continue

        (canonical, translations) = (task[0], task[1:])
        for translation in translations:
            translation.addTranslationReference(canonical)
            canonical.setCanonical()

