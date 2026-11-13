import os
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import psycopg
from fastmcp import FastMCP
from psycopg.rows import dict_row
from dotenv import load_dotenv


load_dotenv(Path(__file__).with_name(".env"))

mcp = FastMCP("Flight Booking Server")
TRAVEL_DATE_TIMEZONE = timezone(timedelta(hours=5, minutes=30))


def get_connection() -> psycopg.Connection[Any]:
    password = os.getenv("DB_PASSWORD")
    if not password:
        raise RuntimeError(
            "DB_PASSWORD is missing. Copy .env.example to .env and set your password."
        )

    try:
        port = int(os.getenv("DB_PORT", "5432"))
    except ValueError as exc:
        raise RuntimeError("DB_PORT must be a number.") from exc

    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=port,
        dbname=os.getenv("DB_NAME", "flight_booking"),
        user=os.getenv("DB_USER", "postgres"),
        password=password,
        row_factory=dict_row,
    )


@mcp.tool
def search_flights(origin: str, destination: str, travel_date: str) -> list[dict[str, Any]]:
    """Find flights with an available seat on a YYYY-MM-DD travel date (Asia/Kolkata)."""
    try:
        day = date.fromisoformat(travel_date)
    except ValueError as exc:
        raise ValueError("travel_date must use YYYY-MM-DD format.") from exc
    if day.isoformat() != travel_date:
        raise ValueError("travel_date must use YYYY-MM-DD format.")

    start = datetime.combine(day, time.min, tzinfo=TRAVEL_DATE_TIMEZONE)
    end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=TRAVEL_DATE_TIMEZONE)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, flight_number, departs_at, seats_left, status
                FROM flights
                WHERE origin = %s
                  AND destination = %s
                  AND departs_at >= %s
                  AND departs_at < %s
                  AND seats_left > 0
                ORDER BY departs_at
                """,
                (origin, destination, start, end),
            )
            flights = cursor.fetchall()

    return [
        {
            "flight_id": flight["id"],
            "flight_number": flight["flight_number"],
            "departure_time": flight["departs_at"].isoformat(),
            "available_seats": flight["seats_left"],
            "status": flight["status"],
        }
        for flight in flights
    ]


@mcp.tool
def book_flight(
    flight_id: int, passenger_name: str, passenger_email: str
) -> dict[str, Any]:
    """Book one available seat and return its unique booking reference."""
    passenger_name = passenger_name.strip()
    passenger_email = passenger_email.strip()
    if not passenger_name or not passenger_email:
        raise ValueError("Passenger name and email must not be empty.")

    booking_reference = f"FB{uuid4().hex[:16].upper()}"

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE flights
                SET seats_left = seats_left - 1
                WHERE id = %s AND seats_left > 0
                RETURNING flight_number
                """,
                (flight_id,),
            )
            flight = cursor.fetchone()

            if flight is None:
                cursor.execute("SELECT id FROM flights WHERE id = %s", (flight_id,))
                if cursor.fetchone() is None:
                    return {"success": False, "message": "Flight not found."}
                return {"success": False, "message": "No seats are available."}

            cursor.execute(
                """
                INSERT INTO bookings (reference, flight_id, passenger_name, passenger_email)
                VALUES (%s, %s, %s, %s)
                """,
                (booking_reference, flight_id, passenger_name, passenger_email),
            )

    return {
        "success": True,
        "booking_reference": booking_reference,
        "flight_number": flight["flight_number"],
    }


@mcp.tool
def get_flight_status(identifier: str) -> dict[str, Any]:
    """Get status and delay information using a flight number or booking reference."""
    identifier = identifier.strip()
    if not identifier:
        raise ValueError("Enter a flight number or booking reference.")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT f.flight_number, f.status, f.delay_minutes
                FROM bookings AS b
                JOIN flights AS f ON f.id = b.flight_id
                WHERE b.reference = %s
                """,
                (identifier,),
            )
            flight = cursor.fetchone()

            if flight is None:
                cursor.execute(
                    """
                    SELECT flight_number, status, delay_minutes
                    FROM flights
                    WHERE flight_number = %s
                    """,
                    (identifier,),
                )
                flight = cursor.fetchone()

    if flight is None:
        return {"found": False, "message": "No matching flight or booking was found."}

    return {
        "found": True,
        "flight_number": flight["flight_number"],
        "status": flight["status"],
        "delay_minutes": flight["delay_minutes"],
    }


if __name__ == "__main__":
    mcp.run()
