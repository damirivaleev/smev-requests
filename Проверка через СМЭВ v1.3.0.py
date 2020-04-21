import requests
import io
import os
import time

while True:
    try:
        inn = input('\nИНН=')
        url_smev = 'http://smev.razdolie.ru/api/smev/3/requests'
        url = 'https://egrul.nalog.ru/'
        url1 = 'https://egrul.nalog.ru/search-result/'
        #print('1')
        if (len(inn) != 10) and (len(inn) != 12):
            print('ОШИБКА: неверная длина ИНН\n')
            continue
        #print('2')
        if len(inn) == 10:  #---------инн 10 символов - это юр лицо---------
            #--------------запрос выписки на сайте ФНС------------------

            my_query = {'query': inn,}

            hash_data = requests.post(url, data=my_query)
            #print(hash_data.json())
            #print('3')
            short_data = requests.get(url1 + hash_data.json()['t'])
            #print(short_data.json())
            #print('4')
            if 'status' in short_data.json():
                print(short_data.json())
                while short_data.json()['status'] == 'wait':
                    short_data = requests.get(url1 + hash_data.json()['t'])
                    if 'status' in short_data.json():
                        pass
                    else:
                        break

            try:
                kratkoe = short_data.json()['rows'][0]['c'].strip()
            except:
                kratkoe = short_data.json()['rows'][0]['n'].strip()
            dolzhnost = short_data.json()['rows'][0]['g'].split(':')[0].strip()
            fio_dir = short_data.json()['rows'][0]['g'].split(',')[0].split(':')[1].strip()
            #print(short_data.json()['rows'][0]['g'].split(',')[0].split(':'))
            #print(fio_dir)
            
            last_director = fio_dir.split(' ')[0]
            first_director = fio_dir.split(' ')[1]
            middle_director = fio_dir.split(' ')[2]
            url2 = 'https://egrul.nalog.ru/vyp-request/'

            for s in ['request', 'status', 'download']:
                try:
                    download_data = requests.get('https://egrul.nalog.ru/vyp-{}/'.format(s) + short_data.json()['rows'][0]['t'])
                    #print(download_data.json())
                    if s == 'download':
                        if download_data.ok:
                            print('Выписка из ЕГРЮЛ на сайте ФНС получена успешно')
                        else:
                            print('ОШИБКА при получении выписки из ЕГРЮЛ на сайте ФНС')
                            print(download_data.raise_for_status())
                except IndexError:
                    print('Неверный ИНН')

            with open('{}.pdf'.format(inn), 'wb') as f:
                f.write(download_data.content)

            #-----------------из пдф выписки в текст------------------------

            from pdfminer.converter import TextConverter
            from pdfminer.pdfinterp import PDFPageInterpreter
            from pdfminer.pdfinterp import PDFResourceManager
            from pdfminer.pdfpage import PDFPage

            def extract_text_from_pdf(pdf_path):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(resource_manager, fake_file_handle)
                page_interpreter = PDFPageInterpreter(resource_manager, converter)

                with open(pdf_path, 'rb') as fh:
                    for page in PDFPage.get_pages(fh,
                                            caching=True,
                                            check_extractable=True):
                        page_interpreter.process_page(page)

                    text = fake_file_handle.getvalue()

                # close open handles
                converter.close()
                fake_file_handle.close()

                if text:
                    return text

            vipiska = extract_text_from_pdf('{}.pdf'.format(inn))
            os.remove('{}.pdf'.format(inn))

            #--------------------фио и инн(физ.лица) руководителя------------------------
            '''
            last_director = vipiska[vipiska.find('доверенности'):]
            last_director = last_director[last_director.find('Фамилия')+7:last_director.find('Имя')]
            last_director = ''.join(c for c in last_director if c.isalpha())
            #print(last_director)

            first_director = vipiska[vipiska.find('доверенности'):]
            first_director = first_director[first_director.find('Имя')+3:first_director.find('Отчество')]
            first_director = ''.join(c for c in first_director if c.isalpha())
            #print(first_director)

            middle_director = vipiska[vipiska.find('доверенности'):]
            middle_director = middle_director[middle_director.find('Отчество')+8:middle_director.find('ИНН')]
            middle_director = middle_director[:middle_director.find('Страница')]
            middle_director = ''.join(c for c in middle_director if c.isalpha() or c.isspace())
            #print(middle_director)
            
            dolzhnost = vipiska[vipiska.find('доверенности'):]
            print('1', dolzhnost)
            dolzhnost = dolzhnost[dolzhnost.find('Должность')+9:]
            print('2', dolzhnost)
            dolzhnost = dolzhnost[:dolzhnost.find('ГРН')]
            print('3', dolzhnost)
            dolzhnost = dolzhnost[:dolzhnost.find('Страница')]
            print('4', dolzhnost)
            dolzhnost = ''.join(c for c in dolzhnost if c.isalpha() or c.isspace())       
            '''
            #------------------------выписка в смэв------------------------------
            
            egrul_query = {"requestName": "VS00051v003-FNS001",
                           "requestData": {"value": inn},
                           "Env": 2}
            egrul = requests.post(url_smev, json=egrul_query)
            if egrul.ok:
                print('Запрос Выписки из ЕГРЮЛ отправлен успешно\n')
                print(kratkoe)
            else:
                print('ОШИБКА при отправке запроса Выписки из ЕГРЮЛ')
                print(egrul.raise_for_status())
            
            
            if vipiska.find('Сведения об управляющей организации') == -1:
                inn_director = vipiska[vipiska.find('доверенности'):]
                inn_director = inn_director[inn_director.find('ИНН')+3:][:12]   #проблема с именем ИННА
                try:
                    int(inn_director)
                except ValueError:
                    #print('ОШИБКА: ИНН руководителя не найден')
                    input('ОШИБКА: в выписке ЕГРЮЛ отсутствует ИНН руководителя')
                    continue
                #print(inn_director)            
            else:
                input('Есть управляющая организация')
                continue
                
            
        else:   #-------------ип или физ лицо------------------
            #--------------------запрос на сайте фнс--------------------

            my_query = {'query': inn,}
            hash_data = requests.post(url, data=my_query)

            egrip_data = requests.get(url1 + hash_data.json()['t'])
            #print(egrip_data.json()['rows'])
            
            #if egrip_data.json()['rows'][0]['tot'] != '0':
            if egrip_data.json()['rows'] and (egrip_data.json()['rows'][0]['tot'] != '0'):
                fio_ip = egrip_data.json()['rows'][0]['n']
                ogrnip = egrip_data.json()['rows'][0]['o']
                #input(fio_ip)

                last_director = fio_ip.split(' ')[0]
                first_director = fio_ip.split(' ')[1]
                try:
                    middle_director = fio_ip.split(' ')[2]
                except IndexError:
                    middle_director = ''
            else:
                print('ИП с таким ИНН не найден')
                last_director = ''

            #-------------------фио ип---------------------

            if last_director == '':           #если в выписке нет фио, значит это физ лицо
                last_director = input('Фамилия: ')
                first_director = input('Имя: ')
                middle_director = input('Отчество: ')
                dolzhnost = 'Физическое лицо'
            else:
                print('Найден ИП с таким ИНН')
                dolzhnost = 'Индивидуальный предприниматель'
                #--------------------запрос ип в смэв----------------------
                egrip_query = {"requestName": "VS00050v003-FNS001",
                               "requestData": {"value": inn},
                               "Env":2}
                egrip = requests.post(url_smev, json=egrip_query)
                if egrip.ok:
                    print('Запрос Выписки из ЕГРИП отправлен успешно')
                else:
                    while egrip.status_code == 500:
                        print('Нет соединения, повторный запрос...')
                        egrip = requests.post(url_smev, json=egrip_query)
                        if egrip.ok:
                            print('Запрос соответствия ИНН и паспортных данных отправлен успешно')
                            break
                    else:
                        print('ОШИБКА при отправке запроса Выписки из ЕГРИП')
                        print(egrip)
                        print(egrip.status_code)
                        print(egrip.reason)
                        print(egrip.text)
                        print(egrip.raise_for_status())
                    
            inn_director = inn    #---инн физ лиц и ип подставляем в инн для запросов---

        last_director = last_director.capitalize()
        first_director = first_director.capitalize()
        middle_director = middle_director.capitalize()

        #-----------------------печать фио и инн физ лица-------------------------------

        print('\nСведения о руководителе:')
        print(last_director)
        print(first_director)
        print(middle_director)
        print(inn_director)
        print(dolzhnost)

        #----------------------соответствие инн в смэв---------------------------

        if len(inn) == 10:
            is_director = input('\nЗаявление на руководителя? (да/нет): ')
            if (is_director == 'нет') or (is_director == 'n'):
                last_director = input('Фамилия: ')
                first_director = input('Имя: ')
                middle_director = input('Отчество: ')

        passport = input('\nСерия и номер паспорта: ')
        passport_1 = passport[:4]
        passport_2 = passport[4:]
        
        if (len(inn) == 12) or (is_director == 'да') or (is_director == 'y'):
            inn_query = {"requestName": "VS00125v001-FNS001",
                         "requestData": {"documentCode": 21,
                                        "familyName": last_director,
                                        "firstName": first_director,
                                        "patronymic": middle_director,
                                        "series": passport_1,
                                        "number": passport_2,
                                        "issuerDate": None,
                                        "issuer": None,
                                        "issuerCode": None,
                                        "inn": inn_director},
                         "Env":2}


            inn_check = requests.post(url_smev, json=inn_query)
            if inn_check.ok:
                print('Запрос соответствия ИНН и паспортных данных отправлен успешно')
            else:
                while inn_check.status_code == 500:
                    print('Нет соединения, повторный запрос...')
                    inn_check = requests.post(url_smev, json=inn_query)
                    if inn_check.ok:
                        print('Запрос соответствия ИНН и паспортных данных отправлен успешно')
                        break
                else:
                    print('ОШИБКА при отправке запроса соответствия ИНН и паспортных данных')
                    print(inn_check)
                    print(inn_check.status_code)
                    print(inn_check.reason)
                    print(inn_check.text)
                    print(inn_check.raise_for_status())

        #---------------------проверка снилс в смэв----------------------

        snils = input('\nСНИЛС: ')
        snils_0 = snils[:3]
        snils_1 = snils[3:6]
        snils_2 = snils[6:9]
        snils_3 = snils[9:]

        snils_query = {"requestName":"VS00113v001-PFR001",
                       "requestData": {"familyName": last_director,
                                       "firstName": first_director,
                                       "patronymic": middle_director,
                                       "snils": "{0}-{1}-{2} {3}".format(snils_0, snils_1, snils_2, snils_3),
                                       "birthDate": None,
                                       "gender": ["Male", 'Female'][(middle_director[-2:].lower() == 'на') or (middle_director[-4:].lower() == 'кызы')]},
                       "Env":2}

        snils_check = requests.post(url_smev, json=snils_query)
        if snils_check.ok:
            print('Запрос проверки СНИЛС отправлен успешно')
        else:
            while snils_check.status_code == 500:
                print('Нет соединения, повторный запрос...')
                snils_check = requests.post(url_smev, json=snils_query)
                if snils_check.ok:
                    print('Запрос проверки СНИЛС отправлен успешно')
                    break
            else:
                print(snils_check)
                print(snils_check.status_code)
                print(snils_check.reason)
                print(snils_check.text)
                print(snils_check.raise_for_status())
                print('ОШИБКА при отправке запроса проверки СНИЛС')            

        #--------------------проверка паспорта в смэв---------------------

        passport_date = input('\nДата выдачи паспорта: ')
        if '/' in passport_date:
            passport_date = '.'.join(passport_date.split('/'))
        elif '.' in passport_date:
            pass
        else:
            passport_date = '.'.join([passport_date[:2], passport_date[2:4], passport_date[4:]])
        
        passport_kod = input('Код подразделения: ')
        birthday = input('Дата рождения: ')
        if '/' in birthday:
            birthday = '.'.join(birthday.split('/'))
        elif '.' in birthday:
            pass
        else:
            birthday = '.'.join([birthday[:2], birthday[2:4], birthday[4:]])

        url_passport = "http://smev.razdolie.ru/api/Mvd/Skmvd/CheckValidPassport/send"

        passport_query = {"lastName": "Валеев",
                          "firstName": "Дамир",
                          "middleName": "Маратович",
                          "citizenLastname": last_director,
                          "citizenFirstname": first_director ,
                          "citizenGivenname": middle_director ,
                          "citizenBirthday": birthday,
                          "series": passport_1,
                          "number": passport_2,
                          "date": passport_date,
                          "issuer": passport_kod}

        #print('Отправляется запрос проверки паспорта\n', requests.post(url_passport, json=passport_query))

        try:
            passport_check = requests.post(url_passport, json=passport_query, timeout=15)

            if passport_check.ok:
                print('Запрос проверки паспорта отправлен успешно')
            else:
                print('ОШИБКА при отправке запроса проверки паспорта')
                print(passport_check)
                print(passport_check.status_code)
                print(passport_check.reason)
                print(passport_check.text)
                print(passport_check.raise_for_status())
        except requests.exceptions.Timeout:
            #print(type(e))
            #print(e)
            con = input('Нет соединения, повторить запрос? (да/нет): ')
            if con == 'да' or con == 'y':
                try:
                    time.sleep(25)
                    passport_check = requests.post(url_passport, json=passport_query, timeout=15)

                    if passport_check.ok:
                        print('Запрос проверки паспорта отправлен успешно')
                    else:
                        print('ОШИБКА при отправке запроса проверки паспорта')
                        print(passport_check)
                        print(passport_check.status_code)
                        print(passport_check.reason)
                        print(passport_check.text)
                        print(passport_check.raise_for_status())
                except requests.exceptions.Timeout:
                    print('Нет соединения')
        
        input('\nНажмите любую клавишу для продолжения...')
    except Exception as e:
        input(e)
