<div align="center">
	<h1><b><i>Anwesha: A Tool for Semantic Search in Bangla</i></b></h1>
	<a href="https://medium.com/">Blog</a> |
	<a href="https://www.altnlp.org/">Paper</a> 
</div>

## Installation
<details><summary>Click to expand </summary>
For details on how to run Anwesha locally, kindly go through the document over <a href="https://github.com/ArupDas15/Bengali_Search_Engine/blob/main/RUN_CODE_INSTRUCTIONS.md">here</a>.
</details>

## Folder Structure
```

IndicTrans
│   .gitignore
│   apply_bpe_traindevtest_notag.sh         # apply bpe for joint vocab (Train, dev and test)
│   apply_single_bpe_traindevtest_notag.sh  # apply bpe for seperate vocab   (Train, dev and test)
│   binarize_training_exp.sh                # binarize the training data after preprocessing for fairseq-training
│   compute_bleu.sh                         # Compute blue scores with postprocessing after translating with `joint_translate.sh`
│   indictrans_fairseq_inference.ipynb      # colab example to show how to use model for inference
│   indicTrans_Finetuning.ipynb             # colab example to show how to use model for finetuning on custom domain data
│   joint_translate.sh                      # used for inference (see colab inference notebook for more details on usage)
│   learn_bpe.sh                            # learning joint bpe on preprocessed text
│   learn_single_bpe.sh                     # learning seperate bpe on preprocessed text
│   LICENSE
│   prepare_data.sh                         # prepare data given an experiment dir (this does preprocessing,
│                                           # building vocab, binarization ) for bilingual training
│   prepare_data_joint_training.sh          # prepare data given an experiment dir (this does preprocessing,
│                                           # building vocab, binarization ) for joint training
│   README.md
│
├───legacy                                  # old unused scripts
├───model_configs                           # custom model configrations are stored here
│       custom_transformer.py               # contains custom 4x transformer models
│       __init__.py
├───inference
│       custom_interactive.py               # for python wrapper around fairseq-interactive
│       engine.py                           # python interface for model inference
└───scripts                                 # stores python scripts that are used by other bash scripts
    │   add_joint_tags_translate.py         # add lang tags to the processed training data for bilingual training
    │   add_tags_translate.py               # add lang tags to the processed training data for joint training
    │   clean_vocab.py                      # clean vocabulary after building with subword_nmt
    │   concat_joint_data.py                # concatenates lang pair data and creates text files to keep track
    │                                       # of number of lines in each lang pair.
    │   extract_non_english_pairs.py        # Mining Indic to Indic pairs from english centric corpus
    │   postprocess_translate.py            # Postprocesses translations
    │   preprocess_translate.py             # Preprocess translations and for script conversion (from indic to devnagiri)
    │   remove_large_sentences.py           # to remove large sentences from training data
    └───remove_train_devtest_overlaps.py    # Finds and removes overlaped data of train with dev and test sets
```


## Citing

If you are using any of the resources, please cite the following article:
```
Bibtex citation to be updated.
```
### Research Team

- Arup Das, <sub>([AIDB](http://www.cse.iitm.ac.in/lab_details.php?arg=MQ==), [IITM](https://www.iitm.ac.in))</sub>
- Bibekananda Kundu, <sub>([CDAC](https://www.cdac.in/)</sub>
- Lokasis Ghorai, <sub>(([AIDB](http://www.cse.iitm.ac.in/lab_details.php?arg=MQ==), [IITM](https://www.iitm.ac.in))</sub>
- Arjun Kumar Gupta, <sub>([AIDB](http://www.cse.iitm.ac.in/lab_details.php?arg=MQ==), [IITM](https://www.iitm.ac.in))</sub>
- Sutanu Chakraborti, <sub>([AIDB](http://www.cse.iitm.ac.in/lab_details.php?arg=MQ==), [IITM](https://www.iitm.ac.in))</sub>
|   | Name		      		| Contact                                                 |	LinkedIn/ Website
|---|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| 1 | Arup Das, <sub>([AIDB](http://www.cse.iitm.ac.in/lab_details.php?arg=MQ==), [IITM](https://www.iitm.ac.in))</sub>        		| (mailto:cs20s016@smail.iitm.ac.in))                     | https://www.linkedin.com/in/arup-das-90033a153/
| 2 | Bibekananda Kundu, <sub>([CDAC](https://www.cdac.in/)</sub>     | (mailto:bibekananda.kundu@gmail.com))                   |	https://www.linkedin.com/in/bibekananda-kundu-51205434/
| 3 | Lokasis Ghorai, <sub>(([AIDB](http://www.cse.iitm.ac.in/lab_details.php?arg=MQ==), [IITM](https://www.iitm.ac.in))</sub> 		| (mailto:cs20m033@smail.iitm.ac.in))                     |	https://www.linkedin.com/in/lokasis-ghorai-6b073a146/
| 4 | Arjun Kumar Gupta, <sub>([AIDB](http://www.cse.iitm.ac.in/lab_details.php?arg=MQ==), [IITM](https://www.iitm.ac.in))</sub>   	| (mailto:cs20m015@smail.iitm.ac.in))                     |	https://www.linkedin.com/in/arjun-kumar-gupta-10898117a/
| 5 | Sutanu Chakraborti, <sub>([AIDB](http://www.cse.iitm.ac.in/lab_details.php?arg=MQ==), [IITM](https://www.iitm.ac.in))</sub>  	| (mailto:sutanuc@cse.iitm.ac.in))						  |	http://www.cse.iitm.ac.in/profile.php?arg=Ng==

