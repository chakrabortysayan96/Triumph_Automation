"""
TC-005 — Validate email popover after hovering the submitter email id in landing
          page of Zora and Details page of the invoice, while invoice is
          triggered via email.

UI-ONLY IMPLEMENTATION:
  Email submission, forwarding, and multi-hop forwarding are manual prerequisites.
  This test locates pre-existing invoices in the dashboard by invoice number and
  verifies the popover content. Tests skip gracefully if the invoice is absent.

Steps:
  Step 2: Invoice 250300002106 submitted directly to Zora via email →
          verify sender email appears in dashboard and details popover.
  Step 3: Invoice 1100006706 forwarded once from another person to Zora →
          verify original sender email appears in popover.
  Step 4: Multi-hop forwarded invoice → documented as manual verification only;
          no spec-level assertion (no invoice number provided in test data).

Expected:
  - Sender email appears in submitter popover on dashboard and details page.
  - Original sender email visible when forwarded once.
  - Last/latest forwarder email shown when forwarded through multiple persons
    (manual verification required — no invoice number available for automation).
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.submitter_email_popover_page import SubmitterEmailPopoverPage
from pages.invoice_details_page import InvoiceDetailsPage
from utils.config import BASE_URL, USERNAME, PASSWORD

INVOICE_DIRECT = "250300002106"
INVOICE_FORWARDED_ONCE = "1100006706"


def _verify_submitter_popover_on_dashboard_and_details(
    page, submitter_page: SubmitterEmailPopoverPage, invoice_number: str, tag: str
) -> str:
    """
    Search for invoice_number, hover submitter on dashboard, open details,
    hover submitter on details, assert emails match, and return the email text.
    Returns the email string on success; calls pytest.skip if invoice absent.
    """
    found = submitter_page.open_invoice_by_number(invoice_number)
    if not found:
        pytest.skip(
            f"[{tag}] Invoice {invoice_number} not found in dashboard. "
            "Submit this invoice to the Zora email inbox as a manual prerequisite."
        )

    # Navigated to details — go back to hover submitter on dashboard first
    page.go_back()
    page.wait_for_load_state("load", timeout=15000)
    submitter_page._dismiss_cookie_banner()

    submitter_page.hover_submitter_by_index(0)
    dashboard_email = submitter_page.get_email_popover_text(timeout=4000)
    assert "@" in dashboard_email or "not available" in dashboard_email.lower(), (
        f"[{tag}] Expected email in dashboard popover, got: '{dashboard_email}'"
    )

    # Open details again and hover submitter
    submitter_page.open_invoice_by_index(0)

    details_page = InvoiceDetailsPage(page)
    assert details_page.is_loaded(), f"[{tag}] Invoice details page did not load."

    details_page.hover_submitter_name()
    details_email = details_page.get_submitter_popover_text(timeout=4000)
    assert "@" in details_email or "not available" in details_email.lower(), (
        f"[{tag}] Expected email in details popover, got: '{details_email}'"
    )
    assert details_email == dashboard_email, (
        f"[{tag}] Email mismatch — dashboard: '{dashboard_email}', "
        f"details: '{details_email}'"
    )

    details_page.navigate_back()
    return dashboard_email


class TestTC005SubmitterPopoverEmailForward:

    def test_tc005_submitter_popover_direct_email_invoice(self, page):
        """Step 2: Invoice submitted directly to Zora via email — verify sender email."""

        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)
        submitter_page._dismiss_cookie_banner()

        email = _verify_submitter_popover_on_dashboard_and_details(
            page, submitter_page, INVOICE_DIRECT, "TC-005-Step2"
        )
        assert "@" in email, (
            f"[TC-005-Step2] Sender email expected in popover for directly submitted "
            f"invoice, got: '{email}'"
        )

    def test_tc005_submitter_popover_forwarded_once_invoice(self, page):
        """Step 3: Invoice forwarded once — verify original sender email in popover."""

        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        submitter_page = SubmitterEmailPopoverPage(page)
        submitter_page._dismiss_cookie_banner()

        email = _verify_submitter_popover_on_dashboard_and_details(
            page, submitter_page, INVOICE_FORWARDED_ONCE, "TC-005-Step3"
        )
        assert "@" in email, (
            f"[TC-005-Step3] Original sender email expected in popover for once-forwarded "
            f"invoice, got: '{email}'"
        )
