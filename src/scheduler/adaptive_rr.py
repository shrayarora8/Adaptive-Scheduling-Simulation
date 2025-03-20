import simpy
from collections import deque
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np

class AdaptiveRoundRobinScheduler:
    def __init__(self, env, cpu, initial_time_quantum):
        self.env = env
        self.cpu = cpu
        self.initial_time_quantum = initial_time_quantum
        self.ready_queue = deque()
        self.completed_jobs = []
        self.execution_log = []
        self.prev_quantum = initial_time_quantum  # Track last quantum

    def process_task(self, name, burst_time):
        arrival_time = self.env.now
        self.ready_queue.append((name, burst_time, arrival_time))

        while self.ready_queue:
            current_jobs = list(self.ready_queue)
            remaining_times = [job[1] for job in current_jobs]

            # Quantum Adjustment
            new_quantum = (0.6 * self.prev_quantum) + (0.4 * np.median(remaining_times))
            adaptive_quantum = max(5, int(new_quantum))  
            self.prev_quantum = adaptive_quantum  # Update for next cycle

            current_name, remaining_time, job_arrival_time = self.ready_queue.popleft()

            with self.cpu.request() as req:
                yield req

                start_time = self.env.now
                time_slice = min(adaptive_quantum, remaining_time)
                yield self.env.timeout(time_slice)
                end_time = self.env.now

                remaining_time -= time_slice

                self.execution_log.append({
                    "Job": current_name,
                    "Start": start_time,
                    "Finish": end_time,
                    "Time Slice": time_slice,
                    "Remaining Time": remaining_time,
                    "Quantum Used": adaptive_quantum,
                    "Completed": remaining_time == 0
                })

                if remaining_time > 0:
                    if remaining_time < adaptive_quantum:
                        self.ready_queue.appendleft((current_name, remaining_time, job_arrival_time))
                    else:
                        self.ready_queue.append((current_name, remaining_time, job_arrival_time))
                else:
                    completion_time = end_time
                    turnaround_time = completion_time - job_arrival_time
                    waiting_time = turnaround_time - burst_time

                    self.execution_log.append({
                        "Job": current_name,
                        "Start": start_time,
                        "Finish": end_time,
                        "Time Slice": time_slice,
                        "Remaining Time": 0,
                        "Quantum Used": adaptive_quantum,
                        "Completed": True,
                        "turnaround_time": turnaround_time,
                        "waiting_time": waiting_time,
                        "burst_time": burst_time
                    })

                    self.completed_jobs.append({
                        "name": current_name,
                        "arrival_time": job_arrival_time,
                        "start_time": start_time,
                        "completion_time": completion_time,
                        "turnaround_time": turnaround_time,
                        "waiting_time": waiting_time,
                        "burst_time": burst_time
                    })