"""
Supabase (PostgreSQL) Models with explicit Primary Key and Foreign Key relationships
"""
from supabase import create_client, Client
from datetime import datetime, timedelta
from config import Config
import secrets
import string

class Database:
    """Supabase Database Connection Manager"""
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """Establish Supabase connection"""
        if self._client is None:
            self._client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        return self._client
    
    def get_client(self):
        """Get Supabase client instance"""
        if self._client is None:
            return self.connect()
        return self._client


class ContractorModel:
    """Contractor Model - Manages contractor records"""
    
    def __init__(self):
        self.client = Database().get_client()
        self.table = 'contractors'
    
    def _generate_token(self):
        """Generate random access token for contractor"""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    
    def create(self, data):
        """
        Create new contractor (PRIMARY KEY: id auto-generated)
        Returns: contractor id
        """
        contractor = {
            'contractor_name': data.get('contractor_name'),
            'po_number': data.get('po_number'),
            'email': data.get('email'),
            'mobile': data.get('mobile'),
            'department': data.get('department'),
            'job_description': data.get('job_description'),
            'hod_name': data.get('hod_name', ''),
            'submission_date': data.get('submission_date', ''),
            'signature_path': data.get('signature_path'),
            'submitted_at': datetime.utcnow().isoformat(),
            'status': 'pending',
            'access_token': self._generate_token()
        }
        result = self.client.table(self.table).insert(contractor).execute()
        return result.data[0]['id'] if result.data else None
    
    def find_by_id(self, contractor_id):
        """Find contractor by PRIMARY KEY"""
        result = self.client.table(self.table).select('*').eq('id', contractor_id).execute()
        return result.data[0] if result.data else None
    
    def find_by_token(self, token):
        """Find contractor by access token"""
        result = self.client.table(self.table).select('*').eq('access_token', token).execute()
        return result.data[0] if result.data else None
    
    def get_with_employees(self, contractor_id):
        """
        Get contractor with all associated employees (JOIN operation)
        Resolves FK: employees.contractor_id -> contractors.id
        """
        contractor = self.find_by_id(contractor_id)
        if contractor:
            employee_model = EmployeeModel()
            employees = employee_model.get_by_contractor(contractor_id)
            contractor['employees'] = employees
        return contractor


class EmployeeModel:
    """Employee Model - Manages employee records with FK to contractor"""
    
    def __init__(self):
        self.client = Database().get_client()
        self.table = 'employees'
    
    def create(self, data, contractor_id):
        """
        Create new employee (PRIMARY KEY: id auto-generated)
        FOREIGN KEY: contractor_id references contractors(id)
        """
        # Build permanent address string
        perm_address = ', '.join(filter(None, [
            data.get('perm_street', ''),
            data.get('perm_city', ''),
            data.get('perm_state', ''),
            data.get('perm_pincode', '')
        ]))
        
        # Build present address string
        pres_address = ', '.join(filter(None, [
            data.get('pres_street', ''),
            data.get('pres_city', ''),
            data.get('pres_state', ''),
            data.get('pres_pincode', '')
        ]))
        
        employee = {
            'contractor_id': contractor_id,  # FK
            'first_name': data.get('first_name'),
            'middle_name': data.get('middle_name'),
            'surname': data.get('surname'),
            'dob': data.get('dob'),
            'father_name': data.get('father_name', ''),
            'aadhar': data.get('aadhar'),
            'mobile': data.get('mobile', ''),
            'emergency_contact': data.get('emergency_name', ''),
            'emergency_mobile': data.get('emergency_phone', ''),
            'address_present': pres_address,
            'address_permanent': perm_address,
            'photo_path': data.get('photo_path'),
            'signature_path': data.get('signature_path'),
            'submitted_at': datetime.utcnow().isoformat(),
            'final_status': 'pending',
            'hr_status': 'pending',
            'hr_approved_by': None,
            'hr_approved_at': None,
            'hr_signature_path': None,
            'medical_status': 'pending',
            'medical_approved_by': None,
            'medical_approved_at': None,
            'medical_signature_path': None,
            'safety_status': 'pending',
            'safety_approved_by': None,
            'safety_approved_at': None,
            'safety_signature_path': None,
            'system_signature_path': None
        }
        result = self.client.table(self.table).insert(employee).execute()
        return result.data[0]['id'] if result.data else None
    
    def find_by_id(self, employee_id):
        """Find employee by PRIMARY KEY"""
        result = self.client.table(self.table).select('*').eq('id', employee_id).execute()
        return result.data[0] if result.data else None
    
    def get_by_contractor(self, contractor_id):
        """Get all employees for a contractor (FK lookup)"""
        result = self.client.table(self.table).select('*').eq('contractor_id', contractor_id).execute()
        return result.data
    
    def get_pending_for_department(self, department):
        """Get pending employees for specific department"""
        status_field = f'{department}_status'
        result = self.client.table(self.table).select('*').eq(status_field, 'pending').execute()
        return result.data
    
    def update_approval(self, employee_id, department, status, approved_by, signature_path=None):
        """Update approval status for a department"""
        update_data = {
            f'{department}_status': status,
            f'{department}_approved_by': approved_by,
            f'{department}_approved_at': datetime.utcnow().isoformat()
        }
        if signature_path:
            update_data[f'{department}_signature_path'] = signature_path
        
        self.client.table(self.table).update(update_data).eq('id', employee_id).execute()
        
        # Update final status
        self._update_final_status(employee_id)
    
    def _update_final_status(self, employee_id):
        """Check all approvals and update final status"""
        employee = self.find_by_id(employee_id)
        if not employee:
            return
        
        if employee['hr_status'] == 'rejected' or employee['medical_status'] == 'rejected' or employee['safety_status'] == 'rejected':
            final_status = 'rejected'
        elif employee['hr_status'] == 'approved' and employee['medical_status'] == 'approved' and employee['safety_status'] == 'approved':
            final_status = 'approved'
        else:
            final_status = 'pending'
        
        self.client.table(self.table).update({'final_status': final_status}).eq('id', employee_id).execute()


class SignatureModel:
    """Signature Model - Manages system signatures"""
    
    def __init__(self):
        self.client = Database().get_client()
        self.table = 'signatures'
    
    def save(self, role, file_path, uploaded_by):
        """Save or update signature for a role"""
        # Check if signature exists
        existing = self.get_by_role(role)
        
        if existing:
            # Update existing
            self.client.table(self.table).update({
                'file_path': file_path,
                'uploaded_by': uploaded_by,
                'uploaded_at': datetime.utcnow().isoformat()
            }).eq('role', role).execute()
        else:
            # Insert new
            self.client.table(self.table).insert({
                'role': role,
                'file_path': file_path,
                'uploaded_by': uploaded_by,
                'uploaded_at': datetime.utcnow().isoformat()
            }).execute()
    
    def get_by_role(self, role):
        """Get signature by role"""
        result = self.client.table(self.table).select('*').eq('role', role).execute()
        return result.data[0] if result.data else None


class IDCardModel:
    """ID Card Model - Manages generated ID cards with FK to employee"""
    
    def __init__(self):
        self.client = Database().get_client()
        self.table = 'idcards'
    
    def create(self, employee_id, pdf_path):
        """
        Create ID card record
        FOREIGN KEY: employee_id references employees(id)
        """
        issued_at = datetime.utcnow()
        valid_till = issued_at + timedelta(days=Config.IDCARD_VALIDITY_DAYS)
        
        idcard = {
            'employee_id': employee_id,  # FK
            'pdf_path': pdf_path,
            'issued_at': issued_at.isoformat(),
            'valid_till': valid_till.isoformat()
        }
        result = self.client.table(self.table).insert(idcard).execute()
        return result.data[0]['id'] if result.data else None
    
    def find_by_employee(self, employee_id):
        """Find ID card by employee FK"""
        result = self.client.table(self.table).select('*').eq('employee_id', employee_id).execute()
        return result.data[0] if result.data else None
    
    def exists_for_employee(self, employee_id):
        """Check if ID card exists for employee"""
        result = self.client.table(self.table).select('id').eq('employee_id', employee_id).execute()
        return len(result.data) > 0


class HODSignatureModel:
    """HOD Signature Model - Manages department HOD signatures"""
    
    def __init__(self):
        self.client = Database().get_client()
        self.table = 'hod_signatures'
    
    def create_or_update(self, department, hod_name, signature_path):
        """
        Create or update HOD signature for a department
        """
        # Check if exists
        existing = self.get_by_department(department)
        
        if existing:
            # Update existing
            update_data = {
                'hod_name': hod_name,
                'signature_path': signature_path,
                'updated_at': datetime.utcnow().isoformat()
            }
            result = self.client.table(self.table).update(update_data).eq('department', department).execute()
            return result.data[0]['id'] if result.data else None
        else:
            # Insert new
            signature_data = {
                'department': department,
                'hod_name': hod_name,
                'signature_path': signature_path,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            result = self.client.table(self.table).insert(signature_data).execute()
            return result.data[0]['id'] if result.data else None
    
    def get_by_department(self, department):
        """Get HOD signature by department"""
        result = self.client.table(self.table).select('*').eq('department', department).execute()
        return result.data[0] if result.data else None
    
    def get_all(self):
        """Get all HOD signatures"""
        result = self.client.table(self.table).select('*').order('department').execute()
        return result.data
    
    def delete_by_department(self, department):
        """Delete HOD signature by department"""
        result = self.client.table(self.table).delete().eq('department', department).execute()
        return result.data


def init_database():
    """
    Initialize Supabase tables - Run this SQL in Supabase SQL Editor:
    """
    sql_schema = """
    -- Contractors table
    CREATE TABLE IF NOT EXISTS contractors (
        id BIGSERIAL PRIMARY KEY,
        contractor_name VARCHAR(255) NOT NULL,
        po_number VARCHAR(100),
        email VARCHAR(255),
        mobile VARCHAR(20),
        department VARCHAR(100),
        job_description TEXT,
        signature_path VARCHAR(500),
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(50) DEFAULT 'pending',
        access_token VARCHAR(50) UNIQUE NOT NULL
    );

    -- Employees table
    CREATE TABLE IF NOT EXISTS employees (
        id BIGSERIAL PRIMARY KEY,
        contractor_id BIGINT NOT NULL REFERENCES contractors(id) ON DELETE CASCADE,
        first_name VARCHAR(100) NOT NULL,
        middle_name VARCHAR(100),
        surname VARCHAR(100) NOT NULL,
        dob DATE,
        father_name VARCHAR(255),
        aadhar VARCHAR(20),
        mobile VARCHAR(20),
        emergency_contact VARCHAR(255),
        emergency_mobile VARCHAR(20),
        address_present TEXT,
        address_permanent TEXT,
        photo_path VARCHAR(500),
        signature_path VARCHAR(500),
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        final_status VARCHAR(50) DEFAULT 'pending',
        hr_status VARCHAR(50) DEFAULT 'pending',
        hr_approved_by VARCHAR(255),
        hr_approved_at TIMESTAMP,
        hr_signature_path VARCHAR(500),
        medical_status VARCHAR(50) DEFAULT 'pending',
        medical_approved_by VARCHAR(255),
        medical_approved_at TIMESTAMP,
        medical_signature_path VARCHAR(500),
        safety_status VARCHAR(50) DEFAULT 'pending',
        safety_approved_by VARCHAR(255),
        safety_approved_at TIMESTAMP,
        safety_signature_path VARCHAR(500),
        system_signature_path VARCHAR(500)
    );

    -- Signatures table
    CREATE TABLE IF NOT EXISTS signatures (
        id BIGSERIAL PRIMARY KEY,
        role VARCHAR(50) UNIQUE NOT NULL,
        file_path VARCHAR(500),
        uploaded_by VARCHAR(255),
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- ID Cards table
    CREATE TABLE IF NOT EXISTS idcards (
        id BIGSERIAL PRIMARY KEY,
        employee_id BIGINT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
        pdf_path VARCHAR(500),
        issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        valid_till TIMESTAMP
    );

    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_contractors_access_token ON contractors(access_token);
    CREATE INDEX IF NOT EXISTS idx_employees_contractor_id ON employees(contractor_id);
    CREATE INDEX IF NOT EXISTS idx_employees_hr_status ON employees(hr_status);
    CREATE INDEX IF NOT EXISTS idx_employees_medical_status ON employees(medical_status);
    CREATE INDEX IF NOT EXISTS idx_employees_safety_status ON employees(safety_status);
    CREATE INDEX IF NOT EXISTS idx_idcards_employee_id ON idcards(employee_id);
    """
    print("Run this SQL in your Supabase SQL Editor:")
    print(sql_schema)
    return sql_schema
