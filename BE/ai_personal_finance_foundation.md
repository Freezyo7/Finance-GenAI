# AI Personal Finance Assistant — Foundation

## 1. Project Vision

Build a secure, scalable personal finance platform supporting both:

- **Personal finance** — one user manages their own finances.
- **Family finance** — multiple users collaborate within a shared household.

The project is designed to practice:

- Django
- Django REST Framework
- Authentication
- Authorization
- RBAC
- Object-level permissions
- Resource-level permissions
- PostgreSQL
- Redis
- Celery
- GenAI
- Tool/function calling
- Embeddings
- RAG
- AI security

### Core principle

> The backend is responsible for security and financial correctness. AI enhances the experience but never replaces authorization or deterministic financial calculations.

---

## 2. Core Domain Model

The central concept is a **Household**.

```text
User
  |
  | membership
  v
Household
  |
  +-------------------+
  |                   |
  v                   v
Members          Financial Accounts
                      |
                      v
                Transactions
```

A user does not directly own every financial object. Access is determined through household membership and resource-level permissions.

---

## 3. Personal vs Family

A Household has a type:

```text
PERSONAL
FAMILY
```

### Personal

```text
Personal Household
    |
    └── User
         └── OWNER
```

### Family

```text
Family Household
    |
    +── Father
    +── Mother
    +── Child
    └── Child
```

Personal and family finance use the **same underlying authorization model**.

---

## 4. User

The `User` represents an authenticated person.

Suggested fields:

```text
User
-------------------------
id
email
password
first_name
last_name
is_active
is_staff
created_at
updated_at
```

Use a **custom Django User model from the beginning**.

Authenticate using email rather than relying on usernames.

---

## 5. Household

```text
Household
-------------------------
id
name
type
created_by
created_at
updated_at
```

Types:

```text
PERSONAL
FAMILY
```

---

## 6. HouseholdMember

This is one of the most important models.

```text
HouseholdMember
-------------------------
id
household
user
role
relationship
status
joined_at
created_at
updated_at
```

### Role

Roles represent **permissions**, not family relationships.

```text
OWNER
ADMIN
MEMBER
VIEWER
```

### Relationship

```text
SELF
FATHER
MOTHER
SPOUSE
CHILD
OTHER
```

### Status

```text
INVITED
ACTIVE
SUSPENDED
REMOVED
```

### Important rule

Do not assume:

```text
Father = OWNER
Mother = ADMIN
Child = VIEWER
```

Instead keep `role` and `relationship` separate.

Example:

```text
Father → OWNER + FATHER
Mother → ADMIN + MOTHER
Child  → MEMBER + CHILD
```

This allows:

```text
Mother → OWNER
Father → VIEWER
Adult Child → ADMIN
```

without changing the data model.

---

## 7. Household Role Permissions

| Role | Household Management | Accounts | Transactions | Budgets | AI |
|---|---|---|---|---|---|
| OWNER | Full | Full | Full | Full | Full |
| ADMIN | Manage members | Manage shared accounts | Full on accessible accounts | Manage | Full |
| MEMBER | View members | Manage assigned accounts | Create/edit accessible transactions | Create/manage allowed budgets | Use |
| VIEWER | View members | Read assigned accounts | Read-only | Read-only | Limited |

**Role alone does not determine access to financial data.**

For financial resources we also check account-level access.

---

## 8. FinancialAccount

```text
FinancialAccount
-------------------------
id
household
name
account_type
institution
currency
balance
created_at
updated_at
```

Types:

```text
BANK_ACCOUNT
CREDIT_CARD
CASH
INVESTMENT
OTHER
```

Examples:

```text
Family Savings
Father Personal HDFC
Mother Personal SBI
Child Allowance
```

---

## 9. AccountMember

Not every household member should automatically see every financial account.

```text
AccountMember
-------------------------
id
account
user
permission
created_at
```

Permissions:

```text
OWNER
EDITOR
VIEWER
```

Example:

```text
Family Savings
    Father → OWNER
    Mother → EDITOR

Father Personal
    Father → OWNER

Child Allowance
    Father → VIEWER
    Child  → OWNER
```

---

## 10. Authorization Hierarchy

```text
User
 |
 v
Household Membership
 |
 v
Household Role
 |
 v
Account Membership
 |
 v
Account Permission
 |
 v
Transaction / Financial Resource
```

This is the core authorization exercise.

---

## 11. Transaction

Transactions belong to accounts.

```text
Transaction
-------------------------
id
account
amount
transaction_type
category
description
merchant
transaction_date
created_at
updated_at
```

Types:

```text
INCOME
EXPENSE
TRANSFER
```

Ownership chain:

```text
Transaction
    |
    v
FinancialAccount
    |
    v
Household
```

Do not make transactions belong only to a user.

---

## 12. Budget

Budgets belong to a household.

```text
Budget
-------------------------
id
household
category
amount
period
start_date
end_date
created_by
created_at
updated_at
```

Initially, household-level access is enough. More granular visibility can be added later if needed.

---

## 13. AIConversation

```text
AIConversation
-------------------------
id
user
household
title
created_at
updated_at
```

A conversation belongs to a user and can optionally be associated with a household.

---

## 14. AIMessage

```text
AIMessage
-------------------------
id
conversation
role
content
created_at
```

Roles:

```text
USER
ASSISTANT
SYSTEM
TOOL
```

Internal system messages must never be exposed to users.

---

## 15. Household Invitations

```text
HouseholdInvitation
-------------------------
id
household
email
role
relationship
token
status
expires_at
invited_by
created_at
```

Flow:

```text
Owner/Admin
     |
     v
Create Invitation
     |
     v
Invitation
     |
     v
User receives invitation
     |
     v
Accept Invitation
     |
     v
HouseholdMember
```

Statuses:

```text
PENDING
ACCEPTED
EXPIRED
REVOKED
```

---

## 16. Authentication Foundation

Authentication answers:

> **Who is this user?**

Initial endpoints:

```http
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/
POST /api/auth/logout/

GET /api/auth/me/

POST /api/auth/change-password/
POST /api/auth/forgot-password/
POST /api/auth/reset-password/
```

Recommended approach:

```text
Custom User
+
JWT
+
Django REST Framework
```

---

## 17. Authorization Foundation

Authorization answers:

> **What is this authenticated user allowed to do?**

Every protected request should conceptually follow:

```text
Request
  |
  v
Authenticate user
  |
  v
Is user authenticated?
  |
  +---- NO ----> 401
  |
 YES
  |
  v
Check household membership
  |
  v
Check role
  |
  v
Check resource ownership/access
  |
  v
Check requested operation
  |
  +---- NO ----> 403
  |
 YES
  |
  v
Execute operation
```

### 401 vs 403

**401 Unauthorized**: no valid authentication.

Examples:

```text
No JWT
Expired JWT
Invalid JWT
```

**403 Forbidden**: authenticated but not permitted.

Example:

```text
User A tries to modify User B's account.
```

---

## 18. Example Authorization Scenarios

### Personal Finance

```text
Nishant
 |
 └── Personal Household
       |
       └── Nishant → OWNER
```

Nishant creates an HDFC account and can access it.

### Family Finance

```text
Family Household

Father → OWNER
Mother → ADMIN
Child  → MEMBER
```

Accounts:

```text
Family Savings
    Father → OWNER
    Mother → EDITOR

Father Personal
    Father → OWNER

Child Allowance
    Father → VIEWER
    Child  → OWNER
```

### Unauthorized Account Access

Child requests:

```http
GET /api/accounts/father-personal/
```

Checks:

```text
Authenticated?
✓

Household member?
✓

Account member?
✗
```

Result:

```text
403 Forbidden
```

---

## 19. AI Security Boundary

The AI must never determine authorization.

### Bad

```text
User
 |
 v
AI
 |
"I think this user can see the account."
```

### Correct

```text
User
 |
 v
Django Authentication
 |
 v
Django Authorization
 |
 v
Retrieve authorized data
 |
 v
AI
 |
 v
Response
```

The AI receives only data the user is already authorized to access.

---

## 20. AI Financial Assistant

Example:

```text
User:
"How much did I spend on food last month?"
```

Correct flow:

```text
Question
   |
   v
Authenticate
   |
   v
Authorize
   |
   v
Identify accessible accounts
   |
   v
Query transactions
   |
   v
Calculate exact total
   |
   v
LLM explains result
```

Do not send the entire transaction database to the LLM.

---

## 21. AI Tool Calling

Eventually the AI should have controlled backend tools:

```text
get_transactions()
get_spending_by_category()
get_monthly_spending()
get_income()
get_budget()
get_recurring_expenses()
```

Architecture:

```text
                         AI
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
 get_transactions   get_budget     get_income
          |               |               |
          +---------------+---------------+
                          |
                          v
                     PostgreSQL
```

Every tool must enforce authorization.

Never trust a user ID or account ID supplied by the LLM.

---

## 22. Financial Calculations

Use deterministic backend/database logic for financial calculations.

Bad:

```text
LLM → calculate total expenses
```

Better:

```text
PostgreSQL
    |
    v
SUM(transactions.amount)
    |
    v
₹74,320
    |
    v
LLM
    |
    v
Explain the spending
```

The LLM should explain, summarize, classify, recommend, and interact.

It should not be the source of truth for arithmetic or authorization.

---

## 23. Initial GenAI Features

Build these after the core backend is stable.

### Transaction Categorization

```text
"PAYTM*NETFLIX"
        |
        v
AI
        |
        v
Entertainment / Streaming
```

### Spending Analysis

```text
Transactions
    |
    v
Backend aggregation
    |
    v
AI explanation
```

### Financial Assistant

Natural-language questions over authorized financial data.

### Budget Generator

AI proposes a budget based on historical spending.

### Subscription Detection

Identify recurring expenses and explain them.

---

## 24. RAG

Add RAG later for general financial knowledge.

Knowledge base:

```text
Budgeting
Saving
Emergency funds
Debt management
Credit scores
Investing basics
Financial planning concepts
```

Pipeline:

```text
Documents
    |
    v
Chunking
    |
    v
Embeddings
    |
    v
pgvector
    |
    v
Similarity Search
    |
    v
Relevant Context
    |
    v
LLM
```

Important:

> Use SQL for structured personal financial data and RAG for unstructured financial knowledge.

---

## 25. Security Practice

Deliberately test:

```text
[ ] Invalid JWT
[ ] Expired JWT
[ ] Token misuse
[ ] IDOR
[ ] Broken object-level authorization
[ ] Privilege escalation
[ ] Mass assignment
[ ] Unauthorized household access
[ ] Unauthorized account access
[ ] Unauthorized transaction access
[ ] Unauthorized AI tool calls
[ ] Prompt injection
[ ] AI data leakage
[ ] Malicious CSV upload
[ ] Rate-limit bypass
```

---

## 26. Audit Logging

Because financial information is sensitive, add an audit log later.

```text
AuditLog
-------------------------
id
user
household
action
resource_type
resource_id
metadata
ip_address
created_at
```

Examples:

```text
USER_LOGIN
ACCOUNT_CREATED
ACCOUNT_UPDATED
TRANSACTION_CREATED
TRANSACTION_DELETED
MEMBER_INVITED
MEMBER_REMOVED
AI_TOOL_EXECUTED
```

Never log passwords, tokens, CVVs, or other sensitive credentials.

---

## 27. Scalability Principles

The system should support:

```text
1 user
    ↓
1 household
    ↓
Personal finance
```

and:

```text
1 household
    ↓
2 members
    ↓
10 members
    ↓
100+ members
```

without changing the fundamental authorization architecture.

Do not hard-code:

```text
father_id
mother_id
child_id
child_1
child_2
```

Use:

```text
HouseholdMember
```

instead.

---

## 28. Recommended Database Indexes

Potential indexes:

```text
HouseholdMember:
    household_id
    user_id
    (household_id, user_id)

AccountMember:
    account_id
    user_id
    (account_id, user_id)

FinancialAccount:
    household_id

Transaction:
    account_id
    transaction_date
    category_id
    (account_id, transaction_date)

Budget:
    household_id
    start_date
    end_date
```

Finalize indexes based on actual query patterns and profiling.

---

## 29. Project Development Phases

### Phase 1 — Foundation

```text
[ ] Initialize project with uv
[ ] Configure Django
[ ] Configure PostgreSQL
[ ] Configure environment variables
[ ] Configure DRF
[ ] Configure Git
[ ] Create custom User
```

### Phase 2 — Authentication

```text
[ ] Registration
[ ] Login
[ ] JWT access token
[ ] Refresh token
[ ] Logout
[ ] /me
[ ] Password change
[ ] Password reset
[ ] Account activation
```

### Phase 3 — Household

```text
[ ] Household model
[ ] PERSONAL household
[ ] FAMILY household
[ ] HouseholdMember
[ ] Roles
[ ] Relationships
[ ] Member status
```

### Phase 4 — Authorization

```text
[ ] IsAuthenticated
[ ] Household membership checks
[ ] Role permissions
[ ] Object-level permissions
[ ] Account-level permissions
[ ] Ownership checks
[ ] Authorization tests
```

This is the main learning phase for authentication/authorization.

### Phase 5 — Financial Data

```text
[ ] FinancialAccount
[ ] AccountMember
[ ] Category
[ ] Transaction
[ ] Budget
[ ] CRUD APIs
[ ] Filtering
[ ] Pagination
[ ] Validation
```

### Phase 6 — Family Features

```text
[ ] Household invitations
[ ] Accept invitation
[ ] Revoke invitation
[ ] Add/remove members
[ ] Account sharing
[ ] Account permissions
```

### Phase 7 — Analytics

```text
[ ] Monthly spending
[ ] Spending by category
[ ] Income vs expense
[ ] Savings rate
[ ] Budget utilization
[ ] Recurring expenses
```

### Phase 8 — GenAI

```text
[ ] LLM integration
[ ] Structured outputs
[ ] Transaction categorization
[ ] Spending analysis
[ ] AI assistant
[ ] Budget generation
[ ] Subscription analysis
```

### Phase 9 — AI Tools

```text
[ ] Tool schemas
[ ] Tool calling
[ ] Authorization inside tools
[ ] Tool result validation
[ ] Conversation history
[ ] AI usage tracking
```

### Phase 10 — RAG

```text
[ ] Knowledge base
[ ] Document ingestion
[ ] Chunking
[ ] Embeddings
[ ] pgvector
[ ] Retrieval
[ ] Context construction
[ ] RAG responses
```

### Phase 11 — Security

```text
[ ] IDOR testing
[ ] Privilege escalation testing
[ ] Prompt injection testing
[ ] AI data isolation
[ ] Rate limiting
[ ] File upload security
[ ] Audit logging
[ ] Security-focused API tests
```

### Phase 12 — Production

```text
[ ] Redis
[ ] Celery
[ ] Docker
[ ] Background CSV processing
[ ] Caching
[ ] Database optimization
[ ] API documentation
[ ] CI/CD
[ ] Monitoring
[ ] Deployment
```

---

## 30. Initial Database Relationship Diagram

```text
                           User
                            |
                 +----------+----------+
                 |                     |
                 v                     v
          HouseholdMember       AIConversation
                 |
                 v
             Household
                 |
        +--------+---------+
        |                  |
        v                  v
FinancialAccount         Budget
        |
        v
  AccountMember
        |
        v
   Transaction


Household
    |
    v
HouseholdInvitation
```

---

## 31. Final Authorization Model

```text
                         USER
                          |
                   Authentication
                          |
                          v
                     HOUSEHOLD
                    /                        PERSONAL         FAMILY
                 |                |
              1 member        N members
                 |                |
                 +-------+--------+
                         |
                         v
                  HOUSEHOLD MEMBER
                         |
                  +------+------+
                  |             |
                 ROLE      RELATIONSHIP
                  |
        +---------+---------+---------+
        |         |         |         |
      OWNER     ADMIN     MEMBER    VIEWER
                  |
                  v
           FINANCIAL ACCOUNT
                  |
             ACCOUNT MEMBER
                  |
         +--------+--------+
         |        |        |
       OWNER    EDITOR   VIEWER
                  |
                  v
             TRANSACTIONS
                  |
                  v
                  AI
```

---

## 32. Project Success Criteria

The foundation is successful when:

### Personal user

```text
User
  └── Personal Household
        └── Own Account
              └── Own Transactions
```

### Family

```text
Family Household
  ├── Father
  ├── Mother
  └── Child
```

with different roles and account-level access.

### Authorization

A user cannot access another user's private financial data even when the JWT is valid.

### AI

The AI receives only data the authenticated user is authorized to access.

### Scalability

Adding:

```text
another family member
another account
another transaction
another household
```

does not require changes to the core authorization architecture.

---

## 33. Development Rule

Build in this order:

```text
Django
   ↓
Custom User
   ↓
Authentication
   ↓
Household
   ↓
Household Membership
   ↓
RBAC
   ↓
Account-Level Permissions
   ↓
Transactions
   ↓
Financial Analytics
   ↓
GenAI
   ↓
AI Tool Calling
   ↓
RAG
   ↓
AI Security
   ↓
Production Scaling
```

**Do not start implementing GenAI until the authentication and authorization foundation is working and tested.**

The core challenge is not simply making an AI chatbot. It is building a **secure, multi-user financial system where GenAI operates inside well-defined authorization boundaries.**
