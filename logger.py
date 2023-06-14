import logging
from pathlib import Path

from rich.logging import RichHandler

logger = logging.getLogger(__name__)

current_path = Path(__file__).parent.absolute()

shell_file = current_path / "debug.log"

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
