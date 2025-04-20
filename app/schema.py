from typing import List
from pydantic import BaseModel, Field, constr


# ----- Base model for both HQ and branch -----
class SwiftCodeBase(BaseModel):
    """
    Shared base schema for SWIFT code entries (used in both input and output models).
    """
    swift_code: str = Field(..., alias="swiftCode")
    bank_name: str = Field(..., alias="bankName")
    address: str
    country_iso2: str = Field(..., alias="countryISO2")
    is_headquarter: bool = Field(..., alias="isHeadquarter")

    class Config:
        populate_by_name = True
        from_attributes = True
        str_strip_whitespace = True


# ----- For POST request -----
class SwiftCodeCreate(SwiftCodeBase):
    """
    Schema used when creating a new SWIFT code via POST endpoint.
    """
    swiftCode: str
    bankName: str
    address: str
    countryISO2: constr(min_length=2, max_length=2)
    countryName: str
    isHeadquarter: bool


# ----- For single branch or HQ response -----
class SwiftCodeResponse(SwiftCodeCreate):
    """
    Full SWIFT code response schema, returned from single SWIFT code lookup.
    """
    pass


# ----- For branch listing under HQ -----
class SwiftCodeBranch(SwiftCodeBase):
    """
    Schema for branches under a headquarter in a nested structure.
    """
    pass


# ----- GET /swift-codes/{code} if it's a headquarter -----
class SwiftCodeWithBranches(SwiftCodeResponse):
    """
    Response schema that includes a headquarter and all its branches.
    """
    branches: List[SwiftCodeBranch] = []


# ----- GET /swift-codes/country/{ISO2} -----
class CountrySwiftCodesResponse(BaseModel):
    """
    Response schema for all SWIFT codes in a specific country.
    """
    country_iso2: str = Field(..., alias="countryISO2")
    country_name: str = Field(..., alias="countryName")
    swift_codes: List[SwiftCodeBranch] = Field(..., alias="swiftCodes")

    class Config:
        populate_by_name = True
        from_attributes = True
        str_strip_whitespace = True


# ----- Generic success message -----
class MessageResponse(BaseModel):
    """
    Generic message response used for status confirmations.
    """
    message: str
