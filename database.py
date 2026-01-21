import sqlite3
from datetime import datetime

from car import Car, Dimensions


def create_tables(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS car (
                plate TEXT PRIMARY KEY,
                first_registered_in_norway TEXT,
                vehicle_category TEXT,
                dimension_width INTEGER,
                dimension_height INTEGER,
                dimension_length INTEGER,
                manufacturer_name TEXT,
                brand TEXT,
                model_name TEXT,
                driving_side TEXT,
                color_name TEXT,
                color_description TEXT,
                fuel_type TEXT,
                fuel_consumption_liter_per_10km REAL,
                wltp_combined_range_km INTEGER,
                transmission_type TEXT,
                maximum_speed_kmh INTEGER,
                inspection_due_date TEXT,
                last_inspection_approved_date TEXT,
                owner_registration_start_timestamp TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        _ensure_columns(conn, "car", {"created_at": "TEXT", "updated_at": "TEXT"})
        conn.commit()
    finally:
        conn.close()


def get_car_by_plate(db_path: str, plate: str) -> Car | None:
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT
                plate,
                first_registered_in_norway,
                vehicle_category,
                dimension_width,
                dimension_height,
                dimension_length,
                manufacturer_name,
                brand,
                model_name,
                driving_side,
                color_name,
                color_description,
                fuel_type,
                fuel_consumption_liter_per_10km,
                wltp_combined_range_km,
                transmission_type,
                maximum_speed_kmh,
                inspection_due_date,
                last_inspection_approved_date,
                owner_registration_start_timestamp
            FROM car
            WHERE plate = ?
            """,
            (plate,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        dimensions = Dimensions(row[3], row[4], row[5])
        return Car(
            row[0],
            row[1],
            row[2],
            dimensions,
            row[6],
            row[7],
            row[8],
            row[9],
            row[10],
            row[11],
            row[12],
            row[13],
            row[14],
            row[15],
            row[16],
            row[17],
            row[18],
            row[19],
        )
    finally:
        conn.close()


def insert_car(db_path: str, car: Car) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO car (
                plate,
                first_registered_in_norway,
                vehicle_category,
                dimension_width,
                dimension_height,
                dimension_length,
                manufacturer_name,
                brand,
                model_name,
                driving_side,
                color_name,
                color_description,
                fuel_type,
                fuel_consumption_liter_per_10km,
                wltp_combined_range_km,
                transmission_type,
                maximum_speed_kmh,
                inspection_due_date,
                last_inspection_approved_date,
                owner_registration_start_timestamp,
                created_at,
                updated_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                car.plate,
                car.first_registered_in_norway,
                car.vehicle_category,
                car.dimension.width,
                car.dimension.height,
                car.dimension.length,
                car.manufacturer_name,
                car.brand,
                car.model_name,
                car.driving_side,
                car.color_name,
                car.color_description,
                car.fuel_type,
                car.fuel_consumption_liter_per_10km,
                car.wltp_combined_range_km,
                car.transmission_type,
                car.maximum_speed_kmh,
                car.inspection_due_date,
                car.last_inspection_approved_date,
                car.owner_registration_start_timestamp,
                now,
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def _ensure_columns(conn: sqlite3.Connection, table: str, columns: dict[str, str]) -> None:
    cursor = conn.execute(f"PRAGMA table_info({table})")
    existing_columns = {row[1] for row in cursor.fetchall()}
    for name, column_type in columns.items():
        if name not in existing_columns:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {column_type}")
