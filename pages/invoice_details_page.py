from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from locators.submitter_email_popover_locators import SubmitterEmailPopoverLocators


class InvoiceDetailsPage(BasePage):
    """Page Object for the Invoice Details page (/ap-invoice-management/invoice)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.back_button: Locator = page.get_by_role("button", name=SubmitterEmailPopoverLocators.BACK_BUTTON)

    def is_loaded(self) -> bool:
        return "/invoice" in self.page.url

    def get_invoice_number(self) -> str:
        text = self.page.locator("h3").first.inner_text()
        return text.replace("Invoice No.", "").strip()

    def hover_submitter_name(self) -> None:
        label = self.page.locator(SubmitterEmailPopoverLocators.SUBMITTER_LABEL).first
        container = label.locator("..").locator("..")
        name_el = container.locator(SubmitterEmailPopoverLocators.SUBMITTER_VALUE).first
        # Scroll the submitter field into the viewport so it is visible and stable
        name_el.scroll_into_view_if_needed()
        # Move cursor to top-left (safe area, away from any field tooltip triggers)
        # before hovering so the mouse path does not cross adjacent fields
        # (e.g., Requester above Submitter) that would trigger their own tooltips.
        self.page.mouse.move(0, 0)
        self.page.wait_for_timeout(300)
        # Dismiss any tooltip that may have appeared during the move
        try:
            self.page.locator('[role="tooltip"]').first.wait_for(
                state="hidden", timeout=1000
            )
        except Exception:
            pass
        name_el.hover(timeout=10000)
        # Wait for any transient mouse-path tooltips from adjacent fields to
        # fade out (MUI default transition ~200 ms) so only the submitter
        # tooltip remains before the caller reads it.
        self.page.wait_for_timeout(700)

    def get_submitter_popover_text(self, timeout: int = 4000) -> str:
        # Priority 1: email tooltip (contains @).
        # Filtering avoids capturing transient tooltips from adjacent fields
        # (e.g. Requester or invoice-number cells) during mouse traversal.
        email_tooltip = self.page.locator('[role="tooltip"]').filter(has_text="@").first
        try:
            email_tooltip.wait_for(state="visible", timeout=timeout)
            return email_tooltip.inner_text().strip()
        except Exception:
            pass

        # Priority 2: "Email not available" tooltip.
        not_avail_tooltip = self.page.locator('[role="tooltip"]').filter(
            has_text=SubmitterEmailPopoverLocators.EMAIL_NOT_AVAILABLE_TEXT
        ).first
        try:
            not_avail_tooltip.wait_for(state="visible", timeout=timeout // 2)
            return not_avail_tooltip.inner_text().strip()
        except Exception:
            pass

        return ""

    def is_submitter_popover_visible(self, timeout: int = 3000) -> bool:
        try:
            email = self.page.locator('[role="tooltip"]').filter(has_text="@").first
            email.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            pass
        try:
            not_avail = self.page.locator('[role="tooltip"]').filter(
                has_text=SubmitterEmailPopoverLocators.EMAIL_NOT_AVAILABLE_TEXT
            ).first
            return not_avail.is_visible()
        except Exception:
            return False

    def move_cursor_away(self) -> None:
        self.page.mouse.move(0, 0)

    def navigate_back(self) -> None:
        self.back_button.click()
        self.page.wait_for_url(
            SubmitterEmailPopoverLocators.DASHBOARD_URL_PATTERN,
            timeout=20000,
        )
        self.page.wait_for_load_state("load", timeout=15000)

    def _get_details_field_value(self, label: str) -> str:
        # DOM structure on the Details tab (view mode):
        #   div.Xr3J_...                  ← field row container (2 children)
        #     div.inline.align-middle     ← label wrapper
        #       p[for="..."]: <label>     ← label element  ← we find this
        #     div.fieldWrapper.inline     ← value wrapper  ← we want this text
        #
        # Strategy: find the label <p> inside the tabpanel, then navigate
        # 2 levels up (xpath=../..) to the field-row container, then select
        # the sibling div that carries the "fieldWrapper" CSS class.
        panel = self.page.get_by_role("tabpanel").first
        label_p = panel.locator("p").filter(has_text=label).first
        field_wrapper = label_p.locator(
            "xpath=../../div[contains(@class,'fieldWrapper')]"
        )
        field_wrapper.wait_for(state="attached", timeout=15_000)
        return field_wrapper.inner_text().strip()

    def get_invoice_due_date_on_details(self) -> str:
        # Returns the Invoice Due Date value from the Invoice Details tab panel.
        return self._get_details_field_value("Invoice Due Date")

    def get_bu_country_on_details(self) -> str:
        # Returns the BU Country value from the Invoice Details tab panel.
        return self._get_details_field_value("BU Country")
