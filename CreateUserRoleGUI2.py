
import json
import logging
import pickle
import queue
import requests
import threading
import tkinter as tk
from tkinter import *
from tkinter import ttk
#from UserCreds import *

LOGIN_URL = ""
LOGIN_USER = ""
LOGIN_PASS = ""


class HCMRoles(object):
	def __init__(self):
		self.id = ""
		self.auth = (LOGIN_USER, LOGIN_PASS)

	def fetch_all_roles(self):
		role_resource = '/hcmRestApi/scim/Roles'
		filter_atribute = '/?attributes=displayName,name,category'
		sort_attribute = '&orderBy=displayName'
		url = LOGIN_URL + role_resource + filter_atribute + sort_attribute
		print(url)
		response = requests.get(url, auth=self.auth)
		role_json = response.json()
		if response.status_code == '200':
			return response.status_code, role_json["Resources"]
		else:
			return response.status_code, []

class User(object):
	def __init__(self, user_name, fn, ln, active, password):
		self.id = ""
		self.user_name = user_name
		self.first_name = fn
		self.last_name = ln
		self.assigned_roles = ""
		self.active = active
		self.created = ""
		self.password = password
		self.auth = (LOGIN_USER, LOGIN_PASS)

	def create_user_payload(self):
		#name is split in first name and last name
		name_part = {}
		name_part["familyName"] = self.last_name
		name_part["givenName"] = self.first_name

		#Main payload
		payload = {}
		payload["name"] = name_part
		payload["active"] = self.active
		payload["userName"] = self.user_name
		payload["schemas"] = ["urn:scim:schemas:core:2.0:User"]
		payload["password"] = self.password
		payload = json.dumps(payload)

		return payload

	def create_user(self):
		user_resource = '/hcmRestApi/scim/Users'
		headers = {'Content-type': 'application/json'}
		datas = self.create_user_payload()

		response = requests.post(LOGIN_URL + user_resource, auth=self.auth, data=datas, headers=headers)
		# logger.debug(response.status_code, response.reason)
		# logger.debug(response.request.headers)
		# logger.debug(response.json())

		r = response.json()

		if response.ok:
			# logger.debug(r)
			self.id = r["id"]
			print(self.id)
			return True,"Success"
		else:
			err_msg = r['Errors'][0]['description']
			print("Error Encoutnered: " + err_msg)
			return False, err_msg

	def add_roles(self, list_of_roles):
		#covnert the lsit of roles to array fo ease of yse
		#https://cba.fa.us1.oraclecloud.com/hcmRestApi/scim/Roles/?filter=name eq "ORA_FND_IT_SECURITY_MANAGER_JOB"&attributes=id,displayName,name
		roles = list_of_roles.split(',')
		invalid_roles = []
		for role in roles:
			print(role)
			#1. get the id for each role, if role not found proceed with next one
			role_resource = '/hcmRestApi/scim/Roles'
			filter_query = '/?filter=name eq "' + role.strip() + '"'
			filter_atribute = '&attributes=id,displayName,name'
			url = LOGIN_URL + role_resource + filter_query + filter_atribute
			# logger.debug(url)
			print(url)

			response = requests.get(url, auth=self.auth)
			role_json = response.json()
			if len(role_json['Resources']) > 0 :
				role_id = role_json['Resources'][0]['id']
				role_code = role_json['Resources'][0]['name']
				role_name = role_json['Resources'][0]['displayName']

				print(role_id + ':' + role_name + ' - ' + role_code)

				#2.patch role with user ID
				#204 - No content repsonse
				url = LOGIN_URL + role_resource + "/" + role_id
				patch_data = '{"members":[{"value":"'+ self.id +'","operation": "ADD"}]}'
				headers = {'Content-type': 'application/json'}
				response = requests.patch(url, auth=self.auth, data=patch_data, headers=headers)
				# logger.debug(response.content)
				# logger.debug(response.status_code)
			else:
				invalid_roles.append(role.strip())

		return invalid_roles

class CreateUserGUI():

	def __init__(self, root):
		self.root = root
		self.drawGUI()
		#self.load_from_pickle()

	def _update_textbox(self, textbox, text, update=True):
		textbox.configure(state='normal')
		if update:
			current_status = textbox.get('1.0', 'end')
			text = current_status + text

		textbox.delete('1.0', 'end')
		textbox.insert('1.0', text)
		textbox.configure(state='disabled')

	def drawGUI(self):
		style = ttk.Style(self.root)
		style.configure('lefttab.TNotebook')
		notebook = ttk.Notebook(self.root, style='lefttab.TNotebook')
		f_create_user = tk.Frame(notebook, width=500, height=500)
		f_instance_details = tk.Frame(notebook, width=500, height=500)
		self.f_roles = tk.Frame(notebook, width=500, height=500)

		#instance information URL
		lbl_url = tk.Label(f_instance_details,text = 'HCM URL:')
		lbl_url.place(x=10, y = 10)
		self.entry_url = tk.Entry(f_instance_details,bd = 1, width=50)
		self.entry_url.place(x= 110,y = 10)
		#self.entry_url.focus()

		#username
		lbl_username = tk.Label(f_instance_details,text = 'Username:')
		lbl_username.place(x=10,y=50)
		self.entry_username = tk.Entry(f_instance_details, bd = 1, width=50)
		self.entry_username.place(x= 110,y = 50)

		#password
		lbl_password = tk.Label(f_instance_details,text = 'Password:')
		lbl_password.place(x=10,y=90)
		self.entry_password = tk.Entry(f_instance_details, bd = 1, width=50, show="•")
		self.entry_password.place(x= 110,y = 90)

		#Save
		btn_save = tk.Button(f_instance_details, text = 'Save', command = self.save_to_pickle, width = 10, fg="black", bd=3)
		btn_save.place(x=10, y= 130)

		#Create User
		lbl_new_usrname = tk.Label(f_create_user,text = '*UserName:')
		lbl_new_usrname.place(x=10, y = 10)
		self.entry_new_un = tk.Entry(f_create_user,bd = 1, width=50)
		self.entry_new_un.place(x= 110,y = 10)
		self.entry_new_un.focus()

		#First Name
		lbl_fn = tk.Label(f_create_user,text = 'First Name:')
		lbl_fn.place(x=10,y=40)
		self.entry_fn = tk.Entry(f_create_user, bd = 1, width=50)
		self.entry_fn.place(x= 110,y = 40)

		#Last Name
		lbl_ln = tk.Label(f_create_user,text = 'Last Name:')
		lbl_ln.place(x=10,y=70)
		self.entry_ln = tk.Entry(f_create_user, bd = 1, width=50)
		self.entry_ln.place(x= 110,y = 70)

		#password
		lbl_pw = tk.Label(f_create_user,text = '*Password:')
		lbl_pw.place(x=10,y=100)
		self.entry_pw = tk.Entry(f_create_user, bd = 1, width=50, show="•")
		self.entry_pw.place(x= 110,y = 100)

		#roles
		lbl_roles = tk.Label(f_create_user,text = 'Roles to be assigned (separated by comma)')
		lbl_roles.place(x=10,y=130)
		self.text_role = tk.Text(f_create_user, height=8, width=50)
		self.text_role.place(x=10,y=150)

		#Create User button
		self.btn_create_usr = tk.Button(f_create_user, text = 'Create User', command = self.call_create_user, width = 20, fg="black", bd=3)
		self.btn_create_usr.place(x=10, y= 290)

		#status area
		lbl_status = tk.Label(f_create_user,text = 'Status:')
		lbl_status.place(x=10,y=330)
		self.text_status = tk.Text(f_create_user, height=5, width=50,state='disabled')
		self.text_status.place(x=10,y=350)

		#Tab 3
		#add refresh role button
		self.btn_fetch_roles = tk.Button(self.f_roles, text = 'Fetch roles from system', command = self.fetch_roles, width = 30, fg="black", bd=3)
		self.btn_fetch_roles.place(x=10, y= 10)

		self.lbl_roles_fetch_status = tk.Label(self.f_roles, text='Status:')
		self.lbl_roles_fetch_status.place(x=10, y=50)


		# cols = ('role_name', 'role_code', 'role_category')
		# tv = ttk.Treeview(f_roles, columns=cols, show='headings')
		# f_roles.grid_rowconfigure(0, weight = 1)
		# f_roles.grid_columnconfigure(0, weight = 1)

		# tv.heading('#1', text='Role Name', anchor='w')
		# tv.heading('#2', text='Role Code')
		# tv.heading('#3', text='Role Category')
		# #tv.pack(fill='both', expand=True)

		# vsb = ttk.Scrollbar(f_roles, orient="vertical", command=tv.yview)
		# vsb1 = ttk.Scrollbar(f_roles, orient="horizontal", command=tv.xview)
		# tv.configure(yscrollcommand=vsb.set, xscrollcommand=vsb1.set)
		# tv.bind("<Double-1>", self.fetch_roles)
		# #vsb.pack(side='right', fill='y')
		# #vsb1.pack(side='bottom', fill='x')
		# tv.grid(row=0,column=0, sticky='nsew')
		# vsb.grid(row=0,column=1,sticky='ns')
		# vsb1.grid(row=1,column=0, sticky='ew')
		# self.treeview = tv

		# for i in range(1,100):
		# 	tv.insert('','end',text="First",values=(i,i,i))

		notebook.add(f_create_user, text='Create User')
		notebook.add(f_instance_details, text='Instance Details')
		notebook.add(self.f_roles, text='Roles')

		notebook.pack(expand=1, fill='both')

	def fetch_roles(self):
		self.thread_role = threading.Thread(target=self.process_fetch_roles)
		self.thread_role.start()
		self.check_fetch_roles()

	def check_fetch_roles(self):
		if self.thread_role.is_alive():
			self.root.after(2, self.check_fetch_roles)
		else:
			self.show_progress_roles(False)

	def process_fetch_roles(self):
		self.show_progress_roles(True)
		self.get_current_login_details()
		roles = HCMRoles().fetch_all_roles()
		out_file = open('RoleDetails.csv','w')
		for role in roles:
			out_file.write(role["displayName"] + "," + role["name"] + "," + role["category"] + '\n')
		out_file.close()

	def show_progress_roles(self, p_running):
		if p_running:
			self.btn_fetch_roles.configure(state='disabled')
			self.progress_bar_roles = ttk.Progressbar(self.f_roles, orient=HORIZONTAL, length=400, mode='indeterminate', takefocus=True)
			self.progress_bar_roles.place(x=10, y=70)
			self.progress_bar_roles.start()
			#self.title = 'Working..'
			self.lbl_roles_fetch_status.configure(text="Status: Fetching roles..")
		else:
			self.progress_bar_roles.stop()
			self.progress_bar_roles.destroy()
			#self.lbl_roles_fetch_status.destroy()
			#self.title = 'HCM User Creation'
			self.lbl_roles_fetch_status.configure(text="Status: Complete! Please chk fld")
			self.btn_fetch_roles.configure(state='normal')


	def save_to_pickle(self):
		#save to pickle
		pfile = open('data.pkl', 'wb')
		save_details = {}
		save_details["url"] = self.entry_url.get()
		save_details["username"] = self.entry_username.get()
		save_details["password"] = self.entry_password.get()
		pickle.dump(save_details, pfile, -1)
		pfile.close()


	def load_from_pickle(self):
		pfile = open('data.pkl', 'rb')
		try:
			save_details = pickle.load(pfile)
			self.entry_url.delete(0,'end')
			self.entry_username.delete(0,'end')
			self.entry_password.delete(0,'end')

			self.entry_url.insert(0,save_details["url"])
			self.entry_username.insert(0,save_details["username"])
			self.entry_password.insert(0,save_details["password"])
		except Exception as e:
			#pickle file is empty, pass
			print(str(e))
			pass

		pfile.close()

	def get_current_login_details(self):
		global LOGIN_URL, LOGIN_USER, LOGIN_PASS

		LOGIN_URL = self.entry_url.get()
		LOGIN_USER = self.entry_username.get()
		LOGIN_PASS = self.entry_password.get()



	def call_create_user(self):
		self.thread_user = threading.Thread(target=self.process_create_user)
		self.thread_user.start()
		self.check_create_user_thread()


	def process_create_user(self):
		#validate if url, username, password are populated
		self.btn_create_usr.configure(state='disabled')
		self.get_current_login_details()
		user_name = self.entry_new_un.get()
		fn = self.entry_fn.get()
		ln = self.entry_ln.get()
		user_pw = self.entry_pw.get()
		self._update_textbox(self.text_status, 'Creating User ' + user_name + '..')
		create_user = User(user_name, fn, ln, True, user_pw)
		#r, r_msg = create_user.create_user()
		create_user.id = '778811B3AC0F611DE0501790298A508F'
		r = True

		if r:
			self._update_textbox(self.text_status, 'User created Successfully!')
			self._update_textbox(self.text_status, 'Attempting to add roles to the user..')

			if len(self.text_role.get('1.0')) != 0:
				#roles are present, add them
				invalid_roles = create_user.add_roles(self.text_role.get('1.0','end'))
				if len(invalid_roles) > 0:

					self._update_textbox(self.text_status, 'Roles Added. Following roles are invalid')
					list_inv_roles = '\n'.join(iroles for iroles in invalid_roles)
					self._update_textbox(self.text_status, list_inv_roles)
					self.text_status.see('end')



	def check_create_user_thread(self):
		if self.thread_user.is_alive():
			self.root.after(2, self.check_create_user_thread)
		else:
			self.btn_create_usr.configure(state='normal')



def main():
	root = tk.Tk()
	root.title('HCM User Creation')
	root.geometry('430x470')
	root.resizable(width=False, height=False)
	CreateUserGUI(root)
	root.mainloop()

if __name__ == '__main__':
	main()
