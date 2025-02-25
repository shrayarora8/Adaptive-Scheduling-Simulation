import simpy
import random
from scheduler.fcfs import FCFSScheduler

# Simulation parameters
RANDOM_SEED = 42  
# number of cpu cores available
CPU_SPEED = 1  
# Average time between process arrivals   
ARRIVAL_RATE = 5
# Total simulation time 
SIM_TIME = 100    

# Generates new processes at random intervals
def process_generator(env, cpu, scheduler):
    process_id = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / ARRIVAL_RATE))  
        burst_time = random.randint(1, 10)  
        process_id += 1
        name = f'Process-{process_id}'
        env.process(scheduler.process_task(name, burst_time))

# Main simulation function
def main():
    random.seed()  
    env = simpy.Environment()  
    # Single-core CPU
    cpu = simpy.Resource(env, capacity=1) 

    fcfs_scheduler = FCFSScheduler(env, cpu) 

    env.process(process_generator(env, cpu,fcfs_scheduler))

    print("Starting FCFS simulation...")
    env.run(until=SIM_TIME)  # Run for 100 time units
    print("Simulation complete.")

if __name__ == '__main__':
    main()
