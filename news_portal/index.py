from bs4 import BeautifulSoup
from flask import (Flask, flash, redirect, render_template,
                   request, session, url_for)
from flask_bootstrap import Bootstrap
from flask_uploads import IMAGES, UploadSet, configure_uploads
from flask_wtf import FlaskForm
from flaskext.mysql import MySQL
from wtforms import (FileField, PasswordField, SelectField,
                     StringField, SubmitField, TextAreaField)
from wtforms.validators import InputRequired, Length

app = Flask(__name__)
Bootstrap(app) #duoc sd bootstrap

# mysql connection setup
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'chang'
app.config['MYSQL_DATABASE_PASSWORD'] = '12345678'
app.config['MYSQL_DATABASE_DB'] = 'news_portal'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
    
# photo upload
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

# returns an array of values : truyen vao cau lenh sql -> tra ve du lieu: 
def sqlDatas(query, vals, i):
    cursor = conn.cursor()
    cursor.execute(query, vals)
    datas = []
    arraydata = []
    try:
        if i == 1:
            arraydata = list(cursor.fetchone())
        else:
            datas = list(cursor.fetchall())
            for data in datas:
                data = list(data)
                arraydata.append(data)
    except TypeError:
        print(TypeError)
    cursor.close()
    return arraydata

# execute sql statements : thuc thi cau lenh ay


def sqlExecute(query, vals):
    cursor = conn.cursor()
    cursor.execute(query, vals)
    conn.commit()
    cursor.close()


# wtf form for editor/writer login: validate cac du lieu dat vao
class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[InputRequired()])
    password = PasswordField('Mật khẩu', validators=[
                             InputRequired(), Length(min=8, max=20)])


# date format: chuyen tu kieu dl datetime -> chuoi
def myDate(a):
    return str(a.strftime("%x | %X"))

# times ago format: 


def pretty_date(time=False):
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return " cách đây vài giây"
        if second_diff < 60:
            return str(second_diff) + " cách đây vài giây"
        if second_diff < 120:
            return "1 phút trước"
        if second_diff < 3600:
            return str(round(second_diff / 60)) + " phút trước"
        if second_diff < 7200:
            return "1 giờ trước"
        if second_diff < 86400:
            return str(round(second_diff / 3600)) + " giờ trước"
    if day_diff == 1:
        return "hôm qua"
    if day_diff < 7:
        return str(day_diff) + " ngày trước"
    if day_diff < 31:
        return str(day_diff / 7) + " tuần trước"
    if day_diff < 365:
        return str(day_diff / 30) + " tháng trước"
    return str(day_diff / 365) + " năm trước"

# returns the sections of the articles: ham lay ra cac chuyen muc


def sections():
    sectionsdb = sqlDatas("select name from sections", None, None)
    mysec = []
    for section in sectionsdb:
        for i in section:
            mysec.append(i)
    return mysec

# returns the number of articles per section : lay ra so luong cac bai bao cua moi chuyen muc


def no_of_articles():
    num_of_article_per_section = []
    for section in sections():
        count = sqlDatas(
            "select count(*) from articles where section=%s", section, 1)[0]
        num_of_article_per_section.append(count)

    return num_of_article_per_section


# returns the position of the current user
def position(un):
    return sqlDatas("select position from users where username=%s", un, 1)[0]

# returns the full name of the current user


def FullName(un):
    return sqlDatas("select Name from users where username=%s", un, 1)[0]


# form for resetting password in profile page
class ResetPassword(FlaskForm):
    currentPassword = PasswordField("Mật khẩu hiện tại", validators=[
                                    InputRequired(), Length(min=8, max=20)])
    newPassword = PasswordField("Mật khẩu mới", validators=[
                                InputRequired(), Length(min=8, max=20)])
    retypePassword = PasswordField("Nhập lại mật khẩu mới", validators=[
                                   InputRequired(), Length(min=8, max=20)])

# a form using wtf for creating articles


class ArticleForm(FlaskForm):
    headline = StringField('Tiêu đề', validators=[InputRequired()])
    byline = StringField('Tác giả', validators=[InputRequired()])
    sectionsdb = sections()
    opt_Ar = []
    for i in sectionsdb:
        opt_Ar.append((i, i))

    section = SelectField(
        'Chuyên mục',
        choices=opt_Ar)
    body = TextAreaField('Nội dung', validators=[Length(min=5)])
    btn_publish = SubmitField('Xuất bản bài báo')
    btn_save = SubmitField('Lưu bản thảo')
    photo = FileField('Nhấn để chọn ảnh')
    photographer = StringField('Người chụp ảnh')
    photo_caption = TextAreaField('Tiêu đề ảnh')
    status = None


################################################################################################################
##                                           WRITER & POSTER                                                  ##
################################################################################################################

# login page for editor and writer
@app.route('/login', methods=['GET', 'POST'])
def login():
    form1 = LoginForm()
    session['offset'] = 0
    if session.get('is_login', None) is True:
        return redirect('/admin/dashboard/'+sections()[0]+'/'+str(session['offset']))
    else:
        if request.method == 'POST':
            if form1.validate_on_submit():
                username = request.form[form1.username.name]
                password = request.form[form1.password.name]
                login_data = sqlDatas(
                    "select * from users where username=%s and `status`='Kích hoạt'", username, 1)
                try:
                    if login_data is not None and login_data[2] == password:
                        session['is_login'] = True
                        session['username'] = username
                        session['current_section'] = sections()[0]
                        flash("Đăng nhập thành công! Chào mừng " +
                              username+"!", "success")
                        return redirect('/admin/dashboard/'+sections()[0]+'/'+str(session['offset']))
                except IndexError:
                    flash("Đăng nhập thất bại", "danger")
                else:
                    flash("Đăng nhập thất bại", "danger")

        return render_template('login.html', form=form1)

# creating of articles
@app.route('/admin/create/', methods=['POST', 'GET'])
def admin():
    if session.get('is_login', None) is not True:
        return redirect('/login')
    else:
        un = session.get('username', None)

        form1 = ArticleForm()
        headline = form1.headline.data
        body = form1.body.data
        byline = form1.byline.data
        section = form1.section.data
        photo_caption = form1.photo_caption.data
        photographer = form1.photographer.data
        stats = ''
        subsection = ''

        ar_count = no_of_articles()
        count_data = []
        counter = 0
        for i in sections():
            count_data.append([i, ar_count[counter]])
            counter = counter + 1

        if form1.validate_on_submit():
            if form1.btn_save.data:
                stats = 'Bản thảo'
            elif form1.btn_publish.data:
                stats = 'Đã xuất bản'

            filename = None
            pic_file = request.files[form1.photo.name]
            if pic_file:
                filename = photos.save(pic_file)

            sql_query = "INSERT INTO `articles` (`uploaded_by`, `headline`, `byline`, `body`, `section`,`photo_filename`, `photographer`, `photo_caption`, `status`, `subsection`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            vals = (un, headline, byline, body, section, filename,
                    photographer, photo_caption, stats, subsection)
            sqlExecute(sql_query, vals)
            last_id = str(sqlDatas("select last_insert_id();", None, 1)[0])

            flash("Bài báo đã được lưu! ", "success")
            return redirect(url_for('admin'))

        return render_template('create_article.html', form=form1, sec=session['current_section'], offset=session['offset'], position=position(un), FullName=FullName(un), sections=sections(), article_counts=count_data)

# dashboard
@app.route('/admin/dashboard/<name>/<offset>', methods=['GET', 'POST'])
def admin_dashboard(name, offset):
    if session.get('is_login', None) is not True:
        return redirect('/login')
    else:
        un = session.get('username', None)
        total = sqlDatas(
            "select count(*) from articles where section=%s", name, 1)[0]
        pos = position(un)

        if int(offset) == 0:
            session['offset'] = 0

        newb = None
        oldb = None

        if int(offset) < 5:
            newb = 'disabled'
        elif int(offset) >= total-5:
            oldb = 'disabled'

        ar_count = no_of_articles()
        count_data = []
        counter = 0
        for i in sections():
            count_data.append([i, ar_count[counter]])
            counter = counter + 1

        drafts = sqlDatas(
            "select count(*) from articles where section=%s and status='Bản thảo'", name, 1)[0]
        published = sqlDatas(
            "select count(*) from articles where section=%s and status='Đã xuất bản'", name, 1)[0]

        article_data = sqlDatas(
            "select * from articles where section=%s order by last_edited desc limit 5 offset "+str(offset), name, None)
        article_data_list = []
        for i in article_data:
            i[10] = pretty_date(i[10])
            i[4] = str(BeautifulSoup(i[4], "lxml").text)
            if i[1] == un and i[9] == "Bản thảo":
                i.append(True)
            else:
                i.append(False)
            article_data_list.append(i)

        return render_template('articles.html', sections=sections(), articles=article_data_list, sec=name, offset=offset, newb=newb, oldb=oldb, article_counts=count_data, draft=drafts, published=published, position=pos, FullName=FullName(un))

# read article
@app.route('/admin/article/read/<article_id>', methods=['GET', 'POST'])
def admin_readmore(article_id):
    if session.get('is_login', None) is not True:
        return redirect('/login')
    else:
        un = session.get('username', None)
        article = sqlDatas(
            "select * from articles where id_article=%s", article_id, 1)
        article[10] = myDate(article[10])

        hasAccess = None

        if position(un) == "Biên tập" or (article[1] == un and article[9] == "Bản thảo"):
            hasAccess = True

        ar_count = no_of_articles()
        count_data = []
        counter = 0
        for i in sections():
            count_data.append([i, ar_count[counter]])
            counter = counter + 1

        return render_template('read_article.html', article=article, sections=sections(), FullName=FullName(un), article_counts=count_data, sec=sections()[0], hasAccess=hasAccess, position=position(un))

# editing of article
@app.route('/admin/article/edit/<article_id>', methods=['GET', 'POST'])
def admin_edit(article_id):
    if session.get('is_login', None) is not True:
        return redirect('/login')
    else:
        un = session.get('username', None)

        article = sqlDatas(
            "select * from articles where id_article=%s", article_id, 1)

        if position(un) == "Biên tập" or (article[1] == un and article[9] == "Bản thảo"):
            article = sqlDatas("select * from articles where id_article=%s", article_id, 1)
            form1 = ArticleForm()
            form1.headline.data = article[2]
            form1.body.data = article[4]
            form1.byline.data = article[3]
            form1.section.data = article[5]
            form1.photo_caption.data = article[8]
            form1.photographer.data = article[7]
            stats = article[9]

            ar_count = no_of_articles()
            count_data = []
            counter = 0
            for i in sections():
                count_data.append([i, ar_count[counter]])
                counter = counter + 1

            if form1.validate_on_submit():
                if form1.btn_save.data:
                    stats = 'Bản thảo'
                elif form1.btn_publish.data:
                    stats = 'Đã xuất bản'

                headline = request.form[form1.headline.name]
                byline = request.form[form1.byline.name]
                section = request.form[form1.section.name]
                body = request.form[form1.body.name]
                photo_caption = request.form[form1.photo_caption.name]
                photographer = request.form[form1.photographer.name]

                filename = None
                pic_file = request.files[form1.photo.name]
                if pic_file:
                    filename = photos.save(pic_file)
                else:
                    filename = article[6]

                sql_query = "UPDATE `articles` SET `headline`=%s, `byline`=%s,`body`=%s,`section`=%s, `photo_filename`=%s, `photographer`=%s, `photo_caption`=%s, `status`=%s WHERE (`id_article` = %s);"
                vals = (headline, byline, body, section, filename,
                        photographer, photo_caption, stats, article[0])
                sqlExecute(sql_query, vals)

                flash("Bài báo đã được chỉnh sửa!", "success")
                return redirect('/admin/article/edit/'+str(article[0]))

        else:
            return redirect("/admin/dashboard/"+sections()[0]+"/0")

        return render_template('edit_article.html', form=form1, article=article, sec=sections()[0], FullName=FullName(un), sections=sections(), article_counts=count_data, position=position(un))

# deleting of article
@app.route('/admin/article/delete/<sec>/<article_id>', methods=['GET', 'POST'])
def admin_delete(sec, article_id):
    if session.get('is_login', None) is not True:
        return redirect('/login')
    else:
        un = session.get('username', None)

        article = sqlDatas(
            "select * from articles where id_article=%s", article_id, 1)

        # if user is Bien tap or article.upload_by = current user and article.status = Ban thao
        if position(un) == "Biên tập" or (article[1] == un and article[9] == "Bản thảo"):
            sqlExecute(
                "DELETE FROM `articles` WHERE (`id_article` = %s );", article_id)
            flash("Bài báo đã được xóa: "+article[2]+"!", "success")

        return redirect('/admin/dashboard/'+sec+'/'+str(session['offset']))

# pagination for dashboard older articles
@app.route('/admin/dashboard/<section>/older', methods=['GET', 'POST'])
def admin_older(section):
    if session.get('is_login', None) is not True:
        return redirect('/login')
    else:
        un = session.get('username', None)
        session['offset'] = session['offset'] + 5
        return redirect('/admin/dashboard/'+section+'/'+str(session['offset']))

# pagination for dashboard newer articles
@app.route('/admin/dashboard/<section>/newer', methods=['GET', 'POST'])
def admin_newer(section):
    if session.get('is_login', None) is not True:
        return redirect('/login')
    else:
        un = session.get('username', None)
        session['offset'] = session['offset'] - 5
        return redirect('/admin/dashboard/'+section+'/'+str(session['offset']))

# logout for editor/writer
@app.route('/admin/logout', methods=['GET', 'POST'])
def admin_logout():
    if session.get('is_login', None) is not True:
        return redirect('/login')
    else:
        un = session.get('username', None)
        session['is_login'] = False
        flash("You just logout!", "info")
        return redirect('/login')

# profile page of editor/writer
@app.route('/admin/account/<stats>', methods=['GET', 'POST'])
def admin_account(stats):
    if session.get('is_login', None) is not True:
        return redirect('/login')
    else:
        form = ResetPassword()
        un = session.get('username', None)
        passw = sqlDatas(
            "select password from users where username=%s", un, 1)[0]

        ar_count = no_of_articles()
        count_data = []
        counter = 0
        for i in sections():
            count_data.append([i, ar_count[counter]])
            counter = counter + 1
        user = sqlDatas("select * from users where username=%s", un, 1)
        numdraft = sqlDatas(
            "select count(*) from articles where uploaded_by=%s and `status`='Bản thảo';", un, 1)[0]
        numpub = sqlDatas(
            "select count(*) from articles where uploaded_by=%s and `status`='Đã xuất bản';", un, 1)[0]

        article_list = []
        if stats == "all":
            article_list = sqlDatas(
                "select headline, last_edited, status, id_article from articles where uploaded_by=%s order by last_edited desc", un, None)
        else:
            article_list = sqlDatas(
                "select headline, last_edited, status, id_article from articles where uploaded_by=%s and `status`=%s order by last_edited desc", (un, stats), None)

        for i in article_list:
            i[1] = myDate(i[1])

        if request.method == 'POST':
            currentP = request.form[form.currentPassword.name]
            newP = request.form[form.newPassword.name]
            reP = request.form[form.retypePassword.name]

            if currentP == passw and newP == reP:
                sqlExecute(
                    "UPDATE `users` SET `password` = %s WHERE (`username` = %s);", (newP, un))
                flash("Mật khaair đã được thay đổi!", "success")
            else:
                flash("Lỗi không thể thay đổi mật khẩu!", "danger")

            return redirect('/admin/account/all')

        return render_template('account.html', un=un, user=user, article_list=article_list, form=form, numdraft=numdraft, numpub=numpub, article_counts=count_data, FullName=FullName(un), sec=sections()[0], sections=sections())

# searching of data
@app.route('/admin/search/<query>', methods=['GET', 'POST'])
def admin_search(query):
    if session.get('is_login', None) is not True:
        return redirect('/login')
    else:
        un = session.get('username', None)

        ar_count = no_of_articles()
        count_data = []
        counter = 0
        for i in sections():
            count_data.append([i, ar_count[counter]])
            counter = counter + 1

        sql_query = "SELECT * FROM articles where headline like %s or byline like %s or body like %s or section like %s or photo_filename like %s or photographer like %s or photo_caption like %s or `status` like %s or last_edited like %s order by last_edited desc"
        sval = "%" + query + "%"
        vals = (sval, sval, sval, sval, sval, sval, sval, sval, sval)

        article_list = sqlDatas(sql_query, vals, None)
        for i in article_list:
            i[10] = myDate(i[10])

        sql_query_draft = "SELECT count(*) FROM articles where (headline like %s or byline like %s or body like %s or section like %s or photo_filename like %s or photographer like %s or photo_caption like %s or `status` like %s or last_edited like %s) and `status`='Bản thảo'"
        sval_draft = "%" + query + "%"
        vals_draft = (sval_draft, sval_draft, sval_draft, sval_draft,
                      sval_draft, sval_draft, sval_draft, sval_draft, sval_draft)

        draft = sqlDatas(sql_query_draft, vals_draft, 1)[0]

        sql_query_published = "SELECT count(*) FROM articles where `status`='Đã xuất bản' and (headline like %s or byline like %s or body like %s or section like %s or photo_filename like %s or photographer like %s or photo_caption like %s or `status` like %s or last_edited like %s)"
        sval_published = "%" + query + "%"
        vals_published = (sval_published, sval_published, sval_published, sval_published,
                          sval_published, sval_published, sval_published, sval_published, sval_published)

        published = sqlDatas(sql_query_published, vals_published, 1)[0]

        return render_template('articles_search.html', article_list=article_list, search=query, sec=sections()[0], article_counts=count_data, FullName=FullName(un), sections=sections(), draft=draft, published=published)

# dashboard for categorized articles -draft or published
@app.route('/admin/dashboard/<name>/<stats>/<offset>', methods=['GET', 'POST'])
def admin_dashboard_stats(name, offset, stats):
    if session.get('is_login', None) is not True:
        return redirect('/login')
    else:
        un = session.get('username', None)
        total = sqlDatas(
            "select count(*) from articles where section=%s and `status`=%s", (name, stats), 1)[0]

        if int(offset) == 0:
            session['offset'] = 0

        pos = position(un)
        newb = None
        oldb = None

        if int(offset) < 5:
            newb = 'disabled'
        elif int(offset) >= total-5:
            oldb = 'disabled'

        ar_count = no_of_articles()
        count_data = []
        counter = 0
        for i in sections():
            count_data.append([i, ar_count[counter]])
            counter = counter + 1

        drafts = sqlDatas(
            "select count(*) from articles where section=%s and status='Bản thảo'", name, 1)[0]
        published = sqlDatas(
            "select count(*) from articles where section=%s and status='Đã xuất bản'", name, 1)[0]

        vals = (name, stats)
        article_data = sqlDatas(
            "select * from articles where section=%s and status=%s order by last_edited desc limit 5 offset "+str(offset), vals, None)
        article_data_list = []
        for i in article_data:
            i[4] = str(BeautifulSoup(i[4], "lxml").text)
            i[10] = pretty_date(i[10])
            if i[1] == un and i[9] == "Bản thảo":
                i.append(True)
            else:
                i.append(False)

            article_data_list.append(i)

        return render_template('articles_status.html', sections=sections(), articles=article_data_list, sec=name, offset=offset, newb=newb, oldb=oldb, article_counts=count_data, draft=drafts, published=published, stats=stats, position=pos, FullName=FullName(un))

# pagination for categorized article - older
@app.route('/admin/dashboard/<section>/<stats>/older', methods=['GET', 'POST'])
def admin_stats_older(section, stats):
    if session.get('is_login', None) is not True:
        return redirect('/login')
    else:
        un = session.get('username', None)
        session['offset'] = session['offset'] + 5
        return redirect('/admin/dashboard/'+section+'/'+stats+'/'+str(session['offset']))


# pagination for categorized article - newer
@app.route('/admin/dashboard/<section>/<stats>/newer', methods=['GET', 'POST'])
def admin_stats_newer(section, stats):
    if session.get('is_login', None) is not True:
        return redirect('/login')
    else:
        un = session.get('username', None)
        session['offset'] = session['offset'] - 5
        return redirect('/admin/dashboard/'+section+'/'+stats+'/'+str(session['offset']))

################################################################################################################
##                                           VIEWER                                                           ##
################################################################################################################
@app.route('/', methods=['GET', 'POST']) #trang chu
def index():
    sections1 = sections()
    subData = [] #lay cac bai bao ra goc man hinh
    for section in sections1:
        data = sqlDatas(
            "select * from articles WHERE section=%s and `status`='Đã xuất bản' order by last_edited desc;", section, 1)
        if data is not None:
            data[10] = pretty_date(data[10])
            subData.append(data)
    hd = [] #lay cac bai bao o giua man hinh
    homeData = sqlDatas(
        "select * from articles where status='Đã xuất bản' order by last_edited desc limit 5;", None, None)
    for data in homeData:
        data[4] = str(BeautifulSoup(data[4], "lxml").text)
        data[10] = pretty_date(data[10])
        hd.append(data)

    if request.method == "POST":
        search = request.form["search"]
        return redirect("/search/"+search)

    return render_template('newspaper/index.html', sections=sections1, subdata=subData, homedata=hd, active="active")

# viewer part sections : xem bao theo chuyen muc
@app.route('/<sectionshere>/<offset>', methods=['GET', 'POST'])
def index_section(sectionshere, offset):
    if int(offset) == 0: #lay ra so luong bai bao de chia ra tung trang
        session['index_offset'] = 0

    total = sqlDatas(
        "select count(*) from articles where section=%s and `status`='Đã xuất bản'", sectionshere, 1)[0]

    newer = ""
    older = ""
    if int(offset) < 5:
        newer = 'disabled'
    if int(offset) >= total-5:
        older = 'disabled'

    # category in the side
    sections1 = sections()  # navigation
    subData = []
    for section in sections1:
        data = sqlDatas(
            "select * from articles WHERE section=%s and `status`='Đã xuất bản' order by last_edited desc;", section, 1)
        if data is not None:
            data[10] = pretty_date(data[10])
            subData.append(data)

    hd = []
    homeData = sqlDatas("select * from articles where section=%s and `status`='Đã xuất bản' order by last_edited desc limit 5 offset " +
                        str(session['index_offset']), sectionshere, None)
    for data in homeData:
        data[4] = str(BeautifulSoup(data[4], "lxml").text)
        data[10] = pretty_date(data[10])
        hd.append(data)

    if request.method == "POST":
        search = request.form["search"]
        return redirect("/search/"+search)

    return render_template('newspaper/section.html', sections=sections1, subdata=subData, homedata=hd, section_=sectionshere, older=older, newer=newer, active="active")

# viewer part pagination : chuyen giua cac trang trong chuyen muc ( older -> nhay len / newer -> tru di)
@app.route('/<sectionshere>/go/<dowhat>', methods=['GET', 'POST'])
def index_section_go(sectionshere, dowhat):
    if dowhat == "older":
        session['index_offset'] = session['index_offset'] + 5
    elif dowhat == "newer":
        session['index_offset'] = session['index_offset'] - 5

    return redirect("/"+sectionshere+"/"+str(session['index_offset']))

# viewer part read more : xem chi tiet bai bao
@app.route('/read/<sectionshere>/<article_id>/<article_headline>', methods=['GET', 'POST'])
def index_read(sectionshere, article_id, article_headline):
    # category in the side
    sections1 = sections()  # navigation
    subData = []
    for section in sections1:
        data = sqlDatas(
            "select * from articles WHERE section=%s and `status`='Đã xuất bản' order by last_edited desc;", section, 1)
        if data is not None:
            data[10] = pretty_date(data[10])
            subData.append(data)

    hd = sqlDatas("select * from articles where id_article=%s", article_id, 1) #chi hien thi duy nhat 1 bai bao/ la bai bai bao vua nhan vao
    hd[10] = pretty_date(hd[10])

    if request.method == "POST":
        search = request.form["search"]
        return redirect("/search/"+search)

    return render_template('newspaper/read.html', sections=sections1, subdata=subData, homedata=hd, section_=sectionshere)

# viewer search : tim kiem
@app.route('/search/<search>', methods=['GET', 'POST'])
def index_search(search):
    # category in the side
    sections1 = sections()  # navigation
    subData = []
    for section in sections1:
        data = sqlDatas(
            "select * from articles WHERE section=%s and `status`='Đã xuất bản' order by last_edited desc;", section, 1)
        if data is not None:
            data[10] = pretty_date(data[10])
            subData.append(data)

#cau lenh query -> 
# %s la bien minh truyen vao
    sql_query = "SELECT * FROM articles where headline like %s or byline like %s or body like %s or section like %s or photo_filename like %s or photographer like %s or photo_caption like %s or last_edited like %s order by last_edited desc"
    sval = "%" + search + "%"
    vals = (sval, sval, sval, sval, sval, sval, sval, sval)
    results = sqlDatas(sql_query, vals, None)
    result = []
    for hd in results:
        hd[10] = pretty_date(hd[10])
        result.append(hd)

    if request.method == "POST":
        search = request.form["search"]
        return redirect("/search/"+search)

    return render_template('newspaper/search.html', sections=sections1, subdata=subData, results=result, searchMo=search)

# viewer part contact page
@app.route('/contact', methods=['GET', 'POST'])
def index_contact():
    sections1 = sections()
    subData = []
    for section in sections1:
        data = sqlDatas(
            "select * from articles WHERE section=%s and `status`='Đã xuất bản' order by last_edited desc;", section, 1)
        if data is not None:
            data[10] = pretty_date(data[10])
            subData.append(data)

    if request.method == "POST" and "search" in request.form:
        search = request.form["search"]
        return redirect("/search/"+search)

    return render_template('newspaper/contact.html', sections=sections1, subdata=subData)


################################################################################################################
##                                           ADMIN                                                            ##
################################################################################################################
dbPassword = "admin"

# login page for the db admin
@app.route('/admin/login', methods=['GET', 'POST'])
def dblogin():
    if request.method == "POST":
        passw = request.form["password"]
        if passw == dbPassword:
            session["dblogin"] = True
            return redirect("/admin")
        else:
            session["dblogin"] = False
            flash("Login Failed", "danger")
    return render_template('admin_login.html')

# home page for db admin
@app.route('/admin', methods=['GET', 'POST'])
def dbhome():
    if session['dblogin']:
        data = sqlDatas("select * from users", None, None)
        sec = sqlDatas("select * from sections", None, None)
        return render_template('admin.html', data=data, sections=sec)
    else:
        return redirect("/admin/login")

# updating of user
@app.route('/admin/user/update/<id>', methods=['GET', 'POST'])
def dbedituser(id):
    if session['dblogin']:
        if request.method == "POST":
            name = request.form["name"]
            password = request.form["password"]
            position = request.form["position"]
            sqlExecute("UPDATE users set `name`=%s, `password`=%s, `position`=%s WHERE (`id_user`=%s)",
                       (name, password, position, id))
            flash("Thông tin người dùng đã cập nhật!", "success")
            return redirect('/admin')
    else:
        return redirect("/admin/login")

# disabling/enabling of user
@app.route('/admin/user/<id>/<stats>', methods=['GET', 'POST'])
def dbedituserstats(id, stats):
    if session['dblogin']:
        sqlExecute(
            "UPDATE users set `status`=%s WHERE (`id_user`=%s)", (stats, id))
        flash("Trạng thái đã cập nhật!", "success")
        return redirect('/admin')
    else:
        return redirect("/admin/login")

# removing of user
@app.route('/admin/user/<id>/delete', methods=['GET', 'POST'])
def dbdeleteuser(id):
    if session['dblogin']:
        if request.method == "POST":
            sqlExecute("delete from users WHERE (`id_user`=%s)", (id))
            flash("Người dùng đã được xóa!", "success")
            return redirect('/admin')
    else:
        return redirect("/admin/login")

# searchng of user account
@app.route('/admin/user/search', methods=['GET', 'POST'])
def dbsearchuser():
    if session['dblogin']:
        if request.method == "POST":
            query = request.form["search"]
            sval = "%" + query + "%"
            data = sqlDatas(
                "select * from users where username like %s or name like %s", (sval, sval), None)
            sec = sqlDatas("select * from sections", None, None)
            return render_template('admin.html', data=data, sections=sec)
    else:
        return redirect("/admin/login")

# adding of user account
@app.route('/admin/user/add', methods=['GET', 'POST'])
def dbadduser():
    if session['dblogin']:
        if request.method == "POST":
            username = request.form["Username"]
            name = request.form["name"]
            password = request.form["password"]
            position = request.form["position"]
            taken = sqlDatas(
                "select count(*) from users where username=%s", username, 1)[0]
            if len(name) < 1 and len(username) < 1:
                flash("Thiếu thông tin người dùng!", "info")
            elif len(password) < 8:
                flash("Mật khẩu phải có nhiều hơn 8 kí tự!", "info")
            elif taken > 0:
                flash("Tên đăng nhập: "+username+" đã tồn tại!", "info")
            else:
                sqlExecute("INSERT into users (`username`,`password`,`position`, `name`, `status`) VALUES(%s,%s,%s,%s,'Kích hoạt');",
                           (username, password, position, name))
                flash("Đã thêm người dùng!", "success")

        return redirect('/admin')
    else:
        return redirect("/admin/login")

# updating of sections
@app.route('/admin/section/update/<id>', methods=['GET', 'POST'])
def dbeditsection(id):
    if session['dblogin']:
        if request.method == "POST":
            name = request.form["sectionname"]
            if len(name) < 1:
                flash("Tên chuyên mục không được để trống!", "info")
            else:
                taken = sqlDatas(
                    "select count(*) from sections where name=%s", name, 1)[0]
                if taken > 0:
                    flash("Chuyên mục đã tồn tại!", "info")
                else:
                    sqlExecute(
                        "UPDATE sections set `name`=%s WHERE (`id_section`=%s)", (name, id))
                    flash("Chuyên mục đã được cập nhật!", "success")
            return redirect('/admin')
    else:
        return redirect("/admin/login")

# removing of sections
@app.route('/admin/section/delete/<id>', methods=['GET', 'POST'])
def dbdeletesection(id):
    if session['dblogin']:
        if request.method == "POST":
            sqlExecute("delete from sections WHERE (`id_section`=%s)", (id))
            flash("Chuyên mục đã được xóa!", "success")
            return redirect('/admin')
    else:
        return redirect("/admin/login")

# adding of sections
@app.route('/admin/section/add', methods=['GET', 'POST'])
def dbaddsection():
    if session['dblogin']:
        if request.method == "POST":
            name = request.form["sectionname"]
            if len(name) < 1:
                flash("Tên chuyên mục không được để trống!", "info")
            else:
                taken = sqlDatas(
                    "select count(*) from sections where name=%s", name, 1)[0]
                if taken > 0:
                    flash("Chuyên mục đã tồn tại!", "info")
                else:
                    sqlExecute(
                        "INSERT into sections (`name`) VALUES(%s)", name)
                    flash("Chuyên mục đã được thêm!", "success")
            return redirect('/admin')
    else:
        return redirect("/admin/login")

# db admin logout
@app.route('/admin/logout', methods=['GET', 'POST'])
def dblogout():
    session['dblogin'] = False
    return redirect("/admin/login")


if __name__ == "__main__":
    app.secret_key = '1234567890'
   #app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
