from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class SwiftCode(Base):
    """
    SQLAlchemy ORM model representing a SWIFT (BIC) code record.

    Fields:
    - id: Auto-incrementing primary key.
    - swiftCode: Unique identifier for the bank branch (8 or 11 character SWIFT/BIC).
    - bankName: Name of the bank.
    - address: Full address of the bank branch.
    - countryISO2: ISO 2-letter country code (e.g., 'US', 'DE').
    - countryName: Full country name.
    - isHeadquarter: Boolean flag indicating whether the record is a headquarter entry.
    """
    __tablename__ = "swift_codes"

    id = Column(Integer, primary_key=True, index=True)
    # SWIFT/BIC Code: Should be 8 or 11 characters long
    swiftCode = Column(String(11), unique=True, nullable=False)

    # Bank name: required
    bankName = Column(String(100), nullable=False)

    # Branch address: required
    address = Column(String(200), nullable=False)

    # Country ISO code: should be exactly 2 characters long
    countryISO2 = Column(String(2), index=True, nullable=False)

    # Country full name
    countryName = Column(String(100), nullable=False)

    # Is this branch the main headquarter?
    isHeadquarter = Column(Boolean, default=False)
