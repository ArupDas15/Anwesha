import pyiwn

#Download the IndoWordnet synset data
#pyiwn.download()

#Create a IndoWordNet class instance and set a language to access its Wordnet
import preprocess
from Lemmatization import lemmatizer

iwn = pyiwn.IndoWordNet(pyiwn.Language.BENGALI)

#import nltk


#nltk.download('stopwords')
from nltk.corpus import stopwords as eng_stopwords
import stopwordsiso as stopwords
import lesk
from bnlp import NLTKTokenizer
from bnlp import POS
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
from bnunicodenormalizer import Normalizer


def query_expansion(query, n_extras=3, syn_wt=0.25, hyper_wt=0.125, hypo_wt=0.0625, ent_wt=0.03125):
    factory = IndicNormalizerFactory()
    normalizer = factory.get_normalizer("bn", remove_nuktas=False)
    # initialize
    bnorm = Normalizer()
    query = normalizer.normalize(query)
    query = bnorm(query)
    dl = preprocess.Document_linearization()
    dl_lem = lemmatizer.document_linearization()
    extra_terms = {}
    stop_words = stopwords.stopwords("bn").union(set(eng_stopwords.words('english')))
    bn_pos = POS()
    # It uses the CRF Model tagset.
    model_path = "models/bn_pos.pkl"
    bnltk = NLTKTokenizer()
    # Stores the list of sentence_tokens.
    sentence_tokens = bnltk.sentence_tokenize(query)

    for sentence_no, q_sent in enumerate(sentence_tokens):
        # Generates a tuple of the form: ('WORD', 'TAG')
        tags = bn_pos.tag(model_path, q_sent)

        sentence = []
        for i, word in enumerate(tags):
            if word[1] in ['JJ', 'NC', 'NP', 'VM', 'JQ', 'NV', 'AMN', 'VAUX', 'NST', 'ALC'] and word[
                0] not in stop_words:
                # The variable sentence only consists of the open class words.
                sentence.append(word[0])

        # Taking only the unique terms in the sentence else it can lead to Key Error.
        sentence = list(set(sentence))
        lesk_obj = lesk.Lesk(list(set(sentence + [dl_lem.lem(w) for w in sentence])), simple=True, adapted=True)
        for word in sentence:
            count = 0
            result = lesk_obj.lesk(word, sentence)
            if str(result) == 'None':
                result = lesk_obj.lesk(dl_lem.lem(word), [w for w in sentence if w != word])
                if str(result) == 'None':
                    result = lesk_obj.lesk(word, list(set([dl_lem.lem(w1) for w1 in
                                                           [w for w in sentence if w != word]])))
                    if str(result) == 'None':
                        result = lesk_obj.lesk(dl_lem.lem(word),
                                               list(set([dl_lem.lem(w1) for w1 in
                                                         [w for w in sentence if w != word]])))
            if str(result) != 'None':
                a = result.lemma_names()
                for t in a:
                    if t not in extra_terms and count < n_extras and (t != word and t != dl_lem.lem(word)):
                        extra_terms[t] = syn_wt
                        count = count + 1
                    elif count < n_extras and (t != word and t != dl_lem.lem(word)):
                        extra_terms[t] = max(extra_terms[t], syn_wt)

                for res in iwn.synset_relation(result, pyiwn.SynsetRelations.HYPERNYMY):
                    if count < n_extras:
                        a = res.lemma_names()[0]
                        if a not in extra_terms and (a != word and a != dl_lem.lem(word)):
                            extra_terms[a] = hyper_wt
                            count = count + 1
                        elif a != word and a != dl_lem.lem(word):
                            extra_terms[a] = max(extra_terms[a], hyper_wt)

                for res in iwn.synset_relation(result, pyiwn.SynsetRelations.HYPONYMY):
                    if count < n_extras:
                        a = res.lemma_names()[0]
                        if a not in extra_terms and (a != word and a != dl_lem.lem(word)):
                            extra_terms[a] = hypo_wt
                            count = count + 1
                        elif a != word and a != dl_lem.lem(word):
                            extra_terms[a] = max(extra_terms[a], hypo_wt)

                for res in iwn.synset_relation(result, pyiwn.SynsetRelations.ENTAILMENT):
                    if count < n_extras:
                        a = res.lemma_names()[0]
                        if a not in extra_terms and (a != word and a != dl_lem.lem(word)):
                            extra_terms[a] = ent_wt
                            count = count + 1
                        elif a != word and a != dl_lem.lem(word):
                            extra_terms[a] = max(extra_terms[a], ent_wt)

    return extra_terms

