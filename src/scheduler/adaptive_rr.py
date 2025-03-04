import simpy
import numpy as np

class AdaptiveRoundRobinScheduler:
    def __init__(self, env, cpu, adjust_interval, initial_quantum=10, sensitivity=0.1):
        self.env = env
        self.cpu = cpu
        self.time_quantum = initial_quantum  
        self.adjust_interval = adjust_interval  # How often we change the quantam based on the workload
        self.process_queue = []
        self.waiting_times = []  
        self.last_adjustment_time = 0
        self.min_quantum = 2  # Lower bound for time quantum
        self.max_quantum = 50  # Upper bound for time quantum
        self.sensitivity = sensitivity

    def add_process(self, process):
        self.process_queue.append(process)

    def adjust_time_quantum(self):
        print(f"[{self.env.now:.2f}] ⚡ DEBUG: Checking Quantum Adjustments | Queue Size: {len(self.waiting_times)}")
        # collects atleast 5 data points for the processes in order to calculate average waiting time and make an 
        # adaptive decison from there
        if len(self.waiting_times) < 2:
            print(f"[{self.env.now:.2f}] Not enough processes (Need 2, Have {len(self.waiting_times)}) - Skipping Adjustment")
            return  

        avg_waiting_time = np.mean(self.waiting_times[-5:])  
        target_waiting_time = np.mean(self.waiting_times[-5:]) * 0.8 

        # Dynamic adjustment formula
        delta = self.sensitivity * 2 * (avg_waiting_time - target_waiting_time)
        new_quantum = int(self.time_quantum + delta)
        new_quantum = max(self.min_quantum, min(self.max_quantum, new_quantum))  # Ensure within bounds
        if new_quantum != self.time_quantum:
            print(f"\n[{self.env.now:.2f}] 🔄 Quantum Adjusted: {self.time_quantum} → {new_quantum} (Avg Wait Time: {avg_waiting_time:.2f} ms)\n")
        self.time_quantum = new_quantum
        print(f"⚡ IMMEDIATE QUANTUM UPDATE: New Quantum is now {self.time_quantum}")


    def process_task(self, name, burst_time):
        arrival_time = self.env.now
        remaining_time = burst_time
        if remaining_time == burst_time:
            print(f"[{self.env.now:.2f}] {name} arrives | Burst Time: {burst_time} | Current Quantum: {self.time_quantum}")

        while remaining_time > 0:
            with self.cpu.request() as req:
                yield req
                execute_time = min(self.time_quantum, remaining_time)
                yield self.env.timeout(execute_time)
                remaining_time -= execute_time

                print(f"[{self.env.now:.2f}] {name} executed for {execute_time}ms | Remaining: {remaining_time}ms | Quantum: {self.time_quantum}")

            if remaining_time > 0:
                print(f"[{self.env.now:.2f}] {name} preempted, re-entering queue with {remaining_time}ms left.")
                self.env.timeout(1)  # Short delay before rescheduling
                self.env.process(self.process_task(name, remaining_time))


        completion_time = self.env.now
        turnaround_time = completion_time - arrival_time
        waiting_time = turnaround_time - burst_time
        self.waiting_times.append(waiting_time)
        if len(self.waiting_times) >= 2 and (len(self.waiting_times) % 2 == 0 or self.env.now - self.last_adjustment_time >= self.adjust_interval):
            self.adjust_time_quantum()
            self.last_adjustment_time = self.env.now
        print(f"[{self.env.now:.2f}] {name} completed | Turnaround: {turnaround_time}ms | Waiting: {waiting_time}ms")

