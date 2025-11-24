"""
Supabase RLS Fix - Disable Row Level Security for development
Run this SQL in your Supabase SQL Editor
"""

sql = """
-- Disable RLS on all tables for development
ALTER TABLE contractors DISABLE ROW LEVEL SECURITY;
ALTER TABLE employees DISABLE ROW LEVEL SECURITY;
ALTER TABLE signatures DISABLE ROW LEVEL SECURITY;
ALTER TABLE idcards DISABLE ROW LEVEL SECURITY;

-- OR if you want to keep RLS enabled, add these policies instead:
-- (Comment out the DISABLE commands above and use these)

/*
-- Enable RLS
ALTER TABLE contractors ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE signatures ENABLE ROW LEVEL SECURITY;
ALTER TABLE idcards ENABLE ROW LEVEL SECURITY;

-- Create policies for full access (you can make these more restrictive later)
CREATE POLICY "Allow all operations on contractors" ON contractors FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on employees" ON employees FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on signatures" ON signatures FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on idcards" ON idcards FOR ALL USING (true) WITH CHECK (true);
*/
"""

print("="*70)
print("SUPABASE RLS FIX")
print("="*70)
print("\nCopy this SQL and run it in your Supabase SQL Editor:\n")
print(sql)
print("="*70)
