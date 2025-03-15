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
        result, exit_code = create_release_with_progress(cmd, [str(file) for file in files_to_release])
        if exit_code == 0:
            print("Release created successfully.")
        else:
            print(f"Error: Failed to create release\n{result}")
            input("Press Enter to continue...")
            return 1
    
    input("Press Enter to continue...")
    return 0

def create_release_with_progress(cmd, files_to_release):
    """Create a release with per-file progress estimation."""
    # Get file sizes and total size
    file_sizes = {file: os.path.getsize(file) for file in files_to_release}
    total_size = sum(file_sizes.values())
    
    print(f"Total upload size: {format_size(total_size)} across {len(files_to_release)} files")
    
    # Show limitation message to manage user expectations
    print("\nNote: Progress is estimated and may not reflect actual upload status.")
    print("GitHub CLI doesn't provide real-time upload progress information.")
    
    # Process each file individually
    current_file_index = 0
    total_uploaded = 0
    
    # Start timing for overall progress
    overall_start_time = time.time()
    
    # Create the release without files first
    create_cmd = ["gh", "release", "create", cmd[3], "--title", cmd[-1], "--notes", cmd[-3]]
    print("\nCreating empty release...", end="")
    result, exit_code = run_command(create_cmd, check=False)
    
    if exit_code != 0:
        print(f"\nError creating release: {result}")
        return result, exit_code
    
    print(" Done!")
    
    # Upload each file separately
    for current_file_index, file in enumerate(files_to_release):
        file_size = file_sizes[file]
        file_name = os.path.basename(file)
        
        print(f"\nUploading file {current_file_index + 1}/{len(files_to_release)}: {file_name}")
        print(f"File size: {format_size(file_size)}")
        
        # Determine optimal estimated speed based on file size
        if file_size > 1024 * 1024 * 1024:  # > 1GB
            base_speed = 2 * 1024 * 1024  # 2 MB/s for large uploads
        else:
            base_speed = 3 * 1024 * 1024  # 3 MB/s for smaller uploads
        
        # Start the upload command for this file
        upload_cmd = ["gh", "release", "upload", cmd[3], file]
        process = subprocess.Popen(
            upload_cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Set up progress tracking for this file
        start_time = time.time()
        last_update = start_time
        last_estimate = 0
        adaptive_speed = base_speed
        last_progress_length = 0
        
        try:
            # Track progress while process is running
            while process.poll() is None:
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Only update every second to avoid too many updates
                if current_time - last_update >= 1:
                    if elapsed > 0:
                        # Calculate all progress metrics
                        time_factor = min(1.0, elapsed / 60)
                        adaptive_speed = base_speed * (1.0 - (time_factor * 0.5))
                        current_estimate = min(file_size, adaptive_speed * elapsed)
                        estimated_uploaded = max(last_estimate, current_estimate)
                        last_estimate = estimated_uploaded
                        percentage = min(99.9, (estimated_uploaded / file_size) * 100)
                        avg_speed = estimated_uploaded / elapsed if elapsed > 0 else 0
                        speed_str = f"{format_size(avg_speed)}/s"
                        
                        # Calculate ETA
                        if avg_speed > 0:
                            file_eta = (file_size - estimated_uploaded) / avg_speed
                            file_eta *= 1.1
                            file_eta_str = format_time(file_eta)
                        else:
                            file_eta_str = "Calculating..."
                        
                        # Determine file state
                        if percentage < 1:
                            state = "Starting"
                        elif percentage < 80:
                            state = "Uploading"
                        else:
                            state = "Finalizing"
                        
                        # Create progress bar
                        bar_length = 20
                        filled_length = int(bar_length * percentage / 100)
                        file_bar = '█' * filled_length + '▒' * (bar_length - filled_length)
                        
                        # Build progress string
                        file_progress = f"\rFile {current_file_index+1}/{len(files_to_release)}: [{file_bar}] {percentage:5.1f}% • {format_size(estimated_uploaded)}/{format_size(file_size)} • {speed_str} • ETA: {file_eta_str} • {state}"
                        
                        # Ensure the line is completely clear before printing new progress
                        if last_progress_length > 0:
                            print('\r' + ' ' * last_progress_length, end='')
                        
                        print(file_progress, end='', flush=True)
                        last_progress_length = len(file_progress)
                    
                    last_update = current_time
                
                # Sleep briefly to avoid high CPU usage
                time.sleep(0.1)
            
            # Process completed for this file
            stdout, stderr = process.communicate()
            exit_code = process.returncode
            
            if exit_code != 0:
                print("\n\nError uploading file {}: {}".format(file_name, stderr))
                return stderr, exit_code
            
            # Update total uploaded size
            total_uploaded += file_size
            
            # Print newline to ensure next output starts on a clean line
            print()
            
            # Show completion message for this file
            elapsed_time = time.time() - start_time
            print(f"✓ File {current_file_index+1}/{len(files_to_release)} completed: {file_name}")
            print(f"  Size: {format_size(file_size)} • Time: {format_time(elapsed_time)} • Speed: {format_size(file_size/elapsed_time)}/s")
            
            # Add simple overall progress update after each file
            overall_elapsed = time.time() - overall_start_time
            overall_percentage = (total_uploaded / total_size) * 100
            print(f"  Overall: {overall_percentage:5.1f}% complete • {format_size(total_uploaded)}/{format_size(total_size)} • Elapsed: {format_time(overall_elapsed)}")
            
        except KeyboardInterrupt:
            print("\n\nProcess interrupted by user. Attempting to clean up...")
            process.kill()
            return "Interrupted by user", 1
    
    # All files uploaded successfully
    total_elapsed = time.time() - overall_start_time
    print(f"\nAll {len(files_to_release)} files uploaded successfully!")
    print(f"Total size: {format_size(total_size)} • Completed in {format_time(total_elapsed)}")
    return "Success", 0

def format_size(size_bytes):
    """Format bytes into a human-readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.1f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.1f} GB"

def format_time(seconds):
    """Format seconds into a human-readable time."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

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
        result, exit_code = create_release_with_progress(cmd, [str(file) for file in files_to_release])
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