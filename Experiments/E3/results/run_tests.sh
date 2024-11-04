#!/bin/bash

# Function to clean up all subprocesses
cleanup() {
    echo "Cleaning up..."
    # Kill all subprocesses
    pkill -P $$
    exit 0
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

python3 ../../main.py cross_validation SDMapStar MIMIC &
python3 ../../main.py cross_validation IDSD MIMIC &
python3 ../../main.py cross_validation BSD MIMIC &

python3 ../../main.py cross_validation SDMapStar Mushrooms &
python3 ../../main.py cross_validation IDSD Mushrooms &
python3 ../../main.py cross_validation BSD Mushrooms &

python3 ../../main.py cross_validation SDMapStar AB &
python3 ../../main.py cross_validation IDSD AB &
python3 ../../main.py cross_validation BSD AB &


wait
