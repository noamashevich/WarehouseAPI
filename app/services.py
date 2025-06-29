import uuid
from app.db import get_db_connection

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


def assign_packages_to_truck_service(package_ids):
    if not package_ids:
        return {"status": 400, "body": {"error": "No package IDs provided"}}

    conn = get_db_connection()
    cursor = conn.cursor()

    placeholders = ','.join('?' for _ in package_ids)
    cursor.execute(f"""
        SELECT id, volume FROM Packages
        WHERE id IN ({placeholders}) AND assigned_truck_id IS NULL
    """, package_ids)
    packages = cursor.fetchall()

    if not packages:
        cursor.close()
        conn.close()
        return {"status": 404, "body": {"error": "No valid unassigned packages found"}}

    total_volume = sum(row["volume"] for row in packages)

    cursor.execute("""
        SELECT id, volume FROM Trucks
        WHERE available = 1
        ORDER BY ABS(volume - ?)
    """, (total_volume,))
    trucks = cursor.fetchall()

    if not trucks:
        cursor.close()
        conn.close()
        return {"status": 404, "body": {"error": "No available trucks"}}

    assigned_packages = []
    deferred_packages = []
    selected_truck = None

    for truck in trucks:
        truck_id, truck_volume = truck["id"], truck["volume"]
        ratio = total_volume / truck_volume

        if ratio >= 0.8 or total_volume <= truck_volume:
            current_volume = 0
            for pkg in packages:
                if current_volume + pkg["volume"] <= truck_volume:
                    cursor.execute("""
                        UPDATE Packages SET assigned_truck_id = ?
                        WHERE id = ?
                    """, (truck_id, pkg["id"]))
                    assigned_packages.append(pkg["id"])
                    current_volume += pkg["volume"]
                else:
                    deferred_packages.append(pkg["id"])

            cursor.execute("UPDATE Trucks SET available = 0 WHERE id = ?", (truck_id,))
            selected_truck = truck_id
            break

    conn.commit()
    cursor.close()
    conn.close()

    if selected_truck:
        return {
            "status": 200,
            "body": {
                "status": "assigned",
                "truck_id": selected_truck,
                "assigned_packages": assigned_packages,
                "deferred_packages": deferred_packages
            }
        }
    else:
        return {
            "status": 200,
            "body": {
                "status": "deferred",
                "assigned_packages": [],
                "deferred_packages": [pkg["id"] for pkg in packages]
            }
        }
