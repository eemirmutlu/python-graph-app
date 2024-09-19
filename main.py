import tkinter as tk
from tkinter import messagebox
import requests
from tkinter import font as tkfont
from data import load_country_data, plot_graphs, save_data_to_excel

class DataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Veri Analizi Uygulaması")
        self.root.geometry("800x600")

        self.custom_font = tkfont.Font(family="Helvetica", size=12)

        self.main_frame = tk.Frame(root, padx=20, pady=20, bg="#f4f4f4")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.main_frame.grid_rowconfigure(5, weight=1)
        self.main_frame.grid_rowconfigure(6, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        tk.Label(self.main_frame, text="Ülke İsmi:", font=self.custom_font, bg="#f4f4f4").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.country_var = tk.StringVar()
        self.country_entry = tk.Entry(self.main_frame, textvariable=self.country_var, font=self.custom_font, width=30)
        self.country_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.country_entry.bind("<KeyRelease>", self.update_country_list)
        self.country_entry.bind("<Return>", self.select_country)

        self.country_listbox = tk.Listbox(self.main_frame, font=self.custom_font, height=6, width=30)
        self.country_listbox.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.country_listbox.bind("<ButtonRelease-1>", self.load_data_from_listbox)

        years = [2020, 2021, 2022, 2023]
        self.gsyh_entries = []
        validate_float = self.root.register(self.validate_float)

        for i in range(4):
            tk.Label(self.main_frame, text=f"{years[i]} GSYH:", font=self.custom_font, bg="#f4f4f4").grid(row=i+2, column=0, padx=10, pady=10, sticky="e")
            entry = tk.Entry(self.main_frame, font=self.custom_font, width=20, validate="key", validatecommand=(validate_float, "%P"))
            entry.grid(row=i+2, column=1, padx=10, pady=10, sticky="w")
            self.gsyh_entries.append(entry)

        tk.Button(self.main_frame, text="Kaydet", command=self.save_data, font=self.custom_font, bg="#4CAF50", fg="white", padx=10, pady=5).grid(row=6, column=0, padx=10, pady=10, sticky="e")
        tk.Button(self.main_frame, text="Grafik Oluştur", command=self.create_graph, font=self.custom_font, bg="#2196F3", fg="white", padx=10, pady=5).grid(row=6, column=1, padx=10, pady=10, sticky="w")

        self.countries = []
        self.load_country_list()

    def validate_float(self, value):
        if value == "" or value.replace('.', '', 1).isdigit():
            return True
        return False

    def load_country_list(self):
        try:
            response = requests.get("https://restcountries.com/v3.1/all")
            countries_data = response.json()
            self.countries = [country['name']['common'] for country in countries_data]
            self.countries.sort()
            self.update_country_list()
        except Exception as e:
            messagebox.showerror("Hata", f"Ülke listesi yüklenirken hata oluştu: {e}")

    def update_country_list(self, event=None):
        search_term = self.country_var.get().lower()
        filtered_countries = [country for country in self.countries if search_term in country.lower()]
        
        self.country_listbox.delete(0, tk.END)
        for country in filtered_countries:
            self.country_listbox.insert(tk.END, country)

    def load_data_from_listbox(self, event):
        selected_country = self.country_listbox.get(tk.ACTIVE)
        self.country_var.set(selected_country)
        self.load_data(None)

    def select_country(self, event):
        selected_country = self.country_var.get()
        if selected_country in self.countries:
            self.load_data(None)
        else:
            messagebox.showerror("Hata", "Geçersiz ülke seçimi")

    def load_data(self, event):
        country = self.country_var.get()
        self.root.after(0, self._load_data, country)

    def _load_data(self, country):
        try:
            data = load_country_data(country)
            
            if data:
                for i, value in enumerate(data):
                    self.gsyh_entries[i].delete(0, tk.END)
                    self.gsyh_entries[i].insert(0, value)
            else:
                for entry in self.gsyh_entries:
                    entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Hata", f"Veri yüklenirken hata oluştu: {e}")

    def save_data(self):
        country = self.country_var.get()
        gsyh = []
        
        try:
            for entry in self.gsyh_entries:
                value = float(entry.get())
                gsyh.append(value)
            
            if not country or len(gsyh) != 4:
                raise ValueError("Ülke ismi ve 4 yıl için GSYH değerleri girilmelidir.")

            save_data_to_excel(country, gsyh)
            messagebox.showinfo("Başarılı", "Veri kaydedildi.")
        except ValueError as e:
            messagebox.showerror("Hata", str(e))

    def create_graph(self):
        try:
            plot_graphs()
            messagebox.showinfo("Başarılı", "Grafik resmi kaydedildi.")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = DataApp(root)
    root.mainloop()
