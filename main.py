import sys
import requests
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QMessageBox

from data import load_country_data, plot_graphs, save_data_to_excel

class DataApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Veri Analizi Uygulaması")
        self.setGeometry(100, 100, 800, 600)

        self.custom_font = QtGui.QFont("Helvetica", 12)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.country_label = QtWidgets.QLabel("Ülke İsmi:")
        self.country_label.setFont(self.custom_font)
        self.main_layout.addWidget(self.country_label)

        self.country_entry = QtWidgets.QLineEdit(self)
        self.country_entry.setFont(self.custom_font)
        self.country_entry.setPlaceholderText("Ülke ismi girin ve seçin...")
        self.country_entry.textChanged.connect(self.update_country_list)
        self.main_layout.addWidget(self.country_entry)

        self.country_listbox = QtWidgets.QListWidget(self)
        self.country_listbox.setFont(self.custom_font)
        self.country_listbox.itemClicked.connect(self.load_data_from_listbox)
        self.main_layout.addWidget(self.country_listbox)

        self.gsyh_entries = []
        years = [2020, 2021, 2022, 2023]

        for year in years:
            layout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f"{year} GSYH:")
            label.setFont(self.custom_font)
            layout.addWidget(label)

            entry = QtWidgets.QLineEdit(self)
            entry.setFont(self.custom_font)
            entry.setPlaceholderText("Değer girin...")
            entry.setValidator(QtGui.QDoubleValidator(0.99, 99.99, 2))
            layout.addWidget(entry)

            self.gsyh_entries.append(entry)
            self.main_layout.addLayout(layout)

        button_layout = QtWidgets.QHBoxLayout()
        self.save_button = QtWidgets.QPushButton("Kaydet", self)
        self.save_button.setFont(self.custom_font)
        self.save_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.save_button.clicked.connect(self.save_data)
        button_layout.addWidget(self.save_button)

        self.graph_button = QtWidgets.QPushButton("Grafik Oluştur", self)
        self.graph_button.setFont(self.custom_font)
        self.graph_button.setStyleSheet("background-color: #2196F3; color: white;")
        self.graph_button.clicked.connect(self.create_graph)
        button_layout.addWidget(self.graph_button)

        self.main_layout.addLayout(button_layout)

        self.countries = []
        self.load_country_list()

    def load_country_list(self):
        try:
            response = requests.get("https://restcountries.com/v3.1/all")
            countries_data = response.json()
            self.countries = [country['name']['common'] for country in countries_data]
            self.countries.sort()
            self.update_country_list()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ülke listesi yüklenirken hata oluştu: {e}")

    def update_country_list(self):
        search_term = self.country_entry.text().lower()
        filtered_countries = [country for country in self.countries if search_term in country.lower()]

        self.country_listbox.clear()
        self.country_listbox.addItems(filtered_countries)

    def load_data_from_listbox(self, item):
        selected_country = item.text()
        self.country_entry.setText(selected_country)
        self.load_data()

    def load_data(self):
        country = self.country_entry.text()
        self._load_data(country)

    def _load_data(self, country):
        try:
            data = load_country_data(country)

            if data:
                for i, value in enumerate(data):
                    self.gsyh_entries[i].setText(str(value))
            else:
                for entry in self.gsyh_entries:
                    entry.clear()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veri yüklenirken hata oluştu: {e}")

    def save_data(self):
        country = self.country_entry.text()
        gsyh = []

        try:
            for entry in self.gsyh_entries:
                value = float(entry.text())
                gsyh.append(value)

            if not country or len(gsyh) != 4:
                raise ValueError("Ülke ismi ve 4 yıl için GSYH değerleri girilmelidir.")

            save_data_to_excel(country, gsyh)
            QMessageBox.information(self, "Başarılı", "Veri kaydedildi.")
        except ValueError as e:
            QMessageBox.critical(self, "Hata", str(e))

    def create_graph(self):
        try:
            plot_graphs()
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DataApp()
    window.show()
    sys.exit(app.exec())
