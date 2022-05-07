from flask import Flask, render_template, request, session, redirect, flash
from flask_bootstrap import Bootstrap
from flask_uploads import IMAGES, UploadSet, configure_uploads

from model import *
from form import LoginForm, ArticleForm, ResetPasswordForm

app = Flask(__name__)
Bootstrap(app)

# photo upload
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

####################################################################################################################
#
#                                             VIEWER                                                                
#
####################################################################################################################

#Homepage
@app.route('/', methods=['GET'])
def index():
    sections = Section.get_all()
    main_articles = Article.get_by(1,None,"Xuất bản")
    side_articles = Article.get_sidepage()
    return render_template('newspaper/index.html', sections=sections, homedata=main_articles, subdata=side_articles)

#View articles by section
@app.route('/Chuyên mục/<section_name>/<id_section>/<offset>', methods=['GET'])
def view_articles_by_section(section_name,id_section,offset):
    offset = int(offset)
    sections = Section.get_all()
    main_articles = Article.get_by(offset,int(id_section),"Xuất bản")
    side_articles = Article.get_sidepage()

    newer = offset+1
    older = offset-1
    if int(offset) == 1:
        older = "disabled"
    if int(offset) >= Article.count_section(id_section)/5:
        newer = "disabled"
    return render_template('newspaper/section.html',section_name=section_name, id_section=id_section, older=older, newer=newer, sections=sections, homedata=main_articles, subdata=side_articles)

#Read an article
@app.route('/<section_name>/<id_articles>/<headline>', methods=['GET'])
def read_article(section_name, id_articles, headline):
    sections = Section.get_all()
    article = Article.read(id_articles)
    side_articles = Article.get_sidepage()
    return render_template('newspaper/read.html',homedata=article, section_name=section_name, headline=headline, subdata=side_articles, sections=sections)

#Search articles
@app.route('/Tìm kiếm/', methods=['GET'])
def search_articles():
    content = request.args.get('content')
    sections = Section.get_all()
    side_articles = Article.get_sidepage()
    main_articles = Article.search(content)
    return render_template('newspaper/search.html',homedata=main_articles, headline=content, subdata=side_articles, sections=sections)


####################################################################################################################
#
#                                             DASHBOARD                                                            
#
####################################################################################################################

#Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if request.method == 'GET':
        if "username" in session:
            return redirect('/dashboard/articles/page/1')
        else:
            return render_template('login.html', form=login_form)

    if request.method == 'POST':
        if login_form.validate_on_submit():
            username = request.form[login_form.username.name]
            password = request.form[login_form.password.name]
            if User.check(username,password):
                session['username'] = username
                session['position'] = User.get_by_username(username)['position']
                flash("Đăng nhập thành công! Chào mừng " + username+"!", "success")
                return redirect('/dashboard/articles/page/1')

        flash("Đăng nhập thất bại", "danger")
        return render_template('login.html', form=login_form)

#Dashboard - main page
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if "username" in session:
        return redirect('/dashboard/articles/page/1')
    else:
        return redirect('/login')

#Dashboard - all articles
@app.route('/dashboard/articles/page/<offset>', methods=['GET'])
def articles(offset):
    if "username" in session:
        username = session.get('username', None)
        user = User.get_by_username(username)
        number_of_total_articles = Article.count_all()
        number_of_published_articles = Article.select().where(Article.status == "Xuất bản").count()
        number_of_draft_articles = number_of_total_articles - number_of_published_articles
        sections = Section.get_all()
        for section in sections:
            section['count'] = Article.select().where(Article.id_section == section['id_section']) .count()
        articles = Article.get_by(int(offset))
        older = str(int(offset) - 1)
        newer = str(int(offset) + 1)    
        if int(offset) == 1:
            older = "disabled"
        if int(offset) >= number_of_total_articles/5:
            newer = "disabled"
        link = ["",""]
        return render_template('articles.html', title="Tổng quát", link=link, sections=sections, articles=articles, offset=offset, newb=newer, oldb=older, draft=number_of_draft_articles, published=number_of_published_articles, user=user)

    else:
        return redirect('/login')

#Dashboard - articles by section
@app.route('/dashboard/articles/sections/<section>/page/<offset>',methods=['GET'])
def articles_section(section,offset):
    if "username" in session:
        username = session.get('username', None)
        user = User.get_by_username(username)
        number_of_total_articles = Article.select().where(Article.id_section == section).count()
        number_of_published_articles = Article.select().where((Article.id_section == section) & (Article.status == "Xuất bản")).count()
        number_of_draft_articles = number_of_total_articles - number_of_published_articles
        sections = Section.get_all()
        for i in sections:
            i['count'] = Article.select().where(Article.id_section == i['id_section']) .count()
        articles = Article.get_by(int(offset), int(section), None)
        older = str(int(offset) - 1)
        newer = str(int(offset) + 1)    
        if int(offset) == 1:
            older = "disabled"
        if int(offset) >= number_of_total_articles/5:
            newer = "disabled"
        tilte = Section[int(section)].name
        link = ["/sections/" + section,""]
        return render_template('articles.html', title=tilte, link=link, sections=sections, articles=articles, offset=offset, newb=newer, oldb=older, draft=number_of_draft_articles, published=number_of_published_articles, user=user)

    else:
        return redirect('/login')

#Dashboard - articles by status
@app.route('/dashboard/articles/status/<status>/page/<offset>',methods=['GET'])
def articles_status(status,offset):
    if "username" in session:
        username = session.get('username', None)
        user = User.get_by_username(username)
        number_of_total_articles = Article.count_all()
        number_of_published_articles = Article.select().where(Article.status == "Xuất bản").count()
        number_of_draft_articles = number_of_total_articles - number_of_published_articles
        sections = Section.get_all()
        for section in sections:
            section['count'] = Article.select().where(Article.id_section == section['id_section']) .count()
        articles = Article.get_by(int(offset), None, status)
        older = str(int(offset) - 1)
        newer = str(int(offset) + 1)    
        if int(offset) == 1:
            older = "disabled"
        if int(offset) >= Article.select().where(Article.status == status).count()/5:
            newer = "disabled"
        link = ["","/status/" + status]
        return render_template('articles.html', title="Tổng quát", link=link, sections=sections, articles=articles, offset=offset, newb=newer, oldb=older, draft=number_of_draft_articles, published=number_of_published_articles, user=user)

    else:
        return redirect('/login')


#Dashboard - articles by section and status
@app.route('/dashboard/articles/sections/<section>/status/<status>/page/<offset>',methods=['GET'])
def articles_section_status(section,status,offset):
    if "username" in session:
        username = session.get('username', None)
        user = User.get_by_username(username)
        number_of_total_articles = Article.select().where(Article.id_section == section).count()
        number_of_published_articles = Article.select().where((Article.id_section == section) & (Article.status == "Xuất bản")).count()
        number_of_draft_articles = number_of_total_articles - number_of_published_articles
        sections = Section.get_all()
        for i in sections:
            i['count'] = Article.select().where(Article.id_section == i['id_section']) .count()
        articles = Article.get_by(int(offset),int(section),status)
        older = str(int(offset) - 1)
        newer = str(int(offset) + 1)    
        if int(offset) == 1:
            older = "disabled"
        if int(offset) >= Article.select().where((Article.id_section == section) & (Article.status == status)).count()/5:
            newer = "disabled"
        tilte = Section[int(section)].name
        link = ["/sections/" + section,"/status/" + status]
        return render_template('articles.html', title=tilte, link=link, sections=sections, articles=articles, offset=offset, newb=newer, oldb=older, draft=number_of_draft_articles, published=number_of_published_articles, user=user)

    else:
        return redirect('/login')

@app.route('/dashboard/articles/read/<id_article>', methods = ['GET'])
def article_read(id_article):
    if "username" in session:
        username = session.get('username', None)
        user = User.get_by_username(username)
        sections = Section.get_all()
        for i in sections:
            i['count'] = Article.select().where(Article.id_section == i['id_section']) .count()
        article = Article.read(id_article)
        return render_template('read_article.html',  user=user, sections=sections, article=article)
    else:
        return redirect('/login')

# Create article
@app.route('/dashboard/articles/create', methods = ['GET','POST'])
def article_create():
    if "username" in session:
        username = session.get('username', None)
        user = User.get_by_username(username)
        sections = Section.get_all()
        for i in sections:
            i['count'] = Article.select().where(Article.id_section == i['id_section']) .count()
        form = ArticleForm()
        form.section.choices = [(section['id_section'], section['name']) for section in Section.get_all()]
            
        if request.method == 'POST':
            headline = form.headline.data
            body = form.body.data
            byline = form.byline.data
            section = form.section.data
            stats = ''
            if form.validate_on_submit():
                if form.btn_save.data:
                    stats = 'Bản thảo'
                elif form.btn_publish.data:
                    stats = 'Xuất bản'
            
                filename = None
                pic_file = request.files[form.photo.name]
                if pic_file:
                    filename = photos.save(pic_file)

                print(section,user['id_user'],byline,headline,body,filename,stats)
                Article.add(section,user['id_user'],byline,headline,body,filename,stats)
                flash("Thêm bài báo thành công! ", "success")
            else:
                flash("Thêm bài báo thất bại! ", "danger")
        return render_template('create_article.html',  user=user, sections=sections, form=form)
    else:
        return redirect('/login')

# Edit an article or delete it
@app.route('/dashboard/articles/edit/<id_article>', methods = ['GET', 'POST'])
def article_modify(id_article):
    if "username" in session:
        username = session.get('username', None)
        user = User.get_by_username(username)
        sections = Section.get_all()
        article = Article.read(id_article)
        for i in sections:
            i['count'] = Article.select().where(Article.id_section == i['id_section']) .count()

        if user['position'] != "Biên soạn" or (article['id_poster'] == user['id_user'] and article['status'] == "Bản thảo"):
            form1 = ArticleForm()
            form1.headline.data = article['headline']
            form1.body.data = article['body']
            form1.byline.data = article['byline']
            form1.section.data = article['id_section']
            form1.section.choices = [(section['id_section'], section['name']) for section in Section.get_all()]
            stats = article['status']

            if request.method == 'POST':
                if form1.validate_on_submit():
                    if form1.btn_save.data:
                        stats = 'Bản thảo'
                    elif form1.btn_publish.data:
                        stats = 'Xuất bản'

                    headline = request.form[form1.headline.name]
                    byline = request.form[form1.byline.name]
                    section = request.form[form1.section.name]
                    body = request.form[form1.body.name]

                    filename = None
                    pic_file = request.files[form1.photo.name]
                    if pic_file:
                        filename = photos.save(pic_file)
                    else:
                        filename = article['photo']

                    print(Article.set(id_article, section, byline, headline, body, filename, stats))
                    print(id_article, section, byline, headline, body, filename, stats)
                    
                    flash("Chỉnh sửa bài báo thành công!", "success")
                    return redirect('/dashboard/articles/edit/'+id_article)
                
                else:
                    flash("Chỉnh sửa bài báo thật bại!", "danger")

            return render_template("edit_article.html", user=user, sections=sections, form=form1, article=article)
        
        else:
            flash("Người dùng không có quyền truy cập", "danger")
            return redirect('/login')
    
    else:
        return redirect('/login')


#Delete an article
@app.route('/dashboard/articles/delete/<id_article>', methods = ['POST'])
def article_delete(id_article):
    if "username" in session:
        username = session.get('username', None)
        if Article.remove(id_article):
            flash("Xóa bài báo thành công!", "success")
            
        else:
            flash("Xóa bài báo thật bại!", "danger")
        return redirect("/dashboard/articles/page/1")

    else:
        return redirect('/login')       

#Search articles
@app.route('/dashboard/articles/search/', methods = ['GET'])
def articles_search():
    if "username" in session:
        username = session.get('username', None)
        user = User.get_by_username(username)
        sections = Section.get_all()
        for i in sections:
            i['count'] = Article.select().where(Article.id_section == i['id_section']) .count()

        content = request.args.get('content')
        article = Article.search(content,None)
        return render_template('search_articles.html',user=user, sections=sections, article_list=article, content=content)

    else:
        return redirect('/login')      

#Profile page, view user information, posts and change password
@app.route('/dashboard/profile', methods = ['GET','POST'])
def profile():
    if "username" in session:
        username = session.get('username', None)
        user = User.get_by_username(username)
        form = ResetPasswordForm()
        sections = Section.get_all()
        for i in sections:
            i['count'] = Article.select().where(Article.id_section == i['id_section']) .count()

        articles = Article.get_user(user['id_user'])

        if request.method == 'POST':
            print("Biểu mẫu: ",form.validate_on_submit())
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    print(err)
            if form.validate_on_submit():
                old_password = request.form[form.currentPassword.name]
                new_password = request.form[form.newPassword.name]
                Updated = User.set_password(user['id_user'], old_password, new_password)
                print(Updated)
                if Updated>0:
                    flash("Cập nhật mật khẩu thành công!", "success")
                else:
                    flash("Cập nhật mật khẩu thật bại! Mật khẩu cũ không đúng", "danger")
            else:
                flash("Cập nhật mật khẩu thật bại! Các trường nhập vào không hợp lệ", "danger")

        return render_template('profile.html',user=user, sections=sections,  article_list=articles, form=form)
    else:
        return redirect('/login')      


#Section management - Retrieve
@app.route('/dashboard/sections', methods = ['GET'])
def sections_view():
    if "username" in session and session['position'] == "Quản trị":
        username = session.get('username', None)
        user = User.get_by_username(username)
        sections = Section.get_all()
        return render_template('sections.html', user=user, sections=sections)
    else:
        return redirect('/login')      

#Section management - Create
@app.route('/dashboard/sections', methods = ['POST'])
def section_create():
    if "username" in session and session['position'] == "Quản trị":
        section_name = request.form["sectionname"]
        Section.add(section_name)
        flash("Thêm chuyên mục thành công!","success")
            
        return redirect('/dashboard/sections')
    else:
        return redirect('/login')      

#Section management - Delete
@app.route('/dashboard/sections/<id_section>/delete', methods = ['POST'])
def section_delete(id_section):
    if "username" in session and session['position'] == "Quản trị":
        if Section.remove(id_section):
            flash("Xóa chuyên mục thành công!","success")
        else:
            flash("Xóa chuyên mục thất bại!","danger")

        return redirect('/dashboard/sections')
    else:
        return redirect('/login')      


#Section management - Update
@app.route('/dashboard/sections/<id_section>/update', methods = ['POST'])
def section_update(id_section):
    if "username" in session and session['position'] == "Quản trị":
        section_name = request.form["sectionname"]
        if Section.set(id_section,section_name):
            flash("Cập nhật chuyên mục thành công!","success")
        else:
            flash("Cập nhật chuyên mục thất bại!","danger")

        return redirect('/dashboard/sections')
    else:
        return redirect('/login')



#user management - Retrieve
@app.route('/dashboard/users', methods = ['GET'])
def users_view():
    if "username" in session and session['position'] == "Quản trị":
        username = session.get('username', None)
        user = User.get_by_username(username)
        users = User.get_all()
        for i in users:
            print(i)
        return render_template('users.html', user=user, users=users)
    else:
        return redirect('/login')      

#user management - Create
@app.route('/dashboard/users', methods = ['POST'])
def user_create():
    if "username" in session and session['position'] == "Quản trị":
        username = request.form["username"]
        password = request.form["password"]
        name = request.form["name"]
        position = request.form["position"]

        if User.add(username,password,name,position):
            flash("Thêm người dùng thành công!","success")
        else:
            flash("Thêm người dùng thất bại!","danger")
            
        return redirect('/dashboard/users')
    else:
        return redirect('/login')      

#user management - Delete
@app.route('/dashboard/users/<id_user>/delete', methods = ['POST'])
def user_delete(id_user):
    if "username" in session and session['position'] == "Quản trị":
        if User.remove(id_user):
            flash("Xóa người dùng thành công!","success")
        else:
            flash("Xóa người dùng thất bại!","danger")

        return redirect('/dashboard/users')
    else:
        return redirect('/login')      


#user management - Update
@app.route('/dashboard/users/<id_user>/update', methods = ['POST'])
def user_update(id_user):
    if "username" in session and session['position'] == "Quản trị":
        password = request.form["password"]
        name = request.form["name"]
        position = request.form["position"]
        status = request.form["status"]
        if User.set(id_user, password, name, position, status):
            flash("Cập nhật người dùng thành công!","success")
        else:
            flash("Cập nhật người dùng thất bại!","danger")

        return redirect('/dashboard/users')
    else:
        return redirect('/login')


#Logout Dashboard
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect('/login')


if __name__ == "__main__":
    app.secret_key = '1234567890'
   #app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
