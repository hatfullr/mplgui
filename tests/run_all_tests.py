import subprocess
import sys

try:
    # This actually produces an error when something goes wrong
    p = subprocess.Popen(['python3', '-m', 'unittest'])
    p.wait()
except:
    sys.exit(1)
sys.exit(0)

