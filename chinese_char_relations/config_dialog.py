# -*- coding: utf-8 -*-
"""GUI settings dialog — General + Appearance tabs."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from aqt import mw
from aqt.qt import (
    QCheckBox,
    QColor,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    Qt,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from aqt.utils import askUser, showInfo, tooltip

from . import indexer
from .defaults import DEFAULT_CONFIG, DEFAULT_UI, merge_config

ADDON_PACKAGE = __name__.split(".")[0]


def _load_config() -> dict[str, Any]:
    return merge_config(mw.addonManager.getConfig(ADDON_PACKAGE))


def _save_config(conf: dict[str, Any]) -> None:
    mw.addonManager.writeConfig(ADDON_PACKAGE, conf)


def _deck_names() -> list[str]:
    if mw.col is None:
        return []
    try:
        return sorted(d.name for d in mw.col.decks.all_names_and_ids())
    except Exception:
        try:
            return sorted(mw.col.decks.allNames())
        except Exception:
            return []


def _field_names() -> list[str]:
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


class _ColorButton(QPushButton):
    """Small swatch + hex label; opens a color picker on click."""

    def __init__(self, color: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._hex = "#ffffff"
        self.setMinimumWidth(110)
        self.set_color(color)
        self.clicked.connect(self._pick)

    def set_color(self, color: str) -> None:
        c = QColor(color)
        if not c.isValid():
            c = QColor("#ffffff")
        self._hex = c.name()
        self.setText(self._hex)
        self.setStyleSheet(
            f"QPushButton {{ background-color: {self._hex}; color: "
            f"{'#111' if c.lightness() > 140 else '#eee'}; "
            f"border: 1px solid #888; padding: 4px 8px; text-align: left; }}"
        )

    def color(self) -> str:
        return self._hex

    def _pick(self) -> None:
        chosen = QColorDialog.getColor(QColor(self._hex), self, "Pick color")
        if chosen.isValid():
            self.set_color(chosen.name())


def _wrap_scroll(inner: QWidget) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setWidget(inner)
    return scroll


class ConfigDialog(QDialog):
    """Settings dialog with General and Appearance tabs."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent or mw)
        self.setWindowTitle("Chinese Character Relations")
        self.setMinimumWidth(500)
        self.setMinimumHeight(560)
        self._conf = _load_config()
        self._build_ui()
        self._load_into_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(10)

        self.tabs = QTabWidget()
        self.tabs.addTab(_wrap_scroll(self._build_general_tab()), "General")
        self.tabs.addTab(_wrap_scroll(self._build_appearance_tab()), "Appearance")
        root.addWidget(self.tabs)

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

    def _build_general_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)

        intro = QLabel(
            "Choose which decks and fields to use for related Chinese words "
            "shown on the answer side during review."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addWidget(self._build_decks_group())
        layout.addWidget(self._build_fields_group())
        layout.addWidget(self._build_display_group())
        layout.addStretch(1)
        return page

    def _build_appearance_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)

        intro = QLabel(
            "Customize how the Related panel looks on the card. "
            "Changes apply on the next answer flip (no rebuild needed). "
            "Use max width like 100%, 36em, or 650px to match your card template."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        layout.addWidget(self._build_layout_group())
        layout.addWidget(self._build_type_group())
        layout.addWidget(self._build_colors_group())
        layout.addWidget(self._build_custom_css_group())
        layout.addStretch(1)
        return page

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
        common = [
            "Word", "Hanzi", "Expression", "Chinese", "Front", "Pinyin",
            "Reading", "Meaning", "Definition", "English", "Back",
        ]
        suggestions = list(dict.fromkeys(field_names + common))

        self.word_combo = self._make_field_combo(suggestions)
        self.pinyin_combo = self._make_field_combo(suggestions)
        self.meaning_combo = self._make_field_combo(suggestions)

        form.addRow("Word / Hanzi", self.word_combo)
        form.addRow("Pinyin", self.pinyin_combo)
        form.addRow("Meaning", self.meaning_combo)
        tip = QLabel("Pick from your note types, or type a custom field name.")
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
        form.addRow("Max per character", self.max_spin)

        self.min_len_spin = QSpinBox()
        self.min_len_spin.setRange(1, 10)
        form.addRow("Min word length", self.min_len_spin)

        self.include_suspended_cb = QCheckBox("Include suspended notes")
        form.addRow(self.include_suspended_cb)

        self.answer_only_cb = QCheckBox("Show on answer side only")
        self.answer_only_cb.setEnabled(False)
        form.addRow(self.answer_only_cb)
        return box

    def _build_layout_group(self) -> QGroupBox:
        box = QGroupBox("Layout")
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.max_width_edit = QLineEdit()
        self.max_width_edit.setPlaceholderText("100%  ·  36em  ·  650px")
        self.max_width_edit.setToolTip(
            "CSS max-width for the Related panel. Use 100% to fill the card container."
        )
        form.addRow("Max width", self.max_width_edit)

        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(0, 40)
        self.radius_spin.setSuffix(" px")
        form.addRow("Corner radius", self.radius_spin)

        self.gap_spin = QDoubleSpinBox()
        self.gap_spin.setRange(0.2, 2.0)
        self.gap_spin.setSingleStep(0.05)
        self.gap_spin.setDecimals(2)
        self.gap_spin.setSuffix(" em")
        form.addRow("Gap between cards", self.gap_spin)

        self.shadow_cb = QCheckBox("Show drop shadow")
        form.addRow(self.shadow_cb)
        return box

    def _build_type_group(self) -> QGroupBox:
        box = QGroupBox("Type size")
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.char_size_spin = self._em_spin()
        self.word_size_spin = self._em_spin()
        self.pinyin_size_spin = self._em_spin()
        form.addRow("Character", self.char_size_spin)
        form.addRow("Related word", self.word_size_spin)
        form.addRow("Pinyin", self.pinyin_size_spin)
        return box

    def _build_colors_group(self) -> QGroupBox:
        box = QGroupBox("Colors")
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.bg_light_btn = _ColorButton("#ffffff")
        self.bg_dark_btn = _ColorButton("#303238")
        self.border_light_btn = _ColorButton("#b0b0b0")
        self.border_dark_btn = _ColorButton("#5a5a5a")
        self.mature_light_btn = _ColorButton("#2e7d32")
        self.mature_dark_btn = _ColorButton("#81c784")
        self.suspended_light_btn = _ColorButton("#c62828")
        self.suspended_dark_btn = _ColorButton("#ef9a9a")

        form.addRow("Background (light)", self.bg_light_btn)
        form.addRow("Background (dark)", self.bg_dark_btn)
        form.addRow("Border (light)", self.border_light_btn)
        form.addRow("Border (dark)", self.border_dark_btn)
        form.addRow("Mature (light)", self.mature_light_btn)
        form.addRow("Mature (dark)", self.mature_dark_btn)
        form.addRow("Suspended (light)", self.suspended_light_btn)
        form.addRow("Suspended (dark)", self.suspended_dark_btn)
        return box

    def _build_custom_css_group(self) -> QGroupBox:
        box = QGroupBox("Custom CSS (advanced)")
        layout = QVBoxLayout(box)
        tip = QLabel(
            "Optional extra CSS appended after the built-in panel styles. "
            "Target .char-relations, .char-relations-group, etc."
        )
        tip.setWordWrap(True)
        tip.setStyleSheet("opacity: 0.7; font-size: 11px;")
        layout.addWidget(tip)
        self.custom_css_edit = QPlainTextEdit()
        self.custom_css_edit.setPlaceholderText(
            ".char-relations-group {\n  /* your rules */\n}"
        )
        self.custom_css_edit.setMinimumHeight(100)
        layout.addWidget(self.custom_css_edit)
        return box

    @staticmethod
    def _em_spin() -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(0.4, 2.5)
        spin.setSingleStep(0.01)
        spin.setDecimals(2)
        spin.setSuffix(" em")
        return spin

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

        ui = conf.get("ui") or deepcopy(DEFAULT_UI)
        self.max_width_edit.setText(str(ui.get("max_width", "100%")))
        self.radius_spin.setValue(int(ui.get("border_radius_px", 12)))
        self.gap_spin.setValue(float(ui.get("gap_em", 0.65)))
        self.shadow_cb.setChecked(bool(ui.get("show_shadow", True)))
        self.char_size_spin.setValue(float(ui.get("char_size_em", 1.05)))
        self.word_size_spin.setValue(float(ui.get("word_size_em", 0.82)))
        self.pinyin_size_spin.setValue(float(ui.get("pinyin_size_em", 0.62)))
        self.bg_light_btn.set_color(str(ui.get("bg_light", "#ffffff")))
        self.bg_dark_btn.set_color(str(ui.get("bg_dark", "#303238")))
        self.border_light_btn.set_color(str(ui.get("border_light", "#b0b0b0")))
        self.border_dark_btn.set_color(str(ui.get("border_dark", "#5a5a5a")))
        self.mature_light_btn.set_color(str(ui.get("mature_light", "#2e7d32")))
        self.mature_dark_btn.set_color(str(ui.get("mature_dark", "#81c784")))
        self.suspended_light_btn.set_color(str(ui.get("suspended_light", "#c62828")))
        self.suspended_dark_btn.set_color(str(ui.get("suspended_dark", "#ef9a9a")))
        self.custom_css_edit.setPlainText(str(ui.get("custom_css") or ""))

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
        if not askUser("Reset all settings (General + Appearance) to defaults?"):
            return
        self._conf = deepcopy(DEFAULT_CONFIG)
        self._load_into_ui()

    def _collect_ui(self) -> dict[str, Any]:
        max_width = self.max_width_edit.text().strip() or "100%"
        return {
            "max_width": max_width,
            "border_radius_px": self.radius_spin.value(),
            "gap_em": round(self.gap_spin.value(), 2),
            "char_size_em": round(self.char_size_spin.value(), 2),
            "word_size_em": round(self.word_size_spin.value(), 2),
            "pinyin_size_em": round(self.pinyin_size_spin.value(), 2),
            "bg_light": self.bg_light_btn.color(),
            "bg_dark": self.bg_dark_btn.color(),
            "border_light": self.border_light_btn.color(),
            "border_dark": self.border_dark_btn.color(),
            "mature_light": self.mature_light_btn.color(),
            "mature_dark": self.mature_dark_btn.color(),
            "suspended_light": self.suspended_light_btn.color(),
            "suspended_dark": self.suspended_dark_btn.color(),
            "show_shadow": self.shadow_cb.isChecked(),
            "custom_css": self.custom_css_edit.toPlainText(),
        }

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
            "show_on_answer_only": True,
            "ui": self._collect_ui(),
        }

    def _on_save(self) -> None:
        conf = self._collect()
        if conf is None:
            return
        prev = self._conf
        _save_config(conf)
        self.accept()

        needs_rebuild = (
            conf.get("decks") != prev.get("decks")
            or conf.get("fields") != prev.get("fields")
        )

        if needs_rebuild:
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
        else:
            tooltip("Appearance saved. Flip a card to see UI changes.")


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
