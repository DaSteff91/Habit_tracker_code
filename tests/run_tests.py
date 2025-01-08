import subprocess
import sys

def run_tests():
    """Run pytest with verbose output"""
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "pytest",
            "-v",
            "tests/"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print("Error running tests: {}".format(e))
        print("\nTry running with pytest directly for more details:")
        print("python -m pytest -v tests/")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()