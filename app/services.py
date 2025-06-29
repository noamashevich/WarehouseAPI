import uuid
from app.db import get_db_connection

# Add Truck
def add_truck_service(data):
    try:
        length = float(data['length'])
        width = float(data['width'])
        height = float(data['height'])

        if length <= 0 or width <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive")

        volume = length * width * height
        truck_id = str(uuid.uuid4())

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Trucks (id, length, width, height, volume, available)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (truck_id, length, width, height, volume))
        conn.commit()
        cursor.close()
        conn.close()

        return {"status": 201, "body": {"status": "created", "truck_id": truck_id}}

    except Exception as e:
        return {"status": 400, "body": {"error": str(e)}}


# Add Package
def add_package_service(data):
    try:
        length = float(data['length'])
        width = float(data['width'])
        height = float(data['height'])

        if length <= 0 or width <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive")

        volume = length * width * height
        package_id = str(uuid.uuid4())

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Packages (id, length, width, height, volume)
            VALUES (?, ?, ?, ?, ?)
        """, (package_id, length, width, height, volume))
        conn.commit()
        cursor.close()
        conn.close()

        return {"status": 201, "body": {"status": "created", "package_id": package_id}}

    except Exception as e:
        return {"status": 400, "body": {"error": str(e)}}


# Assign Packages to Truck – Bin Packing (First Fit)
def assign_packages_to_truck_service(package_ids):
    if not package_ids:
        return {"status": 400, "body": {"error": "No package IDs provided"}}

    conn = get_db_connection()
    cursor = conn.cursor()

    # Load packages
    placeholders = ','.join('?' for _ in package_ids)
    cursor.execute(f"""
        SELECT id, length, width, height, volume FROM Packages
        WHERE id IN ({placeholders}) AND assigned_truck_id IS NULL
    """, package_ids)
    packages = cursor.fetchall()

    if not packages:
        cursor.close()
        conn.close()
        return {"status": 404, "body": {"error": "No valid unassigned packages found"}}

    # Sort packages by volume descending (First-Fit Decreasing)
    packages = sorted(packages, key=lambda p: p["volume"], reverse=True)

    # Load available trucks
    cursor.execute("""
        SELECT id, length, width, height FROM Trucks
        WHERE available = 1
    """)
    trucks = cursor.fetchall()

    if not trucks:
        cursor.close()
        conn.close()
        return {"status": 404, "body": {"error": "No available trucks"}}

    # Track truck usage (simple 1D along length)
    truck_usage = {
        truck["id"]: {
            "max_length": truck["length"],
            "used_length": 0,
            "assigned": []
        } for truck in trucks
    }

    assigned = []
    deferred = []

    for pkg in packages:
        pkg_length = pkg["length"]
        placed = False

        for truck_id, usage in truck_usage.items():
            if usage["used_length"] + pkg_length <= usage["max_length"]:
                usage["assigned"].append(pkg["id"])
                usage["used_length"] += pkg_length
                assigned.append((pkg["id"], truck_id))
                placed = True
                break

        if not placed:
            deferred.append(pkg["id"])

    # Update DB
    for pkg_id, truck_id in assigned:
        cursor.execute("""
            UPDATE Packages SET assigned_truck_id = ? WHERE id = ?
        """, (truck_id, pkg_id))

    # Mark trucks as unavailable if anything was assigned
    for truck_id, usage in truck_usage.items():
        if usage["assigned"]:
            cursor.execute("UPDATE Trucks SET available = 0 WHERE id = ?", (truck_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "status": 200,
        "body": {
            "status": "assigned" if assigned else "deferred",
            "assigned_packages": [pkg for pkg, _ in assigned],
            "deferred_packages": deferred
        }
    }
