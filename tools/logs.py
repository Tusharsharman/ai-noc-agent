from pathlib import Path


LOG_FILE = Path("logs/app.log")


def read_logs(lines: int = 50):
    """
    Read the latest application log entries.

    Args:
        lines: Number of latest log lines to return.

    Returns:
        A string containing the latest log entries.
    """

    if not LOG_FILE.exists():
        return "No application log file found."

    try:
        with LOG_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            all_lines = file.readlines()

        if not all_lines:
            return "Application log file is empty."

        return "".join(
            all_lines[-lines:]
        )

    except Exception as exc:
        return f"Unable to read application logs: {exc}"


def get_error_logs(lines: int = 50):
    """
    Return only ERROR and CRITICAL log entries.
    """

    logs = read_logs(lines)

    if (
        logs.startswith("No application")
        or logs.startswith("Unable")
        or logs.startswith("Application log")
    ):
        return logs

    error_lines = []

    for line in logs.splitlines():
        if "ERROR" in line or "CRITICAL" in line:
            error_lines.append(line)

    if not error_lines:
        return "No ERROR or CRITICAL log entries found."

    return "\n".join(error_lines)
