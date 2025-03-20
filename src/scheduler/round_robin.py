import simpy
from collections import deque
import pandas as pd
import matplotlib.pyplot as plt

class RoundRobinScheduler:
    def __init__(self, env, cpu, time_quantum):
        self.env = env
        self.cpu = cpu
        self.time_quantum = time_quantum
        self.ready_queue = deque()
        self.completed_jobs = []
        self.execution_log = []  

    def process_task(self, name, burst_time):
        arrival_time = self.env.now
        self.ready_queue.append((name, burst_time, arrival_time))

        while self.ready_queue:
            current_name, remaining_time, arrival_time = self.ready_queue.popleft()

            with self.cpu.request() as req:
                yield req

                start_time = self.env.now
                time_slice = min(self.time_quantum, remaining_time)
                yield self.env.timeout(time_slice)
                end_time = self.env.now

                # Log stored so can be utilized in Gantt chart
                self.execution_log.append({
                    "Job": current_name,
                    "Start": start_time,
                    "Finish": end_time,
                    "Time Slice": time_slice,  
                    "Remaining Time": remaining_time - time_slice, 
                    "Completed": remaining_time <= time_slice 
                })

                remaining_time -= time_slice

                if remaining_time > 0:
                    self.ready_queue.append((current_name, remaining_time, arrival_time))
                else:
                    completion_time = end_time
                    turnaround_time = completion_time - arrival_time
                    waiting_time = turnaround_time - burst_time

                    self.execution_log.append({
                        "Job": current_name,
                        "Start": start_time,
                        "Finish": end_time,
                        "Time Slice": time_slice,
                        "Remaining Time": 0,  
                        "Completed": True,
                        "turnaround_time": turnaround_time,  
                        "waiting_time": waiting_time,
                        "burst_time": burst_time
                    })

                    self.completed_jobs.append({
                        "name": current_name,
                        "arrival_time": arrival_time,
                        "start_time": start_time,
                        "completion_time": completion_time,
                        "turnaround_time": turnaround_time,
                        "waiting_time": waiting_time,
                        "burst_time": burst_time
                    })
