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