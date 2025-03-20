import simpy

class FCFSScheduler:
    def __init__(self, env, cpu):
        self.env = env        
        self.cpu = cpu
        self.completed_jobs = []  
        self.execution_log = []

    def process_task(self, name, burst_time):
        arrival_time = self.env.now  
        print(f"{name} arrived at time {arrival_time:.2f}")

        # Request CPU access
        with self.cpu.request() as req:
            yield req  

            start_time = self.env.now  
            print(f"{name} started execution at time {start_time:.2f}")

            yield self.env.timeout(burst_time)

            completion_time = self.env.now
            print(f"{name} completed execution at time {completion_time:.2f}")

            turnaround_time = completion_time - arrival_time
            waiting_time = turnaround_time - burst_time

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
            self.execution_log.append(result)
