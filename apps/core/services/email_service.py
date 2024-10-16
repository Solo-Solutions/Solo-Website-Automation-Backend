from django.conf import settings
from django.core.mail import send_mail


class EmailService:
    def send_reset_password_email(self, token, email):
        reset_link = f'{settings.FRONTEND_URL}/reset-password?token={token}'

        subject = 'Redefinição de Senha'
        message = f'Clique no link para redefinir sua senha: {reset_link}'
        recipient_list = [email]

        self.send_email(subject, message, recipient_list)

    def send_request_email_change(self, token, email):
        reset_link = f'{settings.FRONTEND_URL}/confirm-email/?token={token}'

        subject = 'Confirme sua mudança de e-mail'
        message = f'Clique no link para confirmar a mudança de e-mail: {reset_link}'
        recipient_list = [email]

        self.send_email(subject, message, recipient_list)

    @staticmethod
    def send_email(subject, message, recipient_list, from_email='no-reply@myapp.com'):
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False
        )