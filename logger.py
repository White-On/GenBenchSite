import logging
import time
from pathlib import Path

from rich.logging import RichHandler

logger = logging.getLogger(__name__)

logs_path = Path(__file__).parent / "logs"
logs_path.mkdir(exist_ok=True)
# logs_path = Path(__file__).parent

file_name = f"debug_{time.strftime('%d_%m_%H_%M_%S')}.log"
# we don't want the logs to over populate the folder
# so we delete the odler logs
for file in logs_path.glob("*.log"):
    # file.unlink()
    print(file)

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
