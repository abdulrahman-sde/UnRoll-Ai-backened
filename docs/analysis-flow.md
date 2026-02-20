# Resume Analysis Flow

## Overview

The client sends one HTTP request. The server does all the heavy lifting synchronously and returns the full result. No polling, no webhooks — yet.

```
POST /api/v1/analyses
Content-Type: multipart/form-data

file     = resume.pdf   (required)
job_id   = 42           (optional)
```

---

## Step-by-Step Flow

```
Client
  │
  │  POST /analyses  (multipart: file + job_id?)
  ▼
FastAPI Endpoint  ─── validate JWT ──→  User (from token, never from body)
  │
  │  body.validate_file()  →  reject if not application/pdf
  ▼
AnalysisService.create_analysis(file, job_id, user)
  │
  ├─ 1. EXTRACT TEXT
  │      Read file bytes → parse PDF → plain text string
  │      (library: pdfplumber / pypdf)
  │
  ├─ 2. SAVE RESUME RECORD
  │      INSERT INTO resumes (user_id, content, url)
  │      url = uploaded filename or S3 key (future)
  │      content = extracted plain text
  │      → returns Resume.id
  │
  ├─ 3. FETCH JOB DESCRIPTION  (skip if job_id is None)
  │      SELECT * FROM jobs WHERE id = job_id AND user_id = user.id
  │      → raises 404 if not found or not owned by user
  │
  ├─ 4. CALL OPENAI
  │      System prompt:  strict JSON schema instructions
  │      User message:   resume text + (optional) job description
  │      Model:          gpt-4o
  │      Output format:  structured JSON  →  AnalysisResultSchema
  │      (model_validator derives hire_recommendation automatically)
  │
  ├─ 5. SAVE ANALYSIS RECORD
  │      INSERT INTO analyses (
  │        user_id, resume_id, job_id,
  │        candidate_name, target_role,        ← flat columns for fast SQL
  │        recommendation, hire_recommendation,
  │        overall_score, total_experience_years,
  │        analysis_result,                    ← full JSONB blob
  │        embedding                           ← vector (step 6)
  │      )
  │
  ├─ 6. GENERATE EMBEDDING
  │      build_embedding_text(result)  →  semantic text string
  │      openai.embeddings.create(text, model="text-embedding-3-small")
  │      → 1536-dimension vector stored in pgvector column
  │
  └─ 7. RETURN  AnalysisResponse  →  201 Created
```

---

## Data Model Relationships

```
User
 ├── Job[]          (user creates job postings)
 ├── Resume[]       (user uploads resumes)
 └── Analysis[]
       ├── resume_id  →  Resume   (CASCADE delete)
       ├── job_id     →  Job      (SET NULL on delete)
       └── user_id    →  User     (CASCADE delete)
```

One resume can have **multiple analyses** (re-analyzed against different jobs).  
One job can have **multiple analyses** (multiple candidates screened against it).

---

## Why Resume is Saved Separately

The `Resume` table stores the raw extracted text permanently. This means:

- Re-analysis against a new job **does not re-upload** the PDF — the client sends `resume_id` instead
- The raw text is the source of truth; the `Analysis` is a derived artifact
- You can diff analysis results across time for the same resume

> **Current state:** the `POST /analyses` endpoint accepts a fresh PDF every time and creates a new `Resume` record. A future `POST /resumes` endpoint will allow pre-uploading and reusing resume records.

---

## Why the DB Schema Has Flat Columns + JSONB

```
analyses
  candidate_name      ← indexed, for SQL search: "find all analyses for John"
  recommendation      ← indexed, for SQL filter: "show HIRE recommendations only"
  hire_recommendation ← indexed, for SQL filter: boolean fast path
  overall_score       ← indexed, for SQL sort: "rank by score DESC"
  analysis_result     ← JSONB, stores the full AnalysisResultSchema blob
  embedding           ← pgvector, for semantic RAG search
```

Flat columns exist for queries that need to be **fast and filterable**.  
JSONB exists because the full result is deeply nested and changes shape over time.  
Both are written in the same INSERT — no sync needed.

---

## What the LLM Receives

```
SYSTEM:
  You are an expert technical recruiter. Analyze the resume and return
  a strict JSON object matching the provided schema. Do not add commentary.

USER:
  === RESUME ===
  {extracted_text}

  === JOB DESCRIPTION ===   (omitted if no job_id)
  {job.title}: {job.description}
```

The response is parsed directly into `AnalysisResultSchema` via Pydantic structured output. If the LLM returns an invalid score (e.g. 150) or a missing required field, Pydantic raises a `ValidationError` which the service catches and re-raises as a 422.

---

## Error Cases

| Situation                      | HTTP Status                | Raised by                     |
| ------------------------------ | -------------------------- | ----------------------------- |
| Not a PDF                      | `422 Unprocessable Entity` | `body.validate_file()`        |
| Invalid JWT                    | `401 Unauthorized`         | `get_current_user` dependency |
| `job_id` not found / not owned | `404 Not Found`            | `AnalysisService`             |
| PDF has no extractable text    | `422 Unprocessable Entity` | `AnalysisService`             |
| LLM returns invalid JSON       | `422 Unprocessable Entity` | Pydantic `ValidationError`    |
| OpenAI API failure             | `502 Bad Gateway`          | `AnalysisService`             |
