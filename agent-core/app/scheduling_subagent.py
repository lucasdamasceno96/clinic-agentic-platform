from google.adk.agents import Agent
from google.adk.models import Gemini


def book_appointment(
    patient_name: str,
    date: str,
    time: str,
    reason: str,
) -> dict:
    """Book a medical appointment for a patient.

    Args:
        patient_name: Full name of the patient.
        date: Desired appointment date (YYYY-MM-DD).
        time: Desired appointment time (HH:MM).
        reason: Reason for the appointment (e.g. routine checkup, follow-up).

    Returns:
        dict with confirmation status and appointment details.
    """
    return {
        "status": "confirmed",
        "appointment": {
            "patient": patient_name,
            "date": date,
            "time": time,
            "reason": reason,
        },
    }


def cancel_appointment(
    patient_name: str,
    date: str,
    time: str,
) -> dict:
    """Cancel an existing medical appointment.

    Args:
        patient_name: Full name of the patient.
        date: Appointment date (YYYY-MM-DD).
        time: Appointment time (HH:MM).

    Returns:
        dict with cancellation status.
    """
    return {
        "status": "cancelled",
        "appointment": {
            "patient": patient_name,
            "date": date,
            "time": time,
        },
    }


def get_availability(
    date: str,
) -> dict:
    """Get available appointment slots for a given date.

    Args:
        date: The date to check (YYYY-MM-DD).

    Returns:
        dict with list of available time slots.
    """
    slots = [
        "09:00", "09:30", "10:00", "10:30",
        "11:00", "11:30", "14:00", "14:30",
        "15:00", "15:30", "16:00", "16:30",
    ]
    return {
        "status": "available",
        "date": date,
        "slots": slots,
    }


instruction = """You are a scheduling specialist at LDP Labs Clinic.

Your unique job is to collect dates, times, and patient names to book, reschedule, or cancel medical consultations.

Available tools:
- book_appointment: Create a new appointment.
- cancel_appointment: Cancel an existing appointment.
- get_availability: Check available time slots for a given date.

Collect all required information (name, date, time, reason) before booking.
If the patient hasn't specified all details, ask for them politely.
Once the booking is complete, return the confirmation details to the main orchestrator.

NEVER provide medical advice, diagnoses, or prescriptions. You handle ONLY scheduling."""


def create_scheduling_agent() -> Agent:
    return Agent(
        name="scheduling_subagent",
        model=Gemini(model="gemini-flash-latest"),
        instruction=instruction,
        description="Handles appointment scheduling, rescheduling, and cancellations.",
        tools=[book_appointment, cancel_appointment, get_availability],
    )
