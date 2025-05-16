import time

# Record the start time
start_time = time.time()

# Your code here
# For example, let's say you want to measure the time taken for a loop
for i in range(1000000):
    pass

# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print(f"Time taken: {elapsed_time} seconds")
