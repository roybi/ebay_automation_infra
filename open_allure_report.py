import webbrowser
import os

# Get the absolute path to the report
report_path = os.path.abspath(r"reports\allure-report\index.html")

# Open in default browser
print(f"Opening Allure report: {report_path}")
webbrowser.open(f"file:///{report_path}")
print("\nAllure report opened in your default browser!")
