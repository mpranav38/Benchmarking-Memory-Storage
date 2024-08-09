#!/bin/bash

# Maximum memory allowed to use (MB)
memory_size=128

# Number of hash threads
hash_threads=(1 4 16)

# Number of sort threads
sort_threads=(1 4 16)

# Number of write threads
write_threads=(1 4 16)

# Output directory
output_dir="experiment_results"

# Create the output directory if it doesn't exist
mkdir -p "$output_dir"

# Counter for naming the output files
counter=1

# Iterate over each combination of parameters
for ht in "${hash_threads[@]}"; do
    for st in "${sort_threads[@]}"; do
        for wt in "${write_threads[@]}"; do
            # Construct filename based on parameters
            filename="data$counter.bin"
            ((counter++))

            # Execute the Python script with the current parameters
            ./hashgen1gb.py -t "$ht" -o "$st" -i "$wt" -f "$output_dir/$filename" -s 1024 -m "$memory_size"
        done
    done
done
