from escalation import calculate_days_overdue, get_followup_stage
from email_generator import generate_email
from sender import mock_send_email
from utils import calculate_risk, mask_email


def process_invoice_rules(row):
    due_date = row["due_date"]
    days_overdue = calculate_days_overdue(due_date)

    stage_info = get_followup_stage(days_overdue)

    invoice = {
        "invoice_no": row["invoice_no"],
        "client_name": row["client_name"],
        "amount": row["amount"],
        "due_date": row["due_date"],
        "contact_email": row["contact_email"],
        "masked_email": mask_email(row["contact_email"]),
        "followup_count": row["followup_count"],
        "payment_link": row["payment_link"],
        "days_overdue": days_overdue,
        "stage": stage_info["stage"],
        "tone": stage_info["tone"],
        "cta": stage_info["cta"],
    }

    invoice["risk"] = calculate_risk(
        amount=invoice["amount"],
        days_overdue=invoice["days_overdue"],
        followup_count=invoice["followup_count"]
    )

    invoice["should_send"] = invoice["days_overdue"] > 0

    return {
        "invoice": invoice,
        "email": None,
        "send_result": None,
        "status": "RULES_PROCESSED",
        "explanation": (
            f"Tone selected as {invoice['tone']} because invoice is "
            f"{invoice['days_overdue']} days overdue with "
            f"{invoice['followup_count']} previous reminder(s)."
        )
    }


def generate_email_for_invoice(invoice):
    if invoice["stage"] == "Escalation Flag":
        return None

    return generate_email(invoice)


def approve_and_send(invoice, email):
    return mock_send_email(invoice, email)