""" Handles the entire app """

import os


import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
import pdfplumber
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox  # ignore
from qtui.rpf_ui import Ui_MainWindow

START_TEXT = "(m³/dia) (kgf/cm²) (m)"
END_TEXT = "Temperaturas"


class MainWindow(QMainWindow, Ui_MainWindow):
    """Class that handles the main window"""

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setupUi(self)
        self.setWindowTitle("RFP Extractor")

        self.fileToolButton.clicked.connect(self.copy_file_path)
        self.extractButton.clicked.connect(self.call_extract_rfp)

        self.show()

    def copy_file_path(self):
        """Open file dialog for copying file path"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Open File",
            "uploads",
            "PDF (*.pdf);;All Files (*)",
        )

        if file_path:
            self.fileLineEdit.setText(file_path)

    def call_extract_rfp(self):
        """calls the extract rfp function"""
        well_name = self.wellNameInput.text()
        file_path = self.fileLineEdit.text()
        selected_button = self.hasFluidGroup.checkedButton()
        if selected_button.text() == "Yes":
            self.extract_rfp(well_name, file_path, has_fluid=True)
        if selected_button.text() == "No":
            self.extract_rfp(well_name, file_path, has_fluid=False)

    def extract_rfp(self, wellname, pdf_path, has_fluid=False):
        """extract text from 'Teste de Formação' to 'Temperaturas'"""

        extraction = ""
        start_extracting = False

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if start_extracting:
                        if END_TEXT in text:
                            extraction += text[: text.index(END_TEXT)]
                            break
                        else:
                            extraction += text
                    elif START_TEXT in text:
                        start_extracting = True
                        lines = text.split("\n")
                        for i, line in enumerate(lines):
                            if START_TEXT in line:
                                extraction += "\n".join(lines[i + 1 :])
                                break

                    if page.extract_tables():
                        continue

        except Error as e:
            QMessageBox.critical(None, f"Error extracting text from PDF: {e}")
            return

        extraction = extraction.replace(",", ".").replace(" ", ",")
        rows = extraction.split("\n")

        self.write_to_excel(wellname, rows, has_fluid)

    def write_to_excel(self, wellname, rows, has_fluid=False):
        """Writes to excel"""
        try:
            data = [row.split(",") for row in rows]
            num_columns = max(len(row) for row in data) if data else 0

            if has_fluid is True:
                columns = [
                    "Tipo",
                    "Topo",
                    "Base",
                    "Vazao",
                    "Fluido",
                    "API",
                    "Depl",
                    "Pressao_Estatica",
                    "Prof_Registrada",
                ]
            else:
                columns = [
                    "Tipo",
                    "Topo",
                    "Base",
                    "Vazao",
                    "API",
                    "Depl",
                    "Pressao_Estatica",
                    "Prof_Registrada",
                ]

            # Add generic names for additional columns
            for i in range(len(columns), num_columns):
                columns.append(f"Column_{i+1}")
            df = pd.DataFrame(data, columns=columns)
            # Ask the user for a save location
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save file",
                f"{wellname}.xlsx",
                "Excel Files (*.xlsx)",
                options=options,
            )
            if file_name:
                df.to_excel(file_name, index=False)
        except pd.errors.ParserError as e:
            print(f"Error writing to Excel: {e}")


if __name__ == "__main__":
    appctxt = ApplicationContext()  # 1. Instantiate ApplicationContext
    window = MainWindow()
    window.show()
    exit_code = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
