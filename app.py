"""
Main Flask Application
Approval Workflow System for Manufacturing Company
"""
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, send_from_directory, jsonify, session
from werkzeug.utils import secure_filename
from config import Config
from models import Database, ContractorModel, EmployeeModel, SignatureModel, IDCardModel, HODSignatureModel, init_database
from utils import (
    save_contractor_signature, save_employee_photo, save_employee_signature,
    save_approval_signature, generate_idcard_pdf, allowed_file, optimize_image
)
from email_utils import send_contractor_credentials_email, send_approval_notification
import os
from datetime import datetime
from bson import ObjectId
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Initialize database connection
db = Database()
db.connect()


# ==================== AUTHENTICATION ====================

def login_required(role):
    """Decorator to require login for specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if f'{role}_logged_in' not in session:
                flash('Please login to access this page', 'error')
                return redirect(url_for(f'{role}_login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/hr/login', methods=['GET', 'POST'])
def hr_login():
    """HR login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == Config.HR_USERNAME and password == Config.HR_PASSWORD:
            session['hr_logged_in'] = True
            session['user_role'] = 'HR'
            flash('Login successful!', 'success')
            return redirect(url_for('hr_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html', role='HR', login_route='hr_login')


@app.route('/medical/login', methods=['GET', 'POST'])
def medical_login():
    """Medical login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == Config.MEDICAL_USERNAME and password == Config.MEDICAL_PASSWORD:
            session['medical_logged_in'] = True
            session['user_role'] = 'Medical'
            flash('Login successful!', 'success')
            return redirect(url_for('medical_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html', role='Medical', login_route='medical_login')


@app.route('/safety/login', methods=['GET', 'POST'])
def safety_login():
    """Safety login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == Config.SAFETY_USERNAME and password == Config.SAFETY_PASSWORD:
            session['safety_logged_in'] = True
            session['user_role'] = 'Safety'
            flash('Login successful!', 'success')
            return redirect(url_for('safety_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html', role='Safety', login_route='safety_login')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['user_role'] = 'Admin'
            flash('Login successful!', 'success')
            return redirect(url_for('admin_signatures'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html', role='Admin', login_route='admin_login')


@app.route('/logout')
def logout():
    """Logout user"""
    role = session.get('user_role', '')
    session.clear()
    flash(f'{role} logged out successfully', 'success')
    return redirect(url_for('index'))


# ==================== CONTRACTOR ROUTES ====================

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/check-status')
def check_status_page():
    """Status check page"""
    return render_template('check_status.html')


# ==================== FILE SERVING ====================

@app.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    """Serve uploaded files (photos, signatures, etc.)"""
    # The database stores paths like 'uploads/employee_photos/file.jpg'
    # We need to serve from the uploads directory
    # So strip 'uploads/' prefix if present
    if filename.startswith('uploads/') or filename.startswith('uploads\\'):
        filename = filename[8:]  # Remove 'uploads/' or 'uploads\'
    
    # Replace backslashes with forward slashes for cross-platform compatibility
    filename = filename.replace('\\', '/')
    
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    
    if os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        return send_from_directory(directory, file_name)
    else:
        return "File not found", 404


@app.route('/file/<path:subpath>/<filename>')
def serve_file(subpath, filename):
    """Serve files from uploads subdirectories"""
    directory = os.path.join(Config.UPLOAD_FOLDER, subpath)
    return send_from_directory(directory, filename)


# ==================== CONTRACTOR ROUTES ====================

@app.route('/contractor', methods=['GET', 'POST'])
def contractor_form():
    """
    Contractor Legal Requirement Verification Form
    Step 1 of the workflow
    """
    if request.method == 'POST':
        try:
            # Get form data
            contractor_data = {
                'contractor_name': request.form.get('contractor_name'),
                'po_number': request.form.get('po_number'),
                'email': request.form.get('email'),
                'mobile': request.form.get('mobile'),
                'department': request.form.get('department'),
                'job_description': request.form.get('job_description'),
                'hod_name': request.form.get('hod_name'),
                'submission_date': request.form.get('submission_date')
            }
            
            # Get signature path from hidden field (auto-loaded from database)
            signature_path = request.form.get('signature_path')
            if signature_path:
                contractor_data['signature_path'] = signature_path
            else:
                flash('HOD signature not found. Please contact admin.', 'error')
                return render_template('contractor.html')
            
            # Create contractor record
            contractor_model = ContractorModel()
            contractor_id = contractor_model.create(contractor_data)
            
            # Store contractor_id in session for employee form
            session['contractor_id'] = str(contractor_id)
            
            flash('Contractor information saved successfully!', 'success')
            
            # Redirect to employee application form
            return redirect(url_for('employee_application'))
            
        except Exception as e:
            flash(f'Error saving contractor information: {str(e)}', 'error')
            return render_template('contractor.html')
    
    return render_template('contractor.html')


@app.route('/employee-application', methods=['GET', 'POST'])
def employee_application():
    """
    Employee Application Form
    Step 2 of the workflow - Can add multiple employees
    """
    contractor_id = session.get('contractor_id')
    
    if not contractor_id:
        flash('Please complete contractor form first', 'error')
        return redirect(url_for('contractor_form'))
    
    if request.method == 'POST':
        try:
            # Get number of employees being submitted
            employees_data = []
            employee_count = int(request.form.get('employee_count', 1))
            
            employee_model = EmployeeModel()
            contractor_model = ContractorModel()
            
            # Process each employee
            for i in range(employee_count):
                prefix = f'emp_{i}_'
                
                # Extract employee data
                emp_data = {
                    'first_name': request.form.get(f'{prefix}first_name'),
                    'middle_name': request.form.get(f'{prefix}middle_name', ''),
                    'surname': request.form.get(f'{prefix}surname'),
                    'dob': request.form.get(f'{prefix}dob'),
                    'qualification': request.form.get(f'{prefix}qualification', ''),
                    'aadhar': request.form.get(f'{prefix}aadhar', ''),
                    
                    # Permanent Address
                    'perm_street': request.form.get(f'{prefix}perm_street', ''),
                    'perm_city': request.form.get(f'{prefix}perm_city', ''),
                    'perm_state': request.form.get(f'{prefix}perm_state', ''),
                    'perm_pincode': request.form.get(f'{prefix}perm_pincode', ''),
                    
                    # Present Address
                    'pres_street': request.form.get(f'{prefix}pres_street', ''),
                    'pres_city': request.form.get(f'{prefix}pres_city', ''),
                    'pres_state': request.form.get(f'{prefix}pres_state', ''),
                    'pres_pincode': request.form.get(f'{prefix}pres_pincode', ''),
                    
                    # Bank Details
                    'bank_account': request.form.get(f'{prefix}bank_account', ''),
                    'bank_ifsc': request.form.get(f'{prefix}bank_ifsc', ''),
                    'bank_name': request.form.get(f'{prefix}bank_name', ''),
                    
                    # Emergency Contact
                    'emergency_name': request.form.get(f'{prefix}emergency_name', ''),
                    'emergency_phone': request.form.get(f'{prefix}emergency_phone', ''),
                    'emergency_relation': request.form.get(f'{prefix}emergency_relation', ''),
                    
                    # Past Employer
                    'past_employer_company': request.form.get(f'{prefix}past_employer_company', ''),
                    'past_employer_duration': request.form.get(f'{prefix}past_employer_duration', ''),
                    'past_employer_position': request.form.get(f'{prefix}past_employer_position', ''),
                    
                    # Reference
                    'reference_name': request.form.get(f'{prefix}reference_name', ''),
                    'reference_phone': request.form.get(f'{prefix}reference_phone', ''),
                    'reference_relation': request.form.get(f'{prefix}reference_relation', ''),
                    
                    'remarks': request.form.get(f'{prefix}remarks', '')
                }
                
                employee_name = f"{emp_data['first_name']} {emp_data['surname']}"
                
                # Handle photo upload
                photo_file = request.files.get(f'{prefix}photo')
                if photo_file and allowed_file(photo_file.filename):
                    photo_path = save_employee_photo(photo_file, employee_name)
                    optimize_image(photo_path)
                    emp_data['photo_path'] = photo_path
                
                # Handle signature upload
                sig_file = request.files.get(f'{prefix}signature')
                if sig_file and allowed_file(sig_file.filename):
                    sig_path = save_employee_signature(sig_file, employee_name)
                    emp_data['signature_path'] = sig_path
                
                # Create employee record with FK to contractor (Supabase)
                employee_id = employee_model.create(emp_data, contractor_id)
                
                employees_data.append(str(employee_id))
            
            # Get contractor details for success page and email
            contractor = contractor_model.find_by_id(contractor_id)
            contractor_id_str = str(contractor['id'])
            access_token = contractor.get('access_token')
            contractor_email = contractor.get('email')
            contractor_name = contractor.get('contractor_name')
            
            # Send credentials via email
            if contractor_email:
                try:
                    send_contractor_credentials_email(
                        contractor_email,
                        contractor_name,
                        contractor_id_str,
                        access_token
                    )
                except Exception as e:
                    print(f"Email sending failed: {str(e)}")
                    # Don't fail the whole process if email fails
            
            # Clear session
            session.pop('contractor_id', None)
            
            # Redirect to success page showing credentials
            return render_template('success.html',
                contractor_id=contractor_id_str,
                access_token=access_token,
                email=contractor_email,
                employee_count=len(employees_data)
            )
            
        except Exception as e:
            flash(f'Error submitting employees: {str(e)}', 'error')
            return render_template('application_form.html')
    
    return render_template('application_form.html')


@app.route('/contractor/status')
def contractor_status():
    """
    Contractor Status Tracking Page
    Shows approval status for all employees
    """
    # Accept both contractor_id+token or just token
    contractor_id = request.args.get('contractor_id')
    token = request.args.get('token')
    
    if not token:
        flash('Access token is required', 'error')
        return redirect(url_for('check_status_page'))
    
    contractor_model = ContractorModel()
    
    # If contractor_id provided, validate it matches the token
    if contractor_id:
        contractor = contractor_model.find_by_id(contractor_id)
        if not contractor or contractor.get('access_token') != token:
            flash('Invalid Contractor ID or Access Token', 'error')
            return redirect(url_for('check_status_page'))
    else:
        # Find by token only
        contractor = contractor_model.find_by_token(token)
        if not contractor:
            flash('Invalid Access Token', 'error')
            return redirect(url_for('check_status_page'))
    
    # Get all employees with status
    contractor_with_employees = contractor_model.get_with_employees(str(contractor['id']))
    
    return render_template('contractor_status.html', 
                         contractor=contractor_with_employees,
                         token=token)


# ==================== HR DEPARTMENT ROUTES ====================

@app.route('/hr/dashboard')
@login_required('hr')
def hr_dashboard():
    """
    HR Dashboard
    Shows all pending employee applications for HR review
    """
    employee_model = EmployeeModel()
    pending_employees = employee_model.get_pending_for_department('hr')
    
    # Get contractor info for each employee
    contractor_model = ContractorModel()
    for emp in pending_employees:
        contractor = contractor_model.find_by_id(str(emp['contractor_id']))
        emp['contractor_info'] = contractor
    
    return render_template('hr_dashboard.html', employees=pending_employees)


@app.route('/hr/review/<employee_id>')
@login_required('hr')
def hr_review(employee_id):
    """HR Review page for specific employee"""
    employee_model = EmployeeModel()
    employee = employee_model.find_by_id(employee_id)
    
    if not employee:
        flash('Employee not found', 'error')
        return redirect(url_for('hr_dashboard'))
    
    contractor_model = ContractorModel()
    contractor = contractor_model.find_by_id(str(employee['contractor_id']))
    
    return render_template('hr_review.html', employee=employee, contractor=contractor)


@app.route('/hr/approve/<employee_id>', methods=['POST'])
@login_required('hr')
def hr_approve(employee_id):
    """
    HR Approval endpoint
    Automatically uses HR signature from signatures collection
    """
    try:
        approved_by = request.form.get('approved_by', 'HR Department')
        
        # Get HR signature from database
        signature_model = SignatureModel()
        hr_signature = signature_model.get_by_role('HR')
        
        if not hr_signature:
            flash('HR signature not configured. Please upload HR signature first.', 'error')
            return redirect(url_for('hr_dashboard'))
        
        # Update employee approval
        employee_model = EmployeeModel()
        employee_model.update_approval(
            employee_id, 
            'hr', 
            'approved', 
            approved_by,
            hr_signature['path']
        )
        
        flash('Employee approved by HR', 'success')
        return redirect(url_for('hr_dashboard'))
        
    except Exception as e:
        flash(f'Error approving employee: {str(e)}', 'error')
        return redirect(url_for('hr_dashboard'))


@app.route('/hr/reject/<employee_id>', methods=['POST'])
@login_required('hr')
def hr_reject(employee_id):
    """HR Rejection endpoint"""
    try:
        approved_by = request.form.get('approved_by', 'HR Department')
        reason = request.form.get('reason', 'Documents incomplete')
        
        # Get HR signature
        signature_model = SignatureModel()
        hr_signature = signature_model.get_by_role('HR')
        
        # Update employee approval
        employee_model = EmployeeModel()
        employee_model.update_approval(
            employee_id, 
            'hr', 
            'rejected', 
            approved_by,
            hr_signature['path'] if hr_signature else None
        )
        employee_model.set_reject_reason(employee_id, reason)
        
        flash('Employee rejected by HR', 'success')
        return redirect(url_for('hr_dashboard'))
        
    except Exception as e:
        flash(f'Error rejecting employee: {str(e)}', 'error')
        return redirect(url_for('hr_dashboard'))


# ==================== MEDICAL DEPARTMENT ROUTES ====================

@app.route('/medical/dashboard')
@login_required('medical')
def medical_dashboard():
    """
    Medical Dashboard
    Shows employees approved by HR and pending medical review
    """
    employee_model = EmployeeModel()
    pending_employees = employee_model.get_pending_for_department('medical')
    
    contractor_model = ContractorModel()
    for emp in pending_employees:
        contractor = contractor_model.find_by_id(str(emp['contractor_id']))
        emp['contractor_info'] = contractor
    
    return render_template('medical_dashboard.html', employees=pending_employees)


@app.route('/medical/review/<employee_id>')
@login_required('medical')
def medical_review(employee_id):
    """Medical review page"""
    employee_model = EmployeeModel()
    employee = employee_model.find_by_id(employee_id)
    
    if not employee:
        flash('Employee not found', 'error')
        return redirect(url_for('medical_dashboard'))
    
    contractor_model = ContractorModel()
    contractor = contractor_model.find_by_id(str(employee['contractor_id']))
    
    return render_template('medical_review.html', employee=employee, contractor=contractor)


@app.route('/medical/approve/<employee_id>', methods=['POST'])
@login_required('medical')
def medical_approve(employee_id):
    """Medical approval with signature upload"""
    try:
        approved_by = request.form.get('approved_by', 'Medical Officer')
        signature_file = request.files.get('signature')
        
        if not signature_file or not allowed_file(signature_file.filename):
            flash('Medical signature is required', 'error')
            return redirect(url_for('medical_review', employee_id=employee_id))
        
        # Save signature
        signature_path = save_approval_signature(signature_file, 'medical', approved_by)
        
        # Update employee approval
        employee_model = EmployeeModel()
        employee_model.update_approval(
            employee_id, 
            'medical', 
            'approved', 
            approved_by,
            signature_path
        )
        
        flash('Employee approved by Medical Department', 'success')
        return redirect(url_for('medical_dashboard'))
        
    except Exception as e:
        flash(f'Error approving employee: {str(e)}', 'error')
        return redirect(url_for('medical_dashboard'))


@app.route('/medical/reject/<employee_id>', methods=['POST'])
@login_required('medical')
def medical_reject(employee_id):
    """Medical rejection"""
    try:
        approved_by = request.form.get('approved_by', 'Medical Officer')
        reason = request.form.get('reason', 'Medical fitness issues')
        signature_file = request.files.get('signature')
        
        signature_path = None
        if signature_file and allowed_file(signature_file.filename):
            signature_path = save_approval_signature(signature_file, 'medical', approved_by)
        
        employee_model = EmployeeModel()
        employee_model.update_approval(
            employee_id, 
            'medical', 
            'rejected', 
            approved_by,
            signature_path
        )
        employee_model.set_reject_reason(employee_id, reason)
        
        flash('Employee rejected by Medical Department', 'success')
        return redirect(url_for('medical_dashboard'))
        
    except Exception as e:
        flash(f'Error rejecting employee: {str(e)}', 'error')
        return redirect(url_for('medical_dashboard'))


# ==================== SAFETY DEPARTMENT ROUTES ====================

@app.route('/safety/dashboard')
@login_required('safety')
def safety_dashboard():
    """
    Safety Dashboard
    Shows employees approved by HR and Medical, pending safety review
    """
    employee_model = EmployeeModel()
    pending_employees = employee_model.get_pending_for_department('safety')
    
    contractor_model = ContractorModel()
    for emp in pending_employees:
        contractor = contractor_model.find_by_id(str(emp['contractor_id']))
        emp['contractor_info'] = contractor
    
    return render_template('safety_dashboard.html', employees=pending_employees)


@app.route('/safety/review/<employee_id>')
@login_required('safety')
def safety_review(employee_id):
    """Safety review page"""
    employee_model = EmployeeModel()
    employee = employee_model.find_by_id(employee_id)
    
    if not employee:
        flash('Employee not found', 'error')
        return redirect(url_for('safety_dashboard'))
    
    contractor_model = ContractorModel()
    contractor = contractor_model.find_by_id(str(employee['contractor_id']))
    
    return render_template('safety_review.html', employee=employee, contractor=contractor)


@app.route('/safety/approve/<employee_id>', methods=['POST'])
@login_required('safety')
def safety_approve(employee_id):
    """Safety approval with signature upload - triggers ID card generation"""
    try:
        approved_by = request.form.get('approved_by', 'Safety Officer')
        signature_file = request.files.get('signature')
        
        if not signature_file or not allowed_file(signature_file.filename):
            flash('Safety signature is required', 'error')
            return redirect(url_for('safety_review', employee_id=employee_id))
        
        # Save signature
        signature_path = save_approval_signature(signature_file, 'safety', approved_by)
        
        # Update employee approval
        employee_model = EmployeeModel()
        employee_model.update_approval(
            employee_id, 
            'safety', 
            'approved', 
            approved_by,
            signature_path
        )
        
        # Check if employee is fully approved - if yes, generate ID card
        employee = employee_model.find_by_id(employee_id)
        if employee.get('final_status') == 'approved':
            # Generate ID card
            contractor_model = ContractorModel()
            contractor = contractor_model.find_by_id(str(employee['contractor_id']))
            
            # Generate PDF
            employee_name = f"{employee['first_name']}_{employee['surname']}"
            pdf_filename = f"idcard_{secure_filename(employee_name)}_{str(employee['id'])}.pdf"
            pdf_path = os.path.join(Config.IDCARDS_DIR, pdf_filename)
            
            generate_idcard_pdf(employee, contractor, pdf_path)
            
            # Save ID card record
            idcard_model = IDCardModel()
            idcard_model.create(employee_id, pdf_path)
            
            flash('Employee approved by Safety Department. ID Card generated!', 'success')
        else:
            flash('Employee approved by Safety Department', 'success')
        
        return redirect(url_for('safety_dashboard'))
        
    except Exception as e:
        flash(f'Error approving employee: {str(e)}', 'error')
        return redirect(url_for('safety_dashboard'))


@app.route('/safety/reject/<employee_id>', methods=['POST'])
@login_required('safety')
def safety_reject(employee_id):
    """Safety rejection"""
    try:
        approved_by = request.form.get('approved_by', 'Safety Officer')
        reason = request.form.get('reason', 'PPE or safety requirements not met')
        signature_file = request.files.get('signature')
        
        signature_path = None
        if signature_file and allowed_file(signature_file.filename):
            signature_path = save_approval_signature(signature_file, 'safety', approved_by)
        
        employee_model = EmployeeModel()
        employee_model.update_approval(
            employee_id, 
            'safety', 
            'rejected', 
            approved_by,
            signature_path
        )
        employee_model.set_reject_reason(employee_id, reason)
        
        flash('Employee rejected by Safety Department', 'success')
        return redirect(url_for('safety_dashboard'))
        
    except Exception as e:
        flash(f'Error rejecting employee: {str(e)}', 'error')
        return redirect(url_for('safety_dashboard'))


# ==================== ADMIN / SIGNATURE MANAGEMENT ====================

@app.route('/admin/signatures')
@login_required('admin')
def admin_signatures():
    """Admin page to manage department signatures"""
    signature_model = SignatureModel()
    hod_signature_model = HODSignatureModel()
    
    signatures = {
        'hr': signature_model.get_by_role('HR'),
        'system': signature_model.get_by_role('SYSTEM')
    }
    
    hod_signatures = hod_signature_model.get_all()
    
    return render_template('admin_signatures.html', signatures=signatures, hod_signatures=hod_signatures)


@app.route('/admin/upload-signature', methods=['POST'])
@login_required('admin')
def upload_signature():
    """Upload or update department signature"""
    try:
        role = request.form.get('role')  # HR, SYSTEM, or Department name
        name = request.form.get('name')
        signature_file = request.files.get('signature')
        
        if not signature_file or not allowed_file(signature_file.filename):
            flash('Valid signature file is required', 'error')
            return redirect(url_for('admin_signatures'))
        
        # Save signature
        signature_path = save_approval_signature(signature_file, role.lower(), name)
        
        # Update in database
        signature_model = SignatureModel()
        signature_model.update_signature(role, name, signature_path)
        
        flash(f'{role} signature uploaded successfully', 'success')
        return redirect(url_for('admin_signatures'))
        
    except Exception as e:
        flash(f'Error uploading signature: {str(e)}', 'error')
        return redirect(url_for('admin_signatures'))


@app.route('/admin/upload-hod-signature', methods=['POST'])
@login_required('admin')
def upload_hod_signature():
    """Upload or update HOD signature for a department"""
    try:
        department = request.form.get('department')
        hod_name = request.form.get('hod_name')
        signature_file = request.files.get('hod_signature')
        
        if not department or not hod_name:
            flash('Department and HOD name are required', 'error')
            return redirect(url_for('admin_signatures'))
        
        if not signature_file or not allowed_file(signature_file.filename):
            flash('Valid signature file is required', 'error')
            return redirect(url_for('admin_signatures'))
        
        # Save signature
        signature_path = save_approval_signature(signature_file, department.lower(), hod_name)
        
        # Update in database
        hod_signature_model = HODSignatureModel()
        hod_signature_model.create_or_update(department, hod_name, signature_path)
        
        flash(f'HOD signature for {department} department uploaded successfully', 'success')
        return redirect(url_for('admin_signatures'))
        
    except Exception as e:
        flash(f'Error uploading HOD signature: {str(e)}', 'error')
        return redirect(url_for('admin_signatures'))


@app.route('/api/hod-signature/<department>')
def get_hod_signature(department):
    """API endpoint to get HOD signature by department"""
    try:
        hod_signature_model = HODSignatureModel()
        signature = hod_signature_model.get_by_department(department)
        
        if signature:
            return jsonify({
                'success': True,
                'hod_name': signature.get('hod_name', ''),
                'signature_path': signature.get('signature_path', '')
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No HOD signature found for this department'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== ID CARD DOWNLOAD ====================

@app.route('/download/idcard/<employee_id>')
def download_idcard(employee_id):
    """Download ID card PDF"""
    try:
        idcard_model = IDCardModel()
        idcard = idcard_model.find_by_employee(employee_id)
        
        if not idcard:
            flash('ID card not found', 'error')
            return redirect(url_for('index'))
        
        idcard_path = idcard.get('idcard_path')
        
        if not os.path.exists(idcard_path):
            flash('ID card file not found', 'error')
            return redirect(url_for('index'))
        
        employee_model = EmployeeModel()
        employee = employee_model.find_by_id(employee_id)
        filename = f"IDCard_{employee['first_name']}_{employee['surname']}.pdf"
        
        return send_file(idcard_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f'Error downloading ID card: {str(e)}', 'error')
        return redirect(url_for('index'))


# ==================== API ENDPOINTS ====================

@app.route('/api/contractor/status/<contractor_id>')
def api_contractor_status(contractor_id):
    """API endpoint for contractor status tracking"""
    token = request.args.get('token')
    
    contractor_model = ContractorModel()
    contractor = contractor_model.find_by_token(token)
    
    if not contractor or str(contractor['id']) != contractor_id:
        return jsonify({'error': 'Invalid access'}), 403
    
    contractor_with_employees = contractor_model.get_with_employees(contractor_id)
    
    # Format response
    response = {
        'contractor_name': contractor['contractor_name'],
        'employees': []
    }
    
    for emp in contractor_with_employees.get('employee_details', []):
        emp_data = {
            'name': f"{emp['first_name']} {emp['middle_name']} {emp['surname']}".strip(),
            'approval_flow': emp.get('approval_flow'),
            'final_status': emp.get('final_status'),
            'reject_reason': emp.get('reject_reason'),
            'has_idcard': IDCardModel().exists_for_employee(str(emp['id']))
        }
        response['employees'].append(emp_data)
    
    return jsonify(response)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ==================== APPLICATION STARTUP ====================

if __name__ == '__main__':
    # Initialize database indexes
    init_database()
    
    # Run application
    app.run(debug=True, host='0.0.0.0', port=5000)
