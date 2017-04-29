from sqlalchemy import Column, String, String, Integer, Boolean, TIMESTAMP, ForeignKey, Table
from sqlalchemy.orm import relationship
from flask import current_app
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer)
import hashlib
from common.Model import BaseModel, Base


class User(BaseModel):
    email = Column(String(256), nullable=False, unique=True)
    name = Column(String(256), unique=True)
    passwd_hash = Column(String(256), nullable=False)
    is_activated = Column(Boolean, default=False)


    req_projs = relationship('Project', back_populates='requester', lazy='dynamic')
    req_stories = relationship('Story', back_populates='requester', lazy='dynamic')
    req_issues = relationship('Issue', back_populates='requester', lazy='dynamic')


    def hash_password(self, password):
        """
        crypt the raw password and store it into database
        """
        self.passwd_hash = hashlib.sha224(password).hexdigest()

    def verify_password(self, password):
        """
        check if the password from user matches
        the password stored in the database
        """
        return hashlib.sha224(password).hexdigest() == self.passwd_hash

    def generate_auth_token(self, expiration=3600):
        """
        generate an authorization token used for API accesss
        """
        s = Serializer(
            current_app.config.get('SECRET_KEY'), expires_in=expiration)
        return s.dumps(str(self.id))

class Project(BaseModel):
    name = Column(String(256), nullable=False)
    speed = Column(Integer, default=0)
    requester_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    requester = relationship('User', back_populates='req_projs')

story_to_story = Table("story_to_story", Base.metadata,
    Column("parent_id", Integer, ForeignKey("story.id"), primary_key=True),
    Column("child_id", Integer, ForeignKey("story.id"), primary_key=True)
)

class Story(BaseModel):
    name = Column(String(256), nullable=False)
    desc = Column(String(256), default='')
    type = Column(Integer, default=0)
    points = Column(Integer, default=0)
    requester_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    requester = relationship('User', back_populates='req_stories')
    children = relationship('Story',
                        secondary='story_to_story',
                        primaryjoin='Story.id==story_to_story.c.parent_id',
                        secondaryjoin='Story.id==story_to_story.c.child_id',
                        backref='parent', lazy='dynamic')

class Issue(BaseModel):
    title = Column(String(256), nullable=False)
    content = Column(String(256), default='')
    points = Column(Integer, default=0)
    requester_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    requester = relationship('User', back_populates='req_issues')
    messages = relationship('Message', back_populates='issue', lazy='dynamic')

class Message(BaseModel):
    content = Column(String(256), default='')
    issue_id = Column(Integer, ForeignKey('issue.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    sender = relationship('User')
    issue = relationship('Issue', back_populates='messages')

def create_db():
    from common.Model import get_engine
    Base.metadata.create_all(get_engine())

if __name__ == '__main__':
    create_db()
