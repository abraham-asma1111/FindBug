#!/usr/bin/env python3
"""
Seed Email Templates - Essential templates for notification system
Run this script to populate email_templates table with default templates
"""
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from src.core.database import get_db
from src.domain.models.ops import EmailTemplate


def create_email_templates(db: Session):
    """Create essential email templates"""
    
    templates = [
        {
            "name": "report_submitted",
            "subject": "New Vulnerability Report Submitted - {{notification_title}}",
            "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>New Report Submitted</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">🔒 New Vulnerability Report</h1>
        </div>
        
        <div style="background: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; border-top: none;">
            <h2 style="color: #2563eb; margin-top: 0;">Hello {{user_name}},</h2>
            
            <p>A new vulnerability report has been submitted to your program:</p>
            
            <div style="background: white; padding: 20px; border-left: 4px solid #2563eb; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #333;">{{notification_title}}</h3>
                <p style="color: #666; margin-bottom: 0;">{{notification_message}}</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{action_url}}" 
                   style="background-color: #2563eb; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    {{action_text}}
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px; text-align: center;">
                Please review this report as soon as possible and provide initial feedback within 24 hours.
            </p>
        </div>
        
        <div style="background: #f1f3f4; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666;">
            <p style="margin: 0;">This notification was sent by {{platform_name}}</p>
            <p style="margin: 5px 0 0;">Bahir Dar University - Cyber Security Program</p>
        </div>
    </div>
</body>
</html>
            """,
            "body_text": """
Hello {{user_name}},

A new vulnerability report has been submitted to your program:

{{notification_title}}
{{notification_message}}

Please review this report as soon as possible and provide initial feedback within 24 hours.

{{action_url}}

---
{{platform_name}}
Bahir Dar University - Cyber Security Program
            """,
            "variables": ["user_name", "notification_title", "notification_message", "action_url", "action_text", "platform_name"]
        },
        
        {
            "name": "report_status_changed",
            "subject": "Report Status Updated: {{notification_title}}",
            "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Report Status Updated</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #10b981; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">📋 Report Status Updated</h1>
        </div>
        
        <div style="background: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; border-top: none;">
            <h2 style="color: #10b981; margin-top: 0;">Hello {{user_name}},</h2>
            
            <p>Good news! Your vulnerability report status has been updated:</p>
            
            <div style="background: white; padding: 20px; border-left: 4px solid #10b981; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #333;">{{notification_title}}</h3>
                <p style="color: #666; margin-bottom: 0;">{{notification_message}}</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{action_url}}" 
                   style="background-color: #10b981; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    {{action_text}}
                </a>
            </div>
        </div>
        
        <div style="background: #f1f3f4; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666;">
            <p style="margin: 0;">This notification was sent by {{platform_name}}</p>
            <p style="margin: 5px 0 0;">Bahir Dar University - Cyber Security Program</p>
        </div>
    </div>
</body>
</html>
            """,
            "body_text": """
Hello {{user_name}},

Good news! Your vulnerability report status has been updated:

{{notification_title}}
{{notification_message}}

{{action_url}}

---
{{platform_name}}
Bahir Dar University - Cyber Security Program
            """,
            "variables": ["user_name", "notification_title", "notification_message", "action_url", "action_text", "platform_name"]
        },
        
        {
            "name": "bounty_approved",
            "subject": "🎉 Bounty Approved! {{notification_title}}",
            "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Bounty Approved!</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 28px;">🎉 Bounty Approved!</h1>
            <p style="margin: 10px 0 0; font-size: 18px;">Congratulations on your successful submission!</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; border-top: none;">
            <h2 style="color: #667eea; margin-top: 0;">Hello {{user_name}},</h2>
            
            <p>Excellent work! Your bounty has been approved:</p>
            
            <div style="background: white; padding: 20px; border-left: 4px solid #667eea; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; color: #333;">{{notification_title}}</h3>
                <p style="color: #666; margin-bottom: 0;">{{notification_message}}</p>
            </div>
            
            <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #10b981;">
                <p style="margin: 0; color: #059669; font-weight: bold;">💡 Next Steps:</p>
                <p style="margin: 5px 0 0; color: #059669;">Your bounty will be processed within 30 days. Please ensure your KYC is complete for payment.</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{action_url}}" 
                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 35px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 16px;">
                    {{action_text}}
                </a>
            </div>
        </div>
        
        <div style="background: #f1f3f4; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666;">
            <p style="margin: 0;">This notification was sent by {{platform_name}}</p>
            <p style="margin: 5px 0 0;">Bahir Dar University - Cyber Security Program</p>
        </div>
    </div>
</body>
</html>
            """,
            "body_text": """
Hello {{user_name}},

Excellent work! Your bounty has been approved:

{{notification_title}}
{{notification_message}}

Next Steps:
Your bounty will be processed within 30 days. Please ensure your KYC is complete for payment.

{{action_url}}

---
{{platform_name}}
Bahir Dar University - Cyber Security Program
            """,
            "variables": ["user_name", "notification_title", "notification_message", "action_url", "action_text", "platform_name"]
        },
        
        {
            "name": "bounty_paid",
            "subject": "💰 Bounty Paid! {{notification_title}}",
            "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Bounty Paid!</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 28px;">💰 Bounty Paid!</h1>
            <p style="margin: 10px 0 0; font-size: 18px;">Your payment has been processed successfully!</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; border-top: none;">
            <h2 style="color: #f5576c; margin-top: 0;">Hello {{user_name}},</h2>
            
            <p>Great news! Your bounty payment has been processed:</p>
            
            <div style="background: white; padding: 20px; border-left: 4px solid #f5576c; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; color: #333;">{{notification_title}}</h3>
                <p style="color: #666; margin-bottom: 0;">{{notification_message}}</p>
            </div>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <p style="margin: 0; color: #856404; font-weight: bold;">📝 Payment Details:</p>
                <p style="margin: 5px 0 0; color: #856404;">Check your dashboard for payment details and transaction history.</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{action_url}}" 
                   style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 15px 35px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 16px;">
                    {{action_text}}
                </a>
            </div>
        </div>
        
        <div style="background: #f1f3f4; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666;">
            <p style="margin: 0;">This notification was sent by {{platform_name}}</p>
            <p style="margin: 5px 0 0;">Bahir Dar University - Cyber Security Program</p>
        </div>
    </div>
</body>
</html>
            """,
            "body_text": """
Hello {{user_name}},

Great news! Your bounty payment has been processed:

{{notification_title}}
{{notification_message}}

Payment Details:
Check your dashboard for payment details and transaction history.

{{action_url}}

---
{{platform_name}}
Bahir Dar University - Cyber Security Program
            """,
            "variables": ["user_name", "notification_title", "notification_message", "action_url", "action_text", "platform_name"]
        },
        
        {
            "name": "reputation_updated",
            "subject": "📈 Reputation Updated: {{notification_title}}",
            "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Reputation Updated</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #8b5cf6; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">📈 Reputation Updated</h1>
        </div>
        
        <div style="background: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; border-top: none;">
            <h2 style="color: #8b5cf6; margin-top: 0;">Hello {{user_name}},</h2>
            
            <p>Your reputation score has been updated:</p>
            
            <div style="background: white; padding: 20px; border-left: 4px solid #8b5cf6; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #333;">{{notification_title}}</h3>
                <p style="color: #666; margin-bottom: 0;">{{notification_message}}</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{action_url}}" 
                   style="background-color: #8b5cf6; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    {{action_text}}
                </a>
            </div>
        </div>
        
        <div style="background: #f1f3f4; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666;">
            <p style="margin: 0;">This notification was sent by {{platform_name}}</p>
            <p style="margin: 5px 0 0;">Bahir Dar University - Cyber Security Program</p>
        </div>
    </div>
</body>
</html>
            """,
            "body_text": """
Hello {{user_name}},

Your reputation score has been updated:

{{notification_title}}
{{notification_message}}

{{action_url}}

---
{{platform_name}}
Bahir Dar University - Cyber Security Program
            """,
            "variables": ["user_name", "notification_title", "notification_message", "action_url", "action_text", "platform_name"]
        },
        
        {
            "name": "welcome_staff",
            "subject": "Welcome to FindBug Platform - Staff Account",
            "body_html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome to FindBug</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">🚀 Welcome to FindBug Platform</h1>
            <p style="margin: 10px 0 0; font-size: 18px;">Your Staff Account is Ready!</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 30px; border: 1px solid #dee2e6; border-top: none;">
            <h2 style="color: #2563eb; margin-top: 0;">Hello {{user_name}},</h2>
            
            <p>Welcome aboard! Your staff account has been created and you're now part of the FindBug security team.</p>
            
            <div style="background: #e3f2fd; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #2563eb;">
                <h3 style="margin-top: 0; color: #1565c0;">🎯 Your Responsibilities:</h3>
                <ul style="color: #1565c0; margin: 10px 0; padding-left: 20px;">
                    <li>Review and triage vulnerability reports</li>
                    <li>Assess severity and validity</li>
                    <li>Communicate with researchers</li>
                    <li>Maintain platform security standards</li>
                </ul>
            </div>
            
            <div style="background: #fff3e0; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ff9800;">
                <p style="margin: 0; color: #e65100; font-weight: bold;">🔐 Login Information:</p>
                <p style="margin: 5px 0 0; color: #e65100;">Please check your email for login credentials or contact your administrator.</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{action_url}}" 
                   style="background-color: #2563eb; color: white; padding: 15px 35px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 16px;">
                    Access Your Dashboard
                </a>
            </div>
        </div>
        
        <div style="background: #f1f3f4; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666;">
            <p style="margin: 0;">This notification was sent by {{platform_name}}</p>
            <p style="margin: 5px 0 0;">Bahir Dar University - Cyber Security Program</p>
        </div>
    </div>
</body>
</html>
            """,
            "body_text": """
Hello {{user_name}},

Welcome aboard! Your staff account has been created and you're now part of the FindBug security team.

Your Responsibilities:
- Review and triage vulnerability reports
- Assess severity and validity
- Communicate with researchers
- Maintain platform security standards

Login Information:
Please check your email for login credentials or contact your administrator.

{{action_url}}

---
{{platform_name}}
Bahir Dar University - Cyber Security Program
            """,
            "variables": ["user_name", "action_url", "platform_name"]
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for template_data in templates:
        # Check if template exists
        existing = db.query(EmailTemplate).filter(
            EmailTemplate.name == template_data["name"]
        ).first()
        
        if existing:
            # Update existing template
            existing.subject = template_data["subject"]
            existing.body_html = template_data["body_html"]
            existing.body_text = template_data["body_text"]
            existing.variables = template_data["variables"]
            existing.is_active = True
            updated_count += 1
            print(f"✅ Updated template: {template_data['name']}")
        else:
            # Create new template
            template = EmailTemplate(
                name=template_data["name"],
                subject=template_data["subject"],
                body_html=template_data["body_html"],
                body_text=template_data["body_text"],
                variables=template_data["variables"],
                is_active=True
            )
            db.add(template)
            created_count += 1
            print(f"✅ Created template: {template_data['name']}")
    
    try:
        db.commit()
        print(f"\n🎉 Email templates setup complete!")
        print(f"📊 Created: {created_count} templates")
        print(f"🔄 Updated: {updated_count} templates")
        print(f"📧 Total templates: {created_count + updated_count}")
        
        # List all templates
        all_templates = db.query(EmailTemplate).filter(EmailTemplate.is_active == True).all()
        print(f"\n📋 Available templates:")
        for template in all_templates:
            print(f"   - {template.name}: {template.subject[:50]}...")
            
    except Exception as e:
        print(f"❌ Error creating templates: {e}")
        db.rollback()
        raise


def main():
    """Main function"""
    print("🚀 Starting email templates seeding...")
    
    # Get database session
    db = next(get_db())
    
    try:
        create_email_templates(db)
        print("\n✅ Email templates seeding completed successfully!")
    except Exception as e:
        print(f"\n❌ Error seeding email templates: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
