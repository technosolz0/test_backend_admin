from sqlalchemy.orm import Session
from app.models.vendor_earnings_model import VendorEarnings
from app.models.service_provider_model import ServiceProvider
from app.utils.commission_utils import get_completed_bookings_count, calculate_commission, calculate_referral_incentive
import logging

logger = logging.getLogger(__name__)

def create_vendor_earnings(db: Session, booking_id: int, vendor_id: int,
                          total_paid: float, commission_percentage: float = None,
                          commission_amount: float = None, final_amount: float = None):
    """
    Create a new vendor earnings record.
    If commission details are not provided, they are calculated dynamically based on slabs.
    Includes referral incentive calculation if applicable.
    """
    # Get vendor for referral check
    vendor = db.query(ServiceProvider).filter(ServiceProvider.id == vendor_id).first()
    
    # Get lifetime completed bookings for this vendor
    completed_count = get_completed_bookings_count(db, vendor_id)
    
    # Calculate dynamic commission based on slabs
    calc_percentage, calc_amount = calculate_commission(db, vendor, total_paid, completed_count)
    
    # Use calculated values unless explicitly overridden
    final_percentage = commission_percentage if commission_percentage is not None else calc_percentage
    final_commission_amount = commission_amount if commission_amount is not None else calc_amount
    
    # Calculate referral incentive if vendor has a referrer
    referral_incentive = 0.0
    referrer_id = None
    if vendor and vendor.referred_by_id:
        referrer_id = vendor.referred_by_id
        referral_incentive = calculate_referral_incentive(total_paid, final_commission_amount)
    
    # Calculate final amount (vendor gets total - platform commission)
    # The referral incentive is paid FROM the platform's commission
    if final_amount is None:
        final_amount = total_paid - final_commission_amount

    earning = VendorEarnings(
        booking_id=booking_id,
        vendor_id=vendor_id,
        total_paid=total_paid,
        commission_percentage=final_percentage,
        commission_amount=final_commission_amount,
        final_amount=final_amount,
        referral_incentive=referral_incentive,
        referrer_id=referrer_id
    )
    
    db.add(earning)
    db.commit()
    db.refresh(earning)
    
    logger.info(f"Vendor earnings created for vendor {vendor_id}, booking {booking_id}. "
                f"Slab rate: {final_percentage}%, Referral incentive: {referral_incentive} (to {referrer_id}), "
                f"Booking count: {completed_count}")
    
    return earning

def get_vendor_earnings_by_vendor(db: Session, vendor_id: int):
    return db.query(VendorEarnings).filter(VendorEarnings.vendor_id == vendor_id).all()

def get_vendor_earnings_by_booking(db: Session, booking_id: int):
    return db.query(VendorEarnings).filter(VendorEarnings.booking_id == booking_id).all()

def get_vendor_earnings_by_id(db: Session, earnings_id: int):
    return db.query(VendorEarnings).filter(VendorEarnings.id == earnings_id).first()

def get_all_vendor_earnings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(VendorEarnings).offset(skip).limit(limit).all()

def delete_vendor_earnings(db: Session, earnings_id: int):
    earnings = db.query(VendorEarnings).filter(VendorEarnings.id == earnings_id).first()
    if earnings:
        db.delete(earnings)
        db.commit()
        return True
    return False
