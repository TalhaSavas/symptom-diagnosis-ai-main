import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pyodbc
from datetime import datetime, timedelta
import schedule
import time

# Veritabanı bağlantısı
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                      'Server=EMRECAN;'
                      'Database=SoftwareProject;'
                      'Trusted_Connection=yes;')

def send_email(recipient_email, subject, body, link_text, field):
    gmail_user = 'diagnoishub@gmail.com'
    gmail_password = 'fdzr uheq elkf zoec'

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # E-posta gövdesini HTML olarak tanımlıyoruz
    html_body = f"""
    <html>
    <body>
        <p>{body}</p>
        <p>For more details, visit our <a href="http://127.0.0.1:5000/">{link_text}</a>.</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipient_email, msg.as_string())
        server.close()

        print(f'E-posta gönderildi: {recipient_email}')
        update_sent_email(recipient_email, field)
        return True
    except Exception as e:
        print(f'{recipient_email} adresine e-posta gönderilirken hata oluştu:', str(e))
        return False

def update_sent_email(email, field):
    cursor = conn.cursor()
    cursor.execute(f'UPDATE Patient_table SET {field} = 1 WHERE email = ?', (email,))
    conn.commit()

def get_emails_to_send(field, hours_ago):
    cursor = conn.cursor()
    threshold_time = datetime.now() - timedelta(hours=hours_ago)
    cursor.execute(f'SELECT email FROM Patient_table WHERE {field} = 0 AND Time < ?', (threshold_time,))
    rows = cursor.fetchall()
    return [row[0] for row in rows]

def send_scheduled_emails():
    first_email_subject = "How are you feeling today?"
    first_email_body = " If you don't feel good today,visit our website again."
    second_email_subject = "It's been a week, how are you?"
    second_email_body =  " It's been a week since you visited our site. How are you feeling?"

    recipient_emails = get_emails_to_send('sentEmail', 12)
    if recipient_emails:
        for recipient_email in recipient_emails:
            send_email(recipient_email, first_email_subject, first_email_body, "Visit our index page", 'sentEmail')

    recipient_emails = get_emails_to_send('sentEmail2', 24)
    if recipient_emails:
        for recipient_email in recipient_emails:
            send_email(recipient_email, second_email_subject, second_email_body, "Visit our index page again", 'sentEmail2')

def schedule_job():
    # schedule.every().day.at("09:00").do(send_scheduled_emails)
    # schedule.every().day.at("18:00").do(send_scheduled_emails)
    schedule.every(1).minutes.do(send_scheduled_emails)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    schedule_job()
