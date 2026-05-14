"""
init_db.py

This script initializes the SQLite database for the Smart Home system.
It creates all required tables for storing sensor data and event logs.

Author: Memory Moyo
Project: EPG317E IoT Smart Home
"""

import sqlite3
from sqlite3 import Error


def create_connection(db_file: str):
    """
    Create a connection to the SQLite database.

    Args:
        db_file (str): Path to the database file.

    Returns:
        sqlite3.Connection: Database connection object or None.
    """
    try:
        connection = sqlite3.connect(db_file)
        print("✅ Connected to database successfully")
        return connection
    except Error as e:
        print(f"❌ Error connecting to database: {e}")
        return None


def create_tables(connection):
    """
    Create required tables in the database.

    Tables:
        - sensor_data: Stores sensor readings
        - events: Stores system events (e.g., motion, alarms)
    """
    try:
        cursor = connection.cursor()

        # Create sensor_data table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sensor_type TEXT NOT NULL,
            value REAL NOT NULL
        );
        """)

        # Create events table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            value TEXT
        );
        """)

        connection.commit()
        print("✅ Tables created successfully")

    except Error as e:
        print(f"❌ Error creating tables: {e}")


def main():
    """
    Main function to initialize the database.
    """
    database = "smart_home.db"

    connection = create_connection(database)

    if connection is not None:
        create_tables(connection)
        connection.close()
        print("✅ Database setup complete")
    else:
        print("❌ Failed to create database connection")


if __name__ == "__main__":
    main()