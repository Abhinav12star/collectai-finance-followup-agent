def calculate_risk(amount, days_overdue, followup_count):
    score = 0

    if amount >= 100000:
        score += 2
    elif amount >= 50000:
        score += 1

    if days_overdue >= 22:
        score += 2
    elif days_overdue >= 8:
        score += 1

    if followup_count >= 3:
        score += 2
    elif followup_count >= 1:
        score += 1

    if score >= 5:
        return "HIGH"
    elif score >= 3:
        return "MEDIUM"
    else:
        return "LOW"


def mask_email(email):
    try:
        name, domain = email.split("@")
        if len(name) <= 2:
            masked = name[0] + "*"
        else:
            masked = name[0] + "*" * (len(name) - 2) + name[-1]

        return masked + "@" + domain

    except Exception:
        return "masked_email"