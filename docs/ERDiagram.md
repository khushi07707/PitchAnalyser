# ER Diagram

The following Mermaid diagram represents the main entities and relationships for the application.

```mermaid
erDiagram
    USERS {
        uuid Id PK
        string FirstName
        string LastName
        string Email
    }
    ROLES {
        uuid Id PK
        string Name
    }
    STARTUPS {
        uuid Id PK
        string Name
        string FounderName
        string FounderEmail
    }
    FINANCIAL_DATA {
        uuid Id PK
        decimal AnnualRevenue
    }
    PITCHES {
        uuid Id PK
        string Title
        datetime UploadedAt
    }
    FILE_RECORDS {
        uuid Id PK
        string FileName
        string FilePath
    }
    PITCH_ANALYSES {
        uuid Id PK
        string AnalysisJson
    }

    ROLES ||--o{ USERS : has
    USERS ||--o{ STARTUPS : creates
    STARTUPS ||--o{ PITCHES : contains
    STARTUPS ||--|| FINANCIAL_DATA : has
    PITCHES ||--|| FILE_RECORDS : has
    PITCHES ||--|| PITCH_ANALYSES : analysed_by

```

Explanation: A `User` (founder or admin) can create `Startup` records. Each `Startup` may have optional `FinancialData`, multiple `Pitches`, each `Pitch` has an uploaded `FileRecord` and an associated `PitchAnalysis` produced by the AI service.
