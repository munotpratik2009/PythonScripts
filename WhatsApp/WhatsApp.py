from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlencode
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert

class WhatsApp:
	browser = webdriver.Chrome("c:\\temp\\chromedriver.exe")
	timeout = 20

	def __init__(self):
		self.browser.get("https://web.whatsapp.com/")
		WebDriverWait(self.browser,self.timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.jN-F5')))


	def send_message(self,phone, text):
		payload = urlencode({"phone": phone, "text": text, "source": "", "data": ""})
		self.browser.get("https://api.whatsapp.com/send?"+payload)
		try:
			Alert(self.browser).accept()
		except:
			print("No alert Found")

		WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#action-button")))
		send_message = self.browser.find_element_by_css_selector("#action-button")
		send_message.click()
		confirm = WebDriverWait(self.browser, self.timeout+5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]")))
		confirm.clear()
		confirm.send_keys(text+Keys.ENTER)
		
	#this name can be anything, contact name, blist or group name
	def send_message2(self, name, msg):
		search = self.browser.find_element_by_css_selector(".jN-F5")
		search.send_keys(name + Keys.ENTER)

		send_msg = WebDriverWait(self.browser, self.timeout).until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]")))
		send_msg.send_keys(msg + Keys.ENTER)  # send the message
		


msg = "Hey there!"
wa = WhatsApp()

wa.send_message2("Maa",msg)
wa.send_message2("pili",msg)

#basically created 