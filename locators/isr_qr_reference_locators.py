class IsrQrReferenceLocators:
    """
    Verified live selectors for the ISR/QR Reference feature.

    All locators confirmed against:
      https://zora.triumphpreprod.aiops-d.cloud/ap-invoice-management/
    on 2026-05-12 using Playwright live browser inspection.

    The app uses MUI components.  The ISR/QR Reference text-input has a
    stable DOM id ("isrQrReference") that is safe to target directly.
    Buttons without aria-label are targeted by their visible text / accessible name.
    """

    # -------------------------------------------------------------------------
    # Dashboard — search
    # -------------------------------------------------------------------------

    SEARCH_BAR_TESTID = "search-bar-input"
    SEARCH_ICON_BUTTON_NAME = "icon search"
    COOKIE_BANNER_ID = "onetrust-consent-sdk"
    NO_RESULTS_TEXT = "No results found"

    # -------------------------------------------------------------------------
    # Invoice Details Page — tab strip
    # -------------------------------------------------------------------------

    DETAILS_TAB_NAME = "Details"
    ITEMS_TAB_NAME   = "Items"
    HISTORY_TAB_NAME = "History"

    # -------------------------------------------------------------------------
    # Invoice Details Page — Edit / Save / Cancel buttons
    #
    # The Details tabpanel has "Edit Edit" (icon aria-label + visible text).
    # The header has a plain "Edit" (icon only). We target the tabpanel one.
    # -------------------------------------------------------------------------

    EDIT_BUTTON_IN_PANEL = "Edit Edit"
    SAVE_BUTTON_NAME   = "Save Save"
    CANCEL_BUTTON_NAME = "Cancel Cancel"

    # -------------------------------------------------------------------------
    # Invoice Details Page — bottom action bar
    # -------------------------------------------------------------------------

    APPROVE_BUTTON_NAME = "Approve"
    APPROVE_INVOICE_CONFIRM_NAME = "Approve Invoice"
    BACK_BUTTON_NAME = "Back"

    # -------------------------------------------------------------------------
    # ISR/QR Reference field
    #
    # In edit mode  : <input id="isrQrReference" placeholder="ISR/QR Reference">
    # In view mode  : <p>ISR/QR Reference</p> … <p>{value}</p> as siblings in a wrapper div
    # -------------------------------------------------------------------------

    ISR_QR_REFERENCE_INPUT_ID  = "isrQrReference"
    ISR_QR_REFERENCE_LABEL_TEXT = "ISR/QR Reference"
    ISR_QR_BLANK_DISPLAY        = "\u2014"  # em dash shown when field has no value
    ISR_QR_MAX_LENGTH           = 27       # HTML maxlength attribute confirmed live

    # -------------------------------------------------------------------------
    # URL patterns
    # -------------------------------------------------------------------------

    INVOICE_URL_PATTERN   = "**/invoice**"
    DASHBOARD_URL_PATTERN = "**/dashboard**"

    # -------------------------------------------------------------------------
    # Success / alert notifications
    # -------------------------------------------------------------------------

    SAVE_SUCCESS_ALERT_TEXT = "Updates saved successfully."
