import os
import datetime, time
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug import secure_filename
import stripe

stripe_keys = {
        'secret_key': os.environ['SECRET_KEY'],
        'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']


UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 70 * 1024 * 1024
app.secret_key = os.urandom(24)

def timestamp():
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def allowed_file(filename):
        res = '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
        return res

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        file = request.files['file']
        info = {}
        info["name"] = request.form['name']
        info["email"] = request.form['email']
        info["address"] = request.form['address']
        info["city"] = request.form['city']
        session["email"] = info["email"]
        if file and allowed_file(file.filename):
            f = open("/tmp/addresses", "a")
            filename = secure_filename(file.filename)
            f.write(timestamp() + " " + info["name"] + ":" + info["address"] + ":" + info["city"] + "\n")
            f.close()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template("confirm.html", info=info, key=stripe_keys['publishable_key'])
    return render_template('index.html')



@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents
    amount = 400

    customer = stripe.Customer.create(
        email=session["email"],
        card=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='letter '
    )

    return render_template('thanks.html', amount=amount)

if __name__ == '__main__':
    app.run(debug=True)
