import random
import string
from datetime import datetime

from google.adk.agents import Agent
from google.adk.models import Gemini
from pydantic import BaseModel, Field


class AvailabilityRequest(BaseModel):
    specialty: str = Field(
        description="Medical specialty (e.g. cardiology, dermatology, general)."
    )
    date: str = Field(
        description="Target date in YYYY-MM-DD format.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )


class BookingRequest(BaseModel):
    patient_name: str = Field(description="Patient first name.")
    patient_lastname: str = Field(description="Patient last name.")
    date_time: str = Field(
        description="Appointment datetime in YYYY-MM-DD HH:MM format.",
    )
    doctor_name: str = Field(description="Full name of the doctor.")


class CancelRequest(BaseModel):
    appointment_id: str = Field(
        description="Unique appointment identifier (e.g. LDP-9832A).",
        pattern=r"^LDP-\w+$",
    )


_APPOINTMENTS: dict[str, dict] = {}
_SLOTS_BY_SPECIALTY: dict[str, dict[str, list[str]]] = {}


def _generate_appointment_id() -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"LDP-{suffix}"


def get_availability(specialty: str, date: str) -> dict:
    """Check available appointment slots for a specialty on a given date.

    Args:
        specialty: Medical specialty (e.g. cardiology, dermatology, general).
        date: Target date in YYYY-MM-DD format.

    Returns:
        dict with status, specialty, date, and list of time slots.
    """
    AvailabilityRequest(specialty=specialty, date=date)

    slots = [
        "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
        "11:00 AM", "11:30 AM",
        "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM",
        "04:00 PM", "04:30 PM",
    ]

    booked = _APPOINTMENTS.get(f"{specialty}|{date}", set())
    available = [s for s in slots if s not in booked]

    if specialty not in _SLOTS_BY_SPECIALTY:
        _SLOTS_BY_SPECIALTY[specialty] = {}
    _SLOTS_BY_SPECIALTY[specialty][date] = available

    return {
        "status": "available",
        "specialty": specialty,
        "date": date,
        "slots": available,
    }


def book_appointment(
    patient_name: str,
    patient_lastname: str,
    date_time: str,
    doctor_name: str,
) -> dict:
    """Book a medical appointment and return a confirmation.

    Args:
        patient_name: Patient first name.
        patient_lastname: Patient last name.
        date_time: Appointment datetime in YYYY-MM-DD HH:MM format.
        doctor_name: Full name of the doctor.

    Returns:
        dict with confirmation status and generated appointment ID.
    """
    BookingRequest(
        patient_name=patient_name,
        patient_lastname=patient_lastname,
        date_time=date_time,
        doctor_name=doctor_name,
    )

    appointment_id = _generate_appointment_id()

    _APPOINTMENTS[appointment_id] = {
        "patient_name": patient_name,
        "patient_lastname": patient_lastname,
        "date_time": date_time,
        "doctor_name": doctor_name,
        "created_at": datetime.now().isoformat(),
    }

    date_part = date_time.split(" ")[0]
    specialty_key = f"{doctor_name.lower()}|{date_part}"
    if specialty_key in _APPOINTMENTS:
        existing = _APPOINTMENTS.get(specialty_key, set())
        existing.add(date_time.split(" ")[1])
        _APPOINTMENTS[specialty_key] = existing

    return {
        "status": "confirmed",
        "appointment_id": appointment_id,
        "patient": f"{patient_name} {patient_lastname}",
        "doctor": doctor_name,
        "date_time": date_time,
    }


def cancel_appointment(appointment_id: str) -> dict:
    """Cancel an existing appointment by its ID.

    Args:
        appointment_id: Unique appointment identifier starting with LDP-.

    Returns:
        dict with cancellation confirmation.
    """
    CancelRequest(appointment_id=appointment_id)

    if appointment_id not in _APPOINTMENTS:
        return {
            "status": "not_found",
            "appointment_id": appointment_id,
            "message": f"Appointment {appointment_id} was not found.",
        }

    del _APPOINTMENTS[appointment_id]

    return {
        "status": "cancelled",
        "appointment_id": appointment_id,
        "message": f"Appointment {appointment_id} was successfully cancelled.",
        "cancelled_at": datetime.now().isoformat(),
    }


instruction = """You are a scheduling specialist at LDP Labs Clinic.

Your unique job is to collect the following information to book, reschedule, or cancel medical consultations:

Available tools:
- get_availability(specialty, date): Check available time slots for a given medical specialty and date.
- book_appointment(patient_name, patient_lastname, date_time, doctor_name): Create a new appointment. You MUST collect all four fields before calling this tool.
- cancel_appointment(appointment_id): Cancel an existing appointment using its LDP-XXXXX ID.

For booking, always check availability first, then collect: patient first name, patient last name, desired date and time, and doctor's full name.
Once the booking is complete, return the generated LDP appointment ID to the main orchestrator.
NEVER provide medical advice, diagnoses, or prescriptions. You handle ONLY scheduling."""


def create_scheduling_agent() -> Agent:
    return Agent(
        name="scheduling_subagent",
        model=Gemini(model="gemini-flash-latest"),
        instruction=instruction,
        description="Handles appointment scheduling, rescheduling, and cancellations.",
        tools=[get_availability, book_appointment, cancel_appointment],
    )
