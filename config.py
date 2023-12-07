import json

username = ''
password = ''
mail_server = ''
smtp_port = ''
pop3_port = ''
autoload_value = ''

addresses = ''
keywords_subject = ''
keywords_content = ''
keywords_spam = ''
keywords_important =''


def filter_json(json_data):
    # Khai báo biến toàn cục
    global username, password, smtp_port, pop3_port, mail_server, autoload_value, addresses, keywords_subject, keywords_content, keywords_spam, keywords_important

    # Lọc thông tin từ General
    general_info = json_data.get("General", {})
    username = general_info.get("Username", "")
    password = general_info.get("Password", '')
    smtp_port = int(general_info.get("SMTP", ''))
    pop3_port = int(general_info.get("POP3", ''))
    mail_server = general_info.get("MailServer", "")
    autoload_value = int(general_info.get("Autoload", ''))

    # Lọc thông tin từ Filters
    filters_info = json_data.get("Filters", {})
    addresses = filters_info.get("Addresses", [])
    keywords_subject = filters_info.get("Keywords_subject", [])
    keywords_content = filters_info.get("Keywords_content", [])
    keywords_spam = filters_info.get("Keywords_spam", [])
    keywords_important = filters_info.get("Keywords_important",[])


with open('config.json', 'r') as file:
    json_data = json.load(file)

filter_json(json_data)

