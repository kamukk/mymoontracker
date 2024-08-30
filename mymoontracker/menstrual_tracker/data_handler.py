import json
import datetime
import pytz
from tkinter import messagebox
from constants import ADVICE_FILE, USER_DATA_FILE
import os

class DataHandler:
    def __init__(self):
        self.advice_file = ADVICE_FILE
        self.user_data_file = USER_DATA_FILE

    def load_advice_from_file(self):
        """Load advice from the JSON file."""
        try:
            with open(self.advice_file, 'r', encoding='utf-8') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            messagebox.showerror("Error", "Moon cycles readings file not found.")
            return {}
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error reading moon cycles readings JSON file.")
            return {}

    def load_user_data(self):
        """Load user cycle data from the JSON file."""
        try:
            with open(self.user_data_file, 'r', encoding='utf-8') as json_file:
                cycle_data_json = json.load(json_file)
                cycle_data = []

                if isinstance(cycle_data_json, list):  # Ensure data is a list
                    for item in cycle_data_json:
                        if isinstance(item, dict) and 'date' in item and 'time_zone' in item and 'cycle_type' in item:
                            try:
                                start_date = datetime.datetime.strptime(item['date'], '%Y-%m-%d %H:%M:%S')
                                time_zone = pytz.timezone(item['time_zone'])
                                localized_date = time_zone.localize(start_date)
                                cycle_type = item['cycle_type']
                                cycle_data.append((localized_date, time_zone, cycle_type))
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

    def save_user_data(self, cycle_data):
        """Save user cycle data to the JSON file."""
        try:
            cycle_data_json = [
                {
                    'date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'time_zone': time_zone.zone,
                    'cycle_type': cycle_type
                } for start_date, time_zone, cycle_type in cycle_data
            ]
            with open(self.user_data_file, 'w', encoding='utf-8') as json_file:
                json.dump(cycle_data_json, json_file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving data: {e}")

    def load_description_from_file(self, file_name):
        """Load and return the content of a text file."""
        try:
            file_path = os.path.join("data", file_name)  # Ensure the correct directory is used
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return "Description file not found."
        except Exception as e:
            return f"Error loading description: {e}"
