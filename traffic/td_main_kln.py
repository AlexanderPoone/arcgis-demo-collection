# from selenium import webdriver as wd
# from selenium.webdriver.firefox.options import Options

# options = Options()
# options.headless = True
# driver = wd.Firefox(options=options)

# driver.get('https://traffic.td.gov.hk/LiveProcessor.do')
# document.querySelector('#hk').click()

from subprocess import run, Popen, PIPE, STDOUT
import sys
from re import findall, sub
import websockets
import asyncio


# run()

# sub()

# findres = findall(r'H[0-9]{3}')

# if len(findres) > 0:
#     camCode = findres[0]

#     if camCode == 'H106F':
#     elif camCode == 'H109F':
#     elif camCode == 'H207F':
#     elif camCode == 'H210F':
#     elif camCode == 'H801F':

# run()



# Find chunk
from seleniumwire import webdriver
# from seleniumwire.webdriver.firefox.options import Options
from time import sleep

# options = Options()
# options.headless = True
options = webdriver.FirefoxOptions()
options.add_argument('--headless')


driver = webdriver.Firefox(options=options)


driver.get('https://traffic.td.gov.hk/LiveProcessor.do') #'https://traffic.td.gov.hk/webvideo.jsp')

sleep(3)

driver.execute_script("document.querySelector('#kl').click()")

sleep(3)

driver.execute_script("document.querySelector('.vjs-big-play-button').click()")

sleep(3)

for request in driver.requests:
    if request.response:
        if 'chunklist' in request.url:
            print(request.url)
        # print(
        #     request.url,
        #     request.response.status_code,
        #     request.response.headers['Content-Type']
        # )

            with open(r'C:\Users\Alex\Desktop\yolov5_kln\utils\datasets.py', 'r+') as f:
                datasets = f.read()

                datasets = sub(r"(?<=sources = \[').+?(?='\])", request.url, datasets)

                f.seek(0)

                f.write(datasets)

#python detect.py --source "http://webcast.td.gov.hk/live/mp4:hk/chunklist_w736548841.m3u8?token=0NiFTYFCx2NiExGu2AbTDg%3D%3D" --weights runs/train/exp19/weights/best.pt --save-txt --name temp
process = Popen(r'python C:\Users\Alex\Desktop\yolov5_kln\detect.py --source http://webcast.td.gov.hk/live/mp4:hk/chunklist_w736548841.m3u8?token=0NiFTYFCx2NiExGu2AbTDg%3D%3D --weights C:\Users\Alex\Desktop\yolov5_kln\runs/train/exp19/weights/best.pt', shell=True, stdout=PIPE, stderr=STDOUT)

while True:
    nextline = process.stdout.readline().decode(encoding='utf8')
    # websocket.send(nextline)
    if nextline == '' and process.poll() is not None:
        break
    open('tmp_kln.tmp', 'w').write(nextline)
    # sys.stdout.write(nextline)
    # sys.stdout.flush()

output = process.communicate()[0]
exitCode = process.returncode


# SELF-TEST BELOW ##############################################

# import websockets
# import asyncio

# async def hello():
#     uri = "ws://demo2.hkgisportal.com:6180/aptraffic"
#     async with websockets.connect(uri) as websocket:
#         for x in range(100000):
#             name = '''
#             {
#         "type": "LineString", 
#         "coordinates": [
#             [30, 10], [10, 30], [40, 40]
#         ],
#         "count": 12345
#     }
#             '''
#             await websocket.send(name)
#             await asyncio.sleep(2)

# asyncio.get_event_loop().run_until_complete(hello())