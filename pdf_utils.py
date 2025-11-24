"""
PDF Generation utilities using ReportLab
Generates ID cards and uploads to Supabase Storage
"""
import os
import io
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import requests
from config import Config
from storage_utils import get_storage_client


def download_image_from_url(url):
    """Download image from URL and return PIL Image"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
    except:
        pass
    return None


def generate_idcard_pdf(employee_data, contractor_data):
    """
    Generate ID Card PDF and upload to Supabase Storage
    Returns: public URL of uploaded PDF
    """
    # Create PDF in memory
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(85*mm, 54*mm))
    
    # Calculate dates
    issued_at = datetime.now()
    valid_till = issued_at + timedelta(days=Config.IDCARD_VALIDITY_DAYS)
    
    # Get approval dates
    hr_approval_at = employee_data.get('hr_approved_at')
    if isinstance(hr_approval_at, str):
        try:
            hr_approval_at = datetime.fromisoformat(hr_approval_at.replace('Z', '+00:00'))
        except:
            hr_approval_at = issued_at
    date_of_joining = hr_approval_at if hr_approval_at else issued_at
    
    # Draw border
    c.setStrokeColorRGB(0, 0.2, 0.4)
    c.setLineWidth(1)
    c.rect(2*mm, 2*mm, 81*mm, 50*mm)
    
    # Company logo
    y_position = 48*mm
    try:
        logo_path = Config.COMPANY_LOGO
        if os.path.exists(logo_path):
            c.drawImage(logo_path, 4*mm, y_position-6*mm, width=15*mm, height=6*mm, 
                       preserveAspectRatio=True, mask='auto')
    except:
        pass
    
    # Company name
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(21*mm, y_position, Config.COMPANY_NAME)
    
    # Company address
    c.setFont("Helvetica", 6)
    c.drawString(21*mm, y_position-3*mm, Config.COMPANY_ADDRESS)
    
    # Employee photo
    y_position = 38*mm
    photo_url = employee_data.get('photo_path')
    if photo_url:
        try:
            photo_img = download_image_from_url(photo_url)
            if photo_img:
                # Convert to RGB
                if photo_img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', photo_img.size, (255, 255, 255))
                    if photo_img.mode == 'P':
                        photo_img = photo_img.convert('RGBA')
                    if photo_img.mode == 'RGBA':
                        background.paste(photo_img, mask=photo_img.split()[-1])
                    else:
                        background.paste(photo_img)
                    photo_img = background
                
                # Resize to fit
                photo_img.thumbnail((200, 250), Image.Resampling.LANCZOS)
                
                # Save to buffer
                img_buffer = io.BytesIO()
                photo_img.save(img_buffer, format='JPEG')
                img_buffer.seek(0)
                
                c.drawImage(ImageReader(img_buffer), 4*mm, y_position-25*mm, 
                           width=20*mm, height=25*mm, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Error loading photo: {e}")
            c.rect(4*mm, y_position-25*mm, 20*mm, 25*mm)
    else:
        c.rect(4*mm, y_position-25*mm, 20*mm, 25*mm)
    
    # Employee information
    c.setFont("Helvetica-Bold", 7)
    x_info = 26*mm
    
    # Name
    employee_name = f"{employee_data.get('first_name', '')} {employee_data.get('middle_name', '')} {employee_data.get('surname', '')}".strip()
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(x_info, y_position, "Name:")
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x_info + 12*mm, y_position, employee_name[:30])
    
    # Address
    y_position -= 4*mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(x_info, y_position, "Address:")
    c.setFont("Helvetica", 6)
    c.setFillColorRGB(0, 0, 0)
    address_present = employee_data.get('address_present', '')
    if len(address_present) > 28:
        c.drawString(x_info + 13*mm, y_position, address_present[:28])
        y_position -= 3*mm
        c.drawString(x_info + 13*mm, y_position, address_present[28:56])
    else:
        c.drawString(x_info + 13*mm, y_position, address_present)
    
    # DOB
    y_position -= 4*mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(x_info, y_position, "DOB:")
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x_info + 10*mm, y_position, employee_data.get('dob', ''))
    
    # Joining Date
    y_position -= 4*mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(x_info, y_position, "Joining:")
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x_info + 12*mm, y_position, date_of_joining.strftime('%d-%m-%Y'))
    
    # Contractor
    y_position -= 4*mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(x_info, y_position, "Contractor:")
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x_info + 15*mm, y_position, contractor_data.get('contractor_name', '')[:25])
    
    # Department
    y_position -= 4*mm
    c.setFont("Helvetica-Bold", 7)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(x_info, y_position, "Department:")
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x_info + 15*mm, y_position, contractor_data.get('department', ''))
    
    # Footer section
    c.setStrokeColorRGB(0, 0.2, 0.4)
    c.line(4*mm, 8*mm, 81*mm, 8*mm)
    
    # Issue and valid dates
    c.setFont("Helvetica-Bold", 6)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(4*mm, 5*mm, f"Issue: {issued_at.strftime('%d-%m-%Y')}")
    c.drawString(4*mm, 3*mm, f"Valid Till: {valid_till.strftime('%d-%m-%Y')}")
    
    # System signature
    signature_url = employee_data.get('system_signature_path')
    if signature_url:
        try:
            sig_img = download_image_from_url(signature_url)
            if sig_img:
                # Convert to RGB
                if sig_img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', sig_img.size, (255, 255, 255))
                    if sig_img.mode == 'P':
                        sig_img = sig_img.convert('RGBA')
                    if sig_img.mode == 'RGBA':
                        background.paste(sig_img, mask=sig_img.split()[-1])
                    else:
                        background.paste(sig_img)
                    sig_img = background
                
                sig_buffer = io.BytesIO()
                sig_img.save(sig_buffer, format='JPEG')
                sig_buffer.seek(0)
                
                c.drawImage(ImageReader(sig_buffer), 65*mm, 3*mm, 
                           width=15*mm, height=6*mm, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Error loading signature: {e}")
    
    c.setFont("Helvetica", 5)
    c.drawString(68*mm, 2*mm, "Manager Signature")
    
    # Save PDF
    c.save()
    
    # Upload to Supabase Storage
    pdf_buffer.seek(0)
    pdf_content = pdf_buffer.read()
    
    # Generate filename
    employee_name_clean = employee_name.replace(' ', '_')
    pdf_filename = f"idcard_{employee_name_clean}_{employee_data['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = f"idcards/{pdf_filename}"
    
    try:
        storage = get_storage_client()
        storage.from_('idcards').upload(
            file_path,
            pdf_content,
            file_options={"content-type": "application/pdf"}
        )
        
        # Get public URL
        public_url = storage.from_('idcards').get_public_url(file_path)
        return public_url
    except Exception as e:
        print(f"Error uploading PDF to Supabase: {e}")
        return None
