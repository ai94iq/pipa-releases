#!/usr/bin/env bash

# Ensure compatibility with both bash and zsh
if [ -n "$ZSH_VERSION" ]; then
    setopt SH_WORD_SPLIT
    setopt KSH_ARRAYS
fi

# Function to get user confirmation
get_confirmation() {
    while true; do
        printf "Execute this command? (Y/N): "
        read -r response
        case "$response" in
            [Yy]) return 0 ;;
            [Nn]) return 1 ;;
            *) echo "Please enter Y or N" ;;
        esac
    done
}

# Add check for zip file existence
if ! ls *.zip 1> /dev/null 2>&1; then
    echo "Error: No .zip files found in current directory"
    exit 1
fi

# Extract tag and title from zip filename
for f in *.zip; do
    if [ -f "$f" ]; then
        ZIPNAME="$f"
        TITLE="$f"
        # Extract first three parts of name before -UNOFFICIAL
        TAG=$(echo "$f" | sed -E 's/(.*-.*-[0-9]+)-.*/\1/')
        break
    fi
done

# Add check for tag extraction success
if [ -z "$TAG" ]; then
    echo "Error: Could not extract tag from filename"
    exit 1
fi

# Show extracted information
echo "Tag: $TAG"
echo "Title: $TITLE"

# Get multiline notes with counter
echo "Enter up to 5 release notes (press Enter after each, type 'done' when finished):"
echo "Do not start with '-', bullets will be added automatically"
NOTES=""
count=0

while [ $count -lt 5 ]; do
    printf "Note %d: " "$count"
    read -r LINE
    [ "$LINE" = "done" ] && break
    
    if [ -n "$NOTES" ]; then
        NOTES="${NOTES}

- ${LINE}"
    else
        NOTES="- ${LINE}"
    fi
    ((count++))
done

# Add check for file existence before building file list
found=0
for ext in "img" "zip"; do
    if ls *."$ext" 1> /dev/null 2>&1; then
        found=1
        break
    fi
done

if [ $found -eq 0 ]; then
    echo "Error: No .img or .zip files found for release"
    exit 1
fi

# Show release options
echo
echo "Release options:"
echo "1. Release all files"
echo "2. Release only .img files"
echo "3. Release only .zip files"
printf "Choose release option (1-3): "
read -r choice

# Build file list based on choice
FILES=""
case $choice in
    1)
        for f in *.img *.zip*; do
            [ -f "$f" ] && FILES="${FILES:+$FILES }\"$f\""
        done
        ;;
    2)
        # For img files, always prompt for tag and title
        read -r -p "Enter release tag: " TAG
        read -r -p "Enter release title: " TITLE
        for f in *.img; do
            [ -f "$f" ] && FILES="${FILES:+$FILES }\"$f\""
        done
        ;;
    3)
        for f in *.zip*; do
            [ -f "$f" ] && FILES="${FILES:+$FILES }\"$f\""
        done
        ;;
    *)
        echo "Error: Invalid option"
        exit 1
        ;;
esac

# Check if files were found
if [ -z "$FILES" ]; then
    echo "Error: No matching files found for selected option"
    exit 1
fi

# Show final command
printf '\n'
echo "Final command to be executed:"
echo "================================"
echo "gh release create \"$TAG\" $FILES --title \"$TITLE\" --notes \"$NOTES\""
echo "================================"
printf '\n'

# Get confirmation and execute
if get_confirmation; then
    if eval "gh release create \"$TAG\" $FILES --title \"$TITLE\" --notes \"$NOTES\""; then
        echo "Release created successfully."
    else
        echo "Error: Failed to create release"
        exit 1
    fi
else
    echo "Operation cancelled by user."
    exit 0
fi

read -r -p "Press enter to continue"