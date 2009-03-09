from Acquisition import aq_parent, aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.permissions import ManagePortal
from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.publisher.browser.menu import BrowserSubMenuItem
from Products.LinguaPlone import LinguaPloneMessageFactory as _
from Products.LinguaPlone.browser.interfaces import ITranslateMenu
from Products.LinguaPlone.browser.interfaces import ITranslateSubMenuItem
from Products.LinguaPlone.interfaces import ITranslatable
from plone.memoize.instance import memoize


class TranslateMenu(BrowserMenu):
    implements(ITranslateMenu)

    @memoize
    def getUntranslatedLanguages(self, context):
        lt=getToolByName(context, "portal_languages")
        languages=lt.listSupportedLanguages()
        translated=context.getTranslationLanguages()
        languages=[lang for lang in languages if lang[0] not in translated]
        languages.sort(key=lambda x: x[1])
        return languages


    @memoize
    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""

        menu=[]
        url=context.absolute_url()
        lt=getToolByName(context, "portal_languages")
        showflags=lt.showFlags()
        context_state=getMultiAdapter((context, request),
                name="plone_context_state")

        langs=self.getUntranslatedLanguages(context)
        parent=aq_parent(aq_inner(context))
        if ITranslatable.providedBy(parent):
            parentlangs=parent.getTranslationLanguages()
        else:
            parentlangs=[l[0] for l in lt.listSupportedLanguages()]

        for (lang_id, lang_name) in langs:
            icon=showflags and lt.getFlagForLanguageCode(lang_id) or None
            item={
                "title"       : lang_name,
                "description" : _(u"title_translate_into",
                                    default=u"Translate into ${lang_name}",
                                    mapping={"lang_name" : lang_name}),
                "action"      : url+"/@@translate?newlanguage=%s" % lang_id,
                "selected"    : False,
                "icon"        : icon,
                "extra"       : { "id"        : "translate_into_%s" % lang_id,
                                  "separator" : None,
                                  "class"     : "",
                                 },
                "submenu"     : None,
                }

            menu.append(item)

        menu.append({
            "title"       : _(u"label_manage_translations",
                                default=u"Manage translations..."),
            "description" : _(u"title_manage_translations",
                                default=u""),
            "action"      : url+"/manage_translations_form",
            "selected"    : False,
            "icon"        : None,
            "extra"       : { "id"        : "_manage_translations",
                              "separator" : langs and "actionSeparator" or None,
                              "class"     : ""
                             },
            "submenu"     : None,
            })

        site=getUtility(ISiteRoot)
        mt=getToolByName(context, "portal_membership")
        if mt.checkPermission(ManagePortal, site): 
            portal_state=getMultiAdapter((context, request), name="plone_portal_state")

            menu.append({
                "title"       : _(u"label_language_settings",
                                    default=u"Language settings..."),
                "description" : _(u"title_language_settings", default=u""),
                "action"      : portal_state.portal_url()+"/@@language-controlpanel",
                "selected"    : False,
                "icon"        : None,
                "extra"       : { "id" : "_language_settings",
                                  "separator" : None,
                                  "class" : "",
                                },
                "submenu"     : None,
                })

        return menu


class TranslateSubMenuItem(BrowserSubMenuItem):
    implements(ITranslateSubMenuItem)

    title = _(u"label_translate_menu", default=u"Translate into...")
    description = _(u"title_translate_menu",
            default="Manage translations for your content.")
    submenuId = "plone_contentmenu_translate"

    order = 5
    extra = { "id" : "plone-contentmenu-translate" }

    @property
    def action(self):
        return self.context.absolute_url() + "/manage_translations_form"

    @memoize
    def available(self):
        if not ITranslatable.providedBy(self.context):
            return False

        qi=getToolByName(self.context, "portal_quickinstaller")
        return qi.isProductInstalled("LinguaPlone")


    def disabled(self):
        return False

    def selected(self):
        return False
