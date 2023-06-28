from flask import Flask, render_template, request , redirect, session
from twilio.rest import Client
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client.disaster
collection1 = db.users
collection2 = db.volunteers
app = Flask(__name__)
account_sid = 'ACa8a38cc5d6c7e6bb90748632e6ab40f7'
auth_token = '2b340b315fa8a9e085b5c4540e4370f7'
twilio_phone_number = '+13613109266'
app.secret_key = '1234' 
client = Client(account_sid, auth_token)
@app.route('/')
def index():
    return render_template('login.html')
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/home')
def home():
    if(session.get('email')):
        return render_template('home.html')
    return redirect('/login')
@app.route('/disasters')
def disasters():
    if(session.get('email')):
        return render_template('disasters.html')
    return redirect('/login')
@app.route('/logverify',methods=['POST'])
def logverify():
    email=request.form['email']
    password=request.form['pwd']
    data={
        'email':email,
        'password':password
    }
    if(collection1.find_one(data)):
        session['email']=email
        return redirect('/home')
    return redirect('login')
@app.route('/add',methods=['POST'])
def add():
    name=request.form['name']
    email=request.form['email']
    mobile=request.form['mobile']
    dob=request.form['dob']
    aadhar=request.form['aadhar']
    intr=request.form['intr']
    emer=request.form['emer']
    data={
        'name':name,
        'email':email,
        'mobile':mobile,
        'dob':dob,
        'aadhar':aadhar,
        'intr':intr,
        'emer':emer
    }
    collection2.insert_one(data)
    return redirect('/home')
@app.route('/register',methods=['POST'])
def register():
    name=request.form['name']
    email=request.form['email']
    gender=request.form['gen']
    blood=request.form['blood']
    dob=request.form['dob']
    address=request.form['address']
    password=request.form['pass']
    mobile=request.form['phoneno']
    client.verify.services("VA7db744aceef4c0c86bfc41cb12577602").verifications.create(
        to=mobile,
        channel="sms" 
    )
    session['phone_number'] = mobile # Store the phone number in the session
    return render_template("verify.html",mobile=mobile,email=email,gender=gender,blood=blood,dob=dob,address=address,password=password,name=name)
@app.route('/verification',methods=['POST'])
def verification():
    mobile=request.form['mobile']
    codei=request.form['code']
    verification_check = client.verify.services("VA7db744aceef4c0c86bfc41cb12577602").verification_checks.create(
        to=mobile,
        code=codei
    )
    if verification_check.status == 'approved':
        data = {
        'name':request.form['name'],
        'email':request.form['email'],
        'gender':request.form['gender'],
        'blood':request.form['blood'],
        'dob':request.form['dob'],
        'address':request.form['address'],
        'password':request.form['password'],
        'mobile':request.form['mobile']
        }
        collection1.insert_one(data)
        session['email']=request.form['email']
        return redirect('/home')
    else:
        return redirect('/login')
@app.route('/blood_req')
def blood_req():
    if(session.get('email')):
        return render_template('blood_req.html')
    return redirect('/login')
@app.route('/events')
def events():
    if(session.get('email')):
        return render_template('events.html')
    return redirect('/login')
@app.route('/volunteer')
def volunteer():
    if(session.get('email')):
        return render_template('volunteer.html')
    return redirect('/login')
@app.route('/req',methods=['POST'])
def req():
    loc=request.form['loc']
    blood=request.form['blood']
    d=collection1.find({
        'blood':blood
    })
    for i in d:
        print(i["mobile"])
        message = 'URGENT: Blood Needed! Hello Donar, We are in desperate need of your blood type . Please consider donating. Your generous contribution can save a life! Reply YES after logging into your accound in Res-Q-Zone to confirm availability. Thank you!'
        try:
            client.messages.create(
                body=message,
                from_=twilio_phone_number,
                to=i["mobile"]
            )
        except Exception as e:
            return f'Error sending SMS: {str(e)}'
    return redirect('/home')
@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/')
if __name__ == '__main__':
    app.run()
