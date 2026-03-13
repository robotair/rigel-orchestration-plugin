# Rigel Orchestration Plugin - Examples Guide

This guide walks through 6 complete examples demonstrating how to use the Rigel Kubernetes Orchestration Plugin with ROS1 and ROS2 applications. Each example can be run locally with Docker Compose or deployed to Kubernetes via the plugin.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [ROS1 vs ROS2 Key Differences](#ros1-vs-ros2-key-differences)
- [Example 1: ROS1 Publisher/Subscriber](#example-1-ros1-publishersubscriber)
- [Example 2: ROS1 Service (Client/Server)](#example-2-ros1-service-clientserver)
- [Example 3: ROS1 Actions (Client/Server)](#example-3-ros1-actions-clientserver)
- [Example 4: ROS2 Publisher/Subscriber](#example-4-ros2-publishersubscriber)
- [Example 5: ROS2 Service (Client/Server)](#example-5-ros2-service-clientserver)
- [Example 6: ROS2 Actions (Client/Server)](#example-6-ros2-actions-clientserver)
- [Verification & Debugging](#verification--debugging)

---

## Prerequisites

Before running any example, ensure you have:

1. **Python 3.10+** with [uv](https://docs.astral.sh/uv/)
2. **Docker** and **Docker Compose** for local testing
3. **Kubernetes cluster** for K8s deployment ([Minikube](https://minikube.sigs.k8s.io/docs/), [kind](https://kind.sigs.k8s.io/), or cloud provider)
4. **kubectl** configured to access your cluster

### Installation

```bash
git clone https://github.com/your-org/rigel-orchestration-plugin.git
cd rigel-orchestration-plugin
uv venv
```

---

### Step 1: Verify the Plugin Works

Run this first — before any example — to confirm the plugin and its dependencies are healthy:

```bash
uv run pytest tests/ -v
```

**Expected output:**

```
tests/test_models.py::test_...   PASSED
...
11 passed
```

All tests should pass.

---

### Step 2: Local Testing with Docker Compose

Each example includes a `docker-compose.yaml` for local testing without Kubernetes. This is the fastest way to verify the ROS communication logic works:

```bash
# Run any example locally (no Kubernetes needed)
cd examples/ros1/pubsub
docker compose up --build

# Clean up
docker compose down
```

Optional for ROS1 examples: run local tests through Rigel's Compose plugin:

```bash
cd examples/ros1/pubsub
uv run rigel run sequence local_test
```

This sequence runs `build -> compose_local` from the example `Rigelfile`.

> **ROS2 note:** the current Rigel Compose plugin in this environment always starts `roscore`, so the `local_test` sequence is only enabled for ROS1 examples.

> **ROS1 Note:** ROS1 nodes using `rospy.loginfo()` write to log files inside containers,
> not stdout. Use `docker exec` to view logs (see each example's "Local Testing" section).

---

### Step 3: Kubernetes Deployment

All K8s deployment commands run **from the example directory** (e.g. `examples/ros2/pubsub/`).

#### 3a. Build the Docker image

Use the `build` job defined in each Rigelfile:

```bash
cd examples/ros2/pubsub
uv run rigel run job build
```

Optional: generate the example root `Dockerfile` with Rigel before building:

```bash
uv run rigel run sequence generated_demo
```

This sequence runs `dockerfile -> build -> deploy_k8s`.

#### 3b. Load into Minikube (skip for remote clusters with a registry)

```bash
minikube image load rigel-ros2-pubsub:1.0.0
```

#### 3c. Deploy via the plugin

```bash
uv run rigel run job deploy_k8s
```

Or run both build and deploy in one command using the `demo` sequence:

```bash
# Note: for Minikube, run 3a and 3b first so the image is available before deploy
uv run rigel run sequence demo
```

---

### ROS1 Logging in Kubernetes

ROS1 nodes using `rospy.loginfo()` write to **log files**, not stdout. To view logs in K8s:

```bash
POD=$(kubectl get pod -l app=rigel-k8s-application -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD -- tail -f /root/.ros/log/<node_name>.log
```

---

## Project Structure

Each example follows the same layout:

```
examples/
├── ros1/
│   ├── pubsub/              # Example 1: Publisher/Subscriber
│   │   ├── publisher/
│   │   │   ├── publisher.py
│   │   │   └── Dockerfile       # For docker-compose local testing
│   │   ├── subscriber/
│   │   │   ├── subscriber.py
│   │   │   └── Dockerfile       # For docker-compose local testing
│   │   ├── Dockerfile           # Combined image for Kubernetes (both nodes)
│   │   ├── docker-compose.yaml  # Local multi-container testing
│   │   └── Rigelfile            # Kubernetes deployment config
│   ├── service/             # Example 2: Service Client/Server
│   └── action/              # Example 3: Action Client/Server (catkin build)
└── ros2/
    ├── pubsub/              # Example 4: Publisher/Subscriber
    ├── service/             # Example 5: Service Client/Server
    └── action/              # Example 6: Action Client/Server
```

### Two Dockerfiles per Example

| Dockerfile                                    | Purpose                             | Used By                   |
| --------------------------------------------- | ----------------------------------- | ------------------------- |
| `publisher/Dockerfile` or `server/Dockerfile` | Single-node image for local testing | `docker-compose.yaml`     |
| Root `Dockerfile`                             | Combined image (both nodes) for K8s | `docker build` in Step 3a |

---

## ROS1 vs ROS2 Key Differences

| Aspect             | ROS1 (Noetic)                        | ROS2 (Humble)                                  |
| ------------------ | ------------------------------------ | ---------------------------------------------- |
| **Discovery**      | ROS Master (`roscore`) — centralized | DDS (peer-to-peer) — decentralized             |
| **Plugin Config**  | `deploy_ros_master: true`            | `deploy_ros_master: false`                     |
| **Python Library** | `rospy`                              | `rclpy`                                        |
| **Build System**   | `catkin_make` (only for custom msgs) | `colcon` (not needed for `example_interfaces`) |
| **Base Image**     | `ros:noetic-ros-base`                | `ros:humble-ros-base`                          |
| **Logging**        | Log files (`~/.ros/log/`)            | stdout (`kubectl logs`)                        |
| **Network Config** | `ROS_MASTER_URI` + `ROS_IP`          | `ROS_DOMAIN_ID` + `RMW_IMPLEMENTATION`         |

### Rigelfile Configuration Comparison

`ros_version` is inferred automatically from `application.distro`.

**ROS1** — requires ROS Master:

```yaml
jobs:
  deploy_k8s:
    plugin: "src.plugin.OrchestrationPlugin"
    with:
      orchestration:
        deploy_ros_master: true # deploys roscore as a separate K8s deployment
        additional_k8s_params:
          application:
            spec:
              template:
                spec:
                  containers:
                    - name: "ros-app"
                      env:
                        - name: ROS_MASTER_URI
                          value: "http://ros-master:11311"
                        - name: ROS_IP # Use pod IP, NOT ROS_HOSTNAME
                          valueFrom:
                            fieldRef:
                              fieldPath: status.podIP
```

**ROS2** — no ROS Master, uses DDS:

```yaml
jobs:
  deploy_k8s:
    plugin: "src.plugin.OrchestrationPlugin"
    with:
      orchestration:
        deploy_ros_master: false # DDS handles discovery
        additional_k8s_params:
          application:
            spec:
              template:
                spec:
                  containers:
                    - name: "ros-app"
                      env:
                        - name: ROS_DOMAIN_ID
                          value: "0"
                        - name: RMW_IMPLEMENTATION
                          value: "rmw_fastrtps_cpp"
```

---

## Example 1: ROS1 Publisher/Subscriber

**Objective:** Verify communication between two ROS1 nodes using topics.

### How It Works

```
┌──────────────┐   /number_sequence   ┌──────────────┐
│  Publisher    │ ──── (Int32) ──────► │  Subscriber   │
│  Node        │      topic           │  Node         │
└──────┬───────┘                      └──────┬────────┘
       │           ┌──────────────┐          │
       └──────────►│  ROS Master  │◄─────────┘
                   │  (roscore)   │
                   └──────────────┘
```

- The **Publisher** sends incrementing integers (1, 2, 3, ...) to `/number_sequence` at 1Hz.
- The **Subscriber** receives and logs each message, detecting any missed numbers.
- Both nodes register with the **ROS Master** for topic discovery.

### Files

| File                                            | Description                                        |
| ----------------------------------------------- | -------------------------------------------------- |
| `examples/ros1/pubsub/publisher/publisher.py`   | Publishes `Int32` messages to `/number_sequence`   |
| `examples/ros1/pubsub/publisher/Dockerfile`     | Publisher container image (for docker-compose)     |
| `examples/ros1/pubsub/subscriber/subscriber.py` | Subscribes to `/number_sequence` and logs messages |
| `examples/ros1/pubsub/subscriber/Dockerfile`    | Subscriber container image (for docker-compose)    |
| `examples/ros1/pubsub/Dockerfile`               | Combined image for Kubernetes deployment           |
| `examples/ros1/pubsub/docker-compose.yaml`      | Local multi-container test setup                   |
| `examples/ros1/pubsub/Rigelfile`                | Rigel deployment configuration                     |

### Kubernetes Deploy

```bash
cd examples/ros1/pubsub

# 1. Build the combined image
uv run rigel run job build

# 2. Load into Minikube
minikube image load rigel-ros1-pubsub:1.0.0

# 3. Deploy to Kubernetes
uv run rigel run job deploy_k8s
```

### Verify on Kubernetes

```bash
POD=$(kubectl get pod -l app=rigel-k8s-application -o jsonpath='{.items[0].metadata.name}')

# View publisher logs (ROS1 logs go to files, not stdout)
kubectl exec $POD -- tail -f /root/.ros/log/number_publisher.log

# View subscriber logs
kubectl exec $POD -- tail -f /root/.ros/log/number_subscriber.log

# List topics via ROS Master
kubectl exec $POD -- bash -c "source /opt/ros/noetic/setup.bash && rostopic list"
```

---

## Example 2: ROS1 Service (Client/Server)

**Objective:** Verify communication between two ROS1 nodes using services.

### How It Works

```
┌──────────────┐   add_two_ints    ┌──────────────┐
│   Client     │ ── Request(a,b) ─►│   Server     │
│   Node       │◄── Response(sum)──│   Node       │
└──────┬───────┘     service       └──────┬────────┘
       │           ┌──────────────┐       │
       └──────────►│  ROS Master  │◄──────┘
                   │  (roscore)   │
                   └──────────────┘
```

- The **Server** provides the `add_two_ints` service — accepts two integers, returns their sum.
- The **Client** continuously calls the service with random integers (every 1 second).

### Files

| File                                        | Description                              |
| ------------------------------------------- | ---------------------------------------- |
| `examples/ros1/service/server/server.py`    | Provides `add_two_ints` service          |
| `examples/ros1/service/server/Dockerfile`   | Server container image                   |
| `examples/ros1/service/client/client.py`    | Calls the service with random integers   |
| `examples/ros1/service/client/Dockerfile`   | Client container image                   |
| `examples/ros1/service/Dockerfile`          | Combined image for Kubernetes deployment |
| `examples/ros1/service/docker-compose.yaml` | Local multi-container test setup         |
| `examples/ros1/service/Rigelfile`           | Rigel deployment configuration           |

### Kubernetes Deploy

```bash
# Clean up previous example first
kubectl delete deployment rigel-k8s-application --ignore-not-found
kubectl delete pvc --all --ignore-not-found

cd examples/ros1/service

# 1. Build the combined image
uv run rigel run job build

# 2. Load into Minikube
minikube image load rigel-ros1-service:1.0.0

# 3. Deploy to Kubernetes
uv run rigel run job deploy_k8s
```

### Verify on Kubernetes

```bash
POD=$(kubectl get pod -l app=rigel-k8s-application -o jsonpath='{.items[0].metadata.name}')

# View server logs (shows incoming requests)
kubectl exec $POD -- tail -f /root/.ros/log/add_two_ints_server.log

# View client logs (shows results)
kubectl exec $POD -- tail -f /root/.ros/log/add_two_ints_client.log

# List available services
kubectl exec $POD -- bash -c "source /opt/ros/noetic/setup.bash && rosservice list"
```

---

## Example 3: ROS1 Actions (Client/Server)

**Objective:** Verify communication between two ROS1 nodes using actions (long-running tasks with feedback).

### How It Works

```
┌──────────────┐     fibonacci      ┌──────────────┐
│   Client     │ ── Goal(order) ──►│   Server     │
│   Node       │◄── Feedback ──────│   Node       │
│              │◄── Result ────────│              │
└──────┬───────┘     action        └──────┬────────┘
       │           ┌──────────────┐       │
       └──────────►│  ROS Master  │◄──────┘
                   │  (roscore)   │
                   └──────────────┘
```

- The **Action Server** computes Fibonacci sequences with 1-second delays per step.
- The **Action Client** sends goals and receives **incremental feedback** as each number is computed.
- Uses a custom `Fibonacci.action` message type — requires `catkin_make` during the Docker build.

### Files

| File                                       | Description                                  |
| ------------------------------------------ | -------------------------------------------- |
| `examples/ros1/action/Fibonacci.action`    | Action definition (goal/result/feedback)     |
| `examples/ros1/action/server/server.py`    | Computes Fibonacci and sends feedback        |
| `examples/ros1/action/server/Dockerfile`   | Server image (build context: `action/` root) |
| `examples/ros1/action/client/client.py`    | Sends goals and prints feedback              |
| `examples/ros1/action/client/Dockerfile`   | Client image (build context: `action/` root) |
| `examples/ros1/action/Dockerfile`          | Combined image for Kubernetes deployment     |
| `examples/ros1/action/docker-compose.yaml` | Local multi-container test setup             |
| `examples/ros1/action/Rigelfile`           | Rigel deployment configuration               |

> **Note:** The server and client Dockerfiles use **build context: `.`** (the `action/` root directory)
> so that `catkin_make` can access `Fibonacci.action`, `package.xml`, and `CMakeLists.txt`.

### Local Testing (docker compose)

```bash
cd examples/ros1/action
docker compose up --build   # catkin_make runs during build (~30s first time)

# View logs (ROS1 writes to files, not stdout)
docker exec ros1_action_server bash -c 'tail -f ~/.ros/log/fibonacci_server.log'
docker exec ros1_action_client bash -c 'tail -f ~/.ros/log/fibonacci_client.log'

docker compose down
```

**Expected client log:**

```
[rosout][INFO] ...: Connected to 'fibonacci' action server.
[rosout][INFO] ...: Sending goal: Fibonacci(9)
[rosout][INFO] ...: [Result] Sequence: (0, 1, 1, 2, 3, 5, 8, 13, 21, 34)
...
```

**Expected server log:**

```
[rosout][INFO] ...: Fibonacci action server started.
[rosout][INFO] ...: Received goal: compute Fibonacci(9)
[rosout][INFO] ...: Feedback: [0, 1, 1]
...
[rosout][INFO] ...: Goal succeeded: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### Kubernetes Deploy

```bash
# Clean up previous example first
kubectl delete deployment rigel-k8s-application --ignore-not-found
kubectl delete pvc --all --ignore-not-found

cd examples/ros1/action

# 1. Build the combined image (catkin_make runs during build — takes ~30s)
uv run rigel run job build

# 2. Load into Minikube
minikube image load rigel-ros1-action:1.0.0

# 3. Deploy to Kubernetes
uv run rigel run job deploy_k8s
```

### Verify on Kubernetes

```bash
POD=$(kubectl get pod -l app=rigel-k8s-application -o jsonpath='{.items[0].metadata.name}')

# View server logs (shows goal processing and feedback)
kubectl exec $POD -- tail -f /root/.ros/log/fibonacci_server.log

# View client logs (shows goals sent, feedback received, and results)
kubectl exec $POD -- tail -f /root/.ros/log/fibonacci_client.log
```

---

## Example 4: ROS2 Publisher/Subscriber

**Objective:** Same as Example 1 but using ROS2 — no ROS Master needed.

### How It Works

```
┌──────────────┐   /number_sequence   ┌──────────────┐
│  Publisher    │ ──── (Int32) ──────► │  Subscriber   │
│  Node        │      topic           │  Node         │
└──────────────┘                      └───────────────┘
         ▲              DDS                    ▲
         └──────── Peer-to-Peer ───────────────┘
                   (no roscore!)
```

- Same functionality as Example 1, using **rclpy** instead of rospy.
- **No ROS Master** — nodes discover each other via DDS middleware.

### Key Code Differences from ROS1

| Aspect     | ROS1                                  | ROS2                                               |
| ---------- | ------------------------------------- | -------------------------------------------------- |
| Init       | `rospy.init_node("name")`             | `super().__init__("name")`                         |
| Publisher  | `rospy.Publisher(topic, type, queue)` | `self.create_publisher(type, topic, queue)`        |
| Subscriber | `rospy.Subscriber(topic, type, cb)`   | `self.create_subscription(type, topic, cb, queue)` |
| Timer      | `rospy.Rate(1); rate.sleep()`         | `self.create_timer(1.0, callback)`                 |
| Spin       | `rospy.spin()`                        | `rclpy.spin(node)`                                 |
| Log        | `rospy.loginfo(msg)`                  | `self.get_logger().info(msg)`                      |

### Files

| File                                            | Description                                        |
| ----------------------------------------------- | -------------------------------------------------- |
| `examples/ros2/pubsub/publisher/publisher.py`   | Publishes `Int32` messages to `/number_sequence`   |
| `examples/ros2/pubsub/publisher/Dockerfile`     | Publisher container image                          |
| `examples/ros2/pubsub/subscriber/subscriber.py` | Subscribes to `/number_sequence` and logs messages |
| `examples/ros2/pubsub/subscriber/Dockerfile`    | Subscriber container image                         |
| `examples/ros2/pubsub/Dockerfile`               | Combined image for Kubernetes deployment           |
| `examples/ros2/pubsub/docker-compose.yaml`      | Local multi-container test setup                   |
| `examples/ros2/pubsub/Rigelfile`                | Rigel deployment configuration                     |

### Local Testing (docker compose)

```bash
cd examples/ros2/pubsub
docker compose up --build

# ROS2 logs go to stdout — use docker compose logs
docker compose logs -f publisher
docker compose logs -f subscriber

docker compose down
```

**Expected output:**

```
ros2_publisher  | [INFO] [..] [number_publisher]: Publishing: 12
ros2_subscriber | [INFO] [..] [number_subscriber]: Received: 12 (total: 12)
ros2_publisher  | [INFO] [..] [number_publisher]: Publishing: 13
ros2_subscriber | [INFO] [..] [number_subscriber]: Received: 13 (total: 13)
...
```

### Kubernetes Deploy

```bash
# Clean up previous example (including ROS Master if switching from ROS1)
kubectl delete deployment rigel-k8s-application ros-master --ignore-not-found
kubectl delete service ros-master --ignore-not-found
kubectl delete pvc --all --ignore-not-found

cd examples/ros2/pubsub

# 1. Build the combined image
uv run rigel run job build

# 2. Load into Minikube
minikube image load rigel-ros2-pubsub:1.0.0

# 3. Deploy to Kubernetes
uv run rigel run job deploy_k8s
```

### Verify on Kubernetes

```bash
POD=$(kubectl get pod -l app=rigel-k8s-application -o jsonpath='{.items[0].metadata.name}')

# ROS2 logs go to stdout — kubectl logs works directly
kubectl logs -f $POD

# List topics via ROS2 CLI
kubectl exec $POD -- bash -c "source /opt/ros/humble/setup.bash && ros2 topic list"

# Echo the topic
kubectl exec $POD -- bash -c "source /opt/ros/humble/setup.bash && ros2 topic echo /number_sequence"
```

> **Note:** Unlike ROS1, ROS2 logs go to stdout so `kubectl logs` works directly.

---

## Example 5: ROS2 Service (Client/Server)

**Objective:** Same as Example 2 but using ROS2.

### How It Works

```
┌──────────────┐   add_two_ints    ┌──────────────┐
│   Client     │ ── Request(a,b) ─►│   Server     │
│   Node       │◄── Response(sum)──│   Node       │
└──────────────┘     service       └──────────────┘
         ▲              DDS               ▲
         └──────── Peer-to-Peer ──────────┘
```

- Uses `example_interfaces.srv.AddTwoInts` (standard ROS2 package — no catkin build needed).
- Client uses **async service calls with futures** instead of synchronous `ServiceProxy`.

### Key Code Differences from ROS1

| Aspect         | ROS1                             | ROS2                                  |
| -------------- | -------------------------------- | ------------------------------------- |
| Service type   | `rospy_tutorials.srv.AddTwoInts` | `example_interfaces.srv.AddTwoInts`   |
| Create service | `rospy.Service(name, type, cb)`  | `self.create_service(type, name, cb)` |
| Callback       | `def handle(req)`                | `def handle(request, response)`       |
| Client         | `rospy.ServiceProxy(name, type)` | `self.create_client(type, name)`      |
| Call           | `proxy(a, b)` (sync)             | `client.call_async(request)` (async)  |

### Files

| File                                        | Description                              |
| ------------------------------------------- | ---------------------------------------- |
| `examples/ros2/service/server/server.py`    | Provides `add_two_ints` service          |
| `examples/ros2/service/server/Dockerfile`   | Server container image                   |
| `examples/ros2/service/client/client.py`    | Calls the service with random integers   |
| `examples/ros2/service/client/Dockerfile`   | Client container image                   |
| `examples/ros2/service/Dockerfile`          | Combined image for Kubernetes deployment |
| `examples/ros2/service/docker-compose.yaml` | Local multi-container test setup         |
| `examples/ros2/service/Rigelfile`           | Rigel deployment configuration           |

### Local Testing (docker compose)

```bash
cd examples/ros2/service
docker compose up --build

docker compose logs -f server
docker compose logs -f client

docker compose down
```

**Expected output:**

```
ros2_service_server | [INFO] [..] [add_two_ints_server]: Request: 60 + 90 = 150
ros2_service_client | [INFO] [..] [add_two_ints_client]: Result: 60 + 90 = 150
...
```

### Kubernetes Deploy

```bash
kubectl delete deployment rigel-k8s-application --ignore-not-found
kubectl delete pvc --all --ignore-not-found

cd examples/ros2/service

# 1. Build the combined image
uv run rigel run job build

# 2. Load into Minikube
minikube image load rigel-ros2-service:1.0.0

# 3. Deploy to Kubernetes
uv run rigel run job deploy_k8s
```

### Verify on Kubernetes

```bash
POD=$(kubectl get pod -l app=rigel-k8s-application -o jsonpath='{.items[0].metadata.name}')

# ROS2 logs go to stdout
kubectl logs -f $POD

# List services
kubectl exec $POD -- bash -c "source /opt/ros/humble/setup.bash && ros2 service list"

# Call the service manually
kubectl exec $POD -- bash -c "source /opt/ros/humble/setup.bash && ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts '{a: 10, b: 20}'"
```

---

## Example 6: ROS2 Actions (Client/Server)

**Objective:** Same as Example 3 but using ROS2.

### How It Works

```
┌──────────────┐     fibonacci      ┌──────────────┐
│   Client     │ ── Goal(order) ──►│   Server     │
│   Node       │◄── Feedback ──────│   Node       │
│              │◄── Result ────────│              │
└──────────────┘     action        └──────────────┘
         ▲              DDS               ▲
         └──────── Peer-to-Peer ──────────┘
```

- Uses `example_interfaces.action.Fibonacci` (standard ROS2 — no catkin build needed).
- Server uses **async execute callback** with explicit goal/cancel handling.
- Client uses **futures and callbacks** for non-blocking goal submission.

### Key Code Differences from ROS1

| Aspect       | ROS1                              | ROS2                                          |
| ------------ | --------------------------------- | --------------------------------------------- |
| Server class | `actionlib.SimpleActionServer`    | `rclpy.action.ActionServer`                   |
| Client class | `actionlib.SimpleActionClient`    | `rclpy.action.ActionClient`                   |
| Execute      | `execute_cb(goal)` (sync)         | `async execute_callback(goal_handle)`         |
| Preemption   | `is_preempt_requested()`          | `goal_handle.is_cancel_requested`             |
| Success      | `set_succeeded(result)`           | `goal_handle.succeed(); return result`        |
| Send goal    | `send_goal(goal, feedback_cb=cb)` | `send_goal_async(goal, feedback_callback=cb)` |

### Files

| File                                       | Description                              |
| ------------------------------------------ | ---------------------------------------- |
| `examples/ros2/action/server/server.py`    | Computes Fibonacci with async feedback   |
| `examples/ros2/action/server/Dockerfile`   | Server container image                   |
| `examples/ros2/action/client/client.py`    | Sends goals and receives feedback        |
| `examples/ros2/action/client/Dockerfile`   | Client container image                   |
| `examples/ros2/action/Dockerfile`          | Combined image for Kubernetes deployment |
| `examples/ros2/action/docker-compose.yaml` | Local multi-container test setup         |
| `examples/ros2/action/Rigelfile`           | Rigel deployment configuration           |

### Local Testing (docker compose)

```bash
cd examples/ros2/action
docker compose up --build

docker compose logs -f server
docker compose logs -f client

docker compose down
```

**Expected output:**

```
ros2_action_server | [INFO] [..] [fibonacci_server]: Fibonacci action server started.
ros2_action_client | [INFO] [..] [fibonacci_client]: Sending goal: Fibonacci(9)
ros2_action_server | [INFO] [..] [fibonacci_server]: Received goal: compute Fibonacci(9)
ros2_action_server | [INFO] [..] [fibonacci_server]: Feedback: [0, 1, 1]
ros2_action_server | [INFO] [..] [fibonacci_server]: Feedback: [0, 1, 1, 2]
...
ros2_action_server | [INFO] [..] [fibonacci_server]: Goal succeeded: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

> **Note:** The `example_interfaces.action.Fibonacci` feedback field is named `sequence`
> (not `partial_sequence` as in the custom ROS1 action definition).

### Kubernetes Deploy

```bash
kubectl delete deployment rigel-k8s-application --ignore-not-found
kubectl delete pvc --all --ignore-not-found

cd examples/ros2/action

# 1. Build the combined image
uv run rigel run job build

# 2. Load into Minikube
minikube image load rigel-ros2-action:1.0.0

# 3. Deploy to Kubernetes
uv run rigel run job deploy_k8s
```

### Verify on Kubernetes

```bash
POD=$(kubectl get pod -l app=rigel-k8s-application -o jsonpath='{.items[0].metadata.name}')

# ROS2 logs go to stdout
kubectl logs -f $POD

# List actions
kubectl exec $POD -- bash -c "source /opt/ros/humble/setup.bash && ros2 action list"

# Send a goal manually
kubectl exec $POD -- bash -c "source /opt/ros/humble/setup.bash && ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci '{order: 5}' --feedback"
```

---

## Verification & Debugging

### Common Commands

```bash
# Get the pod name
POD=$(kubectl get pod -l app=rigel-k8s-application -o jsonpath='{.items[0].metadata.name}')

# Check pod status
kubectl get pods -l app=rigel-k8s-application
kubectl get pods -l app=ros-master    # ROS1 only

# Check all resources created by the plugin
kubectl get all | grep -E "rigel|ros-master"

# Pod detailed info (events, readiness probe status)
kubectl describe pod $POD

# View ROS1 node logs (logs go to files, not stdout)
kubectl exec $POD -- tail -f /root/.ros/log/<node_name>.log

# View ROS2 logs (go to stdout)
kubectl logs -f $POD

# Check ROS Master logs (ROS1 only)
kubectl logs -f deployment/ros-master

# Interactive shell into the pod
kubectl exec -it $POD -- bash
```

### Cleanup Between Examples

```bash
# Delete application deployment (keeps ROS Master for the next ROS1 example)
kubectl delete deployment rigel-k8s-application --ignore-not-found
kubectl delete pvc --all --ignore-not-found

# Full cleanup (when switching from ROS1 to ROS2, or done testing)
kubectl delete deployment rigel-k8s-application ros-master --ignore-not-found
kubectl delete service ros-master --ignore-not-found
kubectl delete pvc --all --ignore-not-found
kubectl delete pv --all --ignore-not-found
```

---

## Summary Table

| #   | Pattern | ROS Version | ROS Master | Discovery   | Local Test          | K8s Image                  |
| --- | ------- | ----------- | ---------- | ----------- | ------------------- | -------------------------- |
| 1   | Pub/Sub | ROS1        | Yes        | Centralized | `docker compose up` | `rigel-ros1-pubsub:1.0.0`  |
| 2   | Service | ROS1        | Yes        | Centralized | `docker compose up` | `rigel-ros1-service:1.0.0` |
| 3   | Action  | ROS1        | Yes        | Centralized | `docker compose up` | `rigel-ros1-action:1.0.0`  |
| 4   | Pub/Sub | ROS2        | No         | DDS P2P     | `docker compose up` | `rigel-ros2-pubsub:1.0.0`  |
| 5   | Service | ROS2        | No         | DDS P2P     | `docker compose up` | `rigel-ros2-service:1.0.0` |
| 6   | Action  | ROS2        | No         | DDS P2P     | `docker compose up` | `rigel-ros2-action:1.0.0`  |
