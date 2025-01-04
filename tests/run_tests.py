import subprocess
import sys
import webbrowser
import os
from pathlib import Path

def run_tests():
    """Run pytest with coverage and open report"""
    try:
        # Run tests with coverage
        subprocess.run([
            sys.executable,  # Use system's Python interpreter
            "-m", 
            "pytest",
            "--cov=.",
            "tests/",
            "--cov-report=html"
        ], check=True)

        # Open coverage report in default browser
        report_path = Path("htmlcov/index.html").absolute().as_uri()
        webbrowser.open(report_path)

    except subprocess.CalledProcessError as e:
        print("Error running tests: {}".format(e))
        sys.exit(1)
    except Exception as e:
        print("Unexpected error: {}".format(e))
        sys.exit(1)

if __name__ == "__main__":
    run_tests()