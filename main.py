from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import os

app = FastAPI(
    title="Leave Request Backend",
    version="1.0.0",
    description="Backend for Leave Request Agent integrated with Studio"
)

# --------------------------------
# Simulated Employee Data
# --------------------------------
EMPLOYEES = {
    "EMP101": {"name": "John Doe", "Casual": 5, "Sick": 2, "Unpaid": 999, "Maternity": 90},
    "EMP102": {"name": "Jane Smith", "Casual": 3, "Sick": 1, "Unpaid": 999, "Maternity": 80},
    "EMP103": {"name": "Alice Johnson", "Casual": 7, "Sick": 3, "Unpaid": 999, "Maternity": 90},
}

# --------------------------------
# 1️⃣ Validate Employee API
# --------------------------------
class ValidateEmployeeRequest(BaseModel):
    employee_id: str


@app.post("/validate-employee")
def validate_employee(data: ValidateEmployeeRequest):
    emp_id = data.employee_id.strip().upper()
    if emp_id not in EMPLOYEES:
        return {"status": False, "message": "Invalid Employee ID"}
    return {"status": True, "message": "Valid Employee"}


# --------------------------------
# 2️⃣ Get Leave Balance API
# --------------------------------
class LeaveBalanceRequest(BaseModel):
    employee_id: str


@app.post("/get-leave-balance")
def get_leave_balance(data: LeaveBalanceRequest):
    emp_id = data.employee_id.strip().upper()
    if emp_id not in EMPLOYEES:
        return {"status": False, "message": "Employee not found"}

    return {
        "status": True,
        "employee_id": emp_id,
        "balances": EMPLOYEES[emp_id]
    }


# --------------------------------
# 3️⃣ Calculate Leave Days API
# --------------------------------
class CalculateLeaveRequest(BaseModel):
    start_date: str
    end_date: str


@app.post("/calculate-leave-days")
def calculate_leave_days(data: CalculateLeaveRequest):
    try:
        start = datetime.strptime(data.start_date, "%Y-%m-%d")
        end = datetime.strptime(data.end_date, "%Y-%m-%d")

        if end <= start:
            return {"status": False, "message": "End date cannot be before or same as start date"}

        leave_days = (end - start).days + 1
        return {"status": True, "leave_days": leave_days}

    except ValueError:
        return {"status": False, "message": "Invalid date format (use YYYY-MM-DD)"}


# --------------------------------
# 4️⃣ Submit Leave Request API
# --------------------------------
class SubmitLeaveRequest(BaseModel):
    employee_id: str
    leave_type: str
    start_date: str
    end_date: str
    leave_days: int


@app.post("/submit-leave-request")
def submit_leave_request(data: SubmitLeaveRequest):
    emp_id = data.employee_id.strip().upper()

    if emp_id not in EMPLOYEES:
        return {"status": False, "message": "Employee not found"}

    emp = EMPLOYEES[emp_id]
    leave_type = data.leave_type.capitalize()

    if leave_type not in emp:
        return {"status": False, "message": "Invalid leave type"}

    balance = emp[leave_type]

    if data.leave_days > balance and leave_type != "Unpaid":
        return {"status": False, "message": f"Insufficient {leave_type} leave balance"}

    # Deduct leave balance if applicable
    if leave_type != "Unpaid":
        emp[leave_type] -= data.leave_days

    return {
        "status": True,
        "message": f"{leave_type} leave applied successfully for {data.leave_days} days",
        "remaining_balance": emp[leave_type]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8082))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
