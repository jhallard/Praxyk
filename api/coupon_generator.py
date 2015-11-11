#Generate Coupon codes for free trials

#python imports
import os                                                                                             
import os.path
import json
import sys
import hashlib
import smtplib

#stripe import
import stripe

#load a json file into an object
def load_json_file(fn) :
    if os.path.isfile(fn) :            
        with open(fn, 'r+') as fh :
            data = json.load(fh)
        return data
    return None

#config
API_CONF_FILE    = os.path.expanduser("~") + "/.praxyk/apiconfig/rootconfig"
STRIPE_CONF_FILE = os.path.expanduser("~") + "/.praxyk/apiconfig/stripeconfig"
apiconf       = load_json_file(API_CONF_FILE)
stripeconf    = load_json_file(STRIPE_CONF_FILE)
DEBUG = True

#Stripe api keys
stripe_secret_key = None
stripe_publishable_key = None
if DEBUG:
   stripe_secret_key = stripeconf['test_secret_key']
   stripe_publishable_key = stripeconf['test_publishable_key']
else:
   stripe_secret_key = stripeconf['live_secret_key']
   stripe_publishable_key = stripeconf['live_publishable_key']

stripe.api_key = stripe_secret_key

#send an email
def send_email(recipient, subject, body):
    import smtplib

    gmail_user = apiconf['email']
    gmail_pwd = apiconf['emailpassword']
    FROM = gmail_user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    headers = "\r\n".join(["from: %s" % FROM,
                       "subject: %s" % SUBJECT,
                       "to: %s" % TO,
                       "mime-version: 1.0",
                       "content-type: text/html"])

    # body_of_email can be plaintext or html!                    
    content = headers + "\r\n\r\n" + TEXT
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, content)
        server.close()
        return True
    except:
        return False
#load a file
def load_file(filename):
	f = open(filename,'r')
	email = []
	for line in f:
		email.append(line)
	f.close()
	return email

def generate_coupon_code(email) :
	email_md5 = hashlib.new("md5")
	email_md5.update(email)
	coupon_code = "Free_Trial_"+email_md5.hexdigest()
	stripe.Coupon.create(
		amount_off=1000,
		duration='once',
		id=coupon_code,
		max_redemptions=1,
		currency='usd')
	return coupon_code
	

#main function
def main(argv=None):
	if argv == None :
		argv = sys.argv	
	emails = load_file(argv[1])
	for email in emails :
		code = generate_coupon_code(email=email)
		template = "<h4>Praxyk: Free Trial</h4><p>Hi,</p><p>You have received this email because you were interested in our services! The coupon you are given will give you $10 off your first billing cycle. First you must sign up with our services and add payment information, then you may use the coupon and our services.</p><p>Your coupon code is <strong>"+code+"</strong>. It can only be used once.</p><p>Thank You,</p><p>Praxyk</p><br><p>For more information on Praxyk Services, visit <a href='www.praxyk.com'>our website</a>!</p>"
            	if not send_email(email, "Praxyk Free Trial", template) :
			f = open("error_email.txt",'w')
			f.write(email + " " + code)
			f.close()
                	
		

if __name__ == "__main__":
    main()


