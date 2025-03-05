import requests
import os
from dotenv import load_dotenv

load_dotenv()
LINE_TOKEN = os.getenv("LINE_TOKEN")

class linebot():
    def __init__(self, group_id):
        self.group_id = group_id
        self.token = LINE_TOKEN
        self.messages = []

    def add_message(self, type, text):
        message = {
            'type' : type,
            'text' : text
        }
        try:
            self.messages.append(message)
        except Exception as e:
            print("新增訊息失敗",e)

        return 

    
    def send_line_message(self ):
        url = 'https://api.line.me/v2/bot/message/push'
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LINE_TOKEN}'
        }
        
        data = {
            'to': self.group_id,  # 使用您獲取到的群組ID
            'messages': self.messages
        }
        
        print("發送的資料:", data)
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return True
        else:
            print(f"群組訊息發送失敗，錯誤碼：{response.status_code}")
            print(f"錯誤訊息：{response.text}")
            return False