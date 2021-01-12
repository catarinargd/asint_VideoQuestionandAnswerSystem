from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, scoped_session

import datetime
from sqlalchemy.orm import sessionmaker
from os import path


#SLQ access layer initialization
DATABASE_FILE = "QA.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

#Declaration of data
class Question(Base):
    __tablename__ = 'Question'
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, nullable = False)
    time = Column(String, nullable = False)
    user = Column(String, nullable = False )
    text = Column(String, nullable = False )
    def __repr__(self):
        return "<Quest ( id=%d, video_id=%d, time=%s, user=%s, text=%s>" % (
                               self.id, self.video_id, self.time, self.user, self.text)
    def to_dictionary(self):
        return { "id": self.id, "video_id": self.video_id, "time": self.time,"user":self.user, "text":self.text}

#Declaration of data
class Answer(Base):
    __tablename__ = 'Answer'
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, nullable = False)
    user = Column(String, nullable = False )
    text = Column(String, nullable = False )
    question = Column(Integer, nullable = False)
    def __repr__(self):
        return "<Ans ( id=%d, video_id=%d, user=%s, text=%s, question=%d>" % (
                               self.id, self.video_id, self.user, self.text, self.question)
    def to_dictionary(self):
        return { "id": self.id, "video_id": self.video_id,"user":self.user, "text":self.text, "question":self.question}

Base.metadata.create_all(engine) #Create tables for the data models

db_Session = sessionmaker(bind=engine)
db_session = scoped_session(db_Session)


#function with a query that returns the list of questions of a video
def listQuestions(video_id):
    return db_session.query(Question).filter(Question.video_id==video_id)
    db_session.close()

#function that returns the list of questions with function to_dictionary
def listQuestionsDICT(video_id):
    ret_list = []
    lq = listQuestions(video_id)
    for v in lq:
        qd = v.to_dictionary()
        ret_list.append(qd)
    return ret_list

#funtion with a query to return the first question of a video
def getFirstQuestion(video_id):
    v =  db_session.query(Question).filter(Question.video_id==video_id).first()
    return v

# function to return the first question of a video with function to_dictionary
def getFirstQuestionDICT(id):
    return getFirstQuestion(id).to_dictionary()

#function with a query to return the question with question_id of the video with video_id (a specific question , from a specific video)
def getQuestion(video_id, q_id):
    v =  db_session.query(Question).filter(Question.video_id == video_id, Question.id==q_id).first()
    return v

#return the previous function with to_dictionary
def getQuestionDICT(video_id, q_id):
    v = getQuestion(video_id, q_id).to_dictionary()
    return v

#function to create new question in the database
def newQuestion(video_id, time, user, text):
    qs = Question(video_id = video_id, time = time, user = user, text = text)

    try:
        db_session.add(qs)
        db_session.commit()
        print(qs.video_id)
        db_session.close()
        return qs.id
    except:
        return None

#function with a query that returns the list of answers of a question
def listAnswers(q_id):
    return db_session.query(Answer).filter(Answer.question==q_id)
    db_session.close()

#returns previous function with to_dictionary
def listAnswersDICT(q_id):
    ret_list = []
    la = listAnswers(q_id)
    for v in la:
        ad = v.to_dictionary()
        ret_list.append(ad)
    return ret_list

#function to create a new answer in the database
def newAnswer(video_id, user, text, q_id):
    an = Answer(video_id = video_id, user = user, text = text, question = q_id)
    try:
        db_session.add(an)
        db_session.commit()
        print(an.video_id)
        db_session.close()
        return an.id
    except:
        return None



if __name__ == "__main__":
    pass