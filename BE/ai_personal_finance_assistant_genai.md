# AI Personal Finance Assistant (GenAI Career Track Edition)

A **$0–$5/month** Django + GenAI portfolio project, adjusted specifically to build
the skills employers screen for in GenAI/LLM engineering roles:
RAG, tool calling, structured output, embeddings, prompt safety, and eval.

Core backend design (auth, RBAC, ownership chains, phases) is unchanged from
your original spec — that part was already solid. This document only changes
**what runs where** and **why**, so you learn the same concepts at near-zero cost.

---

## 1. Why keep Django

Django + DRF is the right choice for this, for career purposes specifically:

- Most GenAI job postings (LLM platform, AI backend, applied AI engineer) want
  "backend engineer who can integrate LLMs," not "prompt writer." Django proves
  the backend half.
- The parts of this project that are hardest to fake in an interview —
  object-level authorization, tool-calling with real permission checks,
  prompt-injection isolation — are backend problems. Django/DRF is a fine tool
  for all of them.
- Skip Django only if you were instead trying to build a pure ML/inference
  service (FastAPI territory). You're not — you're building an app with AI
  features, so this is correct.

No change needed to Phases 1–6 (auth, authorization, CRUD, CSV import,
analytics). Build those exactly as planned — they're free regardless of stack,
since they don't touch any paid API.

---

## 2. What actually costs money (and the swap)

| Original component | Cost if used as spec'd | Free-only swap | Notes |
|---|---|---|---|
| PostgreSQL + pgvector | Free if self-hosted, but you need it *hosted* eventually | **Supabase free tier** (Postgres + pgvector built in) | Real hosted pgvector DB for demos/interviews, no card needed |
| Redis | Free self-hosted | **Redis in Docker** (local container, part of your `docker-compose` stack) | No hosted Redis needed — it only has to be reachable while you're running/demoing the project |
| LLM API (chat, categorization, budget gen) | GPT-4-class APIs add up fast per request | **Google Gemini API free tier** (function calling + JSON mode supported) | Single provider, keeps the whole AI layer on one free quota |
| Embeddings | OpenAI embeddings cost per call | **Gemini's free embedding endpoint** | Keeps embeddings on the same free Gemini quota instead of adding another dependency |
| Hosting/deployment | VPS costs money | **`docker-compose` locally** (Django, Celery worker, Redis all containerized); record a demo video/GIF for your portfolio | No hosting bill at all — Supabase is the only externally-hosted piece |
| Celery broker | Free self-hosted | Same Dockerized Redis container doubles as the Celery broker | One container, two jobs |

**Total stack: Docker (self-hosted everything except the DB) + Supabase (free Postgres/pgvector) + Gemini (free LLM + embeddings). Total monthly cost: $0.**

---

## 3. Revised recommended stack

```text
Backend:          Django + DRF                (unchanged)
Auth:              JWT + custom User model     (unchanged)
Database:          PostgreSQL + pgvector       via Supabase (free tier)
Cache/Broker:       Redis                      via Docker (local container)
Background jobs:    Celery                     (unchanged, broker = Dockerized Redis)
LLM:                Google Gemini API (free tier) — chat, categorization, budget gen, RAG answers
Embeddings:         Google Gemini embeddings (free tier)
Storage:            Local disk                 (unchanged — no S3 needed for a practice project)
Testing:            pytest + pytest-django     (unchanged)
Deployment:         docker-compose locally — Django, Celery worker, Redis all containerized;
                    Supabase is the only externally-hosted piece
```

Everything else in your original doc — data models, API structure, the
5 AI features, tool-calling architecture, RAG pipeline, security checklist,
11-phase roadmap — carries over exactly as written. Nothing there needs
architectural changes for cost reasons; it only needed the *providers* swapped.

---

## 4. One addition worth making: an Evaluation phase

This is the one gap I'd add for GenAI-career purposes specifically, since it's
what separates "used an LLM API" from "can build LLM systems" in interviews:

### New Phase — AI Evaluation & Observability (insert after Phase 8, before RAG)

- [ ] Log every LLM call: prompt, response, latency, token count, cost estimate
- [ ] Write a small "golden set" of ~15–20 test questions with expected answer
      shapes (e.g. "categorization output must have valid category + confidence
      between 0–1")
- [ ] Add a script that replays the golden set against the current prompts and
      flags regressions
- [ ] Track structured-output validation failure rate (how often does the LLM
      return malformed JSON, and how does your code handle it — retry? reject?)

This is small to build (a few hours), costs nothing extra, and is one of the
most commonly asked-about skills in GenAI engineering interviews: "how do you
know your LLM feature actually works and keeps working."

---

## 5. What to say about this project when job-hunting

Frame it as: *"Built a backend system where AI augments — not replaces —
core business logic, with enforced authorization at every AI touchpoint."*
That sentence, backed by working code, directly answers the two things
GenAI-adjacent backend interviews actually probe:

1. Can you integrate an LLM into a real system safely (auth, tool-calling
   permission checks, prompt-injection isolation, structured output validation)?
2. Do you understand where an LLM should *not* be trusted (financial
   calculations, authorization decisions) — this project's core rule.

Your original doc's rule — *"AI should enhance the backend, not replace
backend logic"* — is exactly the right thing to lead with in interviews.
