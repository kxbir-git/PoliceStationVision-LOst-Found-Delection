# Lost & Found Portal — Indian Police Station Edition

> A digital Lost Property and Unclaimed Property management system designed for Indian Police Stations, aligned with CCTNS registers and Digital Personal Data Protection (DPDP) Act, 2023 compliance.

> ⚠ **CRITICAL PROTOTYPE DISCLAIMER**: This system is an academic final-year college project prototype developed for demonstration and workflow evaluation. It is **NOT** approved for live sovereign government deployment. Production deployment by state police forces or law enforcement agencies requires hosting on a MeitY-empanelled cloud (NIC / State Government Data Centre) and statutory security clearance. Vercel is utilized solely for academic prototype demonstration.

---

## 1. Project Overview & Institutional Context

Traditional Indian Police Stations maintain physical general diaries, **Lost Property Registers**, and **Unclaimed Property / Malkhana Registers**. The manual process causes severe operational bottlenecks:
- Citizens reporting lost mobile phones, identity cards, or original certificates often face ambiguity regarding legal FIRs vs. administrative loss reports.
- Unclaimed articles recovered from public places, transport hubs, and post offices remain unlinked in police custody lockers (*Malkhana*).
- Prior systems lacked data minimization, frequently collecting and storing unencrypted national identifiers like full 12-digit Aadhaar numbers in violation of modern privacy principles.

This portal establishes a **police-compliant, human-centered digital register**:
1. **Lost Property Registry (Citizen-Facing):** Enables citizens to register lost articles, mandate statutory legal declarations (deterring fraudulent insurance claims), view clear disclaimers that the slip is an administrative acknowledgement (not an FIR), and print computer-generated slips bearing official registration numbers (`LPR-YYYY-XXXXX`).
2. **Unclaimed Property Registry (Police Custody):** Enables beat constables and station duty officers to log articles taken into police custody (`UCP-YYYY-XXXXX`), recording officer badge numbers, pickup locations, and custody locker references.
3. **Police Station Dashboard:** Provides duty officers and Station House Officers (SHOs) with station-filtered registers, match recommendations between lost and custody items, claim verification, status management, official certificate generation, and an immutable audit trail.
4. **DPDP Act, 2023 Alignment:** Enforces purpose limitation, 12-month retention schedules, strict data minimization (storing only masked last 4 digits of ID proofs), and an active citizen right to request erasure/deletion.

---

## 2. Institutional Terminology

This application uses standardized law enforcement terminology aligned with Indian state police manuals:

| Standardized Police Term | Replaced SaaS / Generic Term | Description |
| :--- | :--- | :--- |
| **Lost Property** | *Lost Item* | Articles reported lost by citizens (documents, wallets, electronics). |
| **Unclaimed Property / Property in Custody** | *Found Item* | Property recovered or deposited into station custody (*Malkhana*). |
| **Police Station Dashboard** | *Admin Panel* | Duty officer control center with jurisdiction filtering. |
| **Citizen** | *User* | Lawful resident accessing station public services. |
| **Acknowledgement Slip** | *Receipt* | Computer-generated proof of report (with clear non-FIR disclaimer). |
| **Registration Number** | *Tracking ID* | Formatted serial number (`LPR-2026-XXXXX` / `UCP-2026-XXXXX`). |

---

## 3. Tech Stack

- **Frontend:** Pure semantic HTML5, CSS3, and modern Vanilla JavaScript (ES6+).
  - ❌ **Zero dependencies:** NO React, NO Vue, NO Tailwind, NO Bootstrap, NO jQuery.
  - Custom design system inspired by official gazette records and notice boards.
  - Mobile-responsive (360px+), WCAG AA compliant.
- **Backend:** Python 3 (Flask REST API) + SQLAlchemy ORM.
- **Authentication:** Flask-Login (session-based cookies) with Werkzeug PBKDF2 password hashing.
- **Database:** SQLite (local development) / PostgreSQL (production connection via `DATABASE_URL`).
- **Image Storage:** Cloudinary API (free tier integration; never stores binary images on serverless filesystem).
- **Deployment Target:** Vercel serverless functions (`api/index.py` with static assets in `public/`).
- **Print Engine:** Custom client-side Print CSS (`print.css`) for high-contrast acknowledgement slips.

---

## 4. Design Philosophy: Human-Made Gazette Notice Board

To avoid the generic, glossy look of SaaS templates, this portal adheres to strict editorial design principles:
- **Background Tone:** Tinted off-white paper canvas (`#F8F7F4`), mimicking official government stationary. Pure `#FFFFFF` is never used for backgrounds.
- **Color Palette:** Single muted forest green accent (`#2C5F2D`) for primary actions and terracotta warning accents (`#B85C38`) for statutory disclaimers. Zero gradients, zero purple, zero glassmorphism.
- **Typography:** Expressive serif headings (`Fraunces`) paired with highly legible, clean sans body typography (`Work Sans`).
- **Notice Board Metaphor:** Public listings feature alternate slight tilts (`transform: rotate(-0.5deg)`), subtle tape header borders, and ledger-style tabular grids.

---

## 5. Directory Structure

```
Police Station Version/
├── public/                       # Frontend assets (served via CDN on Vercel)
│   ├── index.html                # Notice board public search & filter
│   ├── report-lost.html          # Citizen Lost Property reporting form
│   ├── report-unclaimed.html     # Police custody intake form
│   ├── property.html             # Property detail & citizen claim filing
│   ├── dashboard.html            # Citizen self-service & DPDP deletion portal
│   ├── police-dashboard.html     # Police Station Dashboard (audit, claims, matches)
│   ├── login.html                # Citizen / Officer session login
│   ├── register.html             # Account registration (role-based)
│   ├── 404.html                  # Custom human-styled 404 notice
│   ├── style.css                 # Notice-board paper theme stylesheet
│   ├── print.css                 # Clean print stylesheet for official slips
│   └── app.js                    # Pure vanilla JS application controller
├── api/
│   ├── __init__.py
│   └── index.py                  # Complete Flask backend & REST API
├── seed_data.py                  # Realistic Indian police demo dataset
├── requirements.txt              # Production Python dependencies
├── vercel.json                   # Serverless routing & function timeout config
├── .env.example                  # Environment variable configuration template
└── README.md                     # Institutional project documentation
```

---

## 6. Local Development Setup

### Prerequisites
- Python 3.8+ (tested on Python 3.8, 3.11, 3.12)
- pip and virtualenv

### Step-by-Step Instructions

1. **Clone and enter the directory:**
   ```bash
   cd "Police Station Version"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   *Note: For local development, Cloudinary keys are optional. If omitted, the portal operates smoothly without external image uploads.*

5. **Seed the database:**
   Execute the automated seed script to populate realistic Indian police data:
   ```bash
   python seed_data.py
   ```

6. **Launch local development server:**
   ```bash
   python api/index.py
   # Or using Flask CLI:
   # flask --app api/index run --port 5000 --debug
   ```

7. **Access the application:**
   Open your browser to: **[http://localhost:5000](http://localhost:5000)**

---

## 7. Demo Accounts & Verification Credentials

The seed script initializes three accounts for testing all institutional workflows:

| Role | Name | Email | Password | Assigned Police Station / Jurisdiction |
| :--- | :--- | :--- | :--- | :--- |
| **Police Officer** | Inspector Rajesh Kumar | `officer@demo.local` | `demo1234` | Kotwali Police Station, Lucknow |
| **Citizen 1** | Priya Sharma | `citizen1@demo.local` | `demo1234` | N/A (Citizen) |
| **Citizen 2** | Amit Verma | `citizen2@demo.local` | `demo1234` | N/A (Citizen) |

---

## 8. Police Taxonomy of Property Categories

In compliance with standard state police property registers, categories are restricted to:
1. `Documents` (Aadhaar, PAN, Driving License, Voter ID, Passport, Educational Marksheets)
2. `Electronic Devices` (Mobile Phones, Laptops, Tablets, Earphones, Smartwatches)
3. `Bags & Luggage` (Backpacks, Suitcases, Briefcases, Duffle Bags)
4. `Wallet / Purse` (Wallets, Coin Pouches, Ladies Handbags)
5. `Keys` (Automobile Ignition Keys, House Keys, Padlock Bunches)
6. `Jewellery` (Gold/Silver Ornaments, Chains, Bangles, Rings)
7. `Vehicles` (Bicycles, Two-wheelers, Four-wheelers)
8. `Books / Stationery` (Academic Textbooks, Diaries, Legal Files)
9. `Clothing / Accessories` (Jackets, Shawls, Watches, Eyeglasses)
10. `Other` (Water Bottles, Umbrellas, Miscellaneous personal effects)

---

## 9. Backend REST API Specification

All backend endpoints are prefixed with `/api`.

### Authentication
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register new citizen account (hashes password with PBKDF2) | Public |
| `POST` | `/api/auth/login` | Authenticate and start session | Public |
| `POST` | `/api/auth/logout` | Terminate current session | Authenticated |
| `GET` | `/api/auth/me` | Fetch active user identity & role | Authenticated |

### Property Register
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/properties` | List properties with filters (`type`, `category`, `q`, `station`, `status`, `reporter=me`) | Public / Filtered |
| `POST` | `/api/properties` | Register Lost or Unclaimed Property (generates `LPR`/`UCP` number, masks ID) | Authenticated |
| `GET` | `/api/properties/<id>` | Retrieve full details (masks PII for non-owners/non-officers) | Public / Masked |
| `PATCH` | `/api/properties/<id>/status` | Update status (`approved`, `returned`) & create audit record | Police Only |
| `DELETE` | `/api/properties/<id>` | Soft-delete / submit erasure request for citizen's own report | Owner Only |

### Claims & Dispute Management
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/properties/<id>/claim` | Submit ownership claim with descriptive proof | Authenticated |
| `GET` | `/api/claims` | List claims filtered by officer's station jurisdiction | Police Only |
| `PATCH` | `/api/claims/<id>` | Approve or reject claim (approving automatically marks item as returned) | Police Only |

### Intelligence & Matching Engine
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/properties/<id>/matches` | Score candidate matches between Lost ↔ Unclaimed properties | Police Only |

### Police Station Dashboard
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/dashboard/stats` | Station counts: total lost, custody items, returned, pending claims | Police Only |
| `GET` | `/api/dashboard/audit-log` | Comprehensive station ledger of all status modifications | Police Only |
| `POST` | `/api/properties/<id>/certificate` | Generate printable HTML acknowledgement slip | Police Only |

### Data Protection (DPDP Act)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/users/request-deletion` | Initiate statutory right to erasure across all citizen reports | Authenticated |

---

## 10. Data Protection & DPDP Act, 2023 Alignment

This portal implements digital governance best practices in accordance with India's **Digital Personal Data Protection (DPDP) Act, 2023**:

1. **Strict Data Minimization (Section 6):**
   - Government identification numbers (Aadhaar, PAN, Driving License, Voter ID) are **never stored in full**.
   - The frontend immediately truncates entries so that only document type and the last 4 digits (e.g., `XXXX-XXXX-4821`) reach the server.
2. **Explicit Consent & Purpose Limitation (Section 5 & 6):**
   - Every reporting form includes an unambiguous, non-pre-ticked consent notice explaining purpose (*loss documentation and matching only*) and the statutory retention period.
3. **Statutory Retention Policy:**
   - Active lost property entries are flagged for review and archival after **12 months**.
4. **Right to Erasure & Revocation of Consent (Section 12):**
   - Citizens can trigger "Request Data Deletion" directly from their dashboard. Deletion requests soft-delete public records immediately and initiate a 30-day anonymization window for station historical records.
5. **Accountability & Immutable Audit Trail:**
   - Every status modification, approval, claim decision, and deletion request records the officer ID, timestamp, prior value, and new value in the `audit_logs` table.

---

## 11. CCTNS Compatibility & NCRB Future Scope

### Conceptual Register Mapping
This prototype mirrors the core data models of the **Crime and Criminal Tracking Network & Systems (CCTNS)** core application:

| Portal Data Field | CCTNS Register Equivalent | Applicable CCTNS Register |
| :--- | :--- | :--- |
| `registration_number` | General Diary / Register Entry Number | Lost Property Register |
| `applicant_name` | Informant / Complainant Name | Lost Property Register |
| `category` | Property Classification Class | Lost & Unclaimed Registers |
| `description` / `how_lost` | G.D. Circumstance Narrative | Lost Property Register |
| `date_lost` / `location_lost` | Date, Time & Place of Occurrence | Lost Property Register |
| `police_station` | Police Station Code / Name | Both Registers |
| `officer_name` & `officer_badge_id` | IO / Duty Officer Badge Identifier | Unclaimed / Seizure Register |
| `current_location` | Malkhana Rack / Locker Reference | Unclaimed Property Register |
| `status` (`pending`/`approved`/`returned`) | Property Disposal Status | Both Registers |

### Future Scope: Live CCTNS Integration
Direct integration with CCTNS via NCRB-approved APIs requires:
- Formal No Objection Certificate (NOC) and API access credentials from the **National Crime Records Bureau (NCRB)**.
- Site security audit and certification by a **CERT-In empanelled auditing firm**.
- Virtual Private Network (VPN) peering into the State Police Wide Area Network (SWAN / CCTNS intranet).

*This prototype is purposefully designed with schema compatibility to enable seamless ingestion via NCRB REST APIs once institutional clearance is obtained.*

---

## 12. Production Deployment & Cloud Hosting Notice

### ⚠ SQLite Serverless Warning
In local development, the application stores data in `lostfound.db` via SQLite.
**SQLite does NOT persist on Vercel Serverless Functions**, as each serverless container runs in an ephemeral, stateless execution environment.

### Production Deployment Steps
1. **Provision a PostgreSQL database:**
   Obtain a free or managed PostgreSQL instance (e.g., Neon, Supabase, Vercel Postgres, or AWS RDS).
2. **Configure Vercel Environment Variables:**
   In your Vercel Project Dashboard (`Settings > Environment Variables`), supply:
   - `DATABASE_URL`: `postgresql://<user>:<password>@<host>:<port>/<dbname>?sslmode=require`
   - `SECRET_KEY`: A cryptographically secure random string.
   - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`: (Optional) Free tier Cloudinary credentials for citizen image uploads.
3. **Deploy via GitHub / Vercel CLI:**
   ```bash
   vercel --prod
   ```

### Statutory Government Hosting Notice
For actual deployment by a state police department or government agency:
- **MeitY-Empanelled Cloud:** Applications must reside within sovereign Indian data centres (NIC National Data Centre, S3WaaS, or MeitY-empanelled CSPs).
- **GIGW 3.0 Compliance:** Must meet the Guidelines for Indian Government Websites including bilingual localization (Hindi & regional languages) and screen reader accessibility.
