@echo off
echo ========================================
echo Building Single EXE with Nuitka (Fixed)
echo ========================================
echo.

REM Check if Nuitka is installed
python -c "import nuitka" 2>nul
if errorlevel 1 (
    echo Nuitka not found. Installing...
    pip install nuitka
    echo.
)

echo Starting Nuitka compilation...
echo This creates a SINGLE EXE file with ALL builds folder contents
echo May take 10-15 minutes on first run...
echo.

REM Build with Nuitka - Single file mode with explicit file inclusion
python -m nuitka ^
    --onefile ^
    --include-data-files=builds/_x86/TextractorCLI.exe=builds/_x86/TextractorCLI.exe ^
    --include-data-files=builds/_x86/texthook.dll=builds/_x86/texthook.dll ^
    --include-data-files=builds/_x86/LoaderDll.dll=builds/_x86/LoaderDll.dll ^
    --include-data-files=builds/_x86/LocaleEmulator.dll=builds/_x86/LocaleEmulator.dll ^
    --include-data-files=builds/_x86/host.lib=builds/_x86/host.lib ^
    --include-data-files=builds/_x86/pch.lib=builds/_x86/pch.lib ^
    --include-data-files=builds/_x86/text.lib=builds/_x86/text.lib ^
    --include-data-files=builds/_x86/minhook.lib=builds/_x86/minhook.lib ^
    --include-data-files=builds/_x86/StressTest.txt=builds/_x86/StressTest.txt ^
    --include-data-files=builds/_x64/TextractorCLI.exe=builds/_x64/TextractorCLI.exe ^
    --include-data-files=builds/_x64/texthook.dll=builds/_x64/texthook.dll ^
    --include-data-files=builds/_x64/LoaderDll.dll=builds/_x64/LoaderDll.dll ^
    --include-data-files=builds/_x64/LocaleEmulator.dll=builds/_x64/LocaleEmulator.dll ^
    --include-data-files=builds/_x64/host.lib=builds/_x64/host.lib ^
    --include-data-files=builds/_x64/pch.lib=builds/_x64/pch.lib ^
    --include-data-files=builds/_x64/text.lib=builds/_x64/text.lib ^
    --include-data-files=builds/_x64/StressTest.txt=builds/_x64/StressTest.txt ^
    --include-data-files=logo.webp=logo.webp ^
    --include-data-dir=plugins=plugins ^
    --include-data-dir=Translator=Translator ^
    --enable-plugin=tk-inter ^
    --include-package=pystray ^
    --include-package=PIL ^
    --include-package=psutil ^
    --include-package=requests ^
    --include-package=bs4 ^
    --include-package=win32gui ^
    --include-package=win32ui ^
    --include-package=win32con ^
    --include-package=win32api ^
    --include-package=win32process ^
    --follow-imports ^
    --assume-yes-for-downloads ^
    --windows-disable-console ^
    --output-dir=SugoiHook_builds ^
    --company-name="Sugoi Toolkit Inc." ^
    --product-name="Sugoi Hook" ^
    --file-version=2.0.1 ^
    --product-version=2.0.1 ^
    --file-description="Modern Hooking Interface" ^
    --output-filename=SugoiHook.exe ^
    SugoiHook_gui.py

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable created: SugoiHook_builds\SugoiHook.exe
echo.
pause
