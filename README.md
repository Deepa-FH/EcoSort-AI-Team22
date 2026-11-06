# EcoSort AI - Home Task 3

# Presentation Link [YouTube] : **[Presentation video](https://youtu.be/k51r7ukfHzA?is=P5BkhNf_qACyAhTH)**

## Web APIs and Database Access Layers

This is a small, portable **Flask + MySQL** application based on the scan-history part of the EcoSort AI capstone. It stores waste-classification results, exposes them through a REST API, and provides a responsive browser interface for CRUD operations.

## Team 22

| Team member | Matriculation number |
|---|---:|
| Deepa Halapeti | 7225894 |
| Prasad Hule | 7225861 |
| Mayuresh Kumbhar | 7226310 |
| Vijay Kathiresan | 7226794 |

## Features

- Flask web dashboard at `http://localhost:5000`
- MySQL table creation and initial sample records
- Create, read, update and delete waste scan records
- JSON REST API with validation and HTTP status codes
- Statistics endpoint for total scans and average confidence
- Repository layer keeps SQL separate from Flask routes
- Transactions commit successful operations and roll back failures
- Environment-variable configuration; no device-specific paths

## Database operations

| HTTP request | SQL operation | Purpose |
|---|---|---|
| `GET /api/scans` | `SELECT` | List all records |
| `GET /api/scans/<id>` | `SELECT ... WHERE` | Read one record |
| `POST /api/scans` | `INSERT` | Create a record |
| `PUT /api/scans/<id>` | `UPDATE` | Edit a record |
| `DELETE /api/scans/<id>` | `DELETE` | Remove a record |
| `GET /api/stats` | `COUNT`, `AVG`, `GROUP BY` | Dashboard statistics |
| `GET /health` | Connection ping | Health check |

## Folder structure

```text
├── app.py                    # Flask routes and REST API
├── config.py                 # Environment configuration
├── database.py               # MySQL pool and transactions
├── repositories/             # SQL access layer
├── services/                 # Input validation and business logic
├── templates/index.html      # Browser dashboard
├── static/style.css          # Responsive Sortly-style design
├── schema.sql                # Table, indexes and sample data
├── requirements.txt
└── .env.example              # Example database configuration
```

## Run the application

Requirements: Python 3.11/3.12 and MySQL 8.

1. Create the database and table:

```bash
mysql -u root -p < schema.sql
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

3. Install and start:

```bash
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env`. The supplied demonstration credentials match `schema.sql`; change them if required by your MySQL setup.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
python app.py
```

Linux/macOS:

```bash
cp .env.example .env
python app.py
```

Change database credentials with the variables documented in `.env.example`. Never commit real passwords.

## Example API request

```bash
curl -X POST http://localhost:5000/api/scans \
  -H "Content-Type: application/json" \
  -d '{"item_name":"Drink can","material_category":"Metal","confidence":0.92,"disposal_bin":"Yellow bin","city":"Dortmund","notes":"API example"}'
```

The application is intentionally independent of the YOLO model and LLM, so the professor can evaluate Flask, MySQL and the database access layer without additional hardware or API keys.
