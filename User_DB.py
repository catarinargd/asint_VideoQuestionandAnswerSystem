from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, scoped_session

import datetime
from sqlalchemy.orm import sessionmaker
from os import path


#SLQ access layer initialization
DATABASE_FILE = "Users.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

#Declaration of data
class UserApp(Base):
    __tablename__ = 'UserApp'
   # id = Column(Integer, primary_key=True)
    username = Column(String,primary_key=True)
    name = Column(String, nullable = False)
    type_user = Column(String, nullable=False )
    nr_videos = Column(Integer, nullable=False )
    nr_views = Column(Integer, nullable=False )
    nr_questions = Column(Integer, nullable=False )
    nr_answers = Column(Integer, nullable=False )
    def __repr__(self):
        return "<ThisUser ( Username=%s, Name=%s, Type_User=%s, Nr_videos=%d, Nr_views=%d, Nr_questions=%d, Nr_answers=%d>" % (
                                 self.username, self.name, self.type_user, self.nr_videos, self.nr_views, self.nr_questions, self.nr_answers)
    def to_dictionary(self):
        return { "username": self.username, "name": self.name,"type_user":self.type_user, "nr_videos":self.nr_videos, "nr_views":self.nr_views, "nr_questions":self.nr_questions, "nr_answers":self.nr_answers}

Base.metadata.create_all(engine) #Create tables for the data models

db_Session = sessionmaker(bind=engine)
db_session = scoped_session(db_Session)

#function with a query that returns the list of users
def listUsers():
    return db_session.query(UserApp).all()
    db_session.close()

#function that returns the list of users with function to_dictionary
def listUsersDICT():
    ret_list = []
    lv = listUsers()
    for v in lv:
        vd = v.to_dictionary()
        ret_list.append(vd)
    return ret_list
#function with a query to return the user in the data base whose username is equal to the one inserted as and argument
def getUser(username):
    v =  db_session.query(UserApp).filter(UserApp.username==username).first()
    return v

#function that returns the user with function to_dictionary
def getUserDICT(username):
    if (getUser(username) == None):
        return None
    return getUser(username).to_dictionary()

#function to create a new user in the database, iniatially, nr_videos inserted, views, 
# questions and answers made is equal to zero, because the new 
# user has not done any of these operations in the browser
def newUser(username , name, type_user):
    nr_videos = 0
    nr_views = 0
    nr_questions = 0
    nr_answers = 0
    us = UserApp(username = username, name = name, type_user = type_user, nr_videos = nr_videos, nr_views = nr_views, nr_questions = nr_questions, nr_answers = nr_answers)
    try:
        db_session.add(us)
        db_session.commit()
        print(us.username)
        print(us.name)
        db_session.close()
        return us.username
    except:
        return None

# function to udpdate the number of videos inserted by a 
# user everytime the user inserts a new one
def increase_nr_videos(username):
    v = getUser(username)
    v.nr_videos += 1
    db_session.commit()    

# function to udpdate the number of views of videos 
# everytime the user views a video
def increase_nr_views(username):
    v = getUser(username)
    v.nr_views += 1
    db_session.commit()   

# function to udpdate the number of questions made by a user
# everytime the user makes a new question
def increase_nr_questions(username):
    v = getUser(username)
    v.nr_questions += 1
    db_session.commit()    

# function to udpdate the number of answers made by a user
# everytime the user responds with a new answer
def increase_nr_answers(username):
    v = getUser(username)
    v.nr_answers += 1
    db_session.commit()    


if __name__ == "__main__":
    pass