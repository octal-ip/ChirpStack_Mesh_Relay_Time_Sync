#!/bin/sh

# 1. Strict Pathing: Prevents PATH hijacking
export PATH=/usr/bin:/usr/sbin:/bin:/sbin

read -r raw_input

# 2. Use printf to avoid flag injection, then whitelist characters
clean_input=$(printf '%s' "$raw_input" | tr -dc '0-9 :\-')

# 3. Collapse whitespace and store
input_date=$(echo $clean_input)

# 4. Check if input is empty, too short, or suspiciously long
# 10 chars is "YYYY-MM-DD", 25 chars allows for "YYYY-MM-DD HH:MM:SS  "
if [ -z "$input_date" ] || [ ${#input_date} -ne 19 ]; then
    echo "ERR_INVALID_LENGTH" >&2
    exit 1
fi

# 5. Regex Validation: Ensure it matches YYYY-MM-DD HH:MM:SS exactly
case "$input_date" in
    [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\ [0-9][0-9]:[0-9][0-9]:[0-9][0-9])
        # Valid format
        ;;
    *)
        echo "ERR_FMT" >&2
        exit 1
        ;;
esac

# 5. Set the system date using UTC
# Using the -- flag prevents the input from being interpreted as an argument
if date -u -s "$input_date" > /dev/null 2>&1; then
    echo "OK"
else
    echo "ERR_SET" >&2
    exit 1
fi
