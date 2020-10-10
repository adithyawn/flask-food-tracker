from flask import Flask, render_template, g, request
import sqlite3

app = Flask(__name__)

###########SETTING DATABASE########

def connect_db():
    sql = sqlite3.connect('C:/Users/Adithya Wilda Nova/Latihan Python/Flask Project/flask-food-tracker/food_log.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

####################################

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/view')
def view():
    return render_template('day.html')

@app.route('/food', methods=['GET','POST'])
def food():
    if request.method == 'POST': #post ini recieved from form input in html with same method
        name = request.form['food-name'] #ini ambil dari form name = 'food-protein
        protein = int(request.form['protein']) #convert to integer biar bisa diitung
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])        
        calories = protein * 4 + carbohydrates * 4 + fat * 9
        
        db = get_db()
        db.execute('insert into food(name, protein, carbohydrates, fat, calories) values (?,?,?,?,?)',\
            [name,protein,carbohydrates,fat,calories]) #ini dari inputnya, yg diatas nama tabelnya food dari db dengan kolom seperti list diatas
        db.commit()
    
    db = get_db()
    cur = db.execute('select name, protein, carbohydrates, fat, calories from food')
    results = cur.fetchall()

        #Buat testing form inputnya udah jalan apa belom bisa pake ini sebelum coba input ke database:
        # return '<h1> Name :{} Protein :{} Carbs :{} Fat :{} </h1>'.format(request.form['food-name'], \
        #     request.form['protein'],request.form['carbohydrates'],request.form['fat'] ) 
                     #ambil data dari name form
    return render_template('add_food.html', results = results) #results ini ambil dr query db trus di render ke html




if __name__ == '__main__':
    app.run(debug=True)