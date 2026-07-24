# -*- coding: utf-8 -*-
"""
Chinese Character Relations

Shows deck words that share CJK characters with the current card
on the answer (back) side during review.
"""

from __future__ import annotations

# Outside Anki (unit tests), aqt is unavailable — skip hook registration.
try:
    from aqt import gui_hooks, mw
    from aqt.qt import QAction, QMenu
    from aqt.utils import tooltip
except ImportError:  # pragma: no cover
    pass
else:
    from . import browser, config_dialog, indexer, reviewer

    _menu_installed = False
    ADDON = __name__

    def _on_profile_open() -> None:
        indexer.rebuild_index(show_progress=True, notify=False)

    def _on_sync_finish() -> None:
        indexer.rebuild_index(show_progress=True, notify=True)

    def _on_rebuild_menu() -> None:
        if mw.col is None:
            tooltip("Open a profile first.")
            return
        indexer.rebuild_index(show_progress=True, notify=True)

    def _on_settings_menu() -> None:
        config_dialog.open_config()

    def _setup_menu() -> None:
        global _menu_installed
        if _menu_installed or mw is None:
            return
        try:
            menu = QMenu("Character Relations", mw)
            settings_action = QAction("Settings…", mw)
            settings_action.triggered.connect(_on_settings_menu)
            menu.addAction(settings_action)
            rebuild_action = QAction("Rebuild Index", mw)
            rebuild_action.triggered.connect(_on_rebuild_menu)
            menu.addAction(rebuild_action)
            mw.form.menuTools.addMenu(menu)
            _menu_installed = True
        except Exception:
            pass

    def _register_hooks() -> None:
        gui_hooks.main_window_did_init.append(_setup_menu)
        gui_hooks.profile_did_open.append(_on_profile_open)
        gui_hooks.sync_did_finish.append(_on_sync_finish)
        gui_hooks.card_will_show.append(reviewer.on_card_will_show)
        gui_hooks.reviewer_did_show_answer.append(reviewer.on_show_answer)
        gui_hooks.reviewer_did_show_question.append(reviewer.on_show_question)
        gui_hooks.webview_did_receive_js_message.append(browser.on_webview_js_message)
        mw.addonManager.setConfigAction(ADDON, config_dialog.open_config)

    _register_hooks()
    _setup_menu()
