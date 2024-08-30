import datetime
import pytz
import tkinter as tk
from tkinter import messagebox
from lunar_cycles import moon_phase, menstrual_cycle_type
from data_handler import DataHandler
import os

class MenstrualCalendarGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Menstrual Cycle Tracker")

        # Initialize DataHandler to handle file operations
        self.data_handler = DataHandler()

        # Load cycle advice data
        self.cycle_advice = self.data_handler.load_advice_from_file()
        if not self.cycle_advice:
            messagebox.showerror("Error", "Failed to load moon cycles info.")

        # Labels and Entry fields for date and time zone
        self.label_date = tk.Label(root, text="Enter cycle start date (YYYY-MM-DD HH:MM):")
        self.label_date.pack()
        self.entry_date = tk.Entry(root)
        self.entry_date.pack()

        self.label_time_zone = tk.Label(root, text="Enter your time zone (e.g., Europe/Vilnius):")
        self.label_time_zone.pack()
        self.entry_time_zone = tk.Entry(root)
        self.entry_time_zone.pack()

        # Buttons for actions
        self.button_add = tk.Button(root, text="Add Cycle", command=self.add_cycle)
        self.button_add.pack()

        self.button_show_recommendations = tk.Button(root, text="Show Recommendations", command=self.show_recommendations)
        self.button_show_recommendations.pack()

        self.button_edit = tk.Button(root, text="Edit Selected Cycle", command=self.edit_cycle)
        self.button_edit.pack()

        self.button_delete = tk.Button(root, text="Delete Selected Cycle", command=self.delete_cycle)
        self.button_delete.pack()

        self.button_calculate_days = tk.Button(root, text="Calculate Days Between Cycles", command=self.calculate_days_between_cycles)
        self.button_calculate_days.pack()

        self.button_compare_to_average = tk.Button(root, text="Compare to Average Lunar Cycle", command=self.compare_to_average_cycle)
        self.button_compare_to_average.pack()

        self.button_show_cycle_types = tk.Button(root, text="Show Cycle Types", command=self.show_cycle_types)
        self.button_show_cycle_types.pack()

        # Listbox to display cycles
        self.listbox_cycles = tk.Listbox(root)
        self.listbox_cycles.pack()

        # Textbox for displaying advice and recommendations
        self.text_output = tk.Text(root, height=15, width=100, wrap=tk.WORD)
        self.text_output.pack()

        # Load user data and populate the listbox
        self.cycle_data = self.data_handler.load_user_data()
        self.populate_listbox()

        # Variable to store the latest cycle type
        self.latest_cycle_type = None

    def add_cycle(self):
        # Get user input
        start_date_str = self.entry_date.get()
        time_zone_str = self.entry_time_zone.get()

        try:
            # Parse date and time zone
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M')
            time_zone = pytz.timezone(time_zone_str)
            localized_date = time_zone.localize(start_date)

            # Determine moon phase and cycle type
            moon_phase_name = moon_phase(localized_date, time_zone)
            cycle_type = menstrual_cycle_type(moon_phase_name)
            self.latest_cycle_type = cycle_type

            # Add cycle to data and update UI
            self.cycle_data.append((localized_date, time_zone, cycle_type))
            self.listbox_cycles.insert(tk.END, localized_date.strftime('%Y-%m-%d %H:%M'))

            # Save data to file
            self.data_handler.save_user_data(self.cycle_data)

            # Display cycle type
            self.text_output.insert(tk.END, f"Cycle type: {cycle_type}\n")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def show_recommendations(self):
        if not self.latest_cycle_type:
            messagebox.showwarning("Warning", "No cycle data available.")
            return

        # Display recommendations and description
        cycle_info = self.cycle_advice.get(self.latest_cycle_type, {})
        description_file = cycle_info.get('description')
        recommendations = cycle_info.get('recommendations', [])

        self.text_output.delete(1.0, tk.END)  # Clear previous text

        if description_file:
            description_path = os.path.join('data', description_file)
            if os.path.exists(description_path):
                with open(description_path, 'r', encoding='utf-8') as file:
                    description = file.read()
                self.text_output.insert(tk.END, f"Description:\n{description}\n\n")
            else:
                self.text_output.insert(tk.END, "Description file not found.\n\n")

        self.text_output.insert(tk.END, "Recommendations:\n")
        for rec in recommendations:
            self.text_output.insert(tk.END, f"- {rec}\n")

    def populate_listbox(self):
        self.listbox_cycles.delete(0, tk.END)
        for start_date, _, _ in self.cycle_data:
            self.listbox_cycles.insert(tk.END, start_date.strftime('%Y-%m-%d %H:%M'))

    def edit_cycle(self):
        selected_index = self.listbox_cycles.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "No cycle selected.")
            return

        # Get user input
        start_date_str = self.entry_date.get()
        time_zone_str = self.entry_time_zone.get()

        try:
            # Parse date and time zone
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M")
            time_zone = pytz.timezone(time_zone_str)
            localized_date = time_zone.localize(start_date)

            # Update cycle data
            moon_phase_name = moon_phase(localized_date, time_zone)
            cycle_type = menstrual_cycle_type(moon_phase_name)
            self.cycle_data[selected_index[0]] = (localized_date, time_zone, cycle_type)

            # Update listbox and save data
            self.listbox_cycles.delete(selected_index[0])
            self.listbox_cycles.insert(selected_index[0], localized_date.strftime('%Y-%m-%d %H:%M'))
            self.data_handler.save_user_data(self.cycle_data)

            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.END, f"Cycle type: {cycle_type}\n")

            messagebox.showinfo("Success", "Cycle updated successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def delete_cycle(self):
        selected_index = self.listbox_cycles.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "No cycle selected.")
            return

        # Remove cycle from data and update UI
        del self.cycle_data[selected_index[0]]
        self.listbox_cycles.delete(selected_index[0])
        self.data_handler.save_user_data(self.cycle_data)

        self.text_output.delete(1.0, tk.END)

    def calculate_days_between_cycles(self):
        if len(self.cycle_data) < 2:
            messagebox.showwarning("Warning", "At least two cycles are needed to calculate the differences.")
            return

        self.text_output.delete(1.0, tk.END)

        # Calculate and display the difference between consecutive cycles
        for i in range(1, len(self.cycle_data)):
            date1, _ = self.cycle_data[i - 1][:2]
            date2, _ = self.cycle_data[i][:2]
            days_between = abs((date2 - date1).days)
            self.text_output.insert(tk.END, f"Days between cycle {i} and cycle {i + 1}: {days_between} days\n")

    def compare_to_average_cycle(self):
        if len(self.cycle_data) < 2:
            messagebox.showwarning("Warning", "No cycle data available.")
            return

        total_days = sum(abs((self.cycle_data[i][0] - self.cycle_data[i - 1][0]).days)
                         for i in range(1, len(self.cycle_data)))
        average_cycle_length = total_days / (len(self.cycle_data) - 1)

        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, f"Average cycle length: {average_cycle_length:.2f} days")

    def show_cycle_types(self):
        if not self.cycle_data:
            messagebox.showwarning("Warning", "No cycle data available.")
            return

        self.text_output.delete(1.0, tk.END)
        for start_date, time_zone, cycle_type in self.cycle_data:
            phase = moon_phase(start_date, time_zone)
            self.text_output.insert(tk.END, f"{start_date.strftime('%Y-%m-%d %H:%M')} - {cycle_type} ({phase})\n")


