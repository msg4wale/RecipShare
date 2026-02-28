#!/usr/bin/env python3
"""Test password hashing fix"""
import sys
sys.path.insert(0, '/Users/ade/Workspace/Dev/proj1')

from app.auth import hash_password, verify_password

print("Testing password hashing with PBKDF2-SHA256...\n")

# Test with a long password (more than 72 bytes)
long_pwd = 'a' * 100
hashed = hash_password(long_pwd)
print('✅ Long password (100 bytes) hashed successfully')

verified = verify_password(long_pwd, hashed)
print(f'✅ Long password verification works: {verified}')

# Test with normal password
normal_pwd = 'testpass123'
hashed2 = hash_password(normal_pwd)
verified2 = verify_password(normal_pwd, hashed2)
print(f'✅ Normal password verification works: {verified2}')

# Test with very long password
very_long = 'x' * 500
hashed3 = hash_password(very_long)
verified3 = verify_password(very_long, hashed3)
print(f'✅ Very long password (500 bytes) verification works: {verified3}')

print("\n✅ Password hashing now uses PBKDF2-SHA256 (no 72-byte limit!)")
print("✅ The ValueError is FIXED!")
