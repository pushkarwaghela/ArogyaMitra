from app.config import settings

print("=" * 50)
print("DEBUG: Settings Check")
print("=" * 50)
print(f"GOOGLE_CALENDAR_CLIENT_ID: {settings.GOOGLE_CALENDAR_CLIENT_ID}")
print(f"GOOGLE_CALENDAR_CLIENT_SECRET: {settings.GOOGLE_CALENDAR_CLIENT_SECRET[:10] if settings.GOOGLE_CALENDAR_CLIENT_SECRET else 'Not set'}...")
print(f"REDIRECT_URI: {settings.GOOGLE_CALENDAR_REDIRECT_URI}")
print("=" * 50)
