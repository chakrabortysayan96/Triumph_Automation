class AssetAcctAsgmtLocators:
    """
    Selectors specific to the Asset Account Assignment (Acct Asgmt.) feature
    on the Items tab of the Invoice Details page.
    Confirmed via live MCP browser inspection on 2026-05-12.
    """

    # ── Cookie consent overlay ───────────────────────────────────────────────
    COOKIE_SDK_ID = "onetrust-consent-sdk"

    # ── Dashboard search ─────────────────────────────────────────────────────
    # data-testid on the wrapper div; the actual <input> is a child element
    SEARCH_INPUT_TESTID = "search-bar-input"
    LOADING_SPINNER_CSS = "[role='progressbar'], [class*='loading'], [class*='spinner']"
    INVOICE_NO_CELL_CSS = "td:nth-child(5)"
    INVOICE_ROW_CSS = "table tbody tr"

    # ── Items tab toolbar ────────────────────────────────────────────────────
    # The pencil icon button that opens the Edit Line panel.
    # Live inspection: the <button> wraps a <div aria-label="edit-icon">.
    # The button is disabled until a row checkbox is selected.
    EDIT_ICON_BTN_SELECTOR = 'button:has([aria-label="edit-icon"])'
    DELETE_ICON_BTN_SELECTOR = 'button:has([aria-label="delete-icon"])'

    # ── Row selection (Items grid) ───────────────────────────────────────────
    # Rows are standard <table tbody tr> elements. Each row's first cell
    # contains a <div class="clickable row …"> wrapping a checkbox <input>.
    ROW_CHECKBOX_CSS = "input[type='checkbox']"

    # ── Edit Line panel fields (confirmed by live DOM, 2026-05-12) ───────────
    # Description field
    DESCRIPTION_INPUT_ID = "description"
    # Acct Asgmt. MUI Autocomplete — the visible text input
    ACCT_ASGMT_INPUT_PLACEHOLDER = "Account Assignment"
    # Quantity
    QUANTITY_INPUT_ID = "quantity"
    # Unit Price
    UNIT_PRICE_INPUT_ID = "unitPrice"
    # GL Account MUI Autocomplete
    GL_ACCOUNT_INPUT_PLACEHOLDER = "GL Account"
    # Cost Center MUI Autocomplete
    COST_CENTER_INPUT_PLACEHOLDER = "Cost Center"
    # Internal Order MUI Autocomplete
    INTERNAL_ORDER_INPUT_PLACEHOLDER = "Internal Order"

    # MUI Autocomplete open / clear arrow buttons
    # These are identified by the aria-label attribute on the <button> element
    # that sits inside the same MuiFormControl container as the input.
    DROPDOWN_OPEN_BTN_ARIA = "Open"
    DROPDOWN_CLEAR_BTN_ARIA = "Clear"

    # ── Acct Asgmt. dropdown option labels ───────────────────────────────────
    # Confirmed options visible in the live listbox (role="option").
    ACCT_ASGMT_BLANK = "Blank [ ]"
    ACCT_ASGMT_COST_CENTER = "Cost Center (K)"
    ACCT_ASGMT_PROJECT = "Project (P)"
    ACCT_ASGMT_INTERNAL_ORDER = "Internal Order (I)"
    ACCT_ASGMT_ASSET = "Asset (A)"

    # ── Edit panel Save / Cancel buttons ────────────────────────────────────
    SAVE_BTN_TEXT = "Save"
    CANCEL_BTN_TEXT = "Cancel"

    # ── Items grid – Acct Asgmt. column cells ────────────────────────────────
    # In the Items grid the Acct Asgmt. value is in the 3rd visible column
    # (cell index 2, 0-based), rendered as plain text inside a <td>.
    ACCT_ASGMT_GRID_COL_HEADER = "Acct. Asgmt."

    # ── History tab ──────────────────────────────────────────────────────────
    HISTORY_USER_LABEL = "User:"
    HISTORY_DATE_LABEL = "Date:"
    HISTORY_ACTION_LABEL = "Action:"
    HISTORY_ROW_SELECTOR = "table tbody tr"

    # Exception / warning indicators (used in validation tests)
    ITEMS_TAB_EXCEPTION_BADGE = (
        '[role="tab"]:has-text("Items") .MuiBadge-badge, '
        '[role="tab"]:has-text("Items") [class*="badge"], '
        '[role="tab"]:has-text("Items") [class*="Badge"]'
    )
    ROW_WARNING_ICON_SELECTORS = [
        '[data-testid*="exception"]',
        '[data-testid*="warning"]',
        '[data-testid*="error"]',
        '[aria-label*="exception"]',
        '[aria-label*="warning"]',
        '[aria-label*="error"]',
        '.MuiSvgIcon-colorError',
        '.MuiSvgIcon-colorWarning',
        '[class*="exception"]',
        '[class*="ExceptionIcon"]',
    ]
