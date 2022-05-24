The below are the steps to locally run the Bangla Search Engine in a Windows 10 Operating System.

# STEPS TO RUN THE BANGLA SEARCH ENGINE:

1. Download Python: https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe and install it. 

![image](https://user-images.githubusercontent.com/37553488/152561667-caf16b00-4248-4c7e-9ac4-1b88212a3324.png)

![InstallPython](https://user-images.githubusercontent.com/37553488/152011384-3bfae798-dc57-423a-a9df-bc6b4dbb5318.PNG)
![InstallPythonComplete](https://user-images.githubusercontent.com/37553488/152011486-9c69de6a-8178-459f-9f30-97610c71797a.PNG)

You can verfy if the correct version of Python is added to the environment path of Windows 10 in Commond Prompt as shown below:

![image](https://user-images.githubusercontent.com/37553488/152561899-a81caa52-67b2-466d-91b9-00dfb0dad5aa.png)

2. Download Pycharm: https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC and install it.

3. Open Pycharm-> Get from VCS-> Provide the repository URL to clone: https://github.com/theindianwriter/Bengali-Search-Engine.git
Follow the steps given here to create a virtual environment: https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html#python_create_virtual_env

The base interpreter will be Python-3.8.10 the one you had installed in Step 1 as shown below.

![venv_2](https://user-images.githubusercontent.com/37553488/152014748-a92b295e-43bb-4c68-a405-a5555d537b86.PNG)

After clicking on Ok, you can verify the python version by typing the below in a terminal.
![image](https://user-images.githubusercontent.com/37553488/152015100-c965e109-8fde-4f21-bdc8-bd2e4ce28b62.png)

4. Follow this link to install npm in your local machine: https://www.geeksforgeeks.org/installation-of-node-js-on-windows/ 

5. Use pip command to install below libraries: 

      `pip install flask, flask-cors, git+https://github.com/riteshpanjwani/pyiwn@master#egg=pyiwn, scikit-learn, scipy, stopwordsiso, bnlp_toolkit, indic-nlp-library, nltk, python-dotenv, weighted-levenshtein, git+https://github.com/libindic/indic-trans.git, bnunicodenormalizer`


Open a python console and download the nltk stopwords as shown below:![download_nltk_stopwords](https://user-images.githubusercontent.com/37553488/152012048-b8f9c785-a725-4038-8244-f7ea2e342495.PNG)
6. Create a folder models under api directory and copy the files bn_ner.pkl (https://github.com/sagorbrur/bnlp/blob/master/model/bn_ner.pkl) and bn_pos.pkl (https://github.com/sagorbrur/bnlp/blob/master/model/bn_pos.pkl) 

   1. Under the SavedModels folder, download the svd_transformer.pkl file from https://drive.google.com/file/d/1WO3uGtHwrN5F5bo7agiQhLJXzyazj9cj/view?usp=sharing 

      1. First, Run the code in the backend. 

          8.1. Open a terminal. 

          8.2. <Path\ Bengali-Search-Engine> cd api (In my case, the path is C:\Users\Arup\PycharmProjects\ Bengali-Search-Engine) 
    
          8.3. Download the Train_Dataset from here: https://drive.google.com/file/d/1MGNgiWOx3zo-aFwNI5mdjvnrQaug9opG/view?usp=sharing. <br/> Extract it and store it into the api folder.

          8.4. cd Bangla_Spellchecker <br/>
               git clone https://github.com/yougov/fuzzy.git <br/>
               cd fuzzy <br/>
               Delete fuzzy.pyx and paste fuzzy.c file instead in src folder under fuzzy. <br/>
               Change line 32 from 'src/fuzzy.pyx' to 'src/fuzzy.c'. <br/>
               python setup.py install <br/>
               cd .. <br/>
               cd .. <br/>
 
          8.5. <Path\ Bengali-Search-Engine\api> flask run 
    
![backend_img1](https://user-images.githubusercontent.com/37553488/150490101-8668c797-db98-4281-81c5-d5c57c5fcec4.png)

    Once you see the message “THE REQUIREMENTS HAVE BEEN LOADED” you are good to start the frontend. 

9. Start the frontend code. 

    9.1. Open a terminal. 

    9.2. <Path\ Bengali-Search-Engine> cd frontend(In my case, the path is C:\Users\Arup\PycharmProjects\ Bengali-Search-Engine) 

    9.3. <Path\ Bengali-Search-Engine\frontend> npm install (This will create the node_modules folder for you.) 

    9.4. <Path\ Bengali-Search-Engine\frontend> npm start 
    
    ![frontend_img1](https://user-images.githubusercontent.com/37553488/150490705-9226d5fd-3fe9-4ad2-a8d0-7a3bd0800928.png)

NOTE: The lemmatised files of the dataset are available over here: https://drive.google.com/file/d/1bOPqbgNmBq1PDnQ2i096d3AfeAXToZhZ/view?usp=sharing

To make the web version operational follow the steps below: 
1. Sign up  and Download ngrok 
2. Perform ngrok authentication
3. First run the backend
for running backend.
-> run backend in your local machine
-> then run ngrok
    ngrok http  5000 -host-header="localhost:5000"
    You will get a https url:

    ```For e.g., Forwarding                    https://5a18-2401-4900-2348-abb7-4d1b-92be-5814-1175.ngrok.io -> http://localhost:5000```
    copy the url (here: https://5a18-2401-4900-2348-abb7-4d1b-92be-5814-1175.ngrok.io and send to person running running frontend)

4. The run frontend from another system. 
for running frontend:
-> make changes in App.js (in place where  axios.get is used replace 'http://127.0.0.1:5000' with https://5a18-2401-4900-2348-abb7-4d1b-92be-5814-1175.ngrok.io) and package.json (in place where "proxy": "http://127.0.0.1:5000" is used with "proxy": "https://5a18-2401-4900-2348-abb7-4d1b-92be-5814-1175.ngrok.io")
-> run frontend
-> then run ngrok
    ngrok http  3000 -host-header="localhost:3000"
    You will get a https url: similar to backend 

    ```For e.g., Forwarding               https://df52-202-142-96-145.ngrok.io-> http://localhost:3000```

Now finally share the link https://df52-202-142-96-145.ngrok.io as the link to the search engine. Meanwhile, keep both the frontend and the baclend running for service.

 