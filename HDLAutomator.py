import tkinter as tk
import subprocess
import base64
import logging
import tkinter.messagebox
import sys
import os
import time
import threading
import queue
import xml.etree.ElementTree as ET

        
class loaderGUI():
    
    def __init__(self,parent):
        self.filename = ""
        self.parent = parent
        self.frame = tk.Frame(self.parent, width= 500, height = 300)
        
        #filepath
        self.lblFilePath = tk.Label(self.parent,text = 'Filepath:')
        self.lblFilePath.place(x=30,y=20)
        
        self.entryFilePath = tk.Entry(self.parent,bd = 5, width=50)
        self.entryFilePath.place(x=110,y=20)
        self.entryFilePath.focus()

        self.btnBrowse = tk.Button(self.parent, text = 'Browse', command = self.browseFile, width = 10)
        self.btnBrowse.place(x=435,y=20)
        
        self.btnSubmit = tk.Button(self.parent, text = 'Submit', command = self.uploadFileIntoUCM, width = 10)
        self.btnSubmit.place(x=30,y=60)

        #UCMID
        self.lblUCMID = tk.Label(self.parent,text = 'UCM ID:')
        self.lblUCMID.place(x=30,y=100)

        self.entryUCMID = tk.Entry(self.parent,bd = 5,state='disabled')
        self.entryUCMID.delete(0)
        self.entryUCMID.place(x=110,y=100)
        
        #status
        self.lblUCMStatus = tk.Label(self.parent,text = 'UCM Status:')
        self.lblUCMStatus.place(x=30,y=140)

        self.entryUCMStatus = tk.Entry(self.parent,bd = 5,state='normal', width=65)
        self.entryUCMStatus.delete(0)
        self.entryUCMStatus.place(x=110,y=140)
            
        #HDLStatus
        self.lblHDLStatus = tk.Label(self.parent,text = 'HDL Status:')
        self.lblHDLStatus.place(x=30,y=180)

        self.textHDLStatus = tk.Text(self.parent, height=10, width=50)
        self.textHDLStatus.config(state='disabled')
        self.textHDLStatus.place(x=110,y=180)

        #Dataset Load Status
        self.lblDSStatus = tk.Label(self.parent,text = 'DS Status:')
        self.lblDSStatus.place(x=30,y=360)

        self.textDSStatus = tk.Text(self.parent, height=10, width=50)
        self.textDSStatus.config(state='disabled')
        self.textDSStatus.place(x=110,y=360)


        self.frame.pack()

    def browseFile(self):
        #from tkFileDialog import askopenfilename
        from tkinter.filedialog import askopenfilename
        #tk().withdraw() 
        self.filename = askopenfilename(  filetypes = (("Compese","*.zip"),("all files","*.zip")),
                                         title = "Choose a file.",
                                          initialdir= os.getcwd())
        
        self.entryFilePath.insert(0, self.filename)
        
    def uploadFileIntoUCM(self):
        
        if not self.entryFilePath.get():
            print('No filepath provided..')
            tk.messagebox.showerror("Error","Please provide filepath.")
            sys.exit(1)

        self.clearContent()

        print('Creating thread for UCM and HDL requests..')
        self.queue = queue.Queue()
        self.btnSubmit.config(state='disabled')
        threadTask(self.queue,(self.entryFilePath.get()).strip("'"),self).start()
        self.parent.after(100,self.process_queue)
        
        

    def clearContent(self):
        print('Clearning UI contents..')
        self.entryUCMStatus.configure(state='normal')
        self.entryUCMID.configure(state='normal')
        self.textHDLStatus.configure(state='normal')
        
        self.entryUCMStatus.delete(0,'end')
        self.entryUCMID.delete(0,'end')
        self.textHDLStatus.delete('1.0','end')
        
        self.entryUCMStatus.configure(state='disabled')
        self.entryUCMID.configure(state='disabled')
        self.textHDLStatus.configure(state='disabled')
      

    def beginDSCheck(self):
        #start poll thread
        print('Start DS status check..')
        self.queue = queue.Queue()
        print('Creating thread for DS Check requests..')
        threadTaskDSCheck(self.queue,self).start()
        self.parent.after(100,self.process_queue1)
        
    def process_queue(self):
        try:
            msg = self.queue.get(0)
            print('UCM and HDL requests complete..')
            self.beginDSCheck()
        except queue.Empty:
            self.parent.after(100,self.process_queue)

    def process_queue1(self):
        try:
            msg = self.queue.get(0)
            self.btnSubmit.configure(state='normal')
            print('DS Check request complete')
        except queue.Empty:
            self.parent.after(100,self.process_queue1)

    

class threadTaskDSCheck(threading.Thread):
    
    def __init__(self, queue,gui):
        print('In threadTaskDSCheck()..')
        threading.Thread.__init__(self)
        self.queue = queue
        self.gui = gui
    
    def run(self):
        print('threadTaskDSCheck started..')
        self.poll()
        print('threadTaskDSCheck completed..')

    def poll(self):
        
        rc = readConfig()

        from suds.client import Client
        #logging.basicConfig(level=logging.INFO)
        #logging.getLogger('suds.client').setLevel(logging.DEBUG)
        #logging.getLogger('suds.transport').setLevel(logging.DEBUG)

        print('creating client ws for DS Check')
        client = Client(rc.WSDLEndpoint, username = rc.userName, password = rc.password, retxml=True, faults=False)
        
        #self.ucmid='UCMFA225638'
        global UCMContentID
        paramStr = 'ContentId=' + UCMContentID
        print("paramStr" + paramStr)
        #paramStr = 'ContentId=' + 'UCMFA225638'
        
        while 1:
            print('Invoke WS for DS Check..')
            result = client.service.getDataSetStatusAsync(Parameters=''+paramStr)
            
            root = ET.fromstring(result)

            statusStr = '(the status will refresh every ' + rc.refreshTime + ' seconds..) \n'
            overallStatus = ''
            
            self.gui.textDSStatus.configure(state='normal')
            self.gui.textDSStatus.delete('1.0','end')
            self.gui.textDSStatus.configure(state='disabled')

            for child in root.iter():
                if child.tag == '{http://xmlns.oracle.com/apps/hcm/common/dataLoader/core/dataLoaderIntegrationService/types/}result' :
                    xml = ET.fromstring(child.text.lstrip().rstrip())
                    break

            for node in xml.findall('DATA_SET/STATUS'):
                overallStatus = node.text
                statusStr = statusStr + 'Overall Status: ' + node.text + '\n'
                #print('Overall Status:' + node.text)

            for node in xml.findall('DATA_SET/IMPORT/'):
                if node.tag == 'STATUS':
                    statusStr = statusStr + 'Import Status: ' + node.text + '\n'
                    #print('IMPORT  Status:' + node.text)
                if node.tag == 'PERCENTAGE_COMPLETE':
                    statusStr = statusStr + 'Import Percentage Completion: ' + node.text + '\n'
                    #print('Percentage complete:' + node.text)

            for node in xml.findall('DATA_SET/LOAD/'):
                if node.tag == 'STATUS':
                    statusStr = statusStr + 'Load Status: ' + node.text + '\n'
                    #print('EXPORT  Status:' + node.text)
                if node.tag == 'PERCENTAGE_COMPLETE':
                    statusStr = statusStr + 'Load Percentage Completion: ' + node.text + '\n'
                    #print('Percentage complete:' + node.text)

            self.gui.textDSStatus.configure(state='normal')
            self.gui.textDSStatus.insert('1.0',statusStr)
            self.gui.textDSStatus.configure(state='disabled')
            print("OverallStatus: " + overallStatus)
            
            if overallStatus == 'COMPLETED':
                print('Load Complete..')
                
                #send BI request to the server for the report
                print('Calling the BI report WS..')
                from suds.client import Client
                BIclient = Client(rc.BIWSDL, username = rc.userName, password = rc.password, retxml=True, faults=False)
                
                rrStr = ' '     
                #rrStr = rrStr + ' <ns0:reportRequest>'
                rrStr = rrStr + ' <ns0:attributeFormat>'+ rc.reportFormat +'</ns0:attributeFormat>'
                rrStr = rrStr + ' <ns0:parameterNameValues>'
                rrStr = rrStr + ' <ns0:item>'
                rrStr = rrStr + ' <ns0:name>CON</ns0:name>'
                rrStr = rrStr + ' <ns0:values>'
                rrStr = rrStr + ' <ns0:item>' + UCMContentID + '</ns0:item>'
                rrStr = rrStr + ' </ns0:values>'
                rrStr = rrStr + ' </ns0:item>'
                rrStr = rrStr + ' </ns0:parameterNameValues>'
                rrStr = rrStr + ' <ns0:reportAbsolutePath>'+ rc.reportPath +'</ns0:reportAbsolutePath>'
                rrStr = rrStr + ' <ns0:sizeOfDataChunkDownload>-1</ns0:sizeOfDataChunkDownload>'
                #rrStr = rrStr + ' </ns0:reportRequest>'
                
                from suds.sax.text import Raw
                rrStr = Raw(rrStr)                
                result = BIclient.service.runReport(rrStr,userID = rc.userName,password = rc.password)
                
                rootBI = ET.fromstring(result)
                print('Results fetched from BI Service..')
                for child in rootBI.iter():
                    if child.tag == '{http://xmlns.oracle.com/oxp/service/PublicReportService}reportBytes' :
                        rawBytes = child.text
                        print('Log File Created at - C:\\temp\HDLLOader\Logs\\' +  UCMContentID + '.' + rc.reportFormat)
                        statusStr = statusStr + 'Log File Created at - C:\\temp\HDLLOader\Logs\\' +  UCMContentID + '.' + rc.reportFormat + '\n'
                        self.gui.textDSStatus.configure(state='normal')
                        self.gui.textDSStatus.delete('1.0','end')
                        self.gui.textDSStatus.insert('1.0',statusStr)
                        self.gui.textDSStatus.configure(state='disabled')
                        open('C:\\temp\\HDLLOader\\Logs\\' + UCMContentID + '.' + rc.reportFormat ,'wb').write(base64.b64decode(rawBytes))
                        self.gui.btnSubmit.config(state='normal')
                        self.queue.put("Task Finished")
                        break
                break
            else:
                print('Load running..sleeping for '+ rc.refreshTime + ' seconds')                
                time.sleep(int(rc.refreshTime))


class threadTask(threading.Thread):
    
    def __init__(self, queue,fp,gui):
        print('In threadTask __init__')
        threading.Thread.__init__(self)
        self.queue = queue
        self.filePath = fp
        self.gui = gui
        
    def run(self):
        print('threadTask Started..')
        self.doLoadAndExecute()
        self.queue.put("Task Finished")
        print('threadTask finished..')

    def doLoadAndExecute(self):
        
        rc = readConfig()
        
        #cmdline params
        pUrl = ' --url="' + rc.endPoint + '"'
        pUser = ' --username="' + rc.userName.rstrip() + '"'
        pPassword = ' --password="' + rc.password.rstrip() + '"'
        pFile =  ' --primaryFile="' + self.filePath + '"'
        pTitle = ' --dDocTitle="' + os.path.split(self.filePath)[1] +'"'
        pSecGrp = ' --dSecurityGroup="FAFusionImportExport"'
        pDocAcc = ' --dDocAccount="hcm/dataloader/import"'

        cmdLine = 'java -jar "C:\\temp\\HDLLOader\\ridc\\oracle.ucm.fa_client_11.1.1.jar" UploadTool '
        cmdLine = cmdLine + pUrl + pUser + pPassword + pFile + pTitle +  pSecGrp + pDocAcc
        print('Command Line for UCM Load:' + cmdLine)
        #global UCMContentID
        #UCMContentID='UCMFA226773'
        
        print('Running Command from cmd..')
        from subprocess import Popen, PIPE, STDOUT
        p = Popen(cmdLine, stdout=PIPE,stderr=STDOUT, shell=True)
        

        lineCtr = 1
        linearray = []
        for line in p.stdout:
            linearray.append(line.decode('UTF-8', 'ignore'))

        self.gui.entryUCMStatus.configure(state='normal')
        self.gui.entryUCMStatus.insert(0,linearray[4])
        self.gui.entryUCMStatus.configure(state='disabled')
        
        if linearray[4].rstrip() == "Upload successful.":
            print('INFO Upload Successful..')
            UCMID = linearray[5].rstrip()
            UCMID = UCMID[UCMID.index('U'):-1]
            global UCMContentID
            UCMContentID = UCMID
            print('INFO UCM ID:' + UCMID)
            self.gui.entryUCMID.configure(state='normal')
            self.gui.entryUCMID.insert(0,UCMID)
            self.gui.entryUCMID.configure(state='disabled')
            print('Calling DataLoader Service..')
            self.invokeDataLoaderService(UCMID,rc)
             

    def invokeDataLoaderService(self,contentId,rc):
        
        from suds.client import Client
        #logging.basicConfig(level=logging.DEBUG)
        #logging.getLogger('suds.client').setLevel(logging.DEBUG)
        #print(rc.WSDLEndpoint)

        print('Client object created, request sent..')
        client = Client(rc.WSDLEndpoint, username = rc.userName, password = rc.password, retxml=True)
        result = client.service.importAndLoadDataAsync(ContentId=contentId)

        #parse the result here..
        self.gui.textHDLStatus.configure(state='normal')
        self.gui.textHDLStatus.insert('1.0',result)
        self.gui.textHDLStatus.configure(state='disabled')

        
class readConfig:

    configFile = open('C:\\temp\\HDLLOader\\HDLAutomationConfig.conf','r')
    for line in configFile:
        parts = line.split("=")

        if parts[0] == 'UserName':
            print('UserName : ' + parts[1])
            userName = parts[1].rstrip()

        if parts[0] == 'Password':
            print('Password : ' + parts[1])
            password = parts[1].rstrip()

        if parts[0] == 'Endpoint':
            print('EndPoint : ' + parts[1])
            endPoint = parts[1].rstrip()

        if parts[0] == 'WSDL':
            print('WSDL : ' + parts[1])
            WSDLEndpoint = parts[1].rstrip()

        if parts[0] == 'RefreshTime':
            print('RefreshTime: ' + parts[1]) 
            refreshTime = parts[1].rstrip()

        if parts[0] == 'BIWSDL':
            print('BIWSDL: ' + parts[1]) 
            BIWSDL = parts[1].rstrip()

        if parts[0] == 'ReportPath':
            print('ReportPath: ' + parts[1]) 
            reportPath = parts[1].rstrip()

        if parts[0] == 'ReportFormat':
            print('ReportFormat: ' + parts[1]) 
            reportFormat = parts[1].rstrip()

def main():
    
    global UCMContentID
    UCMContentID = ''


    root = tk.Tk()
    root.title('HCM Data Loader')

    w = 550
    h = 550
    x = 50
    y = 100
    root.geometry("%dx%d+%d+%d" % (w, h, x, y))
    root.resizable(False, False)

    print('Loading GUI...')
    gui = loaderGUI(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()
