import runpy
from pathlib import Path

# Dynamically determine the path to server2.py
server2_path = Path(__file__).parent.parent / "server_main.py"

# Execute server2.py in the current namespace
runpy.run_path(str(server2_path))

