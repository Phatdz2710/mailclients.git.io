from socket import*
from manager import* 
import base64
import re
import os
import time
import threading

os.chdir("C:")

class SendMail():
    def __init__(self, userMail):
        super(SendMail, self).__init__()
        self.mail_server = (HOST, PORTSMTP) #server 
        self.user_send = userMail #người gửi 
        self.mail_subject = None #Tiêu đề
        self.mail_contents = None #Nội dung 
        self.mail_to = [] #Danh sách người nhận tin nhắn
        self.clientsocket = None #Socket 
        self.path = []
    
    #Kết nối đến server 
    def connectServer(self):
        self.clientsocket = socket(AF_INET, SOCK_STREAM)
        self.clientsocket.connect(self.mail_server)
        self.clientsocket.recv(BUFFERSIZE).decode()

    #Đóng socket 
    def closesocket(self):
        self.clientsocket.close()
    
    #Gửi lệnh đến server 
    def sendCommand(self,command, recvSv):
        self.clientsocket.send((command + "\r\n").encode())
        if recvSv == True:
            self.clientsocket.recv(BUFFERSIZE).decode()

    #Nhận dữ liệu đầu vào 
    def input_data(self, detailMail):
        self.mail_to = detailMail[0]
        self.mail_subject = detailMail[1]
        self.mail_contents = detailMail[2]
        self.path = detailMail[3]
    
    #Bắt đầu trao đổi với server 
    def SendMail(self, classify):
        self.connectServer()
        self.sendCommand(("EHLO [{}]".format(self.mail_server[0])), True)
        self.sendCommand(("MAIL FROM:<{}>").format(self.user_send), True)

        for i in self.mail_to:
            self.sendCommand(("RCPT TO:<{}>".format(i)), True)

        self.sendCommand(("DATA"), True)
        self.sendCommand(("To: {}").format(self.mail_to[0]), False)

        #Gửi CC 
        if classify == 1:
            result = ", ".join(self.mail_to[1:])
            self.sendCommand("CC: {}".format(result), False)
        
        self.sendCommand(("From: <{}>").format(self.user_send), False)
        self.sendCommand(("Subject: {}").format(self.mail_subject), False)
        self.sendCommand("\r\n" + self.mail_contents, False)
        self.sendfile()
        self.sendCommand("\r\n.", True)
        self.closesocket()
    
    def sendfile(self):
        for x in self.path:
            if os.path.exists(x):
                file_size = os.path.getsize(x)
                if(file_size <= 3 * 1024 * 1024):
                    self.clientsocket.send("\n".encode())
                    print(str(x) + " file exist")
                    x_bytes = x.encode('utf-8')
                    NameEncode = "------" + str(base64.b64encode(x_bytes), 'utf-8') 
                    self.clientsocket.send(NameEncode.encode())
                    self.clientsocket.send("\n".encode())
                    self.clientsocket.send(("name:" + str(x)+"\n").encode("utf-8"))
                    with open(x,'rb') as file:
                        data = base64.b64encode(file.read())
                        chunk_size = 72 
                        chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
                        for chunk in chunks:
                            self.clientsocket.sendall(chunk)
                            self.clientsocket.send("\n".encode())
                        self.clientsocket.send(NameEncode.encode())
                        self.clientsocket.send("\n".encode())
                        self.have_file = True 
                else:
                    print(str(x) + " file size over 3mb")
            else:
                print(str(x) + " file not exist")
                

#Nhập mail bên nhận 
def InputMailTo(classify):
    mail_to = []
    print("To: ", end="")
    mail_to.append(InputMail()) #Thêm người nhận chính TO 

    #Nhập thêm người nhận cho CC và BCC 
    if classify != 0:
        inputcc = None #Biến tạm để thêm 
        i = 0
        while True:
            i = i + 1
            inputcc = input(str(i) + ": ")
            if inputcc == '0':
                break
            if is_valid_email(inputcc) == False:
                print("The email address you entered is not valid !!!", end="")
                i = i-1
                continue
            mail_to.append(inputcc)
    return mail_to

#Nhập chi tiết tin nhắn 
def InputDetailMail(classify):
    mail_to = InputMailTo(classify)
    subject = input("Subject: ")
    contents = input("Contents: ")
    filePath = []
    print("Do you want to send file? (1.Yes, 2.No): ", end="")
    choice = input()
    if str(choice) == '1':
        print("Enter '0' to exit")
        nameFile = ''
        i = 0
        while True:
            i = i + 1
            print(str(i) + ': ', end="")
            nameFile = input()
            if nameFile == '0':
                break
            else:
                filePath.append(nameFile)

    detail = [mail_to, subject, contents, filePath]
    return detail


#Menu gửi tin nhắn 
def SendYourMail(userMail):
    send_mail = SendMail(userMail)
    choice = ''
    while True:
        print("0. Exit")
        print("1. TO")
        print("2. CC")
        print("3. BCC")
        choice = input("-> Your choice: ")
        #0: TO - 1: CC - 2: BCC
        if choice == '1':
            detailMail = InputDetailMail(TO)
            send_mail.input_data(detailMail)
            send_mail.SendMail(TO)
            break
        elif choice == '2':
            detailMail = InputDetailMail(CC)
            send_mail.input_data(detailMail)
            send_mail.SendMail(CC)
            break
        elif choice == '3':
            detailMail = InputDetailMail(BCC)
            send_mail.input_data(detailMail)
            send_mail.SendMail(BCC)
            break
        else:
            break












