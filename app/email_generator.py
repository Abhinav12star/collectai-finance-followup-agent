import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


SYSTEM_PROMPT = """
You are an enterprise finance follow-up assistant.

Rules:
- Never invent invoice details.
- Use only the provided invoice data.
- Match the required tone.
- Include client name, invoice number, amount, due date, days overdue, and payment link.
- Keep the email professional, concise, and action-oriented.
- Do not generate generic emails.

Tone Rules:

1st Follow-Up:
Warm & Friendly.
Assume payment oversight.
Use gentle reminder language.

2nd Follow-Up:
Polite but Firm.
Mention that payment is still pending.
Request payment confirmation.

3rd Follow-Up:
Formal & Serious.
Mention escalating concern and possible impact on credit terms.
Request response within 48 hours.

4th Follow-Up:
Stern & Urgent.
State that this is the final reminder before escalation.
Mention legal/recovery action if payment is not completed.

Escalation Flag:
Do not generate an email.
Flag for finance/legal review.
"""


def validate_email_output(email, invoice):
    required_values = [
        str(invoice["client_name"]),
        str(invoice["invoice_no"]),
        str(invoice["amount"]),
        str(invoice["days_overdue"]),
        str(invoice["payment_link"])
    ]

    email_text = (
        email.get("subject", "") + " " + email.get("body", "")
    )

    for value in required_values:
        if value not in email_text:
            return False

    return True


def extract_subject_and_body(text, fallback_subject):
    """
    Extracts Subject and Body from the LLM response.
    If parsing fails, fallback subject is used.
    """
    if not text:
        return fallback_subject, ""

    subject = fallback_subject
    body = text.strip()

    lines = text.strip().splitlines()

    for i, line in enumerate(lines):
        clean_line = line.strip()

        if clean_line.lower().startswith("subject:"):
            subject = clean_line.replace("Subject:", "").replace("subject:", "").strip()

            remaining_lines = lines[i + 1:]

            cleaned_body_lines = []
            for body_line in remaining_lines:
                if body_line.strip().lower() == "body:":
                    continue
                cleaned_body_lines.append(body_line)

            body = "\n".join(cleaned_body_lines).strip()
            break

    return subject, body


def generate_email(invoice):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return fallback_email(invoice)

    fallback_subject = (
        f"Payment Reminder – Invoice #{invoice['invoice_no']} | "
        f"₹{invoice['amount']} Due"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", f"""
Generate a payment follow-up email.

Client Name: {invoice['client_name']}
Invoice Number: {invoice['invoice_no']}
Amount Due: ₹{invoice['amount']}
Due Date: {invoice['due_date']}
Days Overdue: {invoice['days_overdue']}
Follow-up Count: {invoice['followup_count']}
Stage: {invoice['stage']}
Tone: {invoice['tone']}
CTA: {invoice['cta']}
Payment Link: {invoice['payment_link']}

Return in this exact format:

Subject: <email subject>

Body:
<email body>
""")
    ])

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
            google_api_key=api_key
        )

        chain = prompt | llm
        response = chain.invoke({})

        subject, body = extract_subject_and_body(
            response.content,
            fallback_subject
        )

        email = {
            "subject": subject,
            "body": body
        }

        if validate_email_output(email, invoice):
            return email

        return fallback_email(invoice)

    except Exception as e:
        print("Gemini API error:", e)
        return fallback_email(invoice)


def fallback_email(invoice):
    return {
        "subject": f"Payment Reminder – Invoice #{invoice['invoice_no']} | ₹{invoice['amount']} Due",
        "body": f"""
Dear {invoice['client_name']},

This is a reminder that Invoice #{invoice['invoice_no']} for ₹{invoice['amount']} was due on {invoice['due_date']} and is currently {invoice['days_overdue']} days overdue.

Stage: {invoice['stage']}
Tone: {invoice['tone']}

Please complete the payment using the link below:
{invoice['payment_link']}

Regards,
Finance Team
"""
    }