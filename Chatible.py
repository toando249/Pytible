﻿import app
from urllib.parse import urlparse
from ChatfuelAPI import ChatfuelAPI
import random
import datetime
def isFacebookMessage(url):
    o = urlparse(url)
    if o.scheme != 'https': 
        return False
    if ('fbcdn.net' in o.hostname) and (o.path.endswith('.png') or o.path.endswith('.jpg') or o.path.endswith('.jpeg') or o.path.endswith('.gif')):
        return url.split(" ")
    return False

def isCommand(msg):
    if(msg.startswith("//")):
        return msg.split("//")[1]
    return False

def handleUser(senderId,timestamp,message,name,profile_pic,gender):
        usersCollection = app.mongo.db.Users
        result = usersCollection.find_one({'_id':int(senderId)})
        if result is None:
            usersCollection.insert_one({ "_id": int(senderId), "idCouple":None, "status": 1, "favorite":'any' , "timestamp": timestamp, "name": name, "gender": gender, "profile_pic": profile_pic})
            if(isCommand(message)):
                code(senderId,isCommand(message).lower(),1)
            else:
                handleMessage(senderId,"Chờ 1 chút nhaaa :D Đang tìm bạn cho bạn nèee","text")
                startSession()
        else:
            status = result['status']
            if(isCommand(message)):
                code(senderId,isCommand(message).lower(),status)
            else:
                if(status==0):
                    usersCollection.update_one({"_id":int(senderId)},{"$set":{"status":1,"timestamp":timestamp}})
                    handleMessage(senderId,"Đang tìm bạn cho bạn nèee","text")
                    startSession()
                if(status==1):
                    if(message.lower()=="pp"):
                            baibai(senderId)
                    else:
                        handleMessage(senderId,"Bình tĩnh nào D:","text")
                if(status==2):
                    partnerId = result['idCouple']
                    isImage = isFacebookMessage(message)
                    if(isImage):
                        handleMessage(partnerId,isImage,"image")
                    else:
                        if(message.lower()=="pp"):
                            baibai(senderId,partnerId)
                        else:
                            handleMessage(partnerId,message,"text")

def handleMessage(senderId,msg,type):
    if(type=="text"):
        ChatfuelAPI.sendText(senderId,msg)
    if(type=="image"):
        for img in msg:
            ChatfuelAPI.sendImage(senderId,img)

def findUser(senderFavorite, senderGender, senderId):
    usersCollection = app.mongo.db.Users
    if(senderFavorite == 'any'):
        result = list(usersCollection.find({"$or":[{"favorite": senderGender},{"favorite":"any"}],"status":1,"_id":{"$ne":senderId}})) 
        if(len(result)==0):
            return senderId
        recId = senderId
        while recId == senderId:
            recId = result[random.randint(0,len(result)-1)]["_id"]
        return recId
    else:
        result = list(usersCollection.find({"$or":[{ "favorite": senderGender },{ "favorite": "any" }],"gender": senderFavorite,"status":1, "_id":{"$ne":senderId}}))
        if(len(result)==0):
            return senderId
        recId = senderId
        while recId == senderId:
            recId = result[random.randint(0,len(result)-1)]["_id"]
        return recId
                        
def startSession():
    usersCollection = app.mongo.db.Users
    result = list(usersCollection.find({"status":1}).sort("timestamp",1))
    if(len(result)>1):
        i=0
        user1 = result[i]["_id"]
        user2 = findUser(result[i]["favorite"],result[i]["gender"],user1)
        while user1==user2:
            if i < len(result)-1:
                i=i+1
            user1 = result[i]["_id"]
            user2 = findUser(result[i]["favorite"],result[i]["gender"],user1)
            if(i==len(result)-1):
                return handleMessage(user1,'Vui lòng chờ 1 chút nhaa vì chúng mình không tìm được bạn hoặc là bạn có thể hủy lần tìm này bằng "pp" và chọn sở thích khác :<','text')
        usersCollection.update_one({"_id":int(user1)},{"$set":{"status":2,"timestamp":None,"idCouple":user2}})
        usersCollection.update_one({"_id":int(user2)},{"$set":{"status":2,"timestamp":None,"idCouple":user1}})
        handleMessage(user1,"Hì tìm thấy bạn rùi thử chào nhau 1 câu xem nàoo. Để kết thúc hãy nhắn pp nhéee","text")
        handleMessage(user2,"Hì tìm thấy bạn rùi thử chào nhau 1 câu xem nàoo. Để kết thúc hãy nhắn pp nhéee","text")
def baibai(senderId,partnerId=None):
    usersCollection = app.mongo.db.Users
    usersCollection.update_one({"_id":int(senderId)},{"$set":{"status":0,"idCouple":None}})
    handleMessage(senderId,"Bạn đã kết thúc cuộc trò chuyện này :(","text")
    if(partnerId!=None):
        usersCollection.update_one({"_id":int(partnerId)},{"$set":{"status":0,"idCouple":None}})
        handleMessage(partnerId,"Bạn kia đã kết thúc cuộc trò chuyện này :( Đừng buồn nhé tiếp tục tìm bạn khác nàooo","text")

def code(senderId,msg,status):
    msg = msg.lower()
    if(msg=="win" or msg == "installwin" or msg == "windao"):
        if(status==0):
            if(senderId!=2101621863200974):
                usersCollection = app.mongo.db.Users
                resultHn = usersCollection.find_one({ "_id": int(2101621863200974)})
                if(resultHn['status']==2):
                    handleMessage(senderId,":( Không thể kết nối được vì bạn ý đang bận","text")
                else:
                    handleMessage(senderId,"Đã kết nối với người dùng bạn cài win","text")
                    handleMessage(2101621863200974,"Có người cần nhờ bạn cài win","text")
                    usersCollection.update_one({"_id":int(senderId)},{"$set":{"status":2,"timestamp":None,"idCouple":2101621863200974}})
                    usersCollection.update_one({"_id":int(2101621863200974)},{"$set":{"status":2,"timestamp":None,"idCouple":senderId}})
            else:
                handleMessage(senderId,"Bạn đã bị chặn sử dụng tính năng này","text")
        else:
            handleMessage(senderId,"Vui lòng hủy cuộc trò chuyện để sử dụng","text")
    if(msg=="favorite" or msg == "fav"):
        if(status==0):
            ChatfuelAPI.sendChangeFavorite(senderId)
        else:
            handleMessage(senderId,"Vui lòng cuộc trò chuyện hoặc yêu cầu tìm bạn để chọn người sẽ bắt cặp tiếp theo nhé","text")

def setFavorite(senderId,favorite):
    usersCollection = app.mongo.db.Users
    result = usersCollection.find_one({"_id":int(senderId)})
    if result["status"]==0:
        usersCollection.update_one({"_id":int(senderId)},{"$set":{"favorite":favorite}})
        handleMessage(senderId,"Bạn đã đổi thành công","text")
    else:
        handleMessage(senderId,'Vui lòng hủy yêu cầu tìm bạn hoặc kết thúc cuộc trò chuyện bằng cách gõ "pp"',"text")
        


