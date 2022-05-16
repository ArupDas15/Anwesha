from json import load
import numpy as np
import time
import sys

from helper import read_train_data, load_train_data, load_concept_data, read_concept_data
import lsa
import tfidf
import esa
import os

class SearchEngine:

    def __loadModelsRequirements(self, load=True):
        if load:
            self.docs, self.file_paths, self.dids = load_train_data(
                self.datasetPath)
            self.c_docs, self.c_file_paths, self.c_dids = load_concept_data(
                self.conceptDatasetPath)
            self.TFIDF_vectorizer, self.tfidf_matrix, self.TFIDF_vectorizer_lem, self.tfidf_matrix_lem = tfidf.load_tfidf()
            self.LSA_vectorizer, self.LSA_svd_transformer, self.svd_model, self.svd_model_lem, self.LSA_dvecs, self.LSA_vectorizer_lem, self.LSA_svd_transformer_lem, self.LSA_dvecs_lem = lsa.load_LSA()
            self.c_vectorizer, self.c_tfidf_matrix, self.c_vectorizer_lem, self.c_tfidf_matrix_lem, self.doc_concept_matrix, self.doc_concept_matrix_lem = esa.load_ESA()
            # self.c_vectorizer, self.c_tfidf_matrix, self.doc_concept_matrix = esa.load_ESA()

        else:
            self.docs, self.file_paths, self.dids = read_train_data(
                self.datasetPath)
            # self.docs, self.file_paths, self.dids = load_train_data(self.datasetPath)
            self.c_docs, self.c_file_paths, self.c_dids = read_concept_data(
                self.conceptDatasetPath, save_path=False)
            self.TFIDF_vectorizer, self.tfidf_matrix = tfidf.set_up_TFIDF(
                self.docs, lemmatiser=True, save_model=False)
            # self.LSA_vectorizer, self.LSA_svd_transformer, self.svd_model, self.LSA_dvecs = lsa.set_up_LSA(
            #     self.docs, rank=600, lemmatiser=False, save_model=False)
            self.c_vectorizer, self.c_tfidf_matrix, self.doc_concept_matrix = esa.set_up_ESA(
                self.c_docs, self.TFIDF_vectorizer, self.tfidf_matrix, lemmatiser=True, save_model=True)

        print("THE REQUIREMENTS HAVE BEEN LOADED")

    def __rank_results_lsa(self, A, k, file_paths, dids, docs, explainability_list):
        pdl = []
        x = np.argsort(A[0]).T[::-1][:k]
        index = 0
        for y in x:
            if index < k:
                if A[0][y] > 0:
                    pdl.append(tuple(
                        (file_paths[dids[y][0]], docs[dids[y][0]], dids[y][1], A[0][y], explainability_list[0][index])))
            index = index + 1
        return pdl

    def __rank_results_tfidf(self, A, k, file_paths, dids, docs, explainability_list):
        pdl = []
        x = np.argsort(A[0]).T[::-1][:k]
        index = 0
        for y in x:
            if index < k:
                if A[0][y] > 0:
                    pdl.append(tuple(
                        (file_paths[dids[y][0]], docs[dids[y][0]], dids[y][1], A[0][y], explainability_list[0][index])))
            index = index + 1

        return pdl

    def __init__(self, datasetPath="Lemmatization/Lemmatization", conceptDatasetPath="Lemmatization/Wikipedia_Concept_Dataset_lemmatized"):
        # initialization
        self.datasetPath = datasetPath
        self.conceptDatasetPath = conceptDatasetPath

        self.__loadModelsRequirements(load=True)

    def model_tfidf(self, query, lemmatiser=False):

        # TODO THE FORMAT OF IT
        print("#TFIDF without QE and lemmatiser= ", lemmatiser)
        start_time = time.time()
        pdl = []
        relevance_score = []
        if lemmatiser == False:
            A, explainability_list = tfidf.tfidf(vectorizer=self.TFIDF_vectorizer, tfidf_matrix=self.tfidf_matrix,
                                                 q=query, k=10, docs=self.docs, qe=False, lemmatiser=lemmatiser)
        else:
            A, explainability_list = tfidf.tfidf(vectorizer=self.TFIDF_vectorizer_lem,
                                                 tfidf_matrix=self.tfidf_matrix_lem,
                                                 q=query, k=10, docs=self.docs, qe=False, lemmatiser=lemmatiser)
        res = self.__rank_results_tfidf(
            A, 10, self.file_paths, self.dids, self.docs, explainability_list)
        dataToSend = {
            "responseData": {
                "results": [],
                "timeTaken": "",
                "totalResults": "",
            },
        }
        for i in range(0, len(res)):
            document = {
                "title": "",
                "url": "",
                "id": "",
                "content": "",
                "synopsis": "",
                "score": "",
                "explainibity": []
            }
            doc_lines = res[i][1].split("\n")
            doc_title = doc_lines[0]
            doc_content = "\n".join(doc_lines[1:])

            document["title"] = doc_title
            document["id"] = res[i][2]
            pdl.append(int(res[i][2]))
            document["url"] = res[i][0]
            document["content"] = doc_content
            document["synopsis"] = doc_content[:90]
            document["score"] = round(res[i][3], 5)
            relevance_score.append(round(res[i][3], 5))
            document["explainibity"] = res[i][4]
            # print("Document ID: ", res[i][2],"\nURL: ",res[i][0],"\nKey Terms: ",res[i][4])
            dataToSend["responseData"]["results"].append(document)

        end_time = time.time()
        dataToSend["responseData"]["totalResults"] = len(res)

        dataToSend["responseData"]["timeTaken"] = round(
            end_time - start_time, 2)
        if lemmatiser == False:
            filewrite = open(file=os.path.join(os.getcwd(), "IR_result.txt"), mode="w",
                             encoding='utf-8',
                             errors='ignore')
        else:
            filewrite = open(file=os.path.join(os.getcwd(), "IR_result.txt"), mode="a",
                             encoding='utf-8',
                             errors='ignore')
        filewrite.write(str("#TFIDF without QE and lemmatiser= " + str(lemmatiser)) + "\n")
        filewrite.write(query + "\n" + "\n")
        filewrite.write(str(pdl) + "\n")
        filewrite.write(str(relevance_score))
        filewrite.write("\n\n")
        filewrite.close()
        return dataToSend

    def model_lsa(self, query, lemmatiser=False):
        pdl = []
        relevance_score = []
        print("#LSA without QE and lemmatiser = ", lemmatiser)
        start_time = time.time()
        if lemmatiser == False:
            A, explainability_list = lsa.lsa(vectorizer=self.LSA_vectorizer, svd_transformer=self.LSA_svd_transformer, svd_model=self.svd_model,
                                             dvecs=self.LSA_dvecs, q=query, k=10, qe=False, lemmatiser=lemmatiser, docs=self.docs)
        else:
            A, explainability_list = lsa.lsa(vectorizer=self.LSA_vectorizer_lem, svd_transformer=self.LSA_svd_transformer_lem, svd_model=self.svd_model_lem,
                                             dvecs=self.LSA_dvecs_lem, q=query, k=10, qe=False, lemmatiser=lemmatiser, docs=self.docs)
        res = self.__rank_results_lsa(
            A, 10, self.file_paths, self.dids, self.docs, explainability_list)
        dataToSend = {
            "responseData": {
                "results": [],
                "timeTaken": "",
                "totalResults": "",
            },
        }
        for i in range(0, len(res)):
            document = {
                "title": "",
                "url": "",
                "id": "",
                "content": "",
                "synopsis": "",
                "score": "",
                "explainibity": []
            }
            doc_lines = res[i][1].split("\n")
            doc_title = doc_lines[0]
            doc_content = "\n".join(doc_lines[1:])

            document["title"] = doc_title
            document["id"] = res[i][2]
            pdl.append(int(res[i][2]))
            document["url"] = res[i][0]
            document["content"] = doc_content
            document["synopsis"] = doc_content[:90]
            document["score"] = round(res[i][3], 2)
            relevance_score.append(round(res[i][3], 5))
            document["explainibity"] = res[i][4]
            dataToSend["responseData"]["results"].append(document)

        end_time = time.time()
        dataToSend["responseData"]["totalResults"] = len(res)

        dataToSend["responseData"]["timeTaken"] = round(
            end_time - start_time, 2)
        filewrite = open(file=os.path.join(os.getcwd(), "IR_result.txt"), mode="a",
                         encoding='utf-8',
                         errors='ignore')
        filewrite.write(str("LSA without QE and lemmatiser = " + str(lemmatiser)) + "\n")
        filewrite.write(query + "\n" + "\n")
        filewrite.write(str(pdl) + "\n")
        filewrite.write(str(relevance_score))
        filewrite.write("\n\n")
        filewrite.close()
        return dataToSend

    def model_tfidf_qe(self, query, lemmatiser=True):
        pdl = []
        relevance_score = []
        print("#TFIDF with QE and lemmatiser = ", lemmatiser)
        start_time = time.time()
        if lemmatiser == False:
            A, explainability_list = tfidf.tfidf(vectorizer=self.TFIDF_vectorizer, tfidf_matrix=self.tfidf_matrix,
                                                 q=query, docs=self.docs, k=10, qe=True, lemmatiser=lemmatiser)
        else:
            A, explainability_list = tfidf.tfidf(vectorizer=self.TFIDF_vectorizer_lem,
                                                 tfidf_matrix=self.tfidf_matrix_lem,
                                                 q=query, docs=self.docs, k=10, qe=True, lemmatiser=lemmatiser)
        res = self.__rank_results_tfidf(
            A, 10, self.file_paths, self.dids, self.docs, explainability_list)
        dataToSend = {
            "responseData": {
                "results": [],
                "timeTaken": "",
                "totalResults": "",
            },
        }
        for i in range(0, len(res)):
            document = {
                "title": "",
                "url": "",
                "id": "",
                "content": "",
                "synopsis": "",
                "score": "",
                "explainibity": []
            }
            doc_lines = res[i][1].split("\n")
            doc_title = doc_lines[0]
            doc_content = "\n".join(doc_lines[1:])

            document["title"] = doc_title
            document["id"] = res[i][2]
            pdl.append(int(res[i][2]))
            document["url"] = res[i][0]
            document["content"] = doc_content
            document["synopsis"] = doc_content[:90]
            document["score"] = round(res[i][3], 2)
            relevance_score.append(round(res[i][3], 5))
            document["explainibity"] = res[i][4]
            dataToSend["responseData"]["results"].append(document)

        end_time = time.time()
        dataToSend["responseData"]["totalResults"] = len(res)

        dataToSend["responseData"]["timeTaken"] = round(
            end_time - start_time, 2)
        filewrite = open(file=os.path.join(os.getcwd(), "IR_result.txt"), mode="a",
                         encoding='utf-8',
                         errors='ignore')
        filewrite.write(str("#TFIDF with QE and lemmatiser = " + str(lemmatiser)) + "\n")
        filewrite.write(query + "\n" + "\n")
        filewrite.write(str(pdl) + "\n")
        filewrite.write(str(relevance_score))
        filewrite.write("\n\n")
        filewrite.close()
        return dataToSend

    def model_esa(self, query, lemmatiser=False):
        print("#ESA without QE and lemmatiser= ", lemmatiser)
        start_time = time.time()
        pdl = []
        relevance_score = []
        if lemmatiser == False:
            A, explainability_list = esa.esa(tr_tfidf_matrix=self.tfidf_matrix, vectorizer=self.TFIDF_vectorizer, c_vectorizer=self.c_vectorizer, c_tfidf_matrix=self.c_tfidf_matrix, doc_concept_matrix=self.doc_concept_matrix,
                                             q=query, k=10, docs=self.docs, qe=False, lemmatiser=lemmatiser)
        else:
            A, explainability_list = esa.esa(tr_tfidf_matrix=self.tfidf_matrix_lem, vectorizer=self.TFIDF_vectorizer_lem,
                                             c_vectorizer=self.c_vectorizer_lem, c_tfidf_matrix=self.c_tfidf_matrix_lem, doc_concept_matrix=self.doc_concept_matrix_lem,
                                             q=query, k=10, docs=self.docs, qe=False, lemmatiser=lemmatiser)
        res = self.__rank_results_tfidf(
            A, 10, self.file_paths, self.dids, self.docs, explainability_list)
        dataToSend = {
            "responseData": {
                "results": [],
                "timeTaken": "",
                "totalResults": "",
            },
        }
        for i in range(0, len(res)):
            document = {
                "title": "",
                "url": "",
                "id": "",
                "content": "",
                "synopsis": "",
                "score": "",
                "explainibity": []
            }
            doc_lines = res[i][1].split("\n")
            doc_title = doc_lines[0]
            doc_content = "\n".join(doc_lines[1:])

            document["title"] = doc_title
            document["id"] = res[i][2]
            pdl.append(int(res[i][2]))
            document["url"] = res[i][0]
            document["content"] = doc_content
            document["synopsis"] = doc_content[:90]
            document["score"] = round(res[i][3], 5)
            relevance_score.append(round(res[i][3], 5))
            document["explainibity"] = res[i][4]
            # print("Document ID: ", res[i][2],"\nURL: ",res[i][0],"\nKey Terms: ",res[i][4])
            dataToSend["responseData"]["results"].append(document)

        end_time = time.time()
        dataToSend["responseData"]["totalResults"] = len(res)

        dataToSend["responseData"]["timeTaken"] = round(
            end_time - start_time, 2)
        filewrite = open(file=os.path.join(os.getcwd(), "IR_result.txt"), mode="a",
                         encoding='utf-8',
                         errors='ignore')
        filewrite.write(str("LSA with QE and lemmatiser = " + str(lemmatiser)) + "\n")
        filewrite.write(query + "\n" + "\n")
        filewrite.write(str(pdl)+"\n")
        filewrite.write(str(relevance_score) + "\n")
        filewrite.write("\n\n")
        filewrite.close()
        print(pdl)
        print(relevance_score)
        return dataToSend

    def model_esa_qe(self, query, lemmatiser=False):
        print("#ESA with QE and lemmatiser= ", lemmatiser)
        start_time = time.time()
        pdl = []
        relevance_score = []
        if lemmatiser == False:
            A, explainability_list = esa.esa(tr_tfidf_matrix=self.tfidf_matrix, vectorizer=self.TFIDF_vectorizer, c_vectorizer=self.c_vectorizer, c_tfidf_matrix=self.c_tfidf_matrix, doc_concept_matrix=self.doc_concept_matrix,
                                             q=query, k=10, docs=self.docs, qe=True, lemmatiser=lemmatiser)
        else:
            A, explainability_list = esa.esa(tr_tfidf_matrix=self.tfidf_matrix_lem, vectorizer=self.TFIDF_vectorizer_lem,
                                             c_vectorizer=self.c_vectorizer_lem, c_tfidf_matrix=self.c_tfidf_matrix_lem, doc_concept_matrix=self.doc_concept_matrix_lem,
                                             q=query, k=10, docs=self.docs, qe=True, lemmatiser=lemmatiser)
        res = self.__rank_results_tfidf(
            A, 10, self.file_paths, self.dids, self.docs, explainability_list)
        dataToSend = {
            "responseData": {
                "results": [],
                "timeTaken": "",
                "totalResults": "",
            },
        }
        for i in range(0, len(res)):
            document = {
                "title": "",
                "url": "",
                "id": "",
                "content": "",
                "synopsis": "",
                "score": "",
                "explainibity": []
            }
            doc_lines = res[i][1].split("\n")
            doc_title = doc_lines[0]
            doc_content = "\n".join(doc_lines[1:])

            document["title"] = doc_title
            document["id"] = res[i][2]
            pdl.append(int(res[i][2]))
            document["url"] = res[i][0]
            document["content"] = doc_content
            document["synopsis"] = doc_content[:90]
            document["score"] = round(res[i][3], 5)
            relevance_score.append(round(res[i][3], 5))
            document["explainibity"] = res[i][4]
            # print("Document ID: ", res[i][2],"\nURL: ",res[i][0],"\nKey Terms: ",res[i][4])
            dataToSend["responseData"]["results"].append(document)

        end_time = time.time()
        dataToSend["responseData"]["totalResults"] = len(res)

        dataToSend["responseData"]["timeTaken"] = round(
            end_time - start_time, 2)
        return dataToSend

    def model_lsa_qe(self, query, lemmatiser=False):
        print("#LSA with query expansion and lemmatiser = ", lemmatiser)
        pdl = []
        relevance_score = []
        start_time = time.time()
        if lemmatiser == False:
            A, explainability_list = lsa.lsa(vectorizer=self.LSA_vectorizer, svd_transformer=self.LSA_svd_transformer, svd_model=self.svd_model,
                                             dvecs=self.LSA_dvecs, q=query, k=10, qe=True, lemmatiser=lemmatiser, docs=self.docs)
        else:
            A, explainability_list = lsa.lsa(vectorizer=self.LSA_vectorizer_lem, svd_transformer=self.LSA_svd_transformer_lem, svd_model=self.svd_model_lem,
                                             dvecs=self.LSA_dvecs_lem, q=query, k=10, qe=True, lemmatiser=lemmatiser, docs=self.docs)
        res = self.__rank_results_lsa(
            A, 10, self.file_paths, self.dids, self.docs, explainability_list)

        dataToSend = {
            "responseData": {
                "results": [],
                "timeTaken": "",
                "totalResults": "",
            },
        }
        for i in range(0, len(res)):
            document = {
                "title": "",
                "url": "",
                "id": "",
                "content": "",
                "synopsis": "",
                "score": "",
                "explainibity": []
            }
            doc_lines = res[i][1].split("\n")
            doc_title = doc_lines[0]
            doc_content = "\n".join(doc_lines[1:])

            document["title"] = doc_title
            document["id"] = res[i][2]
            pdl.append(int(res[i][2]))
            document["url"] = res[i][0]
            document["content"] = doc_content
            document["synopsis"] = doc_content[:90]
            document["score"] = round(res[i][3], 2)
            relevance_score.append(round(res[i][3], 5))
            document["explainibity"] = res[i][4]
            dataToSend["responseData"]["results"].append(document)

        end_time = time.time()
        dataToSend["responseData"]["totalResults"] = len(res)

        dataToSend["responseData"]["timeTaken"] = round(
            end_time - start_time, 2)
        filewrite = open(file=os.path.join(os.getcwd(), "IR_result.txt"), mode="a",
                         encoding='utf-8',
                         errors='ignore')
        filewrite.write(str("LSA with QE and lemmatiser = " + str(lemmatiser)) + "\n")
        filewrite.write(query + "\n" + "\n")
        filewrite.write(str(pdl))
        filewrite.write(str(relevance_score)+"\n")
        filewrite.write("\n\n")
        filewrite.close()
        print(pdl)
        print(relevance_score)
        return dataToSend


def main():
    searchEngineObject = SearchEngine()
    q = ' '.join(sys.argv[1:])


#     searchEngineObject.model_tfidf(q)
#     searchEngineObject.model_tfidf_qe(q)
#     searchEngineObject.model_lsa(q)
#     searchEngineObject.model_lsa_qe(q)


if __name__ == '__main__':
    main()