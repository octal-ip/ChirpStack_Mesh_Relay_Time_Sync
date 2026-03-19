#!/bin/sh

# Read from stdin
read -r input_date

# Check if input is empty
if [ -z "$input_date" ]; then
    echo "ERR1"
    exit 1
fi

# Set the system date
# BusyBox date -s expects formats like "YYYY-MM-DD hh:mm:ss"
# or "MMDDhhmm[[CC]YY][.ss]"
if date -s "$input_date" > /dev/null 2>&1; then
    echo "OK"
else
    echo "ERR2"
    exit 1
fi
