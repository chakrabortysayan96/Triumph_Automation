# Triumph Automation

End-to-end UI test suite for the **AP Invoice Management** dashboard, built with [Playwright](https://playwright.dev/python/) and [pytest](https://docs.pytest.org/).

---

## Project Structure

```
Triumph_Automation/
├── conftest.py              # Pytest fixtures (browser, context, page, screenshot-on-failure)
├── pytest.ini               # Pytest configuration and CLI options
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not committed)
├── locators/
│   ├── login_locators.py    # Selectors and constants for the login flow
│   └── dashboard_locators.py# Selectors and constants for the dashboard
├── pages/
│   ├── base_page.py         # Shared page-object helpers
│   ├── login_page.py        # Azure SSO login flow
│   └── dashboard_page.py    # Dashboard interactions (grid, columns, screenshots)
├── tests/
│   └── test_dashboard.py    # Test cases for the AP Invoice dashboard
├── utils/
│   └── config.py            # Loads env vars (BASE_URL, USERNAME, PASSWORD, paths)
└── reports/
    ├── report.html           # Auto-generated HTML test report
    ├── screenshots/          # Failure screenshots (auto-saved)
    └── videos/               # Session recordings (auto-saved)
```

---

## Prerequisites

- Python **3.9+**
- pip

---

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd Triumph_Automation
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers

```bash
playwright install chromium
```

### 5. Configure environment variables

Create a `.env` file in the project root (copy from `.env.example` if provided):

```env
BASE_URL=https://<your-app-url>
USERNAME=<your-azure-email>
PASSWORD=<your-password>
```

> **Security note:** Never commit the `.env` file. It is already listed in `.gitignore`.

---

## Running Tests

Run the full test suite:

```bash
pytest
```

Run a specific test file:

```bash
pytest tests/test_dashboard.py
```

Run a specific test by name:

```bash
pytest tests/test_dashboard.py::TestAPInvoiceDashboard::test_ap_invoice_text_visible
```

Run in headless mode (override the fixture default):

```bash
pytest --headed=false
```

---

## Test Reports

After each run, an HTML report is generated at:

```
reports/report.html
```

Open it in any browser to review results, including pass/fail status and captured output.

---

## Artifacts

| Artifact | Location | When created |
|---|---|---|
| HTML report | `reports/report.html` | Every run |
| Failure screenshots | `reports/screenshots/FAIL_<test>_<timestamp>.png` | On test failure |
| Video recordings | `reports/videos/` | Every test session |

---

## Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
addopts = --html=reports/report.html --self-contained-html -v
```

### Changing Tested Grid Columns

To change which columns are swapped in `test_grid_column_swap`, edit only these two fields in [locators/dashboard_locators.py](locators/dashboard_locators.py) — no other file needs to change:

| Field | Description |
|---|---|
| `ACTIVE_STATUS_COLUMN` | Column currently in **Active Columns** — will be moved out |
| `AVAILABLE_INVOICE_TYPE_COLUMN` | Column currently in **Available Columns** — will be moved in |

---

## Architecture

The project follows the **Page Object Model (POM)** pattern:

- **Locators** (`locators/`) — centralise all selectors and UI constants. Update one place when the UI changes.
- **Pages** (`pages/`) — encapsulate interactions per page/component; tests never call Playwright APIs directly.
- **Tests** (`tests/`) — orchestrate page objects and assert outcomes; contain no selector strings.
- **Utils** (`utils/config.py`) — loads all runtime configuration from environment variables (12-Factor compliant).
- **Fixtures** (`conftest.py`) — provide browser, context, and page instances; automatically capture screenshots and videos on failure.

---

## CI/CD

Run tests in a CI pipeline by setting the three required environment variables (`BASE_URL`, `USERNAME`, `PASSWORD`) as secrets and executing:

```bash
pip install -r requirements.txt
playwright install --with-deps chromium
pytest
```

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `playwright` | 1.58.0 | Browser automation |
| `pytest` | 9.0.2 | Test runner |
| `pytest-playwright` | 0.7.2 | Playwright pytest integration |
| `pytest-html` | 4.2.0 | HTML report generation |
| `pytest-metadata` | 3.1.1 | Test metadata in reports |
| `python-dotenv` | 1.2.2 | `.env` file loading |
