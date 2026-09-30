def has_available_seat(active_enrollment_count: int, capacity: int) -> bool:
    return active_enrollment_count < capacity
