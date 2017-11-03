from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, DateField, FieldList, FormField, TextAreaField
from wtforms.validators import DataRequired



class twitterTargetForm(FlaskForm):
    title = StringField(u'Title', validators=[DataRequired()])
    searchString = StringField(u'Search ')
    creator = StringField(u'Creator')
    description = TextAreaField(u'Description')
    subject = StringField(u'Subject')
    status = SelectField(u'Status', choices=[("1", "Active"),("0","Closed")])
    index = BooleanField(u'Index')


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])