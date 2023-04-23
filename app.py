from flask import Flask, jsonify, render_template, request
import mysql.connector
import json
from flask import request
import hashlib




app = Flask(__name__)

class user_model():
     def __init__(self):
            
                self.con=mysql.connector.connect(host='localhost',user='root',password='sharad_KUMAR2021',database='medical')
                self.con.autocommit=True
                self.cur=self.con.cursor(dictionary=True)
                self.cur1=self.con.cursor()
                self.cur2=self.con.cursor(dictionary=True)
                self.cur3=self.con.cursor()
                self.cur4=self.con.cursor()
          #       print("connection successful")
          #   except:
          #        print("Not Connected")


        
     def user_get_all(self):
        self.cur.execute("SELECT * FROM user")
        result=self.cur.fetchall()
        return jsonify(result)
    
     def user_sign_up(self,data):
        self.cur1.execute("SELECT user_name from user")
        user_list = self.cur1.fetchall()
        user_list= jsonify(user_list).get_json()
        user_list = [row[0] for row in user_list]
        if (data['user_name'] in user_list):
            return "User Name not available"
        elif (data['password'] != data['confirm_password']):
            return "Passwords did not match ! "
        else:
          self.cur.execute(f"INSERT INTO user(name,mob_number,email,dob,sex,address,user_name,password) VALUES('{data['name']}','{data['mob_number']}','{data['email']}','{data['dob']}','{data['sex']}','Null','{data['user_name']}','{hashlib.sha256(data['password'].encode('utf-8')).hexdigest()}')")
          return "New user added successfully ! "
     def user_log_in(self,data):
        id = data['user_name']
        psd = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
        self.cur1.execute("SELECT user_name FROM user")
        result = self.cur1.fetchall()
        
        column_list = [row[0] for row in result]

        if not(id in column_list):
             return "User Name not found , PLease Enter correct user name"
        else:
             self.cur2.execute(f"SELECT * FROM user WHERE user_name = '{id}'")
             result1 = jsonify(self.cur2.fetchall()).get_json()
            #  return result1
             if result1[0]['password'] != psd :

                  return "You Entered the Wrong Password,Please Enter the Correct Psssword"
             else:
                  info = result1[0]
                  return render_template('log_info.html',user_name = info['user_name'],name = info['name'],email = info['email'],mob_number=info['mob_number'],sex = info['sex'],dob = info['dob'])
    
     def med_detail(self,data): #data here is a name of medicine of type string.
         self.cur.execute(f"SELECT * FROM drugs WHERE drug_name = '{data}'")
         result = jsonify(self.cur.fetchall()).get_json()
         return result

    
     def find_doctors(self,data): #data here is the name of doctor of type string.
         self.cur.execute(f"SELECT * FROM doclist WHERE speciality = '{data}'")
         result = jsonify(self.cur.fetchall()).get_json()
         return result
             

     def book_appointment(self,data):
        self.cur.execute(f"INSERT INTO appointment(user_name,appointment_date,Doctor_ID) VALUES('{data['user_name']}','{data['appointment_date']}','{data['Doctor_ID']}')")
        self.cur1.execute("SELECT Doctor_ID FROM Doctor_duty")
        result = self.cur1.fetchall()
        column_list = [row[0] for row in result]
        if (int(f"{data['Doctor_ID']}") in column_list):
            self.cur.execute(f"UPDATE Doctor_duty SET doc_load = doc_load + 1 WHERE Doctor_ID = '{data['Doctor_ID']}' ")
        else:
            self.cur.execute(f"INSERT INTO Doctor_duty (Doctor_ID, doc_load) VALUES ('{data['Doctor_ID']}', '1') ")
        return "Appointment booked successfully !"
    
     def order_medicine(self,drug_name,data):
         self.cur4.execute("SELECT drug_name FROM drugs")
         drug_list = self.cur4.fetchall()
         drug_list = jsonify(drug_list).get_json()
         drug_list = [row[0] for row in drug_list]
         if not(drug_name in drug_list):
              return "Sorry ,This medicine is not available"
         else:
            self.cur1.execute(f"SELECT quantity FROM drugs WHERE drug_name = '{drug_name}';")
            drug_quantity = self.cur1.fetchall()
            drug_quantity = jsonify(drug_quantity).get_json()
           
            if int(drug_quantity[0][0]) < int(data['order_quantity']):
                return "Sorry, the quantity of medicine demanded is not available"
            else:
                self.cur3.execute("SELECT DATE(DATE_ADD(NOW(), INTERVAL 5 DAY)) as date;")
                date = self.cur3.fetchall()
                column_list = [row[0] for row in date]
                self.cur.execute(f"INSERT INTO orders(drug_name,address,user_name,shipment_date,order_quantity) VALUES('{drug_name}','{data['address']}','{data['user_name']}','{column_list[0]}','{data['order_quantity']}')")
                self.cur2.execute(f"UPDATE drugs SET quantity = quantity - {data['order_quantity']}  WHERE drug_name = '{drug_name}' ")
                return "Order placed successfully"
     
     def get_opd(self,data):
         self.cur.execute(f"SELECT * FROM appointment WHERE Doctor_ID = '{data['Doctor_ID']}'")
         result = jsonify(self.cur.fetchall()).get_json()
         return result
         
     def update_opd(self,data):
         self.cur1.execute(f"SELECT Doctor_ID from appointment WHERE appointment_id = '{data['appointment_id']}'")
         result = self.cur1.fetchall()
         column_list = [row[0] for row in result]
         doctor = column_list[0]
         if int(doctor) != data['Doctor_ID']:
             return "This patient is not alloted to you ! "
         else:
               self.cur.execute(f"DELETE FROM appointment WHERE appointment_id = '{data['appointment_id']}'")
               self.cur.execute(f"UPDATE Doctor_duty SET doc_load = doc_load - 1 WHERE Doctor_ID = '{data['Doctor_ID']}' ")
               return "Appointment list updated successfully ! "

     def update_status(self,data):
         self.cur.execute(f"UPDATE orders SET status = 'Shipped' WHERE order_id = '{data}';")
         return "Order Status updated successfully"


obj =user_model()




@app.route('/')
def hello():
    return 'Hello, World!'

@app.route("/user/get-all",methods=['GET'])
def user_get_all():
    return obj.user_get_all()

@app.route("/user/sign-up",methods=['POST','GET'])
def user_sign_up():
    if request.method == 'POST':
        userDetails = request.form
        data ={ 'name' : userDetails['Full Name'], 'mob_number' : userDetails['Enter Mobile Number'], 'email' : userDetails['Enter a Valid Email'], 'user_name' : userDetails['Create Username'], 'password' : userDetails['Create Password'], 'confirm_password' : userDetails['Confirm Password'], 'dob' : userDetails['Date of Birth'], 'sex' : userDetails['Select Gender']}
        return obj.user_sign_up(data)
    return render_template('login-page.html')

@app.route("/user/log-in",methods=['POST','GET'])
def user_log_in():
     if request.method == 'POST':
        userDetails = request.form
        data = {'user_name' : userDetails['Name'],'password' : userDetails['Password']}
        return obj.user_log_in(data)
     return render_template('login-page.html')


@app.route("/med-detail",methods=['POST','GET'])
def med_detail():
     return obj.med_detail(request.form)

@app.route("/find-doctors",methods=['POST','GET'])
def find_doctors():
     return obj.find_doctors(request.form)

@app.route("/book-an-appointment",methods=['POST','GET'])
def book_an_appointment():
     return obj.book_appointment(request.form)

@app.route("/order/<drug_name>",methods=['POST','GET'])
def order_medicine(drug_name):
     return obj.order_medicine(drug_name,request.form)


@app.route("/doctor/get-opd",methods=['POST','GET'])
def get_opd():
     return obj.get_opd(request.form)

#the following api removes the appointment from appointment table when a doctor sees the patient.
@app.route("/doctor/update-opd",methods=['POST'])
def update_opd():
    return obj.update_opd(request.form)

@app.route("/shipped/<int:order_id>",methods=['POST'])
def update_status(order_id):
    return obj.update_status(order_id)

if __name__ == '__main__':
    app.run(debug=True)




