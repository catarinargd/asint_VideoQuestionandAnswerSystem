from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, scoped_session

import datetime
from sqlalchemy.orm import sessionmaker
from os import path


#SLQ access layer initialization
DATABASE_FILE = "Video.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False) #echo = True shows all SQL calls

Base = declarative_base()

#Declaration of data
class Video_db(Base):
    __tablename__ = 'Video_db'
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable = False)
    title = Column(String, nullable = False)
    user = Column(String, nullable = False)
    def __repr__(self):
        return "<ThisVideo (id=%d, URL=%s, Title=%s, User=%s>" % (
                                self.id, self.url, self.title, self.user)
    def to_dictionary(self):
        return {"video_id": self.id, "url": self.url, "title": self.title, "user":self.user}

Base.metadata.create_all(engine) #Create tables for the data models

db_Session = sessionmaker(bind=engine)
db_session = scoped_session(db_Session)
#db_session = db_session()

#function with a query to return the list of videos
def listVideos():
    return db_session.query(Video_db).all()
    db_session.close()

#function to return the previous question with to_dictionary
def listVideosDICT():
    ret_list = []
    lv = listVideos()
    for v in lv:
        vd = v.to_dictionary()
        ret_list.append(vd)
    return ret_list

#query to get the video with the id equal to id
def getVideo(id):
     v =  db_session.query(Video_db).filter(Video_db.id==id).first()
     return v

#query to get the video with url equal to url
def getVideoURL(id):
     v =  db_session.query(Video_db.url).filter(Video_db.id==id)
     return v

#function to return getVideo(id) with to_dictionary
def getVideoDICT(id):
    return getVideo(id).to_dictionary()
#function to create a new video in the database
def newVideo(url , title, user):
    vid = Video_db(url = url, title = title, user = user)
    try:
        db_session.add(vid)
        db_session.commit()
        print(vid.id)
        db_session.close()
        return vid.id
    except:
        return None

if __name__ == "__main__":
    pass