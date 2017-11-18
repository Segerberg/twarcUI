#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app, render_template, request,db, url_for, redirect,flash,Response
from app import models
from .forms import twitterTargetForm, SearchForm, twitterCollectionForm, collectionAddForm
from sqlalchemy.exc import IntegrityError
from .twarcUIarchive import twittercrawl
from config import POSTS_PER_PAGE, REDIS_DB
from datetime import datetime
from redislite import Redis
from rq import Queue


q = Queue(connection=Redis(REDIS_DB))

@app.before_request
def before_request():
        search_form = SearchForm()



'''INDEX ROUTE'''
@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    twitterUserCount = models.TWITTER.query.filter(models.TWITTER.status == '1').filter(models.TWITTER.targetType=='User').count()
    twitterSearchCount = models.TWITTER.query.filter(models.TWITTER.status == '1').filter(models.TWITTER.targetType == 'Search').count()
    collectionCount = models.COLLECTION.query.filter(models.COLLECTION.status=='1').count()
    CRAWLLOG = models.CRAWLLOG.query.order_by(models.CRAWLLOG.row_id.desc()).limit(10).all()
    form = SearchForm()
    if request.method == 'POST':
        return redirect((url_for('search_results', form=form, query=form.search.data)))

    return render_template("index.html", twitterUserCount=twitterUserCount, twitterSearchCount=twitterSearchCount, collectionCount=collectionCount, CRAWLLOG=CRAWLLOG, form=form)

'''SEARCH'''
@app.route('/search', methods=['GET', 'POST'])
def search():
    form =SearchForm()
    if request.method == 'POST':
        return redirect((url_for('search_results', form=form, query=form.search.data, page=1)))
    return render_template("search.html", form=form)


'''SEARCH RESULTS'''
@app.route('/search/<query>/<int:page>', methods=['GET', 'POST'])
def search_results(query,page=1):
    form = SearchForm()
    results = models.SEARCH.query.filter(models.SEARCH.text.like(u'%{}%'.format(query))).paginate(page, POSTS_PER_PAGE, False)
    return render_template('search.html', query=query, results=results,form=form)

'''
TWITTER
'''

'''USER-TIMELINES'''
@app.route('/twittertargets', methods=['GET', 'POST'])
def twittertargets():
    TWITTER = models.TWITTER.query.filter(models.TWITTER.status == '1').filter(models.TWITTER.targetType=='User')
    form = twitterTargetForm(prefix='form')

    if request.method == 'POST'and form.validate_on_submit():

        try:


            addTarget = models.TWITTER(title=form.title.data, searchString='', creator=form.creator.data, targetType='User',
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


'''API-SEARCH-TARGETS'''
@app.route('/twittersearchtargets', methods=['GET', 'POST'])
def twittersearchtargets():
    TWITTER = models.TWITTER.query.filter(models.TWITTER.status == '1').filter(models.TWITTER.targetType=='Search')
    templateType = "Search"
    form = twitterTargetForm(prefix='form')
    if request.method == 'POST'and form.validate_on_submit():
        try:
            addTarget = models.TWITTER(title=form.title.data, searchString=form.searchString.data, creator=form.creator.data, targetType='Search',
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

    return render_template("twittertargets.html", TWITTER=TWITTER, form=form, templateType = templateType)

'''COLLECTIONS'''
@app.route('/collections', methods=['GET', 'POST'])
def collections():
    COLLECTIONS = models.COLLECTION.query.filter(models.COLLECTION.status == '1')
    collectionForm = twitterCollectionForm(prefix='collectionForm')
    if request.method == 'POST' and collectionForm.validate_on_submit():
        try:
            addTarget = models.COLLECTION(title=collectionForm.title.data, curator=collectionForm.curator.data,
                                       collectionType=collectionForm.collectionType.data,
                                       description=collectionForm.description.data, subject=collectionForm.subject.data,
                                       status=collectionForm.status.data, lastCrawl=None,
                                       totalTweets=0, added=datetime.now())

            #addLog = models.CRAWLLOG(tag_title=form.title.data, event_start=datetime.now(),
            #                         event_text='ADDED TO DB')
            #addTarget.logs.append(addLog)
            db.session.add(addTarget)
            db.session.commit()
            db.session.close()
            back = models.COLLECTION.query.filter(models.COLLECTION.title == collectionForm.title.data).first()
            return redirect(url_for('collectionDetail', id=back.row_id))

        except IntegrityError:
            flash(u'Collection name is already in use! ', 'danger')
            db.session.rollback()

    return render_template("collections.html", COLLECTIONS=COLLECTIONS, collectionForm=collectionForm)



'''Route to view archived user tweets '''
@app.route('/usertweets/<id>/<int:page>', methods=['GET', 'POST'])
def userlist(id,page=1):
    id=id
    print (id)
    results = models.SEARCH.query.filter(models.SEARCH.username==id).order_by(models.SEARCH.created_at.desc()).paginate(page, POSTS_PER_PAGE, False)
    twitterTarget = models.TWITTER.query.filter(models.TWITTER.title == id).first()
    form = twitterTargetForm(prefix='form')
    if request.method == 'POST' and form.validate_on_submit():
        try:
            addTarget = models.TWITTER(title=form.title.data,searchString='' ,creator=form.creator.data, targetType='User',
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

'''Route to view archived user tweets '''
@app.route('/searchtweets/<id>/<int:page>', methods=['GET', 'POST'])
def searchlist(id,page=1):
    id=id
    results = models.SEARCH.query.filter(models.SEARCH.source==id).order_by(models.SEARCH.created_at.desc()).paginate(page, POSTS_PER_PAGE, False)
    twitterTarget = models.TWITTER.query.filter(models.TWITTER.row_id == id).first()
    form = twitterTargetForm(prefix='form')
    if request.method == 'POST' and form.validate_on_submit():
        try:
            addTarget = models.TWITTER(title=form.title.data,searchString='' ,creator=form.creator.data, targetType='User',
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
    object = models.TWITTER.query.get_or_404(id)
    CRAWLLOG = models.CRAWLLOG.query.order_by(models.CRAWLLOG.row_id.desc()).filter(models.CRAWLLOG.tag_id==id)
    form = twitterTargetForm(prefix='form',obj=object)
    assForm = collectionAddForm(prefix="assForm")
    linkedCollections = models.TWITTER.query. \
        filter(models.TWITTER.row_id == id). \
        first(). \
        tags
    if request.method == 'POST' and assForm.validate_on_submit():
        object.tags.append(assForm.assoc.data)
        db.session.commit()
        return redirect(url_for('twittertargetDetail', id=id))


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



    return render_template("twittertargetdetail.html", TWITTER=TWITTER, form=form, CRAWLLOG=CRAWLLOG, linkedCollections=linkedCollections, assForm=assForm)

'''Route to detail view of collections'''
@app.route('/collectiondetail/<id>', methods=['GET', 'POST'])
def collectionDetail(id):
    object = models.COLLECTION.query.get_or_404(id)
    targets = models.TWITTER.query.all()
    #CRAWLLOG = models.CRAWLLOG.query.order_by(models.CRAWLLOG.row_id.desc()).filter(models.CRAWLLOG.tag_id==id)
    linkedTargets =  models.COLLECTION.query.\
                    filter(models.COLLECTION.row_id==id).\
                    first().\
                    tags

    collectionForm = twitterCollectionForm(prefix='collectionform',obj=object)
    targetForm = twitterTargetForm(prefix='targetform')
    searchApiForm = twitterTargetForm(prefix='searchapiform')



    if request.method == 'POST' and collectionForm.validate_on_submit():
        try:
            collectionForm.populate_obj(object)
            db.session.add(object)
            db.session.commit()
            db.session.close()
            flash(u'Record saved! ', 'success')
        except IntegrityError:
            flash(u'Collection name is already in use!  ', 'danger')
            db.session.rollback()
        return redirect(url_for('collectionDetail',id=id))

    if request.method == 'POST' and targetForm.validate_on_submit():
        try:
            addTarget = models.TWITTER(title=targetForm.title.data, searchString='', creator=targetForm.creator.data,
                                       targetType='User',
                                       description=targetForm.description.data, subject=targetForm.subject.data,
                                       status=targetForm.status.data, lastCrawl=None, totalTweets=0,
                                       added=datetime.now(), woeid=None, index=targetForm.index.data, oldTweets=None)

            addLog = models.CRAWLLOG(tag_title=targetForm.title.data, event_start=datetime.now(), event_text='ADDED TO DB')
            #addTarget.logs.append(addLog)
            #db.session.add(addTarget)
            object.tags.append(addTarget)
            db.session.commit()
            db.session.close()
            flash(u'Record saved! ', 'success')
        except IntegrityError:
            flash(u'Collection name is already in use!  ', 'danger')
            db.session.rollback()
        return redirect(url_for('collectionDetail', id=id))


    if request.method == 'POST' and searchApiForm.validate_on_submit():
        try:
            addTarget = models.TWITTER(title=searchApiForm.title.data, searchString=searchApiForm.searchString.data,
                                       creator=searchApiForm.creator.data,
                                       targetType='Search',
                                       description=searchApiForm.description.data, subject=searchApiForm.subject.data,
                                       status=searchApiForm.status.data, lastCrawl=None, totalTweets=0,
                                       added=datetime.now(), woeid=None, index=searchApiForm.index.data,
                                       oldTweets=None)

            addLog = models.CRAWLLOG(tag_title=targetForm.title.data, event_start=datetime.now(),
                                     event_text='ADDED TO DB')
            # addTarget.logs.append(addLog)
            # db.session.add(addTarget)
            object.tags.append(addTarget)
            db.session.commit()
            db.session.close()

            flash(u'Record saved! ', 'success')
        except IntegrityError:
            flash(u'Collection name is already in use!  ', 'danger')
            db.session.rollback()
        return redirect(url_for('collectionDetail', id=id))

    return render_template("collectiondetail.html",  object = object, targets=targets,collectionForm=collectionForm, targetForm=targetForm,searchApiForm=searchApiForm, linkedTargets=linkedTargets)

'''
Route to add collection <--> target association
'''
@app.route('/addassociation/<id>/<target>', methods=['GET','POST'])
def addCollectionAssociation(id, target):
    object =  db.session.query(models.COLLECTION).get(id)
    linkedTarget = db.session.query(models.TWITTER).filter(models.TWITTER.row_id == target).one()
    object.tags.append(linkedTarget)
    db.session.commit()

    return redirect(url_for('collectionDetail', id=id))


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
Route to remove collection
'''
@app.route('/removecollection/<id>', methods=['GET','POST'])
def removeCollection(id):
    object = models.COLLECTION.query.get_or_404(id)
    db.session.delete(object)
    db.session.commit()
    db.session.close()

    return redirect('/collections')

'''
Route to remove collection <--> target association
'''

@app.route('/removeassociation/<id>/<target>', methods=['GET','POST'])
def removeCollectionAssociation(id, target):
    object =  db.session.query(models.COLLECTION).get(id)
    linkedTarget = db.session.query(models.TWITTER).filter(models.TWITTER.row_id == target).one()
    object.tags.remove(linkedTarget)
    db.session.commit()
    return redirect(request.referrer)



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

'''
Route to call collection twarc-archive
'''
@app.route('/startcollectioncrawl/<id>', methods=['GET','POST'])
def startCollectionCrawl(id):
    with app.app_context():
        linkedTargets = models.COLLECTION.query. \
            filter(models.COLLECTION.row_id == id). \
            first(). \
            tags
        for target in linkedTargets:
            last_crawl = models.TWITTER.query.get(target.row_id)
            last_crawl.lastCrawl = datetime.now()
            db.session.commit()
            flash(u'Archiving started!',  'success')
            q.enqueue(twittercrawl, target.row_id)
        db.session.close()
        return redirect(url_for('collectionDetail', id=id))