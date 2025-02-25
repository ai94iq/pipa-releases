@echo off
setlocal EnableDelayedExpansion

REM Check if any files exist to release
dir /b *.img *.zip >nul 2>&1
if errorlevel 1 (
    echo Error: No .img or .zip files found for release
    pause
    exit /b 1
)

REM Try to extract tag and title from zip filename, or ask user
for %%f in (*.zip) do (
    set "ZIPNAME=%%f"
    set "TITLE=%%f"
    for /f "tokens=1-3 delims=-" %%a in ("%%~nf") do (
        set "TAG=%%a-%%b-%%c"
    )
)

REM If no zip found, prompt for tag and title
if not defined TAG (
    echo No ROM zip found. Please enter release information manually:
    set /p "TAG=Enter release tag: "
    set /p "TITLE=Enter release title: "
)

REM Show extracted information
echo Tag: !TAG!
echo Title: !TITLE!

REM Get multiline notes with counter
echo Enter up to 5 release notes (press Enter after each, type 'done' when finished):
echo Do not start with '-', bullets will be added automatically
set "NOTES="
set "count=0"
:LOOP
if !count! geq 5 goto SHOW_OPTIONS
set /p "LINE=Note !count!: "
if /i "!LINE!"=="done" goto SHOW_OPTIONS
if defined NOTES (
    set "NOTES=!NOTES!%%0A- !LINE!"
) else (
    set "NOTES=- !LINE!"
)
set /a count+=1
goto LOOP

:SHOW_OPTIONS
REM Show release options and get choice
echo.
echo Release options:
echo 1. Release all files
echo 2. Release only .img files
echo 3. Release only .zip files
choice /C 123 /N /M "Choose release option (1-3): "
set "choice=!errorlevel!"

REM Build file list based on choice and handle tag/title
set "FILES="
if "!choice!"=="3" (
    for %%f in (*.zip*) do (
        if defined FILES (
            set "FILES=!FILES! "%%f""
        ) else (
            set "FILES="%%f""
        )
    )
) else if "!choice!"=="2" (
    REM For img files, always prompt for tag and title
    set /p "TAG=Enter release tag: "
    set /p "TITLE=Enter release title: "
    for %%f in (*.img) do (
        if defined FILES (
            set "FILES=!FILES! "%%f""
        ) else (
            set "FILES="%%f""
        )
    )
) else (
    for %%f in (*.img *.zip*) do (
        if defined FILES (
            set "FILES=!FILES! "%%f""
        ) else (
            set "FILES="%%f""
        )
    )
)

REM Check if files were found
if not defined FILES (
    echo Error: No matching files found for selected option
    pause
    exit /b 1
)

REM Show final command
echo.
echo Final command to be executed:
echo ================================
echo gh release create "!TAG!" !FILES! --title "!TITLE!" --notes "!NOTES!"
echo ================================
echo.

REM Prompt for confirmation - case insensitive with better handling
:CONFIRM
set /p "CONFIRM=Execute this command? (Y/N): "
if /i "!CONFIRM!"=="Y" (
    gh release create "!TAG!" !FILES! --title "!TITLE!" --notes "!NOTES!"
    if errorlevel 1 (
        echo Error: Failed to create release
        pause
        exit /b 1
    )
    echo Release created successfully.
) else if /i "!CONFIRM!"=="N" (
    echo Operation cancelled by user.
) else (
    echo Please enter Y or N
    goto CONFIRM
)

pause