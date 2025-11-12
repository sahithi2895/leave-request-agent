from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
import os

app = FastAPI(
    title="Leave Request Backend",
    version="3.0.0",
    description="Backend for Leave Request Agent integrated with Studio — all APIs return HTTP 200."
)

# --------------------------------
# 🧾 Simulated Employee Data
# --------------------------------
EMPLOYEES = {
    "EMP101": {"name": "John Doe", "Casual": 5, "Sick": 2, "Unpaid": 999, "Maternity": 90},
    "EMP102": {"name": "Jane Smith", "Casual": 3, "Sick": 1, "Unpaid": 999, "Maternity": 80},
    "EMP103": {"name": "Alice Johnson", "Casual": 7, "Sick": 3, "Unpaid": 999, "Maternity": 90},
}


# --------------------------------
# 🧩 Models
# --------------------------------
class ValidateEmployeeRequest(BaseModel):
    employee_id: str = Field(..., example="EMP101")


class LeaveBalanceRequest(BaseModel):
    employee_id: str = Field(..., example="EMP101")


class CalculateLeaveRequest(BaseModel):
    start_date: str = Field(..., example="2025-11-10")
    end_date: str = Field(..., example="2025-11-13")


class SubmitLeaveRequest(BaseModel):
    employee_id: str = Field(..., example="EMP101")
    leave_type: str = Field(..., example="Casual")
    start_date: str = Field(..., example="2025-11-10")
    end_date: str = Field(..., example="2025-11-12")
    leave_days: int = Field(..., example=3)


# --------------------------------
# 1️⃣ Validate Employee API
# --------------------------------
@app.post("/validate-employee", summary="Validate employee ID")
def validate_employee(data: ValidateEmployeeRequest):
    emp_id = data.employee_id.strip().upper()
    if emp_id not in EMPLOYEES:
        return {"status": False, "message": "Invalid Employee ID"}
    return {"status": True, "message": "Valid Employee"}


# --------------------------------
# 2️⃣ Get Leave Balance API
# --------------------------------
@app.post("/get-leave-balance", summary="Get leave balance for employee")
def get_leave_balance(data: LeaveBalanceRequest):
    emp_id = data.employee_id.strip().upper()

    if emp_id not in EMPLOYEES:
        return {"status": False, "message": "Employee not found"}

    return {
        "status": True,
        "message": "Leave balances fetched successfully",
        "employee_id": emp_id,
        "balances": EMPLOYEES[emp_id],
    }


# --------------------------------
# 3️⃣ Calculate Leave Days API
# --------------------------------
@app.post("/calculate-leave-days", summary="Calculate total leave days between two dates")
def calculate_leave_days(data: CalculateLeaveRequest):
    try:
        start = datetime.strptime(data.start_date, "%Y-%m-%d")
        end = datetime.strptime(data.end_date, "%Y-%m-%d")
    except ValueError:
        return {"status": False, "leave_days": 0, "message": "Invalid date format (use YYYY-MM-DD)"}

    if end < start:
        return {"status": False, "leave_days": 0, "message": "End date cannot be before start date"}

    leave_days = (end - start).days + 1
    return {"status": True, "leave_days": leave_days, "message": "Calculation successful"}


# --------------------------------
# 4️⃣ Submit Leave Request API
# --------------------------------
@app.post("/submit-leave-request", summary="Submit a leave request for employee")
def submit_leave_request(data: SubmitLeaveRequest):
    emp_id = data.employee_id.strip().upper()

    if emp_id not in EMPLOYEES:
        return {"status": False, "message": "Employee not found"}

    emp = EMPLOYEES[emp_id]
    leave_type = data.leave_type.capitalize()

    if leave_type not in emp:
        return {"status": False, "message": "Invalid leave type"}

    balance = emp[leave_type]

    # Check for sufficient balance
    if data.leave_days > balance and leave_type != "Unpaid":
        return {
            "status": False,
            "message": f"Insufficient {leave_type} leave balance",
            "remaining_balance": balance,
        }

    # Deduct balance (except unpaid)
    if leave_type != "Unpaid":
        emp[leave_type] -= data.leave_days

    return {
        "status": True,
        "message": f"{leave_type} leave applied successfully for {data.leave_days} days",
        "remaining_balance": emp[leave_type],
    }


# --------------------------------
# 🌐 Custom OpenAPI (for Render/Studio)
# --------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = app.openapi()
    openapi_schema["servers"] = [
        {"url": os.environ.get("BASE_URL", "https://leave-request-backend.onrender.com"), "description": "Production"}
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# --------------------------------
# 🚀 Local Run
# --------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8082))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
