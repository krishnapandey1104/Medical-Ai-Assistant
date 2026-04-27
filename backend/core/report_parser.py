import re


# =========================================================
#  ADVANCED REPORT PARSER (UPGRADED )
# =========================================================
def parse_report(text):

    if not text:
        return {
            "structured_data": [],
            "abnormal_values": [],
            "key_lines": []
        }

    lines = text.split("\n")

    structured = []
    abnormal = []

    for line in lines:
        line = line.strip()

        if any(x in line.lower() for x in [
            "hemoglobin", "rbc", "wbc", "platelet",
            "pcv", "rdw", "mcv", "mch", "mchc",
            "neutrophils", "lymphocytes", "eosinophils"
        ]):
            structured.append(line)

            if any(k in line.lower() for k in ["low", "high"]):
                abnormal.append(line)

    return {
        "structured_data": structured[:10],
        "abnormal_values": abnormal[:5],
        "key_lines": structured[:5]
    }







