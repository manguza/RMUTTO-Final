from logging import NOTSET
from os import read
from sqlite3.dbapi2 import Row
from typing import List
import chatterbot, sqlite3 as sql, yaml, pprint
from flask import Flask, render_template, request, redirect, url_for, flash, session, escape
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot import filters
from chatterbot.comparisons import levenshtein_distance
from chatterbot.response_selection import get_first_response
from pythainlp import word_tokenize, sent_tokenize

app = Flask(__name__)
app.secret_key = 'random string'

bot = ChatBot("MyBot",
    filters=[filters.get_recent_repeated_responses],
    response_selection_method = get_first_response,
    statement_comparison_function = levenshtein_distance,
    logic_adapters=[
    {
        'import_path':'chatterbot.logic.BestMatch',
        'statement_comparison_function': levenshtein_distance,
        'response_selection_method' : get_first_response,
        'default_response': 'ขออภัยในความไม่สะดวก หากผู้ใช้งานพิมพ์ข้อมูลผิดกรุณาพิมพ์ใหม่ หรือระบบไม่มีข้อมูลในฐานข้อมูล',
        'maximum_similarity_threshold': 0.90
    }],read_only = True)
    
trainer = ChatterBotCorpusTrainer(bot)

# trainer.train("trainBot/greeting.yml")
# trainer.train("trainBot/start.yml")
# trainer.train("trainBot/end.yml")
# trainer.train("trainBot/information.yml")
# trainer.train("trainBot/form1.yml")
# trainer.train("trainBot/form2.yml")
# trainer.train("trainBot/form3.yml")
# trainer.train("trainBot/form4.yml")
# trainer.train("trainBot/form5.yml")
# trainer.train("trainBot/form7.yml")
# trainer.train("trainBot/form8.yml")
# trainer.train("trainBot/form9.yml")
# trainer.train("trainBot/form10.yml")
# trainer.train("trainBot/form11.yml")
# trainer.train("trainBot/form12.yml")
# trainer.train("trainBot/form13.yml")
# trainer.train("trainBot/form14.yml")
# trainer.train("trainBot/form15.yml")
# trainer.train("trainBot/form16.yml")
# trainer.train("trainBot/form17.yml")
# trainer.train("trainBot/form18.yml")
# trainer.train("trainBot/form19.yml")
# trainer.train("trainBot/form20.yml")
# trainer.train("trainBot/form21.yml")
# trainer.train("trainBot/addform.yml")


#----------------------------------- ChatBot -----------------------------------#

@app.route('/') 
def index():
    con = sql.connect("db.sqlite3")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT text FROM statement where id%2 != 0 group by id order by id DESC limit 5")
    rows = cur.fetchall()
    cur.execute("select text from statement where text like 'เครื่องแต่งกาย แบบปกติ<br>%'")
    rows2 = cur.fetchall()
    
    # for row in rows2:
    #     print(row['text'])
        
    return render_template("index.html", row=rows, row2=rows2)
    
@app.route('/get')
def get_bot_response():
    userText = request.args.get('msg')
    word_tokenize(userText)
    print(word_tokenize(userText))
    return str(bot.get_response(userText))

# @app.route('/get', methods=['GET','POST']) 
# def indexget():
    

#--------------------------------------------------------------------------------#

#---------------------------------- Login ---------------------------------------#
@app.route('/login')
def loginform():
    return redirect(url_for('index'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    username ='admin'
    password = 'admin'
    user_login = request.form.get('username')
    pass_login = request.form.get('password')
    if user_login == username and pass_login == password:
        session['logged_in'] = True
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('logout'))

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))
    else:
        con = sql.connect("db.sqlite3")

        curlist = con.cursor()
        curlist.execute("select * from statement")

        curtag = con.cursor()
        curtag.execute("select * from tag")


        rowslist = len(curlist.fetchall())
        rowstag = len(curtag.fetchall())
        return render_template('./admin/admin.html', rowslist = rowslist, rowstag = rowstag)
#--------------------------------------------------------------------------------#

#-------------------------------- Admin Page ------------------------------------#
@app.route('/list')
def list():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))
    else:
        con = sql.connect("db.sqlite3")
        con.row_factory = sql.Row

        cur = con.cursor()
        cur.execute("select id, text, search_text, in_response_to, search_in_response_to from statement")

        rows = cur.fetchall()
        return render_template('./admin/list.html', rows = rows)

# ---------------------------------- SQL Func ------------------------------------- #
@app.route('/deleteData', methods=['POST'])
def deleteData():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))
    else:
        con = sql.connect("db.sqlite3")

        cur = con.cursor()
        cur.execute("delete from statement where id=?",[request.form['deleteListData']])

        con.commit()
        return redirect(url_for('list'))

@app.route('/editdata', methods = ['GET','POST'])
def editdata():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))
    else:
        if request.method == 'POST':
            try:
                editID = request.form['Eid']
                editText = request.form['Etext']
                editHyperlink = request.form['Ehyperlink']
                editStext = request.form['Estext']
                editIrt = request.form['Eirt']
                editSirt = request.form['Esirt']

                with sql.connect("db.sqlite3") as con:
                    cur = con.cursor()
                    if request.form.get('Ehyperlink'):
                        url = '<a href="{}">{}</a>'
                        cur.execute("update statement set text = ?, search_text = ?, in_response_to = ?, search_in_response_to = ? where id = ?", (url.format(editHyperlink, editText), editStext, editIrt, editSirt, editID))
                        con.commit()
                    else:
                        cur.execute("update statement set text = ?, search_text = ?, in_response_to = ?, search_in_response_to = ? where id = ?", (editText, editStext, editIrt, editSirt, editID))
                        con.commit()
                    
            except:
                con.rollback()
            
            finally:
                con.close()
                return redirect(url_for('list'))

@app.route('/addtext')
def addtextbot():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))
    else:
        return render_template('./admin/addtext.html')

@app.route('/getaddtext', methods = ['GET','POST'])
def getaddtext():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))
    else:
        if request.method == 'POST':
            try:
                hyperlink = request.form['hyperlink']
                text = request.form['text']
                setext = request.form['search_text']
                inresto = request.form['in_response_to']
                seinresto = request.form['search_in_response_to']

                with sql.connect("db.sqlite3") as con:
                    cur = con.cursor()
                    if request.form.get('hyperlink'):
                        url = '<a href="{}">{}</a>'
                        cur.execute("insert into statement (text, search_text, in_response_to, search_in_response_to) values (?,?,?,?)", (url.format(hyperlink, text), setext, inresto, seinresto))
                        con.commit()
                    else:
                        cur.execute("insert into statement (text, search_text, in_response_to, search_in_response_to) values (?,?,?,?)", (text, setext, inresto, seinresto))
                        con.commit()
                    msg = 'Record successfully added'

            except:
                con.rollback()
                msg = "error in insert operation"

            finally:
                con.close()
                return render_template("./admin/addtext.html", msg = msg)
#--------------------------------------------------------------------------------#

if __name__=="__main__":
    app.run(debug=False)