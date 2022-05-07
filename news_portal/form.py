from flask_wtf import FlaskForm
from wtforms import (FileField, PasswordField, SelectField, StringField, SubmitField, TextAreaField)
from wtforms.validators import InputRequired, Length, EqualTo
from model import *

# wtf form for editor/writer login
class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[InputRequired(message="Không được để trống")])
    password = PasswordField('Mật khẩu', validators=[InputRequired(message="Không được để trống"),
                                                     Length(min=8, max=20, message="Mật khẩu phải từ 8 đến 20 kí tự")])


class ResetPasswordForm(FlaskForm):
    currentPassword = PasswordField("Mật khẩu hiện tại", validators=[InputRequired(message="Không được để trống"), 
                                                                     Length(min=8, max=20, message="Mật khẩu phải từ 8 đến 20 kí tự")])
    newPassword = PasswordField("Mật khẩu mới", validators=[InputRequired(message="Không được để trống"), 
                                                            Length(min=8, max=20, message="Mật khẩu phải từ 8 đến 20 kí tự"),
                                                            EqualTo('retypePassword', message="Phải trùng với mật khảu nhập lại")])
    retypePassword = PasswordField("Nhập lại mật khẩu mới")

class ArticleForm(FlaskForm):
    headline = StringField('Tiêu đề', validators=[InputRequired()])
    byline = StringField('Tác giả', validators=[InputRequired()])
    section = SelectField('Chuyên mục', coerce=int, choices=[])
    body = TextAreaField('Nội dung', validators=[Length(min=5)])
    btn_publish = SubmitField('Xuất bản bài báo')
    btn_save = SubmitField('Lưu bản thảo')
    photo = FileField('Thêm ảnh:')
    status = None