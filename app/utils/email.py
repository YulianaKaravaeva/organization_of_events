from flask_mail import Message


# Подготовка письма с подтверждением к отправке
def send_email(to, subject, template):
  msg = Message(
      subject,
      recipients=[to],
      html=template,
      sender=app.config["MAIL_DEFAULT_SENDER"],
  )
  mail.send(msg)
