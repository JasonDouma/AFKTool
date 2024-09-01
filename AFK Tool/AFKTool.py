from PyQt5 import QtCore, QtGui, QtWidgets
import os
import configparser
import time as T
import keyboard
import threading

# Variables
current_script_path = os.path.abspath(__file__)
profile_options_dir = os.path.abspath(os.path.join(current_script_path, "..", "Profile-Settings"))  # Path to profile settings dir
selected_ini_file = None
commands_dict = {}  # Dictionary to store commands
preferences_dict = {}  # Dictionary to store preferences
time_to_wait = float(0.00)
running = False

class run_thread(QtCore.QObject):
    finished = QtCore.pyqtSignal()  # Signal to notify when the thread finishes

    def __init__(self):
        super().__init__()
        self.stop_thread = False
        self.running = False
        self.thread = None
        self.time_to_wait = 0  # Initialize time_to_wait

    def run_func(self):
        # Countdown loop
        for t in range(int(self.time_to_wait), -1, -1):
            print(f"\nrunning in: {t} Seconds.")
            T.sleep(1)
            if t == 0:
                self.running = True
                print("\nreading commands and preferences...")
                print("success!")
            if self.stop_thread:
                print("\nThread stopped during countdown.")
                return

        # Main loop to keep the movement active
        while self.running:
            time_delay = float(preferences_dict.get('time_delay', 0))
            hold_key_time = float(preferences_dict.get('hold_key_time', 0))
            for key, value in commands_dict.items():
                if self.stop_thread:
                    print("\nThread stopped.")
                    self.running = False
                    self.finished.emit()
                    return

                keyboard.press(value)
                T.sleep(hold_key_time)
                keyboard.release(value)
                T.sleep(time_delay)

        self.finished.emit()  # Emit signal when done

    def start(self):
        self.stop_thread = False
        self.thread = threading.Thread(target=self.run_func)
        self.thread.start()

    def stop(self):
        self.stop_thread = True
        self.running = False
        if self.thread is not None:
            self.thread.join()  # Wait for the thread to finish
            self.thread = None
        print('\nending process.')

MyThread = run_thread()
    
def read_ini_file(file_path):
    """Read the ini file and return the commands and preferences as dictionaries."""
    config = configparser.ConfigParser()
    config.read(file_path)

    global commands_dict, preferences_dict
    commands_dict.clear()  # Clear previous commands
    preferences_dict.clear()  # Clear previous preferences

    # Read commands section
    if 'commands' in config:
        commands = config['commands']
        commands_dict.update({key: value for key, value in commands.items()})
        print("Commands loaded:", commands_dict)
    else:
        print("The 'commands' section is missing in the ini file.")
    
    # Read preferences section
    if 'preferences' in config:
        preferences = config['preferences']
        preferences_dict.update({key: value for key, value in preferences.items()})
        print("Preferences loaded:", preferences_dict)
    else:
        print("The 'preferences' section is missing in the ini file.")

def error(command):
    print(f"Showing error: {command}")

def button_click(command):
    print(f"{command} command was fired!")
    if command == "open-settings":
        os.startfile(profile_options_dir)  # Opens profile settings dir
    elif command == "submit-combo":
        print(f'Selecting file: {selected_ini_file}')
        # Print all commands and preferences from the selected ini file
        print("Commands:", commands_dict)
        print("Preferences:", preferences_dict)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(401, 358)
        MainWindow.setWindowOpacity(1.0)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.title_lbl = QtWidgets.QLabel(self.centralwidget)
        self.title_lbl.setGeometry(QtCore.QRect(-500, 20, 511, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe MDL2 Assets")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.title_lbl.setFont(font)
        self.title_lbl.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.title_lbl.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.title_lbl.setObjectName("title_lbl")
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(6, 0, 391, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setAutoFillBackground(False)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("title")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(60, 210, 281, 111))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.profile_options = QtWidgets.QComboBox(self.frame)
        self.profile_options.setGeometry(QtCore.QRect(30, 40, 141, 22))
        self.profile_options.setMaxVisibleItems(100)
        self.profile_options.setObjectName("profile_options")
        self.profile_options.currentIndexChanged.connect(self.load_selected_ini_file)  # Load selected .ini file
        self.selected_profile = QtWidgets.QLabel(self.frame)
        self.selected_profile.setGeometry(QtCore.QRect(0, 10, 281, 20))
        self.selected_profile.setAlignment(QtCore.Qt.AlignCenter)
        self.selected_profile.setObjectName("selected_profile")
        self.openfolder = QtWidgets.QPushButton("Open Settings Folder", self.frame)
        self.openfolder.setGeometry(QtCore.QRect(10, 80, 131, 23))
        self.openfolder.setObjectName("openfolder")
        self.openfolder.clicked.connect(lambda: button_click("open-settings"))
        self.refresh_folder = QtWidgets.QPushButton("Refresh Profiles", self.frame)
        self.refresh_folder.setGeometry(QtCore.QRect(140, 80, 131, 23))
        self.refresh_folder.setObjectName("refresh_folder")
        self.refresh_folder.clicked.connect(self.scan_ini_files_and_add_to_combo_box)  # Refresh button click handler
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(60, 60, 281, 131))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.label = QtWidgets.QLabel(self.frame_2)
        self.label.setGeometry(QtCore.QRect(0, 10, 281, 20))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setKerning(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton("Start Running", self.frame_2)
        self.pushButton.setGeometry(QtCore.QRect(70, 80, 131, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.return_time)  # Start button
        self.lineEdit = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit.setGeometry(QtCore.QRect(72, 50, 131, 20))
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit.setObjectName("lineEdit")
        self.stop_running = QtWidgets.QPushButton(self.frame_2)
        self.stop_running.setGeometry(QtCore.QRect(70, 110, 131, 23))
        self.stop_running.setObjectName("stop_running")
        self.stop_running.clicked.connect(MyThread.stop)  # Stop buttons
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.status_lbl = QtWidgets.QLabel(self.frame_2)
        self.status_lbl.setEnabled(True)
        self.status_lbl.setVisible(False)
        self.status_lbl.setGeometry(QtCore.QRect(0, 110, 281, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.status_lbl.setFont(font)
        self.status_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.status_lbl.setObjectName("status_lbl")
        self.donate_lbl = QtWidgets.QLabel(self.centralwidget)
        self.donate_lbl.setGeometry(QtCore.QRect(110, 30, 181, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.donate_lbl.setFont(font)
        self.donate_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.donate_lbl.setObjectName("donate_lbl")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 401, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Initial load of .ini files
        self.scan_ini_files_and_add_to_combo_box()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AFK Tool"))
        self.title_lbl.setText(_translate("MainWindow", "AFK Tool"))
        self.title.setText(_translate("MainWindow", "AFK Tool"))
        self.selected_profile.setText(_translate("MainWindow", "Selected Profile: NONE"))
        self.openfolder.setText(_translate("MainWindow", "Open Settings Folder"))
        self.refresh_folder.setText(_translate("MainWindow", "Refresh Profiles"))
        self.label.setText(_translate("MainWindow", "Start"))
        self.pushButton.setText(_translate("MainWindow", "Start Running"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Seconds to wait"))
        self.status_lbl.setText(_translate("MainWindow", "Success: Program is running"))
        self.donate_lbl.setText(_translate("MainWindow", "Donation link is on GitHub!"))
        self.stop_running.setText(_translate("MainWindow", "stop running"))

    def return_time(self):
        global time_to_wait
        time_to_wait = float(self.lineEdit.text())  # Convert to float
        MyThread.time_to_wait = time_to_wait  # Update the time_to_wait in MyThread instance
        MyThread.start()  # Correctly call the start method

    def scan_ini_files_and_add_to_combo_box(self):
        # Clear existing items before re-populating
        self.profile_options.clear()

        # Check if the directory exists
        if not os.path.exists(profile_options_dir):
            print(f"Directory {profile_options_dir} does not exist.")
            return

        # Get the list of .ini files in the profile options directory
        ini_files = [f for f in os.listdir(profile_options_dir) if f.lower().endswith('.ini')]

        # Add files to the combo box
        if ini_files:
            self.profile_options.addItems(ini_files)
            print("Found .ini files:", ini_files)
        else:
            print("No .ini files found.")

    def load_selected_ini_file(self):
        global selected_ini_file, commands_dict, preferences_dict
        selected_ini_file = self.profile_options.currentText()

        if selected_ini_file:
            file_path = os.path.join(profile_options_dir, selected_ini_file)
            if os.path.isfile(file_path):
                print(f"Loading .ini file: {file_path}")
                read_ini_file(file_path)
                self.selected_profile.setText(f"Selected Profile: {selected_ini_file}")
                print(f"Selected Profile: {selected_ini_file}")
                print("Commands:", commands_dict)
                print("Preferences:", preferences_dict)
            else:
                print(f"File not found: {file_path}")
                self.selected_profile.setText("Selected Profile: NONE")
                commands_dict.clear()
                preferences_dict.clear()
                print("Cleared commands and preferences dictionaries.")
        else:
            print("No .ini file selected.")
            commands_dict.clear()
            preferences_dict.clear()
            print("Cleared commands and preferences dictionaries.")

def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()