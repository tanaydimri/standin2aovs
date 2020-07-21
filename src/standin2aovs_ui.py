# importing builtin modules
import os

# importing third party modules
from shiboken2 import wrapInstance
from PySide2 import QtGui, QtCore, QtUiTools, QtWidgets

# importing project modules
import output_window_logger
import standin2aovs

reload(standin2aovs)

REL_UI_FILE_PATH = "ui\standin2aovs.ui"
CURRENT_APP = "maya"


def get_main_app_window():
    """
    This function gets the pointer to the Maya's Main window.
    Application Widget will be parented under this.
    """
    import maya.OpenMayaUI as omui

    pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(long(pointer), QtWidgets.QWidget)


class Standin2AovsUI(QtWidgets.QDialog):
    def __init__(self, ui_file_path, parent=get_main_app_window()):
        """
        Init method for the class Standin2AovsUI

        :param ui_file_path: Path to the UI File that needs to be loaded.
        :param parent: Parent window under which the given ui widget would be added.
        """
        # Loading and Initialising the UI
        super(Standin2AovsUI, self).__init__(parent)

        loader = QtUiTools.QUiLoader()
        uifile = QtCore.QFile(ui_file_path)
        uifile.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(uifile, parentWidget=self)
        uifile.close()

        # layout = QtWidgets.QGridLayout()
        # self.ui.addWidget(layout)
        # self.setLayout(layout)

        self.default_browse_directory = os.path.normpath(os.path.expanduser("~Desktop"))

        # Defining the Output console object to be used by the other classes or methods
        self.output_window_logger = output_window_logger.OutputWindowLogger(
            self.ui.textEdit_output_field
        )

        # Connecting all UI signals
        self.ui.btn_browse_ass_file.clicked.connect(self.action_browse_btn)
        self.ui.btn_import_aovs.clicked.connect(self.action_import_aovs)

    def action_browse_btn(self):
        """
        Action to be performed when the Browse button in the UI is clicked.
        """
        # Presenting a browser for the user to seelct a file
        selected_file = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Image", self.default_browse_directory, "ArnoldStandins (*.ass)",
        )

        # Setting the currently selected file field text to the selected file
        self.ui.lineEdit_ass_file_path.setText(selected_file[0])
        self.output_window_logger.update_output_window(
            "Updated the Standin file path to - {0}".format(selected_file[0])
        )

    def action_import_aovs(self):
        """
        Action to be performed when the Import Aovs button in the UI is clicked.
        """
        try:
            self.output_window_logger.update_output_window(
                "{0}  Initiating the Import Process  {0}".format("-"*30).upper()
            )

            ass_file_path = self.ui.lineEdit_ass_file_path.text()

            if not os.path.exists(ass_file_path):
                self.output_window_logger.update_output_window(
                    "ERROR: Please select an ASS file to continue."
                )

                return 1

            standin_2_aovs = standin2aovs.Standin2Aovs(
                ass_file_path, self.output_window_logger
            )
            standin_2_aovs.run(CURRENT_APP)
        finally:
            self.output_window_logger.update_output_window(
                "{0}\t    Import Ends\t{0}".format("-"*30).upper()
            )


def get_ui_file():
    """
    Gets the absolute ui file path from the curent project directory

    :return: The absolute file path to the UI file.
    """
    curr_dir = os.path.dirname(__file__)
    return os.path.join(os.path.split(curr_dir)[0], REL_UI_FILE_PATH)


def main():
    """
    Entry point to the application.
    """
    if CURRENT_APP == "maya":
        import mtoa.core

        mtoa.core.createOptions()  # Creates the default Arnold Nodes

    ui_file_path = get_ui_file()

    # If the UI already exists, closes it before proceeding
    global standin2aovs_ui
    try:
        standin2aovs_ui.close()
    except NameError:
        pass

    standin2aovs_ui = Standin2AovsUI(ui_file_path)
    standin2aovs_ui.show()


if __name__ == "__main__":
    main()
