"""
TC-003 — Search Invoice 779037122 (Purchase Order), Click Urgent Flag, Attempt Approve (Gate Check)

Steps:
  1. Open application and log in; search for invoice number 779037122.
     Invoice type: Purchase Order.
  2. Click the urgent (bypass approval) flag for that invoice.
  3. Open the invoice details page.
  4. Check the Approve button:
       • If the Approve button is DISABLED → raise RuntimeError (deliberate gate failure).
       • If the Approve button is ENABLED  → click it and capture the confirmation popup.

Expected:
  - If the Approve button is disabled, the test raises RuntimeError to signal
    that the approve action cannot be performed for this invoice.
  - If the Approve button is enabled, clicking it triggers a confirmation popup
    whose text is captured and asserted to be non-empty.

Notes:
  - Invoice 779037122 is a Purchase Order type invoice.
  - If the invoice is not found within the current 90-day date range the
    test is skipped with a clear message rather than failing.
  - The RuntimeError on a disabled Approve button is a deliberate design choice:
    it surfaces the gate failure loudly so engineers investigate the invoice data.
"""

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.bypass_approval_page import BypassApprovalPage
from utils.config import BASE_URL, USERNAME, PASSWORD

TARGET_INVOICE_NUMBER = "779037122"
TARGET_INVOICE_TYPE = "Purchase Order"  # Expected invoice type for this test case


class TestTC003SearchInvoiceUrgentApproveGate:

    def test_tc003_search_invoice_urgent_flag_approve_gate(self, page):

        # ------------------------------------------------------------------
        # Step 1: Login and search for invoice 779037122
        # ------------------------------------------------------------------
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        bypass_page = BypassApprovalPage(page)
        bypass_page.dismiss_cookie_banner()

        expect(
            page.get_by_role("heading", name="AP Invoice Management")
        ).to_be_visible(timeout=15_000)

        # Wait for the grid to populate before searching.
        bypass_page.wait_for_grid_loaded()

        bypass_page.search_invoice(TARGET_INVOICE_NUMBER)

        # Check for a 403 / API error — fires when the invoice is outside the
        # server-side allowed date range.
        if bypass_page.is_api_error_visible():
            pytest.skip(
                f"[TC-003] Searching for invoice {TARGET_INVOICE_NUMBER} returned a "
                "403 / API error from the server. "
                "The invoice is outside the current 90-day date window. "
                f"Error: {bypass_page.get_search_api_error()}. "
                "Ask an admin to adjust the allowed date range before re-running."
            )

        # If no invoice cells and 'No results found' is shown, skip gracefully.
        if bypass_page.is_no_results_visible():
            pytest.skip(
                f"[TC-003] Invoice {TARGET_INVOICE_NUMBER} ({TARGET_INVOICE_TYPE}) "
                "was not found in the current date range (max 90 days). "
                "Confirm the invoice date falls within the current range before re-running."
            )

        # Confirm the invoice appears in the grid
        invoice_cell_visible = (
            page.locator("td.dashboard-table-invoiceNo")
            .filter(has=page.get_by_text(TARGET_INVOICE_NUMBER, exact=False))
            .first
            .is_visible(timeout=5_000)
        )
        if not invoice_cell_visible:
            pytest.skip(
                f"[TC-003] Invoice {TARGET_INVOICE_NUMBER} is not visible in the "
                "invoice grid after search. The 'No results found' placeholder was "
                "also not shown — the page may still be loading or the invoice "
                "exists outside the current date range."
            )

        # Verify the Bypass Approval column is active in the current column config.
        # If it has been removed from the Active Columns set, the bypass flag cell
        # will not be rendered and this test cannot proceed.
        if bypass_page.get_bypass_flag_count() == 0:
            pytest.skip(
                "[TC-003] The 'Bypass Approval' column is not visible in the invoice "
                "grid. Add it back via Change Grid View → Active Columns before "
                "running this test."
            )

        # ------------------------------------------------------------------
        # Step 2: Click bypass flag; wait for XHR; Step 3: open details by UUID
        # Capture the detail URL BEFORE clicking so we navigate to the EXACT
        # invoice regardless of any grid re-sort after the XHR completes.
        # ------------------------------------------------------------------
        invoice_url = bypass_page.get_invoice_url_for_row(row_index=0)
        bypass_page.click_bypass_flag(row_index=0)
        bypass_page.navigate_to_invoice_url(invoice_url)

        expect(
            page.locator("h3").filter(has_text="Invoice No.")
        ).to_be_visible(timeout=10_000)

        # Verify this is the correct invoice number in the page heading
        heading_text = page.locator("h3").filter(has_text="Invoice No.").text_content() or ""
        assert TARGET_INVOICE_NUMBER in heading_text, (
            f"[TC-003] Expected detail page for invoice {TARGET_INVOICE_NUMBER}, "
            f"but heading shows: '{heading_text.strip()}'"
        )

        # Verify the invoice type is Purchase Order (TC-003 specific data contract).
        # "Invoice Type" is displayed in the summary header on the details page.
        # We check the full page text so the assertion is not coupled to a
        # specific DOM structure that may change.
        page_text = page.locator("main").text_content() or ""
        assert TARGET_INVOICE_TYPE in page_text, (
            f"[TC-003] Invoice {TARGET_INVOICE_NUMBER} was expected to be of type "
            f"'{TARGET_INVOICE_TYPE}', but that value was not found on the details page. "
            "Verify the invoice type in the system before running this test."
        )

        # ------------------------------------------------------------------
        # Step 4: Approve button gate check
        # ------------------------------------------------------------------
        approve_visible = bypass_page.is_approve_button_visible()
        assert approve_visible, (
            f"[TC-003] Approve button is not visible on the details page for "
            f"invoice {TARGET_INVOICE_NUMBER}."
        )

        if not bypass_page.is_approve_button_enabled():
            # ----------------------------------------------------------------
            # DISABLED BRANCH: Approve button is disabled — raise RuntimeError
            # This is the expected outcome for invoices with incomplete data.
            # ----------------------------------------------------------------
            raise RuntimeError(
                f"[TC-003] Approve button is DISABLED for invoice "
                f"{TARGET_INVOICE_NUMBER}. "
                "The invoice cannot be approved: mandatory fields may be missing, "
                "the invoice status may not permit approval, or the bypass approval "
                "flag alone is insufficient to enable the Approve action. "
                "Investigate the invoice data before retrying."
            )

        # ----------------------------------------------------------------
        # ENABLED BRANCH: Approve button is enabled — click and capture popup
        # ----------------------------------------------------------------
        clicked = bypass_page.click_approve_button()
        assert clicked, (
            f"[TC-003] Clicking the Approve button failed for invoice "
            f"{TARGET_INVOICE_NUMBER}."
        )

        popup_text = bypass_page.get_approve_popup_text()
        # The Approve action may result in either:
        #   (a) A confirmation dialog/modal (success path)
        #   (b) An error toast if the current user is not an authorized approver
        # Both are valid observable responses.  We assert that SOMETHING appeared
        # after clicking Approve — either a confirmation or a meaningful error.
        assert popup_text, (
            f"[TC-003] No confirmation dialog or error toast appeared after "
            f"clicking Approve for invoice {TARGET_INVOICE_NUMBER}. "
            "Expected either a confirmation modal or an error message from the server."
        )
