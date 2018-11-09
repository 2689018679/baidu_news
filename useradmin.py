from flask import Blueprint,render_template,request,jsonify,redirect,url_for,session
import pymysql,re,math,hashlib

app3=Blueprint('app3',__name__,template_folder='templates/useradmin/')
db = pymysql.connect(host="localhost",user="root",password="",db="news")
cur = db.cursor()
@app3.route('/')
def index():
    if 'username' in session:
        try:
            id=session['id']
        except:
            id=""
        return render_template("index.html",id=id)
    else:
        return redirect(url_for("app3.login"))

@app3.route('/login')
def login():
    return render_template("login.html")

@app3.route('/loginout') # 退出后台
def loginout():
    del session['username']
    del session['id']
    return redirect(url_for("app3.login"))

@app3.route("/checklogin", methods=['post'])
def checklogin():
    username = request.form['username']
    password = request.form['password']

    s = hashlib.md5()
    s.update(password.encode())
    password = s.hexdigest()

    #　组织sql语句
    sql = "select password,level from users where username='%s'"%username
    # 执行sql语句
    cur.execute(sql)
    # 获取查询结果
    password0=""
    res = cur.fetchone()
    if res != None:
        password0 = res[0]

    if password0 == password:
        # return "登陆成功"
        session['username'] = username
        session['id'] = res[1]
        return redirect(url_for("app3.index"))
    else:
        # return "登陆失败"
        return redirect(url_for("app3.tips",state="no",href="login",time=3))


@app3.route("/openadduser")
def openadduser():
    if 'username' in session:
        if session['id']==1:
            return render_template("adduser.html")
        else:
            return redirect(url_for("app3.tips",state="no",href="index",time=3))
    else:
        return redirect(url_for("app3.login"))

@app3.route('/adduser',methods=['post'])
def adduser():
    if 'username' in session:
        username=request.form["username"]
        newpass=request.form["newpass"]
        rnewpass=request.form["renewpass"]
        if username!="" and newpass!="" and rnewpass!="":
            if newpass == rnewpass:
                s = hashlib.md5()
                s.update(newpass.encode())
                password = s.hexdigest()
                sql = "insert into users (username,password,level) values ('%s','%s',%s)"%(username,password,2)
                cur.execute(sql)
                db.commit()
                print(1)
                return redirect(url_for("app3.tips", state="yes", href="listuser1", time=3))
            else:
                return redirect(url_for("app3.tips", state="no", href="openadduser", time=3))
        else:
            return redirect(url_for("app3.tips", state="no", href="openadduser", time=3))
    else:
        return redirect(url_for("app3.login"))

@app3.route("/listuser<page>")
def listuser(page):
    if 'username' in session:
        sql = "select count(*) from users"
        cur.execute(sql)
        length = cur.fetchone()[0]
        page = int(page)

        sql = "select id,username,level from users limit %s,6"%((page-1)*6)
        cur.execute(sql)
        res = cur.fetchall()
        pages=range(1, math.ceil(length/6)+1)
        return render_template("listuser.html",data=res,pages=pages,now=page)
    else:
        return redirect(url_for("app3.login"))

@app3.route('/openedituser<id>_<username>')
def openedituser(id,username):
    if 'username' in session and session['id']==1:
        return render_template("edituser.html",id=id,username=username)

@app3.route('/edituser',methods=['post'])
def edituser():
    print(0)
    if 'username' in session and session['id']==1:
        id = request.form['id']
        mypass = request.form['mpass'] # 原始密码
        newpass = request.form['newpass']
        username = request.form['username']

        s = hashlib.md5()
        s.update(mypass.encode())
        mypass = s.hexdigest()

        sql = "select password from users where id=%s"%id
        cur.execute(sql)
        res = cur.fetchone()[0]
        print(1)
        if res == mypass:
            h = hashlib.md5()
            h.update(newpass.encode())
            newpass = h.hexdigest()
            sql = "update users set password='%s' where id=%s"%(newpass,id)
            cur.execute(sql)
            db.commit()
            print(2)
            return redirect(url_for("app3.tips",state="yes",href="listuser1",time=3))
        else:
            return redirect(url_for("app3.tips",state="no",href="openedituser%s_%s"%(id,username),time=3))

@app3.route('/deluser<name>')
def deluser(name):
    if name != session['username']:
        try:
            sql = "delete from users where username='%s'"%name
            cur.execute(sql)
            db.commit()
        except:
            db.rollback()  # 数据回滚
        return redirect(url_for("app3.tips",state="yes",href='listuser1',time=3))
    else:
        return redirect(url_for("app3.tips",state="no",href='listuser1',time=3))

@app3.route('/tips_<state>_<href>_<time>')
def tips(state, href, time):
    return render_template("tips.html", state=state, href=href, time=time)

@app3.route('/openaddclass')
def openaddclass():
    sql = "select id,name from class"
    cur.execute(sql)
    res = cur.fetchall()
    return render_template("addclass.html",data=res)

@app3.route('/addclass',methods=['post'])
def addclass():
    name = request.form['name']

    sql = "insert into class(name) values ('%s')"%name
    cur.execute(sql)
    db.commit()
    sql = "select id from class where name='%s'"%name
    cur.execute(sql)
    id = cur.fetchone()[0]
    res={'ifo':'ok','id':id}

    return jsonify(res)


@app3.route('/openaddnews')
def openaddnews():
    sql = "select * from class"
    cur.execute(sql)
    res=cur.fetchall()
    return render_template('addnews.html',data=res)

@app3.route('/addnews',methods=['post'])
def addnews():
    n_title=request.form['n_title']
    cid=request.form['cid']
    con=request.form['con']
    keyword=request.form['keyword']
    author=request.form['author']
    conres=re.findall(r'<img alt="" src="(.*?)"',con)
    imgurl=",".join(conres)
    arr=cid.split(',')[:-1]
    keyword=keyword.split(',')
    sql="insert into news(n_title,author,imgurl,s_id,con) values('%s','%s','%s',0,'%s')"%(n_title,author,imgurl,con)
    cur.execute(sql)
    db.commit()

    sql1="select id from news where n_title='%s' order by c_time desc"%n_title
    cur.execute(sql1)
    n_id=cur.fetchone()[0]

    for cid in arr:
        sql2="insert into news_category (n_id,category) values(%s,'%s')"%(n_id,cid)
        cur.execute(sql2)
        db.commit()

    for k in keyword:
        sql3="insert into news_keyword (n_id,keyword) values(%s,'%s')"%(n_id,k)
        cur.execute(sql3)
        db.commit()

    return redirect(url_for('app3.openaddnews'))

@app3.route('/openlistnews<page>')
def openlistnews(page):
    sql = "select count(*) from news"
    cur.execute(sql)
    length = cur.fetchone()[0]
    page = int(page)

    sql1 = "select n.*,c.category,k.keyword from news as n left join (select c.n_id,group_concat(c.category) as category from news_category as c group by c.n_id) as c on n.id=c.n_id left join (select k.n_id,group_concat(k.keyword) as keyword from news_keyword as k group by k.n_id) as k on n.id=k.n_id order by n.id desc limit %s,6"%((page-1)*6)
    cur.execute(sql1)
    res = cur.fetchall()
    pages=range(1,math.ceil(length/6)+1)
    return render_template('listnews.html',data=res,pages=pages,now=page)

@app3.route('/listdelnews<id>')
def listdelnews(id):
    sql = "delete from news where id=%s"%id
    cur.execute(sql)
    db.commit()
    sql1 = "delete from news_category where n_id=%s" % id
    cur.execute(sql1)
    db.commit()
    sql2 = "delete from news_keyword where n_id=%s" % id
    cur.execute(sql2)
    db.commit()
    return 'ok'


@app3.route('/openmodnews<id>')
def openmodnews(id):
    sql = "select n.*,c.category,k.keyword from news as n left join (select c.n_id,group_concat(c.category) as category from news_category as c group by c.n_id) as c on n.id=c.n_id left join (select k.n_id,group_concat(k.keyword) as keyword from news_keyword as k group by k.n_id) as k on n.id=k.n_id where n.id=%s" % id
    cur.execute(sql)
    res = cur.fetchall()
    sql1 = "select id,name from class"
    cur.execute(sql1)
    res1 = cur.fetchall()
    return render_template('modnews.html',data=res,data1=res1)


@app3.route('/modnews<id>',methods=['post'])
def modnews(id):
    sql = "delete from news where id=%s" % id
    cur.execute(sql)
    db.commit()
    sql1 = "delete from news_category where n_id=%s" % id
    cur.execute(sql1)
    db.commit()
    sql2 = "delete from news_keyword where n_id=%s" % id
    cur.execute(sql2)
    db.commit()

    n_title = request.form['n_title']
    cid = request.form['cid']
    con = request.form['con']
    keyword = request.form['keyword']
    author = request.form['author']
    conres = re.findall(r'<img alt="" src="(.*?)"', con)
    imgurl = ",".join(conres)
    arr = cid.split(',')[:-1]
    keyword = keyword.split(',')
    sql = "insert into news(n_title,author,imgurl,s_id,con) values('%s','%s','%s',0,'%s')" % (
    n_title, author, imgurl, con)
    cur.execute(sql)
    db.commit()

    sql1 = "select id from news where n_title='%s' order by c_time desc" % n_title
    cur.execute(sql1)
    n_id = cur.fetchone()[0]

    for cid in arr:
        sql2 = "insert into news_category (n_id,category) values(%s,'%s')" % (n_id, cid)
        cur.execute(sql2)
        db.commit()

    for k in keyword:
        sql3 = "insert into news_keyword (n_id,keyword) values(%s,'%s')" % (n_id, k)
        cur.execute(sql3)
        db.commit()

    return redirect(url_for('app3.openlistnews',page=1))


@app3.route('/sendnews<id>')
def sendnews(id):
    sql="update news set s_id=1 where id=%s"%id
    cur.execute(sql)
    db.commit()
    return 'ok'


@app3.route('/backnews<id>')
def backnews(id):
    sql="update news set s_id=0 where id=%s"%id
    cur.execute(sql)
    db.commit()
    return 'ok'

@app3.route('/listdeskuser<page>')
def listdeskuser(page):
    if 'username' in session:
        sql = "select count(*) from user"
        cur.execute(sql)
        length = cur.fetchone()[0]
        page = int(page)

        sql = "select id,username,password from user limit %s,6"%((page-1)*6)
        cur.execute(sql)
        res = cur.fetchall()
        pages=range(1, math.ceil(length/6)+1)
        return render_template("listdesk_user.html",data=res,pages=pages,now=page)
    else:
        return redirect(url_for("app3.login"))

@app3.route('/Reset_DeskUser_password<id>')
def Reset_DeskUser_password(id):
    s = hashlib.md5()
    s.update("000000".encode())
    password = s.hexdigest()
    print(id,password)
    sql="update user set password='%s' where id=%s"%(password,id)
    cur.execute(sql)
    db.commit()
    return redirect(url_for("app3.tips", state="yes", href='listdeskuser1', time=3))

@app3.route('/Cancellation_DeskUser<id>')
def Cancellation_DeskUser(id):
    sql="delete from user where id=%s"%id
    cur.execute(sql)
    db.commit()
    return redirect(url_for("app3.tips", state="yes", href='listdeskuser1', time=3))
