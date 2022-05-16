from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import numpy as np
from query_expansion import query_expansion
import preprocess
import joblib
from scipy import sparse
import os
from Lemmatization import lemmatizer
import pickle
import itertools
import statistics


def set_up_TFIDF(docs, lemmatiser=False, save_model=False):
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
    # Learn vocabulary and idf of the vectorizer from the training set based on the initialized parameters.
    vectorizer.fit(docs)
    # Returns document-term matrix.
    # The below tfidf_matrix has the TF-IDF values of all the documents in the corpus. This is a big sparse matrix.
    tfidf_matrix = vectorizer.transform(docs)
    if save_model:
        if lemmatiser:
            joblib.dump(vectorizer, os.path.join('SavedModels', 'TFIDF_vectorizer_lem.pkl'))
            sparse.save_npz(os.path.join("SavedModels", "TFIDFmatrix_lem.npz"), tfidf_matrix)
        else:
            joblib.dump(vectorizer, os.path.join('SavedModels', 'TFIDF_vectorizer.pkl'))
            sparse.save_npz(os.path.join("SavedModels", "TFIDFmatrix.npz"), tfidf_matrix)
        print("TF-IDF model is saved in SavedModels directory.")
        # exit()
    return vectorizer, tfidf_matrix


def load_tfidf():
    vectorizer = joblib.load(os.path.join('SavedModels', 'TFIDF_vectorizer.pkl'))
    vectorizer_lem = joblib.load(os.path.join('SavedModels', 'TFIDF_vectorizer_lem.pkl'))
    # The below tfidf_matrix has the TF-IDF values of all the documents in the corpus. This is a big sparse matrix.
    tfidf_matrix = sparse.load_npz(os.path.join('SavedModels', "TFIDFmatrix.npz"))
    tfidf_matrix_lem = sparse.load_npz(os.path.join('SavedModels', "TFIDFmatrix_lem.npz"))
    return vectorizer, tfidf_matrix, vectorizer_lem, tfidf_matrix_lem


def document_wt(list1, list2):
    """
    The goal of Document weight function is to assign higher weight
    to documents containing more words from the query than documents having fewer query words
    :param list1: list of words in query after pre-processing the query.
    :param list2: list of words in the document after pre-processing.
    :return: Document-Query Overlap score in the range of [0,1].
    """
    s1 = set(list1)
    s2 = set(list2)
    intersection = float(len(s1.intersection(s2)))
    query_wt = float(len(s1))
    try:
        return intersection / query_wt
    except:
        return 0


def tfidf(vectorizer, tfidf_matrix, q, docs, k=10, qe=False, lemmatiser=False, max_explainble_terms=10):
    if lemmatiser:
        # Returns a space separated lemmatised query.
        qrs = [lemmatizer.document_linearization().pre_process(q)]
        infile = open(os.path.join('Lemmatization', 'reverse_lem.pickle'), 'rb')
        reverse_lem = pickle.load(infile)
        infile.close()
    else:
        qrs = [q]

    qvecs = vectorizer.transform(qrs)

    if qe:
        idf = dict(zip(vectorizer.get_feature_names(), vectorizer.idf_))
        newqrs = []
        # Converting the csr matrix qvecs to dense array to alter the TF-IDF scores.
        Q = qvecs.toarray()
        qe_result = query_expansion(q)
        query = qrs[0]
        for extra_terms in qe_result:
            term = extra_terms
            term_weight = qe_result[term]
            try:
                words = preprocess.Document_linearization().pre_process(term)
                for word in words:
                    if lemmatiser:
                        lem_word = lemmatizer.document_linearization().lem(word)
                        query = " ".join((query, lem_word))
                        index = vectorizer.vocabulary_[lem_word]
                        Q[0][index] = term_weight * idf[lem_word]
                    else:
                        query = " ".join((query, word))
                        index = vectorizer.vocabulary_[word]
                        Q[0][index] = term_weight * idf[word]

            except:
                pass
        newqrs.append(query)
        # Converting the dense array Q back to csr matrix qvecs.
        qvecs = csr_matrix(Q)

    # Returns a list of all the unique words in the vocabulary of the document collection.
    feature_names = vectorizer.get_feature_names()
    q_idx = []
    for v in qvecs:
        q_idx.append(v.indices)
    idx = []
    for v in tfidf_matrix:
        idx.append(v.indices)

    A = cosine_similarity(qvecs, tfidf_matrix)
    row_max = A.max(axis=1)
    A = A / row_max[:, np.newaxis]
    B = np.zeros(shape=A.shape)
    for i in range(0, len(qrs)):
        for j in range(0, tfidf_matrix.shape[0]):
            B[i][j] = document_wt([feature_names[x] for x in q_idx[i]],
                                  # Reference: https://stackoverflow.com/a/38770335
                                  # tfidf_matrix[j, :].nonzero()[1]] gives the list of all the tokens in
                                  # the document 'j' from the document collection.
                                  [feature_names[x] for x in tfidf_matrix[j, :].nonzero()[1]])
    for i in range(0, len(qrs)):
        for j in range(0, tfidf_matrix.shape[0]):
            try:
                A[i][j] = statistics.harmonic_mean([A[i][j], B[i][j]])
            except:
                # Whenever divide by zero error occurs we assign the f-score as 0.
                A[i][j] = 0

    explainability_list = []

    for q in range(0, len(qrs)):
        result = np.argsort(A[q]).T[::-1][:k]
        per_query_explainability_list = []
        for doc in result:
            feature_index = list(set(q_idx[q]).intersection(idx[doc]))
            tfidf_scores = zip(feature_index, [tfidf_matrix[doc, x] for x in feature_index])
            # Contains all the explainable terms of a document at index doc.
            explainable_terms = []
            # print("TFIDF Scores in Document ", str(file_paths[doc]), ":\n")
            for w, s in [(feature_names[i], round(s, 3)) for (i, s) in tfidf_scores]:
                # Extract all the explainable terms of the document at index doc and add it to explainable_terms list.
                if lemmatiser:
                    # Reference: https://stackoverflow.com/a/533917
                    # Reference: https://www.tutorialspoint.com/python-join-tuple-elements-in-a-list
                    values = set()
                    cross_product_list = []
                    for constituent_word in w.split():
                        try:
                            cross_product_list.append(reverse_lem[constituent_word])
                        except:
                            # print("Except: ",constituent_word,"doc_index: ",doc)
                            continue
                    # element here is a tuple. We are joining the items in the tuples by a space.
                    for element in itertools.product(*cross_product_list):
                        values.add(' '.join(element))
                    terms = set(preprocess.Document_linearization().pre_process(docs[doc]))
                    if values is not None:
                        for v in values:
                            if v in terms:
                                explainable_terms.extend([(v, s)])
                else:
                    explainable_terms.extend([(w, s)])
                if len(explainable_terms) > max_explainble_terms:
                    # Sorting in descending order using the second element of the tuple.
                    explainable_terms.sort(key=lambda x: x[1], reverse=True)
                    # Slicing the list to first k elements and ignore all the elements that occur after k elements.
                    explainable_terms = explainable_terms[0:max_explainble_terms]
            # Contains a list of all the explainable terms in all the documents with respect to a query at index q.
            per_query_explainability_list.append(explainable_terms)
        explainability_list.append(per_query_explainability_list)

    return A, explainability_list
