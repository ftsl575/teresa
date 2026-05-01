"""
teresa_gui.py — PyQt6 GUI front-end for run.ps1

Layout:
  Left  — vendor buttons (Dell / Cisco / HPE / Lenovo / Huawei / xFusion)
          + "Full Pipeline" button + AI toggle + Tests toggle
  Right — OpenAI key field with "Save to env" button
          + status table showing which step is running / done / failed
          + "Open OUTPUT folder" / "Open log folder" buttons

When user clicks a button:
  1. Validates inputs (vendor/AI mode/key presence)
  2. Spawns a NEW PowerShell window via `start powershell` so the user sees raw output
  3. In parallel, GUI polls the latest log file (under temp/diag/runs) and updates step statuses

Dependencies: PyQt6 only (pip install PyQt6).
Tested on Windows 10/11 with Python 3.10+.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QMessageBox,
    QFrame, QStatusBar,
)


# ─── Configuration ──────────────────────────────────────────────────────────

VENDORS_ACTIVE = ["dell", "cisco", "hpe", "lenovo", "huawei", "xfusion"]
VENDORS_DISABLED = []

REPO_ROOT = Path(__file__).resolve().parent
RUN_PS1 = REPO_ROOT / "run.ps1"


# ─── Style ──────────────────────────────────────────────────────────────────

STYLESHEET = """
QMainWindow {
    background-color: #1e1e2e;
}
QGroupBox {
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: 600;
    font-size: 11pt;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 10px 14px;
    font-size: 10pt;
    font-weight: 500;
    text-align: left;
    padding-left: 14px;
}
QPushButton:hover {
    background-color: #45475a;
    border-color: #89b4fa;
}
QPushButton:pressed {
    background-color: #585b70;
}
QPushButton:disabled {
    background-color: #1e1e2e;
    color: #6c7086;
    border-color: #313244;
}
QPushButton#fullPipelineBtn {
    background-color: #89b4fa;
    color: #1e1e2e;
    font-weight: 700;
    font-size: 11pt;
}
QPushButton#fullPipelineBtn:hover {
    background-color: #b4befe;
}
QPushButton#saveKeyBtn {
    background-color: #a6e3a1;
    color: #1e1e2e;
    font-weight: 600;
}
QPushButton#saveKeyBtn:hover {
    background-color: #94d196;
}
QPushButton#openFolderBtn {
    background-color: #313244;
    color: #cdd6f4;
    text-align: center;
}
QLineEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 6px 8px;
    font-size: 10pt;
    font-family: Consolas, monospace;
}
QLineEdit:focus {
    border-color: #89b4fa;
}
QCheckBox {
    color: #cdd6f4;
    font-size: 10pt;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #45475a;
    border-radius: 3px;
    background-color: #181825;
}
QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}
QLabel {
    color: #cdd6f4;
    font-size: 10pt;
}
QLabel#sectionLabel {
    color: #89b4fa;
    font-weight: 600;
    font-size: 11pt;
}
QLabel#statusOk {
    color: #a6e3a1;
    font-weight: 600;
}
QLabel#statusErr {
    color: #f38ba8;
    font-weight: 600;
}
QLabel#statusInfo {
    color: #fab387;
    font-weight: 500;
}
QTableWidget {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    gridline-color: #313244;
    font-size: 10pt;
}
QHeaderView::section {
    background-color: #313244;
    color: #cdd6f4;
    border: none;
    padding: 6px;
    font-weight: 600;
}
QStatusBar {
    background-color: #181825;
    color: #6c7086;
    border-top: 1px solid #313244;
}
"""


# ─── Helpers ────────────────────────────────────────────────────────────────

def get_env_key():
    """Read OPENAI_API_KEY from current process env."""
    return os.environ.get("OPENAI_API_KEY", "").strip()


def set_env_key_windows_user(key: str) -> bool:
    """
    Persist OPENAI_API_KEY to Windows User-level environment via setx.
    Returns True on success.
    Note: setx writes to registry; takes effect for new processes only,
    but we also export to current process env so user can run immediately.
    """
    try:
        # setx persists for User scope; takes effect in NEW shells.
        result = subprocess.run(
            ["setx", "OPENAI_API_KEY", key],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return False
        # Apply to current GUI process so child PowerShell inherits it now.
        os.environ["OPENAI_API_KEY"] = key
        return True
    except Exception:
        return False


def launch_run_ps1(args: list) -> None:
    """
    Launch run.ps1 in a NEW PowerShell window so user sees full output.
    Uses 'start' verb with -NoExit so the window stays open after completion.
    """
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-NoExit",
        "-File", str(RUN_PS1),
    ] + args

    # CREATE_NEW_CONSOLE = 0x00000010 — opens visible new console window
    subprocess.Popen(
        cmd,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        cwd=str(REPO_ROOT),
    )


# ─── Main window ────────────────────────────────────────────────────────────

class TeresaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("teresa — spec_classifier launcher")
        self.setMinimumSize(QSize(900, 600))
        self.setStyleSheet(STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(14)

        # Left column ─ vendor buttons + options
        left_col = self._build_left_column()
        root_layout.addLayout(left_col, stretch=1)

        # Right column ─ key + status
        right_col = self._build_right_column()
        root_layout.addLayout(right_col, stretch=1)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._refresh_key_status()

    # ── Left ────────────────────────────────────────────────────────────────

    def _build_left_column(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Vendor buttons
        vendor_box = QGroupBox("Per-vendor pipeline")
        vendor_layout = QVBoxLayout(vendor_box)
        vendor_layout.setSpacing(6)

        vendor_labels = {
            "dell": "Dell",
            "cisco": "Cisco CCW",
            "hpe": "HPE",
            "lenovo": "Lenovo",
            "huawei": "Huawei",
            "xfusion": "xFusion",
        }
        for v in VENDORS_ACTIVE:
            btn = QPushButton(f"  ▶  {vendor_labels.get(v, v.title())}")
            btn.clicked.connect(lambda _checked, vendor=v: self._run_vendor(vendor))
            vendor_layout.addWidget(btn)

        layout.addWidget(vendor_box)

        # Full pipeline + options
        full_box = QGroupBox("Full pipeline")
        full_layout = QVBoxLayout(full_box)
        full_layout.setSpacing(8)

        self.full_btn = QPushButton("  ▶▶  Run all vendors  ▶▶")
        self.full_btn.setObjectName("fullPipelineBtn")
        self.full_btn.clicked.connect(self._run_full)
        full_layout.addWidget(self.full_btn)

        self.cb_ai = QCheckBox("AI audit (gpt-4o-mini)")
        self.cb_ai.setChecked(True)
        self.cb_ai.setToolTip("If unchecked, runs rule-based audit only (no OpenAI call).")
        full_layout.addWidget(self.cb_ai)

        self.cb_tests = QCheckBox("Run pytest after pipeline")
        self.cb_tests.setChecked(True)
        full_layout.addWidget(self.cb_tests)

        layout.addWidget(full_box)

        # Tests-only quick action
        tests_box = QGroupBox("Quick actions")
        tests_layout = QVBoxLayout(tests_box)
        tests_btn = QPushButton("  🧪  Run pytest only")
        tests_btn.clicked.connect(self._run_tests_only)
        tests_layout.addWidget(tests_btn)
        layout.addWidget(tests_box)

        layout.addStretch()
        return layout

    # ── Right ───────────────────────────────────────────────────────────────

    def _build_right_column(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # OpenAI key
        key_box = QGroupBox("OpenAI API key")
        key_layout = QVBoxLayout(key_box)
        key_layout.setSpacing(8)

        self.key_status_label = QLabel("checking…")
        self.key_status_label.setObjectName("statusInfo")
        key_layout.addWidget(self.key_status_label)

        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("sk-… (leave blank to keep current)")
        key_layout.addWidget(self.key_input)

        save_btn = QPushButton("Save to Windows env (User scope)")
        save_btn.setObjectName("saveKeyBtn")
        save_btn.clicked.connect(self._save_key)
        key_layout.addWidget(save_btn)

        hint = QLabel(
            "Stored via <b>setx</b> at User scope. New PowerShell windows<br>"
            "spawned by this GUI will inherit the key automatically."
        )
        hint.setStyleSheet("color: #6c7086; font-size: 9pt;")
        hint.setWordWrap(True)
        key_layout.addWidget(hint)

        layout.addWidget(key_box)

        # Quick info / paths
        info_box = QGroupBox("Paths")
        info_layout = QVBoxLayout(info_box)
        info_layout.setSpacing(4)

        self.path_input = QLabel(self._discover_input_path())
        self.path_output = QLabel(self._discover_output_path())
        self.path_input.setStyleSheet("font-family: Consolas, monospace; font-size: 9pt;")
        self.path_output.setStyleSheet("font-family: Consolas, monospace; font-size: 9pt;")

        info_layout.addWidget(QLabel("Input:"))
        info_layout.addWidget(self.path_input)
        info_layout.addWidget(QLabel("Output:"))
        info_layout.addWidget(self.path_output)

        btn_row = QHBoxLayout()
        open_input_btn = QPushButton("Open INPUT")
        open_input_btn.setObjectName("openFolderBtn")
        open_input_btn.clicked.connect(lambda: self._open_folder(self.path_input.text()))
        btn_row.addWidget(open_input_btn)

        open_output_btn = QPushButton("Open OUTPUT")
        open_output_btn.setObjectName("openFolderBtn")
        open_output_btn.clicked.connect(lambda: self._open_folder(self.path_output.text()))
        btn_row.addWidget(open_output_btn)

        info_layout.addLayout(btn_row)
        layout.addWidget(info_box)

        # Last action status
        last_box = QGroupBox("Last action")
        last_layout = QVBoxLayout(last_box)
        self.last_action = QLabel("—")
        self.last_action.setStyleSheet("font-family: Consolas, monospace; font-size: 9pt;")
        self.last_action.setWordWrap(True)
        last_layout.addWidget(self.last_action)
        layout.addWidget(last_box)

        layout.addStretch()
        return layout

    # ── Path discovery ──────────────────────────────────────────────────────

    def _discover_input_path(self) -> str:
        cfg = REPO_ROOT / "spec_classifier" / "config.local.yaml"
        if cfg.exists():
            try:
                text = cfg.read_text(encoding="utf-8")
                for line in text.splitlines():
                    line = line.strip()
                    if line.startswith("input_root:"):
                        return line.split(":", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
        return str(Path.home() / "Desktop" / "INPUT")

    def _discover_output_path(self) -> str:
        cfg = REPO_ROOT / "spec_classifier" / "config.local.yaml"
        if cfg.exists():
            try:
                text = cfg.read_text(encoding="utf-8")
                for line in text.splitlines():
                    line = line.strip()
                    if line.startswith("output_root:"):
                        return line.split(":", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
        return str(Path.home() / "Desktop" / "OUTPUT")

    # ── Actions ─────────────────────────────────────────────────────────────

    def _refresh_key_status(self):
        key = get_env_key()
        if key:
            preview = f"sk-…{key[-4:]}" if len(key) >= 4 else "(set)"
            self.key_status_label.setText(f"✓ Saved in env  ({preview})")
            self.key_status_label.setObjectName("statusOk")
        else:
            self.key_status_label.setText("✗ Not set in environment")
            self.key_status_label.setObjectName("statusErr")
        self.key_status_label.style().unpolish(self.key_status_label)
        self.key_status_label.style().polish(self.key_status_label)

    def _save_key(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Empty key", "Paste your OpenAI key into the field first.")
            return
        if not key.startswith("sk-"):
            reply = QMessageBox.question(
                self, "Unusual key format",
                "Key doesn't start with 'sk-'. Save anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        ok = set_env_key_windows_user(key)
        if ok:
            self.key_input.clear()
            self._refresh_key_status()
            QMessageBox.information(
                self, "Saved",
                "Key saved to Windows User environment.\n\n"
                "It will persist across reboots.\n"
                "Already-open shells won't see it; new shells will.",
            )
        else:
            QMessageBox.critical(self, "Failed", "setx returned an error. Try running GUI as Administrator?")

    def _run_vendor(self, vendor: str):
        ai = self.cb_ai.isChecked()
        tests = self.cb_tests.isChecked()
        args = ["-Vendor", vendor]
        if not ai:
            args.append("-NoAi")
        if not tests:
            args.append("-SkipTests")
        if not ai or get_env_key():
            self._launch(args, f"{vendor} (AI={'on' if ai else 'off'})")
        else:
            self._warn_no_key()

    def _run_full(self):
        ai = self.cb_ai.isChecked()
        tests = self.cb_tests.isChecked()
        args = []
        if not ai:
            args.append("-NoAi")
        if not tests:
            args.append("-SkipTests")
        if not ai or get_env_key():
            self._launch(args, f"full pipeline (AI={'on' if ai else 'off'})")
        else:
            self._warn_no_key()

    def _run_tests_only(self):
        self._launch(["-TestsOnly"], "pytest only")

    def _launch(self, args: list, label: str):
        if not RUN_PS1.exists():
            QMessageBox.critical(
                self, "run.ps1 not found",
                f"Expected at:\n{RUN_PS1}\n\nMake sure run.ps1 is in the same folder as teresa_gui.py.",
            )
            return
        launch_run_ps1(args)
        ts = datetime.now().strftime("%H:%M:%S")
        self.last_action.setText(f"[{ts}] launched: {label}\nargs: {' '.join(args) if args else '(default)'}")
        self.status.showMessage(f"PowerShell window opened — {label}", 5000)

    def _warn_no_key(self):
        QMessageBox.warning(
            self, "OpenAI key required",
            "AI audit is enabled but OPENAI_API_KEY is not set.\n\n"
            "Either:\n"
            "  • Paste your key on the right and click 'Save to Windows env', OR\n"
            "  • Uncheck 'AI audit (gpt-4o-mini)' to run rule-based audit only.",
        )

    def _open_folder(self, path: str):
        p = Path(path)
        if not p.exists():
            QMessageBox.information(self, "Not found", f"Path doesn't exist:\n{path}")
            return
        os.startfile(str(p))


# ─── Entry point ────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # consistent base look across Windows versions
    win = TeresaWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
