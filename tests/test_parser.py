import pandas as pd
import tempfile
from app.parser import parse_swift_excel


def test_parser_csv_full_coverage():
    """
    Tests the Excel parser against a complete and diverse SWIFT data sample.

    Ensures:
    - HQ and Branch detection based on 'XXX' suffix
    - All required fields are present
    - Casing is properly normalized
    - isHeadquarter flag is correctly interpreted
    """
    # Simulate various SWIFT code types and formats
    data = {
        "SWIFT CODE": [
            "AAAAUS33XXX",   # HQ - ends with XXX
            "AAAABB33",      # Branch - doesn't end with XXX
            "BBBBPLPWXXX",   # HQ - ends with XXX
            "CCCCPLPW",      # Branch - doesn't end with XXX
        ],
        "NAME": [
            "Alpha Bank HQ",
            "Alpha Bank Branch",
            "Beta Bank HQ",
            "Beta Bank Branch"
        ],
        "ADDRESS": [
            "Alpha HQ Address",
            "Alpha Branch Address",
            "Beta HQ Address",
            "Beta Branch Address"
        ],
        "COUNTRY ISO2 CODE": [
            "us",
            "us",
            "pl",
            "pl"
        ],
        "COUNTRY NAME": [
            "united states",
            "united states",
            "poland",
            "poland"
        ]
    }

    df = pd.DataFrame(data)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", mode='w+', delete=False) as f:
        df.to_excel(f.name, index=False)
        parsed = parse_swift_excel(f.name)

    assert len(parsed) == 4

    # check structure and formatting
    for record in parsed:
        assert "swiftCode" in record
        assert "bankName" in record
        assert "address" in record
        assert "countryISO2" in record
        assert "countryName" in record
        assert "isHeadquarter" in record
        assert isinstance(record["isHeadquarter"], bool)
        assert record["countryISO2"].isupper()
        assert record["countryName"].isupper()

    # check specific flags
    assert parsed[0]["isHeadquarter"] is True
    assert parsed[1]["isHeadquarter"] is False
    assert parsed[2]["isHeadquarter"] is True
    assert parsed[3]["isHeadquarter"] is False

    # check casing
    assert parsed[0]["countryISO2"] == "US"
    assert parsed[0]["countryName"] == "UNITED STATES"
    assert parsed[2]["countryISO2"] == "PL"
    assert parsed[2]["countryName"] == "POLAND"
