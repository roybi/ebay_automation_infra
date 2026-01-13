import subprocess
import os

os.chdir(r"C:\_Dev\python\ebay_automation_infra")

# Set up environment to avoid path issues
env = os.environ.copy()
# Try using USERPROFILE short name
env['USERPROFILE'] = r'C:\Users\ROYBIC~1'

# Run allure generate command
cmd = [
    "cmd", "/c", "allure",
    "generate",
    r"reports\allure-results_20260113_113527",
    "-o",
    r"reports\allure-report",
    "--clean"
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, shell=False, env=env)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)
    if result.returncode == 0:
        print("\nAllure report generated successfully!")
        print("Report location: reports\\allure-report\\index.html")
    else:
        print("\nFailed to generate report. Trying alternative method...")
        # Alternative: Try using the allure CLI directly with Java
        print("Attempting to use Java-based allure...")
except Exception as e:
    print(f"Error: {e}")
