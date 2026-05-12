class RequesterEmailPopoverLocators:
    """
    All locators discovered via live MCP browser inspection on
    https://zora.triumphpreprod.aiops-d.cloud/ap-invoice-management/dashboard
    """

    # ── Dashboard table ────────────────────────────────────────────────────
    # CSS class shared by every Requester-name cell (index 15) and the
    # Requester-Email column cell (index 26).  Use .first() per-row to get the
    # name cell; use .last() or .nth(1) to get the email column cell.
    DASHBOARD_REQUESTER_CELL_CSS = "td.dashboard-table-requester"

    # CSS class for the Submitter name cell (needed for TC-014).
    DASHBOARD_SUBMITTER_CELL_CSS = "td.dashboard-table-submitter"

    # Selects every data row in the dashboard grid.
    DASHBOARD_ROW_CSS = "table tbody tr"

    # ── Email tooltip (MUI Tooltip) ───────────────────────────────────────
    # Outer popper element; always present in the DOM but only visible on hover.
    EMAIL_TOOLTIP_ROLE = "tooltip"

    # Inner content element – use .text_content() or inner_text() to read email.
    EMAIL_TOOLTIP_CSS = ".MuiTooltip-tooltip"

    # ── Invoice details page – Requester field ────────────────────────────
    # The label paragraph uses a non-standard `for` attribute set by the app.
    DETAILS_REQUESTER_LABEL_CSS = 'p[for="requestor_name"]'

    # XPath: label p → parent div (div.inline.align-middle) → grandparent div
    # (div.RUPldswjkpaxnk7J5NsV) → second child div (div.fieldWrapper) →
    # descendant p.truncate that contains the name value.
    DETAILS_REQUESTER_VALUE_XPATH = (
        '//p[@for="requestor_name"]/../../div[2]//p[contains(@class,"truncate")]'
    )

    # ── Invoice details page – Submitter field ────────────────────────────
    DETAILS_SUBMITTER_LABEL_CSS = 'p[for="submitter"]'
    DETAILS_SUBMITTER_VALUE_XPATH = (
        '//p[@for="submitter"]/../../div[2]//p[contains(@class,"truncate")]'
    )

    # ── Navigation helpers ────────────────────────────────────────────────
    # The search box on the dashboard.
    SEARCH_BOX_TESTID = "search-bar-input"

    # The heading used as a neutral hover target to dismiss an active tooltip.
    AP_INVOICE_HEADING_TEXT = "AP Invoice Management"

    # ── Notes tab ─────────────────────────────────────────────────────────
    NOTES_TAB_NAME = "Notes"
    NOTES_TEXTBOX_ROLE = "textbox"
    NOTES_POST_BUTTON_NAME = "Post"
