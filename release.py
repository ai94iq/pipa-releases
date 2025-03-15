#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
import time

def run_command(cmd, check=True):
    """Run a command and return its output."""
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.returncode

def check_tag_exists(tag):
    """Check if a GitHub tag already exists and return True if it does."""
    _, exit_code = run_command(["gh", "release", "view", tag], check=False)
    return exit_code == 0

def get_unique_tag(tag):
    """Generate a unique tag if the original already exists."""
    if not check_tag_exists(tag):
        return tag
    
    print(f"Warning: A release with tag \"{tag}\" already exists.")
    
    # Try incrementing versions
    version = 2
    while check_tag_exists(f"{tag}-v{version}"):
        version += 1
    
    new_tag = f"{tag}-v{version}"
    print(f"Using new tag: {new_tag}")
    return new_tag

def get_user_notes(interactive):
    """Get release notes from user input."""
    if not interactive:
        return "- Auto-generated release"
    
    print("\nEnter up to 5 release notes (press Enter after each, type 'done' when finished):")
    print("Do not start with '-', bullets will be added automatically")
    
    notes = []
    for i in range(5):
        note = input(f"Note {i}: ")
        if not note or note.lower() == "done":
            break
        notes.append(f"- {note}")
    
    if not notes:
        return "- Auto-generated release"
    return "\n".join(notes)

def get_confirmation(auto_confirm):
    """Get user confirmation unless auto_confirm is True."""
    if auto_confirm:
        return True
    
    while True:
        response = input("Execute this command? (Y/N): ").lower()
        if response == "y":
            return True
        elif response == "n":
            return False
        else:
            print("Please enter Y or N")

def extract_tag_from_zip(zip_file):
    """Extract tag from ZIP filename."""
    match = re.search(r"(.*?-.*?-\d+).*", os.path.basename(zip_file))
    if match:
        return match.group(1)
    return None

def find_files_by_extension(extensions):
    """Find files by extension(s)."""
    files = []
    for ext in extensions:
        files.extend(list(Path(".").glob(f"*.{ext}")))
    return files

def interactive_mode():
    """Run the script in fully interactive mode with a menu interface."""
    print("=======================================================")
    print("             GitHub ROM Release Creator                ")
    print("=======================================================")
    
    # Check for files to release
    zip_files = find_files_by_extension(["zip"])
    img_files = find_files_by_extension(["img"])
    
    if not (zip_files or img_files):
        print("Error: No .img or .zip files found for release")
        input("Press Enter to continue...")
        return 1
    
    # Display available files
    print("\nAvailable files:")
    if zip_files:
        print("\nZIP files:")
        for i, file in enumerate(zip_files):
            print(f"  {i+1}. {file.name}")
    
    if img_files:
        print("\nIMG files:")
        for i, file in enumerate(img_files):
            print(f"  {i+1}. {file.name}")
    
    # Extract tag and title from zip filename or ask user
    tag = ""
    title = ""
    
    if zip_files:
        zipname = str(zip_files[0])
        title = zipname
        tag = extract_tag_from_zip(zipname)
        
        if tag:
            print(f"\nExtracted tag: {tag}")
            change_tag = input("Do you want to use a different tag? (Y/N): ").lower()
            if change_tag == "y":
                tag = input("Enter release tag: ")
        else:
            print("Could not extract tag from ZIP filename.")
            tag = input("Enter release tag: ")
    else:
        print("No ZIP files found. Please enter release information manually:")
        tag = input("Enter release tag: ")
        title = input("Enter release title: ")
    
    # Check if title needs to be changed
    change_title = input(f"Current title: {title}\nDo you want to change it? (Y/N): ").lower()
    if change_title == "y":
        title = input("Enter release title: ")
    
    # Check if tag already exists on GitHub and get a unique tag
    print(f"\nChecking if tag \"{tag}\" already exists...")
    tag = get_unique_tag(tag)
    
    # Get release notes
    notes = get_user_notes(True)
    
    # Choose which files to include
    print("\nRelease options:")
    print("1. Release all files")
    print("2. Release only .img files")
    print("3. Release only .zip files")
    print("4. Select files individually")
    
    choice = ""
    while choice not in ["1", "2", "3", "4"]:
        choice = input("Choose release option (1-4): ")
    
    files_to_release = []
    
    if choice == "1":
        files_to_release = zip_files + img_files
    elif choice == "2":
        files_to_release = img_files
    elif choice == "3":
        files_to_release = zip_files
    elif choice == "4":
        # Individual file selection
        print("\nSelect files to include (comma-separated numbers, e.g. 1,3,5):")
        all_files = []
        if zip_files:
            print("\nZIP files:")
            for i, file in enumerate(zip_files):
                print(f"  {i+1}. {file.name}")
                all_files.append(file)
        
        if img_files:
            offset = len(zip_files)
            print("\nIMG files:")
            for i, file in enumerate(img_files):
                print(f"  {i+offset+1}. {file.name}")
                all_files.append(file)
        
        selected = input("Enter file numbers: ")
        try:
            selected_indices = [int(x.strip())-1 for x in selected.split(",") if x.strip()]
            for idx in selected_indices:
                if 0 <= idx < len(all_files):
                    files_to_release.append(all_files[idx])
        except ValueError:
            print("Invalid input. Using all files.")
            files_to_release = zip_files + img_files
    
    if not files_to_release:
        print("Error: No files selected for release")
        input("Press Enter to continue...")
        return 1
    
    # Show selected files
    print("\nSelected files for release:")
    for file in files_to_release:
        print(f"  - {file.name}")
    
    # Build command for creating the release
    cmd = ["gh", "release", "create", tag]
    for file in files_to_release:
        cmd.append(str(file))
    cmd.extend(["--title", title, "--notes", notes])
    
    # Show final command
    print("\nFinal command to be executed:")
    print("================================")
    print(" ".join(cmd))
    print("================================")
    print()
    
    # Get confirmation and execute
    if get_confirmation(False):
        print("Executing command...")
        result, exit_code = run_command(cmd, check=False)
        if exit_code == 0:
            print("Release created successfully.")
        else:
            print(f"Error: Failed to create release\n{result}")
            input("Press Enter to continue...")
            return 1
    else:
        print("Operation cancelled by user.")
    
    input("Press Enter to continue...")
    return 0

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Create GitHub releases for ROM files")
    parser.add_argument("-a", "--all", action="store_true", help="Release all files without prompting")
    parser.add_argument("-i", "--img", action="store_true", help="Release only .img files")
    parser.add_argument("-z", "--zip", action="store_true", help="Release only .zip files")
    parser.add_argument("-n", "--notes", action="append", help="Set release notes (use multiple times for multiple lines)")
    parser.add_argument("-y", "--yes", action="store_true", help="Auto-confirm release creation")
    args = parser.parse_args()
    
    # If no args specified, go to interactive mode
    if not any(vars(args).values()):
        return interactive_mode()
    
    # Non-interactive mode
    # Set interactive mode based on command line arguments
    interactive = False
    auto_confirm = args.yes
    
    # Check for files to release
    zip_files = find_files_by_extension(["zip"])
    img_files = find_files_by_extension(["img"])
    
    if not (zip_files or img_files):
        print("Error: No .img or .zip files found for release")
        return 1
    
    # Extract tag and title from zip filename
    tag = ""
    title = ""
    
    if zip_files:
        zipname = str(zip_files[0])
        title = zipname
        tag = extract_tag_from_zip(zipname)
    
    # If no tag was extracted, exit with error
    if not tag:
        print("Error: Could not extract tag from ZIP filename")
        return 1
    
    # Show extracted information
    print(f"Tag: {tag}")
    print(f"Title: {title}")
    
    # Check if tag already exists on GitHub and get a unique tag
    tag = get_unique_tag(tag)
    
    # Get release notes
    notes = ""
    if args.notes:
        notes = "\n".join([f"- {note}" for note in args.notes])
    else:
        notes = "- Auto-generated release"
    
    # Determine which files to release
    files_to_release = []
    
    if args.img:
        files_to_release = img_files
    elif args.zip:
        files_to_release = zip_files
    else:  # --all or default
        files_to_release = zip_files + img_files
    
    if not files_to_release:
        print("Error: No matching files found for selected option")
        return 1
    
    # Build command for creating the release
    cmd = ["gh", "release", "create", tag]
    for file in files_to_release:
        cmd.append(str(file))
    cmd.extend(["--title", title, "--notes", notes])
    
    # Show final command
    print("\nFinal command to be executed:")
    print("================================")
    print(" ".join(cmd))
    print("================================")
    print()
    
    # Get confirmation and execute
    if get_confirmation(auto_confirm):
        print("Executing command...")
        result, exit_code = run_command(cmd, check=False)
        if exit_code == 0:
            print("Release created successfully.")
        else:
            print(f"Error: Failed to create release\n{result}")
            return 1
    else:
        print("Operation cancelled by user.")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())