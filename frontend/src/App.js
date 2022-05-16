import { Route } from "react-router-dom";
import { useHistory } from "react-router";
import { useState,useEffect } from "react";
import axios from "axios";

import Home from "./Home";
import Results from "./Results";
import { BACKEND_URL } from "./CONSTANTS";

import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';


import "./App.css";
import ArticlePage from "./ArticlePage";



function App() {
  const [searchQuery, setSearchQuery] = useState("");
  const [resultsReceived,setResultsReceived] = useState({})
  const [loading,setLoading] = useState(false)
  const [modelType,setModelType] = useState("model_0")
  const [lemmatiser,setLemmatiser] = useState(false)

  const history = useHistory()

  useEffect(() => {
    window.addEventListener("beforeunload", alertUser);
    return () => {
      window.removeEventListener("beforeunload", alertUser);
    };
  }, []);
  const alertUser = (e) => {
    e.preventDefault();
    e.returnValue = ""
  };



  const onClickSearch = () => {
    const processed_query = searchQuery.replace(/\s{2,}/g, ' ').trim()
    setSearchQuery(processed_query)
    
    if(searchQuery !== ""){
      setLoading(true)
      axios
      .get(`${BACKEND_URL}/search?q=${processed_query}&m=${modelType}&lemmatiser=${lemmatiser}`)
      .then((response) => {
        if (response.status === 200) {

          setResultsReceived(response.data)
          setLoading(false)
          history.push(`/search?q=${processed_query}`)
        }
      }); 
    }else{
      toast("No search query!!!",{position: "top-center"})
    }
  }

  const onSearchSubmit = (e) => {
    e.preventDefault()
    const processed_query = searchQuery.replace(/\s{2,}/g, ' ').trim()
    setSearchQuery(processed_query)
    if(searchQuery !== ""){
      setLoading(true)
      axios
      .get(`${BACKEND_URL}/search?q=${processed_query}&m=${modelType}&lemmatiser=${lemmatiser}`)
      .then((response) => {
        if (response.status === 200) {

          setResultsReceived(response.data)
          setLoading(false)
          history.push(`/search?q=${processed_query}`)
        }
      }).catch(err =>{
        setLoading(false)
        toast("SERVER DOWN !!!")
        console.log("SERVER DOWN !!!")
      }); 
    }else{
      toast("No search query!!!",{position: "top-center"})
    }
    
  };

  return (
    
    <div className="App">
        {loading? (
            <div className="loading" />
        ) : null}
      <Route exact path="/">
        <Home
          modelType = {modelType}
          setModelType = {setModelType}
          setLemmatiser = {setLemmatiser}
          lemmatiser={lemmatiser}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onSearchSubmit={onSearchSubmit}
        />
      </Route>
      <Route path="/search">
        <Results
          modelType = {modelType}
          lemmatiser = {lemmatiser}
          setModelType = {setModelType}
          setLemmatiser = {setLemmatiser}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onSearchSubmit={onSearchSubmit}
          resultsReceived = {resultsReceived}
          onClickSearch = {onClickSearch}
        />
      </Route>
      <Route path='/article/:id'>
          <ArticlePage />
      </Route>
    </div>
  );
}

export default App;
