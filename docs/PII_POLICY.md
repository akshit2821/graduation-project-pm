# PII policy — Graduation Project

## Never store or publish

- Reviewer or poster username, profile URL, email, phone  
- Interview participant **names** in deck, git, or public artifacts  
- OAuth tokens, API keys, `credentials.json`  

## At ingest (Part 1)

Drop columns when present: `username`, `userName`, `author`, `email`, `userId`, `profileUrl`, `device`.

## In quote bank and deck

- Short snippets only; no `@handles`  
- Redact digit runs >6 chars if account-like  
- Interview quotes use IDs (P1, P2) not real names  

## Part 2 interviews

- Notes stored in `part-2-research/notes/` — **gitignore** recordings  
- Google Form: collect segment fit, not full legal name in public sheet if avoidable  

## Logging

- Log `feedback_id` and counts — not full post text in shared CI logs  
