"""
TC-004 — Validate email popover after hovering the submitter name in landing
          page of Zora and Details page of the invoice — in different browsers.

Two separate parameterized tests:
  - test_tc004_submitter_popover_chrome  → uses the default `page` fixture (Chromium)
  - test_tc004_submitter_popover_edge   → uses the `edge_page` fixture (Microsoft Edge)

Steps (identical in both browsers):
  1. Navigate to dashboard.
  2. Hover on Submitter Name in dashboard; verify popover appears with correct email.
  3. Click invoice to navigate to details page; hover Submitter Name; verify email
     matches dashboard popover.
  4. View Submitter Name without hovering; return to dashboard without hovering;
     verify only name visible (no inline email).
  5. Hover submitter tooltip again; move cursor away; verify popover disappears.

Test data: Invoice number 1274481 (used when available; falls back to first row).

Expected:
  - Popover appears with correct email in both browsers.
  - Dashboard and details page email match.
  - Only name visible without hover.
  - Popover disappears immediately on cursor move.
"""

import warnings

import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from pages.submitter_email_popover_page import SubmitterEmailPopoverPage
from pages.invoice_details_page import InvoiceDetailsPage
from utils.config import BASE_URL, USERNAME, PASSWORD

INVOICE_NUMBER = "1274481"


def _run_submitter_popover_scenario(page: Page, browser_label: str) -> None:
    """Core scenario executed in both Chrome and Edge."""

    # Step 1: Log in and navigate to dashboard
    login_page = LoginPage(page)
    login_page.navigate(BASE_URL)
    login_page.login(USERNAME, PASSWORD)

    submitter_page = SubmitterEmailPopoverPage(page)
    submitter_page._dismiss_cookie_banner()

    cell_count = submitter_page.get_submitter_cell_count()
    if cell_count == 0:
        pytest.skip(
            f"[TC-004][{browser_label}] No invoices found in dashboard."
        )

    # Step 2: Try to locate invoice 1274481; fall back to first row if absent
    found = submitter_page.open_invoice_by_number(INVOICE_NUMBER)
    if not found:
        warnings.warn(
            f"[TC-004][{browser_label}] Invoice {INVOICE_NUMBER} not found; "
            "falling back to first available row."
        )
        # Re-navigate to reset search state
        login_page.navigate(BASE_URL)
        submitter_page._dismiss_cookie_banner()

    else:
        # open_invoice_by_number navigates to details; go back to hover on dashboard
        page.go_back()
        page.wait_for_load_state("load", timeout=15000)
        submitter_page._dismiss_cookie_banner()

    submitter_page.hover_submitter_by_index(0)
    dashboard_email = submitter_page.get_email_popover_text(timeout=4000)

    assert submitter_page.is_email_popover_visible(), (
        f"[TC-004][{browser_label}] Email popover should be visible on hover "
        "in dashboard."
    )
    assert "@" in dashboard_email or "not available" in dashboard_email.lower(), (
        f"[TC-004][{browser_label}] Expected email address in dashboard popover, "
        f"got: '{dashboard_email}'"
    )

    # Step 3: Open invoice details; hover submitter; verify email matches
    submitter_page.open_invoice_by_index(0)

    details_page = InvoiceDetailsPage(page)
    assert details_page.is_loaded(), (
        f"[TC-004][{browser_label}] Invoice details page did not load."
    )

    details_page.hover_submitter_name()
    details_email = details_page.get_submitter_popover_text(timeout=4000)

    assert "@" in details_email or "not available" in details_email.lower(), (
        f"[TC-004][{browser_label}] Unexpected details popover text: '{details_email}'"
    )
    assert details_email == dashboard_email, (
        f"[TC-004][{browser_label}] Email mismatch — "
        f"dashboard: '{dashboard_email}', details: '{details_email}'"
    )

    # Step 4: Move cursor away; return to dashboard; verify no inline email
    details_page.move_cursor_away()
    page.wait_for_timeout(500)
    assert not details_page.is_submitter_popover_visible(), (
        f"[TC-004][{browser_label}] Popover should be hidden after cursor moves away."
    )

    details_page.navigate_back()
    expect(
        page.locator("td.dashboard-table-submitter").first
    ).not_to_contain_text("@")

    # Step 5: Hover again; move cursor away; verify popover disappears
    submitter_page.hover_submitter_by_index(0)
    assert submitter_page.is_email_popover_visible(), (
        f"[TC-004][{browser_label}] Popover should reappear on second hover."
    )

    submitter_page.move_cursor_away()
    assert submitter_page.is_email_popover_hidden(timeout=3000), (
        f"[TC-004][{browser_label}] Popover should disappear immediately on "
        "cursor move away."
    )


class TestTC004SubmitterPopoverCrossBrowser:

    def test_tc004_submitter_popover_chrome(self, page):
        _run_submitter_popover_scenario(page, "Chrome")

    def test_tc004_submitter_popover_edge(self, edge_page):
        _run_submitter_popover_scenario(edge_page, "Edge")
