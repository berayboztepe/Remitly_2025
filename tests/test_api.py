import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.model import SwiftCode

client = TestClient(app)

# Test data
swift_payload = {
    "swiftCode": "TESTUS99XXX",
    "bankName": "Test Bank",
    "address": "123 Wall Street",
    "countryISO2": "US",
    "countryName": "UNITED STATES",
    "isHeadquarter": True
}

branch_payload = {
    "swiftCode": "TESTUS99001",
    "bankName": "Test Branch",
    "address": "456 Main Street",
    "countryISO2": "US",
    "countryName": "UNITED STATES",
    "isHeadquarter": False
}

# to run fixture automatically runs once at the end of all tests to delete test entries avoid duplicates between test runs
@pytest.fixture(scope="session", autouse=True)
def cleanup_after_tests():
    yield  # run all tests first

    # cleanup
    db = SessionLocal()
    try:
        # Delete test entries by prefix or pattern
        deleted = db.query(SwiftCode).filter(SwiftCode.swiftCode.startswith("TEST")).delete(synchronize_session=False)
        db.commit()
        print(f"✅ Cleanup complete: {deleted} test records deleted.")
    finally:
        db.close()

def test_add_swift_code():
    """Should add a valid SWIFT HQ code successfully."""
    response = client.post("/v1/swift-codes", json=swift_payload)
    assert response.status_code == 200
    assert response.json()["message"] == "SWIFT code added successfully."


def test_add_duplicate_swift_code():
    """Should reject duplicate SWIFT code with 400 error."""
    response = client.post("/v1/swift-codes", json=swift_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "SWIFT code already exists."


def test_get_hq_code_with_branches():
    """Should return HQ code with linked branches."""
    # add a branch
    client.post("/v1/swift-codes", json=branch_payload)

    # now get the HQ
    response = client.get(f"/v1/swift-codes/{swift_payload['swiftCode']}")
    assert response.status_code == 200
    data = response.json()
    assert data["isHeadquarter"] is True
    assert "branches" in data
    assert any(branch["swiftCode"] == branch_payload["swiftCode"] for branch in data["branches"])


def test_add_swift_code_missing_field():
    """Should return 422 if a required field is missing."""
    # "bankName" is missing
    incomplete_payload = {
        "swiftCode": "MISSUS01XXX",
        "address": "Missing Field Ave",
        "countryISO2": "US",
        "countryName": "UNITED STATES",
        "isHeadquarter": True
    }

    response = client.post("/v1/swift-codes", json=incomplete_payload)
    assert response.status_code == 422
    assert "bankName" in response.text  # schema validation failed



def test_get_by_country():
    """Should return all SWIFT codes for a given country."""
    response = client.get("/v1/swift-codes/country/US")
    assert response.status_code == 200
    data = response.json()
    assert data["countryISO2"] == "US"
    assert len(data["swiftCodes"]) >= 2


def test_delete_swift_code():
    """Should successfully delete a valid SWIFT code."""
    response = client.delete(f"/v1/swift-codes/{branch_payload['swiftCode']}")
    assert response.status_code == 200
    assert response.json()["message"] == "SWIFT code deleted successfully."


def test_get_nonexistent_code():
    """Should return 404 for unknown SWIFT code."""
    response = client.get("/v1/swift-codes/DOESNOTEXIST")
    assert response.status_code == 404
    assert response.json()["detail"] == "SWIFT code not found"


def test_delete_nonexistent_code():
    """Should return 404 when trying to delete a non-existent SWIFT code."""
    response = client.delete("/v1/swift-codes/DOESNOTEXIST")
    assert response.status_code == 404
    assert response.json()["detail"] == "SWIFT code not found"


def test_add_invalid_swift_code():
    """Should return 422 for invalid SWIFT code or ISO format."""
    bad_data = {
        "swiftCode": "123", # Too short
        "bankName": "Bad Bank",
        "address": "Nowhere",
        "countryISO2": "USA", # Too long
        "countryName": "United States",
        "isHeadquarter": True
    }
    response = client.post("/v1/swift-codes", json=bad_data)
    assert response.status_code == 422
