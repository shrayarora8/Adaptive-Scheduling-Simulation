import heapq
import simpy

# TODO: Preemptive SJF is not fully correct. 
# Issues: Some processes are not preempting correctly and some processes still complete in the wrong order.
# Current status: Needs Fixing

class PreemptiveSJFScheduler:
    def __init__(self, env, cpu):
        self.env = env
        self.cpu = cpu  
        self.queue = []  
        self.current_process = None
        self.process_dict = {}

    def add_process(self, pid, burst_time):
        arrival_time = self.env.now
        process = {
            'pid': pid,
            'burst_time': burst_time,
            'remaining_time': burst_time,
            'arrival_time': arrival_time,
            'start_time': None,
            'completion_time': None,
            'waiting_time': 0
        }

        self.process_dict[pid] = process
        heapq.heappush(self.queue, (burst_time, arrival_time, pid))

        # If new process has shorter burst time, preempt
        if self.current_process and burst_time < self.current_process['remaining_time']:
            print(f"[{round(self.env.now, 2)}] Preempting Process-{self.current_process['pid']} for Process-{pid}")

            heapq.heappush(self.queue, (
                self.current_process['remaining_time'],
                self.env.now,  
                self.current_process['pid']
            ))

            # Context switch
            self.current_process = None

    def process_task(self, pid, burst_time):
        self.add_process(pid, burst_time)

        while self.queue:
            _, _, pid = heapq.heappop(self.queue)
            process = self.process_dict[pid]

            with self.cpu.request() as req:
                yield req
                
                self.current_process = process

                if process['start_time'] is None:
                    process['start_time'] = round(self.env.now, 2)

                while process['remaining_time'] > 0:
                    if self.queue and self.queue[0][0] < process['remaining_time']:
                        next_pid = self.queue[0][2]
                        print(f"[{round(self.env.now, 2)}] Preempting Process-{pid} for Process-{next_pid}")

                        heapq.heappush(self.queue, (process['remaining_time'], self.env.now, pid))
                        
                        self.current_process = None
                        break  

                    # I time unit premption
                    time_slice = min(process['remaining_time'], 1)  
                    yield self.env.timeout(time_slice)
                    process['remaining_time'] -= time_slice

                if process['remaining_time'] == 0:
                    process['completion_time'] = round(self.env.now, 2)
                    process['turnaround_time'] = process['completion_time'] - process['arrival_time']
                    process['waiting_time'] = process['turnaround_time'] - process['burst_time']

                    print(f"[{round(self.env.now, 2)}] Process-{pid} completed | "
                          f"Turnaround: {process['turnaround_time']} | "
                          f"Waiting: {process['waiting_time']}")

                    self.current_process = None  
