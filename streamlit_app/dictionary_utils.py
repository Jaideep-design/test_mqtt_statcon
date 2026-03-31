import pandas as pd
import json
import numpy as np

def excel_to_json(uploaded_file):

    df = pd.read_excel(uploaded_file)

    required_columns = [
        "Sr. No.",
        "Parameter",
        "Short name",
        "Size [byte]",
        "Index",
        "Total Upto",
        "Scaling Factor",
        "Offset",
        "Data format",
        "Units"
    ]

    df = df.loc[:, required_columns]

    # 🔑 IMPORTANT: convert to object first
    df = df.astype(object)

    # Replace NaN with None
    df = df.where(pd.notnull(df), None)

    registers = df.to_dict(orient="records")

    # Extra safety (optional but robust)
    def clean_nan(obj):
        if isinstance(obj, dict):
            return {k: clean_nan(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_nan(v) for v in obj]
        elif isinstance(obj, float) and np.isnan(obj):
            return None
        return obj

    registers = clean_nan(registers)

    with open("output.json", "w") as f:
        json.dump(registers, f, indent=4)

    return registers
