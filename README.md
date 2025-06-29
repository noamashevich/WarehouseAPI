#  Warehouse API (Package & Truck Assignment)

This project implements a **warehouse backend system** that assigns packages to trucks based on their volume. It ensures optimal truck utilization and supports deferral when packages cannot be fully assigned.

---

##  Features

- Add and manage **trucks** and **packages**
- **Assign packages** to the most suitable truck (≥80% full by volume)
- **Partial loading**: assign as much as possible and defer the rest
- Uses **SQLite** for local persistence (easy to swap with MSSQL)
- **Flask-based API** with modular architecture and error handling

---

##  Technologies Used

- **Python 3.10+**
- **Flask** – REST API Framework
- **SQLite** – Lightweight database (`warehouse.db`)
- **Postman** – for testing API requests

---

##  Project Structure

```
WarehouseAPI/
├── app/
│   ├── __init__.py
│   ├── db.py                # DB connection (SQLite)
│   ├── routes.py            # API endpoints
│   ├── services.py          # Business logic
├── run.py                   # Starts Flask app
├── init_db.py               # Initializes DB schema
├── warehouse.db             # SQLite DB file
├── requirements.txt
├── README.md
```

---

##  How It Works

- You add **trucks** and **packages** via API endpoints
- When calling `/assign-truck`, you provide package IDs
- The system looks for a **truck that is ≥80% full** with the selected packages
- If a truck is found → packages are assigned
- If volume exceeds capacity → assigns partially and defers the rest
- If no truck matches → all packages are deferred

---

## ⚙️ Installation

1. **Clone and setup environment**
```bash
git clone https://github.com/YOUR_USERNAME/WarehouseAPI.git
cd WarehouseAPI

# Optional: create virtual env
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

2. **Initialize the database**
```bash
python init_db.py
```

3. **Run the Flask server**
```bash
python run.py
```

> Runs at: `http://127.0.0.1:5000`

---

## 🔧 Configuration (SQLite-based)

No setup required – DB file `warehouse.db` is created automatically. You can later replace `app/db.py` logic to use **MSSQL**.

---

##  Input & Output

### + Add Truck – `POST /add-truck`
```json
{
  "length": 5,
  "width": 2,
  "height": 2
}
```
**Response:**
```json
{
  "truck_id": "uuid...",
  "status": "created"
}
```

---

### + Add Package – `POST /add-package`
```json
{
  "length": 1,
  "width": 1,
  "height": 2
}
```
**Response:**
```json
{
  "package_id": "uuid...",
  "status": "created"
}
```

---

###  Assign Packages – `POST /assign-truck`
```json
{
  "package_ids": ["uuid-1", "uuid-2"]
}
```
**Response (assigned):**
```json
{
  "status": "assigned",
  "truck_id": "uuid...",
  "assigned_packages": [...],
  "deferred_packages": [...]
}
```

**Response (deferred):**
```json
{
  "status": "deferred",
  "assigned_packages": [],
  "deferred_packages": [...]
}
```

---

##  How to Run (Step-by-Step)

1. Start the server:
```bash
python run.py
```

2. Test with Postman or curl:
```bash
curl -X POST http://localhost:5000/add-truck -H "Content-Type: application/json" -d '{"length": 5, "width": 2, "height": 2}'
```

3. Use `/assign-truck` with real package IDs from `/add-package` responses.

---

## Crash & Error Handling

| Case                     | Status Code | Message                                |
|--------------------------|-------------|----------------------------------------|
| Invalid or missing data | 400         | `{ "error": "..." }`                   |
| No available trucks      | 404         | `{ "error": "No available trucks" }`   |
| No valid packages        | 404         | `{ "error": "No valid packages" }`     |

---
### Bin Packing Logic (Work Item 3 – Bonus)

To reflect real-world physical constraints, the system implements a **First-Fit Decreasing Bin Packing** heuristic:

- Packages are sorted by volume in descending order.
- Each package is assigned to the **first truck** that has enough remaining length to accommodate it.
- The strategy simulates linear space (1D bin packing), where packages are placed sequentially along the truck's length.

#### Trade-offs:
- This approach simplifies spatial constraints (ignores width/height stacking).
- It is efficient and fast (`O(n * m)`) and works well under typical warehouse conditions.
- It avoids overfitting by focusing on a single dimension (length), which balances accuracy and performance.


##  Notes

- Uses `uuid.uuid4()` for unique IDs
- Volume is computed in Python: `length × width × height`
- Database logic is modular and can be replaced with MSSQL

---
