import warnings
from playwright.sync_api import Page
from pages.base_page import BasePage
from locators.column_filters_locators import ColumnFilterLocators


class ColumnFiltersPage(BasePage):
    """
    Page Object for column-level filter interactions on the AP Invoice Management dashboard.

    All filter controls are inside a MUI Popover portal rendered to <body>.
    The popover is opened by clicking the funnel (MuiIconButton) inside a column header.
    """

    def __init__(self, page: Page):
        super().__init__(page)

    # -------------------------------------------------------------------------
    # Setup helpers
    # -------------------------------------------------------------------------

    def _dismiss_cookie_banner(self):
        """Removes the OneTrust cookie overlay so the grid is fully interactive."""
        self.page.evaluate(
            f"document.getElementById('{ColumnFilterLocators.COOKIE_SDK_ID}')?.remove()"
        )
        self.page.wait_for_timeout(300)

    def _col_th(self, column_name: str):
        """
        Returns a Playwright Locator scoped to the <th> whose .header-title button
        contains *exactly* the given column name text.
        """
        return self.page.locator("th").filter(
            has=self.page.locator(
                ColumnFilterLocators.COLUMN_HEADER_TITLE_BUTTON
            ).filter(has_text=column_name)
        )

    def _popover(self):
        """Returns the filter panel Locator (MUI Popover portal)."""
        return self.page.locator(ColumnFilterLocators.FILTER_POPOVER)

    # -------------------------------------------------------------------------
    # Filter icon visibility
    # -------------------------------------------------------------------------

    def has_filter_icon(self, column_name: str) -> bool:
        """
        Returns True when the specified column header contains a filter icon button.
        Non-filterable columns (e.g. Invoice Date) have no such button.
        """
        filter_btn = self._col_th(column_name).locator(
            ColumnFilterLocators.FILTER_ICON_BUTTON
        )
        return filter_btn.count() > 0

    # -------------------------------------------------------------------------
    # Opening the filter panel
    # -------------------------------------------------------------------------

    def click_column_filter_icon(self, column_name: str):
        """
        Clicks the funnel icon in the given column header and waits until the
        filter popover is visible before returning.
        """
        filter_btn = self._col_th(column_name).locator(
            ColumnFilterLocators.FILTER_ICON_BUTTON
        )
        filter_btn.click(timeout=10_000)
        self._popover().wait_for(state="visible", timeout=10_000)

    # -------------------------------------------------------------------------
    # Interacting with the filter panel
    # -------------------------------------------------------------------------

    def enter_search_term(self, search_term: str):
        """
        Types a search term into the filter panel's search input.
        The list of checkboxes updates reactively to show only matching values.
        """
        search_input = self._popover().locator(
            ColumnFilterLocators.FILTER_SEARCH_INPUT
        )
        search_input.clear()
        search_input.fill(search_term)
        self.page.wait_for_timeout(400)  # allow the list to re-render

    def get_available_filter_values(self) -> list:
        """
        Returns the list of checkbox values currently visible in the filter panel
        (i.e. those not hidden by the current search term).
        """
        checkboxes = self._popover().locator(ColumnFilterLocators.FILTER_CHECKBOX)
        return [
            checkboxes.nth(i).get_attribute("value")
            for i in range(checkboxes.count())
        ]

    def select_filter_value(self, value: str):
        """
        Checks the checkbox for the given value inside the filter panel.

        MUI checkboxes render the native <input> as opacity:0 (invisible) and
        handle state via React.  Playwright's force-check on the hidden input
        does not dispatch the React synthetic events that MUI relies on.
        Instead we click the parent MuiCheckbox-root span, which IS clickable
        and correctly triggers React's onChange handler.
        """
        checkbox_parent = self._popover().locator(
            f".MuiCheckbox-root:has({ColumnFilterLocators.FILTER_CHECKBOX}[value='{value}'])"
        )
        checkbox_parent.click(timeout=8_000)

    def select_filter_values(self, values: list):
        """Checks multiple checkboxes in the filter panel."""
        for value in values:
            self.select_filter_value(value)

    def is_apply_button_disabled(self) -> bool:
        """
        Returns True when the Apply button is disabled.

        Apply is disabled when:
          - No checkboxes are selected AND the search box is empty, OR
          - The search term matches zero values (no checkboxes rendered).
        """
        apply_btn = self._popover().get_by_role("button", name="Apply")
        return apply_btn.is_disabled()

    def apply_filter(self) -> bool:
        """
        Clicks the Apply button to commit the filter selection.
        Waits for the grid to finish reloading (networkidle).

        Returns True on success, False if the Apply button was disabled.
        Network-mutating: triggers a GET request with filter params.
        """
        apply_btn = self._popover().get_by_role("button", name="Apply")
        if apply_btn.is_disabled():
            warnings.warn(
                "[ColumnFiltersPage] apply_filter(): Apply button is disabled — "
                "no filter values selected or search term yielded no results."
            )
            return False
        apply_btn.click()
        # The grid shows a MuiCircularProgress spinner while it reloads the data.
        # wait_for_load_state("networkidle") fires before the spinner finishes;
        # instead wait for the spinner to disappear.
        spinner = self.page.locator('.MuiCircularProgress-root[role="progressbar"]')
        try:
            spinner.wait_for(state="visible", timeout=3_000)
        except Exception:
            pass  # spinner appeared and disappeared before we could catch it
        spinner.wait_for(state="hidden", timeout=30_000)
        return True

    def clear_all_filter(self):
        """Clicks 'Clear All' to deselect every checkbox in the open filter panel."""
        clear_btn = self._popover().get_by_role("button", name="Clear All")
        clear_btn.click(timeout=5_000)
        self.page.wait_for_timeout(300)

    def close_filter_panel(self):
        """
        Closes the filter panel by pressing Escape and waits for the popover to
        disappear from the DOM.
        """
        self.page.keyboard.press("Escape")
        self._popover().wait_for(state="hidden", timeout=8_000)

    # -------------------------------------------------------------------------
    # Grid inspection helpers
    # -------------------------------------------------------------------------

    def get_visible_row_count(self) -> int:
        """Returns the number of data rows currently rendered in the grid."""
        return self.page.locator(ColumnFilterLocators.GRID_DATA_ROWS).count()

    def get_all_row_texts(self) -> list:
        """
        Returns the full inner-text of every visible grid row as a list of strings.
        Useful for asserting that a column value is present in each row without
        needing to compute a column index.
        """
        rows = self.page.locator(ColumnFilterLocators.GRID_DATA_ROWS)
        return [rows.nth(i).inner_text() for i in range(rows.count())]
