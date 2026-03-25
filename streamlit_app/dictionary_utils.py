import pandas as pd
import json

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

    # Replace NaN with "NA"
    df = df.fillna("NA")

    registers = df.to_dict(orient="records")

    with open("output.json", "w") as f:
        json.dump(registers, f, indent=4)

    return registers
