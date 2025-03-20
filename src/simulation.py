import simpy
import random
from scheduler.fcfs import FCFSScheduler
from scheduler.sjf import SJFScheduler
from scheduler.round_robin import RoundRobinScheduler
from scheduler.preemptive_sjf import PreemptiveSJFScheduler
from scheduler.adaptive_rr import AdaptiveRoundRobinScheduler  
import numpy as np
import pandas as pd
import os
import ast
import re
import matplotlib.pyplot as plt


# Simulation parameters
RANDOM_SEED = 42  
# number of cpu cores available
CPU_SPEED = 1  
# Average time between process arrivals   
ARRIVAL_RATE = 5
# Total simulation time 
SIM_TIME = 100    

seen_jobs = set()  

def process_generator(env, cpu, scheduler, scheduler_name, workload, last_completion_time):
    base_time = workload[0][0]  

    for job in workload:
        arrival_time, job_id, priority, burst_time = job
        
        adjusted_arrival = last_completion_time + (arrival_time - base_time)

        delay = max(0, adjusted_arrival - env.now)

        yield env.timeout(delay)

        print(f"[{round(env.now, 2)}] New Job-{job_id} | Priority: {priority} | Burst Time: {burst_time}")
        env.process(scheduler.process_task(f"Job-{job_id}", burst_time))


def run_simulation(scheduler_name, workload):
    print(f"\n Running {scheduler_name} Simulation...")
    env = simpy.Environment()
    cpu = simpy.Resource(env, capacity=1)
    seen_jobs = set()

    if scheduler_name == "FCFS":
        scheduler = FCFSScheduler(env, cpu)
    elif scheduler_name == "SJF":
        scheduler = SJFScheduler(env, cpu)
    elif scheduler_name == "RoundRobin":
        scheduler = RoundRobinScheduler(env, cpu, time_quantum=3)
    else:
        raise ValueError("Invalid scheduler name!")

    batch = workload[:25]  # Simpler single batch 

    env.process(process_generator(env, cpu, scheduler, scheduler_name, batch, last_completion_time=0))
    env.run()

    execution_df = pd.DataFrame(scheduler.execution_log)

    # summary logs
    total_turnaround = sum(job["turnaround_time"] for job in scheduler.completed_jobs)
    total_waiting = sum(job["waiting_time"] for job in scheduler.completed_jobs)

    print("\n🔎Batch Summary:")
    print(f"   - Jobs Processed: {len(scheduler.completed_jobs)}")
    print(f"   - Avg Turnaround Time: {total_turnaround / len(scheduler.completed_jobs):.2f} sec")
    print(f"   - Avg Waiting Time: {total_waiting / len(scheduler.completed_jobs):.2f} sec")
    print("   - Completion Order: " + " → ".join(job["name"] for job in scheduler.completed_jobs))
    print("-------------------------------------------------")

    execution_df = pd.DataFrame(scheduler.execution_log)
    
    return execution_df


def parse_cpu_usage(value):
    try:
        if isinstance(value, str):
            fixed_value = re.sub(r"\s+", ",", value.strip())  
            
            parsed_list = ast.literal_eval(fixed_value)  

            if isinstance(parsed_list, list):
                return [float(v) for v in parsed_list if isinstance(v, (int, float))]
        
        if isinstance(value, list):
            return [float(v) for v in value if isinstance(v, (int, float))]

        return []  
    except Exception as e:
        print(f"⚠️ Error parsing CPU usage: {value}, {e}")
        return []  




def load_kaggle_trace(scheduler_name, file_path="borg_traces_data.csv"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file '{file_path}' not found.")
    
    df = pd.read_csv(file_path)

    # We want only "schedule" event jobs
    df = df[df["event"] == "SCHEDULE"]

    df = df[["time", "collection_id", "priority", "cpu_usage_distribution"]].dropna()

    unique_jobs = df["collection_id"].nunique()
    total_rows = len(df)
    print(f"Unique Job IDs: {unique_jobs}, Total Rows: {total_rows}")

    df["cpu_usage_distribution"] = df["cpu_usage_distribution"].apply(parse_cpu_usage)


    df["time"] = pd.to_numeric(df["time"], errors='coerce') / 1e9  
    df = df.dropna(subset=["time"])
    df = df[df["time"] > 0]
    df["time"] = df["time"].astype(float)

    
    df = df.sort_values(by="time", ascending=True).reset_index(drop=True)

    if scheduler_name == "AdaptiveRR":
        df["burst_time"] = df["cpu_usage_distribution"].apply(
            lambda x: np.percentile(x, 40) * 200 if len(x) > 0 and np.percentile(x, 40) > 0 else 0.01
        )
    else:
        df["burst_time"] = df["cpu_usage_distribution"].apply(
            lambda x: np.percentile(x, 97) * 200 if len(x) > 0 and np.percentile(x, 97) > 0 else 0.01
        )


    df = df[["time", "collection_id", "priority", "burst_time"]]

    
    workload = [(round(float(t), 6), int(j), int(p), float(b)) 
                for t, j, p, b in df.itertuples(index=False, name=None)]

    return workload







# Main simulation function
def main():
    #run_simulation("FCFS")
    #run_simulation("SJF")
    #run_simulation("RoundRobin")
    #run_simulation("PreemptiveSJF")
    #run_simulation("AdaptiveRR")
    workload = load_kaggle_trace("borg_traces_data.csv")
    run_simulation("RoundRobin", workload)


if __name__ == '__main__':
    main()
