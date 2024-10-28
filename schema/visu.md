```mermaid
graph LR
subgraph High_Level_Overview [High Level Overview]
    %% Recruiter Group
    subgraph Recruiter
        subgraph Sync_Process [Synchronous Process]
            A[Recruiter] --|Automated Extraction|--> B(Job requirements)
            A --|Manual Modification|--> B
        end
    end
    
    %% Candidates Group
    subgraph Candidates
        subgraph Async_Process [Asynchronous Process]
            A1[Candidate] --> B2(Information Extraction)
            A2[Candidate] --> B2
            B2 --> C2[Knowledge Graph Generation]
            B2 --> D2[Embeddings generation]
        end
    end
    
    %% Connections to Recommendation System
    B --> A3[Recommendation System]
    D2 --> A3
    A3 --> A4[Top K Candidates]
end



