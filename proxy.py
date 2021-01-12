from flask import Flask, abort, request,  redirect, url_for
from flask_dance.consumer import OAuth2ConsumerBlueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import jsonify, url_for
from flask import session 
from time import sleep
import requests

#import functions from other files .py
from User_DB import *
from Video_DB import *
from QA_DB import *
from Logs_DB import *

#necessary so that our server does not need https
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


app = Flask(__name__)
app.secret_key = "supersekrit"  # Replace this with your own secret!
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
fenix_blueprint = OAuth2ConsumerBlueprint(
    "fenix-example", __name__,
    # this value should be retrived from the FENIX OAuth page
    client_id="1132965128044808",
    # this value should be retrived from the FENIX OAuth page
    client_secret="clsAhBfVSyZqxL0lg9cS5AtaTpFIL+NIugcsDb+AVM77CBcQWhz8ZSILCMIdobIkN8zz6XC/u0/loErYGQ9MWg==",
    # do not change next lines
    base_url="https://fenix.tecnico.ulisboa.pt/",
    token_url="https://fenix.tecnico.ulisboa.pt/oauth/access_token",
    authorization_url="https://fenix.tecnico.ulisboa.pt/oauth/userdialog",
)

app.register_blueprint(fenix_blueprint)

@app.route('/')
def home_page():
    # The access token is generated everytime the user authenticates into FENIX
    print(fenix_blueprint.session.authorized)
    print("Access token: "+ str(fenix_blueprint.session.access_token))
    return render_template("appPage.html", loggedIn = fenix_blueprint.session.authorized)

@app.route('/login')
def login():
    return redirect(url_for("fenix-example.login"))

@app.route('/logout')
def logout():
    # this clears all server information about the access token of this connection
    res = str(session.items())
    print(res)
    session.clear()
    res = str(session.items())
    print(res)
    # when the browser is redirected to home page it is not logged in anymore 
    return render_template("appPage.html", loggedIn = False)


@app.route('/API/auth/')
def Authentication(button):
    #this page can only be accessed by a authenticated user
    admin_list = ['ist186961']
    # verification of the user is  logged in
    try:
        if fenix_blueprint.session.authorized == False:
            #if not logged in browser is redirected to login page (in this case FENIX handled the login
            return redirect(url_for("fenix-example.login"))
        else:
            #if the user is authenticated then a request to FENIX is made
            resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
            #res contains the response made to /api/fenix/vi/person (information about current user)
            data = resp.json() 
            
            #define the type_user acording to the usernames that are stored in admin_list
            if data["username"] in admin_list:
                type_user = "Admin"
            else :
                type_user = "Regular"

            #when authentication is done it's necessary to verify if the user is already in the database
            #if it's not, it is necessary to create the user
            if getUser(data["username"]) == None:
                createNewUser(data["username"], data["name"], type_user)

            else:
                if returnSingleUserJSON(data["username"]) == False:
                    createNewUser(data["username"], data["name"], type_user)

        if (button == "AdminPage"):
            return redirect(url_for("AdminPages"))
        else:
            return redirect(url_for("VideoListing"))
    except:
        print("Session Expired")
        return render_template("appPage.html", loggedIn = fenix_blueprint.session.authorized)
        
#function to get the user that is currently logged In
def CurrentUser():
    resp = fenix_blueprint.session.get("/api/fenix/v1/person/")
    #res contains the response made to /api/fenix/vi/person (information about current user)
    user = resp.json() 
    return user

#function to access and send information to thet appPage.html
@app.route("/app_page/")
def renderAppPage():
    #create new message exchange
    ip = request.environ['REMOTE_ADDR']
    CreateNewMessage(ip, "/app_page/")
    return  render_template("appPage.html", loggedIn = fenix_blueprint.session.authorized)

#function to authenticate and access to UserPage or AdminPage acording to the type of user
@app.route('/API/admin/')
def AdminPages(): 
    #create new message exchange
    #function to get the IP of the user that is logged In and using the browser
    ip = request.environ['REMOTE_ADDR']
    CreateNewMessage(ip,"/API/admin/")
    user = CurrentUser()

    #if the user is not in the user database it is necessary to be stored
    if (getUser(user['username']) == None):
        Authentication("AdminPage")
        
    user_data = getUserDICT(user['username'])
    #verify the type of the user , Admin or Regular
    if (user_data["type_user"]=="Admin"):
        print("Administrador")
        return render_template("Admin.html")
    else:
        print("Apenas os administradores podem aceder a esta página!")
        return render_template("UserPage.html")

#function to get access to thet VideoListing.html Page 
@app.route('/API/videolist/')
def VideoListing():
    #create new message exchange
    ip = request.environ['REMOTE_ADDR']
    CreateNewMessage(ip,"/API/videolist/")

    user = CurrentUser()

    if (getUser(user['username']) == None):
        Authentication("videoList")

    return render_template("VideoListing.html")

#function to access a the page of the video with video id = id
@app.route('/API/videopage/<int:id>/',methods=['GET'])
def VideoPage(id):
    #create new message exchange
    video_id = str(id)
    ip = request.environ['REMOTE_ADDR']
    CreateNewMessage(ip,"/API/videopage/" + video_id + "/")
    v = getVideoDICT(id)
    url = v["url"]
    title = v["title"]
    user = CurrentUser()
    user = user['username']
    increase_nr_views(user)

    #send info to the VideoPage.html
    return render_template("VideoPage.html", id = id, url = url, title = title)

#function to create a user in the user database, method = POST, user is being added to the database
@app.route("/API/users/", methods=['POST'])
def createNewUser(username, name, type_user):
    ret = False
    user = CurrentUser()
    try:
        ret = newUser(username, name,type_user)
    except:
        abort(400)
        #the arguments were incorrect
    content = username + ", "+ name +", " + type_user
    if ret:
        #create new message exchange and new data
        
        ip = request.environ['REMOTE_ADDR']
        CreateNewMessage(ip,"/API/users/")
        CreateNewData("User",content,user)
        
        return {"username": ret}
    else:
        abort(409)
        #if there is an erro return ERROR 409
#function to obtain the list of users in the data base , methods = GET
@app.route("/API/users/", methods=['GET'])
def returnsUsersJSON():
    #create new message exchange
    ip = request.environ['REMOTE_ADDR']
    CreateNewMessage(ip, "/API/users/")
    #returns the list of users
    return {"users": listUsersDICT()}

#function to obtain the user with username = username, returns a single user , methods = GET
@app.route("/API/users/<string:username>/", methods=['GET'])
def returnSingleUserJSON(username):
    try:
        v = getUserDICT(username)
        #create new message exchange
        ip = request.environ['REMOTE_ADDR']
        CreateNewMessage(ip,"/API/users/"+username+"/")
        return v
    except:
        abort(404)
    
#function to add a new video to the database , methods = POST
@app.route("/API/videos/", methods=['POST'])
def createNewVideo():
    sleep(0.1)
    user = CurrentUser()
    user = user['username']
    j = request.get_json()
    content = j["url"] + ", " + j["title"]
    ret = False
    try:
        ret = newVideo(j["url"], j["title"], user)
        increase_nr_videos(user)
    except:
        abort(400)
        #the arguments were incorrect
    if ret:
        #create new message exchange and data creation
        ip = request.environ['REMOTE_ADDR']
        CreateNewMessage(ip,"/API/videos/")
        CreateNewData("Video",content,user)
        
        return {"id": ret}
    else:
        abort(409)
        #if there is an erro return ERROR 409
    
#function to obtain the list of videos in the database, methods = GET
@app.route("/API/videos/", methods=['GET'])
def returnsVideosJSON():
    #create new message exchange
    ip = request.environ['REMOTE_ADDR']
    CreateNewMessage(ip,"/API/videos/")
    return {"videos": listVideosDICT()}

#function to obtain the video with video_id = id in the database, methods = GET
@app.route("/API/videos/<int:id>/", methods=['GET'])
def returnSingleVideoJSON(id):
    video_id = str(id)
    #create new message exchange
    ip = request.environ['REMOTE_ADDR']
    CreateNewMessage(ip,"/API/videos/" + video_id + "/")
    try:
        v = getVideoDICT(id)
        return v
    except:
        abort(404)

#function to create a question for the video with video_id = id, methods = POST
@app.route("/API/videos/<int:id>/questions/", methods=['POST'])
def createNewQuestion(id):

    user = CurrentUser()
    user = user['username']
    j = request.get_json()
    ret = False
    v_id = str(j["id"])
    timestamp = str(j["time"])
    content = v_id + ", "+ timestamp + ", "+ j["text"]
    try:
        ret = newQuestion(j["id"], j["time"], user, j["text"])
        increase_nr_questions(user)
    except:
        abort(400)
        #the arguments were incorrect
    if ret:
        v_id = str(id)
        #create new message exchange and data creation
        ip = request.environ['REMOTE_ADDR']
        CreateNewMessage(ip,"/API/videos/"+v_id+"/questions/")
        CreateNewData("Question",content,user)
        
        return {"id": ret}
    else:
        abort(409)

#function to get the list of question of video with id in the database, methods = GET
@app.route("/API/videos/<int:id>/questions/", methods=['GET'])
def returnsQuestionsJSON(id):
    #create new message exchange
    v_id = str(id)
    ip = request.environ['REMOTE_ADDR']
    CreateNewMessage(ip,"/API/videos/"+v_id+"/questions/")
    
    return {"questions": listQuestionsDICT(id)}

#function to return question of the video with id and question with id, methods = GET
@app.route("/API/videos/<int:id>/<int:q_id>/", methods=['GET'])
def returnQuestion(id,q_id):
    try:
        question = getQuestionDICT(id,q_id)
        user = question['user']
        u = getUserDICT(user)
        video_id = str(id)
        question_id = str(q_id)
        #create new message exchange
        ip = request.environ['REMOTE_ADDR']
        CreateNewMessage(ip,"/API/videos/"+video_id+"/"+question_id+"/")
        
        return {"Question": question, "user": u}
    except:
        abort(404)

#function to create an answer of a question of a video, in the database, methods = POST
@app.route("/API/videos/<int:id>/<int:q_id>/answers/", methods=['POST'])
def createNewAnswer(id,q_id):
    #sleep(0.1)
    user = CurrentUser()
    user = user['username']
    j = request.get_json()
    ret = False
    v_id = str(id)
    question = str(q_id)
    content = v_id + ", "+ j["answer"] + ", " + question
    try:
        ret = newAnswer(id, user, j["answer"], q_id) 
    except:
        abort(400)
        #the arguments were incorrect
    if ret:
        increase_nr_answers(user)
        v_id = str(id)
        question  = str(q_id)
        #create new message exchange and datacreation
        ip = request.environ['REMOTE_ADDR']
        CreateNewMessage(ip,"/API/videos/"+v_id+"/"+question+"/answers/")
        CreateNewData("Answer",content,user)
        
        return {"id": ret}
    else:
        abort(409)
    
#function to return the list of answers of a certain question of a video, methods = GET
@app.route("/API/videos/<int:id>/<int:q_id>/answers/", methods=['GET'])
def returnAnswersJSON(id,q_id):
    answer = listAnswersDICT(q_id)
    v_id = str(id)
    question  = str(q_id)
    #create new message exchange
    ip = request.environ['REMOTE_ADDR']
    CreateNewMessage(ip,"/API/videos/"+v_id+"/"+question+"/answers/")

    return {"answers": answer}

#function to obtain the list of messages in the database, methods = GET
@app.route("/API/messages/", methods = ['GET'])
def returnMessagesJSON():
    mess = listMessagesDICT()
    #create new message exchange
    ip = request.environ['REMOTE_ADDR']
    CreateNewMessage(ip,"/API/messages/") 
    
    return {"messages": mess}

#function to obtain the list of datacreation in the database, methods = GET
@app.route("/API/datacreation/", methods = ['GET'])
def returnDataJSON():
    data = listDataDICT()
    #create new message exchange
    ip = request.environ['REMOTE_ADDR']
    CreateNewMessage(ip,"/API/datacreation/") 

    return {"data": data}

#function to access to the LogsPage.html and obtain the logs info
@app.route("/API/logshtml/", methods = ['GET'])
def renderLogsPage():
    #create new message exchange
    ip = request.environ['REMOTE_ADDR']
    CreateNewMessage(ip, "/API/logshtml/")
    return  render_template("LogsPage.html")

#function to access to the AdminPage.html and obtain the userstatistcs info
@app.route("/API/statshtml/", methods = ['GET'])
def renderStatsPage():
    #create new message exchange
    ip = request.environ['REMOTE_ADDR']
    CreateNewMessage(ip, "/API/statshtml/")
    return  render_template("AdminPage.html")


if __name__ == "__main__":
    app.run(debug=True)