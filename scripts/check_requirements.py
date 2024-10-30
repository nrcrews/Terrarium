import subprocess
import sys

def get_installed_packages():
    try:
        result = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], universal_newlines=True)
        installed_packages = {line.strip().lower() for line in result.splitlines() if line.strip()}
        return installed_packages
    except subprocess.CalledProcessError:
        print("Error retrieving installed packages.")
        sys.exit(1)

def check_requirements():
    try:
        with open('requirements/cli.txt', 'r') as file:
            required_packages = {line.strip().lower() for line in file.readlines() if line.strip()}
    except FileNotFoundError:
        print("Error: requirements/cli.txt not found.")
        sys.exit(1)

    installed_packages = get_installed_packages()

    missing_packages = required_packages - installed_packages

    if missing_packages and len(missing_packages) > 0:
        print("Missing packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("Installing missing packages...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing_packages])
        except subprocess.CalledProcessError:
            print("Error installing missing packages.")
            sys.exit(1)
    else:
        print("All required packages are installed.")

if __name__ == "__main__":
    check_requirements()