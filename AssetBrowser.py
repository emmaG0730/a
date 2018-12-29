from PySide import QtCore
from PySide import QtUiTools
from PySide import QtGui
from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import maya.OpenMaya as om 
import json
import maya.cmds as mc
import os

CHARACTER_PATH = 'R:\JX4_SourceData\Animation\Rigs\\'
ANIM_FOLDER_PATH = 'R:\JX4_SourceData\Animation\Characters\\'
PROP_PATH = 'R:\JX4_SourceData\Graphics\Characters\Props\\'
			
def get_maya_file_name(file_path):
	dir_list = []	
	file_list = []
	for dir_path, dir_name, filenames in os.walk(file_path):
		dir_list.append(dir_path)
		if len(filenames) > 0:
			file_list.append(filenames) 
	return dir_list, file_list

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
		self.setFixedWidth(940)
		self.setFixedHeight(770)
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
		self.ui.character_list_widget.addItems(get_maya_file_name(CHARACTER_PATH)[1][0])
		self.ui.character_list_widget.itemDoubleClicked.connect(self.import_corresponding_file)	
		self.ui.character_list_widget.itemClicked.connect(self.get_current_item)	
		
		self.ui.prop_list_widget.addItems(get_maya_file_name(PROP_PATH)[1][0])
		self.ui.prop_list_widget.itemDoubleClicked.connect(self.import_corresponding_file)					
		self.ui.prop_list_widget.itemClicked.connect(self.get_current_item)
		
		self.ui.character_filter_text.textChanged.connect(self.filter_character)
		self.ui.prop_filter_text.textChanged.connect(self.filter_prop)
		self.ui.anim_filter_text.textChanged.connect(self.filter_animation)
		
		self.ui.weapon_type_list_widget.itemClicked.connect(self.get_current_item)
		
		self.ui.ok_btn_char_tab.clicked.connect(self.load_file)	
		self.ui.ok_btn_anim_tab.clicked.connect(self.get_anim_folder_item)					
		self.ui.cancel_btn_char_tab.clicked.connect(self.print_test)	
		self.ui.cancal_btn_anim_tab.clicked.connect(self.concatenate_anim_path)

		self.ui.body_type_MA_rb.toggled.connect(self.add_current_items)
		self.ui.body_type_FA_rb.toggled.connect(self.add_current_items)
		self.ui.body_type_CH_rb.toggled.connect(self.add_current_items)
		
		self.ui.motion_movement_rb.toggled.connect(self.add_current_items)
		self.ui.motion_interaction_rb.toggled.connect(self.add_current_items)
		self.ui.motion_attack_rb.toggled.connect(self.add_current_items)
				
		self.ui.player_cb.currentIndexChanged.connect(self.add_current_items)		
		
		for each in self.get_character_names():
			self.ui.character_name_list_widget.clear()
			self.ui.character_name_list_widget.addItem(each)			
		self.ui.character_name_list_widget	.setCurrentRow(0)
		self.ui.character_name_list_widget.itemClicked.connect(self.get_current_item)
		
		for each in self.get_anim_folder_items():			
			self.ui.animation_folder_list_widget.addItem(each)		
		self.ui.animation_folder_list_widget.setCurrentRow(0)
		self.ui.animation_folder_list_widget.itemClicked.connect(self.get_anim_folder_item)
				
		for each in self.concatenate_anim_path():
			self.ui.anim_list_widget.addItem(each)
		self.ui.animation_folder_list_widget.setCurrentRow(0)
		self.ui.animation_folder_list_widget.itemDoubleClicked.connect(self.import_corresponding_file)
	
	def add_current_items(self):
		self.ui.character_name_list_widget.clear()		
		for each in self.get_character_names():
			self.ui.character_name_list_widget.addItem(each)			
		self.ui.character_name_list_widget.setCurrentRow(0)
		
	def print_test(self):
		self.get_character_names()			
		
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
		print 'current_item : ' + self.CURRENT_ITEM
		return self.CURRENT_ITEM

	def get_MA_rb_text(self):
		self.CURRENT_BODY_TYPE = 'MaleAdult_maya'
		return self.CURRENT_BODY_TYPE
		
	def get_FA_rb_text(self):
		self.CURRENT_BODY_TYPE = 'FemaleAdult'
		print self.CURRENT_BODY_TYPE + ' : in get_FA_rb_text()'
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
		print 'player_cb : ' + str(self.CURRENT_CHARACTER_TYPE)
		return self.CURRENT_CHARACTER_TYPE

	def get_rb_cb_text(self):				
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
		print 'CURRENT_ANIM_PATH : ' + str(self.CURRENT_ANIM_PATH)
		return self.CURRENT_ANIM_PATH		
	
	def get_character_names(self):
		self.get_rb_cb_text()
		print 'CURRENT_ANIM_PATH : \n' +  str(self.CURRENT_ANIM_PATH) + '\n'
		path_list = get_maya_file_name(self.CURRENT_ANIM_PATH)[0]
		character_name_list = []
		for path in path_list:
			dummy_ = path.split('\\')
			while '' in dummy_:
				dummy_.remove('')
			if len(dummy_) == 8:
				character_name_list.append(QtGui.QListWidgetItem(dummy_[-1]))
		print character_name_list
		return character_name_list

	def get_anim_folder_items(self):
		temp_anim_path = self.CURRENT_ANIM_PATH + self.CURRENT_ITEM
		temp_path_list = get_maya_file_name(temp_anim_path)		
		anim_folder_paths = temp_path_list[0][2:]
		anim_folder_path = []
		for each in anim_folder_paths:			
			anim_name_folder = each.split('\\')[-1]
			if '.' not in anim_name_folder:
				anim_folder_path.append(anim_name_folder)
		print 'folders : ' + str(anim_folder_path)
		return anim_folder_path
				
	def get_character_name(self, item):
		self.CURRENT_CHARACTER_NAME = item.text()
		print 'CURRENT_CHARACTER_NAME : ' + str(self.CURRENT_CHARACTER_NAME)
		return self.CURRENT_CHARACTER_NAME
		
	def get_anim_folder_item(self, item):
		self.CURRENT_ANIM_FOLDER = item.text()
		print 'CURRENT_ANIM_FOLDER : ' + str(self.CURRENT_ANIM_FOLDER)
		return self.CURRENT_ANIM_FOLDER
	
	def	 concatenate_anim_path(self):
		self.get_rb_cb_text()
		full_path = self.CURRENT_ANIM_PATH + self.CURRENT_CHARACTER_NAME + '\\' + self.CURRENT_ANIM_FOLDER
		print 'full_path : ' + str(full_path)
		temp_anim_files = get_maya_file_name(full_path)[1][0]
		print 'temp_anim_files : ' + str(temp_anim_files)
		return temp_anim_files
		
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
		if self.ui.open_rb.isChecked():			
			self.open_corresponding_file()
			
		elif self.ui.import_rb.isChecked():
			self.import_corresponding_file()
			
		elif self.ui.reference_rb.isChecked():
			self.reference_corresponding_file()
			
	def import_corresponding_file(self):
		mc.file(CHARACTER_PATH + str(self.CURRENT_ITEM), i = True)		
				
	def open_corresponding_file(self):
		if mc.file(q = True,modified = True):
			result = QtGui.QMessageBox.question(self,'Modified','Current scene has unsaved changes.Continue?',															QtGui.QMessageBox.StandardButton.Yes, QtGui.QMessageBox.StandardButton.No)
			if result == QtGui.QMessageBox.StandardButton.Yes:
				mc.file(new=True, force=True) 
			elif result == QtGui.QMessageBox.StandardButton.No:
				mc.file(new=True, force=False) 			
		mc.file(CHARACTER_PATH + str(self.CURRENT_ITEM), o = True)				
		
	def reference_corresponding_file(self):
		mc.file(CHARACTER_PATH + str(self.CURRENT_ITEM), r = True)		
		
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
	
		

































































































