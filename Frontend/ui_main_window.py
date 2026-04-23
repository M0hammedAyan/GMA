from pathlib import Path
import shutil
import threading
from datetime import date, datetime

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QDesktopServices, QGuiApplication
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QStackedWidget, QVBoxLayout, QWidget

from Frontend.pages.dashboard_page import DashboardPage
from Frontend.pages.add_patient_page import AddPatientPage
from Frontend.pages.patients_page import PatientsPage
from Frontend.pages.profile_page import ProfilePage
from Frontend.pages.record_page import RecordPage
from Frontend.pages.uploads_page import UploadsPage
from Frontend.ui_theme import DARK_STYLE_SHEET, LIGHT_STYLE_SHEET
from Frontend.widgets.header_widget import HeaderWidget
from Frontend.widgets.recording_checklist_dialog import RecordingChecklistDialog
from recorder import Recorder


def hhmmss(total_seconds):
    hours = total_seconds // 3600
    mins = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02}:{mins:02}:{secs:02}"


class MainWindow(QMainWindow):
    recording_started = Signal()
    recording_start_failed = Signal(str)
    recording_stopped = Signal()
    recording_stop_failed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowTitle("GMA Recording System")
        self.setMinimumSize(800, 480)

        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            target_width = min(1100, available.width())
            target_height = min(680, available.height())
            self.resize(target_width, target_height)

        self.controller = Recorder()
        self.start_thread = None
        self.stop_thread = None
        self.is_recording = False
        self.seconds = 0
        self.uhid_seed = 1000
        self.last_saved_session = ""
        self.sessions = {}
        self.patient_rows = []
        self.selected_patient = None
        self._checklist_ready_for_start = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.recording_started.connect(self._handle_started)
        self.recording_start_failed.connect(self._handle_start_error)
        self.recording_stopped.connect(self._handle_stopped)
        self.recording_stop_failed.connect(self._handle_stop_error)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(8)

        self.header = HeaderWidget()
        self.header.tabChanged.connect(self._goto)
        self.header.themeToggled.connect(self._on_theme_toggled)
        root_layout.addWidget(self.header)

        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.patients_page = PatientsPage()
        self.add_patient_page = AddPatientPage()
        self.record_page = RecordPage()
        self.uploads_page = UploadsPage()
        self.profile_page = ProfilePage()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.patients_page)
        self.stack.addWidget(self.add_patient_page)
        self.stack.addWidget(self.record_page)
        self.stack.addWidget(self.uploads_page)
        self.stack.addWidget(self.profile_page)
        root_layout.addWidget(self.stack, 1)

        self.setCentralWidget(root)
        self.setStyleSheet(LIGHT_STYLE_SHEET)

        self._wire_events()
        self._seed_patients()
        self._seed_dummy_uploads()
        self._update_required_state()
        self._refresh_stats()

    def _wire_events(self):
        self.dashboard_page.recordRequested.connect(lambda: self._goto(1))
        self.dashboard_page.addPatientRequested.connect(self.show_add_patient)
        self.dashboard_page.viewUploadsRequested.connect(lambda: self._goto(2))
        self.dashboard_page.profileRequested.connect(self.show_profile)
        self.dashboard_page.cardActionRequested.connect(self._on_dashboard_card_action)

        self.record_page.action_btn.clicked.connect(self._on_action)
        self.record_page.upload_btn.clicked.connect(self.upload_video_from_device)
        self.record_page.back_button.clicked.connect(lambda: self._goto(1))
        self.header.user_button.clicked.connect(self.show_profile)
        self.profile_page.back_button.clicked.connect(lambda: self._goto(0))
        self.add_patient_page.cancel_btn.clicked.connect(lambda: self._goto(1))
        self.add_patient_page.save_btn.clicked.connect(self._save_new_patient)

        self.patients_page.search_bar.textChanged.connect(self._apply_patient_filters)
        self.patients_page.sort_combo.currentTextChanged.connect(self._apply_patient_filters)
        self.patients_page.patientSelected.connect(self.on_patient_selected)
        self.patients_page.patientRecordRequested.connect(self.on_patient_selected)
        self.patients_page.patientUploadRequested.connect(self._on_patient_upload_requested)
        self.patients_page.addPatientRequested.connect(self.show_add_patient)
        self.uploads_page.patientRequested.connect(self._on_upload_patient_requested)

    def _on_theme_toggled(self, _enabled):
        self.setStyleSheet(DARK_STYLE_SHEET if self.header.dark_toggle.isChecked() else LIGHT_STYLE_SHEET)

    def _goto(self, index):
        tab_to_page = {0: 0, 1: 1, 2: 4}
        if index in tab_to_page:
            self.stack.setCurrentIndex(tab_to_page[index])
            self.header.set_active_tab(index)
            self.header.set_tabs_visible(True)

    def show_record(self):
        self.stack.setCurrentIndex(3)
        self.header.set_active_tab(-1)
        self.header.set_tabs_visible(True)

    def show_profile(self):
        self.stack.setCurrentIndex(5)
        self.header.set_active_tab(-1)
        self.header.set_tabs_visible(False)

    def show_add_patient(self):
        self.add_patient_page.load_new_patient()
        self.stack.setCurrentIndex(2)
        self.header.set_active_tab(-1)
        self.header.set_tabs_visible(True)

    def _show_uploads_tab(self, tab_name):
        self._goto(2)
        self.uploads_page.set_active_tab(tab_name)

    def _on_dashboard_card_action(self, card_title):
        if card_title == "Total Patients":
            self._goto(1)
            return

        upload_tab_map = {
            "Today's Recordings": "pending",
            "Pending Uploads": "pending",
            "Uploaded": "uploaded",
            "Rejected": "rejected",
            "Storage Remaining": "pending",
        }
        tab_name = upload_tab_map.get(card_title)
        if tab_name:
            self._show_uploads_tab(tab_name)

    def _save_new_patient(self):
        patient = self.add_patient_page.get_patient()
        self.patient_rows.append(patient)
        self._apply_patient_filters("All")
        self._refresh_stats()
        self._goto(1)

    def _seed_patients(self):
        self.patient_rows = [
            {"UHID": "U1001", "GMA": "GMA2201", "Name": "Aanya", "Age/Weeks": "32", "DOB": "2025-08-19", "Gender": "F", "Status": "Approved"},
            {"UHID": "U1002", "GMA": "GMA2202", "Name": "Kabir", "Age/Weeks": "29", "DOB": "2025-10-01", "Gender": "M", "Status": "Pending"},
            {"UHID": "U1003", "GMA": "GMA2203", "Name": "Mira", "Age/Weeks": "35", "DOB": "2025-07-04", "Gender": "F", "Status": "Rejected"},
        ]
        self._apply_patient_filters("All")

    def _seed_dummy_uploads(self):
        self.sessions.update(
            {
                "dummy_session_1": {
                    "uhid": "U1001",
                    "name": "Aanya",
                    "duration": "00:04:23",
                    "file_size": "352 MB",
                    "timestamp": "Mar 24, 2026 4:22 PM",
                    "status": "pending",
                },
                "dummy_session_2": {
                    "uhid": "U1002",
                    "name": "Kabir",
                    "duration": "00:03:11",
                    "file_size": "287 MB",
                    "timestamp": "Mar 25, 2026 10:05 AM",
                    "status": "successful",
                },
                "dummy_session_3": {
                    "uhid": "U1003",
                    "name": "Mira",
                    "duration": "00:05:02",
                    "file_size": "401 MB",
                    "timestamp": "Mar 26, 2026 1:18 PM",
                    "status": "rejected",
                },
                "dummy_session_4": {
                    "uhid": "U1001",
                    "name": "Aanya",
                    "duration": "00:02:49",
                    "file_size": "233 MB",
                    "timestamp": "Mar 27, 2026 9:41 AM",
                    "status": "pending",
                },
                "dummy_session_5": {
                    "uhid": "U1002",
                    "name": "Kabir",
                    "duration": "00:06:15",
                    "file_size": "498 MB",
                    "timestamp": "Mar 28, 2026 6:09 PM",
                    "status": "successful",
                },
            }
        )

    def _on_upload_patient_requested(self, patient_id):
        patient_id_text = str(patient_id).strip()
        if not patient_id_text:
            return

        for patient in self.patient_rows:
            if str(patient.get("UHID", "")).strip() == patient_id_text or str(patient.get("GMA", "")).strip() == patient_id_text:
                self.on_patient_selected(patient)
                return

    def _apply_patient_filters(self, _value=None):
        query = self.patients_page.search_bar.text().strip().lower()
        sort_mode = self.patients_page.sort_combo.currentText()

        rows = []
        for row in self.patient_rows:
            row_text = " ".join(str(v).lower() for v in row.values())
            if query and query not in row_text:
                continue
            rows.append(row)

        reverse = False
        key_func = lambda r: str(r.get("Name", "")).lower()

        def _creation_order(value):
            text = str(value or "")
            digits = "".join(ch for ch in text if ch.isdigit())
            return int(digits) if digits else 0

        if sort_mode == "Name (Z-A)":
            reverse = True
        elif sort_mode == "Newest to Oldest":
            key_func = lambda r: datetime.strptime(str(r.get("DOB", "1900-01-01")), "%Y-%m-%d")
            reverse = True
        elif sort_mode == "Oldest to Newest":
            key_func = lambda r: datetime.strptime(str(r.get("DOB", "1900-01-01")), "%Y-%m-%d")
        elif sort_mode == "UHID":
            key_func = lambda r: _creation_order(r.get("UHID", ""))
        elif sort_mode == "GMA UHID":
            key_func = lambda r: _creation_order(r.get("GMA", ""))

        rows.sort(key=key_func, reverse=reverse)

        self.patients_page.patient_table.set_rows(rows)

    def _required_valid(self):
        return self.selected_patient is not None

    def _update_required_state(self):
        can_start = self._required_valid() and not self.is_recording
        self.record_page.action_btn.setEnabled(can_start or self.is_recording)

    def _set_patient_locked(self, locked):
        self.record_page.action_btn.setEnabled((not locked) and self._required_valid() or locked)

    def _set_recording_visuals(self, recording):
        rp = self.record_page
        rp.set_recording_mode(recording)
        if recording:
            rp.action_btn.setObjectName("recordingButton")
            rp.action_btn.setText("Stop Recording")
        else:
            rp.action_btn.setObjectName("primaryButton")
            rp.action_btn.setText("Start Recording")

        for widget in [rp.action_btn]:
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def _on_action(self):
        if self.is_recording:
            self.stop_recording()
        else:
            if self._checklist_ready_for_start:
                self._checklist_ready_for_start = False
                self.start_recording()
                return

            checklist_dialog = RecordingChecklistDialog(self)
            result = checklist_dialog.exec()
            if result == RecordingChecklistDialog.SKIPPED:
                self._checklist_ready_for_start = True
                self.record_page.set_recording_mode(True)
                self._log_status("Checklist skipped. Preview opened.")
                return
            if result != RecordingChecklistDialog.Accepted:
                self._log_status("Recording checklist skipped/cancelled")
                return
            self.start_recording()

    def on_patient_selected(self, patient):
        self.selected_patient = dict(patient)
        self.record_page.set_patient(self.selected_patient)
        self._refresh_patient_upload_history()
        self._update_required_state()
        self._checklist_ready_for_start = False
        self.record_page.set_recording_mode(False)
        self.show_record()
        self._log_status(f"Loaded patient {patient.get('Name', '--')}")

    def _on_patient_upload_requested(self, patient):
        self.selected_patient = dict(patient)
        self.record_page.set_patient(self.selected_patient)
        self._refresh_patient_upload_history()
        self._update_required_state()
        self._checklist_ready_for_start = False
        self.record_page.set_recording_mode(False)
        self.upload_video_from_device()

    def start_recording(self):
        if self.start_thread and self.start_thread.is_alive():
            return
        if not self._required_valid():
            QMessageBox.warning(self, "Missing Required Fields", "Fill Name, Age/Weeks and UHID before recording")
            return

        # Show preview mode right away after checklist so users see the live screen instantly.
        self.record_page.set_recording_mode(True)
        self.record_page.action_btn.setEnabled(False)

        def _worker():
            try:
                self.controller.start()
                self.recording_started.emit()
            except Exception as err:
                self.recording_start_failed.emit(str(err))

        self.start_thread = threading.Thread(target=_worker, daemon=True)
        self.start_thread.start()

    def _handle_started(self):
        self.is_recording = True
        self.seconds = 0
        self.timer.start(1000)
        self._set_patient_locked(True)
        self._set_recording_visuals(True)
        self.record_page.action_btn.setEnabled(True)
        self._log_status("Recording started")
        self.show_record()

    def _handle_start_error(self, message):
        self.is_recording = False
        self.timer.stop()
        error_text = str(message)

        if "realsense" in error_text.lower() and "not detected" in error_text.lower():
            # Keep preview mode visible and show hardware issue inline instead of interrupting with a modal.
            self.record_page.set_recording_mode(True)
            self.record_page.set_preview_error("RealSense not detected")
            self.record_page.action_btn.setObjectName("primaryButton")
            self.record_page.action_btn.setText("Start Recording")
            self.record_page.action_btn.setEnabled(True)
            self.record_page.action_btn.style().unpolish(self.record_page.action_btn)
            self.record_page.action_btn.style().polish(self.record_page.action_btn)
            self._log_status("RealSense not detected. Connect camera and retry.")
            return

        self._set_recording_visuals(False)
        self._update_required_state()
        self._log_status(f"Error: {error_text}")
        QMessageBox.critical(self, "Recording Error", error_text)

    def stop_recording(self):
        if self.stop_thread and self.stop_thread.is_alive():
            return

        self.record_page.action_btn.setEnabled(False)
        self._log_status("Stopping recording and finalizing files...")

        def _worker():
            try:
                self.controller.stop()
                self.recording_stopped.emit()
            except Exception as err:
                self.recording_stop_failed.emit(str(err))

        self.stop_thread = threading.Thread(target=_worker, daemon=True)
        self.stop_thread.start()

    def _handle_stopped(self):
        self.timer.stop()
        self.is_recording = False
        self._set_patient_locked(False)
        self._set_recording_visuals(False)
        self._update_required_state()

        self.last_saved_session = self._latest_session_path()
        if self.last_saved_session and self.last_saved_session not in self.sessions:
            status = "pending"
            self.sessions[self.last_saved_session] = {
                "uhid": self.selected_patient.get("UHID", ""),
                "name": self.selected_patient.get("Name", ""),
                "duration": hhmmss(self.seconds),
                "file_size": self._session_size_text(self.last_saved_session),
                "timestamp": datetime.now().strftime("%b %d, %Y %I:%M %p").lstrip("0"),
                "status": status,
            }

        self._log_status(
            f"Recording: {hhmmss(self.seconds)}\n"
            f"Saved under: {self.selected_patient.get('Name', '--')} / {self.selected_patient.get('UHID', '--')}\n"
            f"Path: {self.last_saved_session}"
        )

        self.record_page.action_btn.setEnabled(True)
        if self.controller.last_error is not None:
            QMessageBox.warning(self, "Capture Warning", str(self.controller.last_error))

        self._refresh_patient_upload_history()
        self._refresh_stats()

    def _handle_stop_error(self, message):
        self.timer.stop()
        self.is_recording = False
        self._set_patient_locked(False)
        self._set_recording_visuals(False)
        self._update_required_state()
        self.record_page.action_btn.setEnabled(True)
        self._log_status(f"Stop Error: {message}")
        QMessageBox.critical(self, "Stop Error", message)

    def _latest_session_path(self):
        root = Path(self.controller.output_root)
        if not root.exists():
            return ""
        candidates = sorted(root.glob("session_*"), key=lambda p: p.stat().st_mtime)
        return str(candidates[-1]) if candidates else ""

    def update_timer(self):
        self.seconds += 1
        timer_text = hhmmss(self.seconds)
        self.record_page.timer_label.setText(timer_text)
        self.record_page.set_preview_timer(timer_text)
        self._log_status(f"Recording: {timer_text}", replace_last=True)

    def preview_last_session(self):
        if not self.last_saved_session:
            QMessageBox.information(self, "Preview", "No recorded session found")
            return
        QDesktopServices.openUrl(Path(self.last_saved_session).resolve().as_uri())

    def upload_last_session(self):
        if not self.last_saved_session:
            QMessageBox.information(self, "Upload", "No recorded session available")
            return
        if self.last_saved_session in self.sessions:
            self.sessions[self.last_saved_session]["status"] = "successful"
            self._refresh_patient_upload_history()
            self._refresh_stats()
            self._log_status("Upload marked successful")
            self._goto(2)

    def upload_video_from_device(self):
        if not self.selected_patient:
            QMessageBox.warning(self, "Upload", "Select a patient before uploading a video")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video to Upload",
            "",
            "Video Files (*.mp4 *.mov *.avi *.mkv *.wmv *.m4v);;All Files (*.*)",
        )
        if not file_path:
            return

        source = Path(file_path)
        if not source.exists() or not source.is_file():
            QMessageBox.warning(self, "Upload", "Selected file is not valid")
            return

        stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        session_key = f"device_upload_{stamp}_{source.name}"
        size_mb = source.stat().st_size / (1024 * 1024)

        self.sessions[session_key] = {
            "uhid": self.selected_patient.get("UHID", ""),
            "name": self.selected_patient.get("Name", ""),
            "duration": "--",
            "file_size": f"{size_mb:.0f} MB",
            "timestamp": datetime.now().strftime("%b %d, %Y %I:%M %p").lstrip("0"),
            "status": "successful",
            "source_path": str(source),
        }

        self._refresh_patient_upload_history()
        self._refresh_stats()
        self._log_status(f"Uploaded video from device: {source.name}")
        self._goto(2)

    def _refresh_patient_upload_history(self):
        if not self.selected_patient:
            self.record_page.set_upload_history([])
            return

        selected_uhid = str(self.selected_patient.get("UHID", "")).strip()
        history = []

        for _path, data in reversed(list(self.sessions.items())):
            if str(data.get("uhid", "")).strip() != selected_uhid:
                continue
            history.append(
                {
                    "status": data.get("status", "pending"),
                    "timestamp": data.get("timestamp", "--"),
                    "duration": data.get("duration", "00:00:00"),
                    "file_size": data.get("file_size", "0 MB"),
                }
            )

        self.record_page.set_upload_history(history)

    def _session_size_text(self, session_path):
        base = Path(session_path)
        if not base.exists():
            return "0 MB"
        total_bytes = 0
        for path in base.rglob("*"):
            if path.is_file():
                total_bytes += path.stat().st_size
        mb = total_bytes / (1024 * 1024)
        return f"{mb:.0f} MB"

    def _refresh_uploads_view(self):
        pending = []
        uploaded = []
        rejected = []

        for session_path, data in sorted(self.sessions.items()):
            status = data.get("status", "pending")
            item = {
                "patient_name": data.get("name", "--"),
                "uhid": data.get("uhid", "--"),
                "duration": data.get("duration", "00:00:00"),
                "file_size": data.get("file_size", "0 MB"),
                "timestamp": data.get("timestamp", "--"),
                "status": status,
                "session_path": session_path,
            }
            if status == "successful":
                uploaded.append(item)
            elif status == "rejected":
                rejected.append(item)
            else:
                pending.append(item)

        self.uploads_page.set_uploads(pending=pending, uploaded=uploaded, rejected=rejected)

    def _refresh_stats(self):
        pending = sum(1 for s in self.sessions.values() if s["status"] == "pending")
        uploaded = sum(1 for s in self.sessions.values() if s["status"] == "successful")
        rejected = sum(1 for s in self.sessions.values() if s["status"] == "rejected")
        total_patients = len(self.patient_rows)
        todays_recordings = len(self.sessions)

        usage = shutil.disk_usage(self.controller.output_root if Path(self.controller.output_root).exists() else ".")
        remaining_gb = f"{usage.free / (1024**3):.1f} GB"

        self.dashboard_page.update_stats(
            {
                "Total Patients": total_patients,
                "Today's Recordings": todays_recordings,
                "Pending Uploads": pending,
                "Uploaded": uploaded,
                "Rejected": rejected,
                "Storage Remaining": remaining_gb,
            }
        )
        self._refresh_uploads_view()

    def _log_status(self, message, replace_last=False):
        self.record_page.status_label.setText(message)
