from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

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
        self.driver.find_element_by_xpath('//li[@class="nav-item"][2]/a').click()
        self.driver.implicitly_wait(5)
    
    def search(self,node:str) -> bool:
        search=self.driver.find_element(by=By.ID,value='search')
        search.send_keys(node)
        self.driver.find_element(by=By.ID,value='btn-search').click()
        self.driver.implicitly_wait(5)
        search.clear()
        try:
            self.driver.find_element_by_xpath('//*[@class="node-text"]')
        except:
            return False
        return True
    
    def test(self,data:pd.DataFrame) -> list:
        result=[]
        self.start()
        self.login()
        for disease in data["disease"]:
            result.append(self.search(disease))
        self.stop()
        return result

    def __call__(self,data:str) -> list:
        return self.test(data)