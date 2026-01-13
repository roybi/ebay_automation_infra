"""Setup configuration for eBay Automation Framework."""

from setuptools import setup, find_packages

setup(
    name="ebay_automation_infra",
    version="1.0.0",
    description="eBay Automation Testing Framework using Playwright",
    author="Test Automation Team",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests", "tests.*", ".venv", "reports", "logs"]),
    install_requires=[
        "playwright>=1.40.0",
        "pytest>=7.4.0",
        "pytest-playwright>=0.4.0",
        "pytest-xdist>=3.3.0",
        "pytest-html>=3.2.0",
    ],
    extras_require={
        "dev": [
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
