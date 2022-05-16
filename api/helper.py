import os
import pickle
import re
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
from bnunicodenormalizer import Normalizer

# initialize
bnorm = Normalizer()


def read_train_data(directory_path,save_path=False):
    index = 0
    docs = []
    dids = []
    file_paths = []
    factory = IndicNormalizerFactory()
    normalizer = factory.get_normalizer("bn", remove_nuktas=False)

    for dirpath, dirnames, filenames in os.walk(directory_path):
        for file_name in filenames:
            # Get the absolute file path
            file_path = os.path.join(os.getcwd(), str(dirpath), str(file_name))
            # Create a file object.
            fileObject = open(file_path, "r+", encoding='utf-8', errors='ignore')
            # Extract the text from the file.
            text = fileObject.read()
            text = normalizer.normalize(text)
            text = bnorm(text).get('normalized')
            docs.append(text)
            # using re.findall() we extract all the numbers from the string
            temp = re.findall(r'\d+', file_name)
            doc_num = ''.join(temp)
            dids.append(tuple((index, doc_num)))
            file_paths.append(file_path)
            index = index + 1

    if save_path:
        outfile = open(os.path.join('SavedModels', 'file_paths'), 'wb')
        pickle.dump(file_paths, outfile)
        outfile.close()

        outfile = open(os.path.join('SavedModels', 'dids'), 'wb')
        pickle.dump(dids, outfile)
        outfile.close()

        file1 = open(os.path.join('SavedModels', "OSSep.txt"), "w")
        file1.write(str(os.sep))
        file1.close()

    return docs, file_paths, dids


def load_train_data(directory_path):
    docs = []

    infile = open(os.path.join('SavedModels', 'dids'), 'rb')
    dids = pickle.load(infile)
    infile.close()

    infile = open(os.path.join('SavedModels', 'file_paths'), 'rb')
    file_paths = pickle.load(infile)
    infile.close()

    file1 = open(os.path.join('SavedModels', "OSSep.txt"), "r")
    sep_delimitter = file1.read()
    file1.close()

    for file_name in file_paths:
        # Get the absolute file path
        file_path = file_name.replace(sep_delimitter, os.sep)
        # Create a file object.
        fileObject = open(file_path, "r+", encoding='utf-8', errors='ignore')
        # Extract the text from the file.
        text = fileObject.read()
        docs.append(text)

    return docs, file_paths, dids


def read_concept_data(directory_path,save_path=False):
    index = 0
    c_docs = []
    c_dids = []
    c_file_paths = []
    factory = IndicNormalizerFactory()
    normalizer = factory.get_normalizer("bn", remove_nuktas=False)
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for file_name in filenames:
            # Get the absolute file path
            file_path = os.path.join(str(dirpath), str(file_name))
            c_file_paths.append(file_path)
            # Create a file object.
            fileObject = open(file_path, "r+", encoding='utf-8', errors='ignore')
            # Extract the text from the file.
            text = fileObject.read()
            text = normalizer.normalize(text)
            text = bnorm(text).get('normalized')
            c_docs.append(text)
            # using re.findall() we extract all the numbers from the string
            temp = re.findall(r'\d+', file_name)
            c_doc_num = ''.join(temp)
            c_dids.append(tuple((index, c_doc_num)))
            index += 1
    if save_path:
        outfile = open(os.path.join('SavedModels', 'c_file_paths'), 'wb')
        pickle.dump(c_file_paths, outfile)
        outfile.close()

        outfile = open(os.path.join('SavedModels', 'c_dids'), 'wb')
        pickle.dump(c_dids, outfile)
        outfile.close()


    return c_docs, c_file_paths,c_dids


def load_concept_data(directory_path):
    c_docs = []

    infile = open(os.path.join('SavedModels', 'c_dids'), 'rb')
    c_dids = pickle.load(infile)
    infile.close()

    infile = open(os.path.join('SavedModels', 'c_file_paths'), 'rb')
    c_file_paths = pickle.load(infile)
    infile.close()

    file1 = open(os.path.join('SavedModels', "OSSep.txt"), "r")
    sep_delimitter = file1.read()
    file1.close()

    for file_name in c_file_paths:
        # Get the absolute file path
        c_file_path = file_name.replace(sep_delimitter, os.sep)
        # Create a file object.
        fileObject = open(c_file_path, "r+", encoding='utf-8', errors='ignore')
        # Extract the text from the file.
        text = fileObject.read()
        c_docs.append(text)

    return c_docs, c_file_paths, c_dids