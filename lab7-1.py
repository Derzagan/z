def CheckPassword():
    lowPassword = ["123456", "password", "123456789", "qwerty", "12345", "12345678",
                   "111111",  "123123", "admin", "iloveyou", "sunshine", "qwer123",
                   "football", "p@ssword", "1234567"]
    special_characters = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/"
    
    while True:  
        password = input("Введите пароль: ")
        level = 0
        
        if len(password) < 10:
            print("Короткий пароль. Пожалуйста, выберите другой.")
        else:
            level += 1
        
        if not any(c.isupper() for c in password):
            print("Пароль должен содержать хотя бы одну заглавную букву.")
        else:
            level += 1
        
        if not any(c.islower() for c in password):
            print("Пароль должен содержать хотя бы одну строчную букву.")
        else:
            level += 1
        
        if not any(c.isdigit() for c in password):
            print("Пароль должен содержать хотя бы одну цифру.")
        else:
            level += 1
        
        if not any(c in special_characters for c in password):
            print("Пароль должен содержать хотя бы один специальный символ.")
        else:
            level += 1
        
        if password in lowPassword:
            print("Этот пароль слишком распространенный.")
        else:
            level += 1
        
        if level == 5:
            print("Очень сильный.")
        elif level == 4:
            print("Сильный.")
        elif level == 3:
            print("Средний.")   
        elif level == 2:
            print("Слабый.")
        else:
            print("Очень слабый.")

CheckPassword()