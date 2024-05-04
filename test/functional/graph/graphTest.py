from selenium import webdriver
from selenium.webdriver.common.by import By

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

    def display(self) -> bool:
        self.driver.find_element_by_xpath('//li[@class="nav-item"][2]/a').click()
        self.driver.implicitly_wait(5)
        try:
            self.driver.find_element_by_xpath('//*[@class="node-text"]')
        except:
            return False
        return True
    
    def logout(self) -> None:
        self.driver.find_element_by_xpath('//button[@class="btn btn-outline-light"]').click()
        self.driver.find_element(by=By.ID,value='btn-logout').click()
    
    def test(self,num:int) -> list:
        result=[]
        self.start()
        for _ in range(num):
            self.login()
            result.append(self.display())
            self.logout()
        self.stop()
        return result

    def __call__(self,num:int) -> list:
        return self.test(num)