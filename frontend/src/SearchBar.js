import React, { useState } from "react";
import "./SearchBar.css";
import { ReactTransliterate } from "react-transliterate";
//import "react-transliterate/dist/index.css";

function SearchBar({ modelType, setModelType, searchQuery, setSearchQuery, onSubmit, setLemmatiser, lemmatiser }) {

  const [text, setText] = useState("");

  return (
    <form
      action="/search"
      method="get"
      className="customsearchbox"
      onSubmit={(e) => onSubmit(e)}
    >

      <ReactTransliterate
        value={searchQuery}
        onChangeText={(text) => {
          setText(text);
          setSearchQuery(text)
        }}
        lang="bn"
        placeholder="অনুসন্ধান..."
        className="customsearchTerm"
      />

      {/* <input
        type="text"
        value={searchQuery}
        placeholder="অনুসন্ধান..."
        name="q"
        onInput={(e) => setSearchQuery(e.target.value)}
        className="customsearchTerm"
      /> */}
      <select className="modelOption" value={modelType} onChange={(e) => setModelType(e.target.value)}>
        <option value="model_0" >TFIDF WITHOUT QUERY EXPANSION</option>
        <option value="model_1" >TFIDF WITH QUERY EXPANSION</option>
        <option value="model_2" >LSA </option>
        {/*<option value="model_3" >LSA WITH QUERY EXPANSION</option>*/}
        <option value="model_4" >ESA </option>
        {/*<option value="model_5" >ESA WITH QUERY EXPANSION</option>*/}
      </select>

      <input className="lemmatiser" type="checkbox" id="lemmatisation" name="lemmatisation" value="lemmatisation" checked={lemmatiser} onChange={(e) => setLemmatiser(e.target.checked)} />

      <button type="submit" className="searchButton">
        <i className="fa fa-search"></i>
      </button>
    </form>
  );
}

export default SearchBar;