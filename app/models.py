from app import db, app



class TWITTER(db.Model):
    __tablename__ = 'TWITTER'
    row_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False, index=True)
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


    def __init__(self, title, creator, targetType, description, subject, status, lastCrawl, totalTweets, added, woeid, index,oldTweets):
        self.title = title
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



