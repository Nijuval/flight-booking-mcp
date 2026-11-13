
-- Flight Booking MCP Server
-- PostgreSQL database schema

-- 1. Flights table
CREATE TABLE IF NOT EXISTS public.flights (
    id SERIAL PRIMARY KEY,
    flight_number VARCHAR(20) NOT NULL,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    departs_at TIMESTAMPTZ NOT NULL,
    seats_left INTEGER NOT NULL CHECK (seats_left >= 0),
    status VARCHAR(20) DEFAULT 'on_time'
        CHECK (status IN (
            'on_time',
            'delayed',
            'cancelled',
            'departed',
            'landed'
        )),
    delay_minutes INTEGER DEFAULT 0
);

-- 2. Bookings table
CREATE TABLE IF NOT EXISTS public.bookings (
    id SERIAL PRIMARY KEY,
    reference VARCHAR(30) NOT NULL UNIQUE,
    flight_id INTEGER REFERENCES public.flights(id),
    passenger_name VARCHAR(100) NOT NULL,
    passenger_email VARCHAR(150) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    agent_name VARCHAR(100)
);
