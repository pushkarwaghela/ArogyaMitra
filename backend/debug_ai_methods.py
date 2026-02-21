from app.services.ai_agent import arogya_mitra_agent

print("=" * 60)
print("🔍 Available methods in ArogyaMitraAgent")
print("=" * 60)

methods = [method for method in dir(arogya_mitra_agent) if not method.startswith('_')]
for method in sorted(methods):
    print(f"  • {method}")
print("=" * 60)
