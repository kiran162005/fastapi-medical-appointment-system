# 🏥 Medical Appointment System (FastAPI)

## 📌 Overview
The Medical Appointment System is a backend application built using FastAPI to manage doctors and patient appointments efficiently.

It provides APIs for handling doctor records, scheduling appointments, and performing advanced operations such as filtering, searching, sorting, and pagination.

---

## 🚀 Features

- Manage doctor records
- Schedule and manage appointments
- Input validation using Pydantic
- Dynamic fee calculation based on appointment type
- Filter doctors by specialization, fee, experience, and availability
- Search doctors and appointments
- Sort results based on multiple fields
- Pagination for large datasets
- Multi-step appointment workflow:
  - Schedule
  - Confirm
  - Cancel
  - Complete

---

## 🛠️ Technologies Used

- Python
- FastAPI
- Pydantic
- Uvicorn

---

## 📂 Project Structure

'''
fastapi-medical-appointment-system/
│
├── main.py
├── requirements.txt
├── README.md
└── screenshots/
'''

---

## ▶️ How to Run

### 1. Install dependencies
```bash
pip install fastapi uvicorn
2. Run the application
uvicorn main:app --reload
3. Access API documentation

Open your browser and go to:

http://127.0.0.1:8000/docs
📸 API Testing

All endpoints are tested using Swagger UI.

## 🔧 Key Functionalities

### 👨‍⚕️ Doctor Management
- Add new doctors  
- Update doctor details  
- Delete doctors (with validation)  

### 🗓️ Appointment Management
- Create appointments  
- Calculate consultation fees dynamically  
- Track appointment status  

### ⚙️ Advanced Operations
- Filter doctors based on multiple conditions  
- Search by name or specialization  
- Sort data based on different fields  
- Paginate results  
- Combined browsing (search + sort + pagination)  

---

## 👨‍💻 Author

**Kiran T**