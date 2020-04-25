from re import sub, compile, findall, I
from urllib.error import HTTPError, URLError
from os import system
from random import randint
from time import sleep
from requests import get
from logging import error
from urllib.request import urlretrieve, build_opener, install_opener


class Utils:
    """
        this class used as service all commun
        function between all spider will be hree
    """

    def dowloadImg(self, url, imageFinalName):
        """
            this function take url and image name
            and it will download the image and save it
            into public folder
          :param url: image link
          :param imageFinalName: the final name
        """
        try:
            if imageFinalName is not None and url is not None:
                fileNameDestination = "public/{0}".format(imageFinalName)
                opener = build_opener()
                # set user agent
                opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')]
                install_opener(opener)
                urlretrieve(url, fileNameDestination)
                opener.close()

        except URLError as urlErr:
            error('URLError on %s' % urlErr)
            error('Url Error is : %s ' % url)

        except HTTPError as httpErr:
            error('HTTPError on %s' % httpErr)
            error('Url Error is : %s ' % url)

        except Exception as er:
            error('generale exception on %s', er)
            error('Url Error is : %s ' % url)


    def decodeEmailCloudFare(self, encodedString):
        """
        by pass email cloudfare protection

        this function decode and return email
        :param encodedString: email encoded
        :return: email
        """
        r = int(encodedString[:2], 16)
        email = ''.join([chr(int(encodedString[i:i + 2], 16) ^ r) for i in range(2, len(encodedString), 2)])
        return email

    def listToString(self, list):
        """
            convert list to String
            :param s: list
            :return: string
        """

        if list:
            str1 = " "

            # return string
            return (str1.join(list))

    def deleteLargeSpace(self, text):
        try:
            textToSplit = str(text)

            if textToSplit:
                return ' '.join(textToSplit.split())

        except Exception as e:
            error(e)

    def deleteTagFromHtml(self, text):
        """
        strip html text
        delete tags html
        :param text:
        :return:
        """

        text = str(text)

        clean = compile('<.*?>')

        clearTag = sub(clean, '', text)

        remouveTag = sub(clean, '', clearTag)

        remouvespace = sub(r"\s+", " ", remouveTag, flags=I)

        remouveChar = sub(r'[["\?\][()$%_"]', '', remouvespace, flags=I)
        try:
            result = remouveChar.replace('\\r', '').replace('\\n','').replace('\\t', '').replace('🔽', '').replace('\\xa0', '').replace('&amp;','').strip('"')

        except UnicodeEncodeError:
            raise Exception('Error Encodage')

        except UnicodeDecodeError:
            raise Exception('Error Decodage')
        except Exception as generaleErr:
            print(generaleErr)

        return result

    def extractEmailFromText(self, params):
        """
        this function take text as params and retrun
        one email address
        :param params:
        :return:
        """
        listemail = []
        try:
            if params is None:
                return None

            text = str(params)

            emails = findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text)
            if emails is not None:               ## check if result not none
                for email in emails:             ## starct for boocle
                    if email not in listemail:   ## check if email in list
                        listemail.append(email)  ## add email to list
                    return listemail[0]
            return None

        except IndexError:
            raise Exception('[!] list index out of range')

        except Exception as error:
            raise Exception('[!] Error while get email\n',error)

    def extcartLinkFomText(self, data):
        """
        This functon allow us to get all link from string support http and https
        :param data:
        :return:
        """
        listurls = []
        data = str(data)

        urls = findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]| [! * \(\),] | (?: %[0-9a-fA-F][0-9a-fA-F]))+', data)
        for url in urls:

            url = self.deleteTagFromHtml(url)
            if url not in listurls:
                listurls.append(url)

        if len(listurls) == 1:
            return listurls[0]

        return listurls

    def extractPhoneNumberFromText(self, params):
        """
        this function take text as params and return one nubmer phone
        :param params:
        :return:
        """
        Numberphone = []
        try:
            if not params:
                return None
            text = str(params)

            phones = findall(r"\d{2}?[-.\s+\s]?\d{2}[-.\s+\s]?\d{2}?[.\s+\s]?\d{2}[-.\s+\s]?\d{2}", text)
            if phones is not None:                  ## check if result not none
                for phone in phones:                ## starct for boocle
                    if phone not in Numberphone:    ## check if phone in list
                        Numberphone.append(phone)   ## add email to list
                    return Numberphone[0]
            return None
        except IndexError:
            raise Exception('[!] list index out of range')

        except Exception as error:
            raise Exception('[!] Error while get phone\n',error)

    def extractListPhoneNumberFromText(self, params):
        """
        this function take text as params and return
        list of nubmer phone
        :param params:
        :return:
        """
        Numberphone = []
        try:
            text = str(params)
            phones = findall(r"\d{2}?[-.\s+\s]?\d{2}[-.\s+\s]?\d{2}?[.\s+\s]?\d{2}[-.\s+\s]?\d{2}", text)
            if phones is not None:
                for phone in phones:
                    Numberphone.append(phone)
                return Numberphone
                return None
        except Exception as e:
            raise Exception(e)

    def extractListEmailFromText(self, params):
        """
        this function take text as params and exctart all url
        :param params:
        :return: list url
        """
        listemail = []
        try:
            text = str(params)
            emails = findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text)
            if emails is not None:
                for email in emails:
                    listemail.append(email)
                return listemail
            return None
        except Exception as e:
            raise Exception(e)

    def restartTor(self):
        """
        this function is used to reload tor service
        """
        try:
            Utils.getIpAdd()
            codeExecution = system('sudo systemctl restart tor')
            print("[+] code Exuction ", codeExecution)
            if codeExecution == 0:
                print("[+] restart Tor service ")
                print("[+] wait for restart service tor")
                sleep(2)
                Utils.getIpAdd()
        except KeyboardInterrupt:
            print("[!] Ctrl+c pressed ")
            exit(0)
        except Exception as er:
            print(er)

    @staticmethod
    def changeVpn():
        try:
            print("[+] Change Vpn address ")
            codeEx = system("sudo protonvpn connect -r")
            if codeEx == 0:
                print("[+] wait for restart vpn")
                Utils.randomSleeper(valueA=10, valueB=20)
        except Exception as vpnReloadErr:
            print("[-] %s" % vpnReloadErr)

    @staticmethod
    def getIpAdd():
        """
        this function is static
        function use to check
        ip public
        """
        try:
            proxies = {
                "https":"http://127.0.0.1:9080",
                "http":"http://127.0.0.1:9080",
            }

            url = "https://api.ipify.org/"
            req = get(url=url, proxies=proxies)
            print("[+] Your public ip address now is : ", req.text)
        except Exception as e:
            print(e)

    @staticmethod
    def randomSleeper(valueA, valueB):
        """
        this function here it used to sleep for random time
        bettwen valueA et valueB
        """
        try:

            sleepSecond = randint(valueA, valueB)

            print("[+] I will sleep for {} second".format(sleepSecond))

            sleep(sleepSecond)

            print("[+] This nice sleep oh let's continue")

        except KeyboardInterrupt:
            print("[!] Ctrl+c pressed ")
            exit(0)

        except Exception as er:
            print(er)
