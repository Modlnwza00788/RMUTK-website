from flask import Flask, render_template, request ,session ,redirect ,url_for
from firebase import firebase
from flask_mail import Mail, Message
from flask_session import Session



from flaskthreads import AppContextThread
import os
from os import path
import pandas as pd
import datetime
import functools
#import requests_toolbelt
#import numpy as np
#from acebook_scraper import get_posts
import os.path


#firebase
config = {
  'apiKey': "AIzaSyAmr7xsOAdTu3Wp1MOjVhB_o6CnVMicJDI",
  'authDomain': "rmutk-web.firebaseapp.com",
  'databaseURL': "https://rmutk-web-default-rtdb.asia-southeast1.firebasedatabase.app",
  'projectId': "rmutk-web",
  'storageBucket': "rmutk-web.appspot.com",
  'messagingSenderId': "384359472483",
  'appId': "1:384359472483:web:8cd7a427dfe357f45a0756"
}

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'modfer13@gmail.com',
    "MAIL_PASSWORD": 'uuwotjazgrcfzvgo'
}

firebase = firebase(config)
db = firebase.database()
storage = firebase.storage()
app = Flask(__name__)
app.secret_key = 'marshiro'
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem' #ประเภทของการเก็บไฟล์session
app.config.update(mail_settings)
mail = Mail(app)
Session(app)

def getDateTime(): # year/month/day
    dt = datetime.datetime.now()
    formatedDate = '{}/{}/{}'.format(dt.day, dt.month, dt.year)
    date7 = datetime.timedelta(days=30)
    next7 = dt+date7
    formatedDate7 = '{}/{}/{}'.format(next7.day,next7.month,next7.year)
    formatedTime = '{:0>2}:{:0>2}:{:0>2}'.format(dt.hour, dt.minute, dt.second)
    return formatedDate,formatedTime,formatedDate7

def autoDelete():
    today,_,_ = getDateTime()
    allType = ['News','Event']
    for subType in allType:
        currentItem = db.child(subType).get().val()
        if not currentItem is None:
            for item in currentItem:
                if not currentItem[item]['date_del'] == '':
                    toCheckDate = datetime.datetime.strptime(currentItem[item]['date_del']+' 00:00:00','%d/%m/%Y %H:%M:%S')
                    if toCheckDate.date() <= datetime.datetime.today().date():
                        db.child(subType).child(item).remove()
                if not currentItem[item]['date_post'] == '':
                    toCheckDate = datetime.datetime.strptime(currentItem[item]['date_post'] + ' 00:00:00','%d/%m/%Y %H:%M:%S')
                    if toCheckDate.date() <= datetime.datetime.today().date():
                        db.child(subType).child(item).update({"isOn":"1"})


def sort(arr):
    n = len(arr)
    swapped = False
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            dateNow = datetime.datetime.strptime(arr[j]['date'] + ' ' + arr[j]['time'],'%d/%m/%Y %H:%M:%S')
            dateNext = datetime.datetime.strptime(arr[j+1]['date'] + ' ' + arr[j+1]['time'], '%d/%m/%Y %H:%M:%S')
            if dateNow < dateNext:
                swapped = True
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
        if not swapped:
            return

@app.route('/',methods={'GET','POST'}) #ล็อกอิน
def login():

    if not session.get('id') is None:#bug
        if session['status'] == 0:
            return render_template('index.html')
        elif session['status'] == 1:
            return render_template('./admin/index-admin.html')
    allUser = db.child('User').get().val()
    if allUser is None:
        return render_template('login.html',error="ไม่มีผู้ใช้นี้")
    else:
        if request.method == 'POST':
            id = request.form.get('id')
            password = request.form.get('pass')
            if id in allUser:
                user = allUser[id]
                if password == user['password']:
                    if user['status'] == 0:
                        session['id'] = id ##เก็บค่าsession
                        session['name'] = user['name']
                        session['prefix'] = user['prefix']
                        session['status'] = user['status']
                        session['email'] = user['email']
                        session['notify'] = user['notify']
                        session['branch'] = user['branch'] #เก็บค่าtokenตอนเข้า
                        session['isOn'] = user['isOn']
                        return redirect(url_for('index'))
                    elif user['status'] == 1:
                        session['id'] = id ##เก็บค่าsession
                        session['name'] = user['name']
                        session['prefix'] = user['prefix']
                        session['status'] = user['status']
                        session['email'] = user['email']
                        session['notify'] = user['notify']
                        session['branch'] = user['branch']
                        session['isOn'] = user['isOn']
                        return redirect(url_for('index_admin'))
                else:
                    return render_template('login.html', error='รหัสผ่าน ไม่ถูกต้อง')
            else:
                return render_template('login.html',error='ไม่พบผู้ใช้')

    session['id'] = None
    session['name'] = None
    session['prefix'] = None
    session['email'] = None
    session['status'] = None
    session['notify'] = None
    session['isOn'] = None
    return render_template('login.html')

@app.route('/password',methods={'GET','POST'}) #เปลี่ยนพาส
def password():
    if request.method == 'GET':
        return render_template('profile.html')
    elif request.method == 'POST':
        oldpass = request.form.get('oldpass')
        newpass = request.form.get('newpass')
        conpass = request.form.get('conpass')
        getid = session.get('id')
        allUser = db.child('User').get().val()
        user = allUser[getid]
        if oldpass == user['password']:
            db.child('User').child(session['id']).update({'password': newpass})
        return render_template('profile.html')


@app.route('/index.html')
def index():
    if session['id'] is None:
        return render_template('login.html')
    if session['status'] == 0:
        return render_template('index.html',img1=storage.child("index/n001").get_url(None),
                               img2=storage.child("index/n002").get_url(None),
                               img3=storage.child("index/n003").get_url(None),
                               url1=db.child('ImgeIndex').child('n001','url').get().val(),
                               url2=db.child('ImgeIndex').child('n002','url').get().val(),
                               url3=db.child('ImgeIndex').child('n003','url').get().val())
    elif session['status'] == 1:
        return redirect(url_for('index_admin'))


# ข่าวกิจกรรม
@app.route('/activity.html')
def activity():
    autoDelete()
    allEvent = db.child('Event').get().val()
    data = []
    if not allEvent is None:
        for i in allEvent:
            foundEvent = db.child('Event').child(i).get().val()
            if foundEvent['group'] != "@มหาวิทยาลัย":
                if "1" == str(foundEvent['isOn']):
                    if "0" != str(foundEvent['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    detail = foundEvent['detail'].split('\r\n')
                    img = storage.child("event/" + i).get_url(None)
                    dt = 'โพสเมื่อ ' + foundEvent['date'] + ' ' + foundEvent['time']
                    if foundEvent['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour = 0
                    if foundEvent['group'] == session['branch']:
                        isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundEvent['title'], 'detail': detail, 'owner': foundEvent['owner'],
                                'image': img, 'group': foundEvent['group'],
                                'isUr': isUr, 'length': len(detail), 'datetime': dt, 'date': foundEvent['date'],
                                'time': foundEvent['time'], 'isYour': isYour, 'type': type}
                    data.append(newsDict)
    else:
        newDict = {'id':'e000','title':'ยังไม่มีข่าวกิจกรรม','detail':''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == []:
        newDict = {'id': 'e00', 'title': 'ยังไม่มีข่าวกิจกรรม', 'detail': ''}
        data.append(newDict)
    return render_template('activity.html',data=data,by='',my_id=session['id'],my_group=session['branch'])

@app.route('/activity.html/utk2')
def activity_utk2():
    autoDelete()
    allEvent = db.child('Event').get().val()
    data = []
    if not allEvent is None:
        for i in allEvent:
            foundEvent = db.child('Event').child(i).get().val()
            if foundEvent['group'] == "@มหาวิทยาลัย":
                if "1" == str(foundEvent['isOn']):
                    if "0" != str(foundEvent['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    detail = foundEvent['detail'].split('\r\n')
                    img = storage.child("event/" + i).get_url(None)
                    dt = 'โพสเมื่อ ' + foundEvent['date'] + ' ' + foundEvent['time']
                    if foundEvent['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour = 0
                    if foundEvent['group'] == session['branch']:
                        isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundEvent['title'], 'detail': detail, 'owner': foundEvent['owner'],
                                'image': img, 'group': foundEvent['group'],
                                'isUr': isUr, 'length': len(detail), 'datetime': dt, 'date': foundEvent['date'],
                                'time': foundEvent['time'], 'isYour': isYour, 'type': type}
                    data.append(newsDict)
    else:
        newDict = {'id':'e000','title':'ยังไม่มีข่าวกิจกรรม','detail':''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == []:
        newDict = {'id': 'e00', 'title': 'ยังไม่มีข่าวกิจกรรม', 'detail': ''}
        data.append(newDict)
    return render_template('activity.html',data=data,by=session['id'])

#รายละเอียดข่าวกิจกรรม
@app.route('/activity-details.html/<string:id>')
def activity_details(id:str):
    foundEvent = db.child('Event').child(id).get().val()
    detail = foundEvent['detail'].split('\r\n')
    img = storage.child("event/" + id).get_url(None)
    data = {'title': foundEvent['title'], 'detail': detail, 'length': len(detail), 'image': img}
    return render_template('./admin/activity-details.html',data=data)

# หน้าหลักหระทู้
@app.route('/add-interact.html')
def add_interact():
    return render_template('add-interact.html')

# ข่าวประชาสัมพันธ์แอดมิน
@app.route('/publish-admin.html')
def publish_admin():
    autoDelete()
    allNews = db.child('News').get().val()
    data = []
    if not allNews is None:
        for i in allNews:
            foundNews = db.child('News').child(i).get().val()
            if foundNews['group'] == session['branch'] and foundNews['group'] != "@มหาวิทยาลัย" or session['id'] == 'admin':
                if "0" != str(foundNews['isOn']):
                    if "1" == str(foundNews['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    detail = foundNews['detail'].split('\r\n')
                    img = storage.child("news/" + i).get_url(None)
                    dt = 'โพสเมื่อ ' + foundNews['date'] + ' ' + foundNews['time']
                    if foundNews['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour = 0
                    if foundNews['group'] == session['branch']:
                         isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundNews['title'], 'detail': detail, 'owner': foundNews['owner'],
                                'image': img, 'group': foundNews['group'], 'isUr': isUr, 'length': len(detail),
                                'datetime': dt, 'date': foundNews['date'], 'time': foundNews['time'], 'isYour': isYour,'type': type}
                    data.append(newsDict)
    else:
        newDict = {'id': 'n000', 'title': 'ยังไม่มีข่าวคณะ', 'detail': ''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 'n000', 'title': 'ยังไม่มีข่าวคณะ', 'detail': ''}
        data.append(newDict)

    return render_template('./admin/publish-admin.html',data=data,by='',my_id=session['id'], my_group=session['branch'])

@app.route('/publish-admin.html/rmutk')
def publish_admin_custom():
    autoDelete()
    allNews = db.child('News').get().val()
    data = []
    if not allNews is None:
        for i in allNews:
            foundNews = db.child('News').child(i).get().val()
            if foundNews['group'] == "@มหาวิทยาลัย" or session['branch'] == 'admin':
                if "1" == str(foundNews['isOn']):
                    if "0" != str(foundNews['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    detail = foundNews['detail'].split('\r\n')
                    img = storage.child("news/" +i).get_url(None)
                    dt = 'โพสเมื่อ ' + foundNews['date'] + ' ' + foundNews['time']
                    if foundNews['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour =0
                    if foundNews['group'] == session['branch']:
                        isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundNews['title'], 'detail': detail, 'owner': foundNews['owner'],  'image':img,'group':foundNews['group'],
                                'isUr':isUr,'length': len(detail), 'datetime': dt,'date':foundNews['date'],'time':foundNews['time'],'isYour':isYour,'type':type}
                    data.append(newsDict)

    else:
        newDict = {'id':'n000','title':'ยังไม่มีข่าวมหาวิทยาลัย','detail':''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 'n000', 'title': 'ยังไม่มีข่าวมหาวิทยาลัย', 'detail': ''}
        data.append(newDict)
    return render_template('./admin/publish-admin.html',data=data,by=session['id'])

@app.route('/publish-admin.html/closed')
def publish_admin_closed():
    autoDelete()
    allNews = db.child('News').get().val()
    data = []
    if not allNews is None:
        for i in allNews:
            foundNews = db.child('News').child(i).get().val()
            if str(foundNews['isOn']) != "1":
                if foundNews['group'] == session['branch'] or session['id'] == "admin":
                    if "0" != str(foundNews['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    detail = foundNews['detail'].split('\r\n')
                    img = storage.child("news/" +i).get_url(None)
                    dt = 'โพสเมื่อ ' + foundNews['date'] + ' ' + foundNews['time']
                    if foundNews['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour =0
                    if foundNews['group'] == session['branch']:
                        isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundNews['title'], 'detail': detail, 'owner': foundNews['owner'],  'image':img,'group':foundNews['group'],
                                'isUr':isUr,'length': len(detail), 'datetime': dt,'date':foundNews['date'],'time':foundNews['time'],'isYour':isYour,'type':type}
                    data.append(newsDict)


    else:
        newDict = {'id':'n000','title':'ไม่มีข่าวปิดการใช้งาน','detail':''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 'n000', 'title': 'ไม่มีข่าวปิดการใช้งาน', 'detail': ''}
        data.append(newDict)
    print(data)
    return render_template('./admin/publish-admin.html',data=data,by=session['id'])

@app.route('/publish-admin.html/2')
def publish_admin_2():
    autoDelete()
    allNews = db.child('News').get().val()
    data = []
    if not allNews is None:
        for i in allNews:
            foundNews = db.child('News').child(i).get().val()
            if foundNews['group'] != "@มหาวิทยาลัย":
                if "0" != str(foundNews['isOn']):
                    if "1" == str(foundNews['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    detail = foundNews['detail'].split('\r\n')
                    img = storage.child("news/" + i).get_url(None)
                    dt = 'โพสเมื่อ ' + foundNews['date'] + ' ' + foundNews['time']
                    if foundNews['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour = 0
                    if foundNews['group'] == session['branch']:
                         isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundNews['title'], 'detail': detail, 'owner': foundNews['owner'],
                                'image': img, 'group': foundNews['group'], 'isUr': isUr, 'length': len(detail),
                                'datetime': dt, 'date': foundNews['date'], 'time': foundNews['time'], 'isYour': isYour,'type': type}
                    data.append(newsDict)
    else:
        newDict = {'id': 'n000', 'title': 'ยังไม่มีข่าวคณะ', 'detail': ''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 'n000', 'title': 'ยังไม่มีข่าวคณะ', 'detail': ''}
        data.append(newDict)

    return render_template('./admin/publish-admin.html',data=data,by='',my_id=session['id'], my_group=session['branch'])

@app.route('/publish-admin.html/rmutk2')
def publish_admin_custom2():
    autoDelete()
    allNews = db.child('News').get().val()
    data = []
    if not allNews is None:
        for i in allNews:
            foundNews = db.child('News').child(i).get().val()
            if foundNews['group'] == "@มหาวิทยาลัย" :
                if session['branch'] == 'admin':
                    if "1" == str(foundNews['isOn']):
                        if "0" != str(foundNews['isOn']):
                            type = 'โพส'
                        else:
                            type = 'ไม่โพส'

                        detail = foundNews['detail'].split('\r\n')
                        img = storage.child("news/" +i).get_url(None)
                        dt = 'โพสเมื่อ ' + foundNews['date'] + ' ' + foundNews['time']
                        if foundNews['owner'] == session['id']:
                            isYour = 1
                        else:
                            isYour =0
                        if foundNews['group'] == session['branch']:
                            isUr = 1
                        else:
                            isUr = 0
                        newsDict = {'id': i, 'title': foundNews['title'], 'detail': detail, 'owner': foundNews['owner'],  'image':img,'group':foundNews['group'],
                                    'isUr':isUr,'length': len(detail), 'datetime': dt,'date':foundNews['date'],'time':foundNews['time'],'isYour':isYour,'type':type}
                        data.append(newsDict)

    else:
        newDict = {'id':'n000','title':'ยังไม่มีข่าวมหาวิทยาลัย','detail':''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 'n000', 'title': 'ยังไม่มีข่าวมหาวิทยาลัย', 'detail': ''}
        data.append(newDict)
    return render_template('./admin/publish-admin.html',data=data,by=session['id'])

@app.route('/publish-admin.html/closed2')
def publish_admin_closed2():
    autoDelete()
    allNews = db.child('News').get().val()
    data = []
    if not allNews is None:
        for i in allNews:
            foundNews = db.child('News').child(i).get().val()
            if str(foundNews['isOn']) != "1":
                if foundNews['group'] == session['branch'] or session['id'] == "admin":
                    if "0" != str(foundNews['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    detail = foundNews['detail'].split('\r\n')
                    img = storage.child("news/" +i).get_url(None)
                    dt = 'โพสเมื่อ ' + foundNews['date'] + ' ' + foundNews['time']
                    if foundNews['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour =0
                    if foundNews['group'] == session['branch']:
                        isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundNews['title'], 'detail': detail, 'owner': foundNews['owner'],  'image':img,'group':foundNews['group'],
                                'isUr':isUr,'length': len(detail), 'datetime': dt,'date':foundNews['date'],'time':foundNews['time'],'isYour':isYour,'type':type}
                    data.append(newsDict)


    else:
        newDict = {'id':'n000','title':'ไม่มีข่าวปิดการใช้งาน','detail':''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 'n000', 'title': 'ไม่มีข่าวปิดการใช้งาน', 'detail': ''}
        data.append(newDict)
    return render_template('./admin/publish-admin.html',data=data,by=session['id'])



#หน้ารายละเอียดข่าวแอดมิน

@app.route('/publish-details-admin.html/<string:id>')
def publish_details_admin(id:str):
    foundNews = db.child('News').child(id).get().val()
    detail = foundNews['detail'].split('\r\n')
    img = storage.child("news/" + id).get_url(None)
    data = {'title': foundNews['title'], 'detail': detail, 'length': len(detail), 'image': img}
    return render_template('./admin/publish-details-admin.html',data=data)

#หน้าเพิ่มข่าวแอดมิน
@app.route('/add-publish-admin.html',methods=['GET','POST'])
def add_publish_admin():
    BDl = db.child('HostBranch').get().val()
    data = []
    for i in BDl:
        data.append(i)
    return render_template('./admin/add-publish-admin.html',data=data ,my_group=session['branch'], my_id=session['id'],min=getNextDay())



# หน้าติดต่อ
@app.route('/contact.html')
def contact():
    return render_template('contact.html')

# รายละเอียดกระทู้
@app.route('/interact_details.html/<string:id>')
def interact_details(id : str):
    thread = db.child('Thread').child(id).get().val()
    bword = db.child('BWord').get().val()
    replyList = []
    if 'Reply' in thread:
        allReply = thread['Reply']
        for i in allReply:
            sub_reply = thread['Reply'][i]
            detail = sub_reply['detail'].split('\r\n')
            img1 = storage.child("profile/" + sub_reply['owner']).get_url(None)
            storage.child("profile/" + sub_reply['owner']).download('Check.jpg')
            if not path.exists('Check.jpg'):
                img1 = storage.child("profile/profile.png").get_url(None)
            else:
                os.remove('Check.jpg')
            rep = {'owner':sub_reply['owner'],'date':sub_reply['date'],'time':sub_reply['time'],'email':sub_reply['email'],'name':sub_reply['name'],'detail':detail,'length':len(detail),'img1':img1}
            replyList.append(rep)
    sort(replyList)
    detail = functools.reduce(
        lambda a, b:
            a.replace(b["Keyword"], b["Replace"])
        , bword
        , thread['detail']
    )
    img2 = storage.child("thread/" + id).get_url(None)
    detail = detail.split('\r\n')
    allUser = db.child('User').get().val()
    if not allUser is None:
        user = allUser[thread['owner']]
    else:
        user = {'name':'n/a' , 'email':'n/a'}
    title = functools.reduce(
        lambda a, b:
        a.replace(b["Keyword"], b["Replace"])
        , bword
        , thread['title']
    )
    data = {'id': id, 'title': title, 'detail': detail, 'owner': thread['owner'],'length': len(detail),'name':user['name'],'email':user['email'],'date':thread['date'],'time':thread['time'],'img2':img2}
    return render_template('interact_details.html',data=data,reply=replyList)

# กระทู้
@app.route('/interact.html')
def interact():
    allThread = db.child('Thread').get().val()
    bword = db.child('BWord').get().val()
    data = []
    if not allThread is None:
        for i in allThread:
            foundThread = db.child('Thread').child(i).get().val()
            detail = functools.reduce(
                lambda a, b:
                a.replace(b["Keyword"], b["Replace"])
                , bword
                , foundThread['detail']
            )
            detail = detail.split('\r\n')
            img = storage.child("tread/" +i).get_url(None)
            title = functools.reduce(
                lambda a, b:
                a.replace(b["Keyword"], b["Replace"])
                , bword
                , foundThread['title']
            )
            dt = 'สร้างเมื่อ '+foundThread['date'] + ' ' + foundThread['time']
            if foundThread['owner'] == session['id']:
                isYour = 1
            else:
                isYour = 0
            newsDict = {'id': i, 'title': title, 'detail': detail,'owner':foundThread['owner'],'length': len(detail),'image':img, 'datetime':dt,
                        'date':foundThread['date'],'time':foundThread['time'],'isYour':isYour}
            data.append(newsDict)
    else:
        newDict = {'id': 't000', 'title': 'ยังไม่มีกระทู้', 'detail': ''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 't000', 'title': 'ยังไม่มีกระทู้', 'detail': ''}
        data.append(newDict)
    return render_template('interact.html', data=data,by='',my_id=session['id'],length=len(data))

@app.route('/interact.html/<string:id>')
def interact_custom(id:str):
    allThread = db.child('Thread').get().val()
    bword =db.child('BWord').get().val()
    data = []
    if not allThread is None:
        for i in allThread:
            foundThread = db.child('Thread').child(i).get().val()
            if id == foundThread['owner']:
                detail = foundThread['detail'].split('\r\n')
                img = storage.child("thread/" + i).get_url(None)
                if foundThread['owner'] == session['id']:
                    isYour = 1
                else:
                    isYour = 0
                dt = 'สร้างเมื่อ ' + foundThread['date'] + ' ' + foundThread['time']
                title = functools.reduce(
                    lambda a, b:
                    a.replace(b["Keyword"], b["Replace"])
                    , bword
                    , foundThread['title']
                )
                newsDict = {'id': i, 'title': title, 'detail': detail,'owner':foundThread['owner'],'length': len(detail),'image':img,
                            'datetime':dt,'date':foundThread['date'],'time':foundThread['time'],'isYour':isYour}
                data.append(newsDict)
    else:
        newDict = {'id': 't000', 'title': 'ยังไม่มีกระทู้', 'detail': ''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 't000', 'title': 'ยังไม่มีกระทู้', 'detail': ''}
        data.append(newDict)
    return render_template('interact.html', data=data,by=session['name'])

@app.route('/add_reply',methods=['POST'])
def add_reply():
    if request.method == 'POST':
        tid = request.form.get('id')
        date,time,_ = getDateTime()
        rid = autogen(tid)
        # db.child('Thread').child(tid).child('Reply').push({'owner':session['id'],'name':session['name'],'group':session['branch'],
        #                                                    'email':session['email'],'detail':request.form.get('detail'),'date':date,'time':time})

        newReply = {'owner': session['id'], 'name': session['name'], 'group': session['branch'],'email': session['email'], 'detail': request.form.get('detail'), 'date': date, 'time': time}
        db.child('Thread').child(tid).child("Reply").child("r"+rid).set(newReply)

        return redirect(url_for('interact_details',id=tid))

# ข้อมูลผู้ใช้
@app.route('/profile.html')
def profile():
    if session['id'] is None:
        return render_template('login.html')
    img = storage.child("profile/"+session['id']).get_url(None)
    user = db.child('User').child(session['id']).get().val()
    if session['status'] == 0:
        status = 'นักศึกษา'
    else:
        status = 'ผู้ดูแล'
    data = {'img':img,'id':session['id'],'name':session['name'],'status':status,'email':session['email'],'notify':user['notify'],'branch':user['branch']}
    return render_template('profile.html',data=data)


@app.route('/edit_profile',methods=['POST'])
def edit_profile():
    if request.method == 'POST':
        if request.form.get('notify') is None:
            notify = '0'
        else:
            notify = '1'
        db.child('User').child(session['id']).update({'notify':notify})
        return redirect(url_for('profile'))

@app.route('/edit-img-admin.html')
def edit_img_admin():
    index = db.child('ImgeIndex').get().val()
    coust = 1
    data = []
    if not index is None:
        for i in index:
            url = db.child('ImgeIndex').child(i,'url').get().val()
            img = storage.child("index/" + i).get_url(None)
            newsDict = {'id': i ,'img': img,'url':url,'coust':coust}
            data.append(newsDict)
            coust += 1
    else:
        newDict = {'id':'n000'}
        data.append(newDict)
    return render_template('./admin/edit-img-admin.html',data=data)

@app.route('/img-index.html/<string:id>')
def img_index(id:str):
    img = storage.child("index/" + id).get_url(None)
    url = db.child('ImgeIndex').child(id).get().val()
    return render_template('img-index.html',image=img,id=id,data=url)

@app.route('/img_in', methods = ['POST'])
def img_in():
    if request.method == 'POST':
        id = str(request.form.get('id'))
        imgindex = {'url':request.form.get('url')}
        db.child('ImgeIndex').child(request.form.get('id')).set(imgindex)
        file = request.files['file']
        if not file.filename == "":
            file.save('temp_profile.jpg')
            storage.child('index').child(id).put('temp_profile.jpg')
            os.remove('temp_profile.jpg')
        return redirect(url_for('edit_img_admin'))


# ข่าวประชาสัมพันธ์
@app.route('/publish.html')
def publish():
    autoDelete()
    allNews = db.child('News').get().val()
    date, time, _ = getDateTime()
    today = datetime.datetime.today()
    NewsNew = []
    data = []
    if not allNews is None:
        for i in allNews:
            foundNews = db.child('News').child(i).get().val()
            if foundNews['group'] != "@มหาวิทยาลัย":
                if "1" == str(foundNews['isOn']):
                    if "0" != str(foundNews['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    dw = datetime.datetime.strptime(foundNews['date'],"%d/%m/%Y")
                    dwa = today - datetime.datetime(dw.year,dw.month,dw.day)
                    if dwa.days <= 7 :
                        NewsNew = "New"
                    else:
                        NewsNew = ""
                    detail = foundNews['detail'].split('\r\n')
                    img = storage.child("news/" + i).get_url(None)
                    dt = 'โพสเมื่อ ' + foundNews['date'] + ' ' + foundNews['time']
                    if foundNews['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour = 0
                    if foundNews['group'] == session['branch']:
                        isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundNews['title'], 'detail': detail, 'owner': foundNews['owner'],
                                'image': img, 'group': foundNews['group'],'isUr': isUr, 'length': len(detail), 'datetime': dt, 'date': foundNews['date'],
                                'time': foundNews['time'], 'isYour': isYour, 'type': type,'NewsNew':NewsNew}
                    data.append(newsDict)
    else:
        newDict = {'id':'n000','title':'ยังไม่มีข่าวประชาสัมพันธ์','detail':''}
        data.append(newDict)
    if len(data) > 0:
        sort(data)
    if data == [] :
        newDict = {'id': 'n000', 'title': 'ยังไม่มีข่าวประชาสัมพันธ์', 'detail': ''}
        data.append(newDict)
    return render_template('publish.html',data=data,by='',my_id=session['id'], my_group=session['branch'])

@app.route('/publish.html/utk')
def publish_custom_utk():
    autoDelete()
    allNews = db.child('News').get().val()
    data = []
    if not allNews is None:
        for i in allNews:
            foundNews = db.child('News').child(i).get().val()
            if foundNews['group'] == "@มหาวิทยาลัย":
                if "1" == str(foundNews['isOn']):
                    if "0" != str(foundNews['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    detail = foundNews['detail'].split('\r\n')
                    img = storage.child("news/" + i).get_url(None)
                    dt = 'โพสเมื่อ ' + foundNews['date'] + ' ' + foundNews['time']
                    if foundNews['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour = 0
                    if foundNews['group'] == session['branch']:
                        isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundNews['title'], 'detail': detail, 'owner': foundNews['owner'],
                                'image': img, 'group': foundNews['group'],
                                'isUr': isUr, 'length': len(detail), 'datetime': dt, 'date': foundNews['date'],
                                'time': foundNews['time'], 'isYour': isYour, 'type': type}
                    data.append(newsDict)
    else:
        newDict = {'id':'n000','title':'ยังไม่มีข่าวประชาสัมพันธ์','detail':''}
        data.append(newDict)
    if len(data) > 0:
        sort(data)
    if data == [] :
        newDict = {'id': 'n000', 'title': 'ยังไม่มีข่าวประชาสัมพันธ์', 'detail': ''}
        data.append(newDict)
    return render_template('publish.html',data=data,by=session['id'])

#รายละเอียดข่าว
@app.route('/publish-detail.html/<string:id>')
def publish_detail(id:str):
    foundNews = db.child('News').child(id).get().val()
    detail = foundNews['detail'].split('\r\n')
    img = storage.child("news/" + id).get_url(None)
    data = {'title': foundNews['title'], 'detail': detail, 'length': len(detail), 'image': img}

    return render_template('publish-detail.html',data=data)

# ส่วนการค้นหา
@app.route('/search.html')
def search():
    return render_template('search.html')

# ====================================== ADMIN ================================================================
# ส่วนของ admin
@app.route('/index-admin.html')
def index_admin():
    Cnum = 0
    index = db.child('ImgeIndex').get().val()
    data = []
    if not index is None:
        for i in index:
            img = storage.child("index/" + i).get_url(None)
            Cnum = Cnum +1

            newsDict = {'id': i, 'img': img , 'coust':Cnum}
            data.append(newsDict)
    else:
        newDict = {'id': 'n000'}
        data.append(newDict)
    return render_template('./admin/index-admin.html' ,data=data,img1=storage.child("index/n001").get_url(None),
                           img2=storage.child("index/n002").get_url(None),img3=storage.child("index/n003").get_url(None),
                           url1=db.child('ImgeIndex').child('n001','url').get().val(),url2=db.child('ImgeIndex').child('n002','url').get().val(),
                           url3=db.child('ImgeIndex').child('n003','url').get().val(),my_group=session['branch'],my_id=session['id'])


# ข่าวกิจกรรม
@app.route('/activity-admin.html')
def activity_admin():
    autoDelete()
    allEvent = db.child('Event').get().val()
    data = []
    if not allEvent is None:
        for i in allEvent:
            foundEvent = db.child('Event').child(i).get().val()
            if foundEvent['group'] == session['branch'] and foundEvent['group'] != "@มหาวิทยาลัย" or session[
                'id'] == 'admin':
                if "0" != str(foundEvent['isOn']):
                    if "1" == str(foundEvent['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    detail = foundEvent['detail'].split('\r\n')
                    img = storage.child("event/" + i).get_url(None)
                    date = 'สร้างเมื่อ ' + foundEvent['date']
                    time = 'เวลา' + foundEvent['time']
                    if foundEvent['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour = 0
                    if foundEvent['group'] == session['branch']:
                        isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundEvent['title'], 'detail': detail,'length':len(detail),'owner':foundEvent['owner'], 'group':foundEvent['group'],
                                'isUr':isUr,'isYour':isYour ,'date' : date ,'time':time, 'image':img,'date':foundEvent['date'],'time':foundEvent['time'],'type':type}
                    data.append(newsDict)
    else:
        newDict = {'id':'e000','title':'ยังไม่มีข่าวกิจกรรม','detail':''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 'e000', 'title': 'ยังไม่มีข่าวกิจกรรม', 'detail': '','group':''}
        data.append(newDict)
    return render_template('./admin/activity-admin.html',data=data,by='',my_id=session['id'], my_group=session['branch'])

@app.route('/activity-admin.html/rmutk')
def activity_admin_custom():
    autoDelete()
    allEvent = db.child('Event').get().val()
    data = []
    if not allEvent is None:
        for i in allEvent:
            foundEvent = db.child('Event').child(i).get().val()
            if foundEvent['group'] == "@มหาวิทยาลัย" or session['branch'] == 'admin':
                if "1" == str(foundEvent['isOn']):
                    if "0" != str(foundEvent['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    detail = foundEvent['detail'].split('\r\n')
                    img = storage.child("event/" + i).get_url(None)
                    date = 'สร้างเมื่อ ' + foundEvent['date']
                    time = 'เวลา' + foundEvent['time']
                    if foundEvent['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour = 0
                    if foundEvent['group'] == session['branch']:
                        isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundEvent['title'], 'detail': detail,'length':len(detail),'owner':foundEvent['owner'], 'group':foundEvent['group'],'isUr':isUr,
                                'isYour':isYour ,'date' : date ,'time':time, 'image':img,'date':foundEvent['date'],'time':foundEvent['time'],'type':type}
                    data.append(newsDict)
    else:
        newDict = {'id':'e000','title':'ยังไม่มีข่าวกิจกรรม','detail':''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 'e000', 'title': 'ยังไม่มีข่าวกิจกรรม', 'detail': '','group':''}
        data.append(newDict)
    return render_template('./admin/activity-admin.html',data=data,by=session['id'])

@app.route('/activity-admin.html/2')
def activity_admin_2():
    autoDelete()
    allEvent = db.child('Event').get().val()
    data = []
    if not allEvent is None:
        for i in allEvent:
            foundEvent = db.child('Event').child(i).get().val()
            if foundEvent['group'] != "@มหาวิทยาลัย":
                if "0" != str(foundEvent['isOn']):
                    if "1" == str(foundEvent['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    detail = foundEvent['detail'].split('\r\n')
                    img = storage.child("event/" + i).get_url(None)
                    dt = 'โพสเมื่อ ' + foundEvent['date'] + ' ' + foundEvent['time']
                    if foundEvent['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour = 0
                    if foundEvent['group'] == session['branch']:
                         isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundEvent['title'], 'detail': detail, 'owner': foundEvent['owner'],
                                'image': img, 'group': foundEvent['group'], 'isUr': isUr, 'length': len(detail),
                                'datetime': dt, 'date': foundEvent['date'], 'time': foundEvent['time'], 'isYour': isYour,'type': type}
                    data.append(newsDict)
    else:
        newDict = {'id': 'e000', 'title': 'ยังไม่มีข่าวคณะ', 'detail': ''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 'e000', 'title': 'ยังไม่มีข่าวคณะ', 'detail': ''}
        data.append(newDict)

    return render_template('./admin/activity-admin.html',data=data,by='',my_id=session['id'], my_group=session['branch'])

@app.route('/activity-admin.html/rmutk2')
def activity_admin_custom2():
    autoDelete()
    allEvent = db.child('Event').get().val()
    data = []
    if not allEvent is None:
        for i in allEvent:
            foundEvent = db.child('Event').child(i).get().val()
            if foundEvent['group'] == "@มหาวิทยาลัย":
                if "1" == str(foundEvent['isOn']):
                    if "0" != str(foundEvent['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    detail = foundEvent['detail'].split('\r\n')
                    img = storage.child("event/" +i).get_url(None)
                    dt = 'โพสเมื่อ ' + foundEvent['date'] + ' ' + foundEvent['time']
                    if foundEvent['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour =0
                    if foundEvent['group'] == session['branch']:
                        isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundEvent['title'], 'detail': detail, 'owner': foundEvent['owner'],  'image':img,'group':foundEvent['group'],
                                'isUr':isUr,'length': len(detail), 'datetime': dt,'date':foundEvent['date'],'time':foundEvent['time'],'isYour':isYour,'type':type}
                    data.append(newsDict)

    else:
        newDict = {'id':'e000','title':'ยังไม่มีข่าวมหาวิทยาลัย','detail':''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 'e000', 'title': 'ยังไม่มีข่าวมหาวิทยาลัย', 'detail': ''}
        data.append(newDict)
    return render_template('./admin/activity-admin.html',data=data,by=session['id'],my_group=session['branch'])

@app.route('/activity-admin.html/closed')
def activity_admin_closed():
    autoDelete()
    allEvent = db.child('Event').get().val()
    data = []
    if not allEvent is None:
        for i in allEvent:
            foundEvent = db.child('Event').child(i).get().val()
            if str(foundEvent['isOn']) != "1":
                if foundEvent['group'] == session['branch'] or session['id'] == "admin":
                    if "0" != str(foundEvent['isOn']):
                        type = 'โพส'
                    else:
                        type = 'ไม่โพส'
                    detail = foundEvent['detail'].split('\r\n')
                    img = storage.child("event/" + i).get_url(None)
                    dt = 'โพสเมื่อ ' + foundEvent['date'] + ' ' + foundEvent['time']
                    if foundEvent['owner'] == session['id']:
                        isYour = 1
                    else:
                        isYour = 0
                    if foundEvent['group'] == session['branch']:
                        isUr = 1
                    else:
                        isUr = 0
                    newsDict = {'id': i, 'title': foundEvent['title'], 'detail': detail, 'owner': foundEvent['owner'],
                                'image': img, 'group': foundEvent['group'],
                                'isUr': isUr, 'length': len(detail), 'datetime': dt, 'date': foundEvent['date'],
                                'time': foundEvent['time'], 'isYour': isYour, 'type': type}
                    data.append(newsDict)
    else:
        newDict = {'id': 'e000', 'title': 'ไม่มีข่าวปิดการใช้งาน', 'detail': ''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == []:
        newDict = {'id': 'e000', 'title': 'ไม่มีข่าวปิดการใช้งาน', 'detail': ''}
        data.append(newDict)
    print(data)
    return render_template('./admin/activity-admin.html', data=data, by=session['id'])

#รายละเอียดข่าวกิจกรรมแอดมิน
@app.route('/activity-details-admin.html/<string:id>')
def activity_details_admin(id:str):

    foundEvent = db.child('Event').child(id).get().val()
    detail = foundEvent['detail'].split('\r\n')
    img = storage.child("event/" + id).get_url(None)
    data = {'title': foundEvent['title'], 'detail': detail, 'length': len(detail), 'image': img}

    return render_template('./admin/activity-details-admin.html',data=data)

# เพิ่มข่าวกิจกรรม
@app.route('/add-activity-admin.html')
def add_activity_admin():
    BDl = db.child('HostBranch').get().val()
    data = []
    for i in BDl:
        data.append(i)
    return render_template('./admin/add-activity-admin.html',data=data,my_group=session['branch'],my_id=session['id'],min=getNextDay())
# เพิ่มกระทู้

@app.route('/add-interact-admin.html')
def add_interact_admin():
    return render_template('./admin/add-interact-admin.html')

@app.route('/edit-interact-admin.html/<string:id>')
def edit_interact_admin(id:str):
    data = db.child('Thread').child(id).get().val()
    BDl = db.child('HostBranch').get().val()
    img = storage.child("thread/" + id).get_url(None)
    DBranch = []
    for i in BDl:
        DBranch.append(i)
    print(data)
    return render_template('./admin/edit-interact-admin.html',data=data,id=id,my_group=session['branch'],my_id=session['id'],DBranch=DBranch,img=img)

#วันเดือนปี
def getNextDay(): # year/month/day
    dt = datetime.datetime.now()
    nextDay = datetime.timedelta(days=1)
    next = dt+nextDay
    formatedDate = '{}-{:0>2}-{:0>2}'.format(next.year,next.month,next.day)
    return formatedDate

# เพิ่มผู้ใช้
@app.route('/add-user-admin.html',methods=['GET','POST'])
def add_user_admin():
    BDl = db.child('HostBranch').get().val()
    data = []
    for i in BDl:
        data.append(i)
    return render_template('./admin/add-user-admin.html',data=data,my_group=session['branch'], my_id=session['id'])

# รายละเอียดกระทู็
@app.route('/interact_details_admin.html')
def interact_details_admin():
    return render_template('./admin/interact_details_admin.html')

#หน้ากระทู้หน้าหลัก
@app.route('/interact-admin.html')
def interact_admin():
    allThread = db.child('Thread').get().val()
    bword = db.child('BWord').get().val()
    data = []
    if not allThread is None:
        for i in allThread:
            foundThread = db.child('Thread').child(i).get().val()
            detail = functools.reduce(
                lambda a, b:
                    a.replace(b["Keyword"], b["Replace"])
                , bword
                , foundThread['detail']
            )
            detail = detail.split('\r\n')
            img = storage.child("thread/" +i).get_url(None)
            title = functools.reduce(
                lambda a, b:
                a.replace(b["Keyword"], b["Replace"])
                , bword
                , foundThread['title']
            )
            dt = 'สร้างเมื่อ ' + foundThread['date'] + ' ' + foundThread['time']
            if foundThread['owner'] == session['id']:
                isYour = 1
            else:
                isYour =0
            newsDict = {'id': i, 'title': title, 'detail': detail, 'owner': foundThread['owner'],'length': len(detail),'image':img, 'datetime': dt,
                        'date':foundThread['date'],'time':foundThread['time'],'isYour':isYour}
            data.append(newsDict)
    else:
        newDict = {'id': 't000', 'title': 'ยังไม่มีกระทู้', 'detail': ''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 't000', 'title': 'ยังไม่มีกระทู้', 'detail': ''}
        data.append(newDict)
    return render_template('./admin/interact-admin.html', data=data, by='', length=len(data), my_id=session['id'])

#หน้าแสดงข้อมูลเฉพาะ
@app.route('/interact-admin.html/<string:id>')
def interact_admin_custom(id:str):
    allThread = db.child('Thread').get().val()
    bword = db.child('BWord').get().val()
    data = []
    if not allThread is None:
        for i in allThread:
            foundThread = db.child('Thread').child(i).get().val()
            if id == foundThread['owner']:
                detail = foundThread['detail'].split('\r\n')
                img = storage.child("thread/" + i).get_url(None)
                if foundThread['owner'] == session['id']:
                    isYour = 1
                else:
                    isYour = 0
                dt = 'สร้างเมื่อ ' + foundThread['date'] + ' ' + foundThread['time']
                title = functools.reduce(
                    lambda a, b:
                    a.replace(b["Keyword"], b["Replace"])
                    , bword
                    , foundThread['title']
                )
                newsDict = {'id': i, 'title': title, 'detail': detail,'owner':foundThread['owner'],'length': len(detail),'image':img,
                            'datetime':dt,'date':foundThread['date'],'time':foundThread['time'],'isYour':isYour}
                data.append(newsDict)
    else:
        newDict = {'id': 't000', 'title': 'ยังไม่มีกระทู้', 'detail': ''}
        data.append(newDict)
    if len(data) > 1:
        sort(data)
    if data == [] :
        newDict = {'id': 't000', 'title': 'ยังไม่มีกระทู้', 'detail': ''}
        data.append(newDict)
    return render_template('./admin/interact-admin.html', data=data,by=session['name'])

@app.route('/edit-activity-admin.html/<string:id>')
def edit_activity_admin(id:str):
    data = db.child('Event').child(id).get().val()
    BDl = db.child('HostBranch').get().val()
    if data['date_del'] == '':
        date = ''
    else:
        date = datetime.datetime.strptime(data['date_del'] + ' 00:00:00', '%d/%m/%Y %H:%M:%S')
        date = str(date)[0:10]
    if data['date_post'] == '':
        post = ''
    else:
        post = datetime.datetime.strptime(data['date_post'] + ' 00:00:00', '%d/%m/%Y %H:%M:%S')
        post = str(post)[0:10]
    DBranch = []
    for i in BDl:
        DBranch.append(i)
    return render_template('./admin/edit-activity-admin.html',data=data,id=id,min=getNextDay(),date=str(date)[0:10],post=str(post)[0:10],my_group=session['branch'],DBranch=DBranch, my_id=session['id'])

@app.route('/edit-publish-admin.html/<string:id>')
def edit_publish_admin(id:str):
    data = db.child('News').child(id).get().val()
    BDl = db.child('HostBranch').get().val()
    if data['date_del'] == '':
        date = ''
    else:
        date = datetime.datetime.strptime(data['date_del'] + ' 00:00:00', '%d/%m/%Y %H:%M:%S')
        date = str(date)[0:10]
    if data['date_post'] == '':
        post = ''
    else:
        post = datetime.datetime.strptime(data['date_post'] + ' 00:00:00', '%d/%m/%Y %H:%M:%S')
        post = str(post)[0:10]
    DBranch = []
    for i in BDl:
        DBranch.append(i)
    return render_template('./admin/edit-publish-admin.html',data=data,id=id,min=getNextDay(),date=str(date)[0:10], post=str(post)[0:10],my_group=session['branch'],DBranch=DBranch, my_id=session['id'])

@app.route('/edit-user-admin.html/<string:id>')
def edit_user_admin(id:str):
    data = db.child('User').child(id).get().val()
    img = storage.child("profile/" + id).get_url(None)
    user = db.child('User').child(session['id']).get().val()
    BDl = db.child('HostBranch').get().val()
    if session['status'] == 0:
        status = 'นักศึกษา'
    else:
        status = 'ผู้ดูแล'
    datatoken = {'img': img, 'id': session['id'],'prefix':user['prefix'], 'name': session['name'] ,'status': status, 'email': session['email'],'notify': user['notify'], 'branch': user['branch']}
    DBranch = []
    for i in BDl:
        DBranch.append(i)
    return render_template('./admin/edit-user-admin.html',data=data,id=id,image=img,DBranch=DBranch,datatoken=datatoken,my_group=session['branch'],my_id=session['id'])

@app.route('/publish_search', methods = ['POST'])
def publish_search():
    if request.method == 'POST':
        word = request.form.get('search_txt')
        allNews = db.child('News').get().val()
        data = []
        if not allNews is None:
            for i in allNews:
                foundNews = db.child('News').child(i).get().val()
                if foundNews['group'] != "@มหาวิทยาลัย":
                    if "0" != str(foundNews['isOn']):
                        isOn = "โพส"
                    else:
                        isOn = "ไม่โพส"
                detail = foundNews['detail'].split('\r\n')
                img = storage.child("news/" + i).get_url(None)
                dt = 'สร้างเมื่อ ' + foundNews['date'] + ' ' + foundNews['time']
                if foundNews['owner'] == session['id']:
                    isYour =1
                else:
                    isYour =0
                if foundNews['group'] == session['branch']:
                    isUr =1
                else:
                    isUr =0
                newsDict = {'id': i, 'title': foundNews['title'], 'detail': detail, 'owner': foundNews['owner'],
                            'image': img, 'group': foundNews['group'], 'isUr': isUr, 'length': len(detail),
                            'datetime': dt, 'date': foundNews['date'], 'time': foundNews['time'], 'isYour': isYour,'isOn':isOn}
                if newsDict['title'].find(word) >= 0 or foundNews['detail'].find(word) >= 0 :
                    data.append(newsDict)
        else:
            newDict = {'id': 'n000', 'title': 'ยังไม่มีข่าวประชาสัมพันธ์', 'detail': ''}
            data.append(newDict)
        if len(data) > 1:
            sort(data)
        if session['status'] == 0:
            return render_template('publish.html', data=data, length=len(data),my_group=session['branch'],my_id=session['id'])
        elif session['status'] == 1:
            return render_template('./admin/publish-admin.html', data=data, length=len(data),my_group=session['branch'],my_id=session['id'])

@app.route('/activity_search', methods = ['POST'])
def activity_search():
    if request.method == 'POST':
        word = request.form.get('search_txt')
        allNews = db.child('Event').get().val()
        data = []
        if not allNews is None:
            for i in allNews:
                foundEvent = db.child('Event').child(i).get().val()
                if session['status'] == 0:
                    if 'date_post' in foundEvent and foundEvent['date_post'] is not None and foundEvent['date_post'] != '' and datetime.datetime.strptime(foundEvent['date_post'],
                         "%d/%m/%Y") >= datetime.datetime.today():
                        continue
                detail = foundEvent['detail'].split('\r\n')
                img = storage.child("event/" + i).get_url(None)
                dt = 'สร้างเมื่อ ' + foundEvent['date'] + ' ' + foundEvent['time']
                newsDict = {'id': i, 'title': foundEvent['title'], 'detail': detail, 'length': len(detail), 'datetime' : dt ,'image':img,'date':foundEvent['date'],'time':foundEvent['time']}
                if newsDict['title'].find(word) >= 0 or foundEvent['detail'].find(word) >= 0 :
                    data.append(newsDict)
        else:
            newDict = {'id': 'e000', 'title': 'ยังไม่มีข่าวประชาสัมพันธ์', 'detail': ''}
            data.append(newDict)
        if len(data) > 1:
            sort(data)
        if session['status'] == 0:
            return render_template('activity.html', data=data, length=len(data))
        elif session['status'] == 1:
            return render_template('./admin/activity-admin.html', data=data,length=len(data))

@app.route('/interact_search',methods=['POST'])
def interact_search():
    if request.method == 'POST':
        allThread = db.child('Thread').get().val()
        bword = db.child('BWord').get().val()
        word = request.form.get('search_txt')
        data = []
        if not allThread is None:
            for i in allThread:
                foundThread = db.child('Thread').child(i).get().val()
                detail = foundThread['detail'].split('\r\n')
                title = functools.reduce(
                    lambda a, b:
                    a.replace(b["Keyword"], b["Replace"])
                    , bword
                    , foundThread['title']
                )
                if foundThread['owner'] == session['id']:
                    isYour = 1
                else:
                    isYour = 0
                dt = 'สร้างเมื่อ ' + foundThread['date'] + ' ' + foundThread['time']
                newsDict = {'id': i, 'title': title, 'detail': detail, 'owner': foundThread['owner'],
                            'length': len(detail), 'datetime': dt, 'date': foundThread['date'],
                            'time': foundThread['time'],'isYour':isYour}
                if foundThread['title'].find(word) >= 0:
                    data.append(newsDict)
        else:
            newDict = {'id': 't000', 'title': 'ยังไม่มีกระทู้', 'detail': ''}
            data.append(newDict)
        if len(data) > 1:
            sort(data)
        if session['status'] == 1:
            return render_template('./admin/interact-admin.html', data=data, by='', length=len(data))
        elif session['status'] == 0:
            return render_template('interact.html', data=data, by='',length=len(data))

# ข้อมูลผู้ใช้
@app.route('/user-admin.html')
def user_admin():
    allUser = db.child('User').get().val()
    data = []
    for i in allUser:
        foundUser = db.child('User').child(i).get().val()
        if "0" != str(foundUser['isOn']):
            if foundUser['branch'] == session['branch'] or session['id'] == 'admin':
                if "0" != str(foundUser['isOn']):
                    isOn = "เปิดการใช้งาน"
                else:
                    isOn = "ปิดการใช้งาน"
                if foundUser['status'] == 1:
                    status = 'แอดมิน'
                else:
                    status = 'นักศึกษา'
                userDict = {'id':i,'name':foundUser['name'],'prefix':foundUser['prefix'],'password':foundUser['password'],'status':status,
                            'email':foundUser['email'],'branch':foundUser['branch'],'isOn':isOn}
                data.append(userDict)
    return render_template('./admin/user-admin.html',data=data,by='', my_group=session['branch'],my_id=session['id'])

@app.route('/user-admin.html/closed')
def user_admin_closed():
    allUser = db.child('User').get().val()
    data = []
    for i in allUser:
        foundUser = db.child('User').child(i).get().val()
        if "1" != str(foundUser['isOn']):
            if foundUser['branch'] == session['branch'] or session['id'] == 'admin':
                if "0" != str(foundUser['isOn']):
                    isOn = "เปิดการใช้งาน"
                else:
                    isOn = "ปิดการใช้งาน"
                if foundUser['status'] == 1:
                    status = 'แอดมิน'
                else:
                    status = 'นักศึกษา'
                userDict = {'id': i, 'name': foundUser['name'], 'prefix': foundUser['prefix'],
                            'password': foundUser['password'], 'status': status,
                            'email': foundUser['email'], 'branch': foundUser['branch'], 'isOn': isOn}
                data.append(userDict)
    return render_template('./admin/user-admin.html', data=data, by=session['id'], my_group=session['branch'], my_id=session['id'])

@app.route('/user-admin.html/2')
def user_admin_2():
    allUser = db.child('User').get().val()
    data = []
    for i in allUser:
        foundUser = db.child('User').child(i).get().val()
        if str(foundUser['isOn']) != "0":
            if foundUser['branch'] == session['branch'] or session['id'] == 'admin':
                if str(foundUser['isOn']) == "1":
                    if "0" != str(foundUser['isOn']):
                        isOn = "เปิดการใช้งาน"
                    else:
                        isOn = "ปิดการใช้งาน"
                    if foundUser['status'] == 1:
                        status = 'แอดมิน'
                    else:
                        status = 'นักศึกษา'
                    userDict = {'id': i, 'name': foundUser['name'], 'prefix': foundUser['prefix'],
                                'password': foundUser['password'], 'status': status,
                                'email': foundUser['email'], 'branch': foundUser['branch'], 'isOn': isOn}
                    data.append(userDict)
    return render_template('./admin/user-admin.html', data=data, by='', my_group=session['branch'], my_id=session['id'])

@app.route('/user-admin.html/closed2')
def user_admin_closed2():
    allUser = db.child('User').get().val()
    data = []
    for i in allUser:
        foundUser = db.child('User').child(i).get().val()
        if str(foundUser['isOn']) != "1":
            if foundUser['branch'] == session['branch'] or session['id'] == 'admin':
                if "0" != str(foundUser['isOn']):
                    isOn = "เปิดการใช้งาน"
                else:
                    isOn = "ปิดการใช้งาน"
                if foundUser['status'] == 1:
                    status = 'แอดมิน'
                else:
                    status = 'นักศึกษา'
                userDict = {'id': i, 'name': foundUser['name'], 'prefix': foundUser['prefix'],
                            'password': foundUser['password'], 'status': status,
                            'email': foundUser['email'], 'branch': foundUser['branch'], 'isOn': isOn}
                data.append(userDict)
    return render_template('./admin/user-admin.html', data=data, by=session['id'], my_group=session['branch'],
                           my_id=session['id'])

@app.route('/user_search', methods = ['POST'])
def user_search():
    if request.method == 'POST':
        word = request.form.get('search_txt')
        allUser = db.child('User').get().val()
        data = []
        for i in allUser:
            foundUser = db.child('User').child(i).get().val()
            if foundUser['status'] == 1:
                status = 'แอดมิน'
            else:
                status = 'นักศึกษา'
            userDict = {'id':i,'name':foundUser['name'],'password':foundUser['password'],'status':status,'email':foundUser['email'],'branch':foundUser['branch']}
            if userDict['id'].find(word)>=0 or userDict['name'].find(word) >=0 or userDict['branch'].find(word)>=0:
                data.append(userDict)
        return render_template('./admin/user-admin.html',data=data,length=len(data), my_group=session['branch'],my_id=session['id'])

@app.route('/delete_user', methods = ['POST','GET'])
def delete_user():
    if request.method == 'POST':
        db.child('User').child(request.form.get('id')).remove()
    allUser = db.child('User').get().val()
    data = []
    for i in allUser:
        foundUser = db.child('User').child(i).get().val()
        if foundUser['status'] == 1:
            status = 'แอดมิน'
        else:
            status = 'นักศึกษา'
        userDict = {'id': i, 'name': foundUser['name'], 'password': foundUser['password'], 'status': status}
        data.append(userDict)
    return redirect(url_for('user_admin'))

@app.route('/delete_event', methods = ['POST','GET'])
def delete_event():
    if request.method == 'POST':
        db.child('Event').child(request.form.get('id')).remove()
    if session['id'] == "admin":
        return redirect(url_for('activity_admin_2'))
    elif session['id'] != "admin":
        return redirect(url_for('activity_admin'))
    return redirect(url_for('activity_admin'))

@app.route('/delete_news', methods = ['POST','GET'])
def delete_news():
    if request.method == 'POST':
        db.child('News').child(request.form.get('id')).remove()
        storage.child('news').child(request.form.get('id')).put('logo.jpg')
    if session['id'] == "admin":
        return redirect(url_for('publish_admin_2'))
    elif session['id'] != "admin":
        return redirect(url_for('publish_admin'))
    return redirect(url_for('publish_admin'))

@app.route('/delete_interact/<string:id>')
def delete_interact(id:str):
    db.child('Thread').child(id).remove()
    if session['status'] == 0:
        return redirect(url_for('interact'))
    elif session['status'] == 1:
        return redirect(url_for('interact_admin'))

def getAllEmail():
    allUser = db.child('User').get().val()
    emailList = []
    for id in allUser:
        if allUser[id]['notify'] == '1':
            emailList.append(allUser[id]['email'])
    return emailList

def send_mail(title,detail):
    msg = Message(subject=title,
                  sender=app.config.get("MAIL_USERNAME"),
                  recipients=getAllEmail(),
                  body=detail)
    mail.send(msg)

def foundEmail(email):
    allUser = db.child('User').get().val()
    if not allUser is None:
        for i in allUser:
            if allUser[i]['email'] == email:
                return True
        return False
    return False

#เพิ่มผู้ใช้งาน
@app.route('/success', methods = ['POST'])
def success():
    if request.method == 'POST':
        id = str(request.form.get('id'))
        status = request.form.get('status')
        email = request.form.get('email')
        foundUser = db.child('User').get().val()
        if not id in foundUser:
            if foundEmail(email) == False:
                password = request.form.get('password')
                name = request.form.get('name')
                branch = request.form.get('branch')
                chx = request.form.get('isOn')
                isOn = 1
                if chx != "open":
                    isOn = 0
                prefix = request.form.get('prefix')
                if status == 'admin':
                    status = 1
                elif status == 'user':
                    status = 0
                if prefix == 'mr':
                    prefix = 'นาย'
                elif prefix == 'mis':
                    prefix = 'นางสาว'
                elif prefix == 'mrs':
                    prefix = 'นาง'
                elif prefix == 'pro':
                    prefix = 'ศาสตราจารย์'
                elif prefix == 'acp':
                    prefix = 'รองศาสตราจารย์'
                elif prefix == 'atp':
                    prefix = 'ผู้ช่วยศาสตราจารย์'
                newUser = {'name': name,'prefix' : prefix ,'password': password, 'status': status,'email':email,'branch':branch,'notify':'0','isOn':isOn}
                db.child('User').child(id).set(newUser)
                file = request.files['file']
                if not file.filename == "":
                    file.save('temp_profile.jpg')
                    storage.child('profile').child(id).put('temp_profile.jpg')
                    os.remove('temp_profile.jpg')
                else:
                    storage.child('profile').child(id).put('default_profile_pic_001.png')
                return render_template("./admin/add-user-admin.html",data={'notify':1,'id':'','prefix':'','name':'','status':'','branch':''})
            return render_template("./admin/add-user-admin.html",data={'notify':3,'id':request.form.get('id'),'prefix':request.form.get('prefix'),'name':request.form.get('name'),'status':status,'branch':request.form.get('branch')})
        return render_template("./admin/add-user-admin.html",data={'notify':2,'name':request.form.get('name'),'prefix':request.form.get('prefix'),'status':status,'email':email,'branch':request.form.get('branch')})

#เพิ่มผู้ใช้งานแบบแพ็ค
@app.route('/success_multiple',methods=['POST'])
def success_multiple():
    foundUser = db.child('User').get().val()
    file = request.files['file']
    if not file.filename == "":
        file.save('data.csv')
        df = pd.read_csv('data.csv')
        df = pd.DataFrame(df)
        for index, row in df.iterrows():
            id = str(row['id'])
            name = str(row['name'])
            prefix = str(row['prefix'])
            email = str(row['email'])
            password = str(row['password'])
            status = int(row['status'])
            branch = str(row['branch'])
            chx = request.form.get('isOn')
            isOn = 1
            if chx != "open":
                isOn = 0
            if not id in foundUser:
                if foundEmail(email) == False:
                    newUser = {'name': name,'prefix' : prefix, 'password': password, 'status': status,'email':email,'branch':branch,'notify':'0','isOn':isOn}
                    db.child('User').child(id).set(newUser)
                    storage.child('profile').child(id).put('default_profile_pic_001.png')
        os.remove('data.csv')
    return redirect(url_for('user_admin'))

@app.route('/edit_user', methods = ['POST'])
def edit_user():
    if request.method == 'POST':
        id = str(request.form.get('id'))
        oldId = str(request.form.get('oldId'))
        oldEmail = request.form.get('oldEmail')
        status = request.form.get('status')
        email = request.form.get('email')
        prefix = request.form.get('prefix')
        foundUser = db.child('User').get().val()
        if not id in foundUser or id == oldId:
            if foundEmail(email) == False or email == oldEmail:
                password = request.form.get('password')
                name = request.form.get('name')
                branch = request.form.get('branch')
                chx = request.form.get('isOn')
                isOn = 1
                if chx != "open":
                    isOn = 0
                if status == 'admin':
                    status = 1
                elif status == 'user':
                    status = 0
                if prefix == 'mr':
                    prefix = 'นาย'
                elif prefix == 'mis':
                    prefix = 'นางสาว'
                elif prefix == 'mrs':
                    prefix = 'นาง'
                elif prefix == 'pro':
                    prefix = 'ศาสตราจารย์'
                elif prefix == 'acp':
                    prefix = 'รองศาสตราจารย์'
                elif prefix == 'atp':
                    prefix = 'ผู้ช่วยศาสตราจารย์'
                newUser = {'name': name, 'prefix' : prefix ,'password': password, 'status': status,'email':email,'branch':branch,'notify':'0','isOn':isOn}
                db.child('User').child(id).set(newUser)
                file = request.files['file']
                if not file.filename == "":
                    file.save('temp_profile.jpg')
                    storage.child('profile').child(id).put('temp_profile.jpg')
                    os.remove('temp_profile.jpg')
                return redirect(url_for('user_admin'))
            return redirect(url_for('edit_user_admin',id=oldId))
        return redirect(url_for('edit_user_admin',id=oldId))

def getDateFormated(date_str):
    toDate = datetime.datetime.strptime(date_str+' 00:00:00','%Y/%m/%d %H:%M:%S')
    formatedDate = '{}/{}/{}'.format(toDate.day,toDate.month,toDate.year)
    return formatedDate

@app.route('/success_index', methods=['POST'])
def success_index():
    if request.method == 'POST':
        allNews = db.child('ImgeIndex').get().val()
        id = 1
        if not allNews is None:
            for i in allNews:
                preID = int(i[1:])
                if id == preID:
                    id += 1
                else:
                    break
        format = "{:0>3}"
        currentID = 'n' + format.format(id)
        db.child('ImgeIndex').child(currentID).set(currentID)
        if request.method == 'POST':
            file = request.files['file']
            if not file.filename == "":
                file.save('temp_index_pic')
                storage.child('index').child(currentID).put('temp_index_pic')
                os.remove('temp_index_pic')
            else:
                storage.child('index').child(currentID).put('logo.jpg')

        return render_template('./admin/index-admin.html')

@app.route('/success_news', methods = ['POST'])
def success_news():
    if request.method == 'POST':
        allNews = db.child('News').get().val()
        id = 1
        if not allNews is None:
            for i in allNews:
                preID = int(i[1:])
                if id == preID:
                    id += 1
                else:
                    break
        format = "{:0>3}"
        currentID = 'n'+format.format(id)
        date, time , date7 = getDateTime()
        detail = request.form.get('detail')
        del_date = request.form.get('date')
        groups = request.form.get('branch')
        chx = request.form.get('isOn')
        isOn = 1
        if chx != "open":
            isOn = 0
        if del_date == '':
            delDate = ''
        else:
            delDate = del_date.replace('-', '/')
            delDate = getDateFormated(delDate)
        post_date = request.form.get('datepost')
        if post_date == '' or post_date is None:
            postDate = ''
        else:
            postDate = post_date.replace('-', '/')
            postDate = getDateFormated(postDate)
        newNews = {'title':request.form.get('title'),'detail':detail, 'group':groups,'owner':session['id'],'date_post' : postDate ,
                   'date':date,'time':time,'date_del':delDate,'isOn':isOn}
        db.child('News').child(currentID).set(newNews)
        file = request.files['file']
        if not file.filename == "":
            file.save('temp_news_pic')
            storage.child('news').child(currentID).put('temp_news_pic')
            os.remove('temp_news_pic')
        else:
            storage.child('news').child(currentID).put('logo.jpg')
        task = AppContextThread(target=send_mail('แจ้งเตือน '+request.form.get('title'),request.form.get('detail')))
        task.start()
        task.join()
        if session['id'] == "admin":
            return redirect(url_for('publish_admin_2'))
        elif session['id'] != "admin":
            return redirect(url_for('publish_admin'))
        return redirect(url_for('publish_admin'))

@app.route('/edit_news', methods = ['POST'])
def edit_news():
    if request.method == 'POST':
        date, time , date7 = getDateTime()
        detail = request.form.get('detail')
        del_date = request.form.get('date')
        chx = request.form.get('isOn')
        isOn = 1
        if chx != "open":
            isOn = 0
        if del_date == '':
            delDate = ''
        else:
            delDate = del_date.replace('-', '/')
            delDate = getDateFormated(delDate)
        post_date = request.form.get('datepost')
        groups = request.form.get('branch')
        if post_date == '' or post_date is None:
            postDate = ''
        else:
            postDate = post_date.replace('-', '/')
            postDate = getDateFormated(postDate)
        newNews = {'title':request.form.get('title'),'detail':detail,'date_post' : postDate , 'group':groups,'owner':session['id'],'date':date,'time':time,'date_del':delDate,'isOn':isOn}
        db.child('News').child(request.form.get('id')).set(newNews)
        file = request.files['file']
        if not file.filename == "":
            file.save('temp_news_pic')
            storage.child('news').child(request.form.get('id')).put('temp_news_pic')
            os.remove('temp_news_pic')
        if session['id'] == "admin":
            return redirect(url_for('publish_admin_2'))
        elif session['id'] != "admin":
            return redirect(url_for('publish_admin'))
        return redirect(url_for('publish_admin'))

@app.route('/success_event', methods = ['POST'])
def success_event():
    if request.method == 'POST':
        allEvent = db.child('Event').get().val()
        id = 1
        if not allEvent is None:
            for i in allEvent:
                preID = int(i[1:])
                if id == preID:
                    id += 1
                else:
                    break
        format = "{:0>3}"
        currentID = 'e'+format.format(id)
        date,time,date7 = getDateTime()
        del_date = request.form.get('date')
        groups = request.form.get('branch')
        chx = request.form.get('isOn')
        isOn = 1
        if chx != "open":
            isOn = 0
        if del_date == '':
            delDate = ''
        else:
            delDate = del_date.replace('-', '/')
            delDate = getDateFormated(delDate)
        post_date = request.form.get('datepost')
        if post_date == '' or post_date is None:
            postDate = ''
        else:
            postDate = post_date.replace('-', '/')
            postDate = getDateFormated(postDate)
        newNews = {'title':request.form.get('title'),'detail':request.form.get('detail'), 'group':groups,'owner':session['id'],
                   'date_post' : postDate,'date':date,'time':time,'date_del':delDate,'isOn':isOn}
        db.child('Event').child(currentID).set(newNews)
        file = request.files['file']
        if not file.filename == "":
            file.save('temp_event_pic')
            storage.child('event').child(currentID).put('temp_event_pic')
            os.remove('temp_event_pic')
        else:
            storage.child('event').child(currentID).put('logo.jpg')
        task = AppContextThread(target=send_mail('แจ้งเตือน '+request.form.get('title'),request.form.get('detail')))
        task.start()
        task.join()
        if session['id'] == "admin":
            return redirect(url_for('activity_admin_2'))
        elif session['id'] != "admin":
            return redirect(url_for('activity_admin'))
        return redirect(url_for('activity_admin'))

@app.route('/edit_event', methods = ['POST'])
def edit_event():
    if request.method == 'POST':
        date, time , date7 = getDateTime()
        detail = request.form.get('detail')
        del_date = request.form.get('date')
        if del_date == '':
            delDate = ''
        else:
            delDate = del_date.replace('-', '/')
            delDate = getDateFormated(delDate)
        post_date = request.form.get('datepost')
        groups = request.form.get('branch')
        chx = request.form.get('isOn')
        isOn = 1
        if chx != "open":
            isOn = 0
        if post_date == '' or post_date is None:
            postDate = ''
        else:
            postDate = post_date.replace('-', '/')
            postDate = getDateFormated(postDate)
        newEvent = {'title':request.form.get('title'),'date_post' : postDate, 'group':groups,'owner':session['id'],'detail':detail,
                    'date':date,'time':time,'date_del':delDate,'isOn':isOn}
        db.child('Event').child(request.form.get('id')).set(newEvent)
        file = request.files['file']
        if not file.filename == "":
            file.save('temp_event_pic')
            storage.child('event').child(request.form.get('id')).put('temp_event_pic')
            os.remove('temp_event_pic')
        if session['id'] == "admin":
            return redirect(url_for('activity_admin_2'))
        elif session['id'] != "admin":
            return redirect(url_for('activity_admin'))
        return redirect(url_for('activity_admin'))

@app.route('/success_thread', methods = ['POST'])
def success_thread():
    if request.method == 'POST':
        allThread = db.child('Thread').get().val()
        id = 1
        if not allThread is None:
            for i in allThread:
                preID = int(i[1:])
                if id == preID:
                    id += 1
                else:
                    break
        format = "{:0>3}"
        currentID = 't'+format.format(id)
        detail = request.form.get('detail')
        date,time ,date7 = getDateTime()
        newThread = {'title':request.form.get('title'),'detail':detail,'owner':session['id'],'date':date,'time':time}
        db.child('Thread').child(currentID).set(newThread)
        file = request.files['file']
        if not file.filename == "":
            file.save('temp_news_pic')
            storage.child('thread').child(currentID).put('temp_news_pic')
            os.remove('temp_news_pic')
        else:
            storage.child('thread').child(currentID).put('logo.jpg')
        if session['status'] == 0:
            return redirect(url_for('interact'))
        elif session['status'] == 1:
            return redirect(url_for('interact_admin'))
        return redirect(url_for('interact-admin'))

@app.route('/edit_thread', methods = ['POST'])
def edit_thread():
    if request.method == 'POST':
        allThread = db.child('Thread').get().val()
        id = 1
        if not allThread is None:
            for i in allThread:
                preID = int(i[1:])
                if id == preID:
                    id += 1
                else:
                    break
        format = "{:0>3}"
        currentID = 't' + format.format(id)
        detail = request.form.get('detail')
        date, time, date7 = getDateTime()
        newThread = {'title': request.form.get('title'), 'detail': detail, 'owner': session['id'], 'date': date,
                     'time': time}
        db.child('Thread').child(request.form.get('id')).set(newThread)
        file = request.files['file']
        if not file.filename == "":
            file.save('temp_news_pic')
            storage.child('thread').child(request.form.get('id')).put('temp_news_pic')
            os.remove('temp_news_pic')
        if session['status'] == 0:
            return redirect(url_for('interact'))
        elif session['status'] == 1:
            return redirect(url_for('interact_admin'))
        return redirect(url_for('interact-admin'))

def autogen(tid):
    allThread = db.child('Thread').child(tid).child('Reply').get().val()

    id = 1
    if not allThread is None:
        for i in allThread:
            preID = int(i[1:])
            if id == preID:
                id += 1
            else:
                break
    format = "{:0>3}"
    currentID = format.format(id)
    return str(currentID)

@app.route('/logout') #logout ทำให้ค่าว่าง
def logout():
    session['id'] = None
    session['name'] = None
    session['prefix'] =None
    session['email'] = None
    session['status'] = None
    session['notify'] = None
    autoDelete()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()

@app.route('/Bdropdownlist')
def Bdropdownlist():
    # BDl = db.child('User').get().val()
    # print(BDl)
    # data = []
    # for i in BDl:
    #     data.append("a")

    return render_template('./admin/add-user-admin.html')
