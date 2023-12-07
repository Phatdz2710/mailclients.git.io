from config import*
# PORT của server SMTP
PORTSMTP = smtp_port
# PORT của server POP3
PORTPOP3 = pop3_port
# HOST
HOST = mail_server
BUFFERSIZE = 4 * 1024 * 1024

TO = 0
CC = 1
BCC = 2

mail_folder = 'E:\cnppro2710.git.io-main\cnppro2710.git.io-main\MAIL'

def check_mail_spam(mail):
    spams_token = keywords_spam
    for token in spams_token:
        if token in mail:
            return True
    return False

def check_mail_subject(mail):
    subject = keywords_subject
    for token in subject:
        if token in mail:
            return True
    return False

def check_mail_project(mail):
    project_token = addresses
    for token in project_token:
        if token in mail:
            return True
    return False

def check_mail_work(mail):
    work_token = keywords_content
    for token in work_token:
        if token in mail:
            return True
    return False

def check_mail_important(mail):
    tokens = keywords_important
    for token in tokens:
        if token in mail:
            return True
    return False



# Kiểm tra email đúng định dạng
def is_valid_email(email):
    parts = email.split('@')
    if len(parts) != 2:
        return False

    username = parts[0]
    domain = parts[1]

    if not username.isalnum():
        return False

    parts2 = domain.split('.')
    for t in parts2:
        if not t.isalnum():
            return False

    return True


# Nhập email
def InputMail():
    mails = ""
    while not is_valid_email(mails):
        mails = input()
        if not is_valid_email(mails):
            print("The email address you entered is not valid !!! Please Enter Again: ", end="")
    return mails

def AddFileToFolder(folder_path, namefile, contents):
    import os
    file_path = os.path.join(folder_path, namefile)
    if os.path.exists(file_path):
        return
    with open(file_path, 'wb') as file:
        file.write(contents.encode('utf-8'))

