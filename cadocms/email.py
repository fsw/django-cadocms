from django.template import loader, Context, RequestContext
from html2text import HTML2Text
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

def StandardEmail(template, subject, from_email, to_email, variables, request = None, headers = {}, attachments=[], bcc=[]):
        
    html_content = loader.render_to_string(template, variables, None if request is None else RequestContext(request))
    #https://jugger0.atlassian.net/browse/EDL-43
    #text_content = html2text.html2text(html_content).replace("](", "]\n(");
    h = HTML2Text(baseurl='');
    h.inline_links = False;
    text_content = h.handle(html_content)
      
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email, bcc, headers = headers)
    msg.attach_alternative(html_content, "text/html")
    for a in attachments:
        msg.attach_file(a)
    return msg;


def AdminErrorEmail(subject, body):
    msg = EmailMultiAlternatives('[Django]' + subject, body, settings.FROM_EMAIL, [email for admin, email in settings.ADMINS])
    print(msg)
    msg.send();