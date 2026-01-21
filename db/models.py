# File 4

from dataclasses import dataclass
from typing import Optional

@dataclass
class Customer:
    name: str
    email: str
    phone: str
    id: Optional[int] = None

@dataclass
class Booking:
    customer_id: int
    booking_type: str
    date: str
    time: str
    status: str = "Confirmed"
    id: Optional[int] = None