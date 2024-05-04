import pymysql as sql
import random

class Database:
    def __init__(self,host:str,port:int,user:str,password:str,target:str) -> None:
        self.host=host
        self.port=port
        self.user=user
        self.password=password
        self.target=target
        try:
            self.db=sql.connect(host=self.host,port=self.port,user=self.user,password=self.password,db=self.target,
                                charset='utf8mb4',autocommit=True)
            self.cursor=self.db.cursor()
        except:
            raise Exception()

    def get_sql_info(self) -> tuple:
        return (self.host,self.port,self.user,self.password,self.target)

    def connectDatabase(self,host:str,port:int,user:str,password:str,target:str) -> bool:
        self.host=host
        self.port=port
        self.user=user
        self.password=password
        self.target=target
        try:
            self.db=sql.connect(host=host,port=port,user=user,password=password,db=target,charset='utf8mb4',autocommit=True)
            self.cursor=self.db.cursor()
            return True
        except:
            return False
    
    def ping(self,reconnect=bool) -> None:
        try:
            self.db.ping(reconnect)
        except Exception as e:
            raise e

    def get_user_data(self,email:str) -> tuple|None:
        self.cursor.execute("select * from user where email=%s",(email))
        return self.cursor.fetchone()

    def check_user_email(self,email:str) -> str|None:
        self.cursor.execute("select email from user where email=%s",(email))
        result=self.cursor.fetchone()
        if(result is not None):
            return result[0]
        else:
            return None
    
    def check_user_password(self,email:str,password_need_to_check:str) -> bool:
        self.cursor.execute("select pswd from user where email=%s",(email))
        password=self.cursor.fetchone()[0]
        return True if password_need_to_check==password else False
    
    def set_user_password(self,email:str,password:str) -> None:
        self.cursor.execute("update user set pswd=%s where email=%s",(password,email))
        self.db.commit()

    def set_user_state(self,email:str,user_state:str) -> None:
        self.cursor.execute("update user set user_state=%s where email=%s",(user_state,email))
        self.db.commit()
    
    def create_user(self,email:str,password:str) -> None:
        self.cursor.execute("insert into user(email,pswd) values (%s,%s)",(email,password))
        self.db.commit()

    def create_message(self,email:str,admin:str,send_time:str,content:str) -> None:
        self.cursor.execute("insert into message(email,admin,send_time,content) values (%s,%s,%s,%s)",(email,admin,send_time,content))
        self.db.commit()

    def get_message(self,admin:str) -> tuple:
        self.cursor.execute("select * from message where admin=%s order by send_time desc",(admin))
        return self.cursor.fetchall()
    
    def get_message_unread(self,admin:str) -> tuple:
        self.cursor.execute("select * from message where admin=%s and is_read=0 order by send_time desc",(admin))
        return self.cursor.fetchall()
    
    def get_user_state(self,email:str) -> str|None:
        self.cursor.execute("select user_state from user where email=%s",(email))
        result=self.cursor.fetchone()
        if(result is not None):
            return result[0]
        else:
            return None
    
    def read_message(self,id:int|str) -> None:
        if(isinstance(id,int)):
            id=str(id)
        self.cursor.execute("update message set is_read=1 where id=%s",(id))
        self.db.commit()
    
    def get_history(self,email:str) -> tuple:
        self.cursor.execute("select * from history where email=%s order by conversation_time desc",(email))
        return self.cursor.fetchall()
    
    def insert_history(self,email:str,conversation_time:str,question:str,answer:str) -> None:
        self.cursor.execute("insert into history(email,conversation_time,question,answer) values (%s,%s,%s,%s)",
                            (email,conversation_time,question,answer))
        self.db.commit()

def get_database(database:list|Database) -> Database:
    if(isinstance(database,Database)):
        return database
    elif(isinstance(database,list)):
        index=random.randint(0,len(database)-1)
        return database[index]
    else:
        raise TypeError
    

if __name__ =='__main__':
    from functionsAndClasses import WebConfig
    import os
    web_config=WebConfig(os.getcwd()+'\\backend\\config\\web_config.cfg')
    db=Database(web_config.sql_host,web_config.sql_port,web_config.sql_user,web_config.sql_password,web_config.sql_db)
    print(db.check_user_state('2235060401@qq.com'))
    # for message in db.get_message_unread('zbx05@outlook.com'):
    #     print(message[0])
    # print(db.get_message('zbx04@outlook.com')==())
    # db.create_message('zbx04@outlook.com','zbx05@outlook','2024-1-18 15:01','用户忘记密码，请求重置密码。')
