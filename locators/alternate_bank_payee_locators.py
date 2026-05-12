class AlternateBankPayeeLocators:
    """
    Verified live selectors for the Alternate Bank Payee feature.

    All locators confirmed against:
      https://zora.triumphpreprod.aiops-d.cloud/ap-invoice-management/
    on 2026-05-12 using Playwright live browser inspection.

    The app uses MUI components. No data-testid attributes exist on the form
    fields — MUI Autocomplete inputs are identified by their placeholder text
    and the buttons by their ARIA accessible names.
    """

    # -------------------------------------------------------------------------
    # Dashboard — search
    # -------------------------------------------------------------------------

    # data-testid of the search box ("Search by Invoice, PO or Supplier")
    SEARCH_BAR_TESTID = "search-bar-input"

    # ARIA name of the toggle button that shows / hides the search bar
    SEARCH_ICON_BUTTON_NAME = "icon search"

    # data-testid of the "Clear filters" button shown in the empty-state banner
    CLEAR_FILTERS_TESTID = "clear-filters-button"

    # Element ID of the OneTrust cookie-consent overlay (dismissed via JS)
    COOKIE_BANNER_ID = "onetrust-consent-sdk"

    # -------------------------------------------------------------------------
    # Invoice Details Page — tab strip
    # -------------------------------------------------------------------------

    DETAILS_TAB_NAME = "Details"
    HISTORY_TAB_NAME = "History"

    # -------------------------------------------------------------------------
    # Invoice Details Page — Edit / Save / Cancel buttons
    #
    # The Details tabpanel contains its own Edit button labelled "Edit Edit"
    # (icon + visible text). The invoice header has a plain "Edit" button
    # (icon only). We target the tabpanel button to enter field-level edit mode.
    # -------------------------------------------------------------------------

    # Button ARIA name inside the Details tabpanel
    EDIT_BUTTON_IN_PANEL   = "Edit Edit"
    SAVE_BUTTON_NAME       = "Save Save"
    CANCEL_BUTTON_NAME     = "Cancel Cancel"

    # -------------------------------------------------------------------------
    # Invoice Details Page — bottom action bar
    # -------------------------------------------------------------------------

    APPROVE_BUTTON_NAME = "Approve"
    BACK_BUTTON_NAME    = "Back"

    # -------------------------------------------------------------------------
    # Invoice Details Page — form fields (edit mode)
    #
    # MUI Autocomplete / TextInput fields are identified by placeholder text.
    # MUI IDs (mui-NNN) are dynamic and must NOT be used.
    # -------------------------------------------------------------------------

    SUPPLIER_ID_PLACEHOLDER     = "Supplier ID"
    ALTERNATE_PAYEE_PLACEHOLDER = "Alternate Payee"
    DESCRIPTION_PLACEHOLDER     = "Description"

    # -------------------------------------------------------------------------
    # Alternate Payee — read-only label text (view mode)
    # -------------------------------------------------------------------------

    ALTERNATE_PAYEE_LABEL_TEXT = "Alternate Payee"

    # -------------------------------------------------------------------------
    # Alternate Payee — known dropdown option prefix (confirmed live)
    # Full option label: "0000030000 | SIXT Alt.Payer EUR bank Munich"
    # -------------------------------------------------------------------------

    ALTERNATE_PAYEE_OPTION_VALUE = "0000030000"

    # -------------------------------------------------------------------------
    # History tab
    # -------------------------------------------------------------------------

    # Accessible role of the tab panel; scopes history entry queries
    HISTORY_PANEL_ROLE = "tabpanel"

    # -------------------------------------------------------------------------
    # No-results state (dashboard)
    # -------------------------------------------------------------------------

    NO_RESULTS_TEXT = "No results found"
