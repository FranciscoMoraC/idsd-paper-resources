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

python3 ../../main.py run SDMapStar MIMIC False &
python3 ../../main.py run IDSD MIMIC False &
python3 ../../main.py run BSD MIMIC False &

python3 ../../main.py run SDMapStar Mushrooms False &
python3 ../../main.py run IDSD Mushrooms False &
python3 ../../main.py run BSD Mushrooms False &

python3 ../../main.py run SDMapStar AB False &
python3 ../../main.py run IDSD AB False &
python3 ../../main.py run BSD AB False &

wait
