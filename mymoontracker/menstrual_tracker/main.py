import tkinter as tk
from gui import MenstrualCalendarGUI


def main():
    # Create the main application window
    root = tk.Tk()

    # Initialize the MenstrualCalendarGUI class
    app = MenstrualCalendarGUI(root)

    # Adding additional buttons if needed
    button_calculate_days = tk.Button(root, text="Calculate Days Between Cycles",
                                      command=app.calculate_days_between_cycles)
    button_calculate_days.pack()

    # Add a button to show cycle types
    button_show_cycle_types = tk.Button(root, text="Show Cycle Types",
                                        command=app.show_cycle_types)
    button_show_cycle_types.pack()

    # Start the Tkinter main loop
    root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = MenstrualCalendarGUI(root)
    root.mainloop()
