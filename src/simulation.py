import simpy
import random

# Simulation parameters
RANDOM_SEED = 42  
# number of cpu cores available
CPU_SPEED = 1  
# Average time between process arrivals   
ARRIVAL_RATE = 5 
# Total simulation time 
SIM_TIME = 100    

# Represents a single task or process
class Process:
    def __init__(self, env, name, cpu, burst_time):
        # environment - tracks simulation time
        self.env = env  
        self.name = name
        # simulated cpu resource  
        self.cpu = cpu
        # total cpu time required by process
        self.burst_time = burst_time  
        self.action = env.process(self.run()) 

    def run(self):
        # time when the process arrives
        arrival_time = self.env.now  
        print(f'{self.name} arrived at time {arrival_time:.2f}')

        # Request the CPU to take up the process
        with self.cpu.request() as req:
            # CPU must be available
            yield req  

            print(f'{self.name} started execution at time {self.env.now:.2f}')
            # working on the process
            yield self.env.timeout(self.burst_time)  

            print(f'{self.name} completed execution at time {self.env.now:.2f}')

# Generates new processes at random intervals
def process_generator(env, cpu):
    process_id = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / ARRIVAL_RATE))  
        burst_time = random.randint(1, 10)  
        process_id += 1
        Process(env, f'Process-{process_id}', cpu, burst_time)

# Main simulation function
def main():
    random.seed(RANDOM_SEED)  
    env = simpy.Environment()  
    # Single-core CPU
    cpu = simpy.Resource(env, capacity=1)  

    env.process(process_generator(env, cpu))

    print("Starting simulation...")
    env.run(until=SIM_TIME)  # Run for 100 time units
    print("Simulation complete.")

if __name__ == '__main__':
    main()
