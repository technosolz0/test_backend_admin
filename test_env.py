from app.core.config import settings
try:
    import razorpay
    print(f"Razorpay package: AVAILABLE (version {razorpay.__version__})")
except ImportError:
    print("Razorpay package: NOT FOUND")

print(f"RAZORPAY_KEY_ID: {settings.RAZORPAY_KEY_ID[:8]}..." if settings.RAZORPAY_KEY_ID else "RAZORPAY_KEY_ID: MISSING")
print(f"RAZORPAY_KEY_SECRET: {settings.RAZORPAY_KEY_SECRET[:4]}..." if settings.RAZORPAY_KEY_SECRET else "RAZORPAY_KEY_SECRET: MISSING")
