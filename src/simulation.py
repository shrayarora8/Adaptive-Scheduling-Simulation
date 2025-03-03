import simpy
import random
from scheduler.fcfs import FCFSScheduler
from scheduler.sjf import SJFScheduler
from scheduler.round_robin import RoundRobinScheduler
from scheduler.preemptive_sjf import PreemptiveSJFScheduler
import numpy as np


# Simulation parameters
RANDOM_SEED = 42  
# number of cpu cores available
CPU_SPEED = 1  
# Average time between process arrivals   
ARRIVAL_RATE = 5
# Total simulation time 
SIM_TIME = 100    

# Generates new processes at random intervals
def process_generator(env, cpu, scheduler, scheduler_name):
    process_id = 0
    while True:
        yield env.timeout(np.random.exponential(scale=5))  # Poisson distribution
        burst_time = max(1, int(np.random.normal(loc=10, scale=5))) # normal distribution  
        process_id += 1
        name = f'Process-{process_id}'
        print(f"[{round(env.now, 2)}] New Process-{process_id} | Burst Time: {burst_time}")
        env.process(scheduler.process_task(name, burst_time))

# Function to run a specific scheduler
def run_simulation(scheduler_name):
    print(f"\nStarting {scheduler_name} simulation...")
    random.seed()
    env = simpy.Environment()
    cpu = simpy.Resource(env, capacity=1)

    # Choose scheduler
    if scheduler_name == "FCFS":
        scheduler = FCFSScheduler(env, cpu)
    elif scheduler_name == "SJF":
        scheduler = SJFScheduler(env, cpu)
    elif scheduler_name == "RoundRobin":
        scheduler = RoundRobinScheduler(env, cpu, time_quantum=3)
    elif scheduler_name == "PreemptiveSJF":  
        scheduler = PreemptiveSJFScheduler(env, cpu)
    else:
        raise ValueError("Invalid scheduler name!")

    env.process(process_generator(env, cpu, scheduler, scheduler_name))
    env.run(until=SIM_TIME)
    print(f"{scheduler_name} simulation complete.\n")

# Main simulation function
def main():
    #run_simulation("FCFS")
    #run_simulation("SJF")
    #run_simulation("RoundRobin")
    run_simulation("PreemptiveSJF")

if __name__ == '__main__':
    main()
