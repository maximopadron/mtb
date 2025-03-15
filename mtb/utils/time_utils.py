import re

def parse_interval(interval_str):
    """
    Parses an interval string (e.g., "1h", "30m", "1h30m5s", "2.5h") and returns the total
    number of seconds as a float.

    Supported units:
      - s: seconds
      - m: minutes (60 seconds)
      - h: hours   (3600 seconds)
      - d: days    (86400 seconds)
      - w: weeks   (604800 seconds)
      - mo: months (2592000 seconds, assuming 30 days per month)

    If no unit is provided, the value is assumed to be in seconds.

    Examples:
      "1h"         -> 3600
      "1h30m"      -> 5400
      "1h30m5s"    -> 5405
      "2.5h"       -> 9000.0

    :param interval_str: The interval string.
    :return: Total seconds as a float.
    :raises ValueError: If the string cannot be parsed.
    """
    # Define conversion factors.
    units = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
        "w": 604800,
        "mo": 2592000,
    }
    
    # The regex ensures that "mo" is matched before a single "m".
    pattern = r"(\d+(?:\.\d+)?)(mo|[smhdw])"
    matches = re.findall(pattern, interval_str.lower())
    
    if not matches:
        # If no units were found, assume the entire string is in seconds.
        try:
            return float(interval_str)
        except Exception as e:
            raise ValueError(f"Invalid interval format: {interval_str}") from e

    total = 0.0
    for value, unit in matches:
        factor = units.get(unit)
        if factor is None:
            raise ValueError(f"Unsupported time unit: {unit}")
        total += float(value) * factor
    return total
