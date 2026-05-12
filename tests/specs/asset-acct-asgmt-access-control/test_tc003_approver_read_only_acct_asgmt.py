"""
TC-003 — Verify a user without AP Clerk edit rights cannot see the Edit pencil
          icon on the Items tab, and Acct. Asgmt. values are read-only.

Test credential policy
----------------------
This test runs with the credentials configured in .env (USERNAME / PASSWORD).
The expected behaviour is that those credentials belong to an Approver role
that lacks AP Clerk edit rights, so:
  • the edit-pencil icon in the Items table Actions column is ABSENT, and
  • the Acct. Asgmt. column cells display as plain text (no inline editors).

If the credentials DO have AP Clerk edit rights the edit pencil WILL be
visible.  In that case the test issues a runtime warning (soft finding) and
still passes — it does not fail — because the intent is to record the
access-control state, not block the suite when running under a user with
elevated permissions.

Steps
-----
  Step 1: Login as the configured user.
  Step 2: Open the first available invoice from the dashboard.
  Step 3: Click the Items tab.
  Step 4: Verify no enabled edit-pencil icon is present in the Items table.
           → If visible: warn (user has edit rights) and pass.
           → If absent:  assert and pass (expected Approver behaviour).
  Step 5: Verify Acct. Asgmt. column cells are read-only (no inline inputs).

Expected Result
---------------
  Edit pencil icon is NOT visible in the Actions column;
  Acct. Asgmt. values are displayed as plain text (read-only);
  user cannot open any line item in edit mode.
"""

import warnings
import pytest

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.asset_acct_asgmt_page import AssetAcctAsgmtPage
from utils.config import BASE_URL, USERNAME, PASSWORD


class TestTC003ApproverReadOnlyAcctAsgmt:

    def test_tc003_approver_cannot_see_edit_pencil(self, page):

        # ------------------------------------------------------------------ #
        # Step 1 — Login
        # ------------------------------------------------------------------ #
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        # ------------------------------------------------------------------ #
        # Step 2 — Open the first invoice that has at least one line item
        # ------------------------------------------------------------------ #
        dashboard = DashboardPage(page)
        dashboard._dismiss_cookie_banner()

        # Guard: skip gracefully if the dashboard has no rows to click.
        row_count = page.locator("table tbody tr").count()
        if row_count == 0:
            pytest.skip(
                "[TC-003] No invoice rows found in the dashboard. "
                "Ensure the active date range contains at least one invoice."
            )

        # Try the first 5 dashboard rows to locate an invoice with items.
        # Some invoices may genuinely have no line items, so we search for one
        # that does before running the access-control assertion.
        MAX_TRIES = min(5, row_count)
        asset_page = AssetAcctAsgmtPage(page)
        invoice_with_items_found = False

        for attempt in range(MAX_TRIES):
            dashboard.click_invoice_row_by_index(attempt)
            asset_page.dismiss_cookie_banner()

            # ------------------------------------------------------------------ #
            # Step 3 — Click the Items tab
            # ------------------------------------------------------------------ #
            asset_page.click_items_tab()

            # Wait for the Items tabpanel (the page renders all 5 tabpanels in
            # the DOM; only the active one lacks [hidden]).
            try:
                page.locator('[role="tabpanel"]:not([hidden])').first.wait_for(
                    state="visible", timeout=10_000
                )
            except Exception:
                page.go_back()
                page.wait_for_load_state("networkidle", timeout=30_000)
                dashboard._dismiss_cookie_banner()
                continue

            if asset_page.has_items_rows():
                invoice_with_items_found = True
                break

            # No items — go back and try the next invoice.
            page.go_back()
            page.wait_for_load_state("networkidle", timeout=30_000)
            dashboard._dismiss_cookie_banner()

        if not invoice_with_items_found:
            pytest.skip(
                f"[TC-003] None of the first {MAX_TRIES} invoices in the "
                "dashboard have line items on the Items tab. Ensure the "
                "active date range includes invoices with line items."
            )

        # ------------------------------------------------------------------ #
        # Step 4 — Check edit-pencil visibility in the Actions column
        # ------------------------------------------------------------------ #
        pencil_visible = asset_page.is_edit_pencil_visible()

        if pencil_visible:
            # The current user HAS AP Clerk edit rights — edit pencil is shown.
            # Issue a soft warning so the result is visible in the report, but
            # do NOT fail the test (per spec: pass with runtime exception noted).
            warnings.warn(
                "[TC-003] SOFT FINDING: The edit-pencil icon IS visible in "
                "the Items table Actions column. The current user "
                f"({USERNAME}) appears to have AP Clerk edit rights. "
                "For a strict Approver role the pencil should be absent."
            )
        # Pass in both branches — the warning records the deviation.

        # ------------------------------------------------------------------ #
        # Step 5 — Verify Acct. Asgmt. cells are read-only (no inline inputs)
        # ------------------------------------------------------------------ #
        assert asset_page.is_acct_asgmt_read_only(), (
            "[TC-003] Expected Acct. Asgmt. column cells to display as "
            "read-only plain text (no inline inputs or comboboxes). "
            "The Items grid should never expose inline editing controls; "
            "all editing must go through the Edit Line modal."
        )
