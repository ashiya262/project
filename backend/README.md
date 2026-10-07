# Smart Battery Backend

FastAPI backend for the Smart Battery Lifecycle System.

## Run locally (PowerShell)

From this directory:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SECRET_KEY = "replace-this-with-a-long-random-secret"
$env:DATABASE_URL = "mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/smart_battery"
uvicorn main:app --reload
```

The default database is a local SQLite file (`smart_battery.db`). Set
`DATABASE_URL` as above to use MySQL. URL-encode special characters in a MySQL
password. The app creates missing tables on startup. The complete SQL setup
script is `database/mysql_setup.sql`. Do not commit credentials.

## MySQL setup

Start MySQL and run this in PowerShell from `backend`:

```powershell
Get-Content ..\database\mysql_setup.sql | mysql -u root -p
```

For a fresh database, running the app will also create all tables after the
database itself has been created. Existing installations created with an older
schema need the following one-time migration (only run this if these columns
are not already present); the startup table creation then adds the new tables:

```sql
ALTER TABLE batteries
  ADD COLUMN serial_number VARCHAR(100) NULL,
  ADD COLUMN manufacturer VARCHAR(150) NULL,
  ADD COLUMN chemistry VARCHAR(100) NULL;

ALTER TABLE battery_readings
  ADD COLUMN measured_capacity FLOAT NULL,
  ADD COLUMN cycle_count INT NULL;
```

### Aiven and MySQL Workbench

The backend and Workbench must use the same Aiven host, port, username,
password, and `smart_battery` schema. In Workbench, open the Aiven connection
and run `SELECT DATABASE();` and `SHOW TABLES;` to confirm the schema and API
tables. The backend reads `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and
`DB_NAME` from this directory's `.env`; restart Uvicorn after changing them.

After logging in through Swagger (`POST /api/auth/login`), click **Authorize**
and provide the returned bearer token before calling protected write APIs.
`POST /api/batteries` and `POST /api/batteries/{battery_id}/readings` commit
their rows to the configured MySQL database.

Interactive API documentation: `http://127.0.0.1:8000/docs`.

## API surface

- Authentication: `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- Batteries: `POST/GET /api/batteries`, `GET/PUT /api/batteries/{battery_id}`
- Readings: `POST/GET /api/batteries/{battery_id}/readings`
- Predictions and decision: `/soh`, `/rul`, `/prediction`, `/decision`, `/decision/why`
- Lifecycle: `/second-life`, `POST /what-if`, `POST /reassessment`, `/passport`
- Alerts: `GET/POST /api/alerts`, `GET /api/batteries/{battery_id}/alerts`,
  `PUT /api/alerts/{alert_id}/read`
- Dashboard and analytics: `/api/dashboard/summary`,
  `/api/batteries/{battery_id}/history`, `/api/analytics/{soh,temperature,voltage}`

All battery, reading, alert, dashboard and analytics endpoints require the
`Authorization: Bearer <access_token>` header returned by `/api/auth/login`.
Only register/login are public; `/api/auth/me` also requires that bearer token.
For a battery path such as `GET /api/batteries/{battery_id}`, use the
`battery_id` value from the response. The numeric `id` from `GET /api/batteries`
is also accepted for backwards compatibility.

The current SOH/RUL outputs are rule-based estimates, not a trained or
validated battery prognostics model. For measured-capacity SOH, send
`measured_capacity` in a reading and set the battery's rated `capacity`.
