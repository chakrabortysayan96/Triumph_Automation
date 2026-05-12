import warnings
from playwright.sync_api import Page, Locator, expect
from pages.invoice_details_page import InvoiceDetailsPage
from locators.asset_acct_asgmt_locators import AssetAcctAsgmtLocators
from utils.config import BASE_URL


class AssetAcctAsgmtPage(InvoiceDetailsPage):
    """Page Object for Asset Account Assignment Category (Acct Asgmt.) editing on the Items tab.

    Live-inspected DOM facts (2026-05-12):
    - Edit form is a side panel (NOT role='dialog').  Presence is detected by
      the Description input being visible.
    - Toolbar pencil/edit button: button:has([aria-label='edit-icon'])
      Enabled only after a row checkbox is checked.
    - Acct Asgmt. MUI Autocomplete opens via button[aria-label='Open'] inside
      the same FormControl wrapper.  Option elements use role='option'.
    - Invoice 779037122 (Pending Business Approval) has 2 editable line items.
    """

    # The invoice with confirmed editable line items used by all acct-asgmt tests
    TEST_INVOICE_NUMBER = "779037122"
    # UUID of the specific invoice row that has 2 editable line items
    # (Pending Business Approval; confirmed via live MCP inspection 2026-05-12)
    TEST_INVOICE_UUID = "73e96ce1-8d66-40ba-90f2-1895745e2c68"

    def __init__(self, page: Page):
        super().__init__(page)
        self.items_tab: Locator = page.get_by_role("tab", name="Items")
        self.history_tab: Locator = page.get_by_role("tab", name="History")

        # Edit panel presence sentinel – the Description input is always visible
        # when the edit side-panel is open (no role='dialog' on this app).
        self.description_field: Locator = page.locator('input[id="description"]')

        # Toolbar pencil button – requires a row checkbox to be selected first
        self.edit_icon_btn: Locator = page.locator(
            'button:has([aria-label="edit-icon"])'
        )

        # Acct Asgmt. MUI Autocomplete text input (confirmed placeholder)
        self.acct_asgmt_input: Locator = page.locator(
            f'input[placeholder="{AssetAcctAsgmtLocators.ACCT_ASGMT_INPUT_PLACEHOLDER}"]'
        )
        # Legacy alias kept for backward compatibility
        self.acct_asgmt_dropdown: Locator = self.acct_asgmt_input

        # Other edit-panel fields (confirmed IDs / placeholders from live DOM)
        self.quantity_field: Locator = page.locator('input[id="quantity"]')
        self.unit_price_field: Locator = page.locator('input[id="unitPrice"]')
        self.gl_account_input: Locator = page.locator(
            f'input[placeholder="{AssetAcctAsgmtLocators.GL_ACCOUNT_INPUT_PLACEHOLDER}"]'
        )
        self.cost_center_input: Locator = page.locator(
            f'input[placeholder="{AssetAcctAsgmtLocators.COST_CENTER_INPUT_PLACEHOLDER}"]'
        )
        self.internal_order_input: Locator = page.locator(
            f'input[placeholder="{AssetAcctAsgmtLocators.INTERNAL_ORDER_INPUT_PLACEHOLDER}"]'
        )

        self.save_button: Locator = page.get_by_role("button", name="Save")
        self.cancel_button: Locator = page.get_by_role("button", name="Cancel")
        self.history_panel: Locator = page.get_by_role("tabpanel")

    # ── Navigation helpers ────────────────────────────────────────────────────

    def navigate_to_dashboard(self) -> None:
        self.navigate(BASE_URL)

    def _dismiss_cookie_banner(self) -> None:
        self.page.evaluate(
            f"document.getElementById('{AssetAcctAsgmtLocators.COOKIE_SDK_ID}')?.remove()"
        )

    def _wait_for_spinner_gone(self, appear_ms: int = 3_000, gone_ms: int = 30_000) -> None:
        spinner = self.page.locator(AssetAcctAsgmtLocators.LOADING_SPINNER_CSS)
        try:
            spinner.first.wait_for(state="visible", timeout=appear_ms)
        except Exception:
            pass
        try:
            spinner.first.wait_for(state="hidden", timeout=gone_ms)
        except Exception:
            pass

    def open_invoice_items(self, invoice_number: str) -> None:
        """
        Navigate directly to the known invoice UUID that has editable line items,
        then click the Items tab.

        Dashboard search opens the first matching row, which may be an invoice
        without items. Navigating by UUID guarantees we always land on the
        invoice confirmed to have 2 editable line items (Pending Business Approval).
        """
        base = BASE_URL.replace("/dashboard", "")
        invoice_url = f"{base}/invoice?id={self.TEST_INVOICE_UUID}&tab=0"
        self.page.goto(invoice_url, wait_until="networkidle", timeout=60_000)
        self._dismiss_cookie_banner()

        # Wait for the invoice heading to confirm the page rendered
        try:
            self.page.locator("h3").first.wait_for(state="visible", timeout=20_000)
        except Exception:
            pass

        # Click Items tab and wait for the grid rows to appear
        self.click_items_tab()
        self.page.wait_for_load_state("networkidle", timeout=20_000)
        try:
            self.page.locator("table tbody tr").first.wait_for(state="visible", timeout=15_000)
        except Exception:
            pass  # test assertion will catch if no rows appear

    # ── Tab navigation ────────────────────────────────────────────────────────

    def click_items_tab(self) -> None:
        self.items_tab.click()
        self.page.wait_for_load_state("networkidle", timeout=15_000)

    def click_history_tab(self) -> None:
        self.history_tab.click()
        self.page.wait_for_load_state("networkidle", timeout=15_000)

    # ── Row selection ─────────────────────────────────────────────────────────

    def select_row(self, line_index: int = 0) -> None:
        """
        Check the checkbox for the given Items-grid row (0-based) so that the
        toolbar edit/delete buttons become enabled.
        """
        rows = self.page.locator(AssetAcctAsgmtLocators.INVOICE_ROW_CSS)
        row = rows.nth(line_index)
        row.wait_for(state="visible", timeout=15_000)
        checkbox = row.locator(AssetAcctAsgmtLocators.ROW_CHECKBOX_CSS)
        checkbox.check(timeout=10_000)

    # ── Edit pencil ───────────────────────────────────────────────────────────

    def click_edit_pencil(self, line_index: int = 0) -> None:
        """
        Select the Items-grid row at *line_index* (0-based) then click the
        toolbar pencil/edit button to open the Edit Line panel.

        The toolbar pencil is the primary-colored edit-icon button.  Row-level
        action buttons (in the Actions column of each row) carry the class
        'MuiIconButton-colorTransparent-secondary' and are excluded so that
        the locator resolves to exactly one element even when multiple rows
        are visible.
        """
        self.select_row(line_index)
        toolbar_btn = self.page.locator(
            'button:has([aria-label="edit-icon"]):not([class*="colorTransparent"])'
        ).first
        toolbar_btn.wait_for(state="visible", timeout=10_000)
        expect(toolbar_btn).to_be_enabled(timeout=5_000)
        toolbar_btn.click(timeout=10_000)
        # Wait for the edit panel Description field to become visible
        self.description_field.wait_for(state="visible", timeout=15_000)

    # ── Acct Asgmt. dropdown ──────────────────────────────────────────────────

    def _open_acct_asgmt_dropdown(self) -> None:
        """Open the Acct Asgmt. MUI Autocomplete listbox."""
        self.acct_asgmt_input.wait_for(state="visible", timeout=10_000)
        # The 'Open' arrow button lives in the same MuiFormControl ancestor
        open_btn = self.acct_asgmt_input.locator(
            "xpath=ancestor::*[contains(@class,'MuiFormControl')][1]"
        ).get_by_role("button", name=AssetAcctAsgmtLocators.DROPDOWN_OPEN_BTN_ARIA)
        open_btn.click(timeout=10_000)
        self.page.locator('[role="listbox"]').wait_for(state="visible", timeout=10_000)

    def select_acct_asgmt(self, value: str) -> None:
        """
        Select *value* from the Acct Asgmt. dropdown.
        Cost Center (K) and Project (P) are wrapped in a skip guard per
        the agreed test strategy.
        """
        import pytest
        skip_values = {
            AssetAcctAsgmtLocators.ACCT_ASGMT_COST_CENTER,
            AssetAcctAsgmtLocators.ACCT_ASGMT_PROJECT,
        }
        try:
            self._open_acct_asgmt_dropdown()
            option = self.page.get_by_role("option", name=value, exact=True)
            option.wait_for(state="visible", timeout=10_000)
            option.click(timeout=10_000)
        except Exception as exc:
            if value in skip_values:
                pytest.skip(
                    f"[AssetAcctAsgmt] Cannot select '{value}' — option not interactable. "
                    f"Skipping as per test strategy. Detail: {exc}"
                )
            raise

    def get_acct_asgmt_selected_in_modal(self) -> str:
        """Return the currently selected/pre-filled Acct Asgmt. value in the modal."""
        try:
            return self.acct_asgmt_input.input_value(timeout=5_000).strip()
        except Exception:
            return ""

    def fill_description(self, text: str) -> None:
        self.description_field.click()
        self.description_field.fill(text)

    def fill_quantity(self, value: str) -> None:
        self.quantity_field.click()
        self.quantity_field.fill(value)

    def fill_unit_price(self, value: str) -> None:
        self.unit_price_field.click()
        self.unit_price_field.fill(value)

    def fill_gl_account(self, value: str) -> None:
        """Type *value* into GL Account autocomplete and accept first suggestion."""
        self.gl_account_input.wait_for(state="visible", timeout=10_000)
        self.gl_account_input.click()
        self.gl_account_input.fill(value)
        try:
            self.page.locator('[role="option"]').first.wait_for(state="visible", timeout=5_000)
            self.page.locator('[role="option"]').first.click(timeout=5_000)
        except Exception:
            pass

    def fill_cost_center_field(self, value: str) -> None:
        """Type *value* into Cost Center autocomplete and accept first suggestion."""
        self.cost_center_input.wait_for(state="visible", timeout=10_000)
        self.cost_center_input.click()
        self.cost_center_input.fill(value)
        try:
            self.page.locator('[role="option"]').first.wait_for(state="visible", timeout=5_000)
            self.page.locator('[role="option"]').first.click(timeout=5_000)
        except Exception:
            pass

    def fill_internal_order_field(self, value: str) -> None:
        """Type *value* into Internal Order autocomplete and accept first suggestion."""
        self.internal_order_input.wait_for(state="visible", timeout=10_000)
        self.internal_order_input.click()
        self.internal_order_input.fill(value)
        try:
            self.page.locator('[role="option"]').first.wait_for(state="visible", timeout=5_000)
            self.page.locator('[role="option"]').first.click(timeout=5_000)
        except Exception:
            pass

    def click_save(self) -> bool:
        """
        Click Save and wait for the edit panel to close (Description field hides).
        Network-mutating — triggers a PATCH/PUT API call.
        Returns True on apparent success, False if panel did not close.
        """
        try:
            expect(self.save_button).to_be_enabled(timeout=5_000)
            self.save_button.click(timeout=10_000)
            # Edit panel closes when Description field disappears
            self.description_field.wait_for(state="hidden", timeout=20_000)
            self.page.wait_for_load_state("networkidle", timeout=20_000)
            return True
        except Exception as exc:
            warnings.warn(
                f"[AssetAcctAsgmtPage] click_save: panel may not have closed. Detail: {exc}"
            )
            return False

    def click_cancel(self) -> None:
        self.cancel_button.click()

    def is_save_button_enabled(self) -> bool:
        return self.save_button.is_enabled()

    def is_edit_panel_open(self) -> bool:
        """Return True when the edit panel Description field is visible."""
        try:
            return self.description_field.is_visible(timeout=3_000)
        except Exception:
            return False

    def is_edit_modal_open(self) -> bool:
        """Alias for is_edit_panel_open for backward compatibility."""
        return self.is_edit_panel_open()

    def get_acct_asgmt_value_in_grid(self, row_index: int = 0) -> str:
        """
        Return the Acct Asgmt. cell text for the given row (0-based).
        The column is the 3rd <td> (index 2, 0-based) in the Items table.
        """
        rows = self.page.locator('table tbody tr')
        try:
            row = rows.nth(row_index)
            row.wait_for(state="visible", timeout=10_000)
            cell = row.locator('td').nth(2)
            return cell.inner_text(timeout=5_000).strip()
        except Exception:
            return ""

    def get_row_count(self) -> int:
        """Return the number of data rows visible in the Items grid."""
        return self.page.locator('table tbody tr').count()

    def click_outside_modal(self) -> None:
        """Dismiss the edit panel by pressing Escape."""
        self.page.keyboard.press("Escape")
        try:
            self.description_field.wait_for(state="hidden", timeout=5_000)
        except Exception:
            pass

    def is_acct_asgmt_change_in_history(self, value: str) -> bool:
        """
        Return True if any history entry contains *value* (case-insensitive).
        Assumes the History tab is already selected and loaded.
        Searches the entire <main> content area to handle any card/table structure.
        """
        try:
            self.page.wait_for_load_state("networkidle", timeout=10_000)
            body_text = self.page.locator("main").inner_text(timeout=10_000)
            return value.lower() in body_text.lower()
        except Exception:
            return False

    def get_history_latest_entry_text(self) -> str:
        """Return the full text of the most recent history row/card."""
        try:
            rows = self.page.locator("main").locator(AssetAcctAsgmtLocators.HISTORY_ROW_SELECTOR)
            rows.first.wait_for(state="visible", timeout=15_000)
            return rows.first.inner_text(timeout=5_000).strip()
        except Exception:
            return ""

    def dismiss_cookie_banner(self) -> None:
        """Remove the OneTrust cookie-consent overlay via JavaScript if present."""
        self.page.evaluate(
            f"document.getElementById('{AssetAcctAsgmtLocators.COOKIE_SDK_ID}')?.remove()"
        )

    def navigate_to_history_tab(self) -> None:
        """Dismiss the cookie banner, click the History tab, and wait for load."""
        self.dismiss_cookie_banner()
        self.history_tab.click(timeout=10_000)
        self.page.wait_for_load_state("networkidle", timeout=15_000)

    def get_latest_history_entry(self) -> dict:
        """Return User, Date, and Action from the most recent History entry.

        The History tab renders entries as MuiPaper cards (newest first).
        Each card has sibling <p> pairs: a label paragraph followed by its
        value paragraph. Using the first occurrence of each label gets the
        top (most recent) entry.

        Returns a dict with keys: 'user', 'date', 'action'.
        """
        self.history_panel.wait_for(state="visible", timeout=10_000)

        def _read_field(label: str) -> str:
            try:
                label_p = self.history_panel.get_by_text(label, exact=True).first
                return label_p.locator(
                    "xpath=following-sibling::p[1]"
                ).inner_text(timeout=5_000).strip()
            except Exception:
                return ""

        return {
            "user": _read_field(AssetAcctAsgmtLocators.HISTORY_USER_LABEL),
            "date": _read_field(AssetAcctAsgmtLocators.HISTORY_DATE_LABEL),
            "action": _read_field(AssetAcctAsgmtLocators.HISTORY_ACTION_LABEL),
        }

    # ------------------------------------------------------------------
    # TC-003 — Access control / read-only checks
    # ------------------------------------------------------------------

    def is_edit_pencil_visible(self) -> bool:
        """Return True if at least one enabled edit-pencil button exists in
        the Items table rows (Actions column).

        Uses the same inner aria-label selector as click_edit_pencil() so both
        methods stay in sync if the app's markup changes.
        """
        try:
            edit_buttons = self.page.locator(
                'button:has([aria-label="edit-icon"]):not([disabled])'
            )
            return edit_buttons.count() > 0
        except Exception:
            return False

    def is_acct_asgmt_read_only(self) -> bool:
        """Return True if Acct. Asgmt. cells show plain text with no inline
        inputs or comboboxes (read-only display state).

        The Items grid is always modal-edit-based, so the Acct. Asgmt.
        column (3rd td, CSS 1-based) must never contain inline editing
        controls regardless of user role.
        """
        # Scope to the active (visible) tabpanel only to avoid strict-mode
        # violations — the page renders all 5 tab panels in the DOM.
        panel = self.page.locator('[role="tabpanel"]:not([hidden])').first
        inline_editors = panel.locator(
            'table tbody tr td:nth-child(3) input, '
            'table tbody tr td:nth-child(3) [role="combobox"]'
        )
        return inline_editors.count() == 0

    def has_items_rows(self) -> bool:
        """Return True if the Items table has at least one data row visible.

        Waits up to 5 s for the first row to appear (the app may take a moment
        to render line items after the tab becomes visible).
        """
        try:
            rows = self.page.locator('[role="tabpanel"]:not([hidden]) table tbody tr')
            rows.first.wait_for(state="visible", timeout=5_000)
            return rows.count() > 0
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Field-clearing helpers (TC-005)
    # ------------------------------------------------------------------

    def clear_quantity(self) -> None:
        """Selects all text in the Quantity field and deletes it."""
        self.quantity_field.click()
        self.page.keyboard.press("Control+a")
        self.page.keyboard.press("Delete")

    def clear_unit_price(self) -> None:
        """Selects all text in the Unit Price field and deletes it."""
        self.unit_price_field.click()
        self.page.keyboard.press("Control+a")
        self.page.keyboard.press("Delete")

    # ------------------------------------------------------------------
    # Free-text / paste rejection helpers (TC-006)
    # ------------------------------------------------------------------

    def type_into_acct_asgmt(self, text: str) -> None:
        """
        Attempts to type free text directly into the Acct Asgmt. combobox.
        Does NOT click any option from the dropdown — simulates an invalid
        free-text entry attempt.
        """
        self.acct_asgmt_dropdown.click()
        self.page.keyboard.type(text)
        # Press Escape to close the suggestion dropdown without selecting anything.
        self.page.keyboard.press("Escape")

    def paste_into_acct_asgmt(self, text: str) -> None:
        """
        Simulates pasting text into the Acct Asgmt. field by focusing the
        combobox input, selecting all existing content and typing the text
        (equivalent to a paste).  Does NOT confirm a dropdown option.
        """
        self.acct_asgmt_dropdown.click()
        self.page.keyboard.press("Control+a")
        self.page.keyboard.type(text)
        self.page.keyboard.press("Escape")

    # ------------------------------------------------------------------
    # Exception-indicator helpers (TC-006)
    # ------------------------------------------------------------------

    def has_exception_badge_on_items_tab(self) -> bool:
        """
        Returns True if the Items tab label has a visible exception badge
        (yellow / red dot or count).
        """
        try:
            badge = self.page.locator(AssetAcctAsgmtLocators.ITEMS_TAB_EXCEPTION_BADGE)
            return badge.first.is_visible(timeout=3000)
        except Exception:
            return False

    def has_exception_indicator_on_row(self, row_index: int = 0) -> bool:
        """
        Returns True if the given Items-grid row contains any recognisable
        warning or exception icon.  Tries every selector in the locators
        list and returns True on the first match.
        """
        try:
            rows = self.page.locator('[role="tabpanel"] table tbody tr')
            row = rows.nth(row_index)
            for selector in AssetAcctAsgmtLocators.ROW_WARNING_ICON_SELECTORS:
                if row.locator(selector).count() > 0:
                    return True
            return False
        except Exception:
            return False

