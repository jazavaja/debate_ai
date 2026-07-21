# settings/settings_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QFormLayout, QMessageBox, QComboBox,
    QTabWidget, QDoubleSpinBox, QCheckBox, QFileDialog, QAbstractItemView,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from .settings_manager import SettingsManager
from .settings_config import SettingsConfig, LLMProviderConfig
from ui.styles import DARK_THEME
from ui.custom_messagebox import CustomMessageBox


class ProviderEditWidget(QWidget):
    """ویجت ویرایش یک LLM Provider"""

    def __init__(self, provider: LLMProviderConfig = None, parent=None):
        super().__init__(parent)
        self._provider = provider
        self._setup_ui()
        if provider:
            self._load_provider(provider)

    def _setup_ui(self):
        layout = QFormLayout()
        layout.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثلاً: OpenAI GPT-4")
        layout.addRow("نام نمایشی:", self.name_input)

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["openai", "anthropic", "gemini", "custom"])
        layout.addRow("نوع Provider:", self.provider_combo)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("مثلاً: gpt-4o-mini")
        layout.addRow("مدل:", self.model_input)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        layout.addRow("API Key:", self.api_key_input)

        self.base_uri_input = QLineEdit()
        self.base_uri_input.setPlaceholderText("مثلاً: https://api.openai.com/v1")
        layout.addRow("Base URI:", self.base_uri_input)

        self.auth_header_input = QLineEdit()
        self.auth_header_input.setText("Authorization")
        layout.addRow("Auth Header:", self.auth_header_input)

        self.auth_prefix_input = QLineEdit()
        self.auth_prefix_input.setText("Bearer ")
        layout.addRow("Token Prefix:", self.auth_prefix_input)

        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(0.8)
        layout.addRow("Temperature (دما):", self.temperature_spin)

        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 100)
        self.priority_spin.setValue(1)
        layout.addRow("اولویت (1 = بالاترین):", self.priority_spin)

        self.enabled_check = QCheckBox("✓ این Provider فعال باشد")
        self.enabled_check.setStyleSheet(
            "QCheckBox { color: #e94560; font-weight: bold; padding: 6px; "
            "background-color: #1f3162; border-radius: 6px; }"
        )
        self.enabled_check.setChecked(True)
        layout.addRow("وضعیت:", self.enabled_check)

        self.setLayout(layout)

    def _load_provider(self, provider: LLMProviderConfig):
        self.name_input.setText(provider.name)
        idx = self.provider_combo.findText(provider.provider)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)
        self.model_input.setText(provider.model)
        self.api_key_input.setText(provider.api_key)
        self.base_uri_input.setText(provider.base_uri)
        self.auth_header_input.setText(provider.auth_header_name)
        self.auth_prefix_input.setText(provider.auth_token_prefix)
        self.temperature_spin.setValue(provider.temperature)
        self.priority_spin.setValue(provider.priority)
        self.enabled_check.setChecked(provider.enabled)

    def get_provider(self) -> LLMProviderConfig:
        return LLMProviderConfig(
            name=self.name_input.text().strip(),
            provider=self.provider_combo.currentText(),
            model=self.model_input.text().strip(),
            api_key=self.api_key_input.text().strip(),
            base_uri=self.base_uri_input.text().strip(),
            auth_header_name=self.auth_header_input.text().strip(),
            auth_token_prefix=self.auth_prefix_input.text().strip(),
            temperature=self.temperature_spin.value(),
            priority=self.priority_spin.value(),
            enabled=self.enabled_check.isChecked(),
        )

    def is_valid(self) -> tuple[bool, str]:
        name = self.name_input.text().strip()
        if not name:
            return False, "نام Provider خالی است"
        model = self.model_input.text().strip()
        if not model:
            return False, "مدل خالی است"
        base = self.base_uri_input.text().strip()
        if not base:
            return False, "Base URI خالی است"
        return True, ""


class SettingsDialog(QDialog):
    """پنجره تنظیمات اصلی"""

    settings_saved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ تنظیمات برنامه")
        self.setMinimumSize(800, 600)
        self.resize(900, 650)
        self._current_settings = SettingsManager.load_settings()
        self._setup_ui()
        self.setStyleSheet(DARK_THEME)
        self._load_providers_table()

    def _setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        tabs = QTabWidget()

        # ===== تب LLM Providers =====
        providers_tab = QWidget()
        providers_layout = QVBoxLayout()
        providers_layout.setSpacing(10)

        # هدر
        header_label = QLabel("مدیریت LLM Providers")
        header_label.setStyleSheet("font-size: 16px; color: #e94560; font-weight: bold;")
        providers_layout.addWidget(header_label)

        desc_label = QLabel(
            "Providers به ترتیب اولویت تست می‌شوند. "
            "اگر Provider اول fail شود، به بعدی می‌رود."
        )
        desc_label.setStyleSheet("color: #888; font-size: 12px;")
        providers_layout.addWidget(desc_label)

        # جدول Providers
        self.providers_table = QTableWidget()
        self.providers_table.setColumnCount(5)
        self.providers_table.setHorizontalHeaderLabels([
            "نام", "Provider", "مدل", "اولویت", "فعال"
        ])
        self.providers_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.providers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.providers_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.providers_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.providers_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.providers_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.providers_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.providers_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.providers_table.doubleClicked.connect(self._on_edit_provider)
        providers_layout.addWidget(self.providers_table)

        # دکمه‌های مدیریت
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("➕ افزودن Provider")
        add_btn.clicked.connect(self._on_add_provider)
        btn_layout.addWidget(add_btn)

        edit_btn = QPushButton("✏️ ویرایش")
        edit_btn.clicked.connect(self._on_edit_provider)
        btn_layout.addWidget(edit_btn)

        remove_btn = QPushButton("🗑️ حذف")
        remove_btn.setObjectName("stop_btn")
        remove_btn.clicked.connect(self._on_remove_provider)
        btn_layout.addWidget(remove_btn)

        btn_layout.addStretch()

        up_btn = QPushButton("⬆️ اولویت بالاتر")
        up_btn.clicked.connect(self._on_move_up)
        btn_layout.addWidget(up_btn)

        down_btn = QPushButton("⬇️ اولویت پایین‌تر")
        down_btn.clicked.connect(self._on_move_down)
        btn_layout.addWidget(down_btn)

        providers_layout.addLayout(btn_layout)

        # حداکثر تلاش
        retry_layout = QHBoxLayout()
        retry_layout.addWidget(QLabel("حداکثر تعداد تلاش (Provider):"))
        self.max_retries_spin = QSpinBox()
        self.max_retries_spin.setRange(1, 20)
        self.max_retries_spin.setValue(self._current_settings.max_retries)
        self.max_retries_spin.setSuffix(" provider")
        retry_layout.addWidget(self.max_retries_spin)
        retry_layout.addStretch()
        providers_layout.addLayout(retry_layout)

        providers_tab.setLayout(providers_layout)
        tabs.addTab(providers_tab, "🔄 LLM Providers")

        # ===== تب تنظیمات عمومی =====
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        general_layout.setSpacing(10)

        general_header = QLabel("تنظیمات عمومی")
        general_header.setStyleSheet("font-size: 16px; color: #e94560; font-weight: bold;")
        general_layout.addWidget(general_header)

        general_group = QGroupBox("تنظیمات ذخیره‌سازی")
        general_form = QFormLayout()

        self.settings_path_label = QLabel(str(SettingsManager.DEFAULT_SETTINGS_DIR))
        self.settings_path_label.setStyleSheet("color: #aaa;")
        general_form.addRow("مسیر تنظیمات:", self.settings_path_label)

        general_group.setLayout(general_form)
        general_layout.addWidget(general_group)

        general_layout.addStretch()
        general_tab.setLayout(general_layout)
        tabs.addTab(general_tab, "⚙️ عمومی")

        main_layout.addWidget(tabs)

        # ===== دکمه‌های پایین =====
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)

        # لیست تنظیمات ذخیره شده
        load_group = QGroupBox("📂  بازیابی تنظیمات ذخیره شده")
        load_form = QVBoxLayout()
        load_form.setSpacing(8)
        load_form.setContentsMargins(12, 18, 12, 12)

        load_desc = QLabel("از لیست زیر یکی را انتخاب و بارگذاری کنید:")
        load_desc.setStyleSheet("color: #b0b8d0; font-size: 12px;")
        load_form.addWidget(load_desc)

        load_row = QHBoxLayout()
        load_row.setSpacing(8)
        self.saved_settings_combo = QComboBox()
        self.saved_settings_combo.setMinimumHeight(34)
        self._refresh_saved_list()
        load_row.addWidget(self.saved_settings_combo, stretch=1)

        load_btn = QPushButton("📂 بارگذاری")
        load_btn.setMinimumWidth(110)
        load_btn.clicked.connect(self._on_load_named)
        load_row.addWidget(load_btn)

        delete_saved_btn = QPushButton("🗑️ حذف")
        delete_saved_btn.setObjectName("stop_btn")
        delete_saved_btn.setMinimumWidth(90)
        delete_saved_btn.clicked.connect(self._on_delete_named)
        load_row.addWidget(delete_saved_btn)

        load_form.addLayout(load_row)
        load_group.setLayout(load_form)
        bottom_layout.addWidget(load_group)

        # ذخیره با نام
        save_name_group = QGroupBox("💾  ذخیره تنظیمات با نام")
        save_name_form = QVBoxLayout()
        save_name_form.setSpacing(8)
        save_name_form.setContentsMargins(12, 18, 12, 12)

        save_desc = QLabel("یک نام وارد کنید و تنظیمات فعلی را ذخیره کنید:")
        save_desc.setStyleSheet("color: #b0b8d0; font-size: 12px;")
        save_name_form.addWidget(save_desc)

        save_row = QHBoxLayout()
        save_row.setSpacing(8)
        self.save_name_input = QLineEdit()
        self.save_name_input.setPlaceholderText("مثلاً: تنظیمات-OpenRouter")
        self.save_name_input.setMinimumHeight(34)
        save_row.addWidget(self.save_name_input, stretch=1)

        save_named_btn = QPushButton("💾 ذخیره با نام")
        save_named_btn.setObjectName("start_btn")
        save_named_btn.setMinimumWidth(140)
        save_named_btn.clicked.connect(self._on_save_named)
        save_row.addWidget(save_named_btn)

        save_name_form.addLayout(save_row)
        save_name_group.setLayout(save_name_form)
        bottom_layout.addWidget(save_name_group)

        main_layout.addLayout(bottom_layout)

        # ===== دکمه‌های اصلی =====
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        cancel_btn = QPushButton("لغو")
        cancel_btn.clicked.connect(self.reject)
        action_layout.addWidget(cancel_btn)

        save_btn = QPushButton("✅ ذخیره و اعمال")
        save_btn.setObjectName("start_btn")
        save_btn.clicked.connect(self._on_save_and_apply)
        action_layout.addWidget(save_btn)

        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)

    # ------------------------------------------------------------------ #
    # Provider Table
    # ------------------------------------------------------------------ #

    def _load_providers_table(self):
        providers = self._current_settings.llm_providers
        self.providers_table.setRowCount(len(providers))
        for row, p in enumerate(providers):
            self.providers_table.setItem(row, 0, QTableWidgetItem(p.name))
            self.providers_table.setItem(row, 1, QTableWidgetItem(p.provider))
            self.providers_table.setItem(row, 2, QTableWidgetItem(p.model))
            self.providers_table.setItem(row, 3, QTableWidgetItem(str(p.priority)))
            check_item = QTableWidgetItem()
            check_item.setCheckState(Qt.Checked if p.enabled else Qt.Unchecked)
            check_item.setText("✓" if p.enabled else "✗")
            self.providers_table.setItem(row, 4, check_item)

    def _get_selected_row(self) -> int:
        rows = self.providers_table.selectionModel().selectedRows()
        if not rows:
            return -1
        return rows[0].row()

    def _on_add_provider(self):
        dlg = ProviderEditWidget(parent=self)
        dlg.setWindowTitle("افزودن Provider جدید")
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ افزودن Provider جدید")
        dialog.setMinimumWidth(520)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #101123;
                color: #f2f5fb;
            }
            QLabel {
                color: #f2f5fb;
                font-weight: 600;
                padding: 4px;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #18203a;
                border: 1px solid #2b3a66;
                border-radius: 8px;
                padding: 8px;
                color: #f2f5fb;
                min-height: 24px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #e94560;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #18203a;
                color: #f2f5fb;
                selection-background-color: #e94560;
            }
            QPushButton {
                background-color: #1f3162;
                color: #f2f5fb;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: bold;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #3d5a99;
            }
            QPushButton#start_btn {
                background-color: #e94560;
            }
            QPushButton#start_btn:hover {
                background-color: #ff6b6b;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(dlg)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel = QPushButton("لغو")
        cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel)
        ok = QPushButton("➕ افزودن")
        ok.setObjectName("start_btn")
        ok.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok)
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            valid, msg = dlg.is_valid()
            if not valid:
                CustomMessageBox.warning(self, "⚠️ خطا", msg)
                return
            provider = dlg.get_provider()
            self._current_settings.llm_providers.append(provider)
            self._load_providers_table()

    def _on_edit_provider(self):
        row = self._get_selected_row()
        if row < 0:
            CustomMessageBox.information(self, "ℹ️", "ابتدا یک Provider را انتخاب کنید.")
            return

        provider = self._current_settings.llm_providers[row]
        dlg = ProviderEditWidget(provider=provider, parent=self)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"✏️ ویرایش: {provider.name}")
        dialog.setMinimumWidth(520)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #101123;
                color: #f2f5fb;
            }
            QLabel {
                color: #f2f5fb;
                font-weight: 600;
                padding: 4px;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #18203a;
                border: 1px solid #2b3a66;
                border-radius: 8px;
                padding: 8px;
                color: #f2f5fb;
                min-height: 24px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #e94560;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #18203a;
                color: #f2f5fb;
                selection-background-color: #e94560;
            }
            QPushButton {
                background-color: #1f3162;
                color: #f2f5fb;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: bold;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #3d5a99;
            }
            QPushButton#start_btn {
                background-color: #e94560;
            }
            QPushButton#start_btn:hover {
                background-color: #ff6b6b;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(dlg)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel = QPushButton("لغو")
        cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel)
        ok = QPushButton("💾 ذخیره")
        ok.setObjectName("start_btn")
        ok.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok)
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            valid, msg = dlg.is_valid()
            if not valid:
                CustomMessageBox.warning(self, "⚠️ خطا", msg)
                return
            self._current_settings.llm_providers[row] = dlg.get_provider()
            self._load_providers_table()

    def _on_remove_provider(self):
        row = self._get_selected_row()
        if row < 0:
            CustomMessageBox.information(self, "ℹ️", "ابتدا یک Provider را انتخاب کنید.")
            return

        name = self._current_settings.llm_providers[row].name
        reply = CustomMessageBox.question(
            self, "⚠️ حذف Provider",
            f"آیا از حذف \"{name}\" اطمینان دارید؟"
        )
        if reply == QMessageBox.Yes:
            del self._current_settings.llm_providers[row]
            self._load_providers_table()

    def _on_move_up(self):
        row = self._get_selected_row()
        if row <= 0:
            return
        providers = self._current_settings.llm_providers
        providers[row], providers[row - 1] = providers[row - 1], providers[row]
        # بروزرسانی اولویت
        for i, p in enumerate(providers):
            p.priority = i + 1
        self._load_providers_table()
        self.providers_table.selectRow(row - 1)

    def _on_move_down(self):
        row = self._get_selected_row()
        providers = self._current_settings.llm_providers
        if row < 0 or row >= len(providers) - 1:
            return
        providers[row], providers[row + 1] = providers[row + 1], providers[row]
        for i, p in enumerate(providers):
            p.priority = i + 1
        self._load_providers_table()
        self.providers_table.selectRow(row + 1)

    # ------------------------------------------------------------------ #
    # Save / Load named settings
    # ------------------------------------------------------------------ #

    def _refresh_saved_list(self):
        self.saved_settings_combo.clear()
        names = SettingsManager.list_saved_settings()
        self.saved_settings_combo.addItems(names)

    def _on_save_named(self):
        name = self.save_name_input.text().strip()
        if not name:
            CustomMessageBox.warning(self, "⚠️ خطا", "نام تنظیمات را وارد کنید.")
            return

        path = SettingsManager.get_settings_path(name)
        if path.exists():
            reply = CustomMessageBox.question(
                self, "⚠️ بازنویسی",
                f"تنظیمات \"{name}\" از قبل وجود دارد. بازنویسی شود؟"
            )
            if reply != QMessageBox.Yes:
                return

        settings = self._build_current_settings()
        SettingsManager.save_settings(settings, path)
        self._refresh_saved_list()
        self.save_name_input.clear()
        CustomMessageBox.information(self, "✅ ذخیره شد", f"تنظیمات \"{name}\" ذخیره شد.")

    def _on_load_named(self):
        name = self.saved_settings_combo.currentText()
        if not name:
            CustomMessageBox.information(self, "ℹ️", "تنظیمات ذخیره شده‌ای وجود ندارد.")
            return

        path = SettingsManager.get_settings_path(name)
        settings = SettingsManager.load_settings(path)
        self._current_settings = settings
        self.max_retries_spin.setValue(settings.max_retries)
        self._load_providers_table()
        CustomMessageBox.information(self, "✅ بارگذاری شد", f"تنظیمات \"{name}\" بارگذاری شد.")

    def _on_delete_named(self):
        name = self.saved_settings_combo.currentText()
        if not name:
            return

        reply = CustomMessageBox.question(
            self, "⚠️ حذف",
            f"آیا از حذف تنظیمات \"{name}\" اطمینان دارید؟"
        )
        if reply == QMessageBox.Yes:
            path = SettingsManager.get_settings_path(name)
            if path.exists():
                path.unlink()
            self._refresh_saved_list()

    # ------------------------------------------------------------------ #
    # Save & Apply
    # ------------------------------------------------------------------ #

    def _build_current_settings(self) -> SettingsConfig:
        return SettingsConfig(
            llm_providers=list(self._current_settings.llm_providers),
            max_retries=self.max_retries_spin.value(),
        )

    def _on_save_and_apply(self):
        settings = self._build_current_settings()
        if not settings.llm_providers:
            CustomMessageBox.warning(self, "⚠️ خطا", "حداقل یک Provider اضافه کنید.")
            return

        enabled = [p for p in settings.llm_providers if p.enabled]
        if not enabled:
            CustomMessageBox.warning(self, "⚠️ خطا", "حداقل یک Provider فعال نیاز است.")
            return

        SettingsManager.save_settings(settings)
        self._current_settings = settings
        self.settings_saved.emit()
        CustomMessageBox.information(self, "✅ ذخیره شد", "تنظیمات با موفقیت ذخیره و اعمال شد.")
        self.accept()
