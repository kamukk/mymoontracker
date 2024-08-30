import tkinter as tk
from tkinter import messagebox
import ephem
import datetime
import pytz
import json
import os


# Function to determine the moon phase based on date and user's time zone
def moon_phase(date, time_zone):
    observer = ephem.Observer()
    observer.date = date.astimezone(pytz.utc)
    moon = ephem.Moon(observer)
    phase_degrees = moon.phase

    if phase_degrees == 0:
        return "New moon"
    elif 0 < phase_degrees < 45:
        return "Waxing crescent"
    elif 45 <= phase_degrees < 90:
        return "First quarter"
    elif 90 <= phase_degrees < 135:
        return "Waxing gibbous"
    elif 135 <= phase_degrees < 180:
        return "Full moon"
    elif 180 <= phase_degrees < 225:
        return "Waning gibbous"
    elif 225 <= phase_degrees < 270:
        return "Last quarter"
    elif 270 <= phase_degrees < 315:
        return "Waning crescent"
    else:
        return "New moon"


# Function to determine the menstrual cycle type based on the moon phase
def menstrual_cycle_type(phase):
    if phase in ["New moon", "Waxing crescent"]:
        return "Red Moon Cycle"
    elif phase in ["Full moon", "Waning gibbous"]:
        return "White Moon Cycle"
    elif phase in ["First quarter", "Waxing gibbous"]:
        return "Pink Moon Cycle"
    elif phase in ["Last quarter", "Waning crescent"]:
        return "Purple Moon Cycle"
    else:
        return "Unknown Cycle"


class MenstrualCalendarGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Menstrual Cycle Tracker")

        # Labels and Entry fields
        self.label_date = tk.Label(root, text="Enter cycle start date (YYYY-MM-DD HH:MM):")
        self.label_date.pack()

        self.entry_date = tk.Entry(root)
        self.entry_date.pack()

        self.label_time_zone = tk.Label(root, text="Enter your time zone (e.g., Europe/Vilnius):")
        self.label_time_zone.pack()

        self.entry_time_zone = tk.Entry(root)
        self.entry_time_zone.pack()

        # Buttons
        self.button_add = tk.Button(root, text="Add Cycle", command=self.add_cycle)
        self.button_add.pack()

        self.button_edit = tk.Button(root, text="Edit Selected Cycle", command=self.edit_cycle)
        self.button_edit.pack()

        self.button_delete = tk.Button(root, text="Delete Selected Cycle", command=self.delete_cycle)
        self.button_delete.pack()

        # Listbox to display cycles
        self.listbox_cycles = tk.Listbox(root)
        self.listbox_cycles.pack()

        # Textbox for displaying advice
        self.text_output = tk.Text(root, height=10, width=50)
        self.text_output.pack()

        # File paths
        self.advice_file = 'mooncycles_readings.json'
        self.user_data_file = 'user_cycles_data.json'

        # Load data
        self.cycle_advice = self.load_advice_from_file()
        self.cycle_data = self.load_user_data()

        # Populate the listbox
        self.populate_listbox()

    def load_advice_from_file(self):
        try:
            with open(self.advice_file, 'r', encoding='utf-8') as json_file:
                advice_json = json.load(json_file)
                if isinstance(advice_json, dict):
                    return advice_json
                else:
                    raise ValueError("JSON file must contain a dictionary.")
        except FileNotFoundError:
            messagebox.showerror("Error", "Advice file not found.")
            return {}
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error reading advice JSON file.")
            return {}
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
            return {}

    def load_user_data(self):
        """Load user cycle data from the JSON file."""
        try:
            with open(self.user_data_file, 'r', encoding='utf-8') as json_file:
                cycle_data_json = json.load(json_file)
                cycle_data = []

                if isinstance(cycle_data_json, list):  # Ensure data is a list
                    for item in cycle_data_json:
                        if isinstance(item, dict) and 'date' in item and 'time_zone' in item:
                            try:
                                start_date = datetime.datetime.strptime(item['date'], '%Y-%m-%d %H:%M:%S')
                                time_zone = pytz.timezone(item['time_zone'])
                                localized_date = time_zone.localize(start_date)
                                cycle_data.append((localized_date, time_zone))
                            except (ValueError, pytz.UnknownTimeZoneError) as e:
                                # Ignore invalid date or time zone and continue
                                messagebox.showwarning("Warning", f"Error processing date or time zone: {e}")
                        else:
                            # Ignore invalid entries
                            messagebox.showwarning("Warning", "Found invalid entry in user data JSON.")

                return cycle_data
        except FileNotFoundError:
            # If the file is not found, return an empty list
            return []
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error reading user data JSON file.")
            return []
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            return []

    def save_user_data(self):
        """Save user cycle data to the JSON file."""
        try:
            cycle_data_json = [
                {
                    'date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'time_zone': time_zone.zone
                } for start_date, time_zone in self.cycle_data
            ]
            with open(self.user_data_file, 'w', encoding='utf-8') as json_file:
                json.dump(cycle_data_json, json_file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving data: {e}")

    def get_advice_for_date(self, date, time_zone):
        """Get advice based on the menstrual cycle type for the given date and time zone."""
        phase = moon_phase(date, time_zone)  # Get the moon phase
        cycle_type = menstrual_cycle_type(phase)  # Get the menstrual cycle type

        # Get advice from the loaded JSON based on cycle type
        advice_data = self.cycle_advice.get(cycle_type)

        if advice_data:
            # Load description from the file specified in the JSON
            description_file = advice_data.get("description")
            description = self.load_description_from_file(description_file)

            recommendations = advice_data.get("recommendations", [])
            advice = "\n".join(recommendations) if recommendations else "No recommendations available."

            # Combine description and recommendations
            full_advice = f"{description}\n\nRecommendations:\n{advice}" if description else advice
        else:
            full_advice = "No advice available for this cycle type."

        return full_advice

    def load_description_from_file(self, file_name):
        """Load and return the content of a text file."""
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return "Description file not found."
        except Exception as e:
            return f"Error loading description: {e}"

    def add_cycle(self):
        try:
            # Get user input
            start_date_str = self.entry_date.get()
            time_zone_str = self.entry_time_zone.get()

            # Convert input to datetime and time zone
            time_zone = pytz.timezone(time_zone_str)
            start_date = time_zone.localize(datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M"))

            # Add to listbox and cycle data list
            self.cycle_data.append((start_date, time_zone))
            self.listbox_cycles.insert(tk.END, start_date.strftime('%Y-%m-%d %H:%M:%S'))

            # Save data to file
            self.save_user_data()

            # Display advice
            advice = self.get_advice_for_date(start_date, time_zone)
            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.END, advice)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def edit_cycle(self):
        try:
            # Get the selected cycle
            selected_index = self.listbox_cycles.curselection()
            if not selected_index:
                messagebox.showerror("Error", "No cycle selected.")
                return

            selected_index = selected_index[0]
            selected_date, selected_time_zone = self.cycle_data[selected_index]

            # Get new values from entry fields
            new_start_date_str = self.entry_date.get()
            new_time_zone_str = self.entry_time_zone.get()

            new_time_zone = pytz.timezone(new_time_zone_str)
            new_start_date = new_time_zone.localize(datetime.datetime.strptime(new_start_date_str, "%Y-%m-%d %H:%M"))

            # Update the data in the list
            self.cycle_data[selected_index] = (new_start_date, new_time_zone)
            self.listbox_cycles.delete(selected_index)
            self.listbox_cycles.insert(selected_index, new_start_date.strftime('%Y-%m-%d %H:%M:%S'))

            # Save data to file
            self.save_user_data()

            # Display advice
            advice = self.get_advice_for_date(new_start_date, new_time_zone)
            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.END, advice)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def delete_cycle(self):
        try:
            # Get the selected cycle
            selected_index = self.listbox_cycles.curselection()
            if not selected_index:
                messagebox.showerror("Error", "No cycle selected.")
                return

            selected_index = selected_index[0]

            # Remove from listbox and cycle data list
            self.cycle_data.pop(selected_index)
            self.listbox_cycles.delete(selected_index)

            # Save data to file
            self.save_user_data()

            # Clear the text output
            self.text_output.delete(1.0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def populate_listbox(self):
        """Populate the listbox with cycle data."""
        self.listbox_cycles.delete(0, tk.END)
        for start_date, time_zone in self.cycle_data:
            self.listbox_cycles.insert(tk.END, start_date.strftime('%Y-%m-%d %H:%M:%S'))

    def calculate_days_between_cycles(self):
        """Calculate the number of days between consecutive cycles."""
        if len(self.cycle_data) < 2:
            messagebox.showerror("Error", "Need at least two cycles to calculate days between.")
            return

        self.text_output.delete(1.0, tk.END)

        for i in range(1, len(self.cycle_data)):
            start_date_prev, _ = self.cycle_data[i - 1]
            start_date_current, _ = self.cycle_data[i]

            days_between = (start_date_current - start_date_prev).days
            self.text_output.insert(tk.END, f"Days between cycle {i} and cycle {i + 1}: {days_between} days\n")


# Main program
if __name__ == "__main__":
    root = tk.Tk()
    app = MenstrualCalendarGUI(root)

    # Adding a button to calculate the days between cycles
    button_calculate_days = tk.Button(root, text="Calculate Days Between Cycles",
                                      command=app.calculate_days_between_cycles)
    button_calculate_days.pack()

    root.mainloop()
