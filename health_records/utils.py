def calculate_health_score(record):

    score = 100

    # ==========================
    # BMI
    # ==========================

    try:
        bmi = record.weight / ((record.height / 100) ** 2)

        if bmi < 18.5:
            score -= 15

        elif bmi > 24.9 and bmi <= 29.9:
            score -= 10

        elif bmi >= 30:
            score -= 20

    except:
        pass

    # ==========================
    # Blood Pressure
    # ==========================

    try:
        systolic = int(str(record.blood_pressure).split("/")[0])

        if systolic > 140:
            score -= 20

        elif systolic > 120:
            score -= 10

    except:
        pass

    # ==========================
    # Glucose Level
    # ==========================

    try:
        glucose = float(record.glucose_level)

        if glucose > 180:
            score -= 20

        elif glucose > 140:
            score -= 10

    except:
        pass

    # ==========================
    # ML Prediction Risk
    # ==========================

    risk = str(record.risk).upper()

    if risk == "HIGH RISK":
        score -= 30

    elif risk in ["MEDIUM RISK", "MODERATE RISK"]:
        score -= 15

    elif risk == "LOW RISK":
        score -= 0

    # Final Score
    score = max(0, min(score, 100))

    return score