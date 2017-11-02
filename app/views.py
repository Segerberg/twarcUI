#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app, render_template, request,db, url_for, redirect,flash
from app import models
from .forms import twitterTargetForm, SearchForm
from sqlalchemy.exc import IntegrityError
from .twarcUIarchive import twittercrawl
from config import POSTS_PER_PAGE, REDIS_DB
import os
from datetime import datetime
from redislite import Redis
from rq import Queue

q = Queue(connection=Redis(REDIS_DB))

@app.before_request
def before_request():
        search_form = SearchForm()



'''Index Route'''
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    twitterUserCount = models.TWITTER.query.filter(models.TWITTER.status == '1').filter(models.TWITTER.targetType=='User').count()
    twitterSearchCount = models.TWITTER.query.filter(models.TWITTER.status == '1').filter(models.TWITTER.targetType == 'Search').count()
    CRAWLLOG = models.CRAWLLOG.query.order_by(models.CRAWLLOG.row_id.desc()).limit(10).all()
    form = SearchForm()
    if request.method == 'POST':
        return redirect((url_for('search_results', form=form, query=form.search.data)))

    return render_template("index.html", twitterUserCount=twitterUserCount, twitterSearchCount=twitterSearchCount, CRAWLLOG=CRAWLLOG, form=form)

@app.route('/search', methods=['GET', 'POST'])
def search():
    form =SearchForm()
    if request.method == 'POST':
        return redirect((url_for('search_results', form=form, query=form.search.data, page=1)))
    return render_template("search.html", form=form)


'''Search results'''
@app.route('/search/<query>/<int:page>', methods=['GET', 'POST'])
def search_results(query,page=1):
    form = SearchForm()
    results = models.SEARCH.query.filter(models.SEARCH.text.like(u'%{}%'.format(query))).paginate(page, POSTS_PER_PAGE, False)
    return render_template('search.html', query=query, results=results,form=form)

'''
TWITTER
'''
@app.route('/twittertargets', methods=['GET', 'POST'])
def twittertargets():
    TWITTER = models.TWITTER.query.filter(models.TWITTER.status == '1').filter(models.TWITTER.targetType=='User')
    form = twitterTargetForm(prefix='form')

    if request.method == 'POST'and form.validate_on_submit():

        try:


            addTarget = models.TWITTER(title=form.title.data, creator=form.creator.data, targetType='User',
                                       description=form.description.data, subject=form.subject.data, status=form.status.data,lastCrawl=None, totalTweets=0,
                                       added=datetime.now(), woeid=None, index=form.index.data, oldTweets=None)

            addLog = models.CRAWLLOG(tag_title=form.title.data,event_start=datetime.now(), event_text='ADDED TO DB')
            addTarget.logs.append(addLog)
            db.session.add(addTarget)
            db.session.commit()
            db.session.close()
            back = models.TWITTER.query.filter(models.TWITTER.title == form.title.data).first()
            return redirect(url_for('twittertargetDetail', id=back.row_id))
        except IntegrityError:
            flash(u'Twitter user account already in database!', 'danger')
            db.session.rollback()

    return render_template("twittertargets.html", TWITTER=TWITTER, form=form)



@app.route('/twittersearchtargets', methods=['GET', 'POST'])
def twittersearchtargets():
    TWITTER = models.TWITTER.query.filter(models.TWITTER.status == '1').filter(models.TWITTER.targetType=='Search')

    form = twitterTargetForm(prefix='form')
    if request.method == 'POST'and form.validate_on_submit():
        try:
            addTarget = models.TWITTER(title=form.title.data, creator=form.creator.data, targetType='Search',
                                       description=form.description.data, subject=form.subject.data,
                                       status=form.status.data, lastCrawl=None, totalTweets=0,
                                       added=datetime.now(), woeid=None, index=form.index.data, oldTweets=None)
            addLog = models.CRAWLLOG(tag_title=form.title.data, event_start=datetime.now(), event_text='ADDED TO DB')
            addTarget.logs.append(addLog)
            db.session.add(addTarget)
            db.session.commit()
            db.session.close()
            back = models.TWITTER.query.filter(models.TWITTER.title == form.title.data).first()
            return redirect(url_for('twittertargetDetail', id=back.row_id))

        except IntegrityError:
            flash(u'Search is already in database! ', 'danger')
            db.session.rollback()



    return render_template("twittersearchtargets.html", TWITTER=TWITTER, form=form)



'''Route to view archived user tweets '''
@app.route('/usertweets/<id>/<int:page>', methods=['GET', 'POST'])
def userlist(id,page=1):
    id=id
    results = models.SEARCH.query.filter(models.SEARCH.username==id).order_by(models.SEARCH.created_at.desc()).paginate(page, POSTS_PER_PAGE, False)
    twitterTarget = models.TWITTER.query.filter(models.TWITTER.title == id).first()
    form = twitterTargetForm(prefix='form')
    if request.method == 'POST' and form.validate_on_submit():
        try:
            addTarget = models.TWITTER(title=form.title.data, creator=form.creator.data, targetType='User',
                                       description=form.description.data, subject=form.subject.data,
                                       status=form.status.data, lastCrawl=None, totalTweets=0,
                                       added=datetime.now(), woeid=None, index=form.index.data, oldTweets=None)

            addLog = models.CRAWLLOG(tag_title=form.title.data, event_start=datetime.now(), event_text='ADDED TO DB')
            addTarget.logs.append(addLog)
            db.session.add(addTarget)
            db.session.commit()
            db.session.close()

        except IntegrityError:
            flash(u'Twitter user account already in database ', 'danger')
            db.session.rollback()
        return redirect(url_for('twittertargets'))



    return render_template("usertweets.html", results=results,id=id, twitterTarget=twitterTarget,form=form)



'''Route to detail view of twitter user/search target'''
@app.route('/twittertargets/<id>', methods=['GET', 'POST'])
def twittertargetDetail(id):

    TWITTER = models.TWITTER.query.filter(models.TWITTER.row_id == id).first()
    print (TWITTER.title)
    object = models.TWITTER.query.get_or_404(id)
    CRAWLLOG = models.CRAWLLOG.query.order_by(models.CRAWLLOG.row_id.desc()).filter(models.CRAWLLOG.tag_id==id)
    form = twitterTargetForm(prefix='form',obj=object)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            form.populate_obj(object)
            addLog = models.CRAWLLOG(tag_title=form.title.data, event_start=datetime.now(), event_text='DESCRIPTION ALTERED')
            object.logs.append(addLog)
            db.session.add(object)
            db.session.commit()
            db.session.close()
            flash(u'Record saved! ', 'success')
        except IntegrityError:
            flash(u'Twitter user account already in database ', 'danger')
            db.session.rollback()
        return redirect(url_for('twittertargetDetail',id=id))


    return render_template("twittertargetdetail.html", TWITTER=TWITTER, form=form, CRAWLLOG=CRAWLLOG)


'''
Route to remove twitter-target
'''
@app.route('/removetwittertarget/<id>', methods=['POST'])
def removeTwitterTarget(id):
    object = models.TWITTER.query.get_or_404(id)
    db.session.delete(object)
    db.session.commit()
    db.session.close()
    if object.targetType == 'Search':
        return redirect('/twittersearchtargets')
    else:
        return redirect('/twittertargets')


'''
Route to call twarc-archive
'''
@app.route('/starttwittercrawl/<id>', methods=['GET','POST'])
def startTwitterCrawl(id):
    with app.app_context():

        last_crawl = models.TWITTER.query.get(id)
        last_crawl.lastCrawl = datetime.now()
        db.session.commit()
        db.session.close()
        flash(u'Archiving started!',  'success')
        object = models.TWITTER.query.get_or_404(id)
        q.enqueue(twittercrawl, id)
        if object.targetType == "Search":
            return redirect('/twittersearchtargets')
        else:
            return redirect('/twittertargets')




            




