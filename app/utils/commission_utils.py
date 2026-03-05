from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.booking_model import Booking, BookingStatus
from app.models.service_provider_model import ServiceProvider

def get_completed_bookings_count(db: Session, vendor_id: int) -> int:
    """
    Count successfully completed bookings for a specific vendor.
    Cancelled or failed bookings are not counted.
    """
    return db.query(func.count(Booking.id)).filter(
        Booking.serviceprovider_id == vendor_id,
        Booking.status == BookingStatus.completed
    ).scalar() or 0

def get_commission_percentage(db: Session, vendor: ServiceProvider, completed_bookings: int) -> float:
    """
    Determine commission percentage based on completed bookings count and referral type.
    
    1. Admin Referral: Uses custom bookings count and percentage from AdminReferralCode.
    2. Vendor Referral: First 5 bookings 0%, then standard steps.
    3. No Referral: First 5 bookings 0%, then standard steps (Same as vendor referral for now).
    """
    
    # Handle Admin Referral Override
    if vendor.referral_type == 'admin' and vendor.applied_referral_code:
        from app.models.referral_model import AdminReferralCode
        admin_ref = db.query(AdminReferralCode).filter(AdminReferralCode.code == vendor.applied_referral_code).first()
        if admin_ref:
            if completed_bookings <= admin_ref.no_of_bookings:
                return admin_ref.commission_percentage

    # Handle Vendor Referral or Standard Logic
    # (Requirement: Vendor referral = first 5 bookings 0%)
    if completed_bookings <= 5:
        return 0.0
    elif completed_bookings <= 20:
        return 5.0
    elif completed_bookings <= 50:
        return 10.0
    else:
        return 15.0

def calculate_commission(db: Session, vendor: ServiceProvider, total_paid: float, completed_bookings: int) -> tuple[float, float]:
    """
    Calculate commission amount and percentage.
    Returns (commission_percentage, commission_amount)
    """
    percentage = get_commission_percentage(db, vendor, completed_bookings)
    amount = (total_paid * percentage) / 100
    return percentage, amount

def calculate_referral_incentive(total_paid: float, vendor_commission_amount: float) -> float:
    """
    Calculate referral incentive for the partner/referrer.
    - Max incentive is 5% of total_paid.
    - But it's also capped by the vendor_commission_amount to ensure no platform loss.
    """
    max_incentive = (total_paid * 5.0) / 100
    # Platform must never go into loss, so incentive <= collected commission
    return min(max_incentive, vendor_commission_amount)
