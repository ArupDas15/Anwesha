import SearchBar from "./SearchBar";
import './Header.css';


function Header({modelType,setModelType,searchQuery,setSearchQuery,onSearchSubmit,setLemmatiser,lemmatiser}) {
  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light">
      <div className="container-fluid">
        <SearchBar modelType = {modelType} lemmatiser={lemmatiser} setLemmatiser={setLemmatiser} setModelType = {setModelType} searchQuery={searchQuery} setSearchQuery={setSearchQuery} onSubmit={onSearchSubmit} />
      </div>
    </nav>
  );
}

export default Header ;
