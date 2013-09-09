from django.template import loader, Context, RequestContext
import html2text
from django.core.mail import send_mail, EmailMultiAlternatives

def StandardEmail(template, subject, from_email, to_email, variables, request, headers = {}):
        
    html_content = loader.render_to_string(template, variables, RequestContext(request))
    text_content = html2text.html2text(html_content)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email, headers = headers)
    msg.attach_alternative(html_content, "text/html")
    
    return msg;