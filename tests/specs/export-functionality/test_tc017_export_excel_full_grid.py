"""
TC-017 — Verify Export as Excel downloads a file containing all grid column
          fields with their respective values.

Steps:
  1. Log in as AP Processor and navigate to the main dashboard with multiple records.
  2. Capture a sample of Invoice No. values from the grid.
  3. Click the 'Export as Excel' button and wait for the download.
  4. Open the downloaded export file and verify:
       a. Every expected export column header is present in the file.
       b. The sampled Invoice No. values from the grid appear in the export data.

Expected:
  - All column fields are present in the export file.
  - Data values match the records displayed on the dashboard grid.
"""

import csv
import pytest

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from locators.dashboard_locators import DashboardLocators
from utils.config import BASE_URL, USERNAME, PASSWORD


class TestTC017ExportExcelFullGrid:

    def test_tc017_export_excel_full_grid(self, page):

        # --- Step 1: Log in and navigate to the dashboard ---
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        dashboard = DashboardPage(page)
        dashboard._dismiss_cookie_banner()

        record_count = dashboard.get_grid_record_count()
        if record_count == 0:
            pytest.skip(
                "[TC-017] No records visible in the grid for the current date range. "
                "Adjust the date filter or seed data before running this test."
            )

        # --- Step 2: Capture a sample of Invoice No. values from the grid ---
        sample_invoice_numbers = dashboard.get_column_values("Invoice No.")[:5]

        # --- Step 3: Export ---
        export_path = dashboard.download_excel()
        assert export_path.exists(), (
            f"[TC-017] Downloaded export file not found at: {export_path}"
        )

        # --- Step 4a: Verify all expected export column headers are present ---
        with open(export_path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.reader(fh)
            export_headers = next(reader)
            data_rows = list(reader)

        missing = [
            h for h in DashboardLocators.EXPECTED_EXPORT_HEADERS
            if h not in export_headers
        ]
        assert not missing, (
            f"[TC-017] The following expected columns are missing from the export: "
            f"{missing}"
        )

        # --- Step 4b: Verify sampled Invoice No. values appear in the export data ---
        if sample_invoice_numbers:
            invoice_col_index = next(
                (idx for idx, h in enumerate(export_headers) if h == "Invoice No."),
                None,
            )
            if invoice_col_index is not None:
                export_invoice_numbers = [
                    row[invoice_col_index]
                    for row in data_rows
                    if len(row) > invoice_col_index
                ]
                for inv_no in sample_invoice_numbers:
                    assert inv_no in export_invoice_numbers, (
                        f"[TC-017] Invoice No. '{inv_no}' visible on the dashboard "
                        f"grid was not found in the export file."
                    )

