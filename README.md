# ANSA Deco Glass - Approval Workflow System

## Overview
Complete contractor and employee approval workflow management system for ANSA Deco Glass manufacturing facility. Manages the entire process from contractor registration through multi-level approval (HR → Medical → Safety) to automatic ID card generation.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Supabase account (PostgreSQL database)
- Windows/Linux/Mac

### Installation

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure Supabase in .env
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# 3. Run SQL schema in Supabase SQL Editor (see Database Setup section)

# 4. Upload department signatures via Admin panel

# 5. Start application
python run.py
```

Access: **http://localhost:5000**

---

## 🗄️ Database Setup

### Supabase Tables (PostgreSQL)

Run this SQL in your Supabase SQL Editor:

```sql
-- 1. Contractors Table
CREATE TABLE contractors (
    id BIGSERIAL PRIMARY KEY,
    contractor_name VARCHAR(255) NOT NULL,
    po_number VARCHAR(100),
    email VARCHAR(255),
    mobile VARCHAR(20),
    department VARCHAR(100),
    job_description TEXT,
    hod_name TEXT,
    submission_date TEXT,
    signature_path VARCHAR(500),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    access_token VARCHAR(50) UNIQUE NOT NULL
);

-- 2. Employees Table
CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    contractor_id BIGINT NOT NULL REFERENCES contractors(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    surname VARCHAR(100) NOT NULL,
    dob VARCHAR(20),
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

-- 3. Signatures Table (HR, System)
CREATE TABLE signatures (
    id BIGSERIAL PRIMARY KEY,
    role VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255),
    path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. ID Cards Table
CREATE TABLE idcards (
    id BIGSERIAL PRIMARY KEY,
    employee_id BIGINT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    pdf_path VARCHAR(500),
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_till TIMESTAMP
);

-- 5. HOD Signatures Table (Department-specific)
CREATE TABLE hod_signatures (
    id BIGSERIAL PRIMARY KEY,
    department TEXT NOT NULL UNIQUE,
    hod_name TEXT NOT NULL,
    signature_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create Indexes
CREATE INDEX idx_contractors_access_token ON contractors(access_token);
CREATE INDEX idx_employees_contractor_id ON employees(contractor_id);
CREATE INDEX idx_employees_hr_status ON employees(hr_status);
CREATE INDEX idx_employees_medical_status ON employees(medical_status);
CREATE INDEX idx_employees_safety_status ON employees(safety_status);
CREATE INDEX idx_idcards_employee_id ON idcards(employee_id);
CREATE INDEX idx_hod_signatures_department ON hod_signatures(department);

-- Disable Row Level Security (for development)
ALTER TABLE contractors DISABLE ROW LEVEL SECURITY;
ALTER TABLE employees DISABLE ROW LEVEL SECURITY;
ALTER TABLE signatures DISABLE ROW LEVEL SECURITY;
ALTER TABLE idcards DISABLE ROW LEVEL SECURITY;
ALTER TABLE hod_signatures DISABLE ROW LEVEL SECURITY;
```

---

## 📋 System Workflow

1. **Contractor Registration** → Department HOD signature auto-loaded
2. **Employee Application** → Add multiple employees with photos/signatures
3. **HR Approval** → Review documents, approve/reject
4. **Medical Verification** → Medical fitness check with signature
5. **Safety Approval** → Final safety check, auto-generates ID card
6. **Status Tracking** → Real-time status via unique access token

---

## 👥 User Roles & Access

### Contractor
- Fill registration form with department selection
- HOD signature auto-loads from database based on department
- Add multiple employees
- Track status via access token

### HR Department
- **Login:** http://localhost:5000/hr/login
- **Credentials:** `hr_admin` / `hr@123`
- Review contractor forms and employee documents
- Approve/reject applications
- HR signature auto-applied from database

### Medical Department
- **Login:** http://localhost:5000/medical/login
- **Credentials:** `medical_admin` / `medical@123`
- Review HR-approved employees
- Upload medical officer signature during approval
- Approve/reject based on medical fitness

### Safety Department
- **Login:** http://localhost:5000/safety/login
- **Credentials:** `safety_admin` / `safety@123`
- Review medically fit employees
- Upload safety officer signature
- Final approval triggers automatic ID card generation

### Admin
- **Login:** http://localhost:5000/admin/login
- **Credentials:** `admin` / `admin@123`
- Manage department signatures (HR, System)
- Upload HOD signatures for each department
- System configuration

---

## 🔧 Configuration

### Required Signatures (Upload via Admin Panel)

1. **HR Signature** - Used automatically for all HR approvals
2. **System Signature** - Appears on ID cards (Manager/Authorized person)
3. **HOD Signatures** - Upload for each department:
   - Production
   - Printing
   - Quality Control
   - Packaging
   - Maintenance
   - Logistics
   - Other

### Environment Variables (.env)

```ini
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Login Credentials (Change in Production)
HR_USERNAME=hr_admin
HR_PASSWORD=hr@123
MEDICAL_USERNAME=medical_admin
MEDICAL_PASSWORD=medical@123
SAFETY_USERNAME=safety_admin
SAFETY_PASSWORD=safety@123
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin@123

# File Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# Company Details
COMPANY_NAME=ANSA Deco Glass
COMPANY_ADDRESS=Manufacturing Unit, Industrial Area
IDCARD_VALIDITY_DAYS=365
```

---

## 📁 Project Structure

```
ANSAA/
├── app.py                  # Main Flask application
├── run.py                  # Application runner
├── models.py               # Database models (Supabase)
├── config.py               # Configuration
├── utils.py                # Helper functions (PDF, images)
├── email_utils.py          # Email notifications
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── templates/              # HTML templates
│   ├── base.html
│   ├── contractor.html     # Contractor registration
│   ├── application_form.html  # Employee form
│   ├── hr_*.html          # HR dashboard & review
│   ├── medical_*.html     # Medical dashboard & review
│   ├── safety_*.html      # Safety dashboard & review
│   └── admin_*.html       # Admin panel
├── static/
│   ├── css/style.css      # Complete styling
│   └── images/            # Company logo
└── uploads/               # Uploaded files
    ├── contractor_signatures/
    ├── employee_photos/
    ├── employee_signatures/
    ├── approval_signatures/
    └── idcards/
```

---

## 🎯 Key Features

✅ Multi-step approval workflow (HR → Medical → Safety)
✅ Automatic HOD signature loading based on department
✅ Multiple employees per contractor
✅ Real-time status tracking
✅ Automatic ID card generation (PDF)
✅ Image optimization for uploads
✅ Email notifications (optional)
✅ Role-based access control
✅ PostgreSQL database (Supabase)
✅ Responsive design

---

## 🔐 Security

- Session-based authentication
- File upload validation (type, size)
- SQL injection protection (parameterized queries)
- Secure file naming
- Role-based access control
- HTTPS recommended for production

---

## 🚀 Deployment

### Production Checklist
- [ ] Enable HTTPS
- [ ] Change default passwords in .env
- [ ] Configure email for notifications
- [ ] Set up database backups
- [ ] Enable Supabase Row Level Security
- [ ] Configure proper file permissions
- [ ] Set up monitoring and logging

### Deployment Options
- **Cloud:** Azure, AWS, Google Cloud, Heroku
- **Server:** Linux with Nginx/Apache
- **Container:** Docker + Docker Compose

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review error logs
3. Contact system administrator

---

## 📝 License

Proprietary software for ANSA Deco Glass

---

**Version:** 2.0.0 (Supabase Migration)
**Last Updated:** November 2025

Built with ❤️ for ANSA Deco Glass Manufacturing
