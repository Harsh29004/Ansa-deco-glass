"""
Email utility functions for sending notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config


def send_email(to_email, subject, html_content):
    """
    Send HTML email using SMTP
    Returns: True if successful, False otherwise
    """
    try:
        # Check if email is configured
        if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
            print("Email not configured. Skipping email send.")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = Config.MAIL_DEFAULT_SENDER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            server.starttls()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_contractor_credentials_email(to_email, contractor_name, contractor_id, access_token):
    """
    Send contractor credentials via email
    """
    subject = "ANSA Deco Glass - Your Application Credentials"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8f9fa;
            }}
            .header {{
                background: linear-gradient(135deg, #003366 0%, #0066cc 100%);
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background: white;
                padding: 30px;
                border-radius: 0 0 8px 8px;
            }}
            .credentials {{
                background: #e3f2fd;
                border-left: 4px solid #0066cc;
                padding: 15px;
                margin: 20px 0;
            }}
            .credential-item {{
                margin: 10px 0;
                font-size: 16px;
            }}
            .label {{
                font-weight: bold;
                color: #003366;
            }}
            .value {{
                color: #0066cc;
                font-family: monospace;
                font-size: 18px;
                background: white;
                padding: 8px 12px;
                border-radius: 4px;
                display: inline-block;
                margin-top: 5px;
            }}
            .warning {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                color: #666;
                font-size: 12px;
            }}
            .button {{
                display: inline-block;
                background: #0066cc;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 4px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ANSA Deco Glass</h1>
                <p>Contractor Approval Workflow System</p>
            </div>
            <div class="content">
                <h2>Welcome, {contractor_name}!</h2>
                <p>Thank you for submitting your contractor application. Your credentials have been generated successfully.</p>
                
                <div class="credentials">
                    <h3 style="margin-top: 0;">Your Application Credentials</h3>
                    <div class="credential-item">
                        <div class="label">Contractor ID:</div>
                        <div class="value">{contractor_id}</div>
                    </div>
                    <div class="credential-item">
                        <div class="label">Access Token:</div>
                        <div class="value">{access_token}</div>
                    </div>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Important:</strong>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>Keep these credentials <strong>secure and confidential</strong></li>
                        <li>You will need both to check your application status</li>
                        <li>Do not share your Access Token with anyone</li>
                        <li>Save this email for future reference</li>
                    </ul>
                </div>
                
                <h3>What's Next?</h3>
                <p>Your application will go through the following approval stages:</p>
                <ol>
                    <li><strong>HR Review</strong> - Document verification</li>
                    <li><strong>Medical Check</strong> - Fitness assessment</li>
                    <li><strong>Safety Verification</strong> - PPE and safety requirements</li>
                    <li><strong>ID Card Generation</strong> - Upon final approval</li>
                </ol>
                
                <p style="text-align: center;">
                    <a href="http://localhost:5000/check-status" class="button">Check Application Status</a>
                </p>
                
                <div class="footer">
                    <p>This is an automated email from ANSA Deco Glass Approval System.</p>
                    <p>If you have any questions, please contact: hr@ansadecoglass.com</p>
                    <p>&copy; 2025 ANSA Deco Glass. All rights reserved.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_content)


def send_approval_notification(to_email, employee_name, stage, status):
    """
    Send notification when employee approval status changes
    """
    subject = f"ANSA Deco Glass - {stage} {status.upper()}"
    
    status_color = "#28a745" if status == "approved" else "#dc3545"
    status_text = "✓ Approved" if status == "approved" else "✗ Rejected"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }}
            .header {{ background: linear-gradient(135deg, #003366 0%, #0066cc 100%); color: white; padding: 20px; text-align: center; }}
            .content {{ background: white; padding: 30px; }}
            .status {{ background: {status_color}; color: white; padding: 15px; text-align: center; font-size: 20px; font-weight: bold; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ANSA Deco Glass</h1>
            </div>
            <div class="content">
                <h2>Application Status Update</h2>
                <p>Dear Contractor,</p>
                <p>Employee <strong>{employee_name}</strong> has been reviewed by the {stage} department.</p>
                <div class="status">{status_text}</div>
                <p>Please check the application portal for complete details.</p>
                <p style="margin-top: 30px;">Best regards,<br>ANSA Deco Glass Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_content)
