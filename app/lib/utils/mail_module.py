import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from lib.utils.config import settings

class EmailTemplate:
    def __init__(self, email, password, data):
        self.email = str(email)
        self.password = str(password)
        self.send_mail(data)

    
    def send_mail(self, data): 
        msg = MIMEMultipart()
        msg['From'] = settings.email_from
        msg['To'] = ", ".join(settings.email_to)
        msg['Cc'] = ", ".join(settings.email_cc)
        msg['Subject'] = settings.email_subject

        # add in the message body
        
        html = """\
                  <html>
                  <head></head>
                  <body>
                  İyi akşamlar, <br>
                  <br>
                  Bugün daily rapor göndermeyenler: <br>
                  {0} 
                  <br>
                  Bugün daily rapor gönderenlerin raporları: <br>    
                  {1}
                  </body>
                  </html>
        """.format(data[0].to_html(), 
                   data[1].to_html())

        part1 = MIMEText(html, 'html')
        msg.attach(part1)

        # create server
        server = smtplib.SMTP(host='smtp.elasticemail.com', port=2525)
        server.starttls()

        # Login Credentials for sending the mail
        server.login(self.email, self.password)

        # send the message via the server.
        server.sendmail(settings.email_from, (settings.email_to +
                        settings.email_cc), msg.as_string())

        server.quit()

        print("successfully sent email to " + str(msg['To']))