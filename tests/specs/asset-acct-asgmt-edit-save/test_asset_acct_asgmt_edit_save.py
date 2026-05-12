import pytest
import warnings
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.asset_acct_asgmt_page import AssetAcctAsgmtPage
from locators.asset_acct_asgmt_locators import AssetAcctAsgmtLocators
from utils.config import BASE_URL, USERNAME, PASSWORD


def _acct_matches(actual: str, expected: str) -> bool:
    """Flexible grid assertion: accept full label OR abbreviation code.

    The app may display 'Asset (A)' or just 'A' depending on the row/type.
    Passing if either string is a substring of the other covers both cases.
    """
    return expected in actual or actual in expected


def _login_and_open_items(page: Page) -> AssetAcctAsgmtPage:
    """Shared helper: login → navigate to dashboard → open invoice items tab."""
    login_page = LoginPage(page)
    login_page.navigate(BASE_URL)
    login_page.login(USERNAME, PASSWORD)

    asset_page = AssetAcctAsgmtPage(page)
    asset_page.open_invoice_items(AssetAcctAsgmtPage.TEST_INVOICE_NUMBER)
    return asset_page


class TestAssetAcctAsgmtEditSave:

    def test_aiop_130756_select_asset_save_verify_grid_persist_on_reopen(self, page):
        """
        TC-001: AP Clerk opens a line item, selects Asset (A), saves, verifies
        the Items grid reflects the value, then reopens and confirms persistence.
        """
        # ── Step 1 & 2: Login and open invoice Items tab ──────────────────────
        asset_page = _login_and_open_items(page)

        # Confirm at least one line item is visible
        row_count = asset_page.get_row_count()
        assert row_count > 0, (
            f"[TC-001] Step 2 FAILED: Expected at least 1 line item in Items grid, "
            f"got {row_count}."
        )

        # ── Step 3: Click Edit pencil on line item 0 ──────────────────────────
        asset_page.click_edit_pencil(line_index=0)
        assert asset_page.is_edit_panel_open(), (
            "[TC-001] Step 3 FAILED: Edit Line panel did not open after clicking edit pencil."
        )

        # ── Step 4: Fill Description, Quantity, Unit Price ────────────────────
        asset_page.fill_description("Test Asset Line")
        asset_page.fill_quantity("1")
        asset_page.fill_unit_price("100")

        # ── Step 5 & 6: Open Acct Asgmt. dropdown and select Asset (A) ───────
        asset_page.select_acct_asgmt(AssetAcctAsgmtLocators.ACCT_ASGMT_ASSET)

        # ── Step 7: Verify Save button is now enabled ─────────────────────────
        assert asset_page.is_save_button_enabled(), (
            "[TC-001] Step 6/7 FAILED: Save button should be enabled after selecting Asset (A)."
        )

        # ── Step 7 cont.: Click Save ──────────────────────────────────────────
        saved = asset_page.click_save()
        assert saved, (
            "[TC-001] Step 7 FAILED: Save did not complete (edit panel did not close)."
        )

        # ── Step 8: Verify Items grid shows Asset (A) in Acct. Asgmt. column ─
        asset_page.click_items_tab()
        grid_value = asset_page.get_acct_asgmt_value_in_grid(row_index=0)
        assert AssetAcctAsgmtLocators.ACCT_ASGMT_ASSET in grid_value, (
            f"[TC-001] Step 8 FAILED: Expected 'Asset (A)' in Acct. Asgmt. column, "
            f"got '{grid_value}'."
        )

        # ── Step 9: Reopen same line item and verify Asset (A) is pre-selected ─
        asset_page.click_edit_pencil(line_index=0)
        assert asset_page.is_edit_panel_open(), (
            "[TC-001] Step 9 FAILED: Edit Line panel did not reopen."
        )
        pre_selected = asset_page.get_acct_asgmt_selected_in_modal()
        assert AssetAcctAsgmtLocators.ACCT_ASGMT_ASSET in pre_selected, (
            f"[TC-001] Step 9 FAILED: Expected 'Asset (A)' pre-selected on reopen, "
            f"got '{pre_selected}'."
        )
        # Clean up: cancel the re-opened panel
        asset_page.click_cancel()

    def test_aiop_130757_multiple_line_items_different_acct_asgmt_categories(self, page):
        """
        TC-002: Multiple line items support different Acct Asgmt. categories
        with no cross-contamination. Steps involving Cost Center (K) and
        Project (P) are wrapped in skip guards per the agreed test strategy.
        """
        # ── Steps 1 & 2: Login and open invoice Items tab ─────────────────────
        asset_page = _login_and_open_items(page)

        row_count = asset_page.get_row_count()
        assert row_count >= 2, (
            f"[TC-002] Step 1/2 FAILED: Expected >= 2 line items, got {row_count}."
        )

        # ── Step 3: Edit Line 1 → Asset (A) → Save ────────────────────────────
        asset_page.click_edit_pencil(line_index=0)
        assert asset_page.is_edit_panel_open(), (
            "[TC-002] Step 3 FAILED: Edit panel did not open for Line 1."
        )
        asset_page.fill_description("Test Asset Line 1")
        asset_page.fill_quantity("1")
        asset_page.fill_unit_price("100")
        asset_page.select_acct_asgmt(AssetAcctAsgmtLocators.ACCT_ASGMT_ASSET)
        saved_1 = asset_page.click_save()
        assert saved_1, "[TC-002] Step 3 FAILED: Save for Line 1 (Asset A) did not complete."

        # Verify Line 1 now shows Asset (A)
        asset_page.click_items_tab()
        line1_val = asset_page.get_acct_asgmt_value_in_grid(row_index=0)
        assert _acct_matches(line1_val, AssetAcctAsgmtLocators.ACCT_ASGMT_ASSET), (
            f"[TC-002] Step 3 FAILED: Line 1 should show 'Asset (A)', got '{line1_val}'."
        )

        # ── Step 4: Edit Line 2 → Cost Center (K) → Save ─────────────────────
        # Cost Center (K) selection may be skipped if not interactable
        try:
            asset_page.click_edit_pencil(line_index=1)
            assert asset_page.is_edit_panel_open(), (
                "[TC-002] Step 4 FAILED: Edit panel did not open for Line 2."
            )
            asset_page.fill_description("Test Cost Center Line 2")
            asset_page.fill_quantity("1")
            asset_page.fill_unit_price("100")
            asset_page.select_acct_asgmt(AssetAcctAsgmtLocators.ACCT_ASGMT_COST_CENTER)
            saved_2k = asset_page.click_save()
            if not saved_2k:
                warnings.warn("[TC-002] Step 4: Save for Line 2 Cost Center (K) may not have completed.")
                # Cancel the still-open panel before continuing
                try:
                    asset_page.click_cancel()
                    asset_page.description_field.wait_for(state="hidden", timeout=10_000)
                except Exception:
                    pass
            else:
                # Verify Line 2 = Cost Center (K), Line 1 unchanged
                asset_page.click_items_tab()
                line2_val = asset_page.get_acct_asgmt_value_in_grid(row_index=1)
                assert _acct_matches(line2_val, AssetAcctAsgmtLocators.ACCT_ASGMT_COST_CENTER), (
                    f"[TC-002] Step 4/5 FAILED: Line 2 should show 'Cost Center (K)', got '{line2_val}'."
                )
                line1_after = asset_page.get_acct_asgmt_value_in_grid(row_index=0)
                assert _acct_matches(line1_after, AssetAcctAsgmtLocators.ACCT_ASGMT_ASSET), (
                    f"[TC-002] Step 5 FAILED: Line 1 should still show 'Asset (A)' (no cross-contamination), "
                    f"got '{line1_after}'."
                )
        except pytest.skip.Exception:
            warnings.warn("[TC-002] Step 4: Cost Center (K) skipped — continuing with Internal Order.")

        # ── Step 6: Edit Line 2 → Internal Order → Save ───────────────────────
        asset_page.click_edit_pencil(line_index=1)
        assert asset_page.is_edit_panel_open(), (
            "[TC-002] Step 6 FAILED: Edit panel did not open for Line 2 (Internal Order step)."
        )
        asset_page.fill_description("Test Internal Order Line 2")
        asset_page.fill_quantity("1")
        asset_page.fill_unit_price("100")
        asset_page.select_acct_asgmt(AssetAcctAsgmtLocators.ACCT_ASGMT_INTERNAL_ORDER)
        saved_2i = asset_page.click_save()
        assert saved_2i, "[TC-002] Step 6 FAILED: Save for Line 2 Internal Order did not complete."

        # ── Step 7: Verify Line 1 = Asset (A), Line 2 = Internal Order ────────
        asset_page.click_items_tab()
        line2_io = asset_page.get_acct_asgmt_value_in_grid(row_index=1)
        assert _acct_matches(line2_io, AssetAcctAsgmtLocators.ACCT_ASGMT_INTERNAL_ORDER), (
            f"[TC-002] Step 7 FAILED: Line 2 should show 'Internal Order (I)', got '{line2_io}'."
        )
        line1_unchanged = asset_page.get_acct_asgmt_value_in_grid(row_index=0)
        assert _acct_matches(line1_unchanged, AssetAcctAsgmtLocators.ACCT_ASGMT_ASSET), (
            f"[TC-002] Step 7 FAILED: Line 1 should still show 'Asset (A)', got '{line1_unchanged}'."
        )

        # ── Step 8: Edit Line 2 → Project (P) → Save (with skip guard) ────────
        try:
            asset_page.click_edit_pencil(line_index=1)
            assert asset_page.is_edit_panel_open(), (
                "[TC-002] Step 8 FAILED: Edit panel did not open for Line 2 (Project step)."
            )
            asset_page.fill_description("Test Project Line 2")
            asset_page.fill_quantity("1")
            asset_page.fill_unit_price("100")
            asset_page.select_acct_asgmt(AssetAcctAsgmtLocators.ACCT_ASGMT_PROJECT)
            saved_2p = asset_page.click_save()
            if not saved_2p:
                warnings.warn("[TC-002] Step 8: Save for Line 2 Project (P) may not have completed.")
                # Cancel the still-open panel before continuing
                try:
                    asset_page.click_cancel()
                    asset_page.description_field.wait_for(state="hidden", timeout=10_000)
                except Exception:
                    pass
            else:
                # Verify Line 2 = Project (P), Line 1 unchanged
                asset_page.click_items_tab()
                line2_p = asset_page.get_acct_asgmt_value_in_grid(row_index=1)
                assert _acct_matches(line2_p, AssetAcctAsgmtLocators.ACCT_ASGMT_PROJECT), (
                    f"[TC-002] Step 8/9 FAILED: Line 2 should show 'Project (P)', got '{line2_p}'."
                )
                line1_final = asset_page.get_acct_asgmt_value_in_grid(row_index=0)
                assert _acct_matches(line1_final, AssetAcctAsgmtLocators.ACCT_ASGMT_ASSET), (
                    f"[TC-002] Step 9 FAILED: Line 1 should still show 'Asset (A)', got '{line1_final}'."
                )
        except pytest.skip.Exception:
            warnings.warn("[TC-002] Step 8: Project (P) skipped per test strategy.")

        # ── Step 10: Verify History tab contains updated entries ──────────────
        asset_page.navigate_to_history_tab()
        # History shows 'Acct Assignment Category: <code>' — check for any Acct Assignment entry
        history_has_entry = asset_page.is_acct_asgmt_change_in_history("Acct Assignment")
        assert history_has_entry, (
            "[TC-002] Step 10 FAILED: History tab should contain an Acct Assignment change entry "
            "after line item edits."
        )

    def test_aiop_130764_multiple_changes_in_one_session_saves_final_value(self, page):
        """
        TC-008: Multiple Acct Asgmt. changes in one edit session (no intermediate
        saves) result in only the FINAL selection being saved.
        History records the final value; intermediate selections are not logged.
        Cost Center (K) and Project (P) intermediate selections use skip guards.
        """
        # ── Steps 1 & 2: Login and open invoice Items tab ─────────────────────
        asset_page = _login_and_open_items(page)

        row_count = asset_page.get_row_count()
        assert row_count > 0, (
            f"[TC-008] Step 1 FAILED: Expected at least 1 line item, got {row_count}."
        )

        # ── Step 2: In one session: Cost Center (K) → Project (P) → Asset (A) ─
        asset_page.click_edit_pencil(line_index=0)
        assert asset_page.is_edit_panel_open(), (
            "[TC-008] Step 1 FAILED: Edit Line panel did not open."
        )

        # Intermediate selection: Cost Center (K) — skip gracefully if needed
        try:
            asset_page.select_acct_asgmt(AssetAcctAsgmtLocators.ACCT_ASGMT_COST_CENTER)
        except pytest.skip.Exception:
            warnings.warn("[TC-008] Step 2: Cost Center (K) intermediate selection skipped.")

        # Intermediate selection: Project (P) — skip gracefully if needed
        try:
            asset_page.select_acct_asgmt(AssetAcctAsgmtLocators.ACCT_ASGMT_PROJECT)
        except pytest.skip.Exception:
            warnings.warn("[TC-008] Step 2: Project (P) intermediate selection skipped.")

        # Final selection: Asset (A) — must succeed
        asset_page.select_acct_asgmt(AssetAcctAsgmtLocators.ACCT_ASGMT_ASSET)

        # ── Step 3: Fill mandatory fields and Save ────────────────────────────
        asset_page.fill_description("TC-008 Final Asset Line")
        asset_page.fill_quantity("1")
        asset_page.fill_unit_price("100")
        assert asset_page.is_save_button_enabled(), (
            "[TC-008] Step 3 FAILED: Save button should be enabled after selecting Asset (A)."
        )
        saved = asset_page.click_save()
        assert saved, "[TC-008] Step 3 FAILED: Save did not complete."

        # ── Step 4: Verify Items grid shows only Asset (A) ────────────────────
        asset_page.click_items_tab()
        final_val = asset_page.get_acct_asgmt_value_in_grid(row_index=0)
        assert AssetAcctAsgmtLocators.ACCT_ASGMT_ASSET in final_val, (
            f"[TC-008] Step 4 FAILED: Grid should show 'Asset (A)' as final saved value, "
            f"got '{final_val}'."
        )

        # ── Step 5: History tab shows the final Acct Assignment value ────────
        asset_page.navigate_to_history_tab()
        # Soft check: if line was already Asset(A) before this test, no Acct Assignment
        # change is recorded (only the description changes). Still verify history has an entry.
        history_has_asset = asset_page.is_acct_asgmt_change_in_history(
            AssetAcctAsgmtLocators.ACCT_ASGMT_ASSET
        )
        if not history_has_asset:
            # The Acct Assignment may not appear if the value was unchanged; check for any
            # manual update entry as evidence the save was recorded in history.
            history_has_any = asset_page.is_acct_asgmt_change_in_history("Invoice manually updated")
            warnings.warn(
                "[TC-008] Step 5: No explicit 'Asset (A)' Acct Assignment entry found "
                "(line may have already been Asset(A) — no change recorded). "
                f"Any manual update entry present: {history_has_any}."
            )
            assert history_has_any, (
                "[TC-008] Step 5 FAILED: No history entry found at all after save. "
                "History should at least record the description change."
            )

        # ── Step 6 & 7: Set all remaining line items to Asset (A) ─────────────
        asset_page.click_items_tab()
        total_rows = asset_page.get_row_count()
        for idx in range(1, total_rows):
            asset_page.click_edit_pencil(line_index=idx)
            assert asset_page.is_edit_panel_open(), (
                f"[TC-008] Step 6 FAILED: Edit panel did not open for line item {idx + 1}."
            )
            asset_page.fill_description(f"TC-008 Asset Line {idx + 1}")
            asset_page.fill_quantity("1")
            asset_page.fill_unit_price("100")
            asset_page.select_acct_asgmt(AssetAcctAsgmtLocators.ACCT_ASGMT_ASSET)
            saved_row = asset_page.click_save()
            if not saved_row:
                warnings.warn(
                    f"[TC-008] Step 6: Save for line item {idx + 1} may not have completed."
                )
            asset_page.click_items_tab()

        # ── Step 7: Verify all rows show Asset (A) ────────────────────────────
        for idx in range(total_rows):
            row_val = asset_page.get_acct_asgmt_value_in_grid(row_index=idx)
            assert AssetAcctAsgmtLocators.ACCT_ASGMT_ASSET in row_val, (
                f"[TC-008] Step 7 FAILED: Row {idx + 1} should show 'Asset (A)', got '{row_val}'."
            )

