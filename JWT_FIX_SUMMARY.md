# JWT Authentication Fix - Summary

## Problem
When attempting to create a recipe, users received a **401 "Invalid authentication credentials"** error despite having a valid JWT token and successful login.

## Root Cause
The JWT token's `sub` (subject) claim was being encoded as an **integer** (the user's database ID), but the `jwt.decode()` function requires it to be a **string**. This violated JWT specification requirements.

### Error in Backend
```
JWTError: Subject must be a string.
```

### File: app/routes/auth.py (Login endpoint)
**Before (Line 53):**
```python
access_token = create_access_token(
    data={"sub": db_user.id},  # ❌ Integer passed
    expires_delta=access_token_expires
)
```

**After (Fixed):**
```python
access_token = create_access_token(
    data={"sub": str(db_user.id)},  # ✅ String passed
    expires_delta=access_token_expires
)
```

### File: app/auth.py (Token decoding)
**decode_token() function updated to handle string subject:**

**Before:**
```python
user_id: int = payload.get("sub")
return {"user_id": user_id}
```

**After:**
```python
user_id_str: str = payload.get("sub")
user_id = int(user_id_str)  # Convert back to int
return {"user_id": user_id}
```

## Solution
1. Convert `sub` claim to string when creating JWT token (line 53 in app/routes/auth.py)
2. Convert `sub` claim back to integer when decoding JWT token (app/auth.py)

## Result
✅ JWT tokens now encode/decode correctly
✅ Recipe creation endpoint returns 201 Created (success)
✅ All authenticated operations now work properly

## Files Modified
- `app/routes/auth.py` - Line 53: Convert user ID to string
- `app/auth.py` - decode_token() function: Handle string-to-int conversion

## Testing
Recipe creation now returns HTTP 201 (Created) with recipe data instead of HTTP 401 (Unauthorized).
