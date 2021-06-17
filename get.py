import aiohttp
import asyncio
from amf import *
from pyamf import remoting
import PyPDF2
import PyPDF2.utils
import pdfrw
import os

async def login(session):
    print('getting login page')
    login_page = await session.get('https://cas.prod.casaws.herffjones.com/index.cfm/General/login/?service=ybportal')
    cookies = login_page.cookies

    payload = {
        'username': username,
        'password': password,
        'service': 'ybportal',
        'returnURL': 'https://hjedesign.com/eDesign.html?citrix=yes'
    }   
    print('logging in')
    await session.post('https://cas.prod.casaws.herffjones.com/index.cfm/General/doLogin', cookies=cookies, data=payload)
    
    print('authenticating')
    r1 = await session.post('https://hjedesign.com/eDesignServices/messagebroker/nrtamf', cookies=cookies, data=authenticate_request_bin())
    auth = remoting.decode(await r1.read())
    DSId = auth.bodies[0][1].body.headers['DSId']

    print('getting user')
    r2 = await session.post('https://hjedesign.com/eDesignServices/messagebroker/nrtamf', cookies=cookies, data=user_request_bin(DSId, serviceUUID))
    user = remoting.decode(await r2.read())
    ticketId = user.bodies[0][1].body.body['ticketId']
    return (cookies, DSId, ticketId)

async def get_spreads_list(session, cookies, DSId, ticketId):
    print('getting file list')
    r1 = await session.post('https://hjedesign.com/eDesignServices/messagebroker/nrtamf', cookies=cookies, data=document_request_bin(DSId, ticketId))
    document = remoting.decode(await r1.read())
    
    spreads = []
    for s in document.bodies[0][1].body.body['document']['spreads']:
        if s['right'] is None:
            name = str(s['left']['number']) + '.pdf'
            v = f"{int(s['left']['entityVersion'])}.{int(s['left']['state']['entityVersion'])}"
            command = f"render[pageid={int(s['left']['id'])}]"
        elif s['left'] is None:
            name = str(s['right']['number']) + '.pdf'
            v = f"{int(s['right']['entityVersion'])}.{int(s['right']['state']['entityVersion'])}"
            command = f"render[pageid={int(s['right']['id'])}]"
        else:
            name = f"{str(s['left']['number'])}-{str(s['right']['number'])}.pdf"
            v = f"{int(s['left']['entityVersion'])}.{int(s['left']['state']['entityVersion'])}.{int(s['right']['entityVersion'])}.{int(s['right']['state']['entityVersion'])}"
            command = f"render[spreadid={int(s['id'])}]"
        spreads.append((name,v,command))
    return spreads

async def get_portraits_list(session, cookies, DSId, ticketId):
    print('getting portraits list')
    r1 = await session.post('https://hjedesign.com/eDesignServices/messagebroker/nrtamf', cookies=cookies, data=portrait_query_bin(DSId, ticketId))
    c1 = remoting.decode(await r1.read())
    entityIds = c1.bodies[0][1].body.body['entityIds']

    r2 = await session.post('https://hjedesign.com/eDesignServices/messagebroker/nrtamf', cookies=cookies, data=portraits_request_bin(DSId, ticketId, entityIds, ['AssetVO'] * len(entityIds)))
    c2 = remoting.decode(await r2.read())
    return c2.bodies[0][1].body.body['entities']

async def fetch_pdf(session, name, v, ticketId, command, cookies):
    print('fetching ' + name)
    async with session.get('https://hjedesign.com/eDesignServices/RenderPDFServlet/{}?v={}&ticketid={}&command={}&svg=null&JSESSIONID={}'.format(name, v, ticketId, command, cookies['JSESSIONID'].value), cookies=cookies) as response:
        return (name, await response.read())

async def fetch_pdfs(session, spreads, ticketId, cookies):
    tasks = []
    for s in spreads:
        task = asyncio.ensure_future(fetch_pdf(session, s[0], s[1], ticketId, s[2], cookies))
        tasks.append(task)

    return await asyncio.gather(*tasks)

async def fetch_and_save_img(session, entity, cookies):
    print('fetching ' + entity['name'])
    async with session.get('https://hjedesign.com/eDesignServices/ImageGetServlet?v=0&command=getimage[uuid={}]&JSESSIONID={}'.format(entity['UUID'], cookies['JSESSIONID'].value), cookies=cookies) as response:
        data = await response.read()
    try:
        grade = str(int(entity['grade'])).zfill(3)
    except ValueError:
        grade =  entity['grade']
    file_name = f"{grade}_{entity['lastName']}_{entity['firstName']}.jpg".upper()
    print('saving ' + file_name)
    file_path = os.path.join('portraits', grade, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(data)
    return file_path

async def fetch_and_save_imgs(session, entities, cookies):
    tasks = []
    for entity in entities:
        task = asyncio.ensure_future(fetch_and_save_img(session, entity, cookies))
        tasks.append(task)
    return await asyncio.gather(*tasks)

def process_pdfs(responses):
    print('processing pdfs')
    responses = sorted(responses, key=lambda r: int(r[0].strip('-').split('.')[0].split('-')[0]))
    opages = []
    for r in responses:
        try:
            ipages = pdfrw.PdfReader(fdata=r[1]).pages
        except pdfrw.errors.PdfParseError:
            continue
        if len(ipages) == 2:
            result = pdfrw.PageMerge() + ipages[0] + ipages[1]
            result[1].x += result[0].w
            result = result.render()
        elif len(ipages) == 1:
            result = ipages[0]
        else:
            assert None
            
        opages.append(result)

    pdfrw.PdfWriter('result.pdf').addpages(opages).write()

    with open('result.pdf', 'rb') as f:
        input = PyPDF2.PdfFileReader(f)
        output = PyPDF2.PdfFileWriter()
        for page in input.pages:
            width = page.mediaBox.upperRight[0]
            height = page.mediaBox.upperRight[1]
            if width == 660:
                if page.extractText().find('Odd\nPage') != -1:
                    page.cropBox.lowerLeft = (22,132)
                    page.cropBox.upperRight = (width-12, height-12)
                elif page.extractText().find('Even\nPage') != -1:
                    page.cropBox.lowerLeft = (12, 132)
                    page.cropBox.upperRight = (width-22, height-12)
                else:
                    assert None
            else:
                page.cropBox.lowerLeft = (12, 132)
                page.cropBox.upperRight = (width-12, height-12)
            output.addPage(page)
        with open('cropped_result.pdf', 'wb') as f:
            output.write(f)

async def run():
    async with aiohttp.ClientSession() as session:
        cookies, DSId, ticketId = await login(session)

        # spreads = await get_spreads_list(session, cookies, DSId, ticketId)
        # responses = await fetch_pdfs(session, spreads, ticketId, cookies)
        # process_pdfs(responses)

        entities = await get_portraits_list(session, cookies, DSId, ticketId)
        await fetch_and_save_imgs(session, entities, cookies)



if __name__ == '__main__':
    register_classes()

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run())
    loop.run_until_complete(future)