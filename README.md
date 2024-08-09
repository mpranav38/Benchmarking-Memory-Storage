This project aims to teach you about file I/O and benchmarking. You can use any of the following languages
to implement this assignment: Python, Java, C, C++, Rust; doing your implementation in C, C++, or Rust
will get you up to 10% extra credit pointsfor efficient implementations. You can use any libraries (e.g. STL,
Boost, PThread, OMP, BLAKE3, etc). You must use Linux system for your development. The performance
evaluation should be done on Chameleon in a Linux environment.
You will make use of a hashing algorithm:
• Blake3:
o Repo: https://github.com/BLAKE3-team/BLAKE3
o Paper: https://github.com/BLAKE3-team/BLAKE3-specs/blob/master/blake3.pdf
#
Your benchmark will use a 6-byte NONCE to generate 2^26 (SMALL) or 2^32 (LARGE) BLAKE3 hashes of
10-bytes long each and store them in a file on disk in sorted order (sorted by 12-byte hash). A record could
be defined in C as follows:
#
#define NONCE_SIZE 6
#define HASH_SIZE 10
// Structure to hold a 16-byte record
typedef struct {
uint8_t hash[HASH_SIZE]; // hash value as byte array
uint8_t nonce[NONCE_SIZE]; // Nonce value as byte array
#
Your file should be 1GB (SMALL) or 64GB (LARGE) in size when your benchmark completes (64GB =
2^32*(12B+4B)) – your file should be written in binary to ensure efficient write and read to this data; do
not write the data in ASCII. You are to parallelize your various stages (hash generation, sort, and disk write)
with a pool of threads per stage, that can be controlled separately.
You will have several command line arguments that you will explore from a performance point of view for
the SMALL 1GB workload. There are 27=1x3x3x3 experiments to run, so make sure to automate the
execution of these runs in a bash script (e.g. 3 nested loops in bash should work).
1. Maximum memory allowed to use (MB): 128
2. Number of hash threads: 1, 4, 16
3. Number of sort threads: 1, 4, 16
4. Number of write threads: 1, 4, 16
Each experiment should take about a minute or less, depending on the hardware, processor type, core
counts, and hard drive technology. These experiments should take less than an hour to run in all.
Plot the results of these 27 experiments and identify the best combination of command line arguments.
Explain why you believe the best and worst configurations make sense. 

