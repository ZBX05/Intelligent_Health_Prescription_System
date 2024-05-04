import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

class Test:
    def __init__(self,email:str,password:str,url:str) -> None:
        self.email=email
        self.password=password
        self.url=url
    
    def start(self) -> None:
        self.driver=webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.get(self.url)
    
    def stop(self) -> None:
        self.driver.close()
    
    def login(self) -> None:
        self.driver.find_element(by=By.ID,value='email').send_keys(self.email)
        self.driver.find_element(by=By.ID,value='password').send_keys(self.password)
        self.driver.find_element(by=By.ID,value='btn-login').click()
        self.driver.implicitly_wait(5)
    
    def ask(self,question:str) -> str:
        text=self.driver.find_element(by=By.ID,value='question-text')
        text.send_keys(question)
        self.driver.find_element(by=By.ID,value='btn-submit').click()
        sleep(3)
        answer=self.driver.find_element(by=By.ID,value='answer').get_attribute('innerHTML').split('</b>')[-1]
        text.clear()
        return answer
    
    def test(self,data:pd.DataFrame) -> list:
        self.start()
        self.login()
        result=[]
        for question in data["question"]:
            result.append(self.ask(question))
        self.stop()
        return result
    
    def __call__(self,data:pd.DataFrame) -> list:
        return self.test(data)
