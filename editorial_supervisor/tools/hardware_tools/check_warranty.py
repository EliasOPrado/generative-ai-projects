from langchain_core.tools import tool

@tool
def check_warranty(serial_number: str) -> str:
    """
    Check the warranty status of a device using its serial number.
    """
    return f"The device with serial {serial_number} is under warranty until Dec 31, 2027."