from PySide import QtCore
from PySide import QtUiTools
from PySide import QtGui
from shiboken import wrapInstance

import maya.OpenMayaUI as omui
import json
import maya.cmds as mc
import os

CHARACTER_PATH = 'R:\JX4_SourceData\Animation\Rigs\\'
ANIM_PATH = 'G:\JX4\depot\JX4_SourceData\Animation\Characters\MaleAdult_maya\Expression'


def get_maya_file_name(file_path):
	for dir_path, dir_name, filenames in os.walk(file_path):
		if len(filenames) > 0:			
		 	return filenames
		else:
		 	print 'Empty Directory!'


def maya_main_window():
		main_window_pointer = omui.MQtUtil.mainWindow()
		return wrapInstance(long(main_window_pointer),QtGui.QWidget)

class AssetBrowser(QtGui.QDialog):
	
	def __init__(self, parent = maya_main_window()):
		super(AssetBrowser, self).__init__(parent)
		
		self.setWindowTitle('AssetBrowser')
		self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)		
		self.setFixedWidth(600)
		self.setFixedHeight(600)
		self.init_ui()	
		self.create_layouts()
		self.create_connection()
		
	def init_ui(self):
		f = QtCore.QFile('F:\\GitHub\\AssetBrowser\\AssetBrowserUI.ui')
		f.open(QtCore.QFile.ReadOnly)
		
		loader = QtUiTools.QUiLoader()
		self.ui = loader.load(f, parentWidget = None)
		
		f.close()
		
	def create_layouts(self):
		main_layout = QtGui.QVBoxLayout(self)
		main_layout.setContentsMargins(0, 0, 0, 0)
		main_layout.addWidget(self.ui) 

		
	def create_connection(self):
		self.ui.character_list_widget.addItems(get_maya_file_name(CHARACTER_PATH))
		self.ui.character_list_widget.itemDoubleClicked.connect(self.import_corresponding_file)
		
		self.ui.character_list_widget.itemClicked.connect(self.excute_file)
		
		self.ui.anim_list_widget.addItems(get_maya_file_name(ANIM_PATH))
		self.ui.character_list_widget.itemDoubleClicked.connect(self.import_corresponding_file)
			
		self.ui.cancel_btn_char_tab.clicked.connect(self.close)
		
	def excute_file(self):
		if self.ui.open_rb.toggled == True:
			self.ui.ok_btn_char_tab.clicked.connect(self.open_corresponding_file) 
			
		elif self.ui.import_rb.toggled == True:
			self.ui.ok_btn_char_tab.clicked.connect(self.import_corresponding_file)
			
		elif self.ui.reference_rb.toggled == True:
			self.ui.ok_btn_char_tab.clicked.connect(self.reference_corresponding_file)
			
	def import_corresponding_file(self, item):	
		mc.file(CHARACTER_PATH + str(item.text()), i = True)		
		print 'improted file is : {0}'.format(item.text())
		
	def open_corresponding_file(self, item):
		mc.file(CHARACTER_PATH + str(item.text()), o = True)		
		print 'opened file is : {0}'.format(item.text())
		
	def reference_corresponding_file(self, item):
		mc.file(CHARACTER_PATH + str(item.text()), r = True)		
		print 'referenced file is : {0}'.format(item.text())
		
		

if __name__ ==  '__main__':	
	try:
		asset_browser_dialog.close()
		asset_browser_dialog.deleteLater()
	except:
		pass
		
	asset_browser_dialog = AssetBrowser()
	asset_browser_dialog.show()
		

































































































