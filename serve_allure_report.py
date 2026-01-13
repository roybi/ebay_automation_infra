import subprocess
import os
import webbrowser
import time

os.chdir(r"C:\_Dev\python\ebay_automation_infra")

# Try using allure serve command which might work better
cmd = [
    "node",
    r"C:\Users\Roy Bichovsky\AppData\Roaming\npm\node_modules\allure-commandline\bin\allure",
    "serve",
    r"reports\allure-results_20260113_113527"
]

print("Attempting to start Allure report server...")
print("Command:", " ".join(cmd))

try:
    # Start the server process
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)

    # Wait a bit for the server to start
    time.sleep(3)

    # Check if process is still running
    if process.poll() is None:
        print("\nAllure server started successfully!")
        print("The report should open in your browser automatically.")
        print("If not, check http://localhost:port in your browser")
        print("\nPress Ctrl+C to stop the server when done viewing the report.")
        process.wait()
    else:
        stdout, stderr = process.communicate()
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        print("Return code:", process.returncode)

except KeyboardInterrupt:
    print("\nStopping Allure server...")
    process.terminate()
except Exception as e:
    print(f"Error: {e}")
