import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import List, Optional
from schemas.emails import EmailSchema
from datetime import datetime
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

load_dotenv() 

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
GMAIL_SMTP_SERVER = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587

template_env = Environment(loader=FileSystemLoader("templates"))


class EmailSender:
    def __init__(self):
        self.sender_email = GMAIL_ADDRESS
        self.password = GMAIL_PASSWORD
        self.smtp_server = GMAIL_SMTP_SERVER
        self.smtp_port = GMAIL_SMTP_PORT
        
        # 打印初始化信息，方便调试
        print(f"初始化邮件服务: {self.smtp_server}:{self.smtp_port}")
        print(f"发件人: {self.sender_email}")
        # 不要打印密码
        print(f"密码长度: {len(self.password) if self.password else 0} 字符")

    async def send_email(
        self,
        recipient_emails: List[str],
        subject: str,
        body: str,
        is_html: bool = False,
        attachments: Optional[List[Path]] = None
    ):
        """
        发送简单邮件
        
        Args:
            recipient_emails: 收件人列表
            subject: 邮件主题
            body: 邮件正文
            is_html: 是否为HTML格式
            attachments: 附件列表
        """
        # 打印邮件信息
        print("\n" + "="*50)
        print(f"准备发送邮件 - {datetime.now()}")
        print(f"收件人: {', '.join(recipient_emails)}")
        print(f"主题: {subject}")
        print(f"内容格式: {'HTML' if is_html else '纯文本'}")
        print(f"附件数量: {len(attachments) if attachments else 0}")
        print("="*50)
        
        try:
            # 准备邮件
            message = MIMEMultipart()
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = ", ".join(recipient_emails)
            
            # 添加邮件正文
            content_type = "html" if is_html else "plain"
            message.attach(MIMEText(body, content_type))
            
            # 添加附件
            if attachments:
                print("添加附件:")
                for attachment in attachments:
                    print(f" - {attachment}")
                    with open(attachment, "rb") as file:
                        part = MIMEApplication(file.read(), Name=attachment.name)
                    part["Content-Disposition"] = f'attachment; filename="{attachment.name}"'
                    message.attach(part)
            
            # 连接SMTP服务器
            print("\n正在连接SMTP服务器...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.set_debuglevel(1)  # 启用调试输出
                print("连接成功，启用TLS...")
                
                # 启用TLS加密
                server.starttls()
                print("TLS启用成功，登录中...")
                
                # 登录
                server.login(self.sender_email, self.password)
                print("登录成功，发送邮件...")
                
                # 发送邮件
                response = server.send_message(message)
                
                if not response:
                    print("\n✅ 邮件发送成功!")
                    print("所有收件人都已接受邮件")
                    return {"success": True, "message": "邮件发送成功"}
                else:
                    print("\n⚠️ 部分收件人被拒绝:")
                    for recipient, error in response.items():
                        print(f" - {recipient}: {error}")
                    return {"success": False, "message": "部分收件人被拒绝", "details": response}
        
        except Exception as e:
            print(f"\n❌ 邮件发送失败:")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}")
            
            # 提供更多的错误诊断提示
            if "5.7.8" in str(e) and "SMTP" in str(e):
                print("\n可能的原因:")
                print(" - 应用专用密码不正确")
                print(" - 账户安全设置问题")
                print(" - 两步验证未正确设置")
                print("\n建议:") 
                print(" - 检查环境变量中的GMAIL_APP_PASSWORD是否正确")
                print(" - 确保应用专用密码没有空格")
                print(" - 在Google账户中重新生成应用专用密码")
            
            if "No connection could be made because the target machine actively refused it" in str(e):
                print("\n可能的原因:")
                print(" - SMTP服务器地址或端口错误")
                print(" - 防火墙阻止连接")
                print("\n建议:")
                print(" - 确认GMAIL_SMTP_SERVER和GMAIL_SMTP_PORT设置正确")
            
            return {"success": False, "message": f"邮件发送错误: {str(e)}"}

# 创建邮件发送器实例
email_sender = EmailSender()

async def send_email_task(email_data: EmailSchema):
    """异步发送邮件的后台任务"""
    attachments = None
    if email_data.attachment_paths:
        attachments = [Path(path) for path in email_data.attachment_paths if os.path.exists(path)]
    
    # 根据模板或内容生成 body
    body = ""
    is_html = False
    
    if email_data.template_name and email_data.template_data:
        # 使用模板生成 HTML 内容
        template = template_env.get_template(email_data.template_name)
        body = template.render(**email_data.template_data)
        is_html = True
    elif email_data.html_content:
        body = email_data.html_content
        is_html = True
    elif email_data.text_content:
        body = email_data.text_content
        is_html = False
    
    # 调用正确的参数
    success = await email_sender.send_email(
        recipient_emails=email_data.recipients,
        subject=email_data.subject,
        body=body,
        is_html=is_html,
        attachments=attachments
    )
    
    return success