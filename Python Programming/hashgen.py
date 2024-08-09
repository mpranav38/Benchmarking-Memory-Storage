#! /usr/bin/env python3
import os
import blake3
import argparse
import multiprocessing
import threading
from queue import Queue
from threading import Barrier
import time

# Constants
NONCE_SIZE = 6
HASH_SIZE = 10

# Function to divide records into chunks
def divide_records_into_chunks(records: list, num_chunks: int) -> list:
    chunk_size = len(records) // num_chunks
    chunks = [records[i:i + chunk_size] for i in range(0, len(records), chunk_size)]
    return chunks

# Function to generate hashes for a chunk of records
def generate_hashes(records: list, result_queue: Queue, progress_callback: callable, process_id: int) -> None:
    hashes = []
    total_records = len(records)
    for i, record in enumerate(records):
        nonce = record
        h = blake3.blake3(nonce).digest()[:HASH_SIZE]
        hashes.append((h, nonce))
        # Calculate progress percentage and print only at 100%
        if i == total_records - 1:
            progress_callback(process_id)
    result_queue.put(hashes)

# Function to perform parallel sorting using Timsort
def parallel_timsort(records: list) -> list:
    return sorted(records, key=lambda x: x[0])

# Function to write sorted hashes to a file
def write_sorted_hashes(filename: str, sorted_hashes: list) -> float:
    start_time = time.time()
    with open(filename, 'wb') as f:
        for record in sorted_hashes:
            f.write(record[0] + record[1])
    return time.time() - start_time

# Function to run the benchmark
def run_benchmark(filename: str, hash_threads: int, sort_threads: int, write_threads: int, file_size: int, memory_size: int) -> None:
    # Calculate total number of records based on file size
    total_records = file_size * 1024 * 1024 // 16

    # Generate records
    records = [os.urandom(NONCE_SIZE) for _ in range(total_records)]

    # Divide records into chunks for multiprocessing
    process_chunks = divide_records_into_chunks(records, 4)

    # Start measuring hashgen time
    hashgen_start_time = time.time()

    # Start multiprocessing
    process_queue = multiprocessing.Queue()
    process_threads = []
    for i, chunk in enumerate(process_chunks):
        thread = threading.Thread(target=generate_hashes, args=(chunk, process_queue, print_hash_progress, i))
        process_threads.append(thread)
        thread.start()

    # Wait for multiprocessing threads to complete
    for thread in process_threads:
        thread.join()

    # Collect hash results
    hashes = []
    for _ in process_threads:
        hashes.extend(process_queue.get())

    # Calculate hashgen time
    hashgen_time = time.time() - hashgen_start_time

    # Start sorting
    sorted_hashes = parallel_timsort(hashes)

    # Start measuring sorting time
    sort_start_time = time.time()

    # Write sorted hashes to a file
    write_time = write_sorted_hashes(filename, sorted_hashes)

    # Calculate sorting time
    sort_time = time.time() - sort_start_time

    # Print total hashgen, sort, and write times
    print(f"Hashgen time: {hashgen_time:.4f} seconds")
    print(f"Sort time: {sort_time:.4f} seconds")
    print(f"Write time: {write_time:.4f} seconds")

    # Calculate total time
    total_time = hashgen_time + sort_time + write_time
    print(f"Total time: {total_time:.4f} seconds")

# Function to print hashing progress
def print_hash_progress(process_id: int) -> None:
    print(f"[hashgen{process_id}]: 100.00% completed")

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate hashes and sort them.')
parser.add_argument('-t', '--hash_threads', type=int, required=True, help='Number of hash threads')
parser.add_argument('-o', '--sort_threads', type=int, required=True, help='Number of sort threads')
parser.add_argument('-i', '--write_threads', type=int, required=True, help='Number of write threads')
parser.add_argument('-f', '--filename', type=str, required=True, help='Filename')
parser.add_argument('-s', '--file_size', type=int, required=True, help='File size in MB')
parser.add_argument('-m', '--memory_size', type=int, required=True, help='Maximum memory size in MB')
args = parser.parse_args()

# Run the benchmark
run_benchmark(args.filename, args.hash_threads, args.sort_threads, args.write_threads, args.file_size, args.memory_size)
