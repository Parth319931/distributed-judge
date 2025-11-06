# ⚖️ Distributed Judge — A Local Distributed Computing Code Evaluation Platform

**Distributed Judge** is a lightweight simulation of an **online coding test platform** (like LeetCode or HackerRank) designed to demonstrate **core distributed computing concepts** in Python.

This project runs fully **locally** — no Docker, AWS, or Hadoop required — and shows how multiple distributed nodes can coordinate tasks, synchronize clocks, elect leaders, maintain replication consistency, and balance load in real-time.

---

## 🚀 Features Implemented

| No. | Concept | Description |
|:---:|:---------|:-------------|
| 1️⃣ | **Remote Method Invocation (RMI)** | The backend exposes an XML-RPC style interface (`RMIServer`) that receives code submissions remotely and dispatches them to worker nodes. |
| 2️⃣ | **Multithreading** | Each node uses a thread pool to process multiple submissions concurrently, simulating a distributed code-execution environment. |
| 3️⃣ | **Clock Synchronization** | Implements a **Lamport logical clock** to maintain consistent event ordering across distributed evaluator nodes. |
| 4️⃣ | **Leader Election (Bully Algorithm)** | Nodes use the **Bully Election Algorithm** to elect a coordinator for control operations and metadata consistency. |
| 5️⃣ | **Data Consistency & Replication** | Problem/test data is replicated across nodes with eventual consistency — updates propagate automatically. |
| 6️⃣ | **Load Balancing & Failover** | Dynamic load distribution ensures each node gets fair workloads. If one node fails, its jobs are automatically rerouted to healthy nodes. |

---

## 🧠 System Architecture

```text
        +----------------+
        |  Frontend UI   |  <-- Streamlit app (user code, results)
        +--------+-------+
                 |
                 ↓
        +----------------+
        |   RMI Server   |  <-- Entry point (port 9000)
        +--------+-------+
                 |
        +--------+--------+--------+
        | Node 1 | Node 2 | Node 3 |
        | :9101  | :9102  | :9103  |
        +--------+--------+--------+
                 |  |  |
                 ↓  ↓  ↓
          (Clock sync, replication,
           election, load balancing) ```

Each node acts as a local microservice with its own port, queue, and heartbeat. The NodeManager oversees these nodes, performs leader election, and routes requests efficiently.

🧑‍💻 Tech Stack

| Layer                | Technology                                                                             | Purpose                                                  |
| -------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Frontend**         | [Streamlit](https://streamlit.io/)                                                     | User interface for submissions, results, and admin views |
| **Backend**          | Python (Socket / XML-RPC / Threading)                                                  | Core distributed logic, job execution, replication       |
| **Core Modules**     | `rmi_server`, `node_manager`, `election`, `replication`, `clock_sync`, `load_balancer` | Modular simulation of distributed systems                |
| **Logging**          | Custom `utils/logger.py`                                                               | Timestamped, colored logs of events                      |
| **Language Support** | Python                                                                                 | Code execution sandboxed locally                         |


⚙️ Setup Instructions
🐍 1. Clone the repository
git clone https://github.com/<your-username>/distributed-judge.git
cd distributed-judge

🧩 2. Set up the backend
cd backend
pip install -r requirements.txt   # or install manually: streamlit, flask, etc.
python main_backend.py


This starts the RMI server on 127.0.0.1:9000 and worker nodes on ports 9101–9103.

💻 3. Run the frontend

In a new terminal:

cd frontend
streamlit run app.py


The frontend UI will open in your browser at http://localhost:8501

🧪 Demonstrations
✅ Basic Workflow

Launch the backend.

Open the Streamlit app.

Log in with any username.

Choose a coding problem (e.g., Two Sum, FizzBuzz).

Submit your Python solution.

The backend distributes, executes, and returns the result via RMI.

⚙️ Failure & Recovery Simulation

Kill one node → backend detects failure via heartbeat.

Remaining nodes rebalance the load automatically.

When the node revives, it rejoins the cluster and resumes work.

🗳️ Leader Election

During startup or node failure, the BullyElection algorithm triggers.

The node with the highest ID becomes the leader and handles replication duties.

📂 Project Structure
distributed-judge/
├── backend/
│   ├── main_backend.py
│   ├── rmi_server.py
│   ├── node_manager.py
│   ├── election.py
│   ├── clock_sync.py
│   ├── replication.py
│   ├── load_balancer.py
│   └── utils/
│       └── logger.py
└── frontend/
    ├── app.py
    ├── pages/
    ├── utils/
    ├── assets/
    └── config.py

🧩 Distributed System Highlights

Fully local simulation of distributed computing principles.

Thread-safe execution model for job dispatching.

Automatic leader failover and recovery.

Clear visualization through Streamlit admin dashboard.

Excellent for education and demonstration of distributed systems.

📚 Learning Outcomes

By studying or running this project, you’ll understand:

How distributed coordination works (leader election & synchronization)

How to manage consistency in replicated data

How real systems (like LeetCode/HackerRank) might architect their backend job evaluators

How to apply distributed algorithms practically using Python

💡 Future Improvements

Add persistent storage (SQLite/Postgres) for submissions.

Integrate Docker containers for each node (optional).

Add real-time WebSocket logs to frontend.

Add multiple programming language support.

🧑‍🎓 Author

Parth Gandhi
🎓 B.Tech in Computer Engineering
💡 Passionate about Distributed Systems, Backend Development, and AI-driven Education Platforms.

🛠 License

MIT License © 2025 Parth Gandhi

🌟 Contributing

Pull requests are welcome!
For major changes, please open an issue first to discuss what you’d like to improve.

❤️ Acknowledgment

Built using Cursor IDE + GitHub Copilot, as part of learning and implementing Distributed Computing Concepts hands-on.