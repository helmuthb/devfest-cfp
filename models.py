from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


# user - a logged in user identified with one or more credentials
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    picture_url = db.Column(db.String(200))
    email = db.Column(db.String(100))
    facebook_id = db.Column(db.String(80))
    google_id = db.Column(db.String(80))
    twitter_id = db.Column(db.String(80))
    github_id = db.Column(db.String(80))

    # function converting into a dict for jsonify
    def toDict(self):
        return {
            'id': self.id,
            'name': self.name,
            'picture_url': self.picture_url,
            'email': self.email,
            'facebook_id': self.facebook_id,
            'google_id': self.google_id,
            'twitter_id': self.twitter_id,
            'github_id': self.github_id
        }

    pass


# speaker - a (proposed) speaker at a conference
class Speaker(db.Model):
    __tablename__ = 'speaker'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    email = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    company = db.Column(db.String(100))
    twitter_handle = db.Column(db.String(100))
    github_name = db.Column(db.String(100))
    linkedin_url = db.Column(db.String(100))
    google_url = db.Column(db.String(100))
    company_url = db.Column(db.String(100))
    website_url = db.Column(db.String(100))
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    user = db.relationship(User)

    # function converting into a dict for jsonify
    def toDict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'email': self.email,
            'title': self.title,
            'company': self.company,
            'twitter_handle': self.twitter_handle,
            'github_name': self.github_name,
            'linkedin_url': self.linkedin_url,
            'google_url': self.google_url,
            'company_url': self.company_url,
            'website_url': self.website_url,
            user_id: self.user_id
        }

    pass


# conference - main object which identifies the sessions in it
class Conference(db.Model):
    __tablename__ = 'conference'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date_start = db.Column(db.DateTime)
    date_end = db.Column(db.DateTime)
    cfp_start = db.Column(db.DateTime)
    cfp_end = db.Column(db.DateTime)

    # function to convert into a dict for jsonify
    def toDict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'cfp_start': self.cfp_start,
            'cfp_end': self.cfp_end
        }

    pass


# talk - a session proposal for a conference
class Talk(db.Model):
    __tablename__ = 'talk'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    level = db.Column(db.Integer)
    requirements = db.Column(db.Text)

    # function to convert into a dict for jsonify
    def toDict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'level': self.level,
            'requirements': self.requirements
        }

    pass


# association between sessions and their speakers
session_speaker = db.Table(
    'talk_speaker',
    db.Model.metadata,
    db.Column('talk_id', db.Integer, db.ForeignKey('talk.id')),
    db.Column('speaker_id', db.Integer, db.ForeignKey('speaker.id'))
)

if __name__ == '__main__':
    # initializing Flask & DB
    app = Flask(__name__, template_folder='templates')
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'
    db.init_app(app)
    # create database
    db.create_all()
