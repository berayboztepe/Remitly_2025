# SWIFT Code Management API

A fully containerized RESTful FastAPI service for managing global SWIFT (BIC) codes. This project provides a robust, extensible backend that handles data ingestion from Excel, strict input validation, efficient querying, and a clean interface for integration or direct consumption.

---

## 📁 Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI app with route definitions and startup logic
│   ├── crud_operations.py   # Business logic and database interaction
│   ├── parser.py            # Parses and validates Excel data
│   ├── database.py          # SQLAlchemy session and database configuration
│   ├── model.py             # SQLAlchemy ORM model (SwiftCode)
│   └── schema.py            # Pydantic schemas with validation and aliasing
│
├── data/
│   └── Interns_2025_SWIFT_CODES.xlsx   # Optional seed data file (Excel)
│
├── tests/
│   ├── test_api.py          # Comprehensive endpoint tests including success and failure cases
│   └── test_parser.py       # Excel parser tests ensuring branch/HQ logic
│
├── Dockerfile               # Defines how to containerize the API
├── docker-compose.yml       # Multi-container orchestration (API + PostgreSQL)
├── requirements.txt         # Python dependencies
├── .env                     # Environment variable configuration (excluded from VCS)
└── README.md
```

---

## 🚀 Features

- ✅ **Add, retrieve, and delete SWIFT codes**
- ✅ **Headquarter and branch differentiation**
- ✅ **List SWIFT codes per country (with full info)**
- ✅ **Excel data import at app startup (via parser)**
- ✅ **Strict data validation using Pydantic V2**
- ✅ **Unit + integration testing with automated cleanup**
- ✅ **Fully containerized (Docker & Compose)**
- ✅ **PostgreSQL-backed with SQLAlchemy ORM**

---

## 📦 Installation & Usage

### Prerequisites
- Docker & Docker Compose (highly recommended)

### Setup
Create a `.env` file at the project root:
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/swiftdb
```

### Build & Run
```bash
docker-compose up --build
```

### Access
- API will be available at: `http://localhost:8080`
- Database runs on port `5432` inside container

---

## 🧪 Testing

Tests are located in `tests/` and cover both API endpoints and the parser logic.

### Run all tests:
```bash
docker-compose exec api pytest tests/
```

### Tests include:
- ✔ Adding valid and invalid SWIFT entries
- ✔ Duplicate protection
- ✔ Missing field validation
- ✔ Parsing Excel files and detecting branches vs HQs
- ✔ Deletion and edge case coverage

### Test data cleanup:
At the end of every full test session, any SWIFT code entries starting with `TEST` are removed from the database automatically.

---

## 🧠 API Endpoints Overview

### `GET /v1/swift-codes/{swiftCode}`
Retrieve SWIFT code details. If HQ, includes `branches` field.

### `GET /v1/swift-codes/country/{isoCode}`
Get all codes for a country using ISO2 format (e.g. `US`).

### `POST /v1/swift-codes`
Create a new code. Example format:
```json
{
  "swiftCode": "EXAMPLUSXXX",
  "bankName": "Example Bank",
  "address": "123 Bank St",
  "countryISO2": "US",
  "countryName": "UNITED STATES",
  "isHeadquarter": true
}
```

### `DELETE /v1/swift-codes/{swiftCode}`
Remove a SWIFT code by code string.

---

## 🔐 Validation Rules

Validation is strict and enforced through Pydantic and schema constraints:
- `swiftCode`: 8 to 11 alphanumeric characters (including possible post-string: XXX)
- `countryISO2`: Exactly 2 uppercase letters
- `bankName`, `address`, `countryName`: Must be non-empty strings
- `isHeadquarter`: Must be boolean
- Duplicate SWIFT codes return 400 with clear message

### ❗ Error Handling

- If a required field is missing (e.g. `bankName`), the API returns:
  - **422 Unprocessable Entity** with a descriptive validation error.

- If a SWIFT code format is invalid (e.g. too short or non-alphanumeric), the API returns:
  - **422 Unprocessable Entity** with a field-level validation message.

- If a duplicate SWIFT code is submitted (already exists in DB), the API returns:
  - **400 Bad Request** with message: `"SWIFT code already exists."`

- If a SWIFT code is queried or deleted and it does not exist in the database, the API returns:
  - **404 Not Found** with message: `"SWIFT code not found"` (e.g. `bankName`)

---

`swiftCode` Format Reference:

| Part         | Length | Description                          |
|--------------|--------|--------------------------------------|
| Bank Code    | 4      | Only letters                         |
| Country Code | 2      | Only letters (ISO country code)      |
| Location     | 2      | Letters or digits                    |
| Branch Code  | 3      | Optional — letters or digits         |


---

## 🐳 Docker Setup

### Services
- **api**: Runs the FastAPI app
- **db**: PostgreSQL 13 with data persistence via volume

### Compose Features
- `depends_on` ensures DB starts first
- Excel file parsed on container startup if located in `data/`
- PostgreSQL data persisted with named volume (`pgdata`)

---

## 🗄 PostgreSQL Access

Database is running on port `5432` inside Docker. You can connect using any PostgreSQL client or the CLI:

**Credentials:**
- Host: `localhost`
- Port: `5432`
- User: `postgres`
- Password: `postgres`
- Database name: `swiftdb`

**CLI connection command:**
```bash
psql -h localhost -p 5432 -U postgres -d swiftdb
```

- Excel file parsed on container startup if located in `data/`
- PostgreSQL data persisted with named volume (`pgdata`)

**Important:** Please verify if the database loaded properly. If the data is missing, there may be an issue with reading or parsing the Excel file during startup. Check the container logs to begin troubleshooting.

---

## ⚙️ Dev Tips

- Run with `uvicorn app.main:app --reload` locally for hot reloads
- Keep `.env` out of source control (included in `.gitignore`)
- After building and running the app via Docker, you can test the API locally by visiting http://localhost:8080/docs to access the interactive Swagger UI. Keep in mind that no Frontend operation is performed!
- API server listens on `0.0.0.0:8080` so it's accessible from host

---

## 🔍 Extra Notes

- Excel parser auto-detects `isHeadquarter` based on `swiftCode` ending with `XXX`
- Data is normalized to uppercase during import
- Parser throws informative errors if required columns are missing

---

## ✅ Technologies Used

- **FastAPI**: API framework
- **SQLAlchemy**: ORM for PostgreSQL
- **Pydantic V2**: Input/output validation
- **Docker**: Containerized environment
- **Pytest**: Testing framework
- **PostgreSQL**: Relational DB for persistence

---

## 🧾 Acknowledgment
This project is completed for Remitly-2025 Internship task. This project is a custom backend for managing SWIFT code hierarchies and structured global financial identifiers.

---

## 👤 Author
Emre Beray Boztepe

