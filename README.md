# Adaptive-Scheduling-Simulation

## 📌 Overview
This repository contains the implementation of a discrete-event simulation framework** for **adaptive CPU scheduling** in operating systems. The framework evaluates multiple scheduling algorithms, including First-Come-First-Serve (FCFS), Shortest Job First (SJF), Round Robin (RR), and Adaptive Round Robin (ARR). 

This project was developed as part of ECS 251 – Operating Systems to analyze the impact of dynamic quantum adjustments in scheduling.  

---

## 📂 Code Structure

- **`simulation.py`** → The main simulation framework using `SimPy`, handling process execution and logging.  
- **`fcfs.py`** → Implements **First-Come-First-Serve (FCFS)** scheduling.  
- **`sjf.py`** → Implements **Shortest Job First (SJF)** scheduling.  
- **`preemptive_sjf.py`** → Implements **Preemptive Shortest Job First**, where a new process with a shorter burst can interrupt.  
- **`round_robin.py`** → Implements **Round Robin (RR)** scheduling with a **fixed time quantum.**  
- **`adaptive_rr.py`** → Implements **Adaptive Round Robin (ARR)** scheduling, where **the quantum dynamically adjusts based on workload behavior.**  
- **`dashboard.py`** → The **Streamlit-based visualization tool** that provides:  
  - **Gantt Charts** for process execution  
  - **Performance metrics** (average waiting time, turnaround time)  
  - **Algorithm comparisons**  

---

## How to Set Up and Run the Project Locally

### **Install Python **
Make sure you have **Python 3.8 or higher** installed. If not, install it from:  
🔗 [Python Downloads](https://www.python.org/downloads/)  

### **Clone this repository **
Open a terminal and run the following commands: git clone https://github.com/shrayarora8/Adaptive-Scheduling-Simulation.git

### **Set Up a Virtual Environment **
Create and activate a virtual environment as follows:
cd Adaptive-Scheduling-Simulation
python -m venv venv  
source venv/bin/activate  # Mac/Linux  
venv\Scripts\activate  # Windows

Once done, install required dependencies like:
pip install simpy streamlit plotly pandas

### **Download and Place the Dataset **
Since GitHub does not allow files larger than 100MB, the dataset must be manually downloaded and placed in the correct location.
1. Download the dataset from Google Drive: https://drive.google.com/file/d/1EI16GfKXVSyd3xSmoR9WEkHnDRB8_fDR/view?usp=sharing
2. Move the file into the src/ folder inside your cloned repository

### **Run the Scheduling Simulation (Command-Line Mode) **
To execute the scheduling simulation without the dashboard, run: python simulation.py
This will run the scheduling framework in the terminal and log execution details

### **Launch the Dashboard (Visualization Mode) **
To visualize scheduling performance with Gantt charts and statistics, run: streamlit run dashboard.py
This will start a web-based dashboard where you can select a scheduler, view process execution, and analyze results.


