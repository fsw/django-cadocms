from django.template import loader, Context, RequestContext
import html2text
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

def StandardEmail(template, subject, from_email, to_email, variables, request = None, headers = {}):
        
    html_content = loader.render_to_string(template, variables, None if request is None else RequestContext(request))
    text_content = html2text.html2text(html_content)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email, headers = headers)
    msg.attach_alternative(html_content, "text/html")
    
    return msg;


def AdminErrorEmail(subject, body):
    msg = EmailMultiAlternatives('[Django]' + subject, body, settings.FROM_EMAIL, [email for admin, email in settings.ADMINS])
    print(msg)
    msg.send();