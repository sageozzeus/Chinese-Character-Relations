# -*- coding: utf-8 -*-
"""GUI settings dialog — replaces Anki's raw JSON config editor."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from aqt import mw
from aqt.qt import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    Qt,
    QVBoxLayout,
    QWidget,
)
from aqt.utils import askUser, showInfo, tooltip

from . import indexer

ADDON_PACKAGE = __name__.split(".")[0]

DEFAULT_CONFIG: dict[str, Any] = {
    "decks": [],
    "fields": {
        "word": "Word",
        "pinyin": "Pinyin",
        "meaning": "Meaning",
    },
    "max_per_char": 8,
    "include_suspended": True,
    "candidate_min_length": 2,
    "show_on_answer_only": True,
}


def _load_config() -> dict[str, Any]:
    conf = mw.addonManager.getConfig(ADDON_PACKAGE)
    if not conf:
        return deepcopy(DEFAULT_CONFIG)
    # Ensure nested keys exist
    merged = deepcopy(DEFAULT_CONFIG)
    merged.update({k: v for k, v in conf.items() if k != "fields"})
    fields = conf.get("fields") or {}
    merged["fields"] = {**DEFAULT_CONFIG["fields"], **fields}
    return merged


def _save_config(conf: dict[str, Any]) -> None:
    mw.addonManager.writeConfig(ADDON_PACKAGE, conf)


def _deck_names() -> list[str]:
    if mw.col is None:
        return []
    try:
        # Anki 23+: list of DeckNameId
        return sorted(d.name for d in mw.col.decks.all_names_and_ids())
    except Exception:
        try:
            return sorted(mw.col.decks.allNames())
        except Exception:
            return []


def _field_names() -> list[str]:
    """Unique field names across all note types, sorted."""
    if mw.col is None:
        return []
    names: set[str] = set()
    try:
        for model in mw.col.models.all():
            for fld in model.get("flds", []):
                name = fld.get("name")
                if name:
                    names.add(name)
    except Exception:
        pass
    return sorted(names, key=lambda s: s.lower())


class ConfigDialog(QDialog):
    """Click-friendly settings for Chinese Character Relations."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent or mw)
        self.setWindowTitle("Chinese Character Relations")
        self.setMinimumWidth(440)
        self.setMinimumHeight(520)
        self._conf = _load_config()
        self._build_ui()
        self._load_into_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(14)

        intro = QLabel(
            "Choose which decks and fields to use for related Chinese words "
            "shown on the answer side during review."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("opacity: 0.85; margin-bottom: 4px;")
        root.addWidget(intro)

        root.addWidget(self._build_decks_group())
        root.addWidget(self._build_fields_group())
        root.addWidget(self._build_display_group())

        # Actions row: restore + standard buttons
        actions = QHBoxLayout()
        self.restore_btn = QPushButton("Restore defaults")
        self.restore_btn.clicked.connect(self._restore_defaults)
        actions.addWidget(self.restore_btn)
        actions.addStretch(1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        actions.addWidget(buttons)
        root.addLayout(actions)

    def _build_decks_group(self) -> QGroupBox:
        box = QGroupBox("Decks to scan")
        layout = QVBoxLayout(box)

        self.all_decks_cb = QCheckBox("All decks")
        self.all_decks_cb.setToolTip(
            "When checked, every deck in the collection is indexed."
        )
        self.all_decks_cb.toggled.connect(self._on_all_decks_toggled)
        layout.addWidget(self.all_decks_cb)

        hint = QLabel("Or select specific decks:")
        hint.setStyleSheet("opacity: 0.7; font-size: 11px;")
        layout.addWidget(hint)

        self.deck_list = QListWidget()
        self.deck_list.setMinimumHeight(140)
        self.deck_list.setToolTip("Check the decks that should be indexed.")
        layout.addWidget(self.deck_list)

        select_row = QHBoxLayout()
        select_all = QPushButton("Select all")
        select_none = QPushButton("Select none")
        select_all.clicked.connect(self._select_all_decks)
        select_none.clicked.connect(self._select_no_decks)
        select_row.addWidget(select_all)
        select_row.addWidget(select_none)
        select_row.addStretch(1)
        layout.addLayout(select_row)

        return box

    def _build_fields_group(self) -> QGroupBox:
        box = QGroupBox("Note fields")
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        field_names = _field_names()
        common = ["Word", "Hanzi", "Expression", "Chinese", "Front", "Pinyin",
                  "Reading", "Meaning", "Definition", "English", "Back"]
        # Prefer collection fields, then common suggestions
        suggestions = list(dict.fromkeys(field_names + common))

        self.word_combo = self._make_field_combo(suggestions)
        self.pinyin_combo = self._make_field_combo(suggestions)
        self.meaning_combo = self._make_field_combo(suggestions)

        form.addRow("Word / Hanzi", self.word_combo)
        form.addRow("Pinyin", self.pinyin_combo)
        form.addRow("Meaning", self.meaning_combo)

        tip = QLabel(
            "Pick from your note types, or type a custom field name."
        )
        tip.setWordWrap(True)
        tip.setStyleSheet("opacity: 0.7; font-size: 11px;")
        form.addRow(tip)

        return box

    def _build_display_group(self) -> QGroupBox:
        box = QGroupBox("Display options")
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 50)
        self.max_spin.setToolTip("Maximum related words shown under each character.")
        form.addRow("Max per character", self.max_spin)

        self.min_len_spin = QSpinBox()
        self.min_len_spin.setRange(1, 10)
        self.min_len_spin.setToolTip(
            "Minimum number of Chinese characters in a related word. "
            "Use 2 to prefer compounds over single characters."
        )
        form.addRow("Min word length", self.min_len_spin)

        self.include_suspended_cb = QCheckBox("Include suspended notes")
        self.include_suspended_cb.setToolTip(
            "Show related notes even when all of their cards are suspended."
        )
        form.addRow(self.include_suspended_cb)

        self.answer_only_cb = QCheckBox("Show on answer side only")
        self.answer_only_cb.setToolTip(
            "Keep the question side clean; related words appear after you flip."
        )
        self.answer_only_cb.setEnabled(False)  # MVP: always answer-only
        form.addRow(self.answer_only_cb)

        return box

    @staticmethod
    def _make_field_combo(suggestions: list[str]) -> QComboBox:
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.addItems(suggestions)
        combo.setMinimumWidth(200)
        return combo

    def _load_into_ui(self) -> None:
        conf = self._conf
        decks = list(conf.get("decks") or [])
        all_decks = len(decks) == 0

        self.deck_list.clear()
        selected = set(decks)
        for name in _deck_names():
            item = QListWidgetItem(name)
            item.setFlags(
                item.flags()
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsEnabled
            )
            checked = (not all_decks) and (name in selected)
            item.setCheckState(
                Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
            )
            self.deck_list.addItem(item)

        self.all_decks_cb.blockSignals(True)
        self.all_decks_cb.setChecked(all_decks)
        self.all_decks_cb.blockSignals(False)
        self._on_all_decks_toggled(all_decks)

        fields = conf.get("fields") or {}
        self._set_combo(self.word_combo, fields.get("word", "Word"))
        self._set_combo(self.pinyin_combo, fields.get("pinyin", "Pinyin"))
        self._set_combo(self.meaning_combo, fields.get("meaning", "Meaning"))

        self.max_spin.setValue(int(conf.get("max_per_char", 8)))
        self.min_len_spin.setValue(int(conf.get("candidate_min_length", 2)))
        self.include_suspended_cb.setChecked(bool(conf.get("include_suspended", True)))
        self.answer_only_cb.setChecked(bool(conf.get("show_on_answer_only", True)))

    @staticmethod
    def _set_combo(combo: QComboBox, value: str) -> None:
        idx = combo.findText(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        else:
            combo.setEditText(value)

    def _on_all_decks_toggled(self, checked: bool) -> None:
        self.deck_list.setEnabled(not checked)

    def _select_all_decks(self) -> None:
        self.all_decks_cb.setChecked(False)
        for i in range(self.deck_list.count()):
            self.deck_list.item(i).setCheckState(Qt.CheckState.Checked)

    def _select_no_decks(self) -> None:
        self.all_decks_cb.setChecked(False)
        for i in range(self.deck_list.count()):
            self.deck_list.item(i).setCheckState(Qt.CheckState.Unchecked)

    def _restore_defaults(self) -> None:
        if not askUser("Reset all settings to defaults?"):
            return
        self._conf = deepcopy(DEFAULT_CONFIG)
        self._load_into_ui()

    def _collect(self) -> Optional[dict[str, Any]]:
        word = self.word_combo.currentText().strip()
        if not word:
            showInfo("Please set a Word / Hanzi field name.")
            return None

        if self.all_decks_cb.isChecked():
            decks: list[str] = []
        else:
            decks = []
            for i in range(self.deck_list.count()):
                item = self.deck_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    decks.append(item.text())
            if not decks and self.deck_list.count() > 0:
                showInfo(
                    "No decks selected. Check “All decks”, or select at least one deck."
                )
                return None

        return {
            "decks": decks,
            "fields": {
                "word": word,
                "pinyin": self.pinyin_combo.currentText().strip() or "Pinyin",
                "meaning": self.meaning_combo.currentText().strip() or "Meaning",
            },
            "max_per_char": self.max_spin.value(),
            "include_suspended": self.include_suspended_cb.isChecked(),
            "candidate_min_length": self.min_len_spin.value(),
            "show_on_answer_only": True,  # MVP locked
        }

    def _on_save(self) -> None:
        conf = self._collect()
        if conf is None:
            return
        _save_config(conf)
        self.accept()

        rebuild = askUser(
            "Settings saved.\n\nRebuild the character index now?\n"
            "(Recommended after changing decks or fields.)"
        )
        if rebuild:
            if mw.col is None:
                tooltip("Open a profile first, then rebuild from the Tools menu.")
            else:
                indexer.rebuild_index(show_progress=True, notify=True)
        else:
            tooltip("Settings saved. Rebuild later via Tools → Character Relations.")


def open_config() -> bool:
    """
    Entry point for Tools menu and Anki's Config button.

    Returning True (or None) prevents the raw JSON editor from opening.
    """
    if mw.col is None:
        showInfo("Open a profile before changing settings.")
        return True
    dlg = ConfigDialog(mw)
    dlg.exec()
    return True
