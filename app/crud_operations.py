from sqlalchemy.orm import Session
from typing import List, Optional

from app.model import SwiftCode
from app.schema import SwiftCodeCreate


def get_swift_code_by_code(db: Session, swift_code: str) -> Optional[SwiftCode]:
    """Retrieve a single SWIFT code entry by its SWIFT code.

    :param db: Database session.
    :param swift_code: SWIFT code string to search.
    :return: SwiftCode object or None if not found.
    """
    return db.query(SwiftCode).filter_by(swiftCode=swift_code).first()


def get_swift_codes_by_country(db: Session, country_iso2: str) -> List[SwiftCode]:
    """Retrieve SWIFT code entries for a specific country.
    
    :param db: Database session.
    :param country_iso2: ISO2 country code.
    :return: List of SwiftCode objects.
    """
    return db.query(SwiftCode).filter_by(countryISO2=country_iso2.upper()).all()


def get_branches_for_headquarter(db: Session, swift_code: str) -> List[SwiftCode]:
    """
    Retrieve branches associated with a headquarter SWIFT code (first 8 chars).

    :param db: Database session.
    :param swift_code: Headquarter SWIFT code.
    :return: List of SwiftCode objects for branches.
    """
    # Must match first 8 characters (BIC root)
    root_code = swift_code[:8]
    return db.query(SwiftCode).filter(
        SwiftCode.swiftCode.startswith(root_code),
        SwiftCode.isHeadquarter == False
    ).all()


def create_swift_code(db: Session, swift_data: SwiftCodeCreate) -> Optional[SwiftCode]:
    """
    Create a new SWIFT code entry.

    :param db: Database session.
    :param swift_data: Data for new SWIFT code entry.
    :return: Newly created SwiftCode object or None if already exists.
    """
    existing = get_swift_code_by_code(db, swift_data.swift_code)
    if existing:
        return None

    swift_obj = SwiftCode(**swift_data.model_dump(by_alias=True))
    db.add(swift_obj)
    db.commit()
    db.refresh(swift_obj)
    return swift_obj


def delete_swift_code(db: Session, swift_code: str) -> bool:
    """
    Delete a SWIFT code entry.

    :param db: Database session.
    :param swift_code: SWIFT code to delete.
    :return: True if deleted successfully, False otherwise.
    """
    existing = get_swift_code_by_code(db, swift_code)
    if not existing:
        return False

    db.delete(existing)
    db.commit()
    return True


def bulk_insert_swift_codes(db: Session, entries: List[SwiftCodeCreate]) -> int:
    """
    Insert multiple SWIFT code entries in bulk.
    
    :param db: Database session.
    :param entries: List of SWIFT code data entries.
    :return: Number of successfully inserted entries.
    """
    count = 0
    for entry in entries:
        if not get_swift_code_by_code(db, entry.swift_code):
            db.add(SwiftCode(**entry.model_dump(by_alias=True)))
            count += 1
    db.commit()
    return count
