# debug_auth.py
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.auth import authenticate_admin, hash_password, verify_password, get_admin_by_username
from backend.database import db

async def debug_auth():
    print("=== AUTHENTICATION DEBUG ===\n")
    
    # 1. Check if MongoDB is connected and collections exist
    print("1. Database Check:")
    try:
        collections = await db.list_collection_names()
        print(f"   ✅ Collections: {collections}")
        
        if 'admins' in collections:
            print("   ✅ 'admins' collection exists")
        else:
            print("   ❌ 'admins' collection NOT found!")
            return
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return
    
    # 2. Check if any admin users exist
    print("\n2. Admin Users Check:")
    admin_count = await db.admins.count_documents({})
    print(f"   Total admin users: {admin_count}")
    
    if admin_count == 0:
        print("   ❌ No admin users found! Creating one...")
        # Create an admin user
        from backend.auth import hash_password
        await db.admins.insert_one({
            "username": "admin",
            "password_hash": hash_password("admin123"),
            "email": "admin@wefixit.com"
        })
        print("   ✅ Created default admin: username='admin', password='admin123'")
    
    # 3. List all admin users
    print("\n3. Admin Users List:")
    async for admin in db.admins.find({}):
        print(f"   - {admin['username']}: {admin.get('email', 'no email')}")
        print(f"     Password hash: {admin['password_hash']}")
    
    # 4. Test password verification
    print("\n4. Password Verification Test:")
    test_admin = await db.admins.find_one({"username": "admin"})
    if test_admin:
        test_password = "admin123"
        is_valid = verify_password(test_password, test_admin["password_hash"])
        print(f"   Testing password '{test_password}': {'✅ VALID' if is_valid else '❌ INVALID'}")
        
        # Test wrong password
        wrong_password = "wrongpass"
        is_wrong_valid = verify_password(wrong_password, test_admin["password_hash"])
        print(f"   Testing wrong password '{wrong_password}': {'✅ VALID (UNEXPECTED)' if is_wrong_valid else '❌ INVALID (EXPECTED)'}")
    else:
        print("   ❌ No admin user found for testing")
    
    # 5. Test the authenticate_admin function
    print("\n5. authenticate_admin Function Test:")
    result = await authenticate_admin("admin", "admin123")
    print(f"   authenticate_admin('admin', 'admin123'): {'✅ SUCCESS' if result else '❌ FAILED'}")
    
    result_wrong = await authenticate_admin("admin", "wrongpass")
    print(f"   authenticate_admin('admin', 'wrongpass'): {'✅ SUCCESS (UNEXPECTED)' if result_wrong else '❌ FAILED (EXPECTED)'}")
    
    result_nonexistent = await authenticate_admin("nonexistent", "admin123")
    print(f"   authenticate_admin('nonexistent', 'admin123'): {'✅ SUCCESS (UNEXPECTED)' if result_nonexistent else '❌ FAILED (EXPECTED)'}")
    
    print("\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(debug_auth())