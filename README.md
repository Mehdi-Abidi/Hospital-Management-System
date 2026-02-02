# GDPR-Compliant Mini Hospital Management System

A privacy-first Streamlit dashboard that demonstrates how the GDPR principles of lawful, fair, and transparent data processing map to the CIA triad (Confidentiality, Integrity, Availability). The app encrypts sensitive patient data, enforces role-based access control, keeps immutable audit logs, and offers backup/export capabilities for business continuity.

## Key Features

- **Confidentiality:**
  - Patient names, contacts, and diagnoses are encrypted at rest using Fernet keys.
  - Receptionists can capture/update data without ever seeing sensitive fields.
- **Integrity:**
  - Every action (login, anonymize, create/update, export, log review) is recorded with timestamp, role, and context.
  - Update workflow automatically re-applies anonymization to preserve consistency.
- **Availability:**
  - SQLite + Streamlit combo keeps the system lightweight yet reliable, with graceful error handling and uptime indicators.
  - System footer exposes uptime + last sync so operators know the platform health at a glance.
- **Bonus Enhancements:** real-time activity bar chart, GDPR consent banner, data retention insights, and anonymization refresh control.

## Project Structure

```
.
├── app.py               # Streamlit entrypoint with RBAC views and dashboards
├── config.py            # Loads/persists Fernet encryption keys from .env
├── database.py          # SQLite helpers, encryption-aware CRUD, audit logging
├── db_setup.py          # CLI helper to initialize or reset the database
├── security.py          # Hashing, encryption/decryption, masking utilities
├── requirements.txt     # Python dependencies
├── .env.example         # Template for Fernet key configuration
├── README.md            # This guide
└── data/
    └── hospital.db      # Auto-created SQLite database
```

## Quick Start

### Prerequisites

- Python 3.9+ installed
- pip package manager

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd GDPR-Compliant-Mini-Hospital-Management-System
   ```

2. **Create & activate a virtual environment:**

   **Windows (PowerShell):**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure encryption key:**

   Generate a Fernet key:

   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

   Paste the output into `.env`:

   ```
   FERNET_KEY=<your-generated-key>
   ```

   **Note:** If you skip this step, `config.py` will auto-generate and store a key in `.env` on first run.

5. **Initialize the database with seed data:**

   ```bash
   python db_setup.py
   ```

6. **Run the dashboard:**

   ```bash
   streamlit run app.py
   ```

7. **Access the application:**

   Open your browser to `http://localhost:8501`

## Default Accounts

| Role         | Username      | Password   |
| ------------ | ------------- | ---------- |
| Admin        | `admin`       | `admin123` |
| Doctor       | `Dr. Bob`     | `doc123`   |
| Receptionist | `Alice_recep` | `rec123`   |

> ⚠️ **Security Notice:** Passwords are stored as SHA-256 hashes. Change default credentials in production environments.

## Features by Role

### Admin

- View raw and anonymized patient data
- Add, update, and delete patient records
- Refresh anonymization fields
- Export patient data backup (CSV)
- Access full audit logs
- View activity visualizations
- Monitor data retention compliance

### Doctor

- View anonymized patient data only
- Read-only access to patient registry
- Cannot modify or export data

### Receptionist

- Add new patient records
- Update existing patient information
- Delete patient records
- View anonymized data only
- No access to audit logs

## GDPR Compliance Features

| Feature                         | Implementation                          |
| ------------------------------- | --------------------------------------- |
| **Lawful Processing**           | Consent banner required before login    |
| **Data Minimization**           | Only essential fields collected         |
| **Purpose Limitation**          | Role-based access controls              |
| **Storage Limitation**          | 365-day retention monitor               |
| **Integrity & Confidentiality** | Fernet encryption + audit logs          |
| **Accountability**              | Complete action logging with timestamps |
| **Right to Erasure**            | Delete patient functionality            |
| **Data Portability**            | CSV export capability                   |

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);
```

### Patients Table

```sql
CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,              -- Encrypted
    contact TEXT NOT NULL,            -- Encrypted
    diagnosis TEXT NOT NULL,          -- Encrypted
    anonymized_name TEXT,
    anonymized_contact TEXT,
    anonymized_diagnosis TEXT,
    date_added TEXT NOT NULL
);
```

### Logs Table

```sql
CREATE TABLE logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    role TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    details TEXT
);
```

## Development

### Reset Database

```bash
python db_setup.py --reset
```

### Run Tests

```bash
pytest
```

### Code Structure

- `app.py` - Streamlit UI and routing logic
- `database.py` - Data access layer with encryption integration
- `security.py` - Cryptographic operations (Fernet, SHA-256)
- `config.py` - Environment variable management
- `db_setup.py` - Database initialization script

## Security Considerations

1. **Encryption at Rest:** All PII fields are encrypted using Fernet (AES-128 in CBC mode)
2. **Password Hashing:** SHA-256 hashing for user credentials
3. **Audit Trail:** Immutable logs for all data access and modifications
4. **Session Management:** Streamlit session state with logout functionality
5. **Input Validation:** Form validation prevents empty/malformed data

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This is a **demonstration system** using synthetic data. Not intended for production use with real patient information without proper security audit, compliance review, and infrastructure hardening.
