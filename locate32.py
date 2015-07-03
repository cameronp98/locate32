#!/usr/bin/python
# sources:
# app I'm copying to linux: http://sourceforge.net/projects/locate32/?source=typ_redirect
# app I borrowed tray stuff from: http://kde-apps.org/content/show.php/CpuFreq+Tray?content=67720
# Qstuff: http://pyqt.sourceforge.net/Docs/PyQt4/qtgui.html
# Popen: http://stackoverflow.com/questions/2837214/python-popen-command-wait-until-the-command-is-finished
# Popen.communicate: https://docs.python.org/2/library/subprocess.html#subprocess.Popen.communicate
# threading: http://stackoverflow.com/questions/636561/how-can-i-run-an-external-command-asynchronously-from-python
# sudo: http://stackoverflow.com/questions/5191878/change-to-sudo-user-within-a-python-script
# shlex example: http://stackoverflow.com/questions/4091242/subprocess-call-requiring-all-parameters-to-be-separated-by-commas
# oldschool kill thread: https://web.archive.org/web/20130503082442/http://mail.python.org/pipermail/python-list/2004-May/281943.html
# freaking python garbage collection eats program after showing window: http://stackoverflow.com/questions/18061178/pyqt-window-closes-after-launch
# creating windows is odd: https://gist.github.com/justinfx/1951709
# more on window creation: http://www.learningpython.com/2008/09/20/an-introduction-to-pyqt/
# minimize to tray: https://stackoverflow.com/questions/758256/pyqt4-minimize-to-tray
# layout and widgets: https://stackoverflow.com/questions/8814452/pyqt-how-to-add-separate-ui-widget-to-qmainwindow
# design in qt creator, save, then convert to py file 
# sudo apt-get install qtcreator pyqt4-dev-tools
# pyuic4 mainwindow.ui -o mainwindow.py
# http://pythonthusiast.pythonblogs.com/230_pythonthusiast/archive/1358_developing_cross_platform_application_using_qt_pyqt_and_pyside__gui_application_development-part_5_of_5.html
# pushbutton code for generated gui: https://stackoverflow.com/questions/11113247/how-does-one-make-a-button-in-the-main-window-open-a-different-window
# redirect output of subproces: https://stackoverflow.com/a/3247271
# string splitting: https://stackoverflow.com/questions/25253120/python-split-string-by-space-and-strip-newline-char#25253160
# dump variable:
#	  from inspect import getmembers
#	  from pprint import pprint
#	  pprint(getmembers(output))
# dump variable to file
#	  from inspect import getmembers
#	  from pprint import pprint
#	  logFile=open('mylogfile'+'.txt', 'w')
#	  pprint(getmembers(dataobject), logFile)
#
# for open folder/open file menu: https://stackoverflow.com/questions/23993895/python-pyqt-qtreeview-example-selection
# handle KeyboardInterrupt: https://stackoverflow.com/questions/26893377/how-to-close-windows-in-pyqtgraph
# Another way: https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python
# https://stackoverflow.com/questions/4938723/what-is-the-correct-way-to-make-my-pyqt-application-quit-when-killed-from-the-co
# definite way (NOT GRACEFUL): https://stackoverflow.com/a/6072360
# https://stackoverflow.com/questions/2963263/how-can-i-create-a-simple-message-box-in-python
# http://doc.qt.io/qt-4.8/qmessagebox.html
# get directory from full path: http://stackoverflow.com/questions/15022854/get-the-directory-path-of-absolute-file-path-in-python
# qmodelindex: http://stackoverflow.com/questions/25943153/how-to-access-data-stored-in-qmodelindex
# http://stackoverflow.com/questions/13564550/resizing-widgets-in-pyqt4
# http://www.qtforum.org/article/38989/how-to-make-qt-widgets-resize-automatically.html
# -> http://stackoverflow.com/a/21467559
# https://forum.qt.io/topic/19152/qlayout-attempting-to-add-qlayout/2
# http://stackoverflow.com/questions/1064335/in-python-2-5-how-do-i-kill-a-subprocess
# analyze segmentation fault: http://stackoverflow.com/a/10035594
# gdb python
# (gdb) run /path/to/script.py
# ## wait for segfault ##
# (gdb) backtrace
# # stack trace of the c code
#TODO

#DONE_get update command to work
#\show notifications for update success/failure
#DONE->make search screen
#\use QColumnView and QFileSystemModel instead of QTextBrowser for results
#fix 
#QObject::connect: Cannot queue arguments of type 'QTextCursor'
#(Make sure 'QTextCursor' is registered using qRegisterMetaType().)
#http://www.qtforum.org/article/24502/gui-crash.html
#DONE\fix grey search button after search is done
#make settings screen
#make about screen
#make paths for kdesudo and updatedb variables and settings
#DONE_gksu/gksudo check
#DONE-fix main thread so you can use Ctrl+C to break
#DONE-don't show right click context menu on startup or no search results
#DONE-show search screen on doubleclick
#DONE-double check animation loop(when killing updatedb)
#DONE-clicking search sometimes generates Segmentation fault
#DONE-fix resizing and low res window looks
#DONE-ask if sure when searching for nothing (*)
#SIZE SORTS BY STRING, NOT BY INT-sort by filename/date created/size
# DONE- TRY http://www.linuxquestions.org/questions/programming-9/pyside-qtreewidget-numeric-sorting-4175502323/#post5156692
# DONE-fix ProxyModel(QSortFilterProxyModel) so we can get index to get stuff for context menu
#DONE-add Open with.. dialog
#-get Settings screen to work, start using conf file?
#-Ctrl+F in search window to search results?
#-proper way to kill updatedb thread, only kill our updatedb thread not every process updatedb
#-look into:
#	(during startup)
#	Bus::open: Can not get ibus-daemon's address. 
#	IBusInputContext::createInputContext: no connection to ibus-d
#-look into:
#	#when building search list)
#       #QObject::connect: Cannot queue arguments of type 'Qt::Orientation' 
#	(Make sure 'Qt::Orientation' is registered using qRegisterMetaType()
#-clean code
#

from multiprocessing import Process
import subprocess, sys, os, time, threading, shlex, time, signal, datetime
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT 
import ctypes  # An included library with Python install.
#from pprint import pprint
#from inspect import getmembers
from pipes import quote
	  
#sys.settrace
global updateTimer
updateTimer = QtCore.QTimer()
global searchTimer
searchTimer = QtCore.QTimer()
global updateAnimCount
global searchAnimCount
global updatingProcess
global updateIsDone
updateIsDone = False
global UpdateAction
global output
global sucommand
global haveSearchResults 
global minimize_on_exit
global notify_on_updatedb_complete
haveSearchResults = False


signal.signal(signal.SIGINT, signal.SIG_DFL) #So we can Ctrl+C out

#from http://www.linuxquestions.org/questions/programming-9/pyside-qtreewidget-numeric-sorting-4175502323/#post5156692
#with slight modification
class ProxyModel(QtGui.QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(ProxyModel, self).__init__(parent)

    def lessThan(self, left, right):
        leftData = self.sourceModel().data(left).toString()
        rightData = self.sourceModel().data(right).toString()
        if(leftData == 'Access Denied'):
	     return True
	elif(leftData == '<1'):
	     return True
	elif(rightData == 'Access Denied'):
	     return False
	elif(rightData == '<1'):
	     return False
	else:
	  #print str(leftData) + " < " + str(rightData) + " = " + str(int(leftData) < int(rightData))
	  try:
	      return int(leftData) < int(rightData)
	  except ValueError:
	      return leftData < rightData

#custom class so we can use the context menu on a qtreeview
class myQTreeView(QtGui.QTreeView):
  
  def __init__(self, parent=None):
    super(QtGui.QTreeView, self).__init__(parent)
        
  global haveSearchResults
  global proxymodel
  proxymodel = ProxyModel()
  
  @pyqtSlot()
  def OpenFile(self):
    indexlist = self.selectedIndexes()
    if len(indexlist)>3:
      reply = QtGui.QMessageBox.warning(self,"Open File question","Multiple items selected, open all?",QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
      if(reply == QtGui.QMessageBox.Yes):
	for indexitem in self.selectedIndexes():
	  if(indexitem.column()==0):
	    #print "indexitem="+str(proxymodel.sibling(indexitem.row(),0,indexitem).data().toString()
	    filepath = proxymodel.sibling(indexitem.row(),0,indexitem).data().toString()
	    filepath2 = str(filepath)
	    filepath3 = quote(filepath2)
	    #print "xdg-open "+ filepath3
	    result =  subprocess.call(shlex.split("xdg-open "+ filepath3))
    else:		   
    #print "indexitem="+str(proxymodel.sibling(indexitem.row(),0,indexitem.data().toString()))
      filepath = proxymodel.sibling(self.currentIndex().row(),0,self.currentIndex()).data().toString()
      filepath2 = str(filepath)
      filepath3 = quote(filepath2)
      #print "xdg-open "+ filepath3
      result =  subprocess.call(shlex.split("xdg-open "+ filepath3))

  @pyqtSlot()
  def OpenFolder(self):
    indexlist = self.selectedIndexes()
    if len(indexlist)>3:
      reply = QtGui.QMessageBox.warning(self,"Open Folder question","Multiple items selected, open all folders?",QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
      if(reply == QtGui.QMessageBox.Yes):
	for indexitem in self.selectedIndexes():
	  if(indexitem.column()==0):
	    #print "indexitem="+str(proxymodel.sibling(indexitem.row(),0,indexitem).data().toString()
	    filepath = proxymodel.sibling(indexitem.row(),0,indexitem).data().toString()
	    filepath2 = str(filepath)
	    filepath3 = os.path.dirname(filepath2)
	    filepath4 = quote(filepath3)
	    #print "xdg-open "+ filepath3
	    result =  subprocess.call(shlex.split("xdg-open "+ filepath4))
    else:		   
    #print "indexitem="+str(proxymodel.sibling(indexitem.row(),0,indexitem.data().toString()))
      filepath = proxymodel.sibling(self.currentIndex().row(),0,self.currentIndex()).data().toString()
      filepath2 = str(filepath)
      filepath3 = os.path.dirname(filepath2)
      filepath4 = quote(filepath3)
      result =  subprocess.call(shlex.split("xdg-open "+ filepath4))
    
  @pyqtSlot()
  def OpenWith(self):
    indexlist = self.selectedIndexes()
    filepath = ''
    #print "len(indexlist)="+str(len(indexlist))
    if len(indexlist)>3:
      reply = QtGui.QMessageBox.warning(self,"Open File With question","Multiple items selected, continue?",QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
      if(reply == QtGui.QMessageBox.Yes):
	reply = QtGui.QMessageBox.warning(self,"Open File With question2","Open all items with same program?",QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
	if(reply == QtGui.QMessageBox.Yes):
	    #print "open files with single program stub"
	    text, ok = QtGui.QInputDialog.getText(self, 'Open with...','Open selected files with:')
	    if ok:
	      for indexitem in self.selectedIndexes():
		  if(indexitem.column()==0):
		      filepath = proxymodel.sibling(indexitem.row(),0,indexitem).data().toString()
		      filepath2 = str(filepath)
		      filepath3 = quote(filepath2)
		      try:
			result =  subprocess.call(shlex.split(str(text) +" "+ filepath3))
			#print "result="+str(result)
		      except Exception as e: 
			QtGui.QMessageBox.warning(main_window,"Open With error","Error when trying to open \""+str(filepath)+"\" with \""+str(text)+"\".\n\nError message: "+str(e))   
	else:
	    filepath = ''
	    #print "open files with multi programs stub"	    
	    for indexitem in self.selectedIndexes():
		  if(indexitem.column()==0):
		      text, ok = QtGui.QInputDialog.getText(self, 'Open with...','Open \"'+str(proxymodel.sibling(indexitem.row(),0,indexitem).data().toString() +'\" with:'))
		      if ok:
			filepath = proxymodel.sibling(indexitem.row(),0,indexitem).data().toString()
			filepath2 = str(filepath)
			filepath3 = quote(filepath2)
			try:
			  result =  subprocess.call(shlex.split(str(text) +" "+ filepath3))
			  #print "result="+str(result)
			except Exception as e: 
			  QtGui.QMessageBox.warning(main_window,"Open With error","Error when trying to open \""+str(filepath)+"\" with \""+str(text)+"\".\n\nError message: "+str(e))
    else: #single item selected
         text, ok = QtGui.QInputDialog.getText(self, 'Open with...','Open \"'+str(proxymodel.sibling(self.currentIndex().row(),0,self.currentIndex()).data().toString() +'\" with:'))
	 if ok:
	  filepath = proxymodel.sibling(self.currentIndex().row(),0,self.currentIndex()).data().toString()
	  filepath2 = str(filepath)
	  filepath3 = quote(filepath2)
	  try:
	    result =  subprocess.call(shlex.split(str(text) +" "+ filepath3))
	  #print "result="+str(result)
	  except Exception as e: 
	    QtGui.QMessageBox.warning(main_window,"Open With error","Error when trying to open \""+str(filepath)+"\" with \""+str(text)+"\".\n\nError message: "+str(e))
      
	    
	
  @pyqtSlot(QtCore.QPoint)
  def contextMenuRequested(self,point):
      if(haveSearchResults):
	    menu	 = QtGui.QMenu()   
	    
	    action1 = menu.addAction("Open file")
	    self.connect(action1,SIGNAL("triggered()"),self,SLOT("OpenFile()"))	
	    
	    action2 = menu.addAction("Open folder") 
	    self.connect(action2,SIGNAL("triggered()"),self,SLOT("OpenFolder()"))
	     
	    seperator1 = menu.addSeparator()
	    
	    action3 = menu.addAction("Open with...") 
	    self.connect(action3,SIGNAL("triggered()"),self,SLOT("OpenWith()"))
	    
	    menu.exec_(self.mapToGlobal(point))  

	    
  @classmethod
  def _createRow(cls, *args):
      return [cls._createItem(value) for value in args]

  @staticmethod
  def _createItem(data):
      item = QStandardItem(data)
      flags = item.flags()
      flags ^= Qt.ItemIsEditable
      item.setFlags(flags)
      return item

#thanks qt creator!
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.centralWidget = QtGui.QGroupBox(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        
        form = QtGui.QGridLayout()

        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(320, 200)
        MainWindow.setTabShape(QtGui.QTabWidget.Rounded)

        self.lineEdit = QtGui.QLineEdit()
        self.lineEdit.setGeometry(QtCore.QRect(10, 10, 211, 26))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.pushButton = QtGui.QPushButton()
        self.pushButton.setGeometry(QtCore.QRect(230, 10, 81, 26))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton2 = QtGui.QPushButton()
        self.pushButton2.setGeometry(QtCore.QRect(230, 10, 81, 26))

	form.addWidget(self.lineEdit, 1,0)
	form.addWidget(self.pushButton,1,1)

	
	self.treeView = myQTreeView(self.centralWidget)
	self.treeView.setSortingEnabled(True)
	self.treeView.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.treeView.setGeometry(QtCore.QRect(10, 40, 301, 141))
        self.treeView.setObjectName(_fromUtf8("treeView"))   
        form.addWidget(self.treeView,2,0)
        
        self.treeView.connect(self.treeView,QtCore.SIGNAL("triggered()"),self.treeView.OpenFile)
	self.treeView.connect(self.treeView,QtCore.SIGNAL("triggered()"),self.treeView.OpenFolder)
	self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu); 
	self.treeView.connect(self.treeView,SIGNAL("customContextMenuRequested(QPoint)"),self.treeView,SLOT("contextMenuRequested(QPoint)"))
	
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 320, 22))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))        
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtGui.QToolBar(MainWindow)
        self.mainToolBar.setObjectName(_fromUtf8("mainToolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MainWindow.setStatusBar(self.statusBar)
	MainWindow.setCentralWidget(self.centralWidget)

        self.centralWidget.setLayout(form)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Locate32 - Search", None))
        self.pushButton.setText(_translate("pushButton", "Search", None))

        
class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
  	global minimize_on_exit

	def __init__(self, win_parent = None):
		super(MainWindow, self).__init__()
		self.setupUi(self)
		# connect the clicked signal to on_button_clicked() method
		self.pushButton.clicked.connect(self.on_button_clicked)
		self.pushButton2.clicked.connect(self.on_button2_clicked)
		self.lineEdit.returnPressed.connect(self.lineEditReturnPressed) 
		self.lineEdit.setFocus()
		self.pushButton2.setEnabled(False)

	def on_button_clicked(self, b=None):
	  doSearch()
	 
	def on_button2_clicked(self, b=None):
	  StopSearch()

	
	def lineEditReturnPressed(self, b=None):
	  doSearch()
	
	#def on_treeView_clicked(self, index):
	#  global proxymodel
	#  print proxymodel.sibling(index.row(),0,index).data().toString()
	
	#  print "on_treeView_calicked - row="+str(index.row())
	#  print proxymodel.data(index).toString()
		
	def closeEvent(self, event):
		#print "close event:"+str(event)
		#print "MainWindow() - closeEvent("+str(event.type())+") minimize_on_exit="+str(minimize_on_exit) 
		if(minimize_on_exit):
		  self.hide()
		  event.ignore()
		else:
		 # print "MainWindow() - closeEvent("+str(event.type())+") - should close"
		  event.accept()

class Ui_SettingsWindow(object):
    def setupUi(self, SettingsWindow):
        SettingsWindow.setObjectName(_fromUtf8("SettingsWindow"))
        SettingsWindow.resize(366, 139)
        self.centralWidget = QtGui.QWidget(SettingsWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        
        self.kaputlabel = QtGui.QLabel(self.centralWidget)
        self.kaputlabel.setGeometry(QtCore.QRect(20, 60, 150, 21))
        self.kaputlabel.setText("Settings are currently disabled.")
        
        self.cb_minimize = QtGui.QCheckBox(self.centralWidget)
        self.cb_minimize.setGeometry(QtCore.QRect(20, 10, 131, 21))
        self.cb_minimize.setObjectName(_fromUtf8("cb_minimize"))
        self.cb_minimize.setCheckState(2)
        self.cb_minimize.setEnabled(False) #disabled as not working, have to figure out setting variable across classes
        
        self.cb_notification = QtGui.QCheckBox(self.centralWidget)
        self.cb_notification.setGeometry(QtCore.QRect(20, 40, 351, 21))
        self.cb_notification.setObjectName(_fromUtf8("cb_notification"))
        self.cb_notification.setCheckState(2)
        self.cb_notification.setEnabled(False) #disabled as not working, have to figure out setting variable across classes
        self.retranslateUi(SettingsWindow)
        QtCore.QMetaObject.connectSlotsByName(SettingsWindow)

    def retranslateUi(self, SettingsWindow):
        SettingsWindow.setWindowTitle(_translate("SettingsWindow", "Locate32 - Settings", None))
        self.cb_minimize.setText(_translate("SettingsWindow", "Minimize to tray", None))
        self.cb_notification.setText(_translate("SettingsWindow", "Show notification when finished updating database", None))
        
class SettingsWindow(QtGui.QWidget, Ui_SettingsWindow):
	global minimize_on_exit
	global notify_on_updatedb_complete

	def __init__(self, win_parent = None):
		super(SettingsWindow, self).__init__()
		self.setupUi(self)
		self.hide()
		self.cb_minimize.stateChanged.connect(self.cb_minimize_changed)
		self.cb_notification.stateChanged.connect(self.cb_notification_changed)
		
	def cb_minimize_changed(self,state):
	  if(state==2):
	    minimize_on_exit = True
	  elif(state==0):
	    minimize_on_exit = False
	  print "cb_minimize_changed_changed("+str(state)+") - minimize_on_exit="+str(minimize_on_exit)
	
	def cb_notification_changed(self,state):
	  if(state==2):
	    notify_on_updatedb_complete = True
	  elif(state==0):
	    notify_on_updatedb_complete = False
	  print "cb_notification_changed("+str(state)+") - notify_on_updatedb_complete="+str(notify_on_updatedb_complete)
		
	def closeEvent(self, event):
		#print "close event:"+str(event)
		self.hide()
		event.ignore()

class TrayIcon(QtGui.QSystemTrayIcon):

	def __init__(self, win_parent = None):
		QtGui.QMainWindow.__init__(self, win_parent)
		
		#tray icon
		global LocateIcon
		LocateIcon = QtGui.QIcon("icons/locate32.png") #main icon
		self.setIcon(LocateIcon)
		
		self.setToolTip("Locate32")	
		
		#menu icons below, currently empty
		OpenIcon = QtGui.QIcon("") #needs icon?
		UpdateIcon = QtGui.QIcon("") #needs icon?
		StopUpdateIcon = QtGui.QIcon("") #needs icon?
		SettingsIcon = QtGui.QIcon("") #needs icon?
		AboutIcon = QtGui.QIcon("") #needs icon?
		QuitIcon = QtGui.QIcon("") #needs icon?
	
		#right click menu content
		global UpdateAction
		global OpenAction
		global StopUpdateAction
		global AboutAction
		global QuitAction
		ActionsMenu = QtGui.QMenu()
		OpenAction = ActionsMenu.addAction(OpenIcon,"Open Locate...")
		ActionsMenu.addSeparator()
		UpdateAction = ActionsMenu.addAction(UpdateIcon,"Update Database")
		StopUpdateAction = ActionsMenu.addAction(StopUpdateIcon,"Stop Updating")
		ActionsMenu.addSeparator()
		SettingsAction = ActionsMenu.addAction(UpdateIcon,"Settings")
		AboutAction = ActionsMenu.addAction(UpdateIcon,"About")
		ActionsMenu.addSeparator()
		QuitAction = ActionsMenu.addAction(QuitIcon,"Exit")

		# -- Now add the menu:
		# -- trigger the check action to set current state
		self.setContextMenu(ActionsMenu)
		
		# -- connect the actions:
		self.connect(OpenAction,QtCore.SIGNAL("triggered()"),showSearchScreen)
		self.connect(UpdateAction,QtCore.SIGNAL("triggered()"),updateDB)
		self.connect(StopUpdateAction,QtCore.SIGNAL("triggered()"),stopUpdateDB)
		self.connect(SettingsAction,QtCore.SIGNAL("triggered()"),showSettingScreen)
		self.connect(AboutAction,QtCore.SIGNAL("triggered()"),showAbout)
		self.connect(QuitAction,QtCore.SIGNAL("triggered()"),exitProperly)
		     
		#disable "Stop Updating" as nothing is running
		StopUpdateAction.setEnabled(False)

 
def showSearchScreen():
  global main_window
  main_window.show()

#from https://stackoverflow.com/a/1526089
def modif_date(filename):
  try:
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)
  except Exception as e: 
    return "Access Denied"

def file_size(path):
  try:
      itemsize = os.path.getsize(path)
      #itemsize = itemsize/1024 #KB
      itemsize = itemsize/1048576 #MB
      if itemsize==0:
	itemsize = "<1"
      else:
	itemsize = str(itemsize)
      return itemsize
  except Exception as e: 
    return "Access Denied"
  
def doSearch():
  	global main_window
  	global viewmodel
  	global output
  	global searchIsDone
  	global searchAnimCount
  	global haveSearchResults
  	global searchThreadVar
  	global proxymodel
  	main_window.pushButton.setEnabled(False)
  	continuesearch = True
  	searchIsDone = False
  	main_window.treeView.setModel(None)

	main_window.lineEdit.setEnabled(False)
	
	main_window.pushButton2.setEnabled(True)
	
	viewmodel = QtGui.QStandardItemModel()
        
        proxymodel.setSourceModel(viewmodel)

        
	#on empty search field, list everything, else show searching
	if(main_window.lineEdit.text() == '' or main_window.lineEdit.text() == '*'):
	  reply = QtGui.QMessageBox.warning(main_window,"Search question","Search for everthing?  This is slow.",QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
	  if(reply == QtGui.QMessageBox.Yes):
	    viewmodel.appendRow(QtGui.QStandardItem(""))
	    viewmodel.setHeaderData(0, QtCore.Qt.Horizontal, "Searching everything...")
	    viewmodel.removeRows(0,1)
	    main_window.lineEdit.setText('*')	
	  elif(reply == QtGui.QMessageBox.No):
	    viewmodel.clear()
	    main_window.pushButton.setEnabled(True)
	    main_window.lineEdit.setEnabled(True)
	    continuesearch = False
	    haveSearchResults = False
	else:
	  viewmodel.appendRow(QtGui.QStandardItem(""))
	  viewmodel.setHeaderData(0, QtCore.Qt.Horizontal, "Searching....")
	  viewmodel.removeRows(0,1) 
	  
	if(continuesearch):
	  main_window.treeView.setModel(proxymodel)
	  main_window.treeView.setEnabled(False)
	  main_window.show()
	  searchThreadVar = threading.Thread(target=searchThread, args=(""))
	  searchAnimCount = 0
	  searchTimer.start(200)
	  app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
	  searchThreadVar.start()

def searchThread():
	global haveSearchResults
	global searchIsDone
	global viewmodel
	global searchThreadPid
	haveSearchResults = False
	try:
	  args = shlex.split("/usr/bin/locate "+str(main_window.lineEdit.text()))
	  searchprocess = subprocess.Popen(args,stdout = subprocess.PIPE, stderr= subprocess.PIPE)
	  searchThreadPid = searchprocess.pid
	  output = searchprocess.communicate()
	  #print searchThreadPid
	  output2 = output[0].split("\n")
	  if(output2 == ['']):
	    haveSearchResults = False
	  else:
	    haveSearchResults = True
	    viewmodel.appendRow(QtGui.QStandardItem(""))
	    viewmodel.setHeaderData(0, QtCore.Qt.Horizontal, "Creating list:") #QObject::connect: Cannot queue arguments of type 'Qt::Orientation' (Make sure 'Qt::Orientation' is registered using qRegisterMetaType()
	    viewmodel.removeRows(0,1)
	    for item in output2:
	      	itempath = QtGui.QStandardItem(item)
		if not itempath.text()=='':
		 path = itempath.text()
		 moddate = str(modif_date(path))
		 itemdate = QtGui.QStandardItem(moddate)
		 itemsizecount = file_size(path)
		 itemsize = QtGui.QStandardItem(str(itemsizecount))
		 rowlist = ([itempath,itemdate,itemsize])
		 viewmodel.appendRow(rowlist)
	except Exception as e: 
	  viewmodel.appendRow(QtGui.QStandardItem("searchThread Error"))
	  raise
	pass
	searchIsDone = True
    
def searchAnimation():
  #print "searchAnimation stub"
  global searchTimer
  global searchAnimCount
  global haveSearchResults
  #print "searchAnimCount "+str(searchAnimCount)
  if(searchIsDone == True):
    searchTimer.stop()
    if not(haveSearchResults):
      viewmodel.clear()  
      viewmodel.appendRow(QtGui.QStandardItem(""))
      viewmodel.setHeaderData(0, QtCore.Qt.Horizontal, "No results.") 
      viewmodel.removeRows(0,1)
    else:
      if(viewmodel.rowCount() == 1):
	  headerstring = str(viewmodel.rowCount())+" result-Path"
      else:
	  headerstring = str(viewmodel.rowCount())+" results-Path"
	  viewmodel.setHeaderData(0, QtCore.Qt.Horizontal, headerstring)
	  viewmodel.setHeaderData(1, QtCore.Qt.Horizontal, "Date")
	  viewmodel.setHeaderData(2, QtCore.Qt.Horizontal, "Size in MB")
    #scroll back and forth to cache it all, speeds up scrolling later
    #app.sendPostedEvents()
    
    #scrolling doesn't do anything at all, broken?
    #rc = viewmodel.rowCount()
    #qmi1 = viewmodel.indexFromItem(viewmodel.item(0,rc-1))
    ##qmi2 = viewmodel.indexFromItem(viewmodel.item(0,0))
    #main_window.treeView.scrollTo(qmi1,0)
    #main_window.treeView.scrollTo(qmi2)
    searchAnimCount =  0

    app.restoreOverrideCursor()
    main_window.treeView.setEnabled(True)
    main_window.pushButton.setEnabled(True)
    main_window.lineEdit.setEnabled(True)
    #main_window.pushButton2.setEnabled(False)
	
def updateCommand():
    global notify_on_updatedb_complete
    global updateIsDone
    returncode = subprocess.call(shlex.split(sucommand+" /usr/bin/updatedb"))
    updateIsDone = True  
    #print "supportsMessages="+str(tray_icon.supportsMessages())
    if(notify_on_updatedb_complete):
      tray_icon.showMessage("Locate32","Database update completed.",1)
  
def updateDB():
	global updateTimer
	global updateAnimCount
	global updatingProcess
	updatingProcess = threading.Thread(target=updateCommand, args=(""))
	updateAnimCount = 0
	tray_icon.setToolTip("Locate32 - Updating...")	
	updateTimer.start(100)
	updatingProcess.start()

def stopUpdateDB():
  global updateTimer
  global updateIsDone
  global UpdateAction
  global StopUpdateAction
  global updatingProcess
  returncode = subprocess.call(shlex.split(sucommand+" \"/usr/bin/killall -q updatedb\""))  
  UpdateAction.setEnabled(True)
  StopUpdateAction.setEnabled(False)	
  updateIsDone = False
  updatingProcess.join()
  updateTimer.stop()
  restoreTrayIcon()

  
def restoreTrayIcon():
  global LocateIcon
  tray_icon.setToolTip("Locate32")	
  LocateIcon = QtGui.QIcon("icons/locate32.png") #main icon
  tray_icon.setIcon(LocateIcon)  
  tray_icon.show()


def showSettingScreen():
  settings_window.show()
  #print "showSettingScreen stub" 
  
def showAbout():
  QtGui.QMessageBox.information(main_window,"About","Locate32 (http://locate32.cogit.net/) lookalike for Linux, by zaggynl")
  
def exitProperly():
  #print "exitProperly stub" 
  sys.exit(0)

def updateAnimation():
	global updateAnimCount
	global LocateIcon
	global tray_icon
	global updatingProcess
	global updateTimer
	global updateIsDone
	global UpdateAction
	global StopUpdateAction
	UpdateAction.setEnabled(False)
	StopUpdateAction.setEnabled(True)
	if(updateIsDone == False):
	  #print "updateIsDone ="+ str(updateIsDone)
	  #print str(updatingProcess)
	  #print "updateAnimCount="+str(updateAnimCount)
	  
	  if updateAnimCount == 0:
	    LocateIcon = QtGui.QIcon("icons/uanim1.png")
	  elif updateAnimCount == 1:
	    LocateIcon = QtGui.QIcon("icons/uanim2.png")
	  elif updateAnimCount == 2:
	    LocateIcon = QtGui.QIcon("icons/uanim3.png")	 
	  
	  elif updateAnimCount == 3:
	    LocateIcon = QtGui.QIcon("icons/uanim4.png")	 
	  
	  elif updateAnimCount == 4:
	    LocateIcon = QtGui.QIcon("icons/uanim5.png")	 
	  
	  elif updateAnimCount == 5:
	    LocateIcon = QtGui.QIcon("icons/uanim6.png")	 
	  
	  elif updateAnimCount == 6:
	    LocateIcon = QtGui.QIcon("icons/uanim7.png")	 
	  
	  elif updateAnimCount == 7:
	    LocateIcon = QtGui.QIcon("icons/uanim8.png")	 
	  
	  elif updateAnimCount == 8:
	    LocateIcon = QtGui.QIcon("icons/uanim9.png")	 
	  
	  elif updateAnimCount == 9:
	    LocateIcon = QtGui.QIcon("icons/uanim10.png")	 
	  
	  elif updateAnimCount == 10:
	    LocateIcon = QtGui.QIcon("icons/uanim11.png")	 
	  
	  elif updateAnimCount == 11:
	    LocateIcon = QtGui.QIcon("icons/uanim12.png")	 
	  
	  elif updateAnimCount == 12:
	    LocateIcon = QtGui.QIcon("icons/uanim13.png")	 
	    updateAnimCount = -1
	    
	  tray_icon.setIcon(LocateIcon)  
	  tray_icon.show()
	  updateAnimCount = updateAnimCount +1
	else:
	  updateTimer.stop()
	  restoreTrayIcon()
	  StopUpdateAction.setEnabled(False)
	  UpdateAction.setEnabled(True)	  

if __name__ == "__main__":
	#check if running under linux, else exit
	if(os.name is not 'posix'):
	    exit("This version of Locate32 is for Linux, for Windows try: http://locate32.cogit.net/ (different developer)")

	#check if we have kdesudo or gksu, else exit
	global sucommand
	sucommand = ''
	if (os.path.isfile("/usr/bin/kdesudo")):
	  sucommand = "/usr/bin/kdesudo -c"
	
	if (os.path.isfile("/usr/bin/gksu")):
	  sucommand = "/usr/bin/gksu"
	  
	if (sucommand == ''):
	  exit("Please install kdesudo or gksu, is required for starting/stopping locate database update.")
	
	iconspath = str(os.path.realpath(__file__))
	iconspath = os.path.dirname(iconspath)
	iconspath = iconspath +"/icons"
	if not (os.path.isdir(iconspath)):
	  exit("icons folder missing, forgot to copy icons folder?")
	  
	global tray_icon
	global minimize_on_exit
	global notify_on_updatedb_complete
	minimize_on_exit = True
	notify_on_updatedb_complete = True
		
	# Someone is launching this directly
	# Create the QApplication
	app = QtGui.QApplication(sys.argv)
	
	#What the updateTimer does when it fires
	app.connect(updateTimer,QtCore.SIGNAL("timeout()"),updateAnimation)
	app.connect(searchTimer,QtCore.SIGNAL("timeout()"),searchAnimation)
			
	#The Main window
	main_window = MainWindow()
	main_window.show()
	
	#tray icon
	tray_icon = TrayIcon()
	tray_icon.show()
	
	#settings window
	settings_window = SettingsWindow()
	
	#show/hide on tray icon click, double click won't work, always registers single click
	def tray_icon_event(reason):
	  if reason == QtGui.QSystemTrayIcon.Trigger:
	    if(main_window.isHidden()):
	      main_window.show()
	    else:
	      main_window.hide()
	
	tray_icon.activated.connect(tray_icon_event)
	
	#from http://stackoverflow.com/a/21330349
	#set app icon    
	app_icon = QtGui.QIcon()
	#app_icon.addFile('gui/icons/16x16.png', QtCore.QSize(16,16))
	#app_icon.addFile('gui/icons/24x24.png', QtCore.QSize(24,24))
	#app_icon.addFile('gui/icons/32x32.png', QtCore.QSize(32,32))
	app_icon.addFile('icons/locate32.png', QtCore.QSize(48,48))
	#app_icon.addFile('gui/icons/256x256.png', QtCore.QSize(256,256))
	app.setWindowIcon(app_icon)
		  
	# Enter the main loop
	app.exec_()