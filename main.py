from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# -------------------- DATA --------------------
doctors = [
    {"id": 1, "name": "Dr. Ravi", "specialization": "Cardiologist", "fee": 500, "experience_years": 10, "is_available": True},
    {"id": 2, "name": "Dr. Meena", "specialization": "Dermatologist", "fee": 300, "experience_years": 6, "is_available": True},
    {"id": 3, "name": "Dr. John", "specialization": "General", "fee": 700, "experience_years": 12, "is_available": False},
    {"id": 4, "name": "Dr. Sara", "specialization": "Pediatrician", "fee": 400, "experience_years": 8, "is_available": True},
    {"id": 5, "name": "Dr. Khan", "specialization": "Cardiologist", "fee": 600, "experience_years": 15, "is_available": True},
    {"id": 6, "name": "Dr. Anil", "specialization": "General", "fee": 200, "experience_years": 5, "is_available": True},
]

appointments = []
appt_counter = 1

# -------------------- MODELS --------------------
class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = "in-person"
    senior_citizen: bool = False

class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience_years: int = Field(..., gt=0)
    is_available: bool = True

# -------------------- HELPERS --------------------
def find_doctor(doctor_id):
    for d in doctors:
        if d["id"] == doctor_id:
            return d
    return None

def calculate_fee(base_fee, appointment_type, senior=False):
    if appointment_type == "video":
        fee = base_fee * 0.8
    elif appointment_type == "emergency":
        fee = base_fee * 1.5
    else:
        fee = base_fee

    if senior:
        fee *= 0.85

    return base_fee, round(fee)

def filter_doctors_logic(specialization, max_fee, min_experience, is_available):
    result = []
    for d in doctors:
        if specialization is not None and d["specialization"] != specialization:
            continue
        if max_fee is not None and d["fee"] > max_fee:
            continue
        if min_experience is not None and d["experience_years"] < min_experience:
            continue
        if is_available is not None and d["is_available"] != is_available:
            continue
        result.append(d)
    return result

# -------------------- DAY 1 --------------------
@app.get("/")
def home():
    return {"message": "Welcome to MediCare Clinic"}

@app.get("/doctors")
def get_doctors():
    available = sum(1 for d in doctors if d["is_available"])
    return {"total": len(doctors), "available_count": available, "data": doctors}

@app.get("/appointments")
def get_appointments():
    return {"total": len(appointments), "data": appointments}

@app.get("/doctors/summary")
def summary():
    available = sum(1 for d in doctors if d["is_available"])
    most_exp = max(doctors, key=lambda x: x["experience_years"])["name"]
    cheapest = min(doctors, key=lambda x: x["fee"])["fee"]

    spec_count = {}
    for d in doctors:
        spec = d["specialization"]
        spec_count[spec] = spec_count.get(spec, 0) + 1

    return {
        "total": len(doctors),
        "available": available,
        "most_experienced": most_exp,
        "cheapest_fee": cheapest,
        "specialization_count": spec_count
    }

# -------------------- FILTER --------------------
@app.get("/doctors/filter")
def filter_doctors(
    specialization: Optional[str] = None,
    max_fee: Optional[int] = None,
    min_experience: Optional[int] = None,
    is_available: Optional[bool] = None
):
    result = filter_doctors_logic(specialization, max_fee, min_experience, is_available)
    return {"count": len(result), "data": result}

# -------------------- SEARCH --------------------
@app.get("/doctors/search")
def search_doctors(keyword: str):
    result = [d for d in doctors if keyword.lower() in d["name"].lower() or keyword.lower() in d["specialization"].lower()]
    if not result:
        return {"message": "No doctors found"}
    return {"total_found": len(result), "data": result}

# -------------------- SORT --------------------
@app.get("/doctors/sort")
def sort_doctors(sort_by: str = "fee", order: str = "asc"):
    if sort_by not in ["fee", "name", "experience_years"]:
        return {"error": "Invalid sort_by"}
    if order not in ["asc", "desc"]:
        return {"error": "Invalid order"}

    reverse = order == "desc"
    return {"sorted_by": sort_by, "order": order, "data": sorted(doctors, key=lambda x: x[sort_by], reverse=reverse)}

# -------------------- PAGINATION --------------------
@app.get("/doctors/page")
def paginate(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    total = len(doctors)
    total_pages = (total + limit - 1) // limit
    return {"page": page, "total_pages": total_pages, "data": doctors[start:start + limit]}

# -------------------- COMBINED --------------------
@app.get("/doctors/browse")
def browse(keyword: Optional[str] = None, sort_by: str = "fee", order: str = "asc", page: int = 1, limit: int = 4):
    data = doctors

    if keyword:
        data = [d for d in data if keyword.lower() in d["name"].lower()]

    reverse = order == "desc"
    data = sorted(data, key=lambda x: x[sort_by], reverse=reverse)

    start = (page - 1) * limit
    total = len(data)

    return {"total": total, "page": page, "data": data[start:start + limit]}

# -------------------- ID --------------------
@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        return {"error": "Doctor not found"}
    return doc

# -------------------- POST APPOINTMENT --------------------
@app.post("/appointments")
def create_appointment(req: AppointmentRequest):
    global appt_counter

    doc = find_doctor(req.doctor_id)
    if not doc:
        return {"error": "Doctor not found"}
    if not doc["is_available"]:
        return {"error": "Doctor not available"}

    original_fee, final_fee = calculate_fee(doc["fee"], req.appointment_type, req.senior_citizen)

    appointment = {
        "appointment_id": appt_counter,
        "patient_name": req.patient_name,
        "doctor": doc["name"],
        "date": req.date,
        "reason": req.reason,
        "type": req.appointment_type,
        "original_fee": original_fee,
        "final_fee": final_fee,
        "status": "scheduled"
    }

    appointments.append(appointment)
    appt_counter += 1

    return appointment

# -------------------- CRUD --------------------
@app.post("/doctors")
def add_doctor(new_doc: NewDoctor, response: Response):
    for d in doctors:
        if d["name"].lower() == new_doc.name.lower():
            return {"error": "Doctor already exists"}

    doc = new_doc.dict()
    doc["id"] = len(doctors) + 1
    doctors.append(doc)
    response.status_code = status.HTTP_201_CREATED
    return doc

@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, fee: Optional[int] = None, is_available: Optional[bool] = None):
    doc = find_doctor(doctor_id)
    if not doc:
        return {"error": "Doctor not found"}

    if fee is not None:
        doc["fee"] = fee
    if is_available is not None:
        doc["is_available"] = is_available

    return doc

@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        return {"error": "Doctor not found"}

    for a in appointments:
        if a["doctor"] == doc["name"] and a["status"] == "scheduled":
            return {"error": "Doctor has active appointments"}

    doctors.remove(doc)
    return {"message": f"{doc['name']} deleted"}

# -------------------- WORKFLOW --------------------
@app.post("/appointments/{appointment_id}/confirm")
def confirm(appointment_id: int):
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            a["status"] = "confirmed"
            return a
    return {"error": "Not found"}

@app.post("/appointments/{appointment_id}/cancel")
def cancel(appointment_id: int):
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            a["status"] = "cancelled"
            return a
    return {"error": "Not found"}

@app.post("/appointments/{appointment_id}/complete")
def complete(appointment_id: int):
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            a["status"] = "completed"
            return a
    return {"error": "Not found"}

@app.get("/appointments/active")
def active():
    return {"data": [a for a in appointments if a["status"] in ["scheduled", "confirmed"]]}

@app.get("/appointments/by-doctor/{doctor_id}")
def by_doctor(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        return {"error": "Doctor not found"}
    return {"data": [a for a in appointments if a["doctor"] == doc["name"]]}

# -------------------- APPOINTMENT SEARCH/SORT/PAGE --------------------
@app.get("/appointments/search")
def search_appointments(patient_name: str):
    return {"data": [a for a in appointments if patient_name.lower() in a["patient_name"].lower()]}

@app.get("/appointments/sort")
def sort_appointments(order: str = "asc"):
    reverse = order == "desc"
    return {"data": sorted(appointments, key=lambda x: x["final_fee"], reverse=reverse)}

@app.get("/appointments/page")
def page_appointments(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    total = len(appointments)
    total_pages = (total + limit - 1) // limit
    return {"page": page, "total_pages": total_pages, "data": appointments[start:start + limit]}