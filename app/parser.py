import pandas as pd
from typing import List, Dict
import os


def parse_swift_excel(file_path: str) -> List[Dict]:
    """
    Parses a SWIFT code Excel file into a list of dictionaries.

    Expected Columns:
    - SWIFT CODE: 8 or 11-character bank identifier.
    - NAME: Bank name.
    - ADDRESS: Full bank address.
    - COUNTRY ISO2 CODE: Two-letter ISO country code.
    - COUNTRY NAME: Full country name.

    
    :param file_path: Path to the Excel (.xlsx) file.

    :return: List of dictionaries, each representing a SWIFT code entry.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Excel file not found at path: {file_path}")

    try:
        df = pd.read_excel(file_path, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"Failed to read Excel file: {e}")
    result = []
    
    for _, row in df.iterrows():
        try:
            record = {
                "swiftCode": row["SWIFT CODE"],
                "bankName": row["NAME"],
                "address": row["ADDRESS"],
                "countryISO2": str(row["COUNTRY ISO2 CODE"]).upper(),
                "countryName": str(row["COUNTRY NAME"]).upper(),
                "isHeadquarter": str(row["SWIFT CODE"]).endswith("XXX")
            }
            result.append(record)
        except Exception as e:
            # Skip and log malformed row if necessary
            print(f"Skipping invalid row due to error: {e}")

    return result
