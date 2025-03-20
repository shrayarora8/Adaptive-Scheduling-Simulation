import simpy

class SJFScheduler:
    def __init__(self, env, cpu):
        self.env = env
        self.cpu = cpu
        self.ready_queue = []
        self.completed_jobs = []

    def process_task(self, name, burst_time):
        arrival_time = self.env.now
        print(f"{name} arrived at time {arrival_time:.2f}")

        # Add job to queue but don't sort yet
        self.ready_queue.append((name, burst_time, arrival_time))

        while True:
            # Ensure there are jobs to process
            if not self.ready_queue:
                yield self.env.timeout(1)  # Wait until jobs arrive
                continue

            # Sort by burst time before execution (Shortest Job First)
            self.ready_queue.sort(key=lambda x: x[1])

            # Get shortest job from queue
            name, burst_time, arrival_time = self.ready_queue.pop(0)

            # Wait for CPU availability
            with self.cpu.request() as req:
                yield req  # Request CPU and wait

                start_time = self.env.now
                waiting_time = start_time - arrival_time
                print(f"{name} started execution at time {start_time:.2f}")

                yield self.env.timeout(burst_time)  # Simulate execution

                completion_time = self.env.now
                turnaround_time = completion_time - arrival_time

                result = {
                    "name": name,
                    "arrival_time": arrival_time,
                    "start_time": start_time,
                    "completion_time": completion_time,
                    "turnaround_time": turnaround_time,
                    "waiting_time": waiting_time,
                    "burst_time": burst_time
                }

                self.completed_jobs.append(result)
                print(f"[RESULT] {result}\n")