from flask import Flask, abort, request,  redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, scoped_session

from sqlalchemy.orm import sessionmaker
from os import path
from datetime import datetime



#SLQ access layer initialization
DATABASE_FILE = "Logs.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

#Declaration of data
class Message_DB(Base):
    __tablename__ = 'Message_DB'
    id = Column(Integer, primary_key=True)
    IP = Column(String, nullable = False)
    timeStamp = Column(String, nullable = False)
    endpoint = Column(String, nullable = False)
    
    def __repr__(self):
        return "<ThisMessage ( id = %d, IP= %s, timeStamp = %s, endpoint = %s>" % (
                                 self.id, self.IP, self.timeStamp, self.endpoint)
    def to_dictionary(self):
        return {"id": self.id, "IP": self.IP, "timeStamp":self.timeStamp, "endpoint":self.endpoint}

class DataCreation(Base):
    __tablename__ = 'DataCreation'
    id = Column(Integer, primary_key=True)
    data_type = Column(String, nullable = False)
    timeStamp = Column(String, nullable = False)
    content = Column(String, nullable = False)
    user = Column(String, nullable = False)
    def __repr__(self):
        return "<ThisUser ( id = %d, data_type = %d, timeStamp = %s,content = %s, user = %s>" % (
                                 self.id, self.data_type, self.timeStamp,self.content, self.user)
    def to_dictionary(self):
        return { "id": self.id, "data_type": self.data_type, "timeStamp":self.timeStamp, "content":self.content, "user":self.user}


Base.metadata.create_all(engine) #Create tables for the data models

db_Session = sessionmaker(bind=engine)
db_session = scoped_session(db_Session)

#function with a query to return the list of messages
def listMessages():
    return db_session.query(Message_DB).all()
    db_session.close()

#function to return the previous function with to_dictionary
def listMessagesDICT():
    ret_list = []
    lv = listMessages()
    for v in lv:
        vd = v.to_dictionary()
        ret_list.append(vd)
    return ret_list

#function to create new message in the database
def CreateNewMessage(IP, endpoint):
    now = datetime.now()
    timeStamp = now.strftime("%H:%M:%S")
    
    vid = Message_DB(IP = IP, timeStamp = timeStamp, endpoint = endpoint)

    try:
        db_session.add(vid)
        db_session.commit()
        print(vid.id)
        db_session.close()
        return vid.id
    except:
        abort(400)

#function to create new datacreation in the database
def CreateNewData(data_type, content, user):
    now = datetime.now()
    timeStamp = now.strftime("%H:%M:%S")

    data = DataCreation(data_type = data_type, timeStamp = timeStamp, content = content, user = user)
 
    try:
        db_session.add(data)
        db_session.commit()
        print(data.id)
        db_session.close()
        return data.id
    except:
        abort(400)

#function with a query to return the list of all the datacreation
def listData():
    return db_session.query(DataCreation).all()
    db_session.close()

#function to return the previous question with to_dictionary
def listDataDICT():
    ret_list = []
    lv = listData()
    for v in lv:
        vd = v.to_dictionary()
        ret_list.append(vd)
    return ret_list

if __name__ == "__main__":
    pass