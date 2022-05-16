import SearchBar from "./SearchBar";


function Home({modelType,setModelType,searchQuery,setSearchQuery,onSearchSubmit,setLemmatiser,lemmatiser}) {

  return (
    <div className="customWrap" style={{'top': '50%'}}>
      <SearchBar modelType = {modelType} setModelType = {setModelType} lemmatiser={lemmatiser} setLemmatiser={setLemmatiser} searchQuery={searchQuery} setSearchQuery={setSearchQuery} onSubmit={onSearchSubmit} />
    </div>
  );
}

export default Home;
