from flask_wtf import FlaskForm
from app import models, db
from wtforms import StringField, BooleanField, SelectField,  FieldList, FormField, TextAreaField, SelectMultipleField, widgets,validators
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired,Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField

def collectionTypes():
    return db.session.query(models.COLLECTION).all()

class collectionAddForm(FlaskForm):
    assoc = QuerySelectField(u'Collection Name', query_factory=collectionTypes, get_label='title')


class twitterTargetForm(FlaskForm):
    title = StringField(u'Title', validators=[DataRequired()])
    searchString = StringField(u'Search ')
    creator = StringField(u'Creator')
    description = TextAreaField(u'Description')
    subject = StringField(u'Subject')
    status = SelectField(u'Status', choices=[("1", "Active"),("0","Closed")])
    index = BooleanField(u'Index')



class twitterCollectionForm(FlaskForm):
    title = StringField(u'Title', validators=[DataRequired()])
    curator = StringField(u'Curator')
    description = TextAreaField(u'Description')
    collectionType = SelectField(u'Collection Type', choices=[("Not Specified", "Not Specified"),("Event", "Event"),("Subject","Subject")])
    subject = StringField(u'Subject')
    status = SelectField(u'Status', choices=[("1", "Active"),("0","Closed")])
    inclDateStart = DateField(u'Inclusive start date',format='%Y-%m-%d')
    inclDateEnd = DateField(u'Inclusive end date',[validators.Optional()],format='%Y-%m-%d')


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])

class twitterTrendForm(FlaskForm):
    geoloc = StringField(u'geo location', validators=[DataRequired(),Regexp(message='Not a valid geolocation, sorry.',regex="^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$")])



class stopWordsForm(FlaskForm):
    stopWord = StringField(u'Stop Word', validators=[DataRequired()])

