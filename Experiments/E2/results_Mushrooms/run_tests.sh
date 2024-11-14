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

for i in $(seq 1000 1000 8000)
do
    python3 ../../main.py benchmark BSD Mushrooms instances $i > results_BSD_$i.txt &
    python3 ../../main.py benchmark SDMapStar Mushrooms instances $i > results_SDMapStar_$i.txt &
    python3 ../../main.py benchmark IDSD Mushrooms instances $i > results_IDSD_$i.txt &
done


for i in $(seq 1000 1000 2000)
do
    python3 ../../main.py benchmark QFinder Mushrooms instances $i > results_QFinder_$i.txt &
done

wait
