import { useLocation } from 'react-router-dom'
import './ArticlePage.css';
import Highlighter from "react-highlight-words";

function ArticlePage() {
    const location = useLocation()
    const { data } = location.state
    const imp_terms = data.explainibity.map(x => x[0].trim())
    console.log(imp_terms)


    const findChunksWordsonly = () => {
        const searchWords = imp_terms;
        const textToHighlight = data.content

        return searchWords
            .filter(searchWord => searchWord) // Remove empty words
            .reduce((chunks, searchWord) => {


                const regex = new RegExp(searchWord,'gi')
                //console.log(regex,searchWord)
                const pattern = /[.,/#!$%^&*;:{|}=\-_`~()\s]/g
                let match
                while ((match = regex.exec(textToHighlight))) {
                    let start = match.index
                    let end = regex.lastIndex
                    // We do not return zero-length matches
                    //console.log(start,textToHighlight.substring(start,end))
                    //console.log(start,end)
                    if (end > start && (start-1 < 0  ||textToHighlight[start-1].match(pattern)) && (end >= textToHighlight.length || textToHighlight[end].match(pattern) || textToHighlight[end].charCodeAt(0) === 2404)) {
                        chunks.push({ highlight: false, start, end })
                    }

                    // Prevent browsers like Firefox from getting stuck in an infinite loop
                    // See http://www.regexguru.com/2008/04/watch-out-for-zero-length-matches/
                    if (match.index === regex.lastIndex) {
                        regex.lastIndex++
                    }
                }

                return chunks
            }, [])

    }



    return (

        <div className="article">
            <h3>{data.title}</h3>
            {/* <p>{page_content}</p> */}
            <Highlighter
                highlightClassName="highlight"
                searchWords={imp_terms}
                autoEscape={true}
                textToHighlight={data.content}
                findChunks={findChunksWordsonly}
            />
        </div>
    )
}

export default ArticlePage;