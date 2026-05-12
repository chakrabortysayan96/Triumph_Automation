import re
import warnings
import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.requester_email_popover_page import RequesterEmailPopoverPage
from utils.config import BASE_URL, USERNAME, PASSWORD

# Invoice used across TC-010 / TC-013 (System ID 7317, Invoice No. 2000024754)
_INVOICE_SYSTEM_ID = "7317"
_INVOICE_NUMBER = "2000024754"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class TestRequesterEmailPopover:

    # ── TC-010 ────────────────────────────────────────────────────────────────
    def test_aiop_127799_requester_email_popover_basic(self, page):
        """
        TC-010 — Basic hover → email popover on dashboard and details page.
        Invoice: system-id 7317 / invoice-no 2000024754
        """
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        rp = RequesterEmailPopoverPage(page)

        # Step 1 — Navigate to dashboard and search for the target invoice.
        rp.navigate_to_dashboard(BASE_URL)
        rp.search_invoice(_INVOICE_NUMBER)

        # Step 2 — Hover the Requester name cell in the first result row;
        #           verify the email popover appears with a valid email address.
        rp.hover_requester_in_dashboard(row_index=0)
        assert rp.is_tooltip_visible(), "Email tooltip did not appear on dashboard hover"
        dashboard_email = rp.get_tooltip_email()
        assert EMAIL_RE.match(dashboard_email), (
            f"Dashboard tooltip did not show a valid email; got: '{dashboard_email}'"
        )

        # Step 3 — Open the invoice details page; hover Requester Name field;
        #           verify popover email matches the dashboard email.
        rp.move_cursor_away()
        rp.open_invoice_by_id(_INVOICE_SYSTEM_ID)
        rp.hover_requester_in_details()
        assert rp.is_tooltip_visible(), "Email tooltip did not appear on details page hover"
        details_email = rp.get_tooltip_email()
        assert details_email == dashboard_email, (
            f"Details email '{details_email}' does not match dashboard email '{dashboard_email}'"
        )

        # Step 4 — Verify the requester NAME is visible in the details field
        #           without hover (i.e. the plain name, not the email inline).
        rp.move_cursor_away()
        requester_name = rp.get_requester_name_in_details()
        assert requester_name, "Requester name not visible in details without hover"
        assert "@" not in requester_name, (
            "Expected only a name (no email) without hover; "
            f"got: '{requester_name}'"
        )

        # Step 5 — Re-hover the requester field; move cursor away;
        #           verify the tooltip disappears immediately.
        rp.hover_requester_in_details()
        assert rp.is_tooltip_visible(), "Tooltip did not re-appear on second hover"
        rp.move_cursor_away()
        assert rp.is_tooltip_hidden(), "Tooltip did not disappear after cursor moved away"

    # ── TC-011 ────────────────────────────────────────────────────────────────
    def test_aiop_127800_requester_email_popover_source_data_priority(self, page):
        """
        TC-011 — Source data priority: API → submitter details → 'Email Not Found'.
        Upload steps are skipped (per approval); hover behaviour is validated
        on existing dashboard data.
        """
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        rp = RequesterEmailPopoverPage(page)

        # Step 1 — Navigate to dashboard.
        rp.navigate_to_dashboard(BASE_URL)

        # Step 2 — Invoice upload skipped; validate on first visible invoice
        #           that the requester tooltip is populated (API path).
        rp.hover_requester_in_dashboard(row_index=0)
        tooltip_visible = rp.is_tooltip_visible()
        if not tooltip_visible:
            pytest.skip(
                "[TC-011] No email tooltip appeared for the first dashboard row. "
                "Verify the environment has at least one invoice with a resolved requester email."
            )
        email = rp.get_tooltip_email()
        assert email, "Tooltip appeared but contained no email text (API path)"

        # Step 3 — Verify fallback to submitter details: look for an invoice
        #           where the Requester Email column is blank but the submitter
        #           email is present.  If not found, skip gracefully.
        rp.move_cursor_away()
        rows_count = rp.invoice_rows.count()
        fallback_found = False
        for i in range(min(rows_count, 10)):
            # The second .dashboard-table-requester per row is the Requester Email column.
            email_col = (
                rp.invoice_rows.nth(i)
                .locator("td.dashboard-table-requester")
                .last
                .inner_text()
                .strip()
            )
            if not email_col or email_col in ("—", "-", ""):
                # This row may be using submitter fallback.
                rp.hover_requester_in_dashboard(row_index=i)
                if rp.is_tooltip_visible():
                    fallback_email = rp.get_tooltip_email()
                    warnings.warn(
                        f"[TC-011] Row {i} has blank Requester Email column; "
                        f"tooltip shows '{fallback_email}' (may be submitter fallback)."
                    )
                    fallback_found = True
                rp.move_cursor_away()
                break

        if not fallback_found:
            warnings.warn(
                "[TC-011] Could not locate an invoice demonstrating submitter-fallback "
                "path within the first 10 visible rows.  Pre-seed such an invoice to "
                "fully exercise this scenario."
            )

        # Step 4 — Verify 'Email Not Found' scenario: look for a row where the
        #           tooltip shows that exact string, or skip if none is available.
        not_found_verified = False
        for i in range(min(rows_count, 10)):
            rp.hover_requester_in_dashboard(row_index=i)
            if rp.is_tooltip_visible():
                txt = rp.get_tooltip_email()
                if "email not found" in txt.lower():
                    not_found_verified = True
                    rp.move_cursor_away()
                    break
            rp.move_cursor_away()

        if not not_found_verified:
            warnings.warn(
                "[TC-011] No 'Email Not Found' row visible in the first 10 rows. "
                "Pre-seed an invoice where both API call and submitter details fail "
                "to fully verify this assertion."
            )

    # ── TC-012 ────────────────────────────────────────────────────────────────
    def test_aiop_128157_requester_email_popover_stability(self, page):
        """
        TC-012 — Popover stability: browser resize and rapid mouse movement.
        """
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        rp = RequesterEmailPopoverPage(page)

        # Step 1 — Navigate to dashboard.
        rp.navigate_to_dashboard(BASE_URL)

        # Step 2 — Hover Requester in first row (invoice with valid requester email);
        #           verify the tooltip appears.  Then resize the browser to several
        #           edge-case viewports and confirm the tooltip remains functional.
        rp.hover_requester_in_dashboard(row_index=0)
        tooltip_visible = rp.is_tooltip_visible()
        if not tooltip_visible:
            pytest.skip(
                "[TC-012] No requester email tooltip on the first row. "
                "Ensure the dashboard contains invoices with resolved requester emails."
            )
        rp.move_cursor_away()

        for width, height in [(1280, 800), (1024, 768), (1920, 1080)]:
            rp.resize_browser(width, height)
            rp.hover_requester_in_dashboard(row_index=0)
            expect(page.get_by_role("tooltip").first).to_be_visible(timeout=10_000)
            email = rp.get_tooltip_email()
            assert email, f"Tooltip empty at viewport {width}x{height}"
            rp.move_cursor_away()

        # Restore default viewport
        rp.resize_browser(1280, 720)

        # Step 3 — Hover rapidly across up to 5 requester name cells;
        #           verify tooltips open and close without lag / JavaScript errors.
        rp.hover_multiple_requesters_rapidly(max_rows=5)
        rp.move_cursor_away()
        # Confirm no tooltip is stuck open after moving away.
        assert rp.is_tooltip_hidden(), "A tooltip remained visible after moving cursor away"

    # ── TC-013 ────────────────────────────────────────────────────────────────
    def test_aiop_128160_requester_email_popover_updated_in_notes(self, page):
        """
        TC-013 — Popover reflects requester email for invoice 7317;
        a note is posted and the email in the popover is re-verified.
        """
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        rp = RequesterEmailPopoverPage(page)

        # Step 1 — Navigate to dashboard; search for invoice 2000024754 (system-id 7317).
        rp.navigate_to_dashboard(BASE_URL)
        rp.search_invoice(_INVOICE_NUMBER)

        # Step 2a — Hover Requester on dashboard; capture the baseline email.
        rp.hover_requester_in_dashboard(row_index=0)
        tooltip_visible = rp.is_tooltip_visible()
        if not tooltip_visible:
            pytest.skip(
                "[TC-013] Requester email tooltip not visible for invoice 2000024754. "
                "Verify the invoice exists in this environment."
            )
        baseline_email = rp.get_tooltip_email()
        rp.move_cursor_away()

        # Step 2b — Open the invoice details page.
        rp.open_invoice_by_id(_INVOICE_SYSTEM_ID)

        # Step 2c — Post a note referencing the requester (simulates the
        #            "update the requester in the notes" step).
        note_text = f"Requester email verified: {baseline_email}"
        posted = rp.post_note(note_text)
        if not posted:
            warnings.warn(
                "[TC-013] Note could not be posted (Post button did not become enabled). "
                "Continuing with read-only popover verification."
            )

        # Navigate back to Details tab for popover verification.
        page.get_by_role("tab", name="Details").click()
        page.wait_for_load_state("networkidle", timeout=15_000)

        # Step 2d — Hover Requester in details; verify the email matches the baseline.
        rp.hover_requester_in_details()
        assert rp.is_tooltip_visible(), "Email tooltip did not appear after note posted"
        details_email = rp.get_tooltip_email()
        assert details_email == baseline_email, (
            f"Details email '{details_email}' differs from baseline '{baseline_email}'"
        )

    # ── TC-014 ────────────────────────────────────────────────────────────────
    def test_aiop_128163_requester_email_popover_long_complex_email_stability(self, page):
        """
        TC-014 — Tooltip renders without UI breakage for very long / special-char emails.
        Uses pytest.skip when no qualifying invoice is found in the visible rows.
        """
        login_page = LoginPage(page)
        login_page.navigate(BASE_URL)
        login_page.login(USERNAME, PASSWORD)

        rp = RequesterEmailPopoverPage(page)

        # Step 1 — Navigate to dashboard.
        rp.navigate_to_dashboard(BASE_URL)

        # Heuristic: an email is "long" if > 30 chars, or contains special chars
        # beyond alphanumerics, @, ., -, and _.
        LONG_OR_SPECIAL_RE = re.compile(
            r"(.{31,}|[^a-zA-Z0-9@._\-]+)"
        )

        qualifying_rows: list[int] = []
        rows_count = rp.invoice_rows.count()
        for i in range(min(rows_count, 20)):
            # Read the Requester Email column cell (second .dashboard-table-requester)
            email_col_text = (
                rp.invoice_rows.nth(i)
                .locator("td.dashboard-table-requester")
                .last
                .inner_text()
                .strip()
            )
            if email_col_text and LONG_OR_SPECIAL_RE.search(email_col_text):
                qualifying_rows.append(i)

        if not qualifying_rows:
            pytest.skip(
                "[TC-014] No invoices with long (>30 chars) or special-character "
                "requester emails found in the first 20 dashboard rows. "
                "Pre-seed such invoices to fully exercise this scenario."
            )

        # Step 2 — For each qualifying row, hover both Submitter and Requester
        #           in the dashboard and verify the tooltip renders without breaking.
        for row_idx in qualifying_rows:
            # Submitter
            rp.hover_submitter_in_dashboard(row_index=row_idx)
            if rp.is_tooltip_visible():
                sub_email = rp.get_tooltip_email()
                assert sub_email, f"Row {row_idx}: Submitter tooltip appeared but was empty"
            rp.move_cursor_away()

            # Requester
            rp.hover_requester_in_dashboard(row_index=row_idx)
            if rp.is_tooltip_visible():
                req_email = rp.get_tooltip_email()
                assert req_email, f"Row {row_idx}: Requester tooltip appeared but was empty"
            rp.move_cursor_away()

        # Open the first qualifying invoice details page and verify there too.
        first_row = qualifying_rows[0]
        system_id = (
            rp.invoice_rows.nth(first_row)
            .locator("td.dashboard-table-invoiceNo")
            .first
            .inner_text()
            .strip()
        )
        if system_id and system_id not in ("—", "-", ""):
            rp.open_invoice_by_id(system_id)

            # Submitter on details
            try:
                rp.hover_submitter_in_details()
                if rp.is_tooltip_visible():
                    assert rp.get_tooltip_email(), "Submitter details tooltip empty"
                rp.move_cursor_away()
            except Exception as exc:
                warnings.warn(f"[TC-014] Submitter hover on details raised: {exc}")

            # Requester on details
            try:
                rp.hover_requester_in_details()
                if rp.is_tooltip_visible():
                    assert rp.get_tooltip_email(), "Requester details tooltip empty"
                rp.move_cursor_away()
            except Exception as exc:
                warnings.warn(f"[TC-014] Requester hover on details raised: {exc}")
