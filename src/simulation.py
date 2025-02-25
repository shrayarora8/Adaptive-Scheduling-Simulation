import simpy
import random
from scheduler.fcfs import FCFSScheduler
from scheduler.sjf import SJFScheduler


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
        yield env.timeout(random.expovariate(1.0 / ARRIVAL_RATE))  
        burst_time = random.randint(1, 10)  
        process_id += 1
        name = f'Process-{process_id}'
        env.process(scheduler.process_task(name, burst_time))

# Function to run a specific scheduler
def run_simulation(scheduler_name):
    print(f"\nStarting {scheduler_name} simulation...")
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    cpu = simpy.Resource(env, capacity=1)

    # Choose scheduler
    if scheduler_name == "FCFS":
        scheduler = FCFSScheduler(env, cpu)
    elif scheduler_name == "SJF":
        scheduler = SJFScheduler(env, cpu)
    else:
        raise ValueError("Invalid scheduler name!")
    
    env.process(process_generator(env, cpu, scheduler, scheduler_name))
    env.run(until=SIM_TIME)
    print(f"{scheduler_name} simulation complete.\n")

# Main simulation function
def main():
    run_simulation("FCFS")
    run_simulation("SJF")

if __name__ == '__main__':
    main()
