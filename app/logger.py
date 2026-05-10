import json
from datetime import datetime
from pathlib import Path

# Audit log file path
LOG_FILE = Path("../logs/audit_log.json")


def init_log_file():

    # Create logs folder automatically
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Create empty JSON file if missing
    if not LOG_FILE.exists():

        with open(LOG_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)


def save_audit_log(invoice, email_subject, status):

    init_log_file()

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            logs = json.load(file)

            # Safety fallback
            if not isinstance(logs, list):
                logs = []

    except Exception:
        logs = []

    # Create audit entry
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "invoice_no": invoice["invoice_no"],
        "client_name": invoice["client_name"],
        "amount": invoice["amount"],
        "days_overdue": invoice["days_overdue"],
        "stage": invoice["stage"],
        "tone": invoice["tone"],
        "risk": invoice["risk"],
        "email_subject": email_subject,
        "status": status
    }

    # Append latest log
    logs.append(log_entry)

    # Save updated logs
    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(logs, file, indent=4)

    return log_entry


# TEST LOG CREATOR
# This helps prevent empty audit log table initially
if __name__ == "__main__":

    sample_invoice = {
        "invoice_no": "INV-1001",
        "client_name": "Rajesh Kapoor",
        "amount": 45000,
        "days_overdue": 12,
        "stage": "2nd Follow-Up",
        "tone": "Polite but Firm",
        "risk": "MEDIUM"
    }

    save_audit_log(
        invoice=sample_invoice,
        email_subject="Test Audit Log",
        status="SUCCESS"
    )

    print("✅ Test audit log created successfully.")