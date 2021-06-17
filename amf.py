import requests
import pyamf
from pyamf import remoting
from pyamf.flex import messaging
import uuid
import time

AMF_NAMESPACE = 'com.herffjones.edesign.messages'
username = input('username: ')
password = input('password: ')
serviceUUID = '3db6f56c-0d9c-4c16-adf2-26ca8f49caee'
version = int(time.time()*1000 + 10**12)
documentId = 3930316147
applicationId = 5
orderId = float('nan')

class GetDocumentRequest(object):
    def __init__(self, documentId, ticketId, applicationId, count, orderId):
        self.documentId = documentId
        self.ticketId = ticketId
        self.applicationId = applicationId
        self.count = count
        self.orderId = orderId

    def __repr__(self):
        return self.__dict__

class GetUserRequest(object):
    def __init__(self, version, username, serviceUUID, applcation):
        self.version = version
        self.username = username
        self.serviceUUID = serviceUUID
        self.application = applcation

    def __repr__(self):
        return self.__dict__

class QueryEntityIdsRequest(object):
    def __init__(self, entityClass, orderings, criterion, distinct, applicationId, orderId, count, ticketId):
        self.entityClass = entityClass
        self.orderings = orderings
        self.criterion = criterion
        self.distinct = distinct
        self.applicationId = applicationId
        self.orderId = orderId
        self.count = count
        self.ticketId = ticketId
    
    def __repr__(self):
        return self.__dict__

class AssetOrdering(object):
    def __init__(self, assetType, headerToSortOn, caseInsensitive, path, sortType):
        self.assetType = assetType
        self.headerToSortOn = headerToSortOn
        self.caseInsensitive = caseInsensitive
        self.path = path
        self.sortType = sortType

    def __repr__(self):
        return self.__dict__

class AssetCriterion(object):
    def __init__(self, includeSecret, justSecret, documentId, assetType):
        self.includeSecret = includeSecret
        self.justSecret = justSecret
        self.documentId = documentId
        self.assetType = assetType
    
    def __repr__(self):
        return self.__dict__

class GetEntitiesRequest(object):
    def __init__(self, entityIds, klasses, applicationId, orderId, count, ticketId):
        self.entityIds = entityIds
        self.klasses = klasses
        self.applicationId = applicationId
        self.orderId = orderId
        self.count = count
        self.ticketId = ticketId
    
    def __repr__(self):
        return self.__dict__

def register_classes():
    pyamf.register_class(GetDocumentRequest, '{}.GetDocumentRequest'.format(AMF_NAMESPACE))
    pyamf.register_class(GetUserRequest, '{}.GetUserRequest'.format(AMF_NAMESPACE))
    pyamf.register_class(QueryEntityIdsRequest, '{}.QueryEntityIdsRequest'.format(AMF_NAMESPACE))
    pyamf.register_class(AssetOrdering, '{}.AssetOrdering'.format(AMF_NAMESPACE))
    pyamf.register_class(AssetCriterion, '{}.AssetCriterion'.format(AMF_NAMESPACE))
    pyamf.register_class(GetEntitiesRequest, '{}.GetEntitiesRequest'.format(AMF_NAMESPACE))

def authenticate_request_bin():
    msg = messaging.CommandMessage(operation=5,
                                   messageId=str(uuid.uuid4()).upper(),
                                   headers={
                                        'DSMessagingVersion': 1,
                                        'DSId':'nil'
                                   })
    req = remoting.Request(target='null', body=[msg])
    env = remoting.Envelope(pyamf.AMF3)
    env['/1'] = req

    return remoting.encode(env).getvalue()

def user_request_bin(DSId, serviceUUID):
    msg = messaging.RemotingMessage(operation='perform',
                                    destination='blazeServiceEndPoint',
                                    messageId=str(uuid.uuid4()).upper(), #'FCB40DA3-A988-E785-42FC-11A5BDE6F80A',
                                    headers={
                                        'DSId': DSId,
                                        'DSRequestTimeout': 300,
                                        'DSEndpoint':'nrt-amf'
                                    },
                                    body=[GetUserRequest(version, username, serviceUUID, 'EDESIGN')])
    req = remoting.Request(target='null', body=[msg])
    env = remoting.Envelope(pyamf.AMF3)
    env['/2'] = req

    return remoting.encode(env).getvalue()

def document_request_bin(DSId, ticketId):
    msg = messaging.RemotingMessage(operation='perform',
                                    destination='blazeServiceEndPoint',
                                    messageId=str(uuid.uuid4()).upper(), #'FCB40DA3-A988-E785-42FC-11A5BDE6F80A',
                                    headers={
                                        'DSId': DSId,
                                        'DSRequestTimeout': 300,
                                        'DSEndpoint':'nrt-amf'
                                    },
                                    body=[GetDocumentRequest(documentId, ticketId, applicationId, 1, orderId)])
    req = remoting.Request(target='null', body=[msg])
    env = remoting.Envelope(pyamf.AMF3)
    env['/2'] = req

    return remoting.encode(env).getvalue()

def portrait_query_bin(DSId, ticketId):
    msg = messaging.RemotingMessage(operation='perform',
                                    destination='blazeServiceEndPoint',
                                    messageId=str(uuid.uuid4()).upper(), #'FCB40DA3-A988-E785-42FC-11A5BDE6F80A',
                                    headers={
                                        'DSId': DSId,
                                        'DSRequestTimeout': 300,
                                        'DSEndpoint':'nrt-amf'
                                    },
                                    body=[QueryEntityIdsRequest(entityClass='PortraitVO',
                                                                orderings=[AssetOrdering('PortraitVO', 'Date', False, None, 'ASC')],
                                                                criterion=AssetCriterion(False, False, documentId, 'PortraitVO'),
                                                                distinct=False,
                                                                applicationId=applicationId,
                                                                orderId=orderId,
                                                                count=17,
                                                                ticketId=ticketId)])
    req = remoting.Request(target='null', body=[msg])
    env = remoting.Envelope(pyamf.AMF3)
    env['/2'] = req

    return remoting.encode(env).getvalue()

def portraits_request_bin(DSId, ticketId, entityIds, klasses):
    msg = messaging.RemotingMessage(operation='perform',
                                    destination='blazeServiceEndPoint',
                                    messageId=str(uuid.uuid4()).upper(), #'FCB40DA3-A988-E785-42FC-11A5BDE6F80A',
                                    headers={
                                        'DSId': DSId,
                                        'DSRequestTimeout': 300,
                                        'DSEndpoint':'nrt-amf'
                                    },
                                    body=[GetEntitiesRequest(entityIds, klasses, applicationId, orderId, len(entityIds) + 10, ticketId)])
    req = remoting.Request(target='null', body=[msg])
    env = remoting.Envelope(pyamf.AMF3)
    env['/2'] = req

    return remoting.encode(env).getvalue()

if __name__ == '__main__':
    register_classes()
    
    ses = requests.session()

    r1 = ses.get('https://cas.prod.casaws.herffjones.com/index.cfm/General/login/?service=ybportal')

    cookies = dict(r1.cookies)
    # print(cookies)
    payload = {
        'username': username,
        'password': password,
        'service': 'ybportal',
        'returnURL': 'https://hjedesign.com/eDesign.html?citrix=yes'
    }
    r2 = ses.post('https://cas.prod.casaws.herffjones.com/index.cfm/General/doLogin', cookies=cookies, data=payload)

    print(r2.text)

    # r25 = ses.get('https://hjedesign.com/eDesign.swf?v=' + str(version))

    # with open('15_Requestb.txt', 'rb') as f:
    #     data = f.read()
    r3 = ses.post('https://hjedesign.com/eDesignServices/messagebroker/nrtamf', cookies=cookies, data=authenticate_request_bin())
    c3 = remoting.decode(r3.content)
    DSId = c3.bodies[0][1].body.headers['DSId']

    r4 = ses.post('https://hjedesign.com/eDesignServices/messagebroker/nrtamf', cookies=cookies, data=user_request_bin(DSId, serviceUUID))
    c4 = remoting.decode(r4.content)
    ticketId = c4.bodies[0][1].body.body['ticketId']

    r5 = ses.post('https://hjedesign.com/eDesignServices/messagebroker/nrtamf', cookies=cookies, data=document_request_bin(DSId, ticketId))
    c5 = remoting.decode(r5.content)

    r6 = ses.post('https://hjedesign.com/eDesignServices/messagebroker/nrtamf', cookies=cookies, data=portrait_query_bin(DSId, ticketId))
    c6 = remoting.decode(r6.content)
    entityIds = c6.bodies[0][1].body.body['entityIds']

    r7 = ses.post('https://hjedesign.com/eDesignServices/messagebroker/nrtamf', cookies=cookies, data=portraits_request_bin(DSId, ticketId, entityIds, ['AssetVO'] * len(entityIds)))
    c7 = remoting.decode(r7.content)
    print(c7)