class SubmitterEmailPopoverLocators:

    # --- Dashboard ---
    # Search / filter input — used to find invoices by number before clicking.
    SEARCH_INPUT = '[data-testid="search-bar-input"]'

    # Each row's Invoice Number cell; contains a <button> that opens the details page.
    INVOICE_NO_CELL = "td.dashboard-table-invoiceNo"

    # Each row's Submitter Name cell; hovering triggers the MUI Tooltip popover.
    # Confirmed via live inspection: CSS class `dashboard-table-submitter`.
    SUBMITTER_CELL = "td.dashboard-table-submitter"

    # MUI Tooltip root element — rendered outside the grid as a Popper portal.
    # Confirmed: role="tooltip" with inner <label> holding the email text.
    EMAIL_TOOLTIP = '[role="tooltip"]'

    # Inner <label> element inside the MUI Tooltip that holds the email string.
    EMAIL_TOOLTIP_LABEL = '[role="tooltip"] label'

    # Text shown when no email is associated with the submitter.
    EMAIL_NOT_AVAILABLE_TEXT = "Email not available"

    # --- Invoice Details Page ---
    # Top-level container class for the invoice details view.
    DETAILS_CONTAINER = ".s2pim-invoice-details"

    # Label paragraph for the Submitter field (uses non-standard `for` attribute).
    # Confirmed via live inspection: <p for="submitter">Submitter</p>
    SUBMITTER_LABEL = 'p[for="submitter"]'

    # The submitter name value is a <p class="truncate ..."> inside the sibling
    # `.fieldWrapper` div, two levels up from the label.
    SUBMITTER_VALUE = "p.truncate"

    # Back button text — navigates from details back to the dashboard.
    BACK_BUTTON = "Back"

    # --- URL patterns ---
    DASHBOARD_URL_PATTERN = "**/ap-invoice-management/dashboard**"
    DETAILS_URL_PATTERN = "**/ap-invoice-management/invoice**"
