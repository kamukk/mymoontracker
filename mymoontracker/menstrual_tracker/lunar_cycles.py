import ephem
import pytz

def moon_phase(date, time_zone):
    """Determine the moon phase based on date and user's time zone."""
    observer = ephem.Observer()
    observer.date = date.astimezone(pytz.utc)  # Convert to UTC
    moon = ephem.Moon(observer)
    phase_degrees = moon.phase

    # Determine the moon phase based on the degrees
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
        return "New moon"  # Default to new moon if no conditions match


def menstrual_cycle_type(phase):
    """Determine the menstrual cycle type based on the moon phase."""
    # Match the moon phase to the menstrual cycle type
    if phase in ["New moon", "Waxing crescent"]:
        return "Red Moon Cycle"
    elif phase in ["Full moon", "Waning gibbous"]:
        return "White Moon Cycle"
    elif phase in ["First quarter", "Waxing gibbous"]:
        return "Pink Moon Cycle"
    elif phase in ["Last quarter", "Waning crescent"]:
        return "Purple Moon Cycle"
    else:
        return "Unknown Cycle"  # Default to Unknown Cycle if no conditions match
