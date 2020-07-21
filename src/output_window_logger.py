"""
This module provides a class to have a logger object for the textEdit attached to the main UI.
This makes sure that the logger allow all modules to log to the same widget and since the
logger would be initialized ONLY in the main Widget, that takes cares of the construction and the
destruction as well.
"""


class OutputWindowLogger(object):
    def __init__(self, output_window=None):
        if output_window is None:
            print "No Output Log window found."

        # Variable to hold the output log object on the UI
        self.output_window = (
            output_window
        )

    def update_output_window(self, message):
        """
        This is a convenient method that allows to update the output console on the UI.

        :param message: Message that needs to be added to the console.
        """
        self.output_window.append(">>> {0}".format(message))

    def clear_output_window(self):
        """
        This allows to clean up the Output Window.

        :return string: Returns what was cleaned from the output window
        """
        deleted_text = self.output_window.toPlainText()
        print "DELETING - {0}".format(deleted_text)
        self.output_window.setPlainText("")

        return deleted_text
