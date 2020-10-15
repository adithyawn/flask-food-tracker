from flask import Flask, render_template, g, request
from datetime import datetime
from database import connect_db, get_db


app = Flask(__name__)

##MASIH ADA HUBUNGANNYA SAMA DATABASE TAPI INI LEBIH FLASK SPESIFIC##

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

####################################

@app.route('/', methods=['GET','POST'])
def index():
    db = get_db()

    if request.method == 'POST':

        db.execute('insert into log_date (entry_date) values (?)',[database_date]) #? itu variabel yg mau diinput
        db.commit()
    
    # cur = db.execute('select entry_date from log_date order by entry_date desc') diganti dengan :
    cur = db.execute('select log_date.entry_date, sum(food.protein) as protein , sum(food.carbohydrates) as carbohydrates , sum(food.fat) as fat, \
        sum(food.calories) as calories from log_date left join food_date on food_date.log_date_id = log_date.id left join food on food.id = food_date.food_id group by log_date.entry_date') #as itu biar ada key-nya karena kan udah ada sum perlu key lagi jadinya
        #awalnya pakai join aja, karena gak bisa muncul di list ketika diadd makanya pakai left join, karena left join valuenya boleh 0    
    results = cur.fetchall() #karena gak bisa ubah format inputnya sql makanya dibuat lagi list sendiri (pretty_results) untuk costumize date di luar ini 

    return render_template('home.html')

@app.route('/add', methods=['GET','POST'])
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
    return render_template('add_list.html',results=results) #results ini ambil dr query db trus di render ke html




if __name__ == '__main__':
    app.run(debug=True)