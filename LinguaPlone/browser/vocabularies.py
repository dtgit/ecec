from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.i18nmessageid import Message, MessageFactory

from Products.CMFCore.utils import getToolByName


_ = MessageFactory('linguaplone')


def sort_key(language):
    return language[1]


class UntranslatedLanguagesVocabulary(object):
    """Vocabulary factory returning untranslated languages for the context.
    """
    implements(IVocabularyFactory)

    def __init__(self, incl_neutral=False, incl_nochange=False):
        self.incl_neutral = incl_neutral
        self.incl_nochange = incl_nochange

    def __call__(self, context):
        context = getattr(context, 'context', context)
        ltool = getToolByName(context, 'portal_languages')
        supported = dict(ltool.listSupportedLanguages())
        translated = context.getTranslationLanguages()

        # List all languages not already translated
        languages = [lang for lang in supported if lang not in translated]

        items = [(l, supported[l]) for l in languages]
        items.sort(key=sort_key)
        items = [SimpleTerm(i[0], i[0], i[1].decode('utf-8')) for i in items]
        if self.incl_neutral:
            neutral = SimpleTerm(
                "neutral",
                "neutral",
                _("label_neutral", default=u"Neutral"),
            )
            items.insert(0, neutral)
        if self.incl_nochange:
            nochange = SimpleTerm(
                "nochange",
                "nochange",
                Message(
                    "label_no_change",
                    domain="plone",
                    default=u"No change",
                ),
            )
            items.insert(0, nochange)
        return SimpleVocabulary(items)

UntranslatedLanguagesVocabularyFactory = UntranslatedLanguagesVocabulary()
NeutralAndUntranslatedLanguagesVocabularyFactory = UntranslatedLanguagesVocabulary(incl_neutral=True)
NoChangeNeutralAndUntranslatedLanguagesVocabularyFactory = UntranslatedLanguagesVocabulary(incl_neutral=True, incl_nochange=True)


class DeletableLanguagesVocabulary(object):
    """Vocabulary factory returning deletable languages for the context.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        ltool = getToolByName(context, 'portal_languages')
        available = ltool.getAvailableLanguages()
        translations = context.getNonCanonicalTranslations()

        items = []
        for lang in translations.keys():
            desc = u"%s (%s): %s" % (
                available[lang].decode('utf-8'),
                lang,
                translations[lang][0].Title().decode('utf-8'),
            )
            items.append(SimpleTerm(lang, lang, desc))

        return SimpleVocabulary(items)

DeletableLanguagesVocabularyFactory = DeletableLanguagesVocabulary()
