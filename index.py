from flask import Blueprint,render_template,request,jsonify,redirect,url_for,session
import pymysql,re,math,hashlib,time

app1=Blueprint('app1',__name__)
# app1=Blueprint('app1',__name__,template_folder="templates/news")
db = pymysql.connect(host="localhost",user="root",password="",db="news")
cur = db.cursor()

@app1.route('/')
def index():
    sql1="select * from class"
    cur.execute(sql1)
    res1=cur.fetchall()
    if 'qusername' in session:
        flag=1
        sql = "select headimg from user where username='%s'" % session['qusername']
        cur.execute(sql)
        headimgurl = cur.fetchone()[0]
        if headimgurl=="":
            headimgurl = "static/index/img/1.jpg"

    else:
        flag=0
        headimgurl = "static/index/img/man.png"
    return render_template("news/index.html",data=res1,flag=flag,headimgurl=headimgurl)

@app1.route('/switchindex<category>')
def switchindex(category):
    sql="select n_id from news_category where category='%s'"%category
    cur.execute(sql)
    res=cur.fetchall()
    arr=[]
    if res:
        for i in res:
            sql="select news.*,c.category from news left join (select n_id,group_concat(category) as category from news_category as c group by n_id) as c on news.id=c.n_id where news.id=%s and news.s_id=1"%i[0]
            cur.execute(sql)
            res1=cur.fetchone()
            if res1 == None:
                continue
            arr.append(res1)
    for item in arr:
        arr[arr.index(item)]=list(item)
    for item in arr:
        if item[3]!="":
            item[3]=item[3].split(',')
            length=len(item[3])
        else:
            length=0
        item.append(length)
    return jsonify(arr)

@app1.route('/opendetails<id>')
def opendetails(id):
    sql = "select n.*,c.category,k.keyword from news as n left join (select c.n_id,group_concat(c.category) as category from news_category as c group by c.n_id) as c on n.id=c.n_id left join (select k.n_id,group_concat(k.keyword) as keyword from news_keyword as k group by k.n_id) as k on n.id=k.n_id where n.id=%s" % id
    cur.execute(sql)
    res=cur.fetchall()

    sql1="select group_concat(keyword) from news_keyword where n_id=%s"%id
    cur.execute(sql1)
    now_k=cur.fetchone()[0].split(',')
    sql2="select n_id,group_concat(keyword) from news_keyword group by n_id"
    cur.execute(sql2)
    all_k=cur.fetchall()
    dict1={}
    for item in all_k:
        dict1[item[0]]=item[1].split(',')
    for k,v in dict1.items():
        dict1[k]= len(set(v) & set(now_k))
    # sorted(dict1, key=lambda x: x[1], reverse=True)

    newid = []
    for k, v in dict1.items():
        if v > 0 and k != int(id):
            newid.append(str(k))
    tuijian = ""
    if newid:
        sql3 = "select id,n_title,author,imgurl from news where id in (%s) and s_id=1" % (",".join(newid))
        cur.execute(sql3)
        tuijian = list(cur.fetchall())
        for item in tuijian:
            tuijian[tuijian.index(item)]=list(item)
        for item in tuijian:
            item[3]=item[3].split(',')
            if item[3][0]=="":
                length=0
            else:
                length=len(item[3])
            item.append(length)
            if len(item[3])>=3:
                item[3]=item[3][0:3]
            elif len(item[3])>0:
                item[3]=item[3][0]
    return render_template('news/details.html',data=res,tuijian=tuijian)

@app1.route('/openlogin')
def openlogin():
    return render_template('news/login.html')

@app1.route('/loginout')
def loginout():
    del session['qusername']
    return redirect(url_for('app1.openlogin'))

@app1.route('/login',methods=['post'])
def login():
    username = request.form['username']
    password = request.form['password']
    s = hashlib.md5()
    s.update(password.encode())
    password = s.hexdigest()
    sql = "select count(*) from user where username='%s'"%username
    cur.execute(sql)
    num=cur.fetchone()[0]
    if num!=0:
        sql = "select password from user where username='%s'" % username
        cur.execute(sql)
        password0=cur.fetchone()[0]
        if password==password0:
            session['qusername']=username
            return 'ok'
        else:
            return '密码错误'
    else:
        return '账号为空'

@app1.route('/openregister')
def openregister():
    return render_template('news/register.html')

@app1.route('/register',methods=['post'])
def register():
    username = request.form['username']
    password = request.form['password']
    s = hashlib.md5()
    s.update(password.encode())
    password = s.hexdigest()
    sql = "select count(*) from user where username='%s'" % username
    cur.execute(sql)
    num = cur.fetchone()[0]
    if num==0:
        sql="insert into user(username,password) values('%s','%s')"%(username,password)
        cur.execute(sql)
        db.commit()
        return 'ok'
    else:
        return '账号已存在'

@app1.route('/opencomment<n_id>')
def opencomment(n_id):
    if 'qusername' in session:
        flag = 1
        name=session['qusername']
    else:
        flag = 0
        name=""
    sql="select * from comment where n_id=%s and to_comid=0 order by time desc"%n_id
    cur.execute(sql)
    res=list(cur.fetchall())
    length=len(res)
    t_time=time.time()
    for item in res:
        res[res.index(item)]=list(item)
    data=[]
    for item in res:
        # 2018 - 10 - 26 10: 57:11
        timeArray = time.strptime(str(item[3]), "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        time_difference=int(t_time-timeStamp)
        if time_difference<60:
            item.append("s")
            item[3]=time_difference
        else:
            item.append("h")
        arr=[]
        search_comment(item[0],arr)
        each_data=[]
        each_data.append(item)
        each_data.append(arr)
        data.append(each_data)

    return render_template('news/comment.html',n_id=n_id,flag=flag,name=name,data=data,length=length)

def search_comment(comid,arr):
    sql="select * from comment where to_comid=%s order by time desc"%comid
    cur.execute(sql)
    res=cur.fetchall()
    if len(res)!=0:
        for item in res:
            # print(item)
            arr.append(item)
            search_comment(item[0],arr)
        return arr
    else:
        return ""

@app1.route('/comment',methods=['post'])
def comment():
    if 'qusername' in session:
        con=request.form.get('con')
        n_id=request.form.get('n_id')
        qusername=session['qusername']
        n_id=int(n_id)
        print(session['qusername'],con,n_id)
        sql="insert into comment (n_id,author,con,zan,to_comid,q_author) values(%s,'%s','%s',0,0,'')"%(n_id,qusername,con)
        cur.execute(sql)
        db.commit()
        sql1="select id from comment where n_id=%s order by time desc"%n_id
        cur.execute(sql1)
        n_comid=cur.fetchone()[0]
        print(n_comid)
        res={'type':'ok','n_comid':n_comid}
        return jsonify(res)
    else:
        return 'no'

@app1.route('/dianzan',methods=['post'])
def dianzan():
    num=request.form.get('zannum')
    comid=request.form.get('id')
    sql="update comment set zan=%s where id=%s"%(int(num),int(comid))
    cur.execute(sql)
    db.commit()
    return 'ok'

@app1.route('/answer_comment',methods=['post'])
def answer_comment():
    comid=request.form.get('id')
    n_id = request.form.get('n_id')
    author = session['qusername']
    answer_con=request.form.get('answer_con')
    sql="select author from comment where id=%s"%comid
    cur.execute(sql)
    q_author=cur.fetchone()[0]
    sql="insert into comment (n_id,author,con,zan,to_comid,q_author) values(%s,'%s','%s',0,%s,'%s')"%(n_id,author,answer_con,comid,q_author)
    cur.execute(sql)
    db.commit()
    sql1="select id from comment where con='%s'"%answer_con
    cur.execute(sql1)
    new_comid=cur.fetchone()[0]
    res={
        'new_comid':new_comid,
        'q_author':q_author,
        'answer_con':answer_con
    }
    # print(new_comid,q_author,answer_con)
    return jsonify(res)

@app1.route('/ss_keyword',methods=['post'])
def ss_keyword():
    con=request.form.get('con')
    now_k=con.split(',')
    print(con)
    sql2 = "select n_id,group_concat(keyword) from news_keyword group by n_id"
    cur.execute(sql2)
    all_k = cur.fetchall()
    dict1 = {}
    for item in all_k:
        dict1[item[0]] = item[1].split(',')
    for k, v in dict1.items():
        dict1[k] = len(set(v) & set(now_k))
    # sorted(dict1, key=lambda x: x[1], reverse=True)

    newid = []
    for k, v in dict1.items():
        if v > 0:
            newid.append(str(k))
    tuijian = ""
    if newid:
        sql3 = "select id,n_title,author,imgurl from news where id in (%s) and s_id=1" % (",".join(newid))
        cur.execute(sql3)
        tuijian = list(cur.fetchall())
        for item in tuijian:
            tuijian[tuijian.index(item)] = list(item)
        for item in tuijian:
            if item[3] == "":
                length = 0
            else:
                item[3] = item[3].split(',')
                length = len(item[3])

            item.append(length)
            if tuijian=='':
                flag=0
            else:
                flag=1
        print(tuijian)
        res={
            'tuijian':tuijian,
            'flag':flag
        }
        return jsonify(res)
    else:
        res = {
            'tuijian': "",
            'flag': 0
        }
        return jsonify(res)

@app1.route('/uploadPimg', methods=['post'])
def uploadPimg():
    f = request.files['file']
    imgurl = "static/upload/headimg/"+f.filename
    f.save(imgurl)
    rep = {'info':"ok",'imgurl':'/'+imgurl}
    sql = "update user set headimg='%s' where username='%s'" % (imgurl, session['qusername'])
    cur.execute(sql)
    db.commit()
    return jsonify(rep)

