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
        date = request.form['date'] #assuming the date is in YYYY-MM-DD format
        dt = datetime.strptime(date, '%Y-%m-%d') #strptime untuk convert string ke format datetime object
        database_date = datetime.strftime(dt, '%Y%m%d') #ubah ke format yg diinginkan dengan strf

        db.execute('insert into log_date (entry_date) values (?)',[database_date]) #? itu variabel yg mau diinput
        db.commit()
    
    # cur = db.execute('select entry_date from log_date order by entry_date desc') diganti dengan :
    cur = db.execute('select log_date.entry_date, sum(food.protein) as protein , sum(food.carbohydrates) as carbohydrates , sum(food.fat) as fat, \
        sum(food.calories) as calories from log_date left join food_date on food_date.log_date_id = log_date.id left join food on food.id = food_date.food_id group by log_date.entry_date') #as itu biar ada key-nya karena kan udah ada sum perlu key lagi jadinya
        #awalnya pakai join aja, karena gak bisa muncul di list ketika diadd makanya pakai left join, karena left join valuenya boleh 0    
    results = cur.fetchall() #karena gak bisa ubah format inputnya sql makanya dibuat lagi list sendiri (pretty_results) untuk costumize date di luar ini 

    date_results = [] #biar nanti dictionarynya jadi list [{'entry_date': '20201010', 'pretty_date': 'October 10, 2020'}, {'entry_date': '20201015', 'pretty_date': 'October 10, 2020'} dst..]

    for i in results :
        single_date = {} #membuat dictionary baru, contoh dictionary :
                        # dict_sample = {
                        # "Company": "Toyota",
                        # "model": "Premio",
                        # "year": 2012 }
                        # x = dict_sample["model"]
                        # print(x)
        single_date['entry_date'] = i['entry_date']
        single_date['protein'] = i['protein']
        single_date['carbohydrates'] = i['carbohydrates']
        single_date['fat'] = i['fat']
        single_date['calories'] = i['calories']

        d = datetime.strptime(str(i['entry_date']), '%Y%m%d') #i itu sebenernya looping dari results = cur.fetchall()['entry_date']
        single_date['pretty_date'] = datetime.strftime(d, '%B %d, %Y') #menambah elemen ke dictionary single_date >> single_date["key"] = "value"
        date_results.append(single_date) #tambahkan listnya dr single data ke list pretty results

    return render_template('home.html',results=date_results)

@app.route('/view/<date>', methods=['GET','POST'])
def view(date):
    db = get_db()

    #STEP 1 : TARIK DATA ID DAN ENTRY_DATE YANG SESUAI DENGAN <DATE> DARI TABLE LOG_DATE
    cur = db.execute('select id, entry_date from log_date where entry_date = ?', [date])
    date_result = cur.fetchone() # fetch cuma 1 data pertama, beda sama fetch all
    #keluarannya dari result sebenernya bentuknya dictionary >> result['id'] , result['entry_date']

    #STEP 2 : KALO DATA DI SUBMIT MAKA INPUT DATA KE TABEL FOOD_DATE
    #GAK BISA SUBMIT ID YANG SAMA, KARENA PRIMARY HARUS UNIQUE
    if request.method == 'POST':
    # ini cuma buat test data yg masuk bener gak >> return '<h1>The food item added is #{}</h1>'.format(request.form['food-select']) #food select itu nama isian list form 
        #STEP 2 DETAIL : INPUT DATA KE TABEL FOOD_DATE
        db.execute('insert into food_date (food_id, log_date_id) values (?,?)',[request.form['food-select'],date_result['id']]) #kolom log_date di tabel food_date diisi id dari tabel log_date 
        db.commit()                                                                                                                 #input juga id makanannya dari form isian

    #STEP 3 : INI UNTUK DITAMPILKAN DI HEADER
    d = datetime.strptime(str(date_result['entry_date']), '%Y%m%d') #date tarik dari date_result = cur.fetchone()
    pretty_date = datetime.strftime(d, '%B %d, %Y') #konversi tanggal sesuai format

    #STEP 4 : INI UNTUK DI TAMPILKAN DI DROPDOWN MAKANAN
    food_cur = db.execute('select id, name from food') #tampilkan id dari food
    food_results = food_cur.fetchall()  

    #STEP 5 : TAMPILKAN MAKANAN YANG DI ADD
    log_cur = db.execute('select food.name, food.protein, food.carbohydrates, food.fat, food.calories from log_date join food_date on food_date.log_date_id = log_date.id join food on food.id = food_date.food_id where log_date.entry_date = ?',[date])
    log_results = log_cur.fetchall()

    #STEP 6 : PENJUMLAHAN NUTRISI DI PYTHON
    #Bikin Dictionary biar gampang, karena data yang ditarik dari query itu juga sebenarnya Dictionary
    #Misal : log_results = db.execute('select food.name, food.protein, dst).fetchall()
    #Dalam artian lain log_results di dalamnya adalah food['name'] ; food ['protein] dst
    #Cara Insert nilai ke dalam dictionary di Python adalah nama_dict['key'] = 'valuenya' , kalo udah ada dia add kalo belum bikin key baru
    totals = {}
    totals['protein'] = 0
    totals['carbohydrates'] = 0
    totals['fat'] = 0
    totals['calories'] = 0

    for i in log_results: #enaknya sih namanya pake for food in log_results 
        totals['protein'] += i['protein']
        totals['carbohydrates'] += i['carbohydrates']
        totals['fat'] += i['fat']
        totals['calories'] += i['calories']

    #return '<h1> test {} </h1>'.format(result['entry_date']). Buat ngetest dulu fetchnya bisa jalan apa nggak sebelum otak atik html dll 
    return render_template('day.html', entry_date=date_result['entry_date'], pretty_date=pretty_date, food_results=food_results, log_results=log_results, totals=totals)

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