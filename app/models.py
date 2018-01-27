from app import db, app


assoc_twitter_collections = db.Table('ASSOC_TWITTER_COLLECTIONS',
    db.Column('twitter_id', db.Integer, db.ForeignKey('TWITTER.row_id'), primary_key=True),
    db.Column('collection_id', db.Integer, db.ForeignKey('COLLECTION.row_id'), primary_key=True)
)


class TWITTER(db.Model):
    __tablename__ = 'TWITTER'
    row_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False, index=True)
    searchString = db.Column(db.String(250), nullable=False)
    creator = db.Column(db.String(50))
    targetType = db.Column(db.String(50))
    description = db.Column(db.Text)
    subject = db.Column(db.String(50))
    status = db.Column(db.String(50))
    lastCrawl = db.Column(db.DateTime)
    totalTweets = db.Column(db.Integer)
    added = db.Column(db.DateTime)
    woeid = db.Column(db.String(50))
    index = db.Column(db.Boolean)
    oldTweets = db.Column(db.Boolean)
    logs = db.relationship("CRAWLLOG", backref='twitter', lazy=True, cascade="save-update, merge, delete")
    exports = db.relationship("EXPORTS", backref='twitter_us_exports', lazy=True, cascade="save-update, merge, delete")
    tags = db.relationship('COLLECTION', secondary=assoc_twitter_collections,back_populates='tags', lazy='subquery')




    def __init__(self, title, searchString, creator, targetType, description, subject, status, lastCrawl, totalTweets, added, woeid, index,oldTweets):
        self.title = title
        self.searchString = searchString
        self.creator = creator
        self.targetType = targetType
        self.description = description
        self.subject = subject
        self.status = status
        self.lastCrawl = lastCrawl
        self.added = added
        self.woeid = woeid
        self.index = index
        self.oldTweets = oldTweets
        self.totalTweets = totalTweets

class COLLECTION(db.Model):
    __tablename__ = 'COLLECTION'
    row_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False, index=True)
    curator = db.Column(db.String(50))
    collectionType = db.Column(db.String(250))
    description = db.Column(db.Text)
    subject = db.Column(db.String(50))
    status = db.Column(db.String(50))
    inclDateStart = db.Column(db.DateTime)
    inclDateEnd = db.Column(db.DateTime)
    lastCrawl = db.Column(db.DateTime)
    totalTweets = db.Column(db.Integer)
    added = db.Column(db.DateTime)
    exports = db.relationship("EXPORTS", backref='twitter_coll_exports', lazy=True, cascade="save-update, merge, delete")
    tags = db.relationship('TWITTER', secondary=assoc_twitter_collections, lazy='dynamic',back_populates='tags')


    def __init__(self, title,  curator, collectionType, description, subject, status,inclDateStart,inclDateEnd, lastCrawl, totalTweets, added):
        self.title = title
        self.curator = curator
        self.collectionType = collectionType
        self.description = description
        self.subject = subject
        self.status = status
        self.inclDateStart =inclDateStart
        self.inclDateEnd = inclDateEnd
        self.lastCrawl = lastCrawl
        self.added = added
        self.totalTweets = totalTweets

class TRENDS_LOC(db.Model):
    __tablename__ = 'TRENDS_LOC'
    row_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    loc =  db.Column(db.String(250))
    trends = db.relationship("TWITTER_TRENDS", backref='twitter_trends', lazy=True, cascade="save-update, merge, delete")

    def __init__(self,name, loc):
        self.name = name
        self.loc = loc

class TWITTER_TRENDS(db.Model):
    __tablename__ = 'TWITTER_TRENDS'
    row_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    promoted_content = db.Column(db.String(250))
    tweet_volume = db.Column(db.String(250))
    url = db.Column(db.String(250))
    collected = db.Column(db.DateTime)
    saved = db.Column(db.Boolean)
    trend_loc = db.Column(db.Integer, db.ForeignKey('TRENDS_LOC.row_id'), nullable=False)


    def __init__(self,name, promoted_content, tweet_volume,url,collected, saved):
        self.name = name
        self.promoted_content = promoted_content
        self.tweet_volume = tweet_volume
        self.url = url
        self.collected = collected
        self.saved = saved

class EXPORTS (db.Model):
    __tablename__ = 'EXPORTS'
    row_id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(250))
    type = db.Column(db.String(50))
    exported = db.Column(db.DateTime)
    count = db.Column(db.String(250))
    twitter_id = db.Column(db.Integer, db.ForeignKey('TWITTER.row_id'), nullable=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('COLLECTION.row_id'), nullable=True)

    def __init__(self, url, type, exported, count):
        self.url = url
        self.type = type
        self.exported = exported
        self.count = count


class CRAWLLOG(db.Model):
    __tablename__ = 'CRAWLLOG'
    row_id = db.Column(db.Integer, primary_key=True)
    event_start = db.Column(db.DateTime)
    event_text = db.Column(db.String(250))
    tag_title = db.Column(db.String(50))
    tag_id = db.Column( db.Integer, db.ForeignKey('TWITTER.row_id'),nullable = False)


    def __init__(self,event_start, event_text, tag_title):
        self.event_start = event_start
        self.event_text = event_text

        self.tag_title = tag_title

class SEARCH(db.Model):
    __tablename__ = 'SEARCH'
    row_id = db.Column(db.Integer, primary_key=True)
    screen_name = db.Column(db.String(250))
    username = db.Column(db.String(250))
    text = db.Column(db.String(250))
    created_at = db.Column(db.DateTime)
    source = db.Column(db.String(250))
    retweets = db.Column(db.String(50))
    image_url = db.Column(db.String(50))
    type =  db.Column(db.String(50))

    def __init__(self, screen_name, username, text, created_at, source, retweets,image_url,type):
        self.screen_name = screen_name
        self.username = username
        self.text = text
        self.created_at = created_at
        self.source = source
        self.retweets = retweets
        self.image_url = image_url
        self.type = type

        def __repr__(self):
            return '<Text %r>' % (self.text)


class STOPWORDS(db.Model):
    __tablename__ = 'STOPWORDS'
    row_id = db.Column(db.Integer, primary_key=True)
    stop_word = db.Column(db.String(250))
    lang = db.Column(db.String(50))

    def __init__(self,stop_word, lang):
        self.stop_word = stop_word
        self.lang = lang

class VOCABS(db.Model):
    __tablename__ = 'VOCABS'
    row_id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(250))
    use = db.Column(db.String(50))
    def __init__(self,term, use):
        self.term = term
        self.use = use

