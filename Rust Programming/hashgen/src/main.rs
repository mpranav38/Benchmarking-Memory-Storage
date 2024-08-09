extern crate blake3;
extern crate clap;
extern crate rayon;
extern crate rand;

use rand::random;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;
use rayon::prelude::*;

const NONCE_SIZE: usize = 6;
const HASH_SIZE: usize = 10;
const RECORD_SIZE: usize = NONCE_SIZE + HASH_SIZE;

#[derive(Clone)]
struct Record {
    nonce: Vec<u8>,
}

fn generate_hashes(records: Vec<Record>, num_threads: usize) -> Vec<(Vec<u8>, Vec<u8>)> {
    let pool = rayon::ThreadPoolBuilder::new().num_threads(num_threads).build().unwrap();
    pool.install(|| {
        records.into_par_iter().map(|record| {
            let hash = blake3::hash(&record.nonce).as_bytes()[..HASH_SIZE].to_vec();
            (hash, record.nonce)
        }).collect()
    })
}

fn parallel_timsort(records: Vec<(Vec<u8>, Vec<u8>)>, num_threads: usize) -> Vec<(Vec<u8>, Vec<u8>)> {
    let mut records = records;
    let pool = rayon::ThreadPoolBuilder::new().num_threads(num_threads).build().unwrap();
    pool.install(|| {
        records.par_sort_unstable_by(|a, b| a.0.cmp(&b.0));
    });
    records
}

fn write_sorted_hashes(filename: &str, sorted_hashes: Vec<(Vec<u8>, Vec<u8>)>, num_threads: usize) {
    let pool = rayon::ThreadPoolBuilder::new().num_threads(num_threads).build().unwrap();
    let chunks: Vec<Vec<(Vec<u8>, Vec<u8>)>> = sorted_hashes.chunks(sorted_hashes.len() / num_threads).map(|chunk| chunk.to_vec()).collect();

    pool.install(|| {
        chunks.into_par_iter().enumerate().for_each(|(i, chunk)| {
            let filename = format!("{}_{}", filename, i);
            let file = File::create(&filename).expect("Failed to create file");
            let mut writer = BufWriter::new(file);

            for (hash, nonce) in chunk {
                writer.write_all(&hash).expect("Failed to write hash");
                writer.write_all(&nonce).expect("Failed to write nonce");
            }
        });
    });

    // Merge files
    let file = File::create(filename).expect("Failed to create file");
    let mut writer = BufWriter::new(file);

    for i in 0..num_threads {
        let filename = format!("{}_{}", filename, i);
        let mut file = File::open(&filename).expect("Failed to open file");
        std::io::copy(&mut file, &mut writer).expect("Failed to copy data");
        std::fs::remove_file(&filename).expect("Failed to remove file");
    }
}

fn run_benchmark(filename: &str, file_size: usize, num_hash_threads: usize, num_sort_threads: usize, num_write_threads: usize, memory_size: usize) {
    println!("NUM_THREADS_HASH={}", num_hash_threads);
    println!("NUM_THREADS_SORT={}", num_sort_threads);
    println!("NUM_THREADS_WRITE={}", num_write_threads);
    println!("FILENAME={}", filename);
    println!("MEMORY_SIZE={}MB", memory_size);
    println!("FILESIZE={}MB", file_size);
    println!("RECORD_SIZE={}B", RECORD_SIZE);
    println!("HASH_SIZE={}B", HASH_SIZE);
    println!("NONCE_SIZE={}B", NONCE_SIZE);

    let total_records = file_size * 1024 * 1024 / RECORD_SIZE;

    let records: Vec<Record> = (0..total_records)
        .map(|_| {
            let nonce: Vec<u8> = (0..NONCE_SIZE).map(|_| random::<u8>()).collect();
            Record { nonce }
        })
        .collect();

    let start_hash_time = Instant::now();
    let hashes = generate_hashes(records, num_hash_threads);
    let end_hash_time = start_hash_time.elapsed().as_secs_f64();
    println!("Hash time: {:.4} seconds", end_hash_time);

    let start_sort_time = Instant::now();
    let sorted_hashes = parallel_timsort(hashes, num_sort_threads);
    let end_sort_time = start_sort_time.elapsed().as_secs_f64();
    println!("Sort time: {:.4} seconds", end_sort_time);

    let start_write_time = Instant::now();
    write_sorted_hashes(filename, sorted_hashes, num_write_threads);
    let end_write_time = start_write_time.elapsed().as_secs_f64();

    let total_time = end_hash_time + end_sort_time + end_write_time;
    println!("Total time: {:.4} seconds", total_time);
}

fn main() {
    let args = clap::App::new("Benchmark")
        .arg(clap::Arg::with_name("filename").short('f').required(true).takes_value(true).help("Filename"))
        .arg(clap::Arg::with_name("file_size").short('s').required(true).takes_value(true).help("File size in MB"))
        .arg(clap::Arg::with_name("num_hash_threads").short('t').required(true).takes_value(true).help("Number of hash threads"))
        .arg(clap::Arg::with_name("num_sort_threads").short('o').required(true).takes_value(true).help("Number of sort threads"))
        .arg(clap::Arg::with_name("num_write_threads").short('i').required(true).takes_value(true).help("Number of write threads"))
        .arg(clap::Arg::with_name("memory_size").short('m').required(true).takes_value(true).help("Maximum memory size in MB"))
        .get_matches();

    let filename = args.value_of("filename").unwrap();
    let file_size = args.value_of("file_size").unwrap().parse().expect("Invalid file size");
    let num_hash_threads = args.value_of("num_hash_threads").unwrap().parse().expect("Invalid number of hash threads");
    let num_sort_threads = args.value_of("num_sort_threads").unwrap().parse().expect("Invalid number of sort threads");
    let num_write_threads = args.value_of("num_write_threads").unwrap().parse().expect("Invalid number of write threads");
    let memory_size = args.value_of("memory_size").unwrap().parse().expect("Invalid memory size");

    run_benchmark(filename, file_size, num_hash_threads, num_sort_threads, num_write_threads, memory_size);
}
