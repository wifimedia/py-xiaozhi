@echo off
@chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🧹 Starting code formatting...

echo 🔧 Checking and installing dependency packages...
python -m pip install --upgrade pip >nul
python -m pip install autoflake docformatter isort black flake8 >nul

echo 📦 Key Definitions

:: Define the target folders and files to be formatted.
set TARGETS=src/ scripts/ hooks/ main.py

echo 📁 Formatting targets: %TARGETS%
echo.

:: Remove unused imports and variables
echo 1️⃣ Removing unused imports and variables...
python -m autoflake -r --in-place --remove-unused-variables --remove-all-unused-imports --ignore-init-module-imports %TARGETS%

:: Fix docstring formatting
echo 2️⃣ Formatting docstrings...
python -m docformatter -r -i --wrap-summaries=88 --wrap-descriptions=88 --make-summary-multi-line %TARGETS%

:: Automatically sort imports
echo 3️⃣ Sorting import statements...
python -m isort %TARGETS%

:: Automatically format code
echo 4️⃣ Formatting code...
python -m black %TARGETS%

:: Static code analysis
echo 5️⃣ Static code analysis...
python -m flake8 %TARGETS%

echo.
echo ✅ Code formatting complete!
echo 📊 Targets processed: %TARGETS%
Gửi ý kiến phản hồi

endlocal
