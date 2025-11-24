"""
Utility functions for file handling, signature loading, and PDF generation
"""
import os
from werkzeug.utils import secure_filename
from config import Config
from datetime import datetime
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
from PIL import Image
import io


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_file(file, directory, prefix=''):
    """
    Save uploaded file with secure filename
    Returns: relative path to saved file
    """
    if file and allowed_file(file.filename):
        # Create unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = secure_filename(file.filename)
        filename = f"{prefix}_{timestamp}_{original_filename}" if prefix else f"{timestamp}_{original_filename}"
        
        # Ensure directory exists
        os.makedirs(directory, exist_ok=True)
        
        # Save file
        filepath = os.path.join(directory, filename)
        file.save(filepath)
        
        # Return relative path for storage in database
        return filepath
    return None


def save_contractor_signature(file, contractor_name):
    """Save contractor signature"""
    prefix = secure_filename(contractor_name.replace(' ', '_'))
    return save_file(file, Config.CONTRACTOR_SIGNATURES_DIR, prefix)


def save_employee_photo(file, employee_name):
    """Save employee photo"""
    prefix = secure_filename(employee_name.replace(' ', '_'))
    return save_file(file, Config.EMPLOYEE_PHOTOS_DIR, prefix)


def save_employee_signature(file, employee_name):
    """Save employee signature"""
    prefix = secure_filename(employee_name.replace(' ', '_'))
    return save_file(file, Config.EMPLOYEE_SIGNATURES_DIR, prefix)


def save_approval_signature(file, department, approver_name):
    """Save approval signature (Medical, Safety)"""
    prefix = f"{department}_{secure_filename(approver_name.replace(' ', '_'))}"
    return save_file(file, Config.APPROVAL_SIGNATURES_DIR, prefix)


def optimize_image(filepath, max_size=(800, 800)):
    """
    Optimize image file size while maintaining quality
    Used for photos and signatures
    """
    try:
        with Image.open(filepath) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized
            img.save(filepath, 'JPEG', quality=85, optimize=True)
    except Exception as e:
        print(f"Error optimizing image {filepath}: {e}")


def generate_idcard_pdf_reportlab(data, output_path):
    """
    Generate ID card PDF using ReportLab (Windows-compatible)
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Create canvas - ID card size (85mm x 54mm)
    c = canvas.Canvas(output_path, pagesize=(85*mm, 54*mm))
    
    # Draw border
    c.setStrokeColorRGB(0, 0.2, 0.4)
    c.setLineWidth(1)
    c.rect(2*mm, 2*mm, 81*mm, 50*mm)
    
    # Company logo
    y_position = 48*mm
    if data.get('company_logo') and os.path.exists(data['company_logo']):
        try:
            c.drawImage(data['company_logo'], 4*mm, y_position-6*mm, width=15*mm, height=6*mm, preserveAspectRatio=True, mask='auto')
        except:
            pass
    
    # Company name
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(21*mm, y_position, data['company_name'])
    
    # Company address
    c.setFont("Helvetica", 6)
    c.drawString(21*mm, y_position-3*mm, data['company_address'])
    
    # Employee photo
    y_position = 38*mm
    if data.get('employee_photo') and os.path.exists(data['employee_photo']):
        try:
            c.drawImage(data['employee_photo'], 4*mm, y_position-25*mm, width=20*mm, height=25*mm, preserveAspectRatio=True, mask='auto')
        except:
            # Draw placeholder box
            c.rect(4*mm, y_position-25*mm, 20*mm, 25*mm)
    else:
        c.rect(4*mm, y_position-25*mm, 20*mm, 25*mm)
    
    # Employee information
    c.setFont("Helvetica-Bold", 7)
    x_info = 26*mm
    
    # Name
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(x_info, y_position, "Name:")
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x_info + 12*mm, y_position, data['employee_name'][:30])
    
    # Address
    y_position -= 4*mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(x_info, y_position, "Address:")
    c.setFont("Helvetica", 6)
    c.setFillColorRGB(0, 0, 0)
    address_str = f"{data['address'].get('street', '')}," if data.get('address') else ""
    c.drawString(x_info + 13*mm, y_position, address_str[:28])
    y_position -= 3*mm
    address_str2 = f"{data['address'].get('city', '')}, {data['address'].get('state', '')}" if data.get('address') else ""
    c.drawString(x_info + 13*mm, y_position, address_str2[:28])
    
    # DOB
    y_position -= 4*mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(x_info, y_position, "DOB:")
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x_info + 10*mm, y_position, data.get('dob', ''))
    
    # Joining Date
    y_position -= 4*mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(x_info, y_position, "Joining:")
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x_info + 12*mm, y_position, data.get('date_of_joining', ''))
    
    # Contractor
    y_position -= 4*mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(x_info, y_position, "Contractor:")
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x_info + 15*mm, y_position, data.get('contractor_name', '')[:25])
    
    # Department
    y_position -= 4*mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(x_info, y_position, "Department:")
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x_info + 15*mm, y_position, data.get('department', ''))
    
    # Footer section
    c.setStrokeColorRGB(0, 0.2, 0.4)
    c.line(4*mm, 8*mm, 81*mm, 8*mm)
    
    # Issue and valid dates
    c.setFont("Helvetica-Bold", 6)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(4*mm, 5*mm, f"Issue: {data.get('date_of_issue', '')}")
    c.drawString(4*mm, 3*mm, f"Valid Till: {data.get('valid_until', '')}")
    
    # System signature
    if data.get('system_signature') and os.path.exists(data['system_signature']):
        try:
            c.drawImage(data['system_signature'], 65*mm, 3*mm, width=15*mm, height=6*mm, preserveAspectRatio=True, mask='auto')
        except:
            pass
    c.setFont("Helvetica", 5)
    c.drawString(68*mm, 2*mm, "Manager Signature")
    
    # Save PDF
    c.save()
    return output_path


def generate_idcard_pdf(employee_data, contractor_data, output_path):
    """
    Generate ID Card PDF from employee and contractor data
    Returns: path to generated PDF
    """
    from models import IDCardModel
    
    # Prepare data for template
    idcard_model = IDCardModel()
    existing_card = idcard_model.find_by_employee(str(employee_data['_id']))
    
    issued_at = existing_card['issued_at'] if existing_card else datetime.utcnow()
    valid_till = existing_card['valid_till'] if existing_card else None
    
    if not valid_till:
        from datetime import timedelta
        valid_till = issued_at + timedelta(days=Config.IDCARD_VALIDITY_DAYS)
    
    # Get approval dates
    hr_approval = employee_data.get('approval_flow', {}).get('hr', {})
    medical_approval = employee_data.get('approval_flow', {}).get('medical', {})
    safety_approval = employee_data.get('approval_flow', {}).get('safety', {})
    
    # Date of joining is HR approval date
    date_of_joining = hr_approval.get('at', issued_at)
    
    template_data = {
        'company_name': Config.COMPANY_NAME,
        'company_address': Config.COMPANY_ADDRESS,
        'company_logo': os.path.abspath(Config.COMPANY_LOGO) if os.path.exists(Config.COMPANY_LOGO) else '',
        'employee_name': f"{employee_data.get('first_name', '')} {employee_data.get('middle_name', '')} {employee_data.get('surname', '')}".strip(),
        'employee_photo': os.path.abspath(employee_data.get('photo_path', '')) if employee_data.get('photo_path') and os.path.exists(employee_data.get('photo_path', '')) else '',
        'address': employee_data.get('address', {}).get('present', {}),
        'dob': employee_data.get('dob', ''),
        'date_of_joining': date_of_joining.strftime('%d-%m-%Y') if isinstance(date_of_joining, datetime) else '',
        'date_of_issue': issued_at.strftime('%d-%m-%Y') if isinstance(issued_at, datetime) else '',
        'valid_until': valid_till.strftime('%d-%m-%Y') if isinstance(valid_till, datetime) else '',
        'contractor_name': contractor_data.get('contractor_name', ''),
        'department': contractor_data.get('department', ''),
        'system_signature': os.path.abspath(employee_data.get('system_signature_path', '')) if employee_data.get('system_signature_path') and os.path.exists(employee_data.get('system_signature_path', '')) else ''
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Use ReportLab for Windows compatibility
    if not WEASYPRINT_AVAILABLE:
        generate_idcard_pdf_reportlab(template_data, output_path)
    else:
        # Generate HTML
        html_content = render_idcard_template(template_data)
        # Generate PDF
        HTML(string=html_content, base_url=os.getcwd()).write_pdf(output_path)
    
    return output_path


def render_idcard_template(data):
    """
    Render ID card HTML template
    """
    address_str = f"{data['address'].get('street', '')}, {data['address'].get('city', '')}, {data['address'].get('state', '')} - {data['address'].get('pincode', '')}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: 85.6mm 54mm;
                margin: 0;
            }}
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                width: 85.6mm;
                height: 54mm;
            }}
            .idcard {{
                width: 100%;
                height: 100%;
                border: 2px solid #003366;
                box-sizing: border-box;
                padding: 3mm;
                background: linear-gradient(to bottom, #ffffff 0%, #f0f8ff 100%);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #003366;
                padding-bottom: 2mm;
                margin-bottom: 2mm;
            }}
            .logo {{
                width: 20mm;
                height: auto;
                margin-bottom: 1mm;
            }}
            .company-name {{
                font-size: 11pt;
                font-weight: bold;
                color: #003366;
                margin: 0;
                line-height: 1.2;
            }}
            .company-address {{
                font-size: 7pt;
                color: #666;
                margin: 0;
            }}
            .content {{
                display: flex;
                gap: 3mm;
            }}
            .photo-section {{
                flex-shrink: 0;
            }}
            .photo {{
                width: 20mm;
                height: 25mm;
                object-fit: cover;
                border: 1px solid #003366;
            }}
            .info-section {{
                flex-grow: 1;
                font-size: 7pt;
            }}
            .info-row {{
                margin-bottom: 1mm;
            }}
            .label {{
                font-weight: bold;
                color: #003366;
            }}
            .value {{
                color: #333;
            }}
            .footer {{
                margin-top: 2mm;
                padding-top: 2mm;
                border-top: 1px solid #003366;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 6pt;
            }}
            .signature {{
                width: 15mm;
                height: auto;
                max-height: 6mm;
            }}
            .valid-text {{
                color: #003366;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="idcard">
            <div class="header">
                {f'<img src="{data["company_logo"]}" class="logo" />' if data['company_logo'] else ''}
                <h1 class="company-name">{data['company_name']}</h1>
                <p class="company-address">{data['company_address']}</p>
            </div>
            <div class="content">
                <div class="photo-section">
                    {f'<img src="{data["employee_photo"]}" class="photo" />' if data['employee_photo'] else '<div class="photo"></div>'}
                </div>
                <div class="info-section">
                    <div class="info-row">
                        <span class="label">Name:</span>
                        <span class="value">{data['employee_name']}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Address:</span>
                        <span class="value">{address_str}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">DOB:</span>
                        <span class="value">{data['dob']}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Joining:</span>
                        <span class="value">{data['date_of_joining']}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Contractor:</span>
                        <span class="value">{data['contractor_name']}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Department:</span>
                        <span class="value">{data['department']}</span>
                    </div>
                </div>
            </div>
            <div class="footer">
                <div>
                    <div class="valid-text">Issue: {data['date_of_issue']}</div>
                    <div class="valid-text">Valid Till: {data['valid_until']}</div>
                </div>
                <div>
                    {f'<img src="{data["system_signature"]}" class="signature" />' if data['system_signature'] else ''}
                    <div style="font-size: 5pt;">Manager Signature</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def get_file_size(filepath):
    """Get file size in bytes"""
    if os.path.exists(filepath):
        return os.path.getsize(filepath)
    return 0


def delete_file(filepath):
    """Safely delete a file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        print(f"Error deleting file {filepath}: {e}")
    return False


def get_mime_type(filename):
    """Get MIME type from filename"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    mime_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'pdf': 'application/pdf'
    }
    return mime_types.get(ext, 'application/octet-stream')
