# Distributed-Systems
A comprehensive collection of distributed systems projects covering low-level socket programming, RESTful APIs, gRPC, middleware frameworks (Ice), and message brokers (RabbitMQ). Implemented across multiple languages including Python, Java, and Node.js.

---

## Task 1: Dual-Protocol Chat Application (TCP/UDP)

### Overview
A low-level socket programming project demonstrating a multi-client chat system that utilizes TCP and UDP protocols simultaneously. The server handles concurrent connections using multi-threading.

**Key features:**
* **TCP Communication:** Reliable, ordered delivery of standard chat messages between clients.
* **UDP Communication:** Connectionless, fast broadcasting of special payloads (custom ASCII art).
* **Concurrency:** Python's `threading` module handles non-blocking message reception and multiple client connections.
* **Resource Management:** Clean socket binding and closing using `contextlib` context managers.

### Technologies
* **Language:** Python
* **Core Libraries:** `socket`, `threading`, `contextlib`
* **Architecture:** Client-Server, Multi-threading

---

## Task 2: Space Radar RESTful API

### Overview
A REST API service built with FastAPI that aggregates data from public space APIs. It serves a static HTML client and provides an endpoint to fetch, process, and combine data about near-Earth objects and rocket launches for a specific date range.

**Key features:**
* **Third-Party Integrations:** Asynchronously fetches data from the NASA NEO API and The Space Devs API.
* **Asynchronous Processing:** Uses `httpx` and `asyncio.gather` to perform concurrent requests, reducing response time.
* **Data Processing:** Analyzes data to find the fastest potentially hazardous asteroid and filters rocket launches.
* **Security & Validation:** Implements custom API key authorization (`Asteroid-Api-Key`) and strictly validates input using Pydantic models.
* **Error Handling:** Robust exception handling that returns clean HTTP status codes to the frontend instead of raw server errors.

### Technologies
* **Backend:** Python, FastAPI, Uvicorn
* **HTTP Client:** `httpx` (Async)
* **Data Validation:** Pydantic
* **Frontend:** Static HTML, Vanilla JavaScript, CSS
* **Architecture:** REST API, API Gateway pattern

---

## Task 4: Space Transport Middleware (RabbitMQ)

### Overview
A message-oriented middleware system built with RabbitMQ that acts as a broker between Space Agencies and Space Transport Carriers. The project demonstrates advanced message routing, fair dispatching, and the integration of multiple messaging patterns within a single `topic` exchange.

**Key features:**
* **Topic Exchange Routing:** Utilizes dynamic routing keys (e.g., `task.cargo`, `ack.NASA`, `admin.all`) to intelligently route payloads between publishers and consumers.
* **Competing Consumers (Fair Dispatch):** Carriers subscribe to specific service queues. The system uses `basic_qos(prefetch_count=1)` to ensure tasks are strictly assigned to the first available (idle) carrier, preventing bottlenecking.
* **Request-Reply Pattern:** Agencies publish tasks with unique UUIDs to shared work queues and listen for asynchronous acknowledgments on temporary, exclusive, auto-generated queues.
* **Admin Intercept & Broadcast:** An administrative module uses a wildcard (`#`) binding to silently intercept all system traffic (spy mode) and can broadcast real-time messages to targeted user groups (agencies, carriers, or all).
* **Thread Safety:** Implements separate Pika connections and channels for consuming and publishing within `threading` contexts to ensure robust, non-blocking I/O operations without dropping streams.

### Technologies
* **Language:** Python
* **Message Broker:** RabbitMQ (Dockerized)
* **Core Libraries:** `pika`, `threading`, `json`, `uuid`
* **Architecture:** Message-Oriented Middleware (MOM), Pub/Sub, Work Queues