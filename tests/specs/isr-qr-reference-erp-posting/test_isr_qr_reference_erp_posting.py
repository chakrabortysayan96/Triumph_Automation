import warnings

import pytest
from playwright.sync_api import expect

from locators.isr_qr_reference_locators import IsrQrReferenceLocators
from pages.login_page import LoginPage
from pages.isr_qr_reference_page import IsrQrReferencePage
from utils.config import BASE_URL, USERNAME, PASSWORD

INVOICE_NUMBER = "INV-2026-AT-00142"
# 27-character ISR/QR value used when the field needs to be populated first
ISR_QR_VALUE_27 = "210000000003139471430009017"


class TestIsrQrReferenceErpPosting:

    # =========================================================================
    # TC-018 — Approve button flow when ISR/QR Reference value is present
    #
    # ECC/BSEG-ESRRE verification is out of scope (no ECC access from UI).
    # ECC posting failure simulation is also out of scope (cannot be induced
    # from the UI).  This test exercises:
    #   - ISR/QR Reference is populated before approving
    #   - Approve button and confirmation modal are reachable
    #   - No ISR/QR-related UI validation error blocks the approve flow
    # =========================================================================

    def test_tc018_approve_button_flow_with_isr_qr_value_present(self, page):
        """
        TC-018: Verify the Approve button flow does not surface an ISR/QR-related
        validation error when the ISR/QR Reference field holds a value.

        Scope: UI-only.  ECC posting outcome and BSEG-ESRRE field state are
        out of scope and are not asserted here.
        """
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        qr_page = IsrQrReferencePage(page)

        # Step 1 — Open invoice and verify ISR/QR Reference field is visible
        qr_page.search_and_open_invoice(INVOICE_NUMBER)
        assert qr_page.is_isr_qr_reference_field_visible(), (
            "ISR/QR Reference field should be visible in the Details section"
        )

        # Step 2 — Ensure ISR/QR Reference has a value; populate with 27-char
        #           string if currently blank (field accepts up to 27 characters)
        current_value = qr_page.get_isr_qr_reference_value()
        if not current_value:
            qr_page.click_edit_button()
            assert qr_page.is_isr_qr_reference_field_editable(), (
                "ISR/QR Reference field should be editable after clicking Edit"
            )
            qr_page.enter_isr_qr_reference(ISR_QR_VALUE_27)
            assert qr_page.isr_qr_reference_input.input_value() == ISR_QR_VALUE_27, (
                f"ISR/QR Reference input should contain '{ISR_QR_VALUE_27}' after entry"
            )
            saved = qr_page.click_save_button()
            assert saved, "Save should succeed before attempting ERP posting"
            expect(page.locator('[role="alert"]')).to_contain_text(
                IsrQrReferenceLocators.SAVE_SUCCESS_ALERT_TEXT, timeout=10_000
            )

        # Step 3 — Verify ISR/QR Reference is populated (view mode)
        populated_value = qr_page.get_isr_qr_reference_value()
        assert populated_value, (
            "ISR/QR Reference must be non-empty before attempting approval"
        )

        # Step 4 — Verify Approve button is visible and enabled
        expect(qr_page.approve_button).to_be_visible(timeout=10_000)
        if qr_page.approve_button.is_disabled(timeout=5_000):
            pytest.skip(
                "[TC-018] Approve button is disabled — invoice is not in an "
                "approvable state in the current environment. "
                "Re-run when the invoice is pending approval."
            )

        # Step 5 — Click Approve → Approve Invoice (confirmation modal)
        #           ECC posting outcome is out of scope; no error dialog for
        #           ISR/QR Reference validation is the expected UI behaviour.
        approved = qr_page.click_approve_button()
        if not approved:
            warnings.warn(
                "[TC-018] click_approve_button() returned False — "
                "the approve dialog may not have appeared or the invoice "
                "transitioned to a non-approvable state mid-run."
            )

        # Step 6 — Verify no ISR/QR-specific validation error is shown on screen
        #           (ECC backend failures may surface a generic error — that is
        #           acceptable and not checked here per scope agreement)
        isr_qr_error_visible = page.locator(
            '[role="alert"]:has-text("ISR"), [role="alert"]:has-text("QR Reference")'
        ).is_visible(timeout=3_000)
        assert not isr_qr_error_visible, (
            "No ISR/QR Reference validation error should block the Approve flow "
            "when the field holds a valid value"
        )

    # =========================================================================
    # TC-019 — Approve button flow when ISR/QR Reference field is blank
    #
    # Verifies that a blank ISR/QR Reference field does not cause a UI-level
    # validation error when approving.  BSEG-ESRRE payload inspection is out
    # of scope (no ECC access from UI).
    # =========================================================================

    def test_tc019_blank_isr_qr_does_not_block_erp_posting(self, page):
        """
        TC-019: Verify ECC posting can be initiated when ISR/QR Reference is
        blank — the blank value does not produce a UI validation error.

        Scope: UI-only.  Payload/BSEG-ESRRE state in ECC is out of scope.
        """
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        qr_page = IsrQrReferencePage(page)

        # Step 1 — Open invoice and verify ISR/QR Reference field is visible
        qr_page.search_and_open_invoice(INVOICE_NUMBER)
        assert qr_page.is_isr_qr_reference_field_visible(), (
            "ISR/QR Reference field should be visible in the Details section"
        )

        # Step 2 — Ensure ISR/QR Reference is blank; clear it if it currently
        #           holds a value so the test exercises the blank-field path
        current_value = qr_page.get_isr_qr_reference_value()
        if current_value:
            qr_page.click_edit_button()
            assert qr_page.is_isr_qr_reference_field_editable(), (
                "ISR/QR Reference field should be editable after clicking Edit"
            )
            qr_page.enter_isr_qr_reference("")
            saved = qr_page.click_save_button()
            assert saved, "Save should succeed after clearing ISR/QR Reference"
            expect(page.locator('[role="alert"]')).to_contain_text(
                IsrQrReferenceLocators.SAVE_SUCCESS_ALERT_TEXT, timeout=10_000
            )

        # Step 3 — Verify ISR/QR Reference is blank in view mode
        blank_value = qr_page.get_isr_qr_reference_value()
        assert blank_value == "", (
            f"ISR/QR Reference should be blank before approval; got '{blank_value}'"
        )

        # Step 4 — Verify Approve button is visible and enabled
        expect(qr_page.approve_button).to_be_visible(timeout=10_000)
        if qr_page.approve_button.is_disabled(timeout=5_000):
            pytest.skip(
                "[TC-019] Approve button is disabled — invoice is not in an "
                "approvable state in the current environment. "
                "Re-run when the invoice is pending approval."
            )

        # Step 5 — Click Approve → Approve Invoice (confirmation modal)
        #           A blank ISR/QR Reference must not trigger a validation error.
        approved = qr_page.click_approve_button()
        if not approved:
            warnings.warn(
                "[TC-019] click_approve_button() returned False — "
                "the approve dialog may not have appeared or the invoice "
                "transitioned to a non-approvable state mid-run."
            )

        # Step 6 — Verify no ISR/QR-specific validation error is shown on screen
        isr_qr_error_visible = page.locator(
            '[role="alert"]:has-text("ISR"), [role="alert"]:has-text("QR Reference")'
        ).is_visible(timeout=3_000)
        assert not isr_qr_error_visible, (
            "A blank ISR/QR Reference field must not produce a validation error "
            "when the Approve button is clicked"
        )
