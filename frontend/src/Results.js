import Header from "./Header";
import Responses from "./Responses";


function Results({ modelType, setModelType, searchQuery, setSearchQuery, onSearchSubmit, resultsReceived, onClickSearch, setLemmatiser,lemmatiser }) {

  const handleSelectChange = (e) => {
    const id = e.target.id
    const searchQueryTerms = searchQuery.split(" ")
    searchQueryTerms[id] = e.target.value
    setSearchQuery(searchQueryTerms.join(" "))
  }

  console.log(resultsReceived)
  return (
    <div>
      <Header modelType={modelType} lemmatiser={lemmatiser} setLemmatiser={setLemmatiser} setModelType={setModelType} searchQuery={searchQuery} setSearchQuery={setSearchQuery} onSearchSubmit={onSearchSubmit} />
      <br />
      <div className="container-fluid">
        {resultsReceived["spellcheck"] && resultsReceived["spellcheck"]["correction_detected"] ? (<div>
          <label><p className="text-danger">আপনি কি মানে : </p> </label>
          {resultsReceived["spellcheck"]["query_terms"].map((term, index) => (
            resultsReceived["spellcheck"][term].length > 1 ? (<select name={term} id={index} key={index} onChange={handleSelectChange}>
              {resultsReceived["spellcheck"][term].map((candidate, index) => (
                <option value={candidate} key={index}> {candidate}
                </option>
              ))}
            </select>) : (<span>{term}{" "}</span>)
          ))}
        </div>) : null}
        {resultsReceived["spellcheck"] ? <p>
          <b className="text-primary ">এর জন্য ফলাফল দেখানো হচ্ছে :
          </b> {resultsReceived["spellcheck"]["query_terms"].join(" ")}
        </p> : null}
      </div>
      <Responses resultsReceived={resultsReceived} />
    </div>
  );
}

export default Results;
