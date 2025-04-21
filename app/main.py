from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app import crud_operations as crud
from app import schema as schemas
from app.parser import parse_swift_excel

import os

# FastAPI initialization
app = FastAPI(
    title="SWIFT Code Service",
    version="1.0.0",
    description="RESTful API for managing global SWIFT (BIC) codes"
)


Base.metadata.create_all(bind=engine)

# data from Excel file
DATA_FILE = os.path.join(os.getcwd(), "data", "Interns_2025_SWIFT_CODES.xlsx")

print(f"Looking for Excel file at: {DATA_FILE}")
if os.path.exists(DATA_FILE):
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        records = parse_swift_excel(DATA_FILE)
        count = crud.bulk_insert_swift_codes(
            db, [schemas.SwiftCodeCreate(**entry) for entry in records]
        )
        print(f"Preloaded {count} records from Excel.")
        db.close()
    except Exception as e:
        print(f"Failed to preload Excel data: {e}")
else:
    print("No Excel data found in /data folder.")


@app.get("/v1/swift-codes/{swift_code}", response_model=schemas.SwiftCodeWithBranches)
def get_swift_code(swift_code: str, db: Session = Depends(get_db)):
    """
    Retrieve details of a SWIFT code, including associated branch codes if it's a headquarter.

    :param swift_code: The SWIFT code to retrieve.
    :return:  SwiftCodeWithBranches schema containing the code and its branches (if any).
    """
    code = crud.get_swift_code_by_code(db, swift_code)
    if not code:
        raise HTTPException(status_code=404, detail="SWIFT code not found")

    if code.isHeadquarter:
        branches = crud.get_branches_for_headquarter(db, swift_code)
        return schemas.SwiftCodeWithBranches(
            **code.__dict__,
            branches=[schemas.SwiftCodeBranch(**b.__dict__) for b in branches]
        )
    return schemas.SwiftCodeWithBranches(**code.__dict__, branches=[])


@app.get("/v1/swift-codes/country/{country_iso}", response_model=schemas.CountrySwiftCodesResponse)
def get_by_country(country_iso: str, db: Session = Depends(get_db)):
    """
    Retrieve all SWIFT codes for a specific country.

    :param country_iso: ISO 2-letter country code (e.g., US, GB).
    :return: List of SWIFT codes and the country's name.
    """
    records = crud.get_swift_codes_by_country(db, country_iso)
    if not records:
        raise HTTPException(status_code=404, detail="No SWIFT codes found for this country")
    return schemas.CountrySwiftCodesResponse(
        country_iso2=country_iso.upper(),
        country_name=records[0].countryName,
        swift_codes=[schemas.SwiftCodeBranch(**r.__dict__) for r in records]
    )


@app.post("/v1/swift-codes", response_model=schemas.MessageResponse)
def add_swift_code(swift_code: schemas.SwiftCodeCreate, db: Session = Depends(get_db)):
    """
    Add a new SWIFT code entry to the database.

    :param swift_code: Payload containing SWIFT code details.
    :return: Success message if inserted or error if already exists.
    """
    created = crud.create_swift_code(db, swift_code)
    if not created:
        raise HTTPException(status_code=400, detail="SWIFT code already exists.")
    return {"message": "SWIFT code added successfully."}


@app.delete("/v1/swift-codes/{swift_code}", response_model=schemas.MessageResponse)
def delete_swift_code(swift_code: str, db: Session = Depends(get_db)):
    """
    Delete a SWIFT code from the database.

    :param swift_code: The SWIFT code to delete.
    :return: Success message if deleted, 404 if code not found.
    """
    deleted = crud.delete_swift_code(db, swift_code)
    if not deleted:
        raise HTTPException(status_code=404, detail="SWIFT code not found")
    return {"message": "SWIFT code deleted successfully."}
