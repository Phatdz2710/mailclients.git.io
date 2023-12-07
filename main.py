from manager import *
from sendmail import SendYourMail
from receive import *
from threading import Thread
from config import*


def menu(userMail, userPassword):
    # Khởi tạo luồng nhận tin nhắn liên tục
    recvMail = ReceiveMail(userMail, userPassword)
    # Cho luồng chạy ngầm
    recvMail.daemon = True
    # Chạy luồng
    recvMail.start()

    while True:
        print("1. Send mail")
        print("2. Receive mail")
        print("3. Exit")
        choice = input("Your choice: ")
        if str(choice) == '1':
            SendYourMail(userMail)
        elif str(choice) == '2':
            recvMail.OpenMails()
        elif str(choice) == '3':
            recvMail.SaveMailToFolder()
            break


def __main__():
    # Đăng nhập
    print("User Mail: ", end="")
    userMail = username #InputMail()
    print(username)
    userPassword = password #input("User Password: ")
    print("User Password: ",userPassword)
    # Chạy luồng chính là Menu
    menuThread = Thread(target=menu, args=(userMail, userPassword))
    menuThread.start()


if __name__ == "__main__":
    __main__()