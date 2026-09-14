import argparse
import asyncio
import locale
import os
import signal
import sys

# Windows: Force the C/C++ runtime to use UTF-8 to prevent garbled text
# when sherpa-onnx reads Pinyin files with tone markers.
if sys.platform == "win32":
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
locale.setlocale(locale.LC_ALL, ".UTF-8")
except locale.Error:
pass

os.environ["QSG_RHI_BACKEND"] = "opengl"
# Force qasync to use PySide6
os.environ["QT_API"] = "pyside6"
# Use the 'Basic' style to support custom controls
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"


def parse_args():
"""Parse command-line arguments."""
from src.constants.system import SystemConstants

parser = argparse.ArgumentParser(description=SystemConstants.APP_DISPLAY_NAME)
# Run mode selection
# - gui: Graphical User Interface mode using PySide6 + QML
# - cli: Command Line Interface mode using terminal interaction (lightweight, suitable for headless/SSH)
# - tui: Full-screen TUI (Textual) with configuration editing capabilities; requires `uv sync --extra tui`
# - gpio: GPIO button mode; Linux (Raspberry Pi) only; controlled via physical buttons
parser.add_argument(
"--mode",
choices=["gui", "cli", "tui", "gpio"],
default="gui",
help="Run mode (default: gui): gui / cli / tui (full-screen terminal) / gpio (Linux only)",
)
parser.add_argument(
"--protocol",
choices=["mqtt", "websocket"],
default="websocket",
metavar="PROTOCOL",
help="Communication protocol: mqtt or websocket (default: websocket; specify --protocol mqtt to use MQTT)",
)
parser.add_argument(
"--skip-activation",
action="store_true",
help="Skip the activation process and launch the app directly (for debugging only)",
)
return parser.parse_args()


# Parse arguments first, then initialize configuration and logging (disable ConfigManager lazy singleton)
_args = parse_args()

from src.utils.config_manager import initialize_config  # noqa: E402

initialize_config()

from src.logging import load_logging_config, setup_logging  # noqa: E402

# Disable console logging output in CLI/TUI modes (handled by the interface)
setup_logging(
enable_console=(_args.mode not in ("cli", "tui")),
config=load_logging_config(),
)

from src.bootstrap.container import ServiceContainer  # noqa: E402
from src.constants.system import SystemConstants  # noqa: E402
from src.logging import get_logger  # noqa: E402

logger = get_logger()


async def handle_activation(mode: str) -> bool:
"""Handle the device activation process.

Args:
mode: Execution mode, "gui", "cli", "tui", or "gpio"

Returns:
bool: Whether activation was successful
"""
try:
from src.activation import ActivationService, create_activation_ui

logger.info("Starting device activation process check...")
activation_service = await ActivationService.create()
init_result = await activation_service.initialize()

if not init_result.get("success", False):
logger.error(f"Initialization failed: {init_result.get('error', 'Unknown error')}")
return False

if not init_result.get("need_activation_ui", False):
logger.info("Device already activated; activation process not required")
return True

ui = create_activation_ui(mode, activation_service, init_result)
return await ui.run()

except Exception as e:
logger.error(f"Exception during activation process: {e}", exc_info=True)
return False


async def start_app(mode: str, protocol: str, skip_activation: bool) -> int:
"""Unified entry point for starting the application."""
global _container  # Used for SIGINT handling logger.info(f"Starting {SystemConstants.APP_DISPLAY_NAME}")

# Handle activation process
if not skip_activation:
activation_success = await handle_activation(mode)
if not activation_success:
logger.error("Device activation failed; program exiting")
return 1
else:
logger.warning("Skipping activation process (debug mode)")

# Create and start the application
_container = ServiceContainer()
return await _container.run(mode=mode, protocol=protocol)


# Global container reference for SIGINT handling
_container = None


if __name__ == "__main__":
exit_code = 1
try:
# Use parsed arguments
args = _args

# Detect Wayland environment and configure Qt platform plugin
import os

is_wayland = (
os.environ.get("WAYLAND_DISPLAY")
or os.environ.get("XDG_SESSION_TYPE") == "wayland"
)

if args.mode == "gui" and is_wayland:
if "QT_QPA_PLATFORM" not in os.environ:
os.environ["QT_QPA_PLATFORM"] = "wayland;xcb"
logger.info("Wayland environment: setting QT_QPA_PLATFORM=wayland;xcb")
os.environ.setdefault("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")
logger.info("Wayland environment detection complete; compatibility configuration applied")

# Signal handling
try:
if hasattr(signal, "SIGTRAP"):
signal.signal(signal.SIGTRAP, signal.SIG_IGN)
except Exception:
pass

if args.mode == "gui":
# GUI mode: using PySide6 + qasync
try:
import qasync
from PySide6.QtWidgets import QApplication
except ImportError as e:
logger.error(
"GUI mode requires PySide6 + qasync, but they are not installed in the current environment.\n"
"Please install GUI dependencies using the project venv and try again:\n"
"  uv sync --extra gui\n"
" # Or: pip install '.[gui]'\n"
"Then:\n"
"  uv run python main.py\n"
"  # Or: .venv/bin/python main.py\n"
"To run without the GUI:\n"
"  python main.py --mode cli\n"
"  python main.py
