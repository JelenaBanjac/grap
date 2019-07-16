from flask import Flask, render_template, request, send_from_directory
import os
from src.sheets_handler import read_sheet, write_sheet
import datetime
import time
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")
LOGIN = "jelena.b94@gmail.com"
PASSWORD = "lepotica94."

app = Flask(__name__, static_url_path=os.path.abspath(__file__), static_folder='', template_folder=TEMPLATES_DIR)


def sendemail(from_addr, to_addr_list, cc_addr_list, subject, rendered_message):

    message = MIMEMultipart("alternative")
    message["Subject"] = "Grap MB Stamparija | Porudzbina"
    message["From"] = from_addr
    message["To"] = to_addr_list
    message["Bcc"] = LOGIN

    part2 = MIMEText(rendered_message, "html")
    message.attach(part2)

    fp = open('../img/logo.png', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    msgImage.add_header('Content-ID', '<image1>')
    message.attach(msgImage)

    # Create a secure SSL context
    context = ssl.create_default_context()

    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    server.login(LOGIN, PASSWORD)
    message = message.as_string()
    server.sendmail(from_addr, to_addr_list, message)
    server.close()


@app.route('/')
def root():
    #print(app.send_static_file('index.html'))
    print("HELLLOOOO")
    return app.send_static_file('index.html')


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
        order['Datum'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

        order['BrojPorudzbenice'] = int(time.time())

        order['Kupac'] = {}
        order['Kupac'] = {'nazivPravnogLica':overview['nazivPravnogLica'],
                          'APRNazivPravnogLica':  overview['APRNazivPravnogLica'],
                          'Adresa':  overview['Adresa'],
                          'Pib':  overview['Pib'],
                          'BrojTelefona':  overview['BrojTelefona'],
                          'Email':  overview['Email'],}

        order['Placanje'] = 'Gotovina' if overview['Placanje'] == 'on' else 'Avans'

        order['Logo'] = "cid:image1"

        print(order)
        rendered_template_email = render_template("bill.html", order=order)
        sendemail(from_addr=LOGIN, to_addr_list=LOGIN, cc_addr_list=[], subject="Test", rendered_message=rendered_template_email)

        return render_template('confirmation.html', email=order['Email'])


if __name__ == '__main__':
    app.run()


