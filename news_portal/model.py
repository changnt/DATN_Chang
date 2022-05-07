from datetime import datetime
from urllib.request import urlretrieve
import requests
from bs4 import BeautifulSoup
import os
from peewee import *

#covert date time string to time ago string (Ex: 2022-04-30 08:57:35 will be 10 phút trước)
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
        return str(int(day_diff / 7)) + " tuần trước"
    if day_diff < 365:
        return str(int(day_diff / 30)) + " tháng trước"
    return str(int(day_diff / 365)) + " năm trước"


db = MySQLDatabase('news_portal_mobio', host='localhost',
                   user='chang', password='12345678')


class User(Model):
    id_user = AutoField(primary_key=True)
    username = TextField()
    password = TextField()
    name = TextField()
    position = TextField()
    status = TextField()

    class Meta:
        database = db
        db_table = 'users'
        table_settings = ['ENGINE=InnoDB', 'DEFAULT CHARSET=utf8']

    #check user login
    #warning: username and password are case insensitive
    def check(_username,_password):
        try:
            user_status = User.get((User.username == _username) & (User.password == _password)).status
            if user_status == "Kích hoạt": return True
            else: return False
        except DoesNotExist:
            return False

    #get user's position
    def get_by_username(_username):
        user = User.select().where(User.username == _username).dicts()
        if len(user) > 0:
            return user[0]
        else:
            return None

    #get a user
    def get_by_id(_id_user):
        user = User.select().where(User.id_user == _id_user).dicts()
        if len(user) > 0:
            return user[0]
        else:
            return None

    #get all users
    def get_all():
        return User.select().dicts()

    #create a user
    def add(_username, _password, _name, _position, _status = 'Kích hoạt'):
        try:
            User.create(username = _username, password = _password, name = _name, position = _position, status = _status)
            return True
        except:
            return False

    #change user password
    #WARNING: does not return error when not find object
    #WARNING: password can be set to empty
    def set_password(_id_user,_old_password, _new_password):
        return User.update(password = _new_password,).where((User.id_user == _id_user) & (User.password == _old_password)).execute() 

    #update a user by ID
    #WARNING: does not return error when not find object
    #WARNING: any attriute can be set to empty
    def set(_id_user, _password, _name, _position, _status):
        if User.update(password = _password, name = _name, position = _position, status = _status).where(User.id_user == _id_user).execute() > 0:
            return True
        else:
            return False

    #delete a user by ID
    def remove(_id_user):
        return User.get(User.id_user == _id_user).delete_instance()


class Section(Model):
    id_section = AutoField(primary_key=True)
    name = TextField()

    class Meta:
        database = db
        db_table = 'sections'
        table_settings = ['ENGINE=InnoDB', 'DEFAULT CHARSET=utf8']

    #get all sections
    def get_all():
        return Section.select().dicts()

    #create a section
    #WARNING: can add duplicate name
    def add(_name):
        return Section.create(name = _name) 

    #update a section by id
    #WARNING: does not return error when not find object
    def set(_id_section,_name):
        return Section.update(name = _name).where(Section.id_section == _id_section).execute() 

    #delete a section by id
    def remove(_id_section):
        return Section.get(Section.id_section == _id_section).delete_instance()
    

class Article(Model):
    id_article = AutoField(primary_key=True)
    id_section = IntegerField()
    id_poster = IntegerField()
    byline = TextField()
    headline = TextField()
    body = TextField()
    photo = TextField()
    status = TextField()
    last_edited = DateTimeField()
    class Meta:
        database = db
        db_table = 'articles'
        table_settings = ['ENGINE=InnoDB', 'DEFAULT CHARSET=utf8']

    #get the number of all articles
    def count_all():
        return Article.select().count()

    #get the number of articles in selected section that are published
    def count_section(_id_section):
        return Article.select().where((Article.id_section == _id_section) & (Article.status == 'Xuất bản')).count()
    
    #read an article by ID
    def read(_id_article):
        article = Article.select().where(Article.id_article == _id_article).dicts()[0]
        article['section_name'] = Section[article['id_section']].name
        article['poster_name'] = User[article['id_poster']]['name']
        article['last_edited'] = pretty_date(article['last_edited'])
        return article

    #get up to 5 articles by section, status, page order by edited time
    #if parameter is empty, it will return all result
    def get_by(_offset, _id_section = None, _status = None, ):
        article = {}
        if _id_section is None:
            if _status is None: 
                articles = Article.select().order_by(Article.last_edited.desc()).paginate(_offset,5).dicts()
            else:
                articles = Article.select().where(Article.status == _status).order_by(Article.last_edited.desc()).paginate(_offset, 5).dicts()
        else:
            if _status is None:
                articles = Article.select().where(Article.id_section == _id_section).order_by(Article.last_edited.desc()).paginate(_offset, 5).dicts()
            else:
                articles = Article.select().where((Article.id_section == _id_section) & (Article.status == _status)).order_by(Article.last_edited.desc()).paginate(_offset, 5).dicts()
        
        for article in articles:
            article['section_name'] = Section[article['id_section']].name
            article['poster_name'] = User[article['id_poster']]['name']
            article['body'] = str(BeautifulSoup(article['body'], "lxml").text)
            #article['last_edited'] = pretty_date(article['last_edited'])
        return articles

    #get thelastest published article per section (total: 12) 
    def get_sidepage():
        sections = Section.select()
        sidepage_articles = []
        for section in sections:
            article = Article.select().where((Article.id_section == section.id_section) & (Article.status == 'Xuất bản')).order_by(Article.last_edited.desc()).limit(1).dicts()
            if len(article) > 0:
                article = article[0]
                article['section_name'] = Section[article['id_section']].name
                article['last_edited'] = pretty_date(article['last_edited'])
                sidepage_articles.append(article)
        return sidepage_articles
    
    #get up to 12 articles of user
    def get_user(_id_user):
        articles = Article.select().where(Article.id_poster == _id_user).order_by(Article.last_edited.desc()).dicts()
        for article in articles:
            article['section_name'] = Section[article['id_section']].name
            article['last_edited'] = pretty_date(article['last_edited'])
            pass
        return articles


    #get up to 5 lastest published articles include search keyword in its headline or body
    #ERROR: regardless of Vietnamese characters with accents (for example ắ ẩ  == a)
    def search(_keyword, _status = "Xuất bản"):
        if _status is None:
            articles = Article.select().where(  (Article.headline.contains(_keyword)) | (Article.body.contains(_keyword))  ).order_by(Article.last_edited.desc()).limit(12).dicts()
        else:
            articles = Article.select().where( ( (Article.headline.contains(_keyword)) | (Article.body.contains(_keyword)) ) & (Article.status == _status) ).order_by(Article.last_edited.desc()).limit(12).dicts()
        print('Các bài báo:')
        for article in articles:
            article['section_name'] = Section[article['id_section']].name
            article['last_edited'] = pretty_date(article['last_edited'])
            print(article['headline'])
        return articles

    #get up to 5 lastest articles satisfy the filter
    #ERROR: similar error with search method
    # def filter(_id_section = [1,2,3,4,5,6,7,8,9,10,11,12], _id_poster = [1,2,3,4,5,6,7,8,9,10,11,12], _byline = "", _headline = "", _body = "", _photo = "", _status = ['Xuất bản','Bản thảo']):
    #     return list(Article.select().where((Article.id_section<<(_id_section)) & (Article.id_poster<<(_id_poster)) & (Article.byline.contains(_byline)) & (Article.headline.contains(_headline)) & (Article.body.contains(_body)) & (Article.photo.contains(_photo)) & (Article.status<<(_status)) ).order_by(Article.last_edited.desc()).limit(12))

    #create an article
    def add(_id_section, _id_poster, _byline, _headline, _body, _photo, _status):
        return Article.create(id_section = _id_section, id_poster = _id_poster, byline = _byline, headline = _headline, body = _body,  photo = _photo,  status = _status,  last_edited = datetime.now())
    
    #update an article by ID
    #WARNING: does not return error when not find object
    def set(_id_article, _id_section, _byline, _headline, _body, _photo, _status):
        return Article.update(id_section = _id_section, byline = _byline, headline = _headline, body = _body,  photo = _photo,  status = _status,  last_edited = datetime.now()).where(Article.id_article == _id_article).execute()

    #delete an article by ID
    def remove(_id_article):
        try:
            Article.get(Article.id_article == _id_article).delete_instance()
            sub_file_name = str(_id_article) + '_'
            for file in os.listdir('static/img'):
                if sub_file_name in file:
                    os.remove('static/img/' + file)
            for file in os.listdir('static/audio/'):
                if sub_file_name in file:
                    os.remove('static/audio/' + file)
            for file in os.listdir('static/video/'):
                if sub_file_name in file:
                    os.remove('static/video/' + file)
            return True
        except:
            return False

    #copy all html articles from the first page of each section from Báo Hải Dương to my database (including media to local storage)
    def crawl_articles():
        # list of address from each section
        section_addresses = ["","chinh-tri/1", "goc-nhin/4", "kinh-te/5", "xa-hoi/11", "khoa-hoc---giao-duc/17", "phap-luat/21", "doi-song/12", "van-hoa---giai-tri/31", "the-gioi/35", "the-thao/39", "dat-va-nguoi-xu-dong/25", "ban-doc/47"]
        # get the last id_article in database
        _id_article = int(str(Article.select(Article.id_article).order_by(Article.id_article.desc()).limit(1)[0]))
        # loop over each section by number beacause we want to use index for storing id_section
        for _id_section in range(1,len(section_addresses)):
            # link for copy html
            url = "https://baohaiduong.vn/chuyen-muc/" + section_addresses[_id_section]
            print("Đang lấy các bài báo từ: " + section_addresses[_id_section])
            # Make a GET request to fetch the raw HTML content
            html_content = requests.get(url).text
            # Parse the html content
            soup = BeautifulSoup(html_content, "lxml")
            # get <ul> tag with "class": "list-news left w100pt" in the html which display all articles in middle of the page
            ul_articles = soup.find("ul", attrs={"class": "list-news left w100pt"})
            # get all the <li> tag in <ul> which store an article on each
            li_articles = ul_articles.find_all("li")
            #loop over each <li> tag to extract article infomation
            for article in li_articles:
                _id_article += 1    #increase _id_article by 1
                link = "https://baohaiduong.vn" + article.a.get("href")

                _headline = article.h4.a.text.replace('\n', ' ').strip()
                print("Bài báo \"" + _headline + "\": ")
                if Article.select().where(Article.headline == _headline).count() > 0:
                    print("đã tồn tại!")
                    continue

                #article_photo
                photo_address = article.a.img.get("src").replace("\\","/") #convert src to url address
                _photo = str(_id_article) + "_0.jpg"
                urlretrieve(photo_address, "static/img/" + _photo)

                #artilce_body
                article_content = requests.get(link).text
                article_soup = BeautifulSoup(article_content, "lxml")
                tag_body = article_soup.find("div", attrs={"class": "fck"})
                _body = str(tag_body)

                _id_photo = 1   #id_photo for set photos inside the article file name
                for tag_img in tag_body.find_all("img"):
                    photo_from_address = tag_img.get("src")
                    photo_to_address = str(_id_article) + "_" + str(_id_photo) + ".jpg"
                    if requests.head(photo_from_address).headers["content-type"] not in ("image/png", "image/jpeg", "image/jpg"): #check if photo in correct format
                        print("lỗi hình ảnh " + photo_from_address)
                        continue
                    urlretrieve(photo_from_address.replace("\\","/"), "static/img/" + photo_to_address)   #Download media from url to our project
                    _body = _body.replace(photo_from_address, "/static/img/" + photo_to_address)   #Replace BHD's image address with our address
                    _id_photo += 1

                _id_audio = 1   #id_audio for set audios inside the article file name
                for tag_audio in tag_body.find_all("audio"):
                    audio_from_address = tag_audio.source.get("src")
                    audio_to_address = "static/audio/" + str(_id_article) + "_" + str(_id_photo) + ".mp3"
                    urlretrieve(audio_from_address.replace("\\","/").replace(" ", "%20"), audio_to_address)   #Download media from url to our project
                    _body = _body.replace(audio_from_address, "/" + audio_to_address)   #Replace BHD's audio address with our address
                    _id_audio += 1

                _id_video = 1   #id_video for set videos inside the article file name
                for tag_video in tag_body.find_all("video"):
                    video_from_address = tag_video.source.get("src")
                    video_to_address = "static/video/" + str(_id_article) + "_" + str(_id_photo) + ".mp4"
                    urlretrieve(video_from_address.replace("\\","/").replace(" ", "%20"), video_to_address)   #Download media from url to our project
                    _body = _body.replace(video_from_address, "/" + video_to_address)   #Replace BHD's video address with our address
                    _id_video += 1
                Article.create(id_section = _id_section, id_poster = 1, byline = "Báo Hải Dương", headline = _headline, body = _body, photo = _photo, status = "Xuất bản", last_edited = datetime.now())
                print("Đã thêm")
            print()


# db.connect()
# print(User.add('chang','12345678','chang','Biên tập'))
# for i in a:
#     print(i)
#run crawl
# db.connect()
# Article.crawl_articles()