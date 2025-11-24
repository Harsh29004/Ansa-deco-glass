"""
Run this script to get the Supabase SQL schema
"""
from models import init_database

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SUPABASE DATABASE SCHEMA")
    print("="*60 + "\n")
    print("Copy and paste this SQL into your Supabase SQL Editor:\n")
    print(init_database())
    print("\n" + "="*60)
