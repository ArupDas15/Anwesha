import scipy as scipy
import sklearn as sklearn
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


def set_up_ESA(c_docs, tr_vectorizer, tr_tfidf_matrix, lemmatiser=False, save_model=False):
    if lemmatiser:
        preprocessor = lemmatizer.document_linearization()
        c_vectorizer = TfidfVectorizer(tokenizer=preprocessor.identity_tokenizer, stop_words=None,
                                       use_idf=True,
                                       smooth_idf=True, max_df=0.9)
    else:
        preprocessor = preprocess.Document_linearization()
        c_vectorizer = TfidfVectorizer(tokenizer=preprocessor.pre_process, stop_words=None,
                                       use_idf=True,
                                       smooth_idf=True, max_df=0.9)
    # Learn vocabulary and idf of the vectorizer from the training set based on the initialized parameters.
    c_vectorizer.fit(c_docs)
    # Returns document-term matrix.
    # The below tfidf_matrix has the TF-IDF values of all the documents in the corpus. This is a big sparse matrix.
    c_tfidf_matrix = c_vectorizer.transform(c_docs)
    tr_doc_term_matrix = tr_tfidf_matrix.toarray()
    # The rows in tr_doc_term_matrix represents the documents. To find which document is referred to do
    # tr_file_paths[row_number_of_tr_doc_term_matrix]
    # The columns in tr_doc_term_matrix represents the terms of the vocabulary of the train dataset.
    c_doc_term_matrix = c_tfidf_matrix.toarray()
    tr_doc_concept_matrix = np.zeros((tr_doc_term_matrix.shape[0], c_doc_term_matrix.shape[0]))

    # Returns a list of all the unique words in the vocabulary of Train Dataset.
    tr_feature_names = tr_vectorizer.get_feature_names()
    # Returns a list of all the unique words in the vocabulary of Concept Dataset.
    c_feature_names = c_vectorizer.get_feature_names()
    for i in range(0, tr_doc_term_matrix.shape[0]):
        # tr_feature_index is a numpy array. It contains the indices of the terms in document i that have non-zero
        # tfidf score.
        tr_feature_index = tr_tfidf_matrix[i, :].nonzero()[1]
        # Get the tfidf score for all the indices in tf_feature_index.
        tr_tfidf_scores = zip(tr_feature_index, [tr_tfidf_matrix[i, x] for x in tr_feature_index])
        # Create a tfidf vector of size = no. of concepts(articles) in the concept corpus. THe tfidf vector
        # represents the document vector of document i.
        tfidf_vec = np.zeros((c_doc_term_matrix.shape[0]))
        # w represents the term 't'
        # s represents the tfidf score of the term 't' in document 'd'.
        for w, s in [(tr_feature_names[i], s) for (i, s) in tr_tfidf_scores]:

            try:
                c_word_index = c_vectorizer.vocabulary_[w]

                temp_vec = np.zeros((c_doc_term_matrix.shape[0]))
                for j in range(0, c_doc_term_matrix.shape[0]):
                    temp_vec[j] = c_doc_term_matrix[j][c_word_index] * s
                tfidf_vec = tfidf_vec + temp_vec

            except:

                # if a term in train dataset is not present as a concept in the concept dataset then its tfidf score
                # is set to 0.
                continue
        # tr_filewrite.close()
        tr_doc_concept_matrix[i] = tfidf_vec
    doc_concept_matrix = csr_matrix(tr_doc_concept_matrix)

    if save_model:
        if lemmatiser:
            joblib.dump(c_vectorizer, os.path.join('SavedModels', 'c_TFIDF_vectorizer_lem.pkl'))
            sparse.save_npz(os.path.join("SavedModels", "c_TFIDFmatrix_lem.npz"), c_tfidf_matrix)
            sparse.save_npz(os.path.join("SavedModels", "doc_concept_matrix_lem.npz"), doc_concept_matrix)

        else:
            joblib.dump(c_vectorizer, os.path.join('SavedModels', 'c_TFIDF_vectorizer.pkl'))
            sparse.save_npz(os.path.join("SavedModels", "c_TFIDFmatrix.npz"), c_tfidf_matrix)
            sparse.save_npz(os.path.join("SavedModels", "doc_concept_matrix.npz"), doc_concept_matrix)
        print("ESA model is saved in SavedModels directory.")
    return c_vectorizer, c_tfidf_matrix, doc_concept_matrix


def load_ESA():
    c_vectorizer = joblib.load(os.path.join('SavedModels', 'c_TFIDF_vectorizer.pkl'))
    c_vectorizer_lem = joblib.load(os.path.join('SavedModels', 'c_TFIDF_vectorizer_lem.pkl'))
    # The below tfidf_matrix has the TF-IDF values of all the documents in the corpus. This is a big sparse matrix.
    c_tfidf_matrix = sparse.load_npz(os.path.join('SavedModels', "c_TFIDFmatrix.npz"))
    c_tfidf_matrix_lem = sparse.load_npz(os.path.join('SavedModels', "c_TFIDFmatrix_lem.npz"))
    doc_concept_matrix_lem = sparse.load_npz(os.path.join('SavedModels', "doc_concept_matrix_lem.npz"))
    doc_concept_matrix = sparse.load_npz(os.path.join('SavedModels', "doc_concept_matrix.npz"))
    return c_vectorizer, c_tfidf_matrix, c_vectorizer_lem, c_tfidf_matrix_lem, doc_concept_matrix, doc_concept_matrix_lem
    # return c_vectorizer, c_tfidf_matrix, doc_concept_matrix


def get_concept_representation(c_vectorizer, c_doc_term_matrix, word, tf_idf_score, concept_vec_size):
    concept_vec = np.zeros((concept_vec_size))
    try:
        c_word_index = c_vectorizer.vocabulary_[word]
        for j in range(0, concept_vec_size):
            concept_vec[j] = c_doc_term_matrix[j][c_word_index] * tf_idf_score
    except:
        return scipy.sparse.csr_matrix(np.zeros((concept_vec_size)))
    return scipy.sparse.csr_matrix(concept_vec)


def esa(tr_tfidf_matrix, vectorizer, c_vectorizer, c_tfidf_matrix, doc_concept_matrix, q, docs, k=10, qe=False, lemmatiser=False, explainable_threshold=0.5):
    if lemmatiser:
        # Returns a space separated lemmatized query.
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

    c_doc_term_matrix = c_tfidf_matrix.toarray()
    tr_feature_names = vectorizer.get_feature_names()
    q_concept_matrix = np.zeros((len(qrs), c_doc_term_matrix.shape[0]))
    # Returns a list of all the unique words in the vocabulary of Train Dataset.
    for i in range(0, len(qrs)):
        q_feature_index = qvecs[i, :].nonzero()[1]
        q_tfidf_scores = zip(q_feature_index, [qvecs[i, x] for x in q_feature_index])

        tfidf_vec = np.zeros((c_doc_term_matrix.shape[0]))

        # w represents the term 't'
        # s represents the tfidf score of the term 't' in document 'd'.
        for w, s in [(tr_feature_names[i], s) for (i, s) in q_tfidf_scores]:
            try:
                c_word_index = c_vectorizer.vocabulary_[w]
                # All the documents in the Concept_Dataset is considered to be a wikipedia concept.
                temp_vec = np.zeros((c_doc_term_matrix.shape[0]))
                for j in range(0, c_doc_term_matrix.shape[0]):
                    temp_vec[j] = c_doc_term_matrix[j][c_word_index] * s

                tfidf_vec = tfidf_vec + temp_vec
            except:
                continue
        q_concept_matrix[i] = tfidf_vec

    newqvecs = csr_matrix(q_concept_matrix)
    A = cosine_similarity(newqvecs, doc_concept_matrix)

    feature_names = vectorizer.get_feature_names()
    q_idx = []
    for v in qvecs:
        q_idx.append(v.indices)
    idx = []
    for v in doc_concept_matrix:
        idx.append(v.indices)

    explainability_list = []
    for q in range(0, len(qrs)):
        result = np.argsort(A[q]).T[::-1][:k]
        per_query_explainability_list = []
        concept_size = c_doc_term_matrix.shape[0]

        for doc in result:
            terms = set(preprocess.Document_linearization().pre_process(docs[doc]))
            # tr_feature_index is a numpy array. It contains the indices of the terms in document doc that have 
            # non-zero tfidf score. 
            tr_feature_index = tr_tfidf_matrix[doc, :].nonzero()[1]
            # Create a tuple where first element is the index from tf_feature_index and second element is its tf-idf 
            # score in the document at index 'doc'. 
            tr_tfidf_scores = zip(tr_feature_index, [tr_tfidf_matrix[doc, x] for x in tr_feature_index])
            word_rel_score = []
            max_word_score = 0.0
            for w, s in [(tr_feature_names[j], s) for (j, s) in tr_tfidf_scores]:
                word_score = round(
                    sklearn.metrics.pairwise.cosine_similarity(
                        get_concept_representation(c_vectorizer, c_doc_term_matrix, w, s, concept_size),
                        newqvecs[i])[0][0], 4)
                # Finds the cosine score of the word having maximum relevance to the concept representation of the
                # query.
                max_word_score = max(max_word_score, word_score)
                word_rel_score.append([w, word_score])
            # explainable_terms list contains all the explainable terms of a document at index doc.
            explainable_terms = []
            for word_index in range(0, len(word_rel_score)):

                # Normalise the cosine score of the words with respect to the cosine score of the word having maximum
                # relevance to the concept representation of the query. 
                word_rel_score[word_index][1] = round(word_rel_score[word_index][1] / max_word_score, 4)
                # Find all the words with a cosine score higher than 50% of the top-scoring word.
                if word_rel_score[word_index][1] > explainable_threshold * max_word_score:
                    if lemmatiser:
                        values = set()
                        try:
                            for element in reverse_lem[word_rel_score[word_index][0]]:
                                values.add(element)
                            if values is not None:
                                for v in values:
                                    if v in terms:
                                        explainable_terms.extend([(v, word_rel_score[word_index][1])])
                        except:
                            continue
                    else:
                        # Extract all the explainable terms of the document at index doc and add it to 
                        # explainable_terms list.
                        explainable_terms.append(tuple(word_rel_score[word_index]))
            # Contains a list of all the explainable terms in all the documents with respect to a query at index q.
            print("Explainable Terms: ",explainable_terms)
            per_query_explainability_list.append(explainable_terms)
        explainability_list.append(per_query_explainability_list)

    return A, explainability_list
