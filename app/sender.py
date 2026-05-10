from logger import save_audit_log


def mock_send_email(invoice, email):

    status = "SUCCESS"

    log_entry = save_audit_log(
        invoice=invoice,
        email_subject=email["subject"],
        status=status
    )

    return {
        "status": "SUCCESS",
        "provider": "SMTP Dry Run",
        "message": "Email simulated successfully.",
        "log": log_entry
    }