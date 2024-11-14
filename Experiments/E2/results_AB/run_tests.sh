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

for i in $(seq 100 50 400)
do
    python3 ../../main.py benchmark BSD AB instances $i > results_BSD_$i.txt &
    python3 ../../main.py benchmark SDMapStar AB instances $i > results_SDMapStar_$i.txt &
    python3 ../../main.py benchmark QFinder AB instances $i > results_QFinder_$i.txt &
    python3 ../../main.py benchmark IDSD AB instances $i > results_IDSD_$i.txt &
done
wait
