import simpy

class SJFScheduler:
    def __init__(self, env, cpu):
        self.env = env
        self.cpu = cpu
        self.ready_queue = []

    def process_task(self, name, burst_time):
        arrival_time = self.env.now
        print(f"{name} arrived at time {arrival_time:.2f}")

        self.ready_queue.append((name, burst_time, arrival_time))
        # Sorts by the burst time according to algorithm to pick shortest job to implement first
        self.ready_queue.sort(key=lambda x: x[1])  

        with self.cpu.request() as req:
            yield req

            # shortest job is popped
            current_job = self.ready_queue.pop(0)
            name, burst_time, arrival_time = current_job

            start_time = self.env.now
            waiting_time = start_time - arrival_time
            print(f"{name} started execution at time {start_time:.2f}")

            yield self.env.timeout(burst_time)

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

            print(f"[RESULT] {result}\n")
            return result
