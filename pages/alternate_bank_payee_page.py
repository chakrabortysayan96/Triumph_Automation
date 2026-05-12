import warnings
from datetime import date

from playwright.sync_api import Page, Locator, expect

from pages.base_page import BasePage
from locators.alternate_bank_payee_locators import AlternateBankPayeeLocators


class AlternateBankPayeePage(BasePage):
    """
    Page Object for the Alternate Bank Payee feature on the AP Invoice
    Management invoice details page.

    All locators verified live on 2026-05-12 against the preprod environment.
    MUI Autocomplete inputs are targeted by placeholder text because the app
    renders no data-testid attributes on those components.
    Network-mutating methods return bool; failures are emitted via warnings.warn.
    No assertions live here — they belong in the spec files.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Convenience locators (kept for backward-compatibility with existing callers)
        self.edit_button: Locator = page.get_by_role(
            "button", name=AlternateBankPayeeLocators.EDIT_BUTTON_IN_PANEL
        )
        self.save_button: Locator = page.get_by_role(
            "button", name=AlternateBankPayeeLocators.SAVE_BUTTON_NAME
        )
        self.approve_button: Locator = page.get_by_role(
            "button", name=AlternateBankPayeeLocators.APPROVE_BUTTON_NAME
        )
        self.cancel_button: Locator = page.get_by_role(
            "button", name=AlternateBankPayeeLocators.CANCEL_BUTTON_NAME
        )
        self.history_tab: Locator = page.get_by_role(
            "tab", name=AlternateBankPayeeLocators.HISTORY_TAB_NAME
        )
        self.details_tab: Locator = page.get_by_role(
            "tab", name=AlternateBankPayeeLocators.DETAILS_TAB_NAME
        )
        self.history_panel: Locator = page.get_by_role("tabpanel")

        # MUI Autocomplete inputs (no data-testid, identified by placeholder)
        self.vendor_dropdown: Locator = page.locator(
            f'input[placeholder="{AlternateBankPayeeLocators.SUPPLIER_ID_PLACEHOLDER}"]'
        )
        self.alternate_payee_dropdown: Locator = page.locator(
            f'input[placeholder="{AlternateBankPayeeLocators.ALTERNATE_PAYEE_PLACEHOLDER}"]'
        )

    # =========================================================================
    # Utility
    # =========================================================================

    def _dismiss_cookie_banner(self) -> None:
        """Remove the OneTrust consent overlay via JS so it cannot intercept clicks."""
        self.page.evaluate(
            f"document.getElementById('{AlternateBankPayeeLocators.COOKIE_BANNER_ID}')?.remove()"
        )

    def _expand_date_range_to_today(self) -> None:
        """
        Set the dashboard end-date filter to today so invoices with a recent
        record date are always included in search results.
        Closes the Ant Design calendar popup after filling so it cannot
        intercept subsequent clicks on the invoice grid.
        """
        today_str = date.today().strftime("%m/%d/%Y")
        try:
            end_date_input = self.page.get_by_placeholder("MM/DD/YYYY").nth(1)
            end_date_input.click(click_count=3, timeout=5_000)
            end_date_input.fill(today_str)
            # Use Tab (not Enter) to commit the value without keeping the calendar open
            end_date_input.press("Tab")
            # Force-close any residual Ant Design calendar popup via JS + keyboard
            self.page.evaluate(
                "() => document.querySelectorAll('.ant-picker-dropdown').forEach(e => e.remove())"
            )
            self.page.keyboard.press("Escape")
            try:
                self.page.locator(".ant-picker-dropdown").wait_for(
                    state="hidden", timeout=3_000
                )
            except Exception:
                pass
            self.page.wait_for_load_state("networkidle", timeout=15_000)
        except Exception:
            pass  # Date field absent (e.g. already navigated away); continue

    # =========================================================================
    # Navigation helpers
    # =========================================================================

    def navigate_to_landing_page(self, base_url: str) -> None:
        """Navigate to the dashboard landing page."""
        self.navigate(base_url)

    def search_and_open_invoice(self, invoice_number: str) -> None:
        """
        Search for invoice_number on the dashboard and open its details page.

        Steps:
          1. Dismiss cookie banner and any Ant Design date picker popup via JS
          2. Ensure search box is visible
          3. Fill and submit the search
          4. Click the matching invoice-number button in the grid
          5. Wait for the invoice details page to finish loading
        """
        self._dismiss_cookie_banner()
        # Also remove any open Ant Design date-picker popup via JS so it cannot
        # intercept clicks on the invoice grid row buttons.
        self.page.evaluate(
            "() => document.querySelectorAll('.ant-picker-dropdown').forEach(el => el.remove())"
        )

        search_input = self.page.get_by_test_id(AlternateBankPayeeLocators.SEARCH_BAR_TESTID)
        # Wait up to 60 s for the search bar to appear; the React dashboard sometimes
        # takes longer to hydrate after an SSO redirect (blank-page race condition).
        try:
            search_input.wait_for(state="visible", timeout=60_000)
        except Exception:
            try:
                self.page.get_by_role(
                    "button", name=AlternateBankPayeeLocators.SEARCH_ICON_BUTTON_NAME
                ).click(timeout=5_000)
                search_input.wait_for(state="visible", timeout=15_000)
            except Exception:
                pass  # Proceed; click will raise a clear error if still not visible

        search_input.click(click_count=3)
        search_input.fill(invoice_number)
        search_input.press("Enter")
        self.page.wait_for_load_state("networkidle", timeout=20_000)

        # Dismiss date picker popup again after the search triggers a reload
        # (the Ant Design portal may re-appear after navigation events).
        self.page.evaluate(
            "() => document.querySelectorAll('.ant-picker-dropdown').forEach(el => el.remove())"
        )

        self.page.get_by_role("button", name=invoice_number, exact=True).click(timeout=15_000)
        self.page.wait_for_url("**/invoice**", timeout=20_000)
        self.page.wait_for_load_state("networkidle", timeout=20_000)
        # Wait for the Details tab to appear — this confirms the invoice page has
        # fully hydrated (tabs are only rendered once the invoice data API response
        # has been received and the React component has mounted).
        try:
            self.page.get_by_role("tab", name="Details").wait_for(
                state="visible", timeout=20_000
            )
        except Exception:
            # Last resort: give the app extra time on slow environments
            self.page.wait_for_timeout(5_000)

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
        self.history_panel.wait_for(state="visible", timeout=10_000)

    # =========================================================================
    # Edit-mode lifecycle
    # =========================================================================

    def click_edit_button(self) -> None:
        """
        Click the Edit button inside the Details tabpanel to enter edit mode.
        Waits for the Cancel button to appear as confirmation that edit mode is active.

        Two fallback strategies handle MUI accessible-name variations (e.g. the
        button aria-label may be 'Edit Edit' when the icon and text are separate
        ARIA nodes, or just 'Edit' in some invoice states).
        Strategy 3 (page-wide button search) was intentionally removed — it is
        too broad and risks clicking header edit icons or other controls.
        """
        candidates = [
            self.edit_button,
            self.page.get_by_role("tabpanel")
            .get_by_role("button")
            .filter(has_text="Edit")
            .first,
        ]
        for locator in candidates:
            try:
                locator.click(timeout=10_000)
                expect(self.cancel_button).to_be_visible(timeout=15_000)
                return
            except Exception:
                pass
        raise TimeoutError(
            "Edit button not found — invoice may be in a non-editable state "
            "or the accessible name changed."
        )

    def click_save_button(self) -> bool:
        """
        Click Save and wait for the page to return to view mode.
        Returns True on success; logs a warning and returns False on failure.
        Network-mutating: triggers a PATCH/PUT request to the API.
        """
        try:
            self.save_button.click(timeout=15_000)
            self.page.wait_for_load_state("networkidle", timeout=30_000)
            return True
        except Exception as exc:
            warnings.warn(f"[AlternateBankPayeePage] click_save_button() failed: {exc}")
            return False

    def click_cancel_button(self) -> None:
        """Cancel edit mode without saving."""
        self.cancel_button.click()
        self.page.wait_for_load_state("networkidle", timeout=10_000)

    def click_approve_button(self) -> bool:
        """
        Click the Approve button in the bottom action bar.
        Returns True if successfully clicked; False if disabled or absent.
        ERP posting outcome is out of scope — this step only exercises the button.
        Network-mutating when enabled: triggers the ERP posting request.
        """
        try:
            if self.approve_button.is_disabled(timeout=3_000):
                warnings.warn(
                    "[AlternateBankPayeePage] Approve button is disabled — "
                    "invoice may not be in an approvable state."
                )
                return False
            self.approve_button.click(timeout=10_000)
            self.page.wait_for_load_state("networkidle", timeout=30_000)
            return True
        except Exception as exc:
            warnings.warn(f"[AlternateBankPayeePage] click_approve_button() failed: {exc}")
            return False

    def click_back_button(self) -> None:
        """Navigate back to the dashboard using the Back button."""
        self.page.get_by_role("button", name=AlternateBankPayeeLocators.BACK_BUTTON_NAME).click()
        self.page.wait_for_load_state("networkidle", timeout=15_000)

    # =========================================================================
    # Alternate Payee interactions (edit mode)
    # =========================================================================

    def is_alternate_payee_field_visible(self) -> bool:
        """Return True when the Alternate Payee label is visible in the Details tabpanel."""
        try:
            panel = self.page.get_by_role("tabpanel").first
            return (
                panel.get_by_text(
                    AlternateBankPayeeLocators.ALTERNATE_PAYEE_LABEL_TEXT, exact=True
                ).first.is_visible(timeout=10_000)
            )
        except Exception:
            return False

    def open_alternate_payee_dropdown(self) -> None:
        """Scroll the Alternate Payee input into the centre of the viewport (so
        the sticky bottom-action-bar cannot intercept the click) then click
        the MUI Autocomplete input to expand the option list."""
        self.alternate_payee_dropdown.scroll_into_view_if_needed()
        self.page.wait_for_timeout(200)
        self.alternate_payee_dropdown.click(timeout=10_000)

    def get_alternate_payee_dropdown_options(self) -> list:
        """Return all visible option label texts from the open Alternate Payee dropdown.

        Ensures the dropdown is open, waits for the listbox, then reads every
        li[role="option"] text. Returns an empty list when no options appear.
        """
        try:
            listbox = self.page.get_by_role("listbox")
            listbox.wait_for(state="visible", timeout=8_000)
            options = listbox.get_by_role("option").all()
            return [
                (opt.text_content() or "").strip()
                for opt in options
                if (opt.text_content() or "").strip()
            ]
        except Exception:
            return []

    def get_alternate_payee_dropdown_options_count(self) -> int:
        """Return the number of options visible in the Alternate Payee dropdown.

        The dropdown does NOT need to be pre-opened; this method opens it first.
        Returns 0 when the dropdown has no options or cannot be opened.
        """
        try:
            self.open_alternate_payee_dropdown()
            listbox = self.page.get_by_role("listbox")
            listbox.wait_for(state="visible", timeout=8_000)
            count = listbox.get_by_role("option").count()
            # Close the dropdown without selecting.
            self.page.keyboard.press("Escape")
            try:
                listbox.wait_for(state="hidden", timeout=3_000)
            except Exception:
                pass
            return count
        except Exception:
            return 0

    def get_alternate_payee_input_value(self) -> str:
        """Return the raw text currently shown in the Alternate Payee combobox input.

        Works in both edit mode (returns the typed / selected value) and view mode
        (falls back to the read-only paragraph text).
        """
        try:
            if self.alternate_payee_dropdown.is_visible(timeout=2_000):
                return (self.alternate_payee_dropdown.input_value(timeout=5_000) or "").strip()
        except Exception:
            pass
        return self.get_alternate_payee_value_readonly()

    def select_alternate_payee_option(self, option_value: str) -> None:
        """
        Open the Alternate Payee dropdown and select the option whose label
        contains option_value (partial match, case-sensitive).
        """
        self.open_alternate_payee_dropdown()
        option = self.page.get_by_role("option", name=option_value, exact=False)
        option.wait_for(state="visible", timeout=15_000)
        option.click()

    def type_in_alternate_payee_field(self, text: str) -> None:
        """
        Type raw text into the Alternate Payee input WITHOUT selecting a dropdown
        option.  Used to verify that free-text / partial input is rejected by MUI.
        """
        self.alternate_payee_dropdown.click(click_count=3)
        self.alternate_payee_dropdown.type(text, delay=60)

    def clear_alternate_payee_field(self) -> None:
        """
        Remove the current Alternate Payee selection by selecting all text and
        pressing Backspace, then Escape to close the dropdown without selecting.
        """
        self.alternate_payee_dropdown.click(click_count=3)
        self.alternate_payee_dropdown.press("Backspace")
        self.alternate_payee_dropdown.press("Escape")

    # =========================================================================
    # Supplier / Vendor interactions (edit mode)
    # =========================================================================

    def change_vendor(self, vendor_id: str) -> None:
        """
        Change the Supplier ID to vendor_id.
        The Supplier ID MUI Autocomplete can load its option list SLOWLY —
        a 45-second timeout is applied for the option to become visible.
        After selection, waits for the Alternate Payee field to refresh.
        """
        self.vendor_dropdown.click(click_count=3)
        self.vendor_dropdown.fill(vendor_id)
        option = self.page.get_by_role("option", name=vendor_id, exact=False)
        option.wait_for(state="visible", timeout=45_000)
        option.click()
        self.page.wait_for_load_state("networkidle", timeout=20_000)

    # =========================================================================
    # State inspection — view mode
    # =========================================================================

    def is_edit_button_visible(self) -> bool:
        """
        Return True if the Edit button is visible in the Details tabpanel.

        Three fallback strategies handle MUI accessible-name variations and
        async rendering delays after page navigation:
          1. Exact accessible-name 'Edit Edit' (icon + text) with an 8-second timeout.
          2. Any button inside the tabpanel whose text contains 'Edit' (partial).
          3. Any visible button on the page whose text contains 'Edit'.
        """
        try:
            if self.edit_button.is_visible(timeout=8_000):
                return True
        except Exception:
            pass
        try:
            if (
                self.page.get_by_role("tabpanel")
                .get_by_role("button")
                .filter(has_text="Edit")
                .first
                .is_visible(timeout=5_000)
            ):
                return True
        except Exception:
            pass
        try:
            return (
                self.page.locator("button", has_text="Edit")
                .first
                .is_visible(timeout=3_000)
            )
        except Exception:
            return False

    def is_edit_button_disabled(self) -> bool:
        """Return True if the Edit button is disabled (not interactable)."""
        try:
            return self.edit_button.is_disabled()
        except Exception:
            return True

    def get_alternate_payee_value_readonly(self) -> str:
        """
        Return the Alternate Payee value shown in read-only view mode.

        Reads the value from the DOM directly WITHOUT entering edit mode.
        Uses a TreeWalker JS traversal to collect all non-empty text nodes from
        the Details tabpanel in DOM order, then returns the text immediately
        after the 'Alternate Payee' label node.

        Returns '' on any failure, and '\u2014' (em dash) when the field is empty
        in the application (which renders empty values as '—').
        """
        try:
            tabpanel = self.page.get_by_role("tabpanel").first
            value = tabpanel.evaluate(
                """
                el => {
                    // Collect all non-whitespace text nodes in DOM order
                    const walker = document.createTreeWalker(
                        el, NodeFilter.SHOW_TEXT, null
                    );
                    const texts = [];
                    while (walker.nextNode()) {
                        const t = (walker.currentNode.textContent || '').trim();
                        if (t) texts.push(t);
                    }
                    // Find 'Alternate Payee' and return the next distinct text
                    for (let i = 0; i < texts.length; i++) {
                        if (texts[i] === 'Alternate Payee') {
                            for (let j = i + 1; j < texts.length; j++) {
                                const v = texts[j].trim();
                                if (v && v !== 'Alternate Payee') return v;
                            }
                        }
                    }
                    return '';
                }
                """
            )
            return (value or "").strip()
        except Exception:
            return ""

    def get_alternate_payee_value(self) -> str:
        """
        Return the current Alternate Payee value in either mode.
        Prefers the edit-mode input value; falls back to the read-only paragraph.
        """
        try:
            if self.alternate_payee_dropdown.is_visible(timeout=2_000):
                return self.alternate_payee_dropdown.input_value()
        except Exception:
            pass
        return self.get_alternate_payee_value_readonly()

    # =========================================================================
    # State inspection — edit mode
    # =========================================================================

    def is_alternate_payee_field_disabled(self) -> bool:
        """Return True if the Alternate Payee combobox input is disabled in edit mode."""
        try:
            return self.alternate_payee_dropdown.is_disabled(timeout=3_000)
        except Exception:
            return False

    def is_save_button_disabled(self) -> bool:
        """Return True if the Save button is currently disabled."""
        try:
            return self.save_button.is_disabled()
        except Exception:
            return True

    def is_approve_button_disabled(self) -> bool:
        """Return True if the Approve button in the bottom action bar is disabled."""
        try:
            return self.approve_button.is_disabled()
        except Exception:
            return True

    # =========================================================================
    # History tab helpers
    # =========================================================================

    def get_history_entry_count(self) -> int:
        """Count history entries by counting the 'User:' labels in the tabpanel."""
        try:
            tabpanel = self.page.get_by_role("tabpanel")
            return tabpanel.locator("p", has_text="User:").count()
        except Exception:
            return 0

    def get_history_entries(self) -> list:
        """
        Return a list of action strings from all visible history entries.
        Each item is the text that follows the 'Action:' label in an entry.
        """
        try:
            tabpanel = self.page.get_by_role("tabpanel")
            action_labels = tabpanel.locator("p", has_text="Action:").all()
            entries = []
            for label in action_labels:
                try:
                    value = label.locator(
                        "xpath=following-sibling::p[1]"
                    ).text_content().strip()
                    entries.append(value)
                except Exception:
                    pass
            return entries
        except Exception:
            return []

    def history_latest_entry_mentions_field(self, field_text: str) -> bool:
        """
        Return True if any paragraph in the current History tabpanel contains
        field_text.  Useful for asserting a field change was (or was not) recorded.
        """
        try:
            tabpanel = self.page.get_by_role("tabpanel")
            return tabpanel.locator("p", has_text=field_text).first.is_visible(timeout=3_000)
        except Exception:
            return False

    def is_history_entry_present(self, keyword: str) -> bool:
        """Return True if any history entry text contains keyword (case-insensitive)."""
        entries = self.get_history_entries()
        kw = keyword.lower()
        return any(kw in entry.lower() for entry in entries)
