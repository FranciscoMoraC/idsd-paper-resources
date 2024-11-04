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

for i in $(seq 5 22)
do
    python3 ../../main.py benchmark BSD Mushrooms columns $i > results_BSD_Mushrooms_$i.txt &
    python3 ../../main.py benchmark SDMapStar Mushrooms columns $i > results_SDMapStar_Mushrooms_$i.txt &
    python3 ../../main.py benchmark QFinder Mushrooms columns $i > results_QFinder_Mushrooms_$i.txt &
    python3 ../../main.py benchmark IDSD Mushrooms columns $i > results_IDSD_Mushrooms_$i.txt &
done

for i in $(seq 5 13)
do
    python3 ../../main.py benchmark BSD MIMIC columns $i > results_BSD_MIMIC_$i.txt &
    python3 ../../main.py benchmark SDMapStar MIMIC columns $i > results_SDMapStar_MIMIC_$i.txt &
    python3 ../../main.py benchmark QFinder MIMIC columns $i > results_QFinder_MIMIC_$i.txt &
    python3 ../../main.py benchmark IDSD MIMIC columns $i > results_IDSD_MIMIC_$i.txt &
done

for i in $(seq 5 9)
do
    python3 ../../main.py benchmark BSD AB columns $i > results_BSD_AB_$i.txt &
    python3 ../../main.py benchmark SDMapStar AB columns $i > results_SDMapStar_AB_$i.txt &
    python3 ../../main.py benchmark QFinder AB columns $i > results_QFinder_AB_$i.txt &
    python3 ../../main.py benchmark IDSD AB columns $i > results_IDSD_AB_$i.txt &
done

wait
