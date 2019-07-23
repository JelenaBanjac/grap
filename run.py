from flask import Flask, render_template, request, send_from_directory
import os
from src.sheets_handler import read_sheet, write_sheet
from datetime import datetime
import time
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from weasyprint import HTML
from email import encoders

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")
LOGIN = "grap.noreply@gmail.com"
PASSWORD = "grapbanjac38."
LOGO_PATH = "assets/img/logo.png"

app = Flask(__name__, template_folder=TEMPLATES_DIR)

def sendemail(from_addr, to_addr_list, cc_addr_list, subject, rendered_message):

	message = MIMEMultipart("alternative")
	message["Subject"] = "Grap MB Štamparija | Porudžbina"
	message["From"] = from_addr
	message["To"] = to_addr_list
	message["Cc"] = "grap.noreply@gmail.com;grapmb@gmail.com"

	part2 = MIMEText(rendered_message, "html")
	message.attach(part2)

	# attach image
	with open(LOGO_PATH, 'rb') as fp:
		part_img = MIMEImage(fp.read())
	part_img.add_header('Content-ID', '<image1>')
	message.attach(part_img)

	# attach file
	filename = 'GrapMB-Racun.pdf' 
    # Open PDF file in binary mode
	with open(filename, "rb") as attachment:
		part_pdf = MIMEBase("application", "octet-stream")
		part_pdf.set_payload(attachment.read())
    # Encode file in ASCII characters to send by email    
	encoders.encode_base64(part_pdf)
    # Add header as key/value pair to attachment part
	part_pdf.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
	message.attach(part_pdf)

	message = message.as_string()

	# Create a secure SSL context
	context = ssl.create_default_context()

	server = smtplib.SMTP("smtp.gmail.com", 587)

	server.ehlo()
	server.starttls(context=context)
	server.ehlo()
	server.login(LOGIN, PASSWORD)

	server.sendmail(from_addr, to_addr_list, message)
	server.close()


@app.route('/')
def root():
	return open('index.html').read()


@app.route('/assets/<path:path>')
def serve_dist(path):
    return send_from_directory('assets', path)


@app.route('/order')
def order():
	return render_template('order.html', articles=read_sheet())


@app.route('/overview', methods=['POST', 'GET'])
def overview():
	if request.method == 'POST':
		articles = read_sheet()

		overview = request.form

		print(overview)

		# all items
		for article in articles:
			article['Komada'] = overview[f'Komada_{article["Id"]}']
			article['Iznos'] = f"{int(article['Komada']) * float(article['Cena']):.2f}"

		# just extract order items
		order = {}
		order['Artikli'] = []
		for article in articles:
			if float(article['Komada']) >= 1:
				order['Artikli'].append(article)

		order['Ukupno'] = f"{sum([float(article['Iznos']) for article in articles]):.2f}"

		# add also address and other info
		for key, value in overview.items():
			if not key.startswith('Komada'):
				order[key] = value
		order['Datum'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

		order['BrojPorudzbenice'] = int(time.time())

		order['Kupac'] = {}
		order['Kupac'] = {'nazivPravnogLica':overview['nazivPravnogLica'],
						  'APRNazivPravnogLica':  overview['APRNazivPravnogLica'],
						  'Grad':  overview['Grad'],
						  'PostanskiBroj':  overview['PostanskiBroj'],
						  'Ulica':  overview['Ulica'],
						  'Pib':  overview['Pib'],
						  'FiksniTelefon':  overview['FiksniTelefon'],
						  'MobilniTelefon':  overview['MobilniTelefon'],
						  'Email':  overview['Email'],}

		if overview['Placanje'] in ['Bezgotovinski', 'Gotovinski']:
			order['Placanje'] = overview['Placanje']
		else:
			order['Placanje'] = 'Bezgotovinski'

		order['Logo'] = LOGO_PATH
		rendered_template_pdf = render_template("bill.html", order=order)
		with open('racun.html', 'w') as f:
			f.write(rendered_template_pdf)
		pdf = HTML(filename='racun.html')
		pdf.write_pdf('GrapMB-Racun.pdf')

		order['Logo'] = "cid:image1"
		rendered_template_email = render_template("bill.html", order=order)

		sendemail(from_addr=LOGIN, to_addr_list=order['Email'], cc_addr_list=[], subject="Test", rendered_message=rendered_template_email)

		# add to database
		for article in order['Artikli']:
			row = [order['BrojPorudzbenice'], order['Kupac']['nazivPravnogLica'], order['Kupac']['APRNazivPravnogLica'], 
				   order['Kupac']['Grad'], order['Kupac']['PostanskiBroj'], order['Kupac']['Ulica'],
				   order['Kupac']['Pib'], order['Kupac']['FiksniTelefon'], order['Kupac']['MobilniTelefon'], order['Kupac']['Email'], order['Placanje'], order['Datum'],
				   article['Id'], article['Cena'], article['Komada'], article['Iznos']]
			write_sheet(row)

		return render_template('confirmation.html', email=order['Email'])


if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
