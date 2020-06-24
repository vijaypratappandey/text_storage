# importing required build-in modules

#------ flask ------
from flask import Flask           # flask app initialization
from flask import render_template # flask html templates
from flask import request         # flask html actions
from flask import session         # flask session USER_NAME storage

#------- MongoDB -------
from pymongo import MongoClient   # MongoDB driver


# Flask name initialization
app = Flask(__name__)

# Python cnnection with MongoDB 
conn = MongoClient('localhost',27017)
# Database Creation in MongoDB
db = conn['storage']
#  Collection Creation in MongoDB Database
collection = db['text_storage']


# Set the secret key to some random bytes. Keep this really secret!
# Required for session uses
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Home Page Response 
@app.route('/')
def home():
   session.pop('USER_NAME', None)
   return render_template('index.html')


# Every Html Page Response
@app.route('/<string:page_name>')
def method_name(page_name):
   return render_template(page_name)


# Response for Admin SignIn
@app.route('/submit_admin_form', methods=['POST', 'GET'])
def adminSignIn():
   if request.method == 'POST':
      data = request.form.to_dict()
      # print(data)
      email = 'vijay@123.com'
      password = '123'
      msg = None
      if email == data.get('email'):
         if password == data.get('password'):
            return render_template('afterAdminSignIn.html')
         else:
            msg = 'Invalid Password !! Please try again'
            return render_template('adminSignIn.html',msg=msg)
      else:
         msg = 'Invalid Admin Id !! Please try again'
         return render_template('afterLogIn.html', msg = msg)
   else:
      return '''
      <h2 style="color:red;"> Something went wrong !!!</h2>
      '''


# Response for User SignUp Form
@app.route('/submit_signup_form', methods=['POST', 'GET'])
def signUp():
   if request.method == 'POST':
      data = request.form.to_dict()
      # print(data)
      msg = None
      password = data.get('password')
      id = data.get('email')
      if data.get('cnf_password') == password:
         DEFAULT_MONEY = 10
         session['USER_NAME'] = id
         # print('USER_NAME',session['USER_NAME'])
         try:
            ack = collection.insert({
               '_id': id,
               'password':password,
               'token':DEFAULT_MONEY,
               'contents':[]
            })
            # print(ack)

            return render_template('afterLogIn.html',id=id)
         except:
            msg = 'Invalid Email Address !! Already Have Account'
            return render_template('signUp.html',data={'msg':msg})

      else:
         msg = 'Invalid Password !! Both password must be same'
         return render_template('signUp.html',data={'msg':msg})
   else:
      return '''
      <h2 style="color:red;"> Something went wrong !!!</h2>
      '''


# Response for Text Upload
@app.route('/uploader', methods=['POST','GET'])
def file_uploaded():
   if request.method == 'POST':
      title = request.form['title']
      data = request.form['content']
      try:
         token = collection.find_one(
               {'_id':session['USER_NAME']},
               {'_id':0,'token':1}
         )
         token = token.get('token')
         # print(token)
         if token>0:
            ack = collection.update(
                  {'_id':session['USER_NAME']},
                  {"$push": {'contents':
                                 {'title':title, 'text':data},
                           },
                  "$set":{'token':token-1}
                  }
            )
            # print(ack)
            msg = 'Successfully Uploaded'
            return render_template('afterLogIn.html',msg=msg )
         else:
            msg = 'Your Money is Low !! Plaese Contact with Admin' 
            return render_template('index.html', msg=msg)  

      except:
         msg = 'Something went wrong !! Plaese Try Again' 
         return render_template('index.html', msg=msg)  
   else:
      return '''
      <h2 style="color:red;"> Something went wrong !!!</h2>
      '''


# Respomse for User SignIn form 
@app.route('/submit_signin_form', methods=['POST', 'GET'])
def signIn():
   if request.method == 'POST':
      data = request.form.to_dict()
      email = data.get('email')
      password = data.get('password')
      msg = None
      data_mongo = collection.find_one(
         {'_id':email},
         {'password':1,
         '_id':0}
      )
      if data_mongo:
         if password == data_mongo.get('password'):
            session['USER_NAME'] = email
            # print('USER_NAME',session['USER_NAME'])
            return render_template('afterLogIn.html',id=email)
         else:
            msg = 'Invalid Password !! Password may be wrong'
            return render_template('index.html',data={'msg': msg})
      else:
         msg = 'Invalid Email Address !! Your Email is not registered, Please Sign Up'
         return render_template('index.html',data={'msg': msg})
   
   else:
      return '''
      <h2 style="color:red;"> Something went wrong !!!</h2>
      '''


# Response for Balance Check by User
@app.route('/balance')
def balanceCheck():
   balance = collection.find_one(
         {'_id':session['USER_NAME']},
         {'_id':0,'token':1}
   )
   balance = balance.get('token')
   # print(balance)
   return render_template('balanceCheck.html',data={'id':session['USER_NAME'],'balance':balance})



# Respnse for Contents list
@app.route('/contents')
def showContents():
   title = collection.find_one(
         {'_id':session['USER_NAME']},
         {'_id':0,'contents':1}
   )
   titles = title.get('contents')
   # print(titles)
   return render_template('showContents.html',data={'id':session['USER_NAME'],'titles':titles})



# Response for Content Updation by User
@app.route('/update',methods=['POST','GET'])
def update():
   if request.method == 'POST':
      title = request.form['title']
      data = request.form['content']
      try:
         token = collection.find_one(
               {'_id':session['USER_NAME']},
               {'_id':0,'token':1}
         )
         token = token.get('token')
         # print(token)
         if token>0:
            ack = collection.update(
                  {'_id':session['USER_NAME'], 'contents.title':title},
                  {"$set": 
                     {'contents.$.text': data, 'token':token-1 },
                  }
            )
            # print(ack)
            msg = 'Successfully Updated'
            return render_template('updateContent.html',msg=msg)
         else:
            msg = 'Your Money is Low !! Plaese Contact with Admin' 
            return render_template('index.html', msg=msg)  

      except:
         msg = 'Something went wrong !! Plaese Try Again' 
         return render_template('index.html', msg=msg)  
   else:
      return '''
      <h2 style="color:red;"> Something went wrong !!!</h2>
      '''


# Response for Token form
@app.route('/submit_token_form',methods=['POST','GET'])
def token_update():
   if request.method == 'POST':
      id = request.form['email']
      token_up = request.form['token']
      session['USER_NAME'] = id
      # print(id,token_up)
      try:
         token = collection.find_one(
               {'_id':id},
               {'_id':0,'token':1}
         )
         token = token.get('token')
         # print(token)
         ack = collection.update(
                  {'_id': id },
                  {"$set": 
                     {'token':token+int(token_up) },
                  }
            )
         # print(ack)
         msg = 'Successfully Added'
         return render_template('afterAdminSignIn.html',msg=msg) 

      except:
         msg = 'Something went wrong !! Plaese Try Again' 
         return render_template('afterAdminSignIn.html', msg=msg)  
   else:
      return '''
      <h2 style="color:red;"> Something went wrong !!!</h2>
      '''


# Response for Content Removable By User
@app.route('/delete', methods=['POST','GET'])
def deleteContent():
   if request.method == 'POST':
      title = request.form['title']
      try:
         token = collection.find_one(
               {'_id':session['USER_NAME']},
               {'_id':0,'token':1}
         )
         token = token.get('token')
         collection.update(
                  {'_id': session['USER_NAME']},
                  {"$pull": 
                     {
                        'contents':{'title':title}
                     },
                  "$set":{'token':token-1}
                  }
            )
         # print(ack)
         msg = 'Successfully Deleted'
         return render_template('deleteContent.html',msg=msg) 

      except:
         msg = 'Something went wrong !! Plaese Try Again' 
         return render_template('afterLogIn.html', msg=msg)  
   else:
      return '''
      <h2 style="color:red;"> Something went wrong !!!</h2>
      '''
  

# Response for User Removable By Admin
@app.route('/remove_user')
def removeUser():
   try:
      collection.remove({'_id':session['USER_NAME']})
      msg = 'Successfully Removed'
      return render_template('afterAdminSignIn.html',msg=msg) 

   except:
         msg = 'Something went wrong !! Plaese Try Again' 
         return render_template('afterAdminSignIn.html', msg=msg)  

# Used when Deploy on AWS EC2
# app.run(host='0.0.0.0',port='80')



