import streamlit as st
import pandas as pd
import plotly.express as px
import simpy
from scheduler.fcfs import FCFSScheduler
from scheduler.sjf import SJFScheduler
from scheduler.round_robin import RoundRobinScheduler
from scheduler.adaptive_rr import AdaptiveRoundRobinScheduler
from simulation import load_kaggle_trace, process_generator

def get_scheduler(scheduler_name, env, cpu):
    if scheduler_name == "FCFS":
        return FCFSScheduler(env, cpu)
    elif scheduler_name == "SJF":
        return SJFScheduler(env, cpu)
    elif scheduler_name == "RoundRobin":
        return RoundRobinScheduler(env, cpu, time_quantum=3)
    elif scheduler_name == "AdaptiveRR":
        return AdaptiveRoundRobinScheduler(env, cpu, initial_time_quantum=2)
    else:
        raise ValueError("Invalid scheduler selected!")

st.title("CPU Scheduling Simulation Dashboard")

scheduler_name = st.sidebar.selectbox(
    "Choose Scheduler",
    ["FCFS", "SJF", "RoundRobin", "AdaptiveRR"]
)

if st.button("Run Simulation"):
    workload = load_kaggle_trace(scheduler_name, "borg_traces_data.csv")

    workload.sort(key=lambda x: x[0])

    workload = [job for job in workload if job[0] > 0]

    env = simpy.Environment()
    cpu = simpy.Resource(env, capacity=1)
    scheduler = get_scheduler(scheduler_name, env, cpu)

    seen_jobs = set()
    batch = []
    batch_size = 25
    last_completion_time = 0

    for job in workload:
        arrival_time, job_id, priority, burst_time = job
        if job_id not in seen_jobs:
            seen_jobs.add(job_id)
            batch.append(job)
            if len(batch) >= batch_size:
                break

    if not batch:
        st.error("No jobs found after filtering duplicates and zero arrival times.")
    else:
        print("Batch workload:", batch)
        env.process(process_generator(env, cpu, scheduler, scheduler_name, batch, last_completion_time))
        env.run()

        if scheduler_name == "AdaptiveRR":
            execution_df = pd.DataFrame(scheduler.execution_log)
            execution_df.to_csv("adaptive_rr_execution.csv", index=False)
            print("Execution log saved as adaptive_rr_execution.csv. Upload it here.")

            if execution_df.empty:
                st.error("No execution log data available for Adaptive RR.")
            else:
                execution_df['Start'] = pd.to_numeric(execution_df['Start'], errors='coerce')
                execution_df['Finish'] = pd.to_numeric(execution_df['Finish'], errors='coerce')
                execution_df['Time Slice'] = execution_df['Finish'] - execution_df['Start']
                execution_df['Remaining Time'] = pd.to_numeric(execution_df['Remaining Time'], errors='coerce')
                execution_df['Quantum Used'] = pd.to_numeric(execution_df['Quantum Used'], errors='coerce')
                execution_df["width"] = execution_df["Time Slice"]

                fig = px.bar(
                    execution_df,
                    x="width",
                    y="Job",
                    orientation='h',
                    color="Quantum Used", 
                    base="Start",
                    hover_data=["Time Slice", "Remaining Time", "Quantum Used"],  
                    title=f"{scheduler_name} Scheduling Gantt Chart",
                    labels={'width': 'Time Slice (Duration)', 'Start': 'Start Time', 'Job': 'Job'}
                )

        elif scheduler_name == "RoundRobin":
            execution_df = pd.DataFrame(scheduler.execution_log)

            if execution_df.empty:
                st.error("No execution log data available for Round Robin.")
            else:
                execution_df['Start'] = pd.to_numeric(execution_df['Start'], errors='coerce')
                execution_df['Finish'] = pd.to_numeric(execution_df['Finish'], errors='coerce')
                execution_df['Time Slice'] = execution_df['Finish'] - execution_df['Start']
                execution_df['Remaining Time'] = pd.to_numeric(execution_df['Remaining Time'], errors='coerce')
                execution_df['Completed'] = execution_df['Remaining Time'] <= 0  
                execution_df["width"] = execution_df["Time Slice"]  

                fig = px.bar(
                    execution_df,
                    x="width",  
                    y="Job",
                    orientation='h',
                    color="Job",
                    base="Start",  
                    hover_data=["Time Slice", "Remaining Time", "Completed"],
                    title=f"{scheduler_name} Scheduling Gantt Chart",
                    labels={'width': 'Time Slice (Duration)', 'Start': 'Start Time', 'Job': 'Job'}
                )
        
        else:
            execution_df = pd.DataFrame(scheduler.completed_jobs)

            if execution_df.empty:
                st.error("No data was collected from the simulation.")
            else:
                execution_df['start_time'] = pd.to_numeric(execution_df['start_time'], errors='coerce')
                execution_df['completion_time'] = pd.to_numeric(execution_df['completion_time'], errors='coerce')
                execution_df["duration"] = execution_df["completion_time"] - execution_df["start_time"]

                fig = px.bar(
                    execution_df,
                    x="duration",
                    y="name",
                    orientation='h',
                    color="name",
                    base="start_time",
                    title=f"{scheduler_name} Scheduling Gantt Chart",
                    labels={'duration': 'Completion Time', 'start_time': 'Start Time', 'name': 'Job'}
                )

        fig.update_layout(
            xaxis_title="Time (seconds)",
            yaxis_title="Job",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

        avg_turnaround = execution_df["turnaround_time"].mean()
        avg_waiting = execution_df["waiting_time"].mean()

        col1, col2 = st.columns(2)
        col1.metric("Average Turnaround Time (sec)", f"{avg_turnaround:.2f}")
        col2.metric("Average Waiting Time (sec)", f"{avg_waiting:.2f}")

        st.subheader("Detailed Simulation Data")
        st.dataframe(execution_df, use_container_width=True)
