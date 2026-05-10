# 🔷 Technical Stack & Decision Log

---

# 🧠 1. LLM Selection

## ✅ Chosen Model

- **Gemini 2.0 Flash (`gemini-2.0-flash`)**
- **Provider:** Google AI Studio

---

## 💡 Why Gemini?

Gemini 2.0 Flash was selected because it provides:

- ⚡ Fast response generation
- 💰 Cost-efficient API usage
- 🧠 Strong prompt-following capability
- 🔗 Easy LangChain integration
- 🏢 Suitable performance for enterprise finance workflows

Compared to **GPT-4o** and **Claude Sonnet**, Gemini Flash offered:

- 🚀 Faster prototyping
- 💵 Lower API cost
- 📧 Reliable structured email generation
- 🤖 Good performance for finance recovery automation

---

# ⚙️ 2. Agent Framework

## ✅ Framework Used

- **LangChain**

---

## 🏗️ Architecture Type

- Single-agent sequential workflow

---

## 🔄 Workflow Architecture

```text
CSV Input
   ↓
Overdue Detection
   ↓
Tone Escalation Engine
   ↓
Risk Scoring
   ↓
Gemini AI Email Generation
   ↓
Human Approval Workflow
   ↓
Dry-Run Email Sending
   ↓
Audit Logging






# ⚙️ 2. Agent Framework

## ✅ Framework Used

- **LangChain**

---

## 🏗️ Architecture Type

- Single-agent sequential workflow

---

## 🔄 Workflow Architecture

```text
CSV Input
   ↓
Overdue Detection
   ↓
Tone Escalation Engine
   ↓
Risk Scoring
   ↓
Gemini AI Email Generation
   ↓
Human Approval Workflow
   ↓
Dry-Run Email Sending
   ↓
Audit Logging
```

---

## 💡 Why LangChain?

LangChain was selected because it provides:

- 🧩 Easy prompt management
- 🔄 Scalable LLM orchestration
- 🔗 Simple Gemini integration
- 🏢 Production-ready architecture
- ♻️ Reusable prompt pipeline support

---

# ✍️ 3. Prompt Design

## ✅ System Prompt Strategy

The system prompt enforces:

- 📧 Professional finance communication
- 📈 Stage-specific tone escalation
- 🧾 Dynamic invoice field usage
- ⚡ Concise and action-oriented responses

---

## 🛡️ Guardrails Applied

The prompts explicitly instruct the model to:

- ❌ Never invent invoice information
- ✅ Use only provided invoice fields
- 🎯 Maintain proper escalation tone
- 🚫 Avoid generic responses
- 🚫 Avoid hallucinated payment details
- 🔗 Include payment links and clear CTA instructions

---

## 👨‍💼 Human-in-the-Loop Protection

All generated emails require manual approval before simulated sending.

This reduces hallucination risk and prevents uncontrolled automated communication.

---

# 🔐 4. Security Risk Mitigation

| 🔴 Risk | 🛡️ Mitigation Strategy |
|---|---|
| Prompt Injection | Controlled prompts and structured invoice fields |
| Data Privacy / PII | Emails masked in audit logs and dashboard |
| API Key Exposure | `.env` + `python-dotenv` used |
| Hallucination Risk | Strict prompts + fallback templates + human approval workflow |
| Unauthorized Access | Local sandbox execution only; OAuth/API authentication planned for production |
| Email Spoofing | Dry-run email simulation used; SPF/DKIM/DMARC recommended for production SMTP deployment |

---

# 👨‍💼 5. Human-in-the-Loop Review

The system includes:

- ✅ Approve workflow
- ❌ Reject workflow
- 🚨 Manual escalation workflow

This prevents uncontrolled automated communication and ensures finance team oversight before email dispatch.

---

# 📊 6. Observability & Logging

The system stores:

- 🕒 Timestamps
- 🧾 Invoice details
- ⚠️ Risk level
- 📈 Escalation stage
- 📬 Send status
- 🧠 Audit logs

Logs are stored in JSON format and downloadable as:

- 📄 CSV reports
- 📑 PDF audit reports

---

# 🚀 7. Future Improvements

Planned future enhancements:

- ⏰ APScheduler automation
- 📧 Real SMTP integration
- 🗄️ SQLite/PostgreSQL audit database
- 🔑 OAuth authentication
- 📡 LangSmith observability
- 👥 Role-based access control
- 📈 Real-time recovery analytics
- 🤖 AI-based payment forecasting

---