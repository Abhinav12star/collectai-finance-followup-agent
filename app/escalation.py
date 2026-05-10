from datetime import date


def calculate_days_overdue(due_date):
    today = date.today()
    return max((today - due_date).days, 0)


def get_followup_stage(days_overdue):

    if days_overdue <= 0:
        return {
            "stage": "Not Due",
            "tone": "No Follow-up Needed",
            "cta": "No action required"
        }

    elif 1 <= days_overdue <= 7:
        return {
            "stage": "1st Follow-Up",
            "tone": "Warm & Friendly",
            "cta": "Pay now using payment link"
        }

    elif 8 <= days_overdue <= 14:
        return {
            "stage": "2nd Follow-Up",
            "tone": "Polite but Firm",
            "cta": "Confirm expected payment date"
        }

    elif 15 <= days_overdue <= 21:
        return {
            "stage": "3rd Follow-Up",
            "tone": "Formal & Serious",
            "cta": "Respond within 48 hours"
        }

    elif 22 <= days_overdue <= 30:
        return {
            "stage": "4th Follow-Up",
            "tone": "Stern & Urgent",
            "cta": "Pay immediately or call finance team"
        }

    else:
        return {
            "stage": "Escalation Flag",
            "tone": "Legal / Finance Review",
            "cta": "Assign to finance manager"
        }