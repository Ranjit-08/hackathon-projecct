import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def _send(to: str, subject: str, html: str) -> bool:
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = f"Walk-in Platform <{Config.SMTP_USER}>"
        msg['To']      = to
        msg.attach(MIMEText(html, 'html'))
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=15) as srv:
            srv.ehlo()
            srv.starttls()
            srv.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            srv.sendmail(Config.SMTP_USER, to, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

def send_booking_confirmation(user_name, user_email, company_name, role, interview_date, slot_time):
    subject = f"✅ Interview Slot Confirmed — {company_name}"
    html = f"""
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;background:#f0f4ff;margin:0;padding:20px;">
  <div style="max-width:600px;margin:auto;background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.1);">
    <div style="background:linear-gradient(135deg,#1e3a5f,#4f8ef7);padding:32px;text-align:center;">
      <h1 style="color:white;margin:0;font-size:24px;">🎉 Booking Confirmed!</h1>
      <p style="color:rgba(255,255,255,.85);margin:8px 0 0;">Your interview slot is locked in</p>
    </div>
    <div style="padding:32px;">
      <p style="font-size:16px;color:#1e293b;">Hi <strong>{user_name}</strong>,</p>
      <p style="color:#475569;">Here are your interview details:</p>
      <table style="width:100%;border-collapse:collapse;margin:20px 0;border-radius:8px;overflow:hidden;">
        <tr style="background:#f0f4ff;">
          <td style="padding:14px 16px;font-weight:600;color:#1e3a5f;width:40%;">🏢 Company</td>
          <td style="padding:14px 16px;color:#334155;">{company_name}</td>
        </tr>
        <tr>
          <td style="padding:14px 16px;font-weight:600;color:#1e3a5f;">💼 Role</td>
          <td style="padding:14px 16px;color:#334155;">{role}</td>
        </tr>
        <tr style="background:#f0f4ff;">
          <td style="padding:14px 16px;font-weight:600;color:#1e3a5f;">📅 Date</td>
          <td style="padding:14px 16px;color:#334155;">{interview_date}</td>
        </tr>
        <tr>
          <td style="padding:14px 16px;font-weight:600;color:#1e3a5f;">⏰ Time Slot</td>
          <td style="padding:14px 16px;color:#334155;">{slot_time}</td>
        </tr>
      </table>
      <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:8px;padding:16px;margin-top:16px;">
        <p style="color:#15803d;margin:0;font-size:14px;">💡 <strong>Tip:</strong> Practice with our AI Mock Interview feature to boost your confidence!</p>
      </div>
      <p style="color:#94a3b8;font-size:13px;margin-top:24px;">Best of luck! 🌟<br><strong>Walk-in Interview Platform Team</strong></p>
    </div>
  </div>
</body>
</html>"""
    return _send(user_email, subject, html)

def send_otp_email(to_email, name, otp):
    subject = "🔐 Verify Your Email — HireWalk"
    html = f"""
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;background:#f0f4ff;margin:0;padding:20px;">
  <div style="max-width:500px;margin:auto;background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.1);">
    <div style="background:linear-gradient(135deg,#1e3a5f,#4f8ef7);padding:32px;text-align:center;">
      <h1 style="color:white;margin:0;font-size:24px;">🔐 Verify Your Email</h1>
    </div>
    <div style="padding:32px;text-align:center;">
      <p style="font-size:16px;color:#1e293b;">Hi <strong>{name}</strong>, use this OTP to verify your account:</p>
      <div style="font-size:3rem;font-weight:800;letter-spacing:12px;color:#1e3a5f;margin:24px 0;padding:20px;background:#f0f4ff;border-radius:12px;">{otp}</div>
      <p style="color:#64748b;font-size:.9rem;">This OTP expires in <strong>10 minutes</strong>. Do not share it with anyone.</p>
    </div>
  </div>
</body>
</html>"""
    return _send(to_email, subject, html)