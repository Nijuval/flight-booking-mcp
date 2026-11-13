
# Flight Booking MCP Server

A Python-based Flight Booking Server built using the Model Context Protocol (MCP) and PostgreSQL.

This project allows an AI assistant to interact with a flight booking database through MCP tools. Users can search for available flights, book seats, and check flight status using natural language.

## Features

- Search available flights by origin, destination, and travel date.
- Book a flight using passenger details.
- Generate unique booking references.
- Check flight status using a flight number or booking reference.
- PostgreSQL database integration.
- Atomic seat updates to prevent overbooking.
- MCP integration with Visual Studio Code and GitHub Copilot.

## Technology Stack

- Python
- Model Context Protocol (MCP)
- FastMCP
- PostgreSQL
- Psycopg
- Visual Studio Code
- GitHub Copilot


## Project Architecture

The project follows a simple MCP-based architecture:

```text
User
  |
  v
AI Assistant (GitHub Copilot)
  |
  v
MCP Client (VS Code)
  |
  v
Flight Booking MCP Server
  |
  +-- search_flights
  |
  +-- book_flight
  |
  +-- get_flight_status
  |
  v
PostgreSQL Database
  |
  +-- flights
  |
  +-- bookings
```

## MCP Tools

| Tool | Description |
|---|---|
| `search_flights` | Searches flights by origin, destination and travel date. |
| `book_flight` | Books one available seat and generates a booking reference. |
| `get_flight_status` | Retrieves flight status using a flight number or booking reference. |


## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/flight-booking-mcp.git
cd flight-booking-mcp
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Update `.env` with your PostgreSQL credentials.


### 6. Configure PostgreSQL

Create a PostgreSQL database named:

```sql
CREATE DATABASE flight_booking;
```

Connect to the `flight_booking` database and execute the SQL commands in `schema.sql` to create the required tables.

Using pgAdmin:
1. Select the `flight_booking` database.
2. Open Query Tool.
3. Open or paste the contents of `schema.sql`.
4. Execute the script.

### 7. Run the MCP Server

```bash
python server.py
```

The server uses the standard input/output (stdio) transport and can connect to an MCP-compatible client.
