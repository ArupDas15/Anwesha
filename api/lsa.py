from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import Pipeline
from sklearn.metrics.pairwise import cosine_similarity

from Lemmatization import lemmatizer
from query_expansion import query_expansion
import numpy as np
import preprocess
import joblib
import os
import pickle
import itertools


def set_up_LSA(docs, rank, save_model=False, lemmatiser=False):
    if lemmatiser:
        preprocessor = lemmatizer.document_linearization()
        vectorizer = TfidfVectorizer(tokenizer=preprocessor.identity_tokenizer, stop_words=None,
                                     use_idf=True,
                                     smooth_idf=True, max_df=0.9)
    else:
        preprocessor = preprocess.Document_linearization()
        vectorizer = TfidfVectorizer(tokenizer=preprocessor.pre_process, stop_words=None,
                                     use_idf=True,
                                     smooth_idf=True, max_df=0.9)
    svd_model = TruncatedSVD(n_components=rank,
                             algorithm='randomized',
                             n_iter=10)
    svd_transformer = Pipeline([('tfidf', vectorizer),
                                ('svd', svd_model)])
    dvecs = svd_transformer.fit_transform(docs)
    if save_model:
        if lemmatiser:
            np.save(os.path.join('SavedModels', 'dvecs_lem'), dvecs)
            joblib.dump(svd_transformer, os.path.join('SavedModels', 'svd_transformer_lem.pkl'))
            joblib.dump(svd_model, os.path.join('SavedModels', 'svd_model_lem.pkl'))
        else:
            np.save(os.path.join('SavedModels', 'dvecs'), dvecs)
            joblib.dump(svd_transformer, os.path.join('SavedModels', 'svd_transformer.pkl'))
            joblib.dump(svd_model, os.path.join('SavedModels', 'svd_model.pkl'))
        print("LSA model is saved in SavedModels directory.")
        exit()
    return vectorizer, svd_transformer, svd_model,dvecs


def load_LSA():
    vectorizer = joblib.load(os.path.join('SavedModels', 'TFIDF_vectorizer.pkl'))
    svd_transformer = joblib.load(os.path.join('SavedModels', 'svd_transformer.pkl'))
    svd_model = joblib.load(os.path.join('SavedModels', 'svd_model.pkl'))
    svd_model_lem = joblib.load(os.path.join('SavedModels', 'svd_model_lem.pkl'))
    dvecs = np.load(os.path.join('SavedModels', 'dvecs.npy'))
    vectorizer_lem = joblib.load(os.path.join('SavedModels', 'TFIDF_vectorizer_lem.pkl'))
    svd_transformer_lem = joblib.load(os.path.join('SavedModels', 'svd_transformer_lem.pkl'))
    dvecs_lem = np.load(os.path.join('SavedModels', 'dvecs_lem.npy'))
    return vectorizer, svd_transformer,svd_model,svd_model_lem, dvecs, vectorizer_lem, svd_transformer_lem, dvecs_lem

# Reference: https://www.kaggle.com/akashram/topic-modeling-intro-implementation
# Returns the word representation of the document currently projected in the concept space.
def get_concept2word_representation(model, vector, vocabulary_size):
    concept2word_rep = np.zeros((vocabulary_size))
    #Generates VT(concept-term matrix).
    for idx, topic in enumerate(model.components_):
    #vector[idx] is a co-effecient of the document and concept coordinate
    #topic is a concept vector in terms of word representation
        concept2word_rep += (vector[idx]*topic)
    return concept2word_rep


def lsa(vectorizer, svd_transformer, svd_model, docs, dvecs, q, k=10, qe=False, lemmatiser=False):
    if lemmatiser:
        # Returns a space separated lemmatised query.
        qrs = [lemmatizer.document_linearization().pre_process(q)]
        infile = open(os.path.join('Lemmatization', 'reverse_lem.pickle'), 'rb')
        reverse_lem = pickle.load(infile)
        infile.close()
    else:
        qrs = [q]

    qvecs = svd_transformer.transform(qrs)

    if qe == True:
        newqrs = []
        extra_term_concept_vectors = np.zeros((qvecs.shape))
        qe_result = query_expansion(q)
        for extra_terms in qe_result:
            query = q
            term = extra_terms
            term_weight = qe_result[term]
            try:
                words = preprocess.Document_linearization().pre_process(term)
                extra_words = ""

                for word in words:
                    if lemmatiser:
                        lem_word = lemmatizer.document_linearization().lem(word)
                        query = " ".join((query, lem_word))
                        extra_words = " ".join((extra_words, lem_word))
                    else:
                        query = " ".join((query, word))
                        extra_words = " ".join((extra_words, word))

                extra_term_concept_vectors[0] = extra_term_concept_vectors[0] + (
                        term_weight * svd_transformer.transform([extra_words]))

            except:
                pass
            newqrs.append(query)

            qvecs[0] += extra_term_concept_vectors[0]

    A = cosine_similarity(qvecs, dvecs)

    explainability_list = []

    for q in range(0, len(qrs)):
        result = np.argsort(A[q]).T[::-1][:k]
        per_query_explainability_list = []
        vocabulary_size = len(vectorizer.vocabulary_)
        query_word_rep = get_concept2word_representation(svd_model, qvecs[q], vocabulary_size)

        for doc in result:
            doc_word_rep = get_concept2word_representation(svd_model, dvecs[doc], vocabulary_size)
            # Calculates the hadamard product between the word representations of the query and the document vector.
            doc_query_pro = query_word_rep * doc_word_rep
            # explainable_terms list contains all the explainable terms of a document at index doc.
            explainable_terms = []
            terms = set(preprocess.Document_linearization().pre_process(docs[doc]))
            for i in doc_query_pro.argsort()[::-1]:
                if lemmatiser:
                    values = set()
                    cross_product_list = []
                    try:
                        cross_product_list.append(reverse_lem[vectorizer.get_feature_names()[i]])
                    except:
                        # print("Except: ",constituent_word,"doc_index: ",doc)
                        continue
                        # element here is a tuple. We are joining the items in the tuples by a space.
                    for element in itertools.product(*cross_product_list):
                        values.add(' '.join(element))
                    if values is not None:
                        for v in values:
                            if v in terms:
                                explainable_terms.extend([(v, doc_query_pro[i])])
                    if len(explainable_terms) >= 10:
                        break
                else:
                    if vectorizer.get_feature_names()[i] in terms:
                        explainable_terms.append((vectorizer.get_feature_names()[i], doc_query_pro[i]))
                        if len(explainable_terms) >= 10:
                            break
            per_query_explainability_list.append(explainable_terms)
        explainability_list.append(per_query_explainability_list)

    return A, explainability_list