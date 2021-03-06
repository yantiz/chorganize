from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext import mutable
from datetime import datetime

global db
db = SQLAlchemy()

def createApp(testing=False):
    app = Flask(__name__)
    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_sqlite.db'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    db.create_all()
    return app
    
    
association_table = db.Table('association_table',
    db.Column('user_email', db.String(80), db.ForeignKey('user.email'), nullable=False),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), nullable=False),
    db.PrimaryKeyConstraint('user_email', 'group_id')
)


class User(db.Model):
    __tablename__ = 'user'

    email = db.Column(db.String(80), primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    firstName = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(80), nullable=True)
    chores = db.relationship('Chore', backref='user', lazy='dynamic')
    groups = db.relationship('Group', secondary=association_table, lazy='dynamic',
                             backref=db.backref('users', lazy='dynamic'))

    def getEmail(self):
        return self.email

    def setEmail(self, email):
        self.email = email
        db.session.commit()

    def getUsername(self):
        return self.username

    def setUsername(self, username):
        self.username = username
        db.session.commit()

    def getPassword(self):
        return self.password

    def setPassword(self, password):
        self.password = password
        db.session.commit()

    def getFirstName(self):
        return self.firstName

    def setFirstName(self, firstName):
        self.firstName = firstName
        db.session.commit()

    def getLastName(self):
        return self.lastName

    def setLastName(self, lastName):
        self.lastName = lastName
        db.session.commit()

    def addChore(self, chore):
        self.chores.append(chore)
        db.session.commit()

    def getChores(self):
        return self.chores.all()
        
    def removeChore(self, chore):
        self.chores.remove(chore)
        db.session.commit()

    def addGroup(self, group):
        self.groups.append(group)
        db.session.commit()

    def getGroups(self):
        return self.groups.all()

    @classmethod
    def createUser(cls, email, username, password, firstName, lastName):
        user = User(email=email, username=username, password=password, firstName=firstName, lastName=lastName)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def getUser(cls, email):
        return cls.query.filter_by(email=email).one()

    @classmethod
    def deleteUser(cls, email):
        user = cls.getUser(email)
        db.session.delete(user)
        db.session.commit()

    @property
    def serialize(self):
        return {
                'email': self.email,
                'username': self.username,
                'firstName': self.firstName,
                'lastName': self.lastName
               }


class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    chores = db.relationship('Chore', backref='group', lazy='dynamic')
    performances = db.Column(mutable.MutableDict.as_mutable(db.PickleType))

    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name
        db.session.commit()

    def addChore(self, chore):
        self.chores.append(chore)
        db.session.commit()

    def getChores(self):
        return self.chores.all()

    def addUser(self, user):
        self.users.append(user)
        db.session.commit()
        userEmail = user.getEmail()
        if self.performances is None:
            self.performances = {userEmail: {'total': 0, 'onTime': 0}}
        elif userEmail not in self.performances:
            self.performances[userEmail] = {'total': 0, 'onTime': 0}
        db.session.commit()

    def getUsers(self):
        return self.users.all()

    def removeUser(self, user):
        self.users.remove(user)
        db.session.commit()

    def getPerformanceByEmail(self, email):
        return self.performances.get(email)

    def incrementPerformanceTotalByEmail(self, email):
        if email in self.performances:
            performance = self.performances[email]
            performance['total'] += 1
            self.performances[email] = performance
            db.session.commit()
        

    def incrementPerformanceOnTimeByEmail(self, email):
        if email in self.performances:
            performance = self.performances[email]
            performance['onTime'] += 1
            self.performances[email] = performance
            db.session.commit()

    @classmethod
    def createGroup(cls, name):
        group = Group(name=name)
        db.session.add(group)
        db.session.commit()
        return group

    @classmethod
    def getGroup(cls, id):
        return cls.query.filter_by(id=id).one()

    @classmethod
    def deleteGroup(cls, id):
        group = cls.getGroup(id)
        db.session.delete(group)
        db.session.commit()

    @property
    def serialize(self):
        return {
                'id': self.id,
                'name': self.name
               }


class Chore(db.Model):
    __tablename__ = 'chore'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, default=None)
    completed = db.Column(db.Boolean, default=False)
    deadline = db.Column(db.DateTime, default=None)
    userEmail = db.Column(db.String, db.ForeignKey('user.email'), default=None)
    groupID = db.Column(db.Integer, db.ForeignKey('group.id'))

    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name
        db.session.commit()

    def getDescription(self):
        return self.description

    def setDescription(self, description):
        self.description = description
        db.session.commit()

    def getCompleted(self):
        return self.completed

    def setCompleted(self, completed):
        self.completed = completed
        db.session.commit()

    def getDeadline(self):
        return self.deadline

    def setDeadline(self, deadline):
        self.deadline = deadline
        db.session.commit()

    def getUserEmail(self):
        return self.userEmail

    def getGroupID(self):
        return self.groupID

    def deadlinePassed(self):
        if self.deadline != None:
            now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return ((self.deadline - now).days < 0)
        else:
            return None

    @classmethod
    def createChore(cls, name, description=None, completed=False):
        chore = Chore(name=name, description=description, completed=completed)
        db.session.add(chore)
        db.session.commit()
        return chore

    @classmethod
    def getChore(cls, id):
        return cls.query.filter_by(id=id).one()

    @classmethod
    def deleteChore(cls, id):
        chore = cls.getChore(id)
        db.session.delete(chore)
        db.session.commit()

    @property
    def serialize(self):
        return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'completed': self.completed,
                'deadline': self.deadline,
                'groupID': self.groupID,
                'userEmail': self.userEmail,
                'deadlinePassed': self.deadlinePassed()
               }

if __name__ == '__main__':
    app = createApp()
    app.app_context().push()
    db.create_all()
