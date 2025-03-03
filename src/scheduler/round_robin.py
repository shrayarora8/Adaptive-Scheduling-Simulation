import simpy
from collections import deque

class RoundRobinScheduler:
    def __init__(self, env, cpu, time_quantum):
        self.env = env
        self.cpu = cpu
        self.time_quantum = time_quantum
        self.ready_queue = deque()

    def process_task(self, name, burst_time):
        arrival_time = self.env.now
        print(f"{name} arrived at time {arrival_time:.2f}")

        self.ready_queue.append((name, burst_time, arrival_time))

        while self.ready_queue:
            current_name, remaining_time, arrival_time = self.ready_queue.popleft()

            with self.cpu.request() as req:
                yield req

                start_time = self.env.now
                time_slice = min(self.time_quantum, remaining_time)

                print(f"{current_name} started execution at time {start_time:.2f} with {remaining_time} units left")

                yield self.env.timeout(time_slice)
                remaining_time -= time_slice

                # Check if completed, if not requeue
                if remaining_time > 0:
                    print(f"{current_name} time quantum expired, {remaining_time} units remaining.")
                    self.ready_queue.append((current_name, remaining_time, arrival_time))
                else:
                    completion_time = self.env.now
                    turnaround_time = completion_time - arrival_time
                    waiting_time = turnaround_time - burst_time

                    result = {
                        "name": current_name,
                        "arrival_time": arrival_time,
                        "start_time": start_time,
                        "completion_time": completion_time,
                        "turnaround_time": turnaround_time,
                        "waiting_time": waiting_time,
                        "burst_time": burst_time
                    }

                    print(f"[RESULT] {result}\n")
