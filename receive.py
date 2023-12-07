from socket import *
from manager import *
from config import *
import manager
import time
import threading
import base64
import os


class ReceiveMail(threading.Thread):
    def __init__(self, userMail, userPassword):
        super(ReceiveMail, self).__init__()
        self.mail_server = (HOST, PORTPOP3)  # Server Pop3
        self.user_mail = userMail  # Mail người dùng
        self.user_password = userPassword  # Mật khẩu người dùng
        self.clientsocket = None  # Socket
        self.recvMail = None  # Tên các file .msc
        self.listInbox = []  # Danh sách mail Inbox
        self.listSpam = []  # Danh sách mail Spam
        self.listProject = []  # Danh sách mail Project
        self.listWork = []  # danh sách mail Work
        self.listImportant = [] # danh sách mail important
        self.count_mails = 0  # Số lượng mail
        self.first_time_run = True
        self.CreateMyFolder()
        self.LoadMailFromFolder()
        
    def LoadMailFromFolder(self):
        try:
            now_directory = os.path.join(manager.mail_folder, self.user_mail)
            list_folder = ['Inbox', 'Spam', 'Work', 'Project', 'Important']
            #Kiểm tra xem thư mục có tồn tại hay không
            if os.path.exists(now_directory):
                print(now_directory)
                #lặp lại các folder trong folder của mail đó 
                for name_folder in list_folder:
                    now_dir = os.path.join(now_directory, name_folder) # Folder đang xét
                    for filetxt in os.listdir(now_dir): # Đọc tất cả file txt trong folder đang xét 
                        if filetxt != 'status.txt': # Loại trừ file status 
                            txtpath = os.path.join(now_dir, filetxt) # tạo đường dẫn đến file txt
                            with open(txtpath, 'rb', encoding='utf-8') as file: # Mở file txt 
                                contents = file.read().decode('utf-8')
                                if name_folder == 'Inbox':
                                    self.listInbox.append({'mail':contents, 'status':0}) 
                                elif name_folder == 'Spam':
                                    self.listSpam.append({'mail':contents, 'status':0})
                                elif name_folder == 'Project':
                                    self.listProject.append({'mail':contents, 'status':0})
                                elif name_folder == 'Work':
                                    self.listWork.append({'mail':contents, 'status':0})
                                elif name_folder == 'Important':
                                    self.listImportant.append({'mail':contents, 'status':0})
                                self.count_mails = self.count_mails + 1
        except Exception as e:
            print(f"ERROR")

    def CreateMyFolder(self):
        now_directory = os.path.join(manager.mail_folder, self.user_mail) # Khởi tạo đường dẫn hiện tại 
        list_folder = ['Inbox','Spam','Work','Project','Important'] # Danh sách các loại mail 
        if not os.path.exists(now_directory): # Kiểm tra xem folder đã tồn tại hay chưa 
            os.mkdir(now_directory) #Tạo folder mới nếu chưa có folder 
            for name_folder in list_folder:
                subfolder_path = os.path.join(now_directory, name_folder) # Tạo đường dẫn đến folder trong list_folder 
                os.mkdir(subfolder_path) # Tạo các folder đó 
                #Thêm các file trạng thái cho từng loại mail 
            # manager.AddFileToFolder(now_directory, 'status_Inbox.txt', '') 
            # manager.AddFileToFolder(now_directory, 'status_Spam.txt', '')
            # manager.AddFileToFolder(now_directory, 'status_Project.txt', '')
            # manager.AddFileToFolder(now_directory, 'status_Important.txt', '')
            # manager.AddFileToFolder(now_directory, 'status_Work.txt', '')

    
    def SaveMailToFolder(self):
        try:
            now_directory = os.path.join(manager.mail_folder, self.user_mail) # Khởi tạo đường dẫn hiện tại 
            list_folder = ['Inbox','Spam','Work','Project','Important'] # Danh sách các loại mail 
        
            # Tạo danh sách các list_mail trong chương trình 
            _list = [self.listInbox, self.listSpam, self.listWork, self.listProject, self.listImportant]
            for i in range(0, len(list_folder)): # Duyệt từng folder trong list_folder
                subfolder_path = os.path.join(now_directory, list_folder[i]) # tạo đường dẫn đến các folder đó 
                for j in range(0, len(_list[i])): # Bắt đầu ghi các nội dung mail vào trong folder
                    print(_list[i][j]['mail'])
                    manager.AddFileToFolder(subfolder_path, 'mail {}.txt'.format(str(j)), _list[i][j]['mail'])
        except Exception as e:
            print(f"ERROR")

    # Kết nối đến server
    def connectServer(self):
        self.clientsocket = socket(AF_INET, SOCK_STREAM)
        self.clientsocket.connect(self.mail_server)
        self.clientsocket.recv(BUFFERSIZE)

    # Đóng socket
    def closesocket(self):
        self.clientsocket.close()

    # Gửi lệnh đến server
    def sendCommand(self, command):
        self.clientsocket.send((command + '\r\n').encode())
        return self.clientsocket.recv(BUFFERSIZE).decode()


    def get_mails(self):
        self.recvMail = self.sendCommand("UIDL")
        parts = self.recvMail.split(' ')
        count = len(parts) - 1  # Lấy số lượng mail
        if count > self.count_mails:
            is_change = self.classifyMails(count)  # Cập nhật lại danh sách mail trong inbox và spam
            if is_change == True:
                self.count_mails = count  # Cập nhật lại số lượng mail

    # Chạy gửi thông tin cho server
    def SendCommandToServer(self):
        self.sendCommand("CAPA")
        self.sendCommand("USER {}".format(self.user_mail))
        self.sendCommand("PASS {}".format(self.user_password))
        self.sendCommand("STAT")
        self.sendCommand("LIST")
        self.get_mails()
        self.sendCommand("QUIT")


    # Xuất các mail trong list 
    def ShowList(self, list):
        i = 0
        for mail_info in list:  # Fix: change self.list to list
            i = i + 1
            if 'mail' not in mail_info or 'status' not in mail_info:
                continue
            mail = mail_info['mail']
            sender = next((line for line in mail.split('\r\n') if line.startswith("From: ")), None)
            subject_line = next((line for line in mail.split('\r\n') if line.startswith("Subject: ")), None)

            # Add status (Đã xem/Chưa xem) before the "From" field
            status = "Đã xem" if mail_info['status'] == 1 else "Chưa xem"
            print(f"{i}. ({status}) {sender} {subject_line}")


    def load_mail_status(self, mail_list,name):
        # Load mail status from a text file
        status_file = os.path.join(manager.mail_folder, self.user_mail, 'status_{}.txt'.format(name))
        if os.path.exists(status_file):
            with open(status_file, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    mail_number, status = map(int, line.strip().split(','))
                    if mail_number <= len(mail_list):
                        if isinstance(mail_list[mail_number - 1], dict):
                            mail_list[mail_number - 1]['status'] = status

    def save_mail_status(self,list,name):
        now_dir = os.path.join(manager.mail_folder, self.user_mail, 'status_{}.txt'.format(name))
        with open(now_dir, 'w') as file:
            for i, mail_info in enumerate(list):
                if 'status' in mail_info:
                    status = mail_info['status']
                    file.write(f"{i + 1},{status}\n")

    def classifyMails(self, countmails):
        is_change = False
        try:
            for count in range(self.count_mails + 1, countmails + 1):
                mail = ''
                while len(mail) == 0 or mail[-2:] != '\r\n':
                    mail += self.sendCommand("RETR {}".format(str(count)))
                is_change = True
                if check_mail_spam(mail):
                    self.listSpam.append({'mail': mail, 'status': 0})
                elif check_mail_project(mail):
                    self.listProject.append({'mail': mail, 'status': 0})
                elif check_mail_work(mail):
                    self.listWork.append({'mail': mail, 'status': 0})
                elif check_mail_important(mail):
                    self.listImportant.append({'mail': mail, 'status':0})
                else:
                    # Mark the email as unread (status = 0) when initially received
                    self.listInbox.append({'mail': mail, 'status': 0})
        except Exception as e:
            print(f"Error in classifyMails: {e}")
        return is_change
    

    def printInformation(self, index, list):
        information = list[index]
        data_Inf = information['mail'].split('\r\n', 1)[1] if '\r\n' in information['mail'] else information['mail']
        dataBody = data_Inf.split('\r\n')[0:6]

        if '------' not in data_Inf:
            dataBody = data_Inf.split('\r\n')[0:5]
            dataBody_concat = '\r\n'.join(dataBody[0:5])
            print(dataBody_concat)
        else:
            dataBody = data_Inf.split('\r\n')[0:6]
            dataBody_concat = '\r\n'.join(dataBody[0:6])
            print(dataBody_concat)
            dataFile = data_Inf.split('\r\n')[6:]
            del dataFile[-2:]
            data_File = [item for item in dataFile if item != '']
            x = 1
            i = 1
            check = data_File[0]
            name = True
            SaveName = ""
            strtmp = ""
            dataObj = []
            while i < len(data_File):
                if data_File[i] != check:
                    if name:
                        print(str(x) + ". " + data_File[i][5:])
                        name = False
                        SaveName = data_File[i][5:]
                    else:
                        strtmp = strtmp + data_File[i]
                else:
                    obj = {"key": x, "value": strtmp, "name": SaveName}
                    dataObj.append(obj)
                    strtmp = ""
                    SaveName = ""
                    x += 1
                    name = True
                    if i + 1 < len(data_File):
                        check = data_File[i + 1]
                        i += 1
                    else:
                        break
                i += 1
            ques = int(input("Wanna Save Mail(1.YES , 2. NO): "))
            while ques == 1:
                numFile = int(input("Number File wanna save: "))
                if numFile > len(dataObj):
                    print("Not exist please input again")
                    continue
                path = input("Input path wanna save: ")
                os.chdir(path)
                with open(dataObj[numFile - 1]["name"], 'wb') as file:
                    decodeFile = base64.b64decode(dataObj[numFile - 1]["value"])
                    file.write(decodeFile)
                    print("Download file succesfull")
                ques = int(input("Wanna Save Mail(1.YES , 2. NO): "))
            dataObj.clear()

    def open_mail(self, classify):
        if self.count_mails == 0:
            return
        mail_number = input("Mail Number: ")
        if mail_number.isdigit() == False:
            return
        if classify == 1:
            if int(mail_number) > len(self.listInbox):
                return
            mail_info = self.listInbox[int(mail_number) - 1]
            # Mark the email as read (status = 1) when opened
            mail_info['status'] = 1
            self.printInformation(int(mail_number) - 1, self.listInbox)
        elif classify == 2:
            if int(mail_number) > len(self.listSpam):
                return
            mail_info = self.listSpam[int(mail_number) - 1]
            # Mark the email as read (status = 1) when opened
            mail_info['status'] = 1
            self.printInformation(int(mail_number) - 1, self.listSpam)

        elif classify == 3:
            if int(mail_number) > len(self.listProject):
                return
            mail_info = self.listProject[int(mail_number) - 1]
            # Mark the email as read (status = 1) when opened
            mail_info['status'] = 1
            self.printInformation(int(mail_number) - 1, self.listProject)
        elif classify == 4:
            if int(mail_number) > len(self.listWork):
                return
            mail_info = self.listWork[int(mail_number) - 1]
            # Mark the email as read (status = 1) when opened
            mail_info['status'] = 1
            self.printInformation(int(mail_number) - 1, self.listWork)
        elif classify == 5:
            if int(mail_number) > len(self.listImportant):
                return
            mail_info = self.listImportant[int(mail_number) - 1]
            # Mark the email as read (status = 1) when opened
            mail_info['status'] = 1
            self.printInformation(int(mail_number) - 1, self.listImportant)
        else:
            return
    
    def OpenMails(self):
        if self.first_time_run == True:
            print("Loading mails...")  # Chờ để lấy thông tin
            time.sleep(3)
            self.first_time_run = False

        while True:
            print("0.Exit")
            print("1. Inbox")
            print("2. Spam")
            print("3. Project")
            print("4. Work")
            print("5. Important")
            choice = input("Your choice: ")
            if str(choice) == '0':
                break
            elif str(choice) == '1':
                if len(self.listInbox) == 0:
                    continue
                self.load_mail_status(self.listInbox,'Inbox')  # Load mail status before displaying inbox
                self.ShowList(self.listInbox)
                self.open_mail(1)
                self.save_mail_status(self.listInbox,'Inbox')  # Save mail status after opening emails
            elif str(choice) == '2':
                if len(self.listSpam) == 0:
                    continue
                self.load_mail_status(self.listSpam,'Spam')
                self.ShowList(self.listSpam)
                self.open_mail(2)
                self.save_mail_status(self.listSpam,'Spam')
            elif str(choice) == '3':
                if len(self.listProject) == 0:
                    continue
                self.load_mail_status(self.listProject,'Project')
                self.ShowList(self.listProject)
                self.open_mail(3)
                self.save_mail_status(self.listProject,'Project')
            elif str(choice) == '4':
                if len(self.listWork) == 0:
                    continue
                self.load_mail_status(self.listWork,'Work')
                self.ShowList(self.listWork)
                self.open_mail(4)
                self.save_mail_status(self.listWork,'Work')
            elif str(choice) == '5':
                if len(self.listImportant) == 0:
                    continue
                self.load_mail_status(self.listImportant,'Important')
                self.ShowList(self.listImportant)
                self.open_mail(5)
                self.save_mail_status(self.listImportant,'Important')
            else:
                break

    def run(self):
        while True:
            self.connectServer()
            self.SendCommandToServer()
            self.closesocket()
            time_load = autoload_value
            time.sleep(autoload_value)