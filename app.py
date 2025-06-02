from flask import Flask , redirect , render_template , request , url_for , session , jsonify , flash
from pymongo import MongoClient 
from bson.objectid import ObjectId
from reportlab.pdfgen import canvas
import os
from datetime import datetime , timedelta

app = Flask(__name__)

app.secret_key = "HMI@STS"
client = MongoClient("mongodb+srv://hmisrithiru:1324sriram@cluster0.sobnbjm.mongodb.net/")
db_name = client['C1']
Client_data_Appointment = db_name["Client_data_Appointment"]
CLient_data_Contact = db_name["CLient_data_Contact"]
CART = db_name["CART"]

app.permanent_session_lifetime = timedelta(days=70)

@app.route("/")
def Home():
    if session.get("appointed"):
        return render_template("index.html" , apointed = True , ap_date = session.get("date"))
    else:
        return render_template("index.html" , apointed = False)
        
    

@app.route("/appointment", methods=["POST"])
def appointment():
    try:
        full_name = request.form.get("fullname")
        number = request.form.get("number")
        select_gender = request.form.get("select-gender")
        dob = request.form.get("dob")
        app_date = request.form.get("app")
        addresh = request.form.get("addresh")

        if not full_name or not number or not select_gender or not dob or not addresh:
            return "Please fill all fields before submitting.", 400

        data = {
            "full_name": full_name,
            "number": number,
            "select_gender": select_gender,
            "dob": dob,
            "app": app_date,
            "addresh": addresh
        }

   
        Client_data_Appointment.insert_one(data)


        filename = f"{full_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join("static", "pdfs", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        c = canvas.Canvas(filepath)
        c.setFont("Helvetica", 34)
        c.drawString(100, 800, "Appointment Confirmation")
        c.setFont("Helvetica", 12)
        c.drawString(100, 770, f"Name: {full_name}")
        c.drawString(100, 750, f"Phone Number: {number}")
        c.drawString(100, 730, f"Gender: {select_gender}")
        c.drawString(100, 710, f"Date of Birth: {dob}")
        c.drawString(100, 690, f"Appointment Date: {app_date}")
        c.drawString(100, 670, f"Address: {addresh}")
        c.save()
        
        session["appointed"] = full_name
        session["date"] = app_date 
        return redirect(url_for("appointment_success", filename=filename))

    except Exception as e:
        return f"Error: {str(e)}", 500
            

@app.route("/appointment-success")
def appointment_success():
    filename = request.args.get("filename")
    return render_template("suess.html", filename=filename)

@app.route("/clear")
def Cls():
    try:
        session.clear()
        return jsonify({"Sucess":True})
    except:
        return jsonify({"Sucess":False})
        

@app.route("/contact" , methods=["POST"])
def Contact():
    Name = request.form.get("Name")
    Email = request.form.get("Email")
    ph = request.form.get("ph") 
    Meassage = request.form.get("Meassage") 
    
    data={
        "Name":Name,
        "Email":Email,
        "PhoneNumber":ph,
        "Meassage":Meassage
    } 
    
    CLient_data_Contact.insert_one(data)
    return render_template("contactSuess.html")


@app.route("/doc/admin")
def admin():
    
    Appoint = Client_data_Appointment.find({}).sort("_id" , -1)
    c = Client_data_Appointment.count_documents({})
    return render_template('admin.html' , appint = Appoint , c=c)

@app.route("/doc/admin/meassage")
def meassage():
    m = CLient_data_Contact.find({}).sort("_id" , -1)
    c = CLient_data_Contact.count_documents({})
    return render_template("Meassage.html" , m=m ,  c=c)

@app.route("/del/meassage/<m_id>" , methods=["POST"])
def meassage_del(m_id):
    CLient_data_Contact.delete_one({"_id":ObjectId(m_id)})
    return redirect("/doc/admin")

@app.route("/del/mark/<p_id>" , methods=["POST"])
def Mark_store(p_id):
    try:
            get_data = Client_data_Appointment.find_one({"_id":ObjectId(p_id)})
            CART.insert_one(get_data)
            Client_data_Appointment.find_one_and_delete({"_id":ObjectId(p_id)})
            return redirect("/doc/admin")
    except:
        return "Pls Try Again Later Server Loads Many More Times..."

@app.route("/doc/admin/records")
def Records():
    get_Recors = CART.find({}).sort("_id" , -1)
    c = CART.count_documents({})
    return render_template("R.html" , g = get_Recors , c=c)
  
  
@app.route("/del/rec/<p_id>" , methods=["POST"])
def Delete_rec(p_id):
    CART.find_one_and_delete({"_id":ObjectId(p_id)})
    flash("Message deleted successfully!", "success")
    return redirect("/doc/admin/records")  


if __name__ == "__main__":
    app.run(debug=True)
