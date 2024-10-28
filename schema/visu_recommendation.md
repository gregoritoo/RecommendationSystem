```mermaid
graph LR
subgraph Recommandation [Recommandation]
    B(Knowledge Graph)
    subgraph ExactMatching
        A[Keyword] --|SPARQL Request|--> B(Knowledge Graph)
        B -->C(Matching Candidates)
    end
    subgraph SimilarityMatching
        A1["Sentence description"] --|Similarity Search| -->B1(Top Matching Chuncks)
        B1(Top Matching Chuncks) --|SPARQL Request|--> B(Knowledge Graph)
        B(Knowledge Graph) -->C1(Similarity Candidates)
    end
    C1(Similarity Candidates) --> D(Found Candidates)
    C(Matching Candidates) --> D(Found Candidates)
    D(Found Candidates) --|Reranking| -->E(Top-K Candidates)
end



