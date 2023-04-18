import random
import time
from bs4 import BeautifulSoup
import requests
import language_tool_python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

wge_idx = int(input('Введите id задания - '))
login = input('Введите логин - ')
password = input('Введите пароль - ')
auto = str(input('Выполнять полностью автоматически|y-yes or n-no - '))
if auto == "y":
    auto = True
if auto == 'n':
    auto = False
else:
    print('Error:Неправельный ввод')
    exit()
data = {
    "simora_login":login,
    "simora_pass":password,
}
error_time = 0.5
print('Загрузка...')
spell = language_tool_python.LanguageTool('ru-RU')
session = requests.session()
options = webdriver.ChromeOptions()
options.add_argument('headless')
session_selen = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
session_selen.get('https://login.cerm.ru')
session_selen.find_element(By.ID,  'txtLogin' ).send_keys(data['simora_login'])
session_selen.find_element(By.ID,  'txtPass' ).send_keys(data['simora_pass'])
session_selen.find_element(By.ID,  'login_button' ).click()
session_selen.get(f"https://login.cerm.ru/_user/user_app.php?mod=pwg&do=schema&wge_idx={wge_idx}&action=pExercise")
headers = {
"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",}
session.post('https://login.cerm.ru/_user/user_app.php',data = data,headers=headers)
session.get(f"https://login.cerm.ru/_user/user_app.php?mod=pwg&do=schema&wge_idx={wge_idx}&action=pExercise")
print("Загрузка завершина")
while True:
    tasks = session.post(f"https://login.cerm.ru/_user/user_app.php?exactmod=pwg&do=schema&wge_idx={wge_idx}&action=pState&reqState=gettask").json()
    if tasks['status'] == True:
        if tasks['data']['nextState'] == 'RNO':
            session_selen.refresh()
            soup = BeautifulSoup(session_selen.page_source,'lxml')
            try:
                error = soup.find(id = "trainer_rno_right").text
                session_selen.find_element(By.ID,'prno').send_keys(error)
                time.sleep(error_time)
                session_selen.find_element(By.ID,'prno').send_keys(error)
                time.sleep(error_time)
                session_selen.find_element(By.ID,'prno').send_keys(error)
            except:
                tasks = session.post(f"https://login.cerm.ru/_user/user_app.php?exactmod=pwg&do=schema&wge_idx={wge_idx}&action=pState&reqState=gettask").json()
                continue
        else:
            print('work')
            try:
                tasks = tasks['data']['stateData']['taskData']
            except:
                tasks = session.post(f"https://login.cerm.ru/_user/user_app.php?exactmod=pwg&do=schema&wge_idx={wge_idx}&action=pState&reqState=gettask").json()['data']['stateData']['taskData']
            variant_none = None
            for task in tasks:
                thisTimeTask = tasks[str(task)]
                id = thisTimeTask['id']
                text = thisTimeTask['masked'].capitalize()
                variants = []
                for variant in thisTimeTask['variants']:
                    if variant == '(слитно)':
                        variant = ''
                    if variant == '(дефис)':
                        variant = '-'
                    if variant == '(ничего)':
                        variant = ''
                        variant_none = True
                    if variant == '(раздельно)':
                        variant = ' '
                    if spell.check(text.replace('..',variant)) == []:
                        if variant == '':
                            if variant_none == True:
                                variant = '(ничего)'
                            else:
                                variant = '(слитно)'
                        if variant == ' ':
                            variant = '(раздельно)'
                        if variant == '-':
                            variant = '(дефис)'
                        variants.append(variant)
                if len(variants) != 1:
                    if auto:
                        variants.clear()
                        variants.append(thisTimeTask['variants'][random.randrange(len(thisTimeTask['variants']))])
                    else:
                        print(f"""
                              Возможна ошибка, введите верный ответ\n
                              слово - {text} \n
                              варианты - {thisTimeTask['variants']}\n
                              Введите только вариант ответа (как написанно)
                              """)
                        otvet = input('Ответ - ')
                        variants.clear()
                        variants.append(otvet)
                answer = session.post(f"https://login.cerm.ru/_user/user_app.php?exactmod=pwg&do=schema&wge_idx={wge_idx}&action=pState&reqState=setanswer&reqData[taskID]={id}&reqData[panswer]={variants[0]}",headers=headers).json()
                procent = session.get(f'https://login.cerm.ru/_user/user_app.php?mod=pwg&do=schema&wge_idx={wge_idx}&action=pMyProgress',headers=headers)
                procent_text = BeautifulSoup(procent.text,'lxml').find(class_ = "indicator_label").text
                try:
                    print(id,' - ',answer["data"]['nextState']=='ingame',procent_text)
                    if answer['data']['nextState'] == 'RNO':
                        session_selen.refresh()
                        soup = BeautifulSoup(session_selen.page_source,'lxml')
                        try:
                            error = soup.find(id = "trainer_rno_right").text
                            session_selen.find_element(By.ID,'prno').send_keys(error)
                            time.sleep(error_time)
                            session_selen.find_element(By.ID,'prno').send_keys(error)
                            time.sleep(error_time)
                            session_selen.find_element(By.ID,'prno').send_keys(error)
                        except:
                            pass
                    session.post(f"https://login.cerm.ru/_user/user_app.php?exactmod=pwg&do=schema&wge_idx={str(wge_idx)}&action=pState&reqState=save",headers=headers)
                except:
                    pass
    else:
        session_selen.refresh() 
        soup = BeautifulSoup(session_selen.page_source,'lxml')
        try:
            error = soup.find(id = "trainer_rno_right").text
            session_selen.find_element(By.ID,'prno').send_keys(error)
            time.sleep(error_time)
            session_selen.find_element(By.ID,'prno').send_keys(error)
            time.sleep(error_time)
            session_selen.find_element(By.ID,'prno').send_keys(error)
        except:
            session.post('https://login.cerm.ru/_user/user_app.php',data = data,headers=headers)
            session.get(f"https://login.cerm.ru/_user/user_app.php?mod=pwg&do=schema&wge_idx={wge_idx}&action=pExercise")