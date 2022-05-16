import { Link } from "react-router-dom";



function Responses({ resultsReceived }) {

  const listItems = resultsReceived['responseData'] ? (resultsReceived['responseData']['results'].map((response) => {
    const imp_terms = response.explainibity.map(x => x[0])

    return (
      <div className="row border" key={response.url}>
        <p><b>Score</b> : {response.score}</p>
        <p>
          <b>Doc number </b>: {response.id}
        </p>
        <p>
          <b>Title </b>:
          <Link to={{ pathname: `/article/${response.id}`, state: { data: response } }} >{response.title} </Link>
        </p>
        <p><b>Key terms</b>: {imp_terms.slice(0,Math.min(7,imp_terms.length)).join(" ,") }{imp_terms.length > 7 ? '...': null}</p>
        <p>{response.synopsis}...</p>
        
      </div>
    )
  })) : <div></div>

  return (
    <div className="container-fluid">
      {resultsReceived['responseData'] ? <p><small className="text-muted">প্রায় {resultsReceived['responseData']['totalResults']} টি ফলাফল ({resultsReceived['responseData']['timeTaken']} secs)</small></p> : <p></p>}
      
      {listItems}
    </div>
  );
}

export default Responses;