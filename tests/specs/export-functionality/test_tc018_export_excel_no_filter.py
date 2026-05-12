"""
TC-018 — Verify Export as Excel behavior when no filters are applied on the
          dashboard grid (default state after login).

Steps:
  1. Log in as AP Processor and navigate to the main dashboard.
  2. Without applying any filter, click the 'Export as Excel' button.
  3. Open the downloaded Excel file.
  4. Verify that all column fields visible on the grid are present as headings
     in the Excel file.

Expected:
  - All the fields (column headers) are available in the Excel.
"""

import csv
import pytest

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from locators.dashboard_locators import DashboardLocators
from utils.config import BASE_URL, USERNAME, PASSWORD


class TestTC018ExportExcelNoFilter:

    def test_tc018_export_excel_no_filter(self, page):

        # --- Step 1: Log in and navigate to the dashboard ---
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        dashboard = DashboardPage(page)
        dashboard._dismiss_cookie_banner()

        # --- Step 2: Export without applying any filter ---
        export_path = dashboard.download_excel()
        assert export_path.exists(), (
            f"[TC-018] Downloaded export file not found at: {export_path}"
        )

        # --- Step 3 & 4: Verify all expected column fields are present ---
        with open(export_path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.reader(fh)
            export_headers = next(reader)

        assert len(export_headers) > 0, (
            "[TC-018] The export file has no column headings in the first row."
        )

        missing = [
            h for h in DashboardLocators.EXPECTED_EXPORT_HEADERS
            if h not in export_headers
        ]
        assert not missing, (
            f"[TC-018] The following expected columns are missing from the export: "
            f"{missing}"
        )
