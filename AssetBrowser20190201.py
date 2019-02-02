from PySide import QtCore
from PySide import QtUiTools
from PySide import QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import maya.OpenMaya as om 
import json
import maya.cmds as mc
import os

import subprocess

CHARACTER_PATH = 'R:\JX4_SourceData\Animation\Rigs\\'
ANIM_FOLDER_PATH = 'R:\JX4_SourceData\Animation\Characters\\'
PROP_PATH = 'R:\JX4_SourceData\Graphics\Characters\Props\lantern\\'
			
def get_maya_folders(file_path):
	dir_list = []	
	for dir_path, dir_name, filenames in os.walk(file_path):
		dir_list.append(dir_path)		
	return dir_list

def get_maya_files(file_path):
	file_list = []
	for dir_path, dir_name, filenames in os.walk(file_path):
		if len(filenames) > 0:
			file_list.append(filenames) 
	return file_list

def maya_main_window():
		main_window_pointer = omui.MQtUtil.mainWindow()
		return wrapInstance(long(main_window_pointer),QtGui.QWidget)
		
class AssetBrowser(QtGui.QDialog):	
	CURRENT_ITEM = ''	
	FILTER_TEXT = ''	
	CURRENT_BODY_TYPE = ''
	CURRENT_MOTION_NAME = ''
	CURRENT_CHARACTER_TYPE = ''
	CURRENT_CHARACTER_NAME = ''
	CURRENT_ANIM_FOLDER = ''
	CURRENT_ANIM_PATH = ''
	DEFAULT = True
	browser_instance = None	
	'''
	@classmethod
	def show_dialog(cls):
		if not cls.browser_instance:
			cls.browser_instance = AssetBrowser()
		if cls.browser_instance.isHidden():			
			cls.browser_instance.show()
		else:
			cls.browser_instance.raise_()
			cls.browser_instance.activateWindow()
	'''
		
	def __init__(self, parent = maya_main_window()):
		super(AssetBrowser, self).__init__(parent)
		
		self.setWindowTitle('AssetBrowser')
		self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)		
		#self.setFixedWidth(940)
		#self.setFixedHeight(770)
		self.init_ui()	
		self.create_layouts()
		self.create_connection()

	def init_ui(self):
		f = QtCore.QFile('F:\\GitHub\\AssetBrowser\\AssetBrowserUI2.ui')
		f.open(QtCore.QFile.ReadOnly)		
		loader = QtUiTools.QUiLoader()
		self.ui = loader.load(f, parentWidget = None)	
		f.close()
		
	def create_layouts(self):
		main_layout = QtGui.QVBoxLayout(self)
		main_layout.setContentsMargins(0, 0, 0, 0)
		main_layout.addWidget(self.ui) 
		
		
	def create_connection(self):
		'''
		connect signals
		'''
		self.ui.character_list_widget.addItems(get_maya_files(CHARACTER_PATH)[0])
		self.ui.character_list_widget.itemDoubleClicked.connect(self.import_corresponding_file)	
		self.ui.character_list_widget.itemClicked.connect(self.get_current_item)	
		
		self.ui.prop_list_widget.addItems(get_maya_files(PROP_PATH)[0])
		self.ui.prop_list_widget.itemDoubleClicked.connect(self.import_corresponding_file)					
		self.ui.prop_list_widget.itemClicked.connect(self.get_current_item)
		
		self.ui.character_filter_text.textChanged.connect(self.filter_character)
		self.ui.prop_filter_text.textChanged.connect(self.filter_prop)
		self.ui.anim_filter_text.textChanged.connect(self.filter_animation)
		
		self.ui.weapon_type_list_widget.itemClicked.connect(self.get_current_item)
		
		self.ui.ok_btn_char_tab.clicked.connect(self.load_file)	
		self.ui.ok_btn_anim_tab.clicked.connect(self.load_file)					
		self.ui.cancel_btn_char_tab.clicked.connect(self.close)	
		self.ui.cancal_btn_anim_tab.clicked.connect(self.close)

		self.ui.body_type_MA_rb.toggled.connect(self.add_current_items)
		self.ui.body_type_FA_rb.toggled.connect(self.add_current_items)
		self.ui.body_type_CH_rb.toggled.connect(self.add_current_items)
		
		self.ui.motion_movement_rb.toggled.connect(self.add_current_items)
		self.ui.motion_interaction_rb.toggled.connect(self.add_current_items)
		self.ui.motion_attack_rb.toggled.connect(self.add_current_items)
				
		self.ui.player_cb.currentIndexChanged.connect(self.add_current_items)		
		
		for each in self.get_character_names():
			self.ui.character_name_list_widget.clear()
			self.ui.character_name_list_widget.addItem(QtGui.QListWidgetItem(each))		
		self.ui.character_name_list_widget	.setCurrentRow(0)
		self.ui.character_name_list_widget.itemClicked.connect(self.switch_character_name)
		
		for each in self.get_anim_folder_items():			
			self.ui.animation_folder_list_widget.addItem(QtGui.QListWidgetItem(each))		
		self.ui.animation_folder_list_widget.setCurrentRow(0)
		self.ui.animation_folder_list_widget.itemClicked.connect(self.switch_anim_folder_item)
				
		for each in self.load_default_anims():
			self.ui.anim_list_widget.addItem(each)
		self.ui.anim_list_widget.setCurrentRow(0)
		self.ui.anim_list_widget.itemDoubleClicked.connect(self.import_corresponding_file)
	
	def add_current_items(self):
		self.ui.character_name_list_widget.clear()
		self.ui.animation_folder_list_widget.clear()
		self.ui.anim_list_widget.clear()
				
		for char in self.get_character_names():
			if char != None:
			 self.ui.character_name_list_widget.addItem(char)			
		self.ui.character_name_list_widget.setCurrentRow(0)
		
		for folder in self.get_anim_folder_items():
			if folder != None:
			 self.ui.animation_folder_list_widget.addItem(folder)			
		self.ui.animation_folder_list_widget.setCurrentRow(0)

		try:
			for anim in self.load_default_anims():
				self.ui.anim_list_widget.addItem(anim)			
		except:
			pass
		self.ui.anim_list_widget.setCurrentRow(0)
		
	def print_test(self):
		print 'CURRENT_ANIM_FOLDER : ' + str(self.CURRENT_ANIM_FOLDER)			
		
	def get_default_body_type(self):
		if 	self.ui.body_type_MA_rb.isChecked():
			self.CURRENT_BODY_TYPE = self.ui.body_type_MA_rb.text() + '_maya'
		return self.CURRENT_BODY_TYPE
			
	def get_default_motion_type(self):
		if 	self.ui.motion_movement_rb.isChecked():
			self.CURRENT_MOTION_NAME = self.ui.motion_movement_rb.text()
		return self.CURRENT_MOTION_NAME
		
	def get_default_character_type(self):
		self.CURRENT_CHARACTER_TYPE = self.ui.player_cb.currentText()
		return self.CURRENT_CHARACTER_TYPE
			
	def get_current_item(self,item):
		self.CURRENT_ITEM = item.text()		
		return self.CURRENT_ITEM

	def get_MA_rb_text(self):
		self.CURRENT_BODY_TYPE = 'MaleAdult_maya'
		return self.CURRENT_BODY_TYPE
		
	def get_FA_rb_text(self):
		self.CURRENT_BODY_TYPE = 'FemaleAdult'
		return self.CURRENT_BODY_TYPE
		
	def get_CH_rb_text(self):
		self.CURRENT_BODY_TYPE = 'MaleChild'
		return self.CURRENT_BODY_TYPE
			
	def get_movement_rb_text(self):
		self.CURRENT_MOTION_NAME = 'Movement'
		return self.CURRENT_MOTION_NAME
		
	def get_interaction_rb_text(self):
		self.CURRENT_MOTION_NAME = 'Interaction'
		return self.CURRENT_MOTION_NAME
		
	def get_attack_rb_text(self):
		self.CURRENT_MOTION_NAME = 'Attack'
		return self.CURRENT_MOTION_NAME
		
	def get_character_cb_type(self):
		self.CURRENT_CHARACTER_TYPE = self.ui.player_cb.currentText()
		return self.CURRENT_CHARACTER_TYPE
		
	def list_spliter(self, file_list, item_num):
		'''
		split string in list by list length to decide which item to add on list widget 
		'''		
		splited_list = file_list.split('\\')
		while '' in splited_list:
			splited_list.remove('')
		if len(splited_list) == item_num:
			last_file = splited_list[-1]
			return last_file

	def get_rb_cb_text(self):
		'''
		get base animation path from body type , motion type and character type
		'''			
		if self.DEFAULT:
			self.get_default_body_type()
			self.get_default_motion_type()
			self.get_default_character_type()
		else:
			self.get_character_cb_type()						
			if self.ui.body_type_MA_rb.isChecked():
				self.get_MA_rb_text()
			elif self.ui.body_type_FA_rb.isChecked():				
				self.get_FA_rb_text()
				
			elif self.ui.body_type_CH_rb.isChecked():
				self.get_CH_rb_text()				
			if 	self.ui.motion_movement_rb.isChecked():				
				self.get_movement_rb_text()				
			elif self.ui.motion_interaction_rb.isChecked():				
				self.get_interaction_rb_text()				
			elif self.ui.motion_attack_rb.isChecked():	
				self.get_attack_rb_text()			
		self.CURRENT_ANIM_PATH = (ANIM_FOLDER_PATH +'{0}'+'\\'+'{1}'+'\\'+'{2}'+'\\').format(
					self.CURRENT_BODY_TYPE,self.CURRENT_MOTION_NAME ,self.CURRENT_CHARACTER_TYPE + '_temp')					
		self.DEFAULT = False				
		return self.CURRENT_ANIM_PATH		
		
	def get_character_names(self):
		'''
		load default character names onto "character_name_list_widget"
		'''
		self.get_rb_cb_text()
		path_lists = get_maya_folders(self.CURRENT_ANIM_PATH)
		character_name_list = []
		for path in path_lists:
			char_name = self.list_spliter(path, 8)
			if char_name != None:
				character_name_list.append(char_name)				
		return character_name_list

	def get_anim_folder_items(self):
		'''
		load default animation folders onto "animation_folder_list_widget"
		'''
		self.get_rb_cb_text()
		print 'self.get_character_names() : ' + str(self.get_character_names())
		if len(self.get_character_names()) > 0 :
			character_name = self.get_character_names()[0]
		else:
			character_name = ''
		temp_anim_path = self.CURRENT_ANIM_PATH + character_name
		temp_path_list = get_maya_folders(temp_anim_path)	
		anim_folder_path = []
		for each in temp_path_list:
			temp_anim_folder = self.list_spliter(each, 9)
			if temp_anim_folder != None:		
				anim_folder_path.append(temp_anim_folder)
		return anim_folder_path
			
	def load_default_anims(self):
		'''
		load default animations onto "anim_list_widget"
		'''
		self.get_rb_cb_text()	
		default_full_path = self.CURRENT_ANIM_PATH + self.CURRENT_CHARACTER_NAME + '\\' + self.CURRENT_ANIM_FOLDER
		temp_anim_files = get_maya_files(default_full_path)
		if len(temp_anim_files) > 0:
			return temp_anim_files[0]
			
	def	 get_anims(self, full_path):		
		temp_anim_files = get_maya_files(full_path)
		self.ui.anim_list_widget.clear()
		if len(temp_anim_files) > 0:
			for anim in temp_anim_files[0]:
				self.ui.anim_list_widget.addItem(anim)

		
								
	def switch_character_name(self, item):
		'''
		load animations when switching character names constently  
		'''
		self.get_rb_cb_text()	
		self.CURRENT_CHARACTER_NAME = item.text()
		folders = get_maya_folders(self.CURRENT_ANIM_PATH	+ self.CURRENT_CHARACTER_NAME)
		self.ui.animation_folder_list_widget.clear()
		for folder in folders:
			character_item = self.list_spliter(folder, 9)
			if character_item != None:
				self.ui.animation_folder_list_widget.addItem(QtGui.QListWidgetItem(character_item))
		self.ui.animation_folder_list_widget.setCurrentRow(0)
		
		folder_name = self.ui.animation_folder_list_widget.currentItem().text()
		full_path = self.CURRENT_ANIM_PATH	 + self.CURRENT_CHARACTER_NAME + '\\' + folder_name
		self.get_anims(full_path)
				
	def switch_anim_folder_item(self, item):
		'''
		load animations when switching animations folders constently  
		'''
		self.get_rb_cb_text()  
		character_name = self.ui.character_name_list_widget.currentItem().text()
		self.CURRENT_ANIM_FOLDER = item.text()
		full_path = self.CURRENT_ANIM_PATH + character_name + '\\' + self.CURRENT_ANIM_FOLDER
		self.get_anims(full_path)

	def filter_character(self, name):
		'''
		This function if for filter files to match input string  
		'''
		temp_filter_list = []
		file_list = get_maya_file_name(CHARACTER_PATH)[1][0]
		for each_file in file_list:
			if name.lower() in each_file.lower():
				temp_filter_list.append(each_file)
				self.ui.character_list_widget.clear()
				self.ui.character_list_widget.addItems(temp_filter_list)	
		
	def filter_prop(self, name):
		'''
		This function if for filter files to match input string  
		'''
		temp_filter_list = []
		file_list = get_maya_file_name(PROP_PATH)[1][0]
		for each_file in file_list:
			if name.lower() in each_file.lower():
				temp_filter_list.append(each_file)
				self.ui.prop_list_widget.clear()
				self.ui.prop_list_widget.addItems(temp_filter_list)
				
	def filter_animation(self, name):
		'''
		This function if for filter files to match input string  
		'''
		temp_filter_list = []
		file_list = get_maya_file_name(self.CURRENT_ANIM_PATH)[1][0]
		for each_file in file_list:
			if name.lower() in each_file.lower():
				temp_filter_list.append(each_file)
				self.ui.anim_list_widget.clear()
				self.ui.anim_list_widget.addItems(temp_filter_list)
						
	def load_file(self):		
		if self.ui.open_rb.isChecked() or self.ui.anim_open_rb.isChecked():			
			self.open_corresponding_file()				
		elif self.ui.import_rb.isChecked() or self.ui.anim_import_rb.isChecked():
			self.import_corresponding_file()				
		elif self.ui.reference_rb.isChecked() or self.ui.anim_reference_rb.isChecked():
			self.reference_corresponding_file()
				

	def get_loadfile_path(self):
		self.get_rb_cb_text()  
		tab_index = self.ui.asset_tab_widget.currentIndex()
		if tab_index == 0:			
			#if character list widget is actived ,load character; if prop listwidget is actived ,load props
			if 'prop' in self.CURRENT_ITEM.lower():
				file_name = self.ui.prop_list_widget.currentItem().text()
				file_path = PROP_PATH + file_name
			else:
				file_name = self.ui.character_list_widget.currentItem().text()
				file_path = CHARACTER_PATH + file_name
			
		elif tab_index == 1:
			character_name = self.ui.character_name_list_widget.currentItem().text()
			anim_folder_name = self.ui.animation_folder_list_widget.currentItem().text()
			file_name = self.ui.anim_list_widget.currentItem().text()
			file_path = self.CURRENT_ANIM_PATH + character_name + '\\' + anim_folder_name + '\\' + file_name
			
		file_namespace = file_name.split('.')[0]
		return file_path, file_namespace

	def import_corresponding_file(self):
		path = self.get_loadfile_path()
		file_path = path[0]
		file_namespace =  path[1]
		mc.file(file_path ,i = True, type = "mayaAscii", ignoreVersion = True, ra = True, 
					mergeNamespacesOnClash = False, namespace = file_namespace, options = "v=0;",pr = True)
					
	def reference_corresponding_file(self):
		path = self.get_loadfile_path()
		file_path = path[0]
		file_namespace =  path[1]
		print file_path
		print file_namespace
		mc.file(file_path ,r = True, type = "mayaAscii", ignoreVersion = True, gl = True, 
					mergeNamespacesOnClash = False, namespace = file_namespace, options = "v=0;")
		
	def open_corresponding_file(self):		
		path = self.get_loadfile_path()
		file_path = path[0]
		file_namespace =  path[1]			
		if mc.file(q = True,modified = True):
			result = QtGui.QMessageBox.question(self,'Modified',
			'Save changes to ' + str(file_path) + '?',QtGui.QMessageBox.StandardButton.Yes, QtGui.QMessageBox.StandardButton.No)
			print 'result : ' + str(result)
			if result == QtGui.QMessageBox.StandardButton.Yes:
				mc.file(new = True, force = False)
				mc.file(save = True)
			elif result == QtGui.QMessageBox.StandardButton.No:
				mc.file(new = True, force = True) 	

		mc.file(file_path ,o = True, type = "mayaAscii", ignoreVersion = True, options = "v=0;")
		
		
	#right click 	
	#-------------------
	def contextMenuEvent(self, event):
		context_menu = QtGui.QMenu(self)
		context_menu.addAction((QtGui.QAction("New", self,triggered = self.test)))
		context_menu.addAction('Import')
		context_menu.addAction('Reference')
		context_menu.addAction((QtGui.QAction('Show in explorer', self,triggered = self.oepn_source_manager)))		
		context_menu.exec_(self.mapToGlobal(event.pos()))
		
	def test(self):
		print 'test'
		
	def oepn_source_manager(self):
		path = self.get_loadfile_path()
		slash = '\\'
		new_path = slash.join(path[0].split('\\')[:-1])		
		subprocess.call("explorer " + new_path , shell = True)
	#-------------------
		
	def switch_file(self, item):
		current_item  = self.get_current_item(item)
		anim_file_path = ANIM_FOLDER_PATH + current_item
		get_maya_file_name(anim_file_path)
		anim_list_widget.addItem()
		
if __name__ ==  '__main__':	
	try:
		asset_browser_dialog.close()
		asset_browser_dialog.deleteLater()
	except:
		pass
		
	asset_browser_dialog = AssetBrowser()
	asset_browser_dialog.show()
	
		

































































































