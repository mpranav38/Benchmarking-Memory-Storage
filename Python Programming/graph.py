#! /usr/bin/env python

import matplotlib.pyplot as plt



# Data

data = [

    ((1, 1, 1), 247.4449),

    ((1, 1, 4), 238.6284),

    ((1, 1, 16), 241.4112),

    ((1, 4, 1), 239.7154),

    ((1, 4, 4), 242.8663),

    ((1, 4, 16), 245.406),

    ((1, 16, 1), 237.2396),

    ((1, 16, 4), 249.8463),

    ((1, 16, 16), 237.8621),

    ((4, 1, 1), 335.8198),

    ((4, 1, 4), 360.3365),

    ((4, 1, 16), 335.6322),

    ((4, 4, 1), 336.2104),

    ((4, 4, 4), 336.4641),

    ((4, 4, 16), 360.8162),

    ((4, 16, 1), 358.8438),

    ((4, 16, 4), 335.0055),

    ((4, 16, 16), 335.6405),

    ((16, 1, 1), 347.2122),

    ((16, 1, 4), 319.915),

    ((16, 1, 16), 320.3294),

    ((16, 4, 1), 320.2528),

    ((16, 4, 4), 322.9995),

    ((16, 4, 16), 321.2506),

    ((16, 16, 1), 347.081),

    ((16, 16, 4), 320.9774),

    ((16, 16, 16), 319.6688)

]



# Combine thread values into a single variable

threads = [(x[0][0], x[0][1], x[0][2]) for x in data]

total_time = [x[1] for x in data]



# Plotting

plt.figure(figsize=(12, 6))

plt.plot(total_time, marker='o', linestyle='-')

plt.xlabel('Data Points (Threads: Hash, Write, Sort)')

plt.ylabel('Total Time (seconds)')

plt.title('Total Time vs. Data Points (Thread Combinations)')

plt.grid(True)



# Set x-axis ticks with thread combinations

plt.xticks(range(len(threads)), threads, rotation=45)



# Save the plot to a file

plt.savefig('2d_graph_with_thread_labels.png')



# Show plot

plt.tight_layout()

plt.show()

