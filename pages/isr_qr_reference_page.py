import warnings
from datetime import date

from playwright.sync_api import Page, Locator, expect

from pages.base_page import BasePage
from locators.isr_qr_reference_locators import IsrQrReferenceLocators


class IsrQrReferencePage(BasePage):
    """
    Page Object for the ISR/QR Reference feature on the AP Invoice Management
    invoice details page.

    All locators verified live on 2026-05-12 against the preprod environment.
    Network-mutating methods (Save, Approve) return bool and log failures via
    warnings.warn so that tests can decide whether to skip or assert.
    No assertions live here — they belong in the spec files.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.edit_button: Locator = page.get_by_role(
            "button", name=IsrQrReferenceLocators.EDIT_BUTTON_IN_PANEL
        )
        self.save_button: Locator = page.get_by_role(
            "button", name=IsrQrReferenceLocators.SAVE_BUTTON_NAME, exact=True
        )
        self.cancel_button: Locator = page.get_by_role(
            "button", name=IsrQrReferenceLocators.CANCEL_BUTTON_NAME, exact=True
        )
        self.approve_button: Locator = page.get_by_role(
            "button", name=IsrQrReferenceLocators.APPROVE_BUTTON_NAME, exact=True
        )
        self.history_tab: Locator = page.get_by_role(
            "tab", name=IsrQrReferenceLocators.HISTORY_TAB_NAME
        )
        self.details_tab: Locator = page.get_by_role(
            "tab", name=IsrQrReferenceLocators.DETAILS_TAB_NAME
        )
        self.isr_qr_reference_input: Locator = page.locator(
            f'#{IsrQrReferenceLocators.ISR_QR_REFERENCE_INPUT_ID}'
        )

    # =========================================================================
    # Private helpers
    # =========================================================================

    def _dismiss_cookie_banner(self) -> None:
        """Remove the OneTrust consent overlay via JS so it cannot intercept clicks."""
        self.page.evaluate(
            f"document.getElementById('{IsrQrReferenceLocators.COOKIE_BANNER_ID}')?.remove()"
        )

    def _expand_date_range_to_today(self) -> None:
        """
        Set the dashboard end-date filter to today so invoices with a recent
        record date are always included in search results.
        Aggressively closes the Ant Design calendar popup afterwards.
        """
        today_str = date.today().strftime("%m/%d/%Y")
        try:
            end_date_input = self.page.get_by_placeholder("MM/DD/YYYY").nth(1)
            end_date_input.click(click_count=3, timeout=5_000)
            end_date_input.fill(today_str)
            end_date_input.press("Enter")
            end_date_input.press("Tab")
            self.page.keyboard.press("Escape")
            # Click the page heading to force-dismiss any lingering calendar
            try:
                self.page.get_by_role("heading", level=1).first.click(timeout=2_000)
            except Exception:
                pass
            # Wait for calendar dropdown to disappear
            try:
                self.page.locator(".ant-picker-dropdown").wait_for(
                    state="hidden", timeout=5_000
                )
            except Exception:
                pass
            self.page.wait_for_load_state("networkidle", timeout=15_000)
        except Exception:
            pass

    # =========================================================================
    # Navigation
    # =========================================================================

    def navigate_to_landing_page(self, base_url: str) -> None:
        """Navigate to the dashboard landing page."""
        self.navigate(base_url)

    def search_and_open_invoice(self, invoice_number: str) -> None:
        """
        Search for invoice_number on the dashboard and open its details page.

        Steps:
          1. Dismiss cookie banner
          2. Close any open Ant Design date picker to unblock the grid
          3. Fill and submit the search by invoice number
          4. Click the matching invoice-number button in the grid
          5. Wait for the invoice details page to finish loading
        """
        self._dismiss_cookie_banner()

        # Close any open Ant Design date-range picker before interacting with the grid.
        # Clicking the search input reliably collapses the calendar.
        try:
            self.page.locator(".ant-picker-dropdown").first.wait_for(
                state="visible", timeout=1_500
            )
            # Calendar is open — click the heading to dismiss it
            self.page.get_by_role("heading", level=1).first.click(timeout=3_000)
            self.page.locator(".ant-picker-dropdown").first.wait_for(
                state="hidden", timeout=5_000
            )
        except Exception:
            pass

        search_input = self.page.get_by_test_id(IsrQrReferenceLocators.SEARCH_BAR_TESTID)
        if not search_input.is_visible(timeout=3_000):
            self.page.get_by_role(
                "button", name=IsrQrReferenceLocators.SEARCH_ICON_BUTTON_NAME
            ).click()
            expect(search_input).to_be_visible(timeout=5_000)

        search_input.click(click_count=3)
        search_input.fill(invoice_number)
        search_input.press("Enter")
        self.page.wait_for_load_state("networkidle", timeout=20_000)

        self.page.get_by_role("button", name=invoice_number, exact=True).click(timeout=15_000)
        self.page.wait_for_url("**/invoice**", timeout=20_000)
        self.page.wait_for_load_state("networkidle", timeout=20_000)
        # Wait for invoice content to render (Edit button confirms the Details tab loaded)
        self.edit_button.wait_for(state="visible", timeout=20_000)

    def navigate_away_without_saving(self, base_url: str) -> None:
        """
        Navigate directly to the dashboard URL, abandoning any unsaved edits.
        Using page.goto() bypasses client-side React Router navigation guards.
        """
        self.page.goto(base_url, wait_until="networkidle", timeout=30_000)

    # =========================================================================
    # Tab navigation
    # =========================================================================

    def click_details_tab(self) -> None:
        """Switch to the Details tab."""
        self.details_tab.click()
        self.page.wait_for_load_state("networkidle", timeout=10_000)

    def click_history_tab(self) -> None:
        """Switch to the History tab and wait for the panel to appear."""
        self.history_tab.click()
        self.page.get_by_role("tabpanel").wait_for(state="visible", timeout=10_000)

    # =========================================================================
    # Edit-mode lifecycle
    # =========================================================================

    def click_edit_button(self) -> None:
        """
        Click the Edit button inside the Details tabpanel to enter edit mode.
        Waits for the Cancel button to confirm that edit mode is active.
        """
        self.edit_button.click(timeout=15_000)
        expect(self.cancel_button).to_be_visible(timeout=15_000)

    def click_save_button(self) -> bool:
        """
        Click Save and wait for the success notification.
        Returns True on success; logs a warning and returns False on failure.
        Network-mutating: triggers a PATCH/PUT request to the API.
        """
        try:
            self.save_button.click(timeout=15_000)
            self.page.locator('[role="alert"]').wait_for(state="visible", timeout=15_000)
            self.page.wait_for_load_state("networkidle", timeout=30_000)
            return True
        except Exception as exc:
            warnings.warn(f"[IsrQrReferencePage] click_save_button() failed: {exc}")
            return False

    def click_cancel_button(self) -> None:
        """Cancel edit mode without saving."""
        self.cancel_button.click()
        self.page.wait_for_load_state("networkidle", timeout=10_000)

    def click_approve_button(self) -> bool:
        """
        Click the Approve button in the bottom action bar, then confirm in the
        modal dialog by clicking 'Approve Invoice'.
        Returns True if the flow completed; False if disabled or an error occurred.
        Network-mutating when enabled: triggers the ERP posting request.
        ERP posting outcome is out of scope — this step only exercises the button.
        """
        try:
            if self.approve_button.is_disabled(timeout=5_000):
                warnings.warn(
                    "[IsrQrReferencePage] Approve button is disabled — "
                    "invoice may not be in an approvable state."
                )
                return False
            self.approve_button.click(timeout=10_000)
            confirm_btn = self.page.get_by_role(
                "button",
                name=IsrQrReferenceLocators.APPROVE_INVOICE_CONFIRM_NAME,
                exact=True,
            )
            confirm_btn.wait_for(state="visible", timeout=10_000)
            confirm_btn.click()
            self.page.wait_for_load_state("networkidle", timeout=30_000)
            return True
        except Exception as exc:
            warnings.warn(f"[IsrQrReferencePage] click_approve_button() failed: {exc}")
            return False

    # =========================================================================
    # ISR/QR Reference field interactions
    # =========================================================================

    def enter_isr_qr_reference(self, value: str) -> None:
        """
        Clear the ISR/QR Reference input and fill it with value (edit mode only).
        Clears first (fill("")) to guarantee React detects a change even when the
        new value equals the currently stored value (preventing a disabled Save button).
        """
        self.isr_qr_reference_input.wait_for(state="visible", timeout=10_000)
        self.isr_qr_reference_input.scroll_into_view_if_needed()
        self.isr_qr_reference_input.click(click_count=3)
        self.isr_qr_reference_input.fill("")   # force React onChange
        self.isr_qr_reference_input.fill(value)

    def enter_isr_qr_reference_keystroke(self, value: str) -> None:
        """
        Simulate keyboard typing into the ISR/QR Reference field (edit mode only).
        Uses press_sequentially() which respects the HTML maxlength="27" attribute.
        Use this method when testing the 27-character limit enforcement (TC-012).
        """
        self.isr_qr_reference_input.wait_for(state="visible", timeout=10_000)
        self.isr_qr_reference_input.scroll_into_view_if_needed()
        self.isr_qr_reference_input.click(timeout=10_000)
        self.isr_qr_reference_input.press("Control+a")
        self.isr_qr_reference_input.press("Delete")
        self.isr_qr_reference_input.press_sequentially(value, delay=20)

    def get_isr_qr_reference_value(self) -> str:
        """
        Return the current ISR/QR Reference value.
        - Edit mode  : reads the text-input value via input_value().
        - View mode  : finds the 'ISR/QR Reference' label paragraph in the tabpanel
                       and returns the next sibling paragraph (the value cell).
        Returns an empty string if the field cannot be located.
        """
        try:
            if self.isr_qr_reference_input.is_visible(timeout=500):
                return self.isr_qr_reference_input.input_value()
        except Exception:
            pass
        # View mode: use JS to find the label paragraph and return its adjacent value paragraph
        try:
            raw: str = self.page.evaluate(
                """() => {
                    const panel = document.querySelector('[role="tabpanel"]');
                    if (!panel) return '';
                    const paras = Array.from(panel.querySelectorAll('p'));
                    const idx = paras.findIndex(
                        p => p.textContent.trim() === 'ISR/QR Reference'
                    );
                    if (idx >= 0 && idx + 1 < paras.length) {
                        return paras[idx + 1].textContent.trim();
                    }
                    return '';
                }"""
            )
            # Return empty string for blank display values (em-dash or plain dash)
            blank_values = {"\u2014", "\u2013", "-", "—", "–"}
            return "" if (raw or "") in blank_values else (raw or "")
        except Exception:
            return ""

    def get_isr_qr_reference_character_count(self) -> int:
        """Return the number of characters currently in the ISR/QR Reference field."""
        return len(self.get_isr_qr_reference_value())

    def is_isr_qr_reference_field_visible(self) -> bool:
        """
        Return True when the ISR/QR Reference row is present in the Details tabpanel
        (works in both view mode and edit mode).
        """
        try:
            return bool(
                self.page.evaluate(
                    """() => {
                        const panel = document.querySelector('[role="tabpanel"]');
                        if (!panel) return false;
                        const paras = Array.from(panel.querySelectorAll('p'));
                        return paras.some(p => p.textContent.trim() === 'ISR/QR Reference');
                    }"""
                )
            )
        except Exception:
            return False

    def is_isr_qr_reference_field_editable(self) -> bool:
        """
        Return True if the ISR/QR Reference input is visible and not disabled
        (i.e. the page is in edit mode and the field accepts input).
        """
        try:
            return (
                self.isr_qr_reference_input.is_visible(timeout=2_000)
                and not self.isr_qr_reference_input.is_disabled()
            )
        except Exception:
            return False

    def is_edit_button_visible_and_enabled(self) -> bool:
        """
        Return True if the Edit button inside the Details tabpanel is both
        visible and not disabled (i.e. the current user has edit rights).
        """
        try:
            return (
                self.edit_button.is_visible(timeout=5_000)
                and not self.edit_button.is_disabled()
            )
        except Exception:
            return False

    def is_edit_button_disabled(self) -> bool:
        """Return True if the Edit button is absent or disabled."""
        try:
            if not self.edit_button.is_visible(timeout=3_000):
                return True
            return self.edit_button.is_disabled()
        except Exception:
            return True

    # =========================================================================
    # Items tab helpers
    # =========================================================================

    def click_items_tab(self) -> None:
        """Switch to the Items tab and wait for the line-items table to load."""
        self.page.get_by_role("tab", name=IsrQrReferenceLocators.ITEMS_TAB_NAME).click()
        self.page.wait_for_load_state("networkidle", timeout=10_000)

    def get_items_tab_column_headers(self) -> list:
        """
        Navigate to the Items tab and return all column header texts from the
        line-items table. Used to assert that ISR/QR Reference is NOT a column there.
        """
        self.click_items_tab()
        panel = self.page.get_by_role("tabpanel").last
        headers = panel.get_by_role("columnheader").all()
        return [(h.text_content() or "").strip() for h in headers]

    # =========================================================================
    # Misc
    # =========================================================================

    def scroll_to_details_section(self) -> None:
        """
        Ensure the Details tab is active and scroll the ISR/QR Reference
        field label into view. Works in both view mode and edit mode.
        """
        try:
            details_tab = self.page.get_by_role(
                "tab", name=IsrQrReferenceLocators.DETAILS_TAB_NAME
            )
            if details_tab.get_attribute("aria-selected") != "true":
                details_tab.click()
                self.page.wait_for_load_state("networkidle", timeout=10_000)
            # In view mode, scroll to the label paragraph; in edit mode, scroll to the input
            try:
                self.isr_qr_reference_input.scroll_into_view_if_needed(timeout=2_000)
                return
            except Exception:
                pass
            panel = self.page.get_by_role("tabpanel").first
            panel.locator("p").filter(
                has_text=IsrQrReferenceLocators.ISR_QR_REFERENCE_LABEL_TEXT
            ).first.scroll_into_view_if_needed()
        except Exception:
            pass

    def resize_browser_window(self, width: int, height: int) -> None:
        """Resize the browser viewport to the given dimensions."""
        self.page.set_viewport_size({"width": width, "height": height})

    def get_history_entries(self) -> list:
        """Return a list of text entries from the History tab panel."""
        try:
            panel = self.page.get_by_role("tabpanel")
            items = panel.locator("li, [role='listitem']").all()
            return [item.text_content().strip() for item in items]
        except Exception:
            return []
