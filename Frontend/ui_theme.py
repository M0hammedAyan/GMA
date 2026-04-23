DARK_STYLE_SHEET = """
QWidget { background: #09090B; color: #FAFAFA; font-size: 14px; }
QFrame#topHeader, QFrame#panel, QFrame#statsCard {
	background: #111113;
	border: 1px solid #27272A;
	border-radius: 12px;
}
QFrame#topHeader {
	min-height: 88px;
}
QFrame#headerDivider {
	background: #2B3448;
	border: none;
	margin: 2px 2px;
}

QLabel#appTitle { font-size: 20px; font-weight: 700; }
QLabel#sectionTitle { font-size: 17px; font-weight: 600; }
QLabel#uploadsQueueTitle {
	font-size: 17px;
	font-weight: 700;
	background: transparent;
}
QScrollArea#homeScroll {
	background: transparent;
	border: none;
}
QScrollArea#homeScroll > QWidget > QWidget {
	background: transparent;
}
QFrame#homeHeroCard {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #1F4D47, stop: 1 #23394A);
	border: 1px solid #2E6D67;
	border-radius: 18px;
}
QFrame#homeHeroCard:hover {
	border: 1px solid #5FA39A;
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #245952, stop: 1 #29465A);
}
QLabel#homeHeroCaption {
	font-size: 17px;
	font-weight: 700;
	letter-spacing: 1px;
	color: #B8DCD7;
	background: transparent;
}
QLabel#homeHeroName {
	font-size: 28px;
	font-weight: 700;
	color: #F3FFFC;
	background: transparent;
}
QLabel#homeHeroRole {
	font-size: 14px;
	font-weight: 600;
	color: #D3ECE8;
	background: #2E5D58;
	border-radius: 14px;
	padding: 5px 12px;
}
QLabel#homeHeroAvatar {
	background: #2E5D58;
	border: 1px solid #3B766F;
	border-radius: 35px;
}
QLabel#homeSectionTitle {
	font-size: 28px;
	font-weight: 700;
	color: #E5E7EB;
	background: transparent;
}
QLabel#homeSectionSubtitle {
	font-size: 14px;
	font-weight: 500;
	color: #A1A1AA;
	background: transparent;
}
QFrame#homeStatCard {
	background: #111827;
	border: 1px solid #223047;
	border-radius: 14px;
}
QFrame#homeStatCard:hover {
	border: 1px solid #3B82F6;
	background: #162236;
}
QLabel#homeStatIcon {
	background: #1F2937;
	border: none;
	border-radius: 10px;
}
QLabel#homeStatIcon[variant="patients"] { background: #163F3B; }
QLabel#homeStatIcon[variant="pending"] { background: #4D3A1F; }
QLabel#homeStatIcon[variant="uploaded"] { background: #12463A; }
QLabel#homeStatIcon[variant="rejected"] { background: #4D1F27; }
QLabel#homeStatTitle {
	font-size: 16px;
	font-weight: 700;
	color: #F3F4F6;
	background: transparent;
}
QLabel#homeStatValue {
	font-size: 32px;
	font-weight: 800;
	color: #FFFFFF;
	background: transparent;
}
QLabel#homeStatSubtitle {
	font-size: 13px;
	font-weight: 500;
	color: #9CA3AF;
	background: transparent;
}
QLabel#homeStatArrow {
	font-size: 18px;
	font-weight: 700;
	background: #1C2A3F;
	border: 1px solid #304562;
	border-radius: 11px;
	color: #93C5FD;
}
QFrame#homeQuickAction {
	background: #101623;
	border: 1px solid #222F45;
	border-radius: 14px;
}
QFrame#homeQuickAction:hover {
	border: 1px solid #60A5FA;
	background: #162134;
}
QLabel#homeQuickIcon {
	background: #1B283B;
	border: none;
	border-radius: 10px;
}
QLabel#homeQuickIcon[variant="record"] { background: #0E4A44; }
QLabel#homeQuickIcon[variant="patient"] { background: #103B48; }
QLabel#homeQuickIcon[variant="upload"] { background: #1A3F32; }
QLabel#homeQuickIcon[variant="profile"] { background: #203A55; }
QLabel#homeQuickTitle {
	font-size: 16px;
	font-weight: 700;
	color: #F9FAFB;
	background: transparent;
}
QLabel#homeQuickSubtitle {
	font-size: 13px;
	font-weight: 500;
	color: #9CA3AF;
	background: transparent;
}
QLabel#homeQuickArrow {
	font-size: 20px;
	font-weight: 700;
	background: transparent;
	color: #D1D5DB;
}
QLabel#statsTitle {
	color: #D1D5DB;
	font-size: 15px;
	font-weight: 800;
	font-family: "Montserrat", "Segoe UI", sans-serif;
	background: transparent;
}
QLabel#statsValue {
	font-size: 34px;
	font-weight: 800;
	font-family: "Poppins", "Segoe UI", sans-serif;
	background: transparent;
}
QFrame#statsCard[variant="patients"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #1E3A8A, stop: 1 #172554);
	border: 1px solid #3B82F6;
}
QFrame#statsCard[variant="recordings"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #0F766E, stop: 1 #134E4A);
	border: 1px solid #2DD4BF;
}
QFrame#statsCard[variant="pending"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #713F12, stop: 1 #422006);
	border: 1px solid #F59E0B;
}
QFrame#statsCard[variant="uploaded"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #14532D, stop: 1 #052E16);
	border: 1px solid #22C55E;
}
QFrame#statsCard[variant="rejected"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #7F1D1D, stop: 1 #450A0A);
	border: 1px solid #EF4444;
}
QFrame#statsCard[variant="storage"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #312E81, stop: 1 #1E1B4B);
	border: 1px solid #6366F1;
}
QFrame#statsCard[variant="success_rate"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #9A3412, stop: 1 #7C2D12);
	border: 1px solid #FB923C;
}
QFrame#statsCard[variant="session_size"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #0E7490, stop: 1 #164E63);
	border: 1px solid #22D3EE;
}
QFrame#statsCard[variant="cameras"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #5B21B6, stop: 1 #3B0764);
	border: 1px solid #A78BFA;
}
QFrame#statsCard[variant="patients"] QLabel#statsTitle,
QFrame#statsCard[variant="recordings"] QLabel#statsTitle,
QFrame#statsCard[variant="pending"] QLabel#statsTitle,
QFrame#statsCard[variant="uploaded"] QLabel#statsTitle,
QFrame#statsCard[variant="rejected"] QLabel#statsTitle,
QFrame#statsCard[variant="storage"] QLabel#statsTitle,
QFrame#statsCard[variant="success_rate"] QLabel#statsTitle,
QFrame#statsCard[variant="session_size"] QLabel#statsTitle,
QFrame#statsCard[variant="cameras"] QLabel#statsTitle {
	color: #D1D5DB;
}
QFrame#statsCard[variant="patients"] QLabel#statsValue,
QFrame#statsCard[variant="recordings"] QLabel#statsValue,
QFrame#statsCard[variant="pending"] QLabel#statsValue,
QFrame#statsCard[variant="uploaded"] QLabel#statsValue,
QFrame#statsCard[variant="rejected"] QLabel#statsValue,
QFrame#statsCard[variant="storage"] QLabel#statsValue,
QFrame#statsCard[variant="success_rate"] QLabel#statsValue,
QFrame#statsCard[variant="session_size"] QLabel#statsValue,
QFrame#statsCard[variant="cameras"] QLabel#statsValue {
	color: #FFFFFF;
}
QLabel#timer { font-size: 24px; font-weight: 700; color: #FAFAFA; }
QLabel#stateBadge { color: #A1A1AA; font-weight: 600; }
QLabel#patientInfoLabel { color: #FAFAFA; font-size: 14px; font-weight: 500; }
QFrame#recordShell {
	background: #1E6A8D;
	border: 1px solid #0F3E58;
	border-radius: 12px;
}
QFrame#recordLeftPanel, QFrame#recordRightPanel {
	background: #1F6B8F;
	border: 2px solid #0F3E58;
	border-radius: 20px;
}
QLabel#recordField {
	background: #206B8E;
	border: 2px solid #0B3E59;
	border-radius: 9px;
	padding: 0 12px;
	font-size: 22px;
	font-weight: 500;
	color: #E6F4FF;
}
QScrollArea#recordContentScroll {
	background: transparent;
	border: none;
}
QScrollArea#recordContentScroll > QWidget > QWidget {
	background: transparent;
}
QListWidget#patientHistoryList {
	background: #1A5A79;
	border: 1px solid #0B3E59;
	border-radius: 10px;
	padding: 4px;
	color: #E6F4FF;
}
QListWidget#patientHistoryList::item {
	padding: 6px 8px;
	border-bottom: 1px solid #2B7AA0;
}
QListWidget#patientHistoryList::item:selected {
	background: #2563EB;
	color: #FFFFFF;
}
QFrame#recordPreviewCard {
	background: #12283C;
	border: 1px solid #2A4F73;
	border-radius: 14px;
}
QLabel#previewChip {
	background: #1F2937;
	border: 1px solid #334155;
	border-radius: 12px;
	padding: 6px 10px;
	font-size: 12px;
	font-weight: 700;
	color: #E5E7EB;
}
QLabel#previewSurface {
	background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #0F172A, stop: 1 #1E3A8A);
	border: 1px solid #334155;
	border-radius: 12px;
	color: #D1D5DB;
	font-size: 16px;
	font-weight: 600;
}
QLabel#previewStatusChip {
	background: #111827;
	border: 1px solid #374151;
	border-radius: 13px;
	padding: 6px 12px;
	font-size: 13px;
	font-weight: 700;
	color: #E5E7EB;
}
QLabel#previewStatusChip[state="recording"] {
	background: #7F1D1D;
	border: 1px solid #EF4444;
	color: #FEE2E2;
}
QLabel#previewStatusChip[state="error"] {
	background: #7C2D12;
	border: 1px solid #FB923C;
	color: #FFEDD5;
}

QPushButton {
	background: #18181B;
	border: 1px solid #27272A;
	border-radius: 10px;
	padding: 7px 12px;
	color: #FAFAFA;
}
QPushButton:hover { border-color: #3F3F46; }
QPushButton#primaryButton {
	background: #2563EB;
	border-color: #2563EB;
}
QPushButton#quickActionButton {
	min-height: 32px;
	text-align: left;
	padding: 6px 12px;
	font-weight: 700;
	border-radius: 10px;
	color: #FFFFFF;
}
QPushButton#quickActionButton[actionVariant="patients"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #1E3A8A, stop: 1 #1E40AF);
	border: 1px solid #60A5FA;
}
QPushButton#quickActionButton[actionVariant="recordings"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #0F766E, stop: 1 #0F766E);
	border: 1px solid #2DD4BF;
}
QPushButton#quickActionButton[actionVariant="uploads"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #14532D, stop: 1 #166534);
	border: 1px solid #4ADE80;
}
QPushButton#quickActionButton:hover {
	border-width: 2px;
}
QPushButton#navTab {
	min-height: 32px;
	padding: 0 16px;
	font-weight: 700;
	border-radius: 12px;
	color: #E5E7EB;
	background: #171A24;
	border: 1px solid #2A3347;
}
QPushButton#navTab:hover {
	background: #1F2A3D;
	border: 1px solid #4B6B97;
	color: #F8FAFC;
}
QPushButton#navTab[tabVariant="dashboard"] {
	border-color: #3B82F6;
}
QPushButton#navTab[tabVariant="dashboard"]:hover {
	background: #1E3A5F;
	border-color: #60A5FA;
}
QPushButton#navTab[tabVariant="patients"] {
	border-color: #10B981;
}
QPushButton#navTab[tabVariant="patients"]:hover {
	background: #123F35;
	border-color: #34D399;
}
QPushButton#navTab[tabVariant="uploads"] {
	border-color: #F59E0B;
}
QPushButton#navTab[tabVariant="uploads"]:hover {
	background: #4A3410;
	border-color: #FBBF24;
}
QPushButton#navTab[tabVariant="dashboard"]:checked {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #1E40AF, stop: 1 #1D4ED8);
	border: 1px solid #60A5FA;
	color: #FFFFFF;
}
QPushButton#navTab[tabVariant="patients"]:checked {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #065F46, stop: 1 #047857);
	border: 1px solid #34D399;
	color: #FFFFFF;
}
QPushButton#navTab[tabVariant="uploads"]:checked {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #B45309, stop: 1 #D97706);
	border: 1px solid #FCD34D;
	color: #111827;
}
QPushButton#filterChip:checked {
	background: #2563EB;
	border-color: #2563EB;
}
QPushButton#recordingButton {
	background: #DC2626;
	border-color: #DC2626;
}
QPushButton#backButton {
	background: transparent;
	border: 1px solid #27272A;
	padding: 4px 8px;
	max-width: 190px;
}
QPushButton#secondaryButton {
	background: #18181B;
	border: 1px solid #27272A;
}
QPushButton#uploadTab {
	background: transparent;
	border: 1px solid #27272A;
	padding: 4px 10px;
	min-width: 90px;
}
QPushButton#uploadTab:hover {
	background: #1A2234;
	border-color: #3B82F6;
}
QPushButton#uploadTab:checked {
	background: #2563EB;
	border-color: #2563EB;
}
QPushButton#uploadTab[tabVariant="pending"]:hover {
	background: #3F320F;
	border-color: #F59E0B;
}
QPushButton#uploadTab[tabVariant="uploaded"]:hover {
	background: #123226;
	border-color: #22C55E;
}
QPushButton#uploadTab[tabVariant="rejected"]:hover {
	background: #3A1717;
	border-color: #EF4444;
}
QPushButton#uploadTab[tabVariant="pending"]:checked {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #A16207, stop: 1 #CA8A04);
	border-color: #FACC15;
	color: #111827;
}
QPushButton#uploadTab[tabVariant="uploaded"]:checked {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #166534, stop: 1 #15803D);
	border-color: #4ADE80;
	color: #FFFFFF;
}
QPushButton#uploadTab[tabVariant="rejected"]:checked {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #B91C1C, stop: 1 #DC2626);
	border-color: #F87171;
	color: #FFFFFF;
}
QPushButton#themeToggle {
	min-width: 34px;
	max-width: 34px;
	min-height: 34px;
	max-height: 34px;
	border-radius: 17px;
	font-size: 16px;
	font-weight: 700;
	border: 1px solid #4B5D74;
	background: qlineargradient(
		x1: 0, y1: 0,
		x2: 1, y2: 1,
		stop: 0 #2D4A73,
		stop: 1 #2A3B52
	);
	color: #FACC15;
	padding: 0px;
}
QPushButton#themeToggle:checked {
	color: #EAF2FF;
}
QPushButton#themeToggle:hover {
	background: qlineargradient(
		x1: 0, y1: 0,
		x2: 1, y2: 1,
		stop: 0 #355B8C,
		stop: 1 #314866
	);
	border: 1px solid #5D7492;
}
QPushButton#themeToggle:pressed {
	background: #223247;
}
QPushButton#userButton {
	min-height: 38px;
	border-radius: 19px;
	padding: 0 14px;
	font-size: 14px;
	font-weight: 600;
	color: #F3F4F6;
	background: qlineargradient(
		x1: 0, y1: 0,
		x2: 1, y2: 1,
		stop: 0 #2A333F,
		stop: 1 #1F2937
	);
	border: 1px solid #4B5563;
}
QPushButton#userButton:hover {
	border: 1px solid #6B7280;
	background: qlineargradient(
		x1: 0, y1: 0,
		x2: 1, y2: 1,
		stop: 0 #374151,
		stop: 1 #293548
	);
}
QPushButton#userButton:pressed {
	background: #1F2A38;
}
QLineEdit#compactInput, QDateEdit#compactInput, QSpinBox#compactInput, QComboBox#compactInput {
	background: #111113;
	color: #FAFAFA;
	border: 1px solid #27272A;
	border-radius: 10px;
	padding: 6px 8px;
}
QHeaderView::section {
	background: #111113;
	border: 1px solid #27272A;
	padding: 8px;
}

QLabel#preview {
	border: 1px dashed #3F3F46;
	border-radius: 10px;
	color: #A1A1AA;
}
QLabel#previewRecording {
	border: 2px solid #DC2626;
	border-radius: 10px;
	color: #FAFAFA;
}

QLabel#avatarWidget {
	background: #18181B;
	border: 1px solid #27272A;
	border-radius: 24px;
	font-size: 18px;
	font-weight: 700;
	color: #FAFAFA;
}
QLabel#profileKey {
	color: #A1A1AA;
	font-size: 13px;
	background: transparent;
}
QLabel#profileValue {
	color: #FAFAFA;
	font-size: 13px;
	font-weight: 500;
}
QFrame#profileHeaderCard {
	background: transparent;
	border: 1px solid #24344D;
	border-radius: 12px;
}
QFrame#profileFormCard {
	background: transparent;
	border: 1px solid #24344D;
	border-radius: 12px;
}
QFrame#profileHeaderCard QLabel,
QFrame#profileFormCard QLabel {
	background: transparent;
}
QLabel#profileAvatar {
	background: #1F3A50;
	border: 1px solid #2F4D67;
	border-radius: 26px;
	font-size: 20px;
	font-weight: 800;
	color: #CCFBF1;
}
QLineEdit#profileField {
	background: #0F172A;
	color: #F8FAFC;
	border: 1px solid #334155;
	border-radius: 10px;
	padding: 6px 8px;
}
QLineEdit#profileField:read-only {
	background: #0F172A;
	color: #CBD5E1;
}
QLabel#hospitalIcon {
	padding: 2px;
}

QLabel#addPreviewAvatar {
	background: #18181B;
	border: 1px solid #27272A;
	border-radius: 23px;
	font-size: 16px;
	font-weight: 700;
	color: #FAFAFA;
}

QFrame#uploadCard {
	background: #111113;
	border: 1px solid #202026;
	border-radius: 10px;
}
QFrame#uploadCard:hover {
	border: 1px solid #3B82F6;
}
QFrame#uploadCard[status="pending"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #3C2D0A, stop: 1 #241B05);
	border: 1px solid #A16207;
}
QFrame#uploadCard[status="pending"]:hover {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #4B3810, stop: 1 #2F2408);
	border: 1px solid #F59E0B;
}
QFrame#uploadCard[status="uploading"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #113329, stop: 1 #0A1F18);
	border: 1px solid #15803D;
}
QFrame#uploadCard[status="uploading"]:hover {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #154336, stop: 1 #0D2920);
	border: 1px solid #22C55E;
}
QFrame#uploadCard[status="rejected"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #3A1414, stop: 1 #220C0C);
	border: 1px solid #B91C1C;
}
QFrame#uploadCard[status="rejected"]:hover {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #4A1A1A, stop: 1 #2A1010);
	border: 1px solid #EF4444;
}
QFrame#patientsTopBar {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #13203A, stop: 1 #1A2E50);
	border: 1px solid #3B82F6;
	border-radius: 12px;
}
QFrame#patientsTablePanel, QFrame#patientsListPanel {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #0E172A, stop: 1 #0B1220);
	border: 1px solid #2A3D61;
	border-radius: 12px;
}
QFrame#patientsDirectoryHeader {
	background: #101827;
	border: 1px solid #25334A;
	border-radius: 12px;
}
QLabel#patientsDirectoryTitle {
	font-size: 24px;
	font-weight: 800;
	color: #F8FAFC;
	background: transparent;
}
QLabel#patientsDirectorySubtitle {
	font-size: 13px;
	font-weight: 500;
	color: #94A3B8;
	background: transparent;
}
QPushButton#sortChip {
	min-height: 28px;
	padding: 0 12px;
	border-radius: 14px;
	background: #1A2436;
	border: 1px solid #2C3D5A;
	color: #CBD5E1;
	font-weight: 700;
}
QPushButton#sortChip:hover {
	background: #22324A;
	border: 1px solid #4B6B97;
	color: #E2E8F0;
}
QPushButton#sortChip:checked {
	background: #223A54;
	border: 1px solid #3B82F6;
	color: #E2E8F0;
}
QScrollArea#patientsListScroll {
	background: transparent;
	border: none;
}
QScrollArea#patientsListScroll > QWidget > QWidget {
	background: transparent;
}
QFrame#patientListCard {
	background: #111D30;
	border: 1px solid #2B3D5D;
	border-radius: 14px;
}
QFrame#patientListCard:hover {
	background: #17263D;
	border: 1px solid #3B82F6;
}
QLabel#patientAvatar {
	background: #1E3448;
	border-radius: 18px;
	font-size: 17px;
	font-weight: 800;
	color: #99F6E4;
}
QLabel#patientName {
	font-size: 18px;
	font-weight: 800;
	color: #F8FAFC;
	background: transparent;
}
QLabel#patientMeta {
	font-size: 12px;
	font-weight: 500;
	color: #94A3B8;
	background: transparent;
}
QLabel#patientRowChevron {
	font-size: 20px;
	font-weight: 700;
	color: #94A3B8;
	background: transparent;
}
QPushButton#patientActionButton {
	min-height: 28px;
	min-width: 86px;
	padding: 0 12px;
	border-radius: 12px;
	font-size: 11px;
	font-weight: 700;
	background: #1A2436;
	border: 1px solid #2C3D5A;
	color: #E2E8F0;
}
QPushButton#patientActionButton:hover {
	background: #22324A;
	border: 1px solid #4B6B97;
}
QPushButton#patientActionButton[variant="record"] {
	background: #0B3F3A;
	border: 1px solid #0F766E;
	color: #CCFBF1;
}
QPushButton#patientActionButton[variant="record"]:hover {
	background: #0F514A;
	border: 1px solid #2DD4BF;
	color: #ECFEFF;
}
QPushButton#patientActionButton[variant="upload"] {
	background: #1E293B;
	border: 1px solid #3B82F6;
	color: #DBEAFE;
}
QPushButton#patientActionButton[variant="upload"]:hover {
	background: #25344C;
	border: 1px solid #60A5FA;
	color: #EFF6FF;
}
QPushButton#patientsFab {
	min-width: 46px;
	max-width: 46px;
	min-height: 46px;
	max-height: 46px;
	border-radius: 23px;
	font-size: 24px;
	font-weight: 700;
	background: #0F172A;
	border: 1px solid #2E3A55;
	color: #E2E8F0;
}
QFrame#uploadsTopBar {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #13203A, stop: 1 #1A2E50);
	border: 1px solid #3B82F6;
	border-radius: 12px;
}
QFrame#uploadsStatsPanel {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #0F172A, stop: 1 #111827);
	border: 1px solid #2F4F78;
	border-radius: 12px;
}
QFrame#uploadsListPanel {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #0E172A, stop: 1 #0B1220);
	border: 1px solid #2A3D61;
	border-radius: 12px;
}
QScrollArea#uploadsScroll {
	background: transparent;
	border: none;
}
QScrollArea#uploadsScroll > QWidget > QWidget {
	background: transparent;
}
QFrame#addPatientTopBar {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #13203A, stop: 1 #1A2E50);
	border: 1px solid #3B82F6;
	border-radius: 12px;
}
QFrame#addPatientFormPanel {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #0E172A, stop: 1 #0B1220);
	border: 1px solid #2A3D61;
	border-radius: 12px;
}
QLabel#formLabel {
	background: transparent;
	color: #BFDBFE;
	font-weight: 600;
	font-size: 14px;
}
QLineEdit#searchBar {
	min-height: 34px;
	border-radius: 10px;
	padding: 0 10px;
	background: #0D1628;
	border: 1px solid #35538B;
	color: #F8FAFC;
	selection-background-color: #2563EB;
}
QLineEdit#searchBar:focus {
	border: 1px solid #60A5FA;
}
QTableWidget#patientTable {
	background: #0D1628;
	alternate-background-color: #111E35;
	border: 1px solid #2A3D61;
	border-radius: 10px;
	gridline-color: #1E2E4C;
	selection-background-color: #1D4ED8;
	selection-color: #FFFFFF;
}
QTableWidget#patientTable::item {
	padding: 8px;
	border-bottom: 1px solid #1E2E4C;
}
QTableWidget#patientTable QHeaderView::section {
	background: #162846;
	color: #BFDBFE;
	font-weight: 700;
	border: 1px solid #28426B;
	padding: 8px;
}
QLabel#uploadPatientName {
	font-size: 13px;
	font-weight: 600;
	color: #FAFAFA;
	background: transparent;
}
QLabel#uploadMeta {
	font-size: 11px;
	color: #A1A1AA;
	background: transparent;
}
QLabel#uploadBadgePending {
	border: 1px solid #EAB308;
	color: #FACC15;
	background: transparent;
	border-radius: 9px;
	padding: 1px 7px;
}
QLabel#uploadBadgeUploaded {
	border: 1px solid #16A34A;
	color: #FFFFFF;
	background: #16A34A;
	border-radius: 9px;
	padding: 1px 7px;
}
QLabel#uploadBadgeRejected {
	border: 1px solid #DC2626;
	color: #F87171;
	background: transparent;
	border-radius: 9px;
	padding: 1px 7px;
}
"""

LIGHT_STYLE_SHEET = """
QWidget { background: #F6F7FB; color: #111827; font-size: 14px; }
QFrame#topHeader, QFrame#panel, QFrame#statsCard {
	background: #FFFFFF;
	border: 1px solid #E5E7EB;
	border-radius: 12px;
}
QFrame#topHeader {
	min-height: 88px;
}
QFrame#headerDivider {
	background: #D7E3EF;
	border: none;
	margin: 2px 2px;
}

QLabel#appTitle { font-size: 20px; font-weight: 700; color: #111827; }
QLabel#sectionTitle { font-size: 17px; font-weight: 600; color: #111827; }
QLabel#uploadsQueueTitle {
	font-size: 17px;
	font-weight: 700;
	color: #111827;
	background: transparent;
}
QScrollArea#homeScroll {
	background: transparent;
	border: none;
}
QScrollArea#homeScroll > QWidget > QWidget {
	background: transparent;
}
QFrame#homeHeroCard {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #245D56, stop: 1 #2F475F);
	border: 1px solid #3C6E6A;
	border-radius: 18px;
}
QFrame#homeHeroCard:hover {
	border: 1px solid #5A8D87;
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #2A6760, stop: 1 #35536B);
}
QLabel#homeHeroCaption {
	font-size: 17px;
	font-weight: 700;
	letter-spacing: 1px;
	color: #CBE5E1;
	background: transparent;
}
QLabel#homeHeroName {
	font-size: 28px;
	font-weight: 700;
	color: #F5FFFD;
	background: transparent;
}
QLabel#homeHeroRole {
	font-size: 14px;
	font-weight: 600;
	color: #E7F6F3;
	background: #3B6A64;
	border-radius: 14px;
	padding: 5px 12px;
}
QLabel#homeHeroAvatar {
	background: #3A6A64;
	border: 1px solid #4C7F79;
	border-radius: 35px;
}
QLabel#homeSectionTitle {
	font-size: 28px;
	font-weight: 700;
	color: #0F172A;
	background: transparent;
}
QLabel#homeSectionSubtitle {
	font-size: 14px;
	font-weight: 500;
	color: #475569;
	background: transparent;
}
QFrame#homeStatCard {
	background: #FFFFFF;
	border: 1px solid #E5E7EB;
	border-radius: 14px;
}
QFrame#homeStatCard:hover {
	border: 1px solid #93C5FD;
	background: #F8FBFF;
}
QLabel#homeStatIcon {
	background: #F1F5F9;
	border: none;
	border-radius: 10px;
}
QLabel#homeStatIcon[variant="patients"] { background: #DDF5F0; }
QLabel#homeStatIcon[variant="pending"] { background: #FFF2DB; }
QLabel#homeStatIcon[variant="uploaded"] { background: #DCFCE8; }
QLabel#homeStatIcon[variant="rejected"] { background: #FDE7EC; }
QLabel#homeStatTitle {
	font-size: 16px;
	font-weight: 700;
	color: #1F2937;
	background: transparent;
}
QLabel#homeStatValue {
	font-size: 32px;
	font-weight: 800;
	color: #0F172A;
	background: transparent;
}
QLabel#homeStatSubtitle {
	font-size: 13px;
	font-weight: 500;
	color: #334155;
	background: transparent;
}
QLabel#homeStatArrow {
	font-size: 18px;
	font-weight: 700;
	background: #EEF7F5;
	border: 1px solid #D8E8E5;
	border-radius: 11px;
	color: #2F6A61;
}
QFrame#homeQuickAction {
	background: #FFFFFF;
	border: 1px solid #E5E7EB;
	border-radius: 14px;
}
QFrame#homeQuickAction:hover {
	border: 1px solid #93C5FD;
	background: #F8FBFF;
}
QLabel#homeQuickIcon {
	background: #EDF2F7;
	border: none;
	border-radius: 10px;
}
QLabel#homeQuickIcon[variant="record"] { background: #D9F5EE; }
QLabel#homeQuickIcon[variant="patient"] { background: #DBF1F8; }
QLabel#homeQuickIcon[variant="upload"] { background: #E2F5E9; }
QLabel#homeQuickIcon[variant="profile"] { background: #E4EEF8; }
QLabel#homeQuickTitle {
	font-size: 16px;
	font-weight: 700;
	color: #111827;
	background: transparent;
}
QLabel#homeQuickSubtitle {
	font-size: 13px;
	font-weight: 500;
	color: #334155;
	background: transparent;
}
QLabel#homeQuickArrow {
	font-size: 20px;
	font-weight: 700;
	background: transparent;
	color: #1F2937;
}
QLabel#statsTitle {
	color: #334155;
	font-size: 15px;
	font-weight: 800;
	font-family: "Montserrat", "Segoe UI", sans-serif;
	background: transparent;
}
QLabel#statsValue {
	font-size: 34px;
	font-weight: 800;
	font-family: "Poppins", "Segoe UI", sans-serif;
	color: #111827;
	background: transparent;
}
QFrame#statsCard[variant="patients"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #DBEAFE, stop: 1 #BFDBFE);
	border: 1px solid #93C5FD;
}
QFrame#statsCard[variant="recordings"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #CCFBF1, stop: 1 #99F6E4);
	border: 1px solid #5EEAD4;
}
QFrame#statsCard[variant="pending"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #FEF3C7, stop: 1 #FDE68A);
	border: 1px solid #FCD34D;
}
QFrame#statsCard[variant="uploaded"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #DCFCE7, stop: 1 #BBF7D0);
	border: 1px solid #86EFAC;
}
QFrame#statsCard[variant="rejected"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #FEE2E2, stop: 1 #FECACA);
	border: 1px solid #FCA5A5;
}
QFrame#statsCard[variant="storage"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #E0E7FF, stop: 1 #C7D2FE);
	border: 1px solid #A5B4FC;
}
QFrame#statsCard[variant="success_rate"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #FFEDD5, stop: 1 #FED7AA);
	border: 1px solid #FDBA74;
}
QFrame#statsCard[variant="session_size"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #CFFAFE, stop: 1 #A5F3FC);
	border: 1px solid #22D3EE;
}
QFrame#statsCard[variant="cameras"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #EDE9FE, stop: 1 #DDD6FE);
	border: 1px solid #C4B5FD;
}
QFrame#statsCard[variant="patients"] QLabel#statsTitle,
QFrame#statsCard[variant="recordings"] QLabel#statsTitle,
QFrame#statsCard[variant="pending"] QLabel#statsTitle,
QFrame#statsCard[variant="uploaded"] QLabel#statsTitle,
QFrame#statsCard[variant="rejected"] QLabel#statsTitle,
QFrame#statsCard[variant="storage"] QLabel#statsTitle,
QFrame#statsCard[variant="success_rate"] QLabel#statsTitle,
QFrame#statsCard[variant="session_size"] QLabel#statsTitle,
QFrame#statsCard[variant="cameras"] QLabel#statsTitle {
	color: #334155;
}
QFrame#statsCard[variant="patients"] QLabel#statsValue,
QFrame#statsCard[variant="recordings"] QLabel#statsValue,
QFrame#statsCard[variant="pending"] QLabel#statsValue,
QFrame#statsCard[variant="uploaded"] QLabel#statsValue,
QFrame#statsCard[variant="rejected"] QLabel#statsValue,
QFrame#statsCard[variant="storage"] QLabel#statsValue,
QFrame#statsCard[variant="success_rate"] QLabel#statsValue,
QFrame#statsCard[variant="session_size"] QLabel#statsValue,
QFrame#statsCard[variant="cameras"] QLabel#statsValue {
	color: #0F172A;
}
QLabel#timer { font-size: 24px; font-weight: 700; color: #111827; }
QLabel#stateBadge { color: #6B7280; font-weight: 600; }
QLabel#patientInfoLabel { color: #111827; font-size: 14px; font-weight: 500; }
QFrame#recordShell {
	background: #EAF4FF;
	border: 1px solid #BFDBFE;
	border-radius: 12px;
}
QFrame#recordLeftPanel, QFrame#recordRightPanel {
	background: #E0F2FE;
	border: 2px solid #93C5FD;
	border-radius: 20px;
}
QLabel#recordField {
	background: #F8FCFF;
	border: 1px solid #BFDBFE;
	border-radius: 9px;
	padding: 0 12px;
	font-size: 20px;
	font-weight: 500;
	color: #0F172A;
}
QScrollArea#recordContentScroll {
	background: transparent;
	border: none;
}
QScrollArea#recordContentScroll > QWidget > QWidget {
	background: transparent;
}
QListWidget#patientHistoryList {
	background: #F8FCFF;
	border: 1px solid #BFDBFE;
	border-radius: 10px;
	padding: 4px;
	color: #0F172A;
}
QListWidget#patientHistoryList::item {
	padding: 6px 8px;
	border-bottom: 1px solid #DBEAFE;
}
QListWidget#patientHistoryList::item:selected {
	background: #DBEAFE;
	color: #0F172A;
}
QFrame#recordPreviewCard {
	background: #F8FBFF;
	border: 1px solid #BFDBFE;
	border-radius: 14px;
}
QLabel#previewChip {
	background: #FFFFFF;
	border: 1px solid #D1D5DB;
	border-radius: 12px;
	padding: 6px 10px;
	font-size: 12px;
	font-weight: 700;
	color: #334155;
}
QLabel#previewSurface {
	background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #F8FAFC, stop: 1 #DBEAFE);
	border: 1px solid #BFDBFE;
	border-radius: 12px;
	color: #64748B;
	font-size: 16px;
	font-weight: 600;
}
QLabel#previewStatusChip {
	background: #FFFFFF;
	border: 1px solid #D1D5DB;
	border-radius: 13px;
	padding: 6px 12px;
	font-size: 13px;
	font-weight: 700;
	color: #334155;
}
QLabel#previewStatusChip[state="recording"] {
	background: #FEE2E2;
	border: 1px solid #F87171;
	color: #991B1B;
}
QLabel#previewStatusChip[state="error"] {
	background: #FFEDD5;
	border: 1px solid #FDBA74;
	color: #9A3412;
}

QPushButton {
	background: #FFFFFF;
	border: 1px solid #D1D5DB;
	border-radius: 10px;
	padding: 7px 12px;
	color: #111827;
}
QPushButton:hover { border-color: #9CA3AF; }
QPushButton#primaryButton {
	background: #2563EB;
	border-color: #2563EB;
	color: #FFFFFF;
}
QPushButton#quickActionButton {
	min-height: 32px;
	text-align: left;
	padding: 6px 12px;
	font-weight: 700;
	border-radius: 10px;
}
QPushButton#quickActionButton[actionVariant="patients"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #DBEAFE, stop: 1 #BFDBFE);
	border: 1px solid #93C5FD;
	color: #1E3A8A;
}
QPushButton#quickActionButton[actionVariant="recordings"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #CCFBF1, stop: 1 #99F6E4);
	border: 1px solid #5EEAD4;
	color: #134E4A;
}
QPushButton#quickActionButton[actionVariant="uploads"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #DCFCE7, stop: 1 #BBF7D0);
	border: 1px solid #86EFAC;
	color: #14532D;
}
QPushButton#quickActionButton:hover {
	border-width: 2px;
}
QPushButton#navTab {
	min-height: 32px;
	padding: 0 16px;
	font-weight: 700;
	border-radius: 12px;
	color: #334155;
	background: #FFFFFF;
	border: 1px solid #CBD5E1;
}
QPushButton#navTab:hover {
	background: #F8FAFC;
	border: 1px solid #94A3B8;
	color: #0F172A;
}
QPushButton#navTab[tabVariant="dashboard"] {
	border-color: #93C5FD;
}
QPushButton#navTab[tabVariant="dashboard"]:hover {
	background: #EFF6FF;
	border-color: #60A5FA;
}
QPushButton#navTab[tabVariant="patients"] {
	border-color: #86EFAC;
}
QPushButton#navTab[tabVariant="patients"]:hover {
	background: #ECFDF5;
	border-color: #4ADE80;
}
QPushButton#navTab[tabVariant="uploads"] {
	border-color: #FCD34D;
}
QPushButton#navTab[tabVariant="uploads"]:hover {
	background: #FFFBEB;
	border-color: #F59E0B;
}
QPushButton#navTab[tabVariant="dashboard"]:checked {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #DBEAFE, stop: 1 #BFDBFE);
	border: 1px solid #60A5FA;
	color: #1E3A8A;
}
QPushButton#navTab[tabVariant="patients"]:checked {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #DCFCE7, stop: 1 #BBF7D0);
	border: 1px solid #4ADE80;
	color: #14532D;
}
QPushButton#navTab[tabVariant="uploads"]:checked {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #FEF3C7, stop: 1 #FDE68A);
	border: 1px solid #F59E0B;
	color: #92400E;
}
QPushButton#filterChip:checked {
	background: #2563EB;
	border-color: #2563EB;
	color: #FFFFFF;
}
QPushButton#recordingButton {
	background: #DC2626;
	border-color: #DC2626;
	color: #FFFFFF;
}
QPushButton#backButton {
	background: transparent;
	border: 1px solid #D1D5DB;
	padding: 4px 8px;
	max-width: 190px;
}
QPushButton#secondaryButton {
	background: #FFFFFF;
	border: 1px solid #D1D5DB;
}
QPushButton#uploadTab {
	background: transparent;
	border: 1px solid #D1D5DB;
	padding: 4px 10px;
	min-width: 90px;
}
QPushButton#uploadTab:hover {
	background: #F1F5F9;
	border-color: #93C5FD;
}
QPushButton#uploadTab:checked {
	background: #2563EB;
	border-color: #2563EB;
	color: #FFFFFF;
}
QPushButton#uploadTab[tabVariant="pending"]:hover {
	background: #FFFBEB;
	border-color: #F59E0B;
}
QPushButton#uploadTab[tabVariant="uploaded"]:hover {
	background: #ECFDF5;
	border-color: #22C55E;
}
QPushButton#uploadTab[tabVariant="rejected"]:hover {
	background: #FEF2F2;
	border-color: #EF4444;
}
QPushButton#uploadTab[tabVariant="pending"]:checked {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #FEF3C7, stop: 1 #FDE68A);
	border-color: #F59E0B;
	color: #92400E;
}
QPushButton#uploadTab[tabVariant="uploaded"]:checked {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #DCFCE7, stop: 1 #BBF7D0);
	border-color: #4ADE80;
	color: #14532D;
}
QPushButton#uploadTab[tabVariant="rejected"]:checked {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #FEE2E2, stop: 1 #FECACA);
	border-color: #F87171;
	color: #991B1B;
}
QPushButton#themeToggle {
	min-width: 34px;
	max-width: 34px;
	min-height: 34px;
	max-height: 34px;
	border-radius: 17px;
	font-size: 16px;
	font-weight: 700;
	border: 1px solid #C7DAEC;
	background: qlineargradient(
		x1: 0, y1: 0,
		x2: 1, y2: 1,
		stop: 0 #FFF2C6,
		stop: 1 #D8EEFF
	);
	color: #FACC15;
	padding: 0px;
}
QPushButton#themeToggle:checked {
	color: #2B5E8F;
}
QPushButton#themeToggle:hover {
	background: qlineargradient(
		x1: 0, y1: 0,
		x2: 1, y2: 1,
		stop: 0 #FFE9A0,
		stop: 1 #C8E7FF
	);
	border: 1px solid #B8D2EA;
}
QPushButton#themeToggle:pressed {
	background: #DDEEFF;
}
QPushButton#userButton {
	min-height: 38px;
	border-radius: 19px;
	padding: 0 14px;
	font-size: 14px;
	font-weight: 600;
	color: #1F2937;
	background: qlineargradient(
		x1: 0, y1: 0,
		x2: 1, y2: 1,
		stop: 0 #F8FAFC,
		stop: 1 #EEF2FF
	);
	border: 1px solid #CBD5E1;
}
QPushButton#userButton:hover {
	border: 1px solid #94A3B8;
	background: qlineargradient(
		x1: 0, y1: 0,
		x2: 1, y2: 1,
		stop: 0 #F1F5F9,
		stop: 1 #E2E8F0
	);
}
QPushButton#userButton:pressed {
	background: #E2E8F0;
}
QLineEdit#compactInput, QDateEdit#compactInput, QSpinBox#compactInput, QComboBox#compactInput {
	background: #FFFFFF;
	color: #111827;
	border: 1px solid #D1D5DB;
	border-radius: 10px;
	padding: 6px 8px;
}
QHeaderView::section {
	background: #DDEEFF;
	color: #6B7280;
	border: 1px solid #E5E7EB;
	padding: 8px;
}

QLabel#preview {
	border: 1px dashed #9CA3AF;
	border-radius: 10px;
	color: #6B7280;
}
QLabel#previewRecording {
	border: 2px solid #DC2626;
	border-radius: 10px;
	color: #111827;
}

QLabel#avatarWidget {
	background: #EFF6FF;
	border: 1px solid #BFDBFE;
	border-radius: 24px;
	font-size: 18px;
	font-weight: 700;
	color: #1D4ED8;
}
QLabel#profileKey {
	color: #6B7280;
	font-size: 13px;
	background: transparent;
}
QLabel#profileValue {
	color: #111827;
	font-size: 13px;
	font-weight: 500;
}
QFrame#profileHeaderCard {
	background: transparent;
	border: 1px solid #E5E7EB;
	border-radius: 12px;
}
QFrame#profileFormCard {
	background: transparent;
	border: 1px solid #E5E7EB;
	border-radius: 12px;
}
QFrame#profileHeaderCard QLabel,
QFrame#profileFormCard QLabel {
	background: transparent;
}
QLabel#profileAvatar {
	background: #ECFEFF;
	border: 1px solid #BAE6FD;
	border-radius: 26px;
	font-size: 20px;
	font-weight: 800;
	color: #0F766E;
}
QLineEdit#profileField {
	background: #FFFFFF;
	color: #111827;
	border: 1px solid #D1D5DB;
	border-radius: 10px;
	padding: 6px 8px;
}
QLineEdit#profileField:read-only {
	background: #FFFFFF;
	color: #475569;
}
QLabel#hospitalIcon {
	padding: 2px;
}

QLabel#addPreviewAvatar {
	background: #EFF6FF;
	border: 1px solid #BFDBFE;
	border-radius: 23px;
	font-size: 16px;
	font-weight: 700;
	color: #1D4ED8;
}

QFrame#uploadCard {
	background: #FFFFFF;
	border: 1px solid #E5E7EB;
	border-radius: 10px;
}
QFrame#uploadCard:hover {
	border: 1px solid #93C5FD;
}
QFrame#uploadCard[status="pending"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #FFFBEB, stop: 1 #FEF3C7);
	border: 1px solid #F59E0B;
}
QFrame#uploadCard[status="pending"]:hover {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #FFF7D6, stop: 1 #FDE68A);
	border: 1px solid #D97706;
}
QFrame#uploadCard[status="uploading"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #ECFDF5, stop: 1 #DCFCE7);
	border: 1px solid #22C55E;
}
QFrame#uploadCard[status="uploading"]:hover {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #DCFCE7, stop: 1 #BBF7D0);
	border: 1px solid #16A34A;
}
QFrame#uploadCard[status="rejected"] {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #FEF2F2, stop: 1 #FEE2E2);
	border: 1px solid #EF4444;
}
QFrame#uploadCard[status="rejected"]:hover {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #FEE2E2, stop: 1 #FECACA);
	border: 1px solid #DC2626;
}
QFrame#patientsTopBar {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #DBEAFE, stop: 1 #DCFCE7);
	border: 1px solid #93C5FD;
	border-radius: 12px;
}
QFrame#patientsTablePanel, QFrame#patientsListPanel {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #EFF6FF, stop: 1 #ECFEFF);
	border: 1px solid #BFDBFE;
	border-radius: 12px;
}
QFrame#patientsDirectoryHeader {
	background: #FFFFFF;
	border: 1px solid #E5E7EB;
	border-radius: 12px;
}
QLabel#patientsDirectoryTitle {
	font-size: 24px;
	font-weight: 800;
	color: #0F172A;
	background: transparent;
}
QLabel#patientsDirectorySubtitle {
	font-size: 13px;
	font-weight: 500;
	color: #475569;
	background: transparent;
}
QPushButton#sortChip {
	min-height: 28px;
	padding: 0 12px;
	border-radius: 14px;
	background: #F8FAFC;
	border: 1px solid #E2E8F0;
	color: #475569;
	font-weight: 700;
}
QPushButton#sortChip:hover {
	background: #F1F5F9;
	border: 1px solid #94A3B8;
	color: #334155;
}
QPushButton#sortChip:checked {
	background: #ECFEFF;
	border: 1px solid #99F6E4;
	color: #0F766E;
}
QScrollArea#patientsListScroll {
	background: transparent;
	border: none;
}
QScrollArea#patientsListScroll > QWidget > QWidget {
	background: transparent;
}
QFrame#patientListCard {
	background: #FFFFFF;
	border: 1px solid #E5E7EB;
	border-radius: 14px;
}
QFrame#patientListCard:hover {
	background: #F8FBFF;
	border: 1px solid #93C5FD;
}
QLabel#patientAvatar {
	background: #ECFEFF;
	border-radius: 18px;
	font-size: 17px;
	font-weight: 800;
	color: #0F766E;
}
QLabel#patientName {
	font-size: 18px;
	font-weight: 800;
	color: #111827;
	background: transparent;
}
QLabel#patientMeta {
	font-size: 12px;
	font-weight: 500;
	color: #475569;
	background: transparent;
}
QLabel#patientRowChevron {
	font-size: 20px;
	font-weight: 700;
	color: #64748B;
	background: transparent;
}
QPushButton#patientActionButton {
	min-height: 28px;
	min-width: 86px;
	padding: 0 12px;
	border-radius: 12px;
	font-size: 11px;
	font-weight: 700;
	background: #F8FAFC;
	border: 1px solid #D1D5DB;
	color: #334155;
}
QPushButton#patientActionButton:hover {
	background: #F1F5F9;
	border: 1px solid #94A3B8;
}
QPushButton#patientActionButton[variant="record"] {
	background: #ECFDF5;
	border: 1px solid #34D399;
	color: #065F46;
}
QPushButton#patientActionButton[variant="record"]:hover {
	background: #D1FAE5;
	border: 1px solid #10B981;
	color: #064E3B;
}
QPushButton#patientActionButton[variant="upload"] {
	background: #EFF6FF;
	border: 1px solid #93C5FD;
	color: #1D4ED8;
}
QPushButton#patientActionButton[variant="upload"]:hover {
	background: #DBEAFE;
	border: 1px solid #60A5FA;
	color: #1E40AF;
}
QPushButton#patientsFab {
	min-width: 46px;
	max-width: 46px;
	min-height: 46px;
	max-height: 46px;
	border-radius: 23px;
	font-size: 24px;
	font-weight: 700;
	background: #0F172A;
	border: 1px solid #1E293B;
	color: #FFFFFF;
}
QFrame#uploadsTopBar {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #DBEAFE, stop: 1 #DCFCE7);
	border: 1px solid #93C5FD;
	border-radius: 12px;
}
QFrame#uploadsStatsPanel {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #F8FBFF, stop: 1 #EEF6FF);
	border: 1px solid #BFDBFE;
	border-radius: 12px;
}
QFrame#uploadsListPanel {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #EFF6FF, stop: 1 #ECFEFF);
	border: 1px solid #BFDBFE;
	border-radius: 12px;
}
QScrollArea#uploadsScroll {
	background: transparent;
	border: none;
}
QScrollArea#uploadsScroll > QWidget > QWidget {
	background: transparent;
}
QFrame#addPatientTopBar {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #DBEAFE, stop: 1 #DCFCE7);
	border: 1px solid #93C5FD;
	border-radius: 12px;
}
QFrame#addPatientFormPanel {
	background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #EFF6FF, stop: 1 #ECFEFF);
	border: 1px solid #BFDBFE;
	border-radius: 12px;
}
QLabel#formLabel {
	background: transparent;
	color: #1E3A8A;
	font-weight: 600;
	font-size: 14px;
}
QLineEdit#searchBar {
	min-height: 34px;
	border-radius: 10px;
	padding: 0 10px;
	background: #FFFFFF;
	border: 1px solid #93C5FD;
	color: #0F172A;
	selection-background-color: #BFDBFE;
}
QLineEdit#searchBar:focus {
	border: 1px solid #3B82F6;
}
QTableWidget#patientTable {
	background: #FFFFFF;
	alternate-background-color: #F0F9FF;
	border: 1px solid #BFDBFE;
	border-radius: 10px;
	gridline-color: #DBEAFE;
	selection-background-color: #DBEAFE;
	selection-color: #0F172A;
}
QTableWidget#patientTable::item {
	padding: 8px;
	border-bottom: 1px solid #DBEAFE;
}
QTableWidget#patientTable QHeaderView::section {
	background: #E0F2FE;
	color: #1E3A8A;
	font-weight: 700;
	border: 1px solid #BFDBFE;
	padding: 8px;
}
QLabel#uploadPatientName {
	font-size: 13px;
	font-weight: 600;
	color: #111827;
	background: transparent;
}
QLabel#uploadMeta {
	font-size: 11px;
	color: #6B7280;
	background: transparent;
}
QLabel#uploadBadgePending {
	border: 1px solid #EAB308;
	color: #B45309;
	background: transparent;
	border-radius: 9px;
	padding: 1px 7px;
}
QLabel#uploadBadgeUploaded {
	border: 1px solid #16A34A;
	color: #FFFFFF;
	background: #16A34A;
	border-radius: 9px;
	padding: 1px 7px;
}
QLabel#uploadBadgeRejected {
	border: 1px solid #DC2626;
	color: #DC2626;
	background: transparent;
	border-radius: 9px;
	padding: 1px 7px;
}
"""

# Backward-compatible export for existing imports.
STYLE_SHEET = DARK_STYLE_SHEET
