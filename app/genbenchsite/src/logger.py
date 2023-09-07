import logging
import time
from pathlib import Path

from rich.logging import RichHandler

logger = logging.getLogger(__name__)

logs_path = Path("logs")
logs_path.mkdir(exist_ok=True)

date_format = "%m_%d_%H_%M_%S"
max_logs = 10
file_name = f"log_GBS_{time.strftime(date_format)}.log"

# we don't want the logs to over populate the folder
# so we delete the older logs

# we get all the dates of the logs
date_files = [file.name[len("log_GBS_") : -4] for file in logs_path.glob("*.log")]
# sort them
oldest_files_dates = sorted(date_files)[: -max_logs + 1]
# and get the names of the files to delete
oldest_files = [f"log_GBS_{date}.log" for date in oldest_files_dates]
for file in oldest_files:
    (logs_path / file).unlink()

# logs_path = Path(__file__).parent
# file_name = "debug.log"

shell_file = logs_path / file_name

# the handler determines where the logs go: stdout/file
shell_handler = RichHandler()
file_handler = logging.FileHandler(shell_file, mode="w")

logger.setLevel(logging.DEBUG)
shell_handler.setLevel(logging.WARNING)
file_handler.setLevel(logging.DEBUG)

# the formatter determines what our logs will look like
# fmt_shell = "%(levelname)s %(asctime)s %(message)s" # no need level with rich
fmt_shell = "%(asctime)s %(message)s"
fmt_file = (
    "%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)s] %(message)s"
)

shell_formatter = logging.Formatter(fmt_shell)
file_formatter = logging.Formatter(fmt_file)

# here we hook everything together
shell_handler.setFormatter(shell_formatter)
file_handler.setFormatter(file_formatter)

logger.addHandler(shell_handler)
logger.addHandler(file_handler)
