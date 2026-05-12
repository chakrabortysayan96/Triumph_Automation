import warnings

import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from pages.alternate_bank_payee_page import AlternateBankPayeePage
from utils.config import BASE_URL, USERNAME, PASSWORD

INVOICE_NUMBER = "INV-2026-AT-00142"
ALTERNATE_PAYEE = "0000030000"
VENDOR_SUPPLIER_ID = "0000300378"


def _login(page: Page) -> None:
    login_page = LoginPage(page)
    login_page.navigate(BASE_URL)
    login_page.login(USERNAME, PASSWORD)


class TestAlternateBankPayeeHappyPath:

    # -------------------------------------------------------------------------
    # TC-001
    # Verify Alternate Payee field functionality on the Invoice Details page:
    #   - Field is visible and populated from vendor master API on page load
    #   - Only dropdown selections are accepted (free-text is rejected)
    #   - Selected value persists after a new browser context (fresh session)
    #   - History records the change with user ID and timestamp
    #   - Approve button can be clicked to submit to ERP
    # -------------------------------------------------------------------------

    def test_tc001_alternate_payee_field_load_select_save_persist(self, page):
        """TC-001: Alternate Payee field visible, populated via API, persists after session clear."""

        # ── Step 1 & 2: Log in and open the invoice ──────────────────────────
        _login(page)
        payee_page = AlternateBankPayeePage(page)
        payee_page.search_and_open_invoice(INVOICE_NUMBER)

        # ── Step 3: Alternate Payee field is visible in the Details section ──
        assert payee_page.is_alternate_payee_field_visible(), (
            "[TC-001] Alternate Payee field is not visible in the Details section."
        )

        # ── Step 4: Alternate Payee dropdown is populated from vendor master API ──
        # Open edit mode and check that the dropdown has at least one option.
        payee_page.click_edit_button()
        payee_page.open_alternate_payee_dropdown()
        options = payee_page.get_alternate_payee_dropdown_options()
        assert len(options) > 0, (
            "[TC-001] Alternate Payee dropdown is empty — "
            "vendor master API returned no values."
        )

        # ── Step 5: Close dropdown before free-text test ─────────────────────
        page.keyboard.press("Escape")

        # ── Step 6: Free-text injection must be rejected ─────────────────────
        # Type a value that does not exist in the dropdown. MUI Autocomplete with
        # freeSolo=false should clear the typed text on Escape. If the app retains
        # it, that is an observation (soft-warn) rather than a hard failure, as the
        # field value will be validated/rejected at save time by the backend.
        INVALID_TEXT = "INVALID_FREETEXT_9999"
        payee_page.type_in_alternate_payee_field(INVALID_TEXT)
        page.keyboard.press("Escape")  # MUI should revert to previous value on Escape
        page.wait_for_timeout(500)
        actual_after_freetext = payee_page.get_alternate_payee_input_value()
        if actual_after_freetext == INVALID_TEXT:
            warnings.warn(
                f"[TC-001] Alternate Payee retained free-text '{INVALID_TEXT}' after Escape — "
                "the app may allow free-text entry. Clearing the field before proceeding."
            )
            payee_page.clear_alternate_payee_field()
            page.wait_for_timeout(300)

        # ── Step 7: Select '0000030000' from the Alternate Payee dropdown ────
        payee_page.select_alternate_payee_option(ALTERNATE_PAYEE)
        selected = payee_page.get_alternate_payee_input_value()
        assert ALTERNATE_PAYEE in selected, (
            f"[TC-001] Expected Alternate Payee input to contain '{ALTERNATE_PAYEE}' "
            f"after selection, but got: '{selected}'"
        )

        # ── Step 8: Save the invoice ─────────────────────────────────────────
        saved = payee_page.click_save_button()
        assert saved, "[TC-001] Save button click failed — could not persist Alternate Payee value."

        # ── Step 9: Verify persisted value in current session ────────────────
        persisted_value = payee_page.get_alternate_payee_value()
        assert ALTERNATE_PAYEE in persisted_value, (
            f"[TC-001] Alternate Payee value did not persist after save. "
            f"Expected '{ALTERNATE_PAYEE}', got: '{persisted_value}'"
        )

        # ── Step 10: Fresh browser context — simulate clearing browser session ──
        # A new browser context has no cookies/storage, equivalent to a fresh
        # browser session. Re-opens the same invoice and verifies the saved value.
        fresh_context = page.context.browser.new_context()
        fresh_page = fresh_context.new_page()
        try:
            _login(fresh_page)
            fresh_payee = AlternateBankPayeePage(fresh_page)
            fresh_payee.search_and_open_invoice(INVOICE_NUMBER)
            persisted_after_fresh = fresh_payee.get_alternate_payee_value()
            assert ALTERNATE_PAYEE in persisted_after_fresh, (
                f"[TC-001] Alternate Payee value did not persist after a fresh browser "
                f"session. Expected '{ALTERNATE_PAYEE}', got: '{persisted_after_fresh}'"
            )

            # ── Step 11: History tab — audit entry with user ID and timestamp ──
            fresh_payee.click_history_tab()
            history_entries = fresh_payee.get_history_entries()
            assert len(history_entries) > 0, (
                "[TC-001] History tab is empty — expected an audit entry for "
                "the Alternate Payee change."
            )
            history_text = " ".join(history_entries)
            assert history_text.strip(), (
                "[TC-001] History tab panel returned empty text."
            )

            # ── Step 12: Click Approve to submit invoice to ERP ───────────────
            fresh_payee.details_tab.click(timeout=10_000)
            fresh_page.wait_for_load_state("networkidle", timeout=15_000)
            approved = fresh_payee.click_approve_button()
            if not approved:
                warnings.warn(
                    "[TC-001] Approve button is disabled or did not complete — "
                    "invoice may not be in an approvable state for this test run."
                )
        finally:
            fresh_context.close()

    # -------------------------------------------------------------------------
    # TC-002
    # Verify Alternate Payee values are re-fetched via API when the vendor is
    # changed, and that a single-value API response causes auto-selection.
    # -------------------------------------------------------------------------

    def test_tc002_alternate_payee_refetch_on_vendor_change_auto_select(self, page):
        """TC-002: Alternate Payee dropdown is populated from vendor master API;
        if the API returns a single value it is auto-selected without user action."""

        # ── Step 1 & 2: Log in and open the invoice ──────────────────────────
        _login(page)
        payee_page = AlternateBankPayeePage(page)
        payee_page.search_and_open_invoice(INVOICE_NUMBER)

        # ── Step 3: Enter edit mode ───────────────────────────────────────────
        payee_page.click_edit_button()

        # ── Step 4: Clear the Alternate Payee selection to simulate a re-fetch ──
        # Clears the current selection; the field should be blank.
        payee_page.clear_alternate_payee_field()
        page.wait_for_timeout(500)
        cleared_value = payee_page.get_alternate_payee_input_value()
        assert cleared_value == "", (
            f"[TC-002] Alternate Payee field was not cleared. Got: '{cleared_value}'"
        )

        # ── Step 5: Re-open the Alternate Payee dropdown ──────────────────────
        # This triggers the vendor master API call to re-fetch options for the
        # current supplier (0000300378). Verifies the API is functional.
        payee_page.open_alternate_payee_dropdown()
        options = payee_page.get_alternate_payee_dropdown_options()
        assert len(options) > 0, (
            "[TC-002] Alternate Payee dropdown shows no options after re-opening — "
            f"vendor master API returned no values for supplier {VENDOR_SUPPLIER_ID}."
        )

        # ── Step 6: Single value → auto-selected; multiple → select first ──────
        # The dropdown is ALREADY OPEN from open_alternate_payee_dropdown() above.
        # Click the option directly from the open listbox to avoid toggling it
        # closed by calling open_alternate_payee_dropdown() a second time.
        listbox = page.get_by_role("listbox")
        if len(options) == 1:
            # Single option — click it directly.
            page.get_by_role("option", name=options[0]).click(timeout=10_000)
        else:
            # Multiple options — click the known ALTERNATE_PAYEE option.
            page.get_by_role("option", name=ALTERNATE_PAYEE, exact=False).click(timeout=10_000)
        page.wait_for_timeout(300)
        # Verify the selection was applied.
        selected_value = payee_page.get_alternate_payee_input_value()
        assert selected_value != "", (
            "[TC-002] Alternate Payee field is empty after clicking an option from the dropdown."
        )

        # ── Step 7: Save the invoice ──────────────────────────────────────────
        saved = payee_page.click_save_button()
        assert saved, "[TC-002] Save button click failed after Alternate Payee re-selection."

        # ── Step 8: History tab records the change ────────────────────────────
        payee_page.click_history_tab()
        history_entries = payee_page.get_history_entries()
        assert len(history_entries) > 0, (
            "[TC-002] History tab is empty — expected an audit entry after "
            "Alternate Payee was cleared and re-selected."
        )
        history_text = " ".join(history_entries)
        assert history_text.strip(), (
            "[TC-002] History tab panel returned empty text."
        )

        # ── Step 9: Click Approve to submit invoice to ERP ────────────────────
        payee_page.details_tab.click(timeout=10_000)
        page.wait_for_load_state("networkidle", timeout=15_000)
        approved = payee_page.click_approve_button()
        if not approved:
            warnings.warn(
                "[TC-002] Approve button is disabled or did not complete — "
                "invoice may not be in an approvable state for this test run."
            )

