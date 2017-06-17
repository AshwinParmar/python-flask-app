from flask import Flask, render_template, json, request,redirect,session
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'Th!$_mY_$3cR3T'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/user-registered-success')
def userRegisterSuccess():
    return render_template('userRegisterSuccess.html')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
        
        
        # connect to mysql

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()


        if len(data) > 0:
	    _hashed_password = generate_password_hash(_password)
            if check_password_hash(str(data[0][3]),_password):
	    #if str(data[0][3]) == _hashed_password:
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
            

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()


@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:
            
            # All Good, let's call MySQL
            
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
		return render_template('user-registered-success.html', message = 'User created successfully !')
                #return json.dumps({'message':'User created successfully !'})
            else:
		return render_template('error.html', error = 'Error: ' + str(data[0]))
                #return json.dumps({'error':str(data[0])})
        else:
	    return render_template('error.html', error = 'Error: <span>Enter the required fields.</span>')
            #return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

if __name__ == "__main__":
    app.run(host='192.168.33.10',port=90)
