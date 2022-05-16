import { useLocation } from 'react-router-dom'
import './ArticlePage.css';
import Highlighter from "react-highlight-words";

function ArticlePage() {
    const location = useLocation()
    const { data } = location.state
    const imp_terms = data.explainibity.map(x => x[0].trim())
    console.log(imp_terms)
    // const page_content = data.content.split(" ").map((item, id) => {

    //     const item_modified = item.replace(/[.,/#!$%^&*;:|'"{}=_`~()]/g, "")
    //     if (imp_terms.includes(item_modified)) {
    //         return <mark key={id}>{item}</mark>
    //     } else {
    //         return <small key={id}> {item} </small>
    //     }
    // })

    // const findChunksWordsonly = ()=> {
    //     const searchWords = imp_terms;
    //     const textToHighlight = data.content
    //     const chunks = [];
    //     const textLow = textToHighlight.toLowerCase();
    //     // Match at the beginning of each new word
    //     // New word start after whitespace or - (hyphen)
    //     const sep = /[$\|\s]+/;

    //     // Match at the beginning of each new word
    //     // New word start after whitespace or - (hyphen)
    //     const singleTextWords = textLow.split(sep);

    //     // It could be possible that there are multiple spaces between words
    //     // Hence we store the index (position) of each single word with textToHighlight
    //     let fromIndex = 0;
    //     const singleTextWordsWithPos = singleTextWords.map(s => {
    //       const indexInWord = textLow.indexOf(s, fromIndex);
    //       fromIndex = indexInWord;
    //       return {
    //         word: s,
    //         index: indexInWord
    //       };
    //     });

    //     // Add chunks for every searchWord
    //     searchWords.forEach(sw => {
    //       const swLow = sw.toLowerCase();
    //       // Do it for every single text word
    //       singleTextWordsWithPos.forEach(s => {
    //         if (s.word == swLow) {
    //           const start = s.index;
    //           const end = s.index + swLow.length;
    //           chunks.push({
    //             start,
    //             end
    //           });
    //         }
    //       });


    //     //   if (textLow.startsWith(swLow)) {
    //     //     const start = 0;
    //     //     const end = swLow.length;
    //     //     chunks.push({
    //     //       start,
    //     //       end
    //     //     });
    //     //   }
    //     });

    //     return chunks;
    // }

    const findChunksWordsonly = () => {
        const searchWords = imp_terms;
        const textToHighlight = data.content

        return searchWords
            .filter(searchWord => searchWord) // Remove empty words
            .reduce((chunks, searchWord) => {
                //searchWord = sanitize(searchWord)

                // if (autoEscape) {
                //     searchWord = escapeRegExpFn(searchWord)
                // }

                const regex = new RegExp(searchWord,'gi')
                //console.log(regex,searchWord)
                const pattern = /[.,/#!$%^&*;:{}=\-_`~()\s]/g
                let match
                while ((match = regex.exec(textToHighlight))) {
                    let start = match.index
                    let end = regex.lastIndex
                    // We do not return zero-length matches
                    //console.log(textToHighlight.substring(start,end))
                    //console.log(start,end) 
            
                    //console.log(textToHighlight[start-1],textToHighlight[end+1])  
                    if (end > start && (start-1 < 0 || textToHighlight[start-1].match(pattern)) && (end >= textToHighlight.length || textToHighlight[end].match(pattern)) ) {
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