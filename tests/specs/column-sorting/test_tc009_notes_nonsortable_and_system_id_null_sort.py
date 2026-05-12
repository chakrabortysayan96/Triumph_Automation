"""
TC-009 — Verify that:
  (a) The Notes column header is non-sortable (no sort interaction occurs when clicked).
  (b) Clicking the System ID column (which contains null/empty "—" values) sorts the
      grid; null/empty values are grouped consistently at the top or bottom; no error.

Steps:
  1. Log in as AP Processor and navigate to main dashboard with records.
  2. Identify and click the Notes column header — it must NOT sort.
  3. Identify the System ID column and click its header once.
  4. Verify null/empty ("—") values are grouped consistently and the sort indicator shown.

Expected:
  - Notes: clicking the Notes header does NOT produce a sort indicator change;
    the Notes column is NOT sortable (no .header-title.sortable class).
  - System ID: after a sort click, rows with null/empty cells are grouped
    (all at top or all at bottom); a sort direction indicator is visible; no error.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from locators.dashboard_locators import DashboardLocators
from utils.config import BASE_URL, USERNAME, PASSWORD

NON_SORTABLE_COLUMN = "Notes"
NULL_VALUE_COLUMN   = "System ID"
NULL_PLACEHOLDER    = "—"


class TestTC009NoteNonSortableAndSystemIDNullSort:

    def test_tc009_notes_nonsortable_and_system_id_null_sort(self, page):

        # --- Step 1: Log in and navigate to the dashboard ---
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        dashboard = DashboardPage(page)
        dashboard._dismiss_cookie_banner()

        record_count = dashboard.get_grid_record_count()
        if record_count == 0:
            pytest.skip(
                "[TC-009] No records visible in the grid for the current date range. "
                "Adjust the date filter or seed data before running this test."
            )

        # --- Step 2: Notes column — verify it is NOT sortable ---
        assert not dashboard.is_column_header_sortable(NON_SORTABLE_COLUMN), (
            f"[TC-009] '{NON_SORTABLE_COLUMN}' unexpectedly has the sortable class. "
            "The Notes column should not be sortable."
        )

        # The Notes header should be present but must NOT carry any sort direction
        assert dashboard.get_sort_direction(NON_SORTABLE_COLUMN) is None, (
            f"[TC-009] '{NON_SORTABLE_COLUMN}' unexpectedly returned a sort direction. "
            "Non-sortable columns must not have a sort indicator."
        )

        # Click the Notes header — the sort direction must remain None afterwards
        notes_header = page.get_by_role("columnheader", name=NON_SORTABLE_COLUMN)
        expect(notes_header).to_be_visible()
        notes_header.click()
        page.wait_for_timeout(1000)  # brief pause; no grid reload expected

        assert dashboard.get_sort_direction(NON_SORTABLE_COLUMN) is None, (
            f"[TC-009] Clicking '{NON_SORTABLE_COLUMN}' produced an unexpected sort direction. "
            "Non-sortable columns must not react to header clicks."
        )

        # --- Step 3 & 4: System ID column — sort with null/empty values ---
        if not dashboard.is_column_header_sortable(NULL_VALUE_COLUMN):
            pytest.skip(
                f"[TC-009] '{NULL_VALUE_COLUMN}' is not a sortable column in this build. "
                "Cannot validate null-value sort behaviour."
            )

        dashboard.click_column_header(NULL_VALUE_COLUMN)
        sort_direction = dashboard.get_sort_direction(NULL_VALUE_COLUMN)
        assert sort_direction in ("ascending", "descending"), (
            f"[TC-009] Expected a sort direction after clicking '{NULL_VALUE_COLUMN}', "
            f"got '{sort_direction}'."
        )

        # Sort indicator must be visible in the columnheader
        expect(
            page.get_by_role("columnheader", name=f"{NULL_VALUE_COLUMN} in {sort_direction}")
        ).to_be_visible()

        # Verify null/empty values are grouped (all at top or all at bottom)
        values = dashboard.get_column_values(NULL_VALUE_COLUMN)
        if values:
            null_indices = [i for i, v in enumerate(values) if v.strip() == NULL_PLACEHOLDER or v.strip() == ""]
            non_null_indices = [i for i, v in enumerate(values) if v.strip() not in (NULL_PLACEHOLDER, "")]

            if null_indices and non_null_indices:
                max_null   = max(null_indices)
                min_null   = min(null_indices)
                max_nonnull = max(non_null_indices)
                min_nonnull = min(non_null_indices)

                # Grouped means: all nulls come before all non-nulls OR vice versa
                nulls_at_top    = max_null < min_nonnull
                nulls_at_bottom = min_null > max_nonnull

                assert nulls_at_top or nulls_at_bottom, (
                    f"[TC-009] Null/empty values in '{NULL_VALUE_COLUMN}' are not grouped "
                    f"consistently after sort. Null indices: {null_indices[:5]}, "
                    f"Non-null indices: {non_null_indices[:5]}"
                )
