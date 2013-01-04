from gi.repository import Gtk, GdkPixbuf, Gdk
import os, math, datetime

from aboutbox import aboutBoxShow

class TuxFit:
	def __init__(self):
		self.foodarray = {}

		if not os.path.exists(os.path.expanduser('~/.config/tuxfit')):
			print 'test'
    			os.makedirs(os.path.expanduser('~/.config/tuxfit'))

		self.builder = Gtk.Builder()
		filename = os.path.join('', 'tuxfit.glade')        

		self.builder.add_from_file(filename)
		self.builder.connect_signals(self)
		self.window = self.builder.get_object('win-main')
		self.window.set_default_size(1000, 650)
		self.window.set_title('TuxFit')
		self.window.set_icon_from_file('muscle.png')
		self.window.connect('destroy', self.quit_activate)
		self.window.show_all()

		#Menus
		self.menu = self.builder.get_object('popupmenu')

		self.foodremoveBtn = self.builder.get_object('foodremoveBtn')
		self.foodremoveBtn.connect('activate', self.remove_rows)

		self.menuabt = self.builder.get_object('menu-about')
		self.menuabt.connect('activate', self.about_activate)

		self.menuaqt = self.builder.get_object('menu-quit')
		self.menuaqt.connect('activate', self.quit_activate)

		self.menu_new = self.builder.get_object('menu-new')
		self.menu_new.connect('activate', self.clear_foodView)

		self.menusave = self.builder.get_object('save-menu-item')
		self.menusave.connect('activate', self.save_days_data)

		self.menuopen = self.builder.get_object('open-menu-item')
		self.menuopen.connect('activate', self.open_days_data)

		self.menuview = self.builder.get_object('menu-toggle')
		self.menuview.connect('toggled', self.view_activate)

		self.menutools = self.builder.get_object('menu-tools')
		self.menutools.connect('toggled', self.tools_activate)

		#TreeViews + Models
		self.searchmodel = self.builder.get_object('SearchBox')

		self.searchview = self.builder.get_object('treeview1')
		self.searchview.connect('row-activated', self.on_activated)
		self.searchview.connect('focus-out-event', lambda x,y: 	self.contextPopup.hide())
		self.searchview.connect('focus-in-event', self.searchViewChanged)

		self.olddataModel = self.builder.get_object('viewoldmodel')

		self.foodModel = self.builder.get_object('liststore1')
		self.foodView = self.builder.get_object('treeview2')
		self.foodView.connect('button-press-event', self.treeview_right_click)

		self.treeSelect = self.builder.get_object('treeview-selection3')		
		self.treeSelect.connect('changed', self.searchViewChanged)

		self.treeSelect2 = self.builder.get_object('treeview-selection2')		
		self.treeSelect2.set_mode(Gtk.SelectionMode.MULTIPLE)

		#Total Labels
		self.totalCalLabel = self.builder.get_object('label11')
		self.totalProtLabel = self.builder.get_object('label10')
		self.totalCarbLabel = self.builder.get_object('label9')
		self.totalFatLabel = self.builder.get_object('label8')

		#Preview Labels
		self.nameLabelPreview = self.builder.get_object('nameLabelPreview')
		self.calLabelPreview = self.builder.get_object('calLabelPreview')
		self.protLabelPreview = self.builder.get_object('protLabelPreview')
		self.carbLabelPreview = self.builder.get_object('carbLabelPreview')
		self.fatLabelPreview = self.builder.get_object('fatLabelPreview')

		#AddFood Text Entrys
		self.nameEntry = self.builder.get_object('entry2')
		self.calEntry = self.builder.get_object('entry3')
		self.protEntry = self.builder.get_object('entry4')
		self.carbEntry = self.builder.get_object('entry5')
		self.fatEntry = self.builder.get_object('entry6')
		self.boozeEntry = self.builder.get_object('entry7')
		
		#searchfield
		self.searchEntry = self.builder.get_object('searchEntry')
		self.searchEntry.connect('changed', self.searchfunc)

		#NoteBook Items
		self.notebook = self.builder.get_object('notebook2')

		self.addfoodBtn = self.builder.get_object('addfoodBtn')
		self.addfoodBtn.connect('clicked', lambda x: self.notebook.set_current_page(1))

		self.addFoodCancel = self.builder.get_object('addFoodCancel')
		self.addFoodCancel.connect('clicked', self.add_food_cancel)

		self.addFoodSave = self.builder.get_object('addFoodSave')
		self.addFoodSave.connect('clicked', self.add_food)

		self.contextPopup = self.builder.get_object('vbox1')

		self.closeoldBtn = self.builder.get_object('closeoldBtn')
		self.closeoldBtn.connect('clicked', self.back_to_main)

		self.rmvfoodBtn = self.builder.get_object('rmvfoodBtn')
		self.rmvfoodBtn.connect('clicked', self.rmv_food_list_item)

		self.calcBmiBtn = self.builder.get_object('bmiBtn')
		self.calcBmiBtn.connect('clicked', self.calculate_bmi)

		#Data Import#
		self.import_foodnames()
		self.import_foodtable()
		self.update_totals()

	def remove_rows(self, widget=None, shittyargs=None):
		row = self.treeSelect2.get_selected_rows()[1]
		for i in reversed(row):
			#print i
			print self.foodModel
			tempiter = self.foodModel.get_iter(i)
			self.foodModel.remove(tempiter)
		self.update_totals()

	def searchViewChanged(self, widget=None, shittyargs=None):
		row = self.treeSelect.get_selected()[1]
		self.nameLabelPreview.set_text(self.foodarray[self.searchmodel[row][0]][0])
		self.calLabelPreview.set_text(self.foodarray[self.searchmodel[row][0]][1])
		self.protLabelPreview.set_text(self.foodarray[self.searchmodel[row][0]][2])
		self.carbLabelPreview.set_text(self.foodarray[self.searchmodel[row][0]][3])
		self.fatLabelPreview.set_text(self.foodarray[self.searchmodel[row][0]][4])
		#self.notebook.set_current_page(2)
		self.contextPopup.show()

	def add_food_cancel(self, widget=None):
		self.clear_foodentry()
		self.notebook.set_current_page(0)

	def searchfunc(self, widget):
		tempArray = []
		for i in self.foodarray:
			if self.searchEntry.get_text().lower() in i.lower():
				tempArray.append(i)
		#print tempArray
		self.searchmodel.clear()
		for i in sorted(tempArray):
			self.searchmodel.append([i])

	def about_activate(self, action):
		aboutBoxShow(self.window)

	def quit_activate(self, action):
		print 'kthxbai'
		self.save_foodModel()
        	Gtk.main_quit()

	def view_activate(self, action):
		box = self.builder.get_object('box7')
		if box.get_property('visible') == True: 
			box.hide()
		else:
			box.show()

	def tools_activate(self, action):
		box = self.builder.get_object('notebook1')
		if box.get_property('visible') == True: 
			box.hide()
		else:
			box.show()

	def save_foodModel(self, widget=None):
		f = open(os.path.expanduser('~/.config/tuxfit/current'), 'w')
		for a in range(0,len(self.foodModel)):
			for b in range(0,self.foodModel.get_n_columns()):
				tempIter = self.foodModel.get_iter(a)
				result = self.foodModel.get_value(tempIter,b)
				#print result
				f.write(result)
				f.write('\n')
		f.close()

	def import_foodnames(self):
		try: f = open(os.path.expanduser('~/.config/tuxfit/fday'), 'r')
		except: return
		num_lines = sum(1 for line in f)

		f = open(os.path.expanduser('~/.config/tuxfit/fday'), 'r')
		for i in range(0, num_lines/6):
			line = f.readline().replace('\n', '')
			self.searchmodel.append([line])
			self.foodarray[line] = line, f.readline().replace('\n', ''), f.readline().replace('\n', ''), f.readline().replace('\n', ''), f.readline().replace('\n', ''), f.readline().replace('\n', '')
		f.close()

	def import_foodtable(self):
		try: f = open(os.path.expanduser('~/.config/tuxfit/current'), 'r')
		except: return
		num_lines = sum(1 for line in f)
		f = open(os.path.expanduser('~/.config/tuxfit/current'), 'r')
		for i in range(0, num_lines/6):
			self.foodModel.append([f.readline().replace('\n', ''), f.readline().replace('\n', ''), f.readline().replace('\n', ''), f.readline().replace('\n', ''), f.readline().replace('\n', ''), f.readline().replace('\n', '')])
		f.close()

	def update_totals(self, widget=None):
		totalCal = 0
		totalProt = 0
		totalCarb = 0
		totalFat = 0
		for i in range(0,len(self.foodModel)):
			tempIter = self.foodModel.get_iter(i)
			totalCal = totalCal + float(self.foodModel.get_value(tempIter, 1))
			totalProt = totalProt + float(self.foodModel.get_value(tempIter, 2))
			totalCarb = totalCarb + float(self.foodModel.get_value(tempIter, 3))
			totalFat = totalFat + float(self.foodModel.get_value(tempIter, 4))
		self.totalCalLabel.set_label('Calories: ' + str(totalCal))

		if totalProt != 0:
			totalProt = ((totalProt*4)/totalCal)*100
			self.totalProtLabel.set_label('Protein: ' + str(math.ceil(totalProt)) + '%')
		else:
			self.totalProtLabel.set_label('Protein: ')

		if totalCarb != 0:
			totalCarb = ((totalCarb*4)/totalCal)*100
			self.totalCarbLabel.set_label('Carbs: ' + str(math.ceil(totalCarb)) + '%')
		else:
			self.totalCarbLabel.set_label('Carbs: ')

		if totalFat != 0:
			totalFat = ((totalFat*9)/totalCal)*100
			self.totalFatLabel.set_label('Fat: ' + str(math.ceil(totalFat)) + '%')
		else:
			self.totalFatLabel.set_label('Fat: ')

	def add_food(self, widget=None):
		f = open(os.path.expanduser('~/.config/tuxfit/fday'), 'a')
		if self.nameEntry.get_text() == '' or self.calEntry.get_text() == '' or self.protEntry.get_text() == '' or self.carbEntry.get_text() == '' or self.fatEntry.get_text() == '':
			md = Gtk.MessageDialog(self.window, 
			    0, Gtk.MessageType.ERROR, 
			    Gtk.ButtonsType.CLOSE, "Error loading file")
			md.run()
			md.destroy()
			return
		if self.nameEntry.get_text() != '':
			f.write(self.nameEntry.get_text() + '\n')
		if self.calEntry.get_text() != '':
			f.write(self.calEntry.get_text() + '\n')
		if self.protEntry.get_text() != '':
			f.write(self.protEntry.get_text() + '\n')
		if self.carbEntry.get_text() != '':
			f.write(self.carbEntry.get_text() + '\n')
		if self.fatEntry.get_text() != '':
			f.write(self.fatEntry.get_text() + '\n')
		if self.boozeEntry.get_text() != '':
			f.write(self.boozeEntry.get_text() + '\n')
		else:
			self.boozeEntry.set_text('0')
			f.write('0\n')
		f.close()

		self.foodarray[self.nameEntry.get_text()] = self.nameEntry.get_text(), self.calEntry.get_text(), self.protEntry.get_text(), self.carbEntry.get_text(), self.fatEntry.get_text(), self.boozeEntry.get_text()
		self.searchmodel.append([self.nameEntry.get_text()])

		self.notebook.set_current_page(0)
		self.clear_foodentry()

	def clear_foodentry(self, widget=None):
		self.nameEntry.set_text('')
		self.calEntry.set_text('')
		self.protEntry.set_text('')
		self.carbEntry.set_text('')
		self.fatEntry.set_text('')
		self.boozeEntry.set_text('')

	def on_activated(self, widget, row, col):
		self.foodModel.append(self.foodarray[self.searchmodel[row][0]])
		self.update_totals()

	def clear_foodView(self, widget=None):
		self.foodModel.clear()

	def treeview_right_click(self, treeview, event):
		if event.button == 3:
			x = int(event.x)
			y = int(event.y)
			time = event.time
			self.menu.popup( None, None, None, None, event.button, time)
			return True

	def save_days_data(self, widget=None):
		self.dialog = Gtk.FileChooserDialog("Save Data..",
                               None,
                               Gtk.FileChooserAction.SAVE,
                               (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
		self.dialog.set_default_response(Gtk.ResponseType.OK)
		now = datetime.datetime.now()
       		self.dialog.set_current_name(str(now.day) + '-' + str(now.month) + '-' + str(now.year) + '.tfd')
		response = self.dialog.run()
		if response == Gtk.ResponseType.OK:
			answer = -5
			selectedfile = self.dialog.get_filename()
			if os.path.isdir(selectedfile) == False and os.path.exists(selectedfile):
				#print 'oh shit dawg, theres files in your filepaths!'
				md = Gtk.MessageDialog(self.dialog, 
				    0, Gtk.MessageType.QUESTION, 
				    Gtk.ButtonsType.CANCEL, "OverWrite Existing File?")
				md.add_button('Ok', Gtk.ResponseType.OK)
				answer = md.run()
				#print answer
				md.destroy()		
			if answer == -5 :
				f = open(selectedfile, 'w')
				f.write('TuxFit\n')
				f.write(str(now.day) + '/' + str(now.month) + '/' + str(now.year) + '\n')
				for a in range(0,len(self.foodModel)):
					for b in range(0,self.foodModel.get_n_columns()):
						tempIter = self.foodModel.get_iter(a)
						result = self.foodModel.get_value(tempIter,b)
						#print result
						f.write(result)
						f.write('\n')
				f.close()
		self.dialog.destroy()

	def open_days_data(self, widget=None):
		self.dateLbl = self.builder.get_object('dateLbl')
		self.dialog = Gtk.FileChooserDialog("Open Data..",
                               None,
                               Gtk.FileChooserAction.SAVE,
                               (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
		self.dialog.set_default_response(Gtk.ResponseType.OK)
		response = self.dialog.run()
		if response == Gtk.ResponseType.OK:
			f = open(self.dialog.get_filename(), 'r')
			if f.readline() == 'TuxFit\n':				
				num_lines = sum(1 for line in f)
				f = open(self.dialog.get_filename(), 'r')
				f.readline()
				self.dateLbl.set_text(f.readline())
				for i in range(0, num_lines/6):
					self.olddataModel.append([f.readline().replace('\n', ''), f.readline().replace('\n', ''), f.readline().replace('\n', ''), f.readline().replace('\n', ''), f.readline().replace('\n', ''), f.readline().replace('\n', '')])
				f.close()
				box = self.builder.get_object('box7')
				box.hide()
				box3 = self.builder.get_object('box3')
				box3.hide()
				menubar1 = self.builder.get_object('menubar1')
				menubar1.hide()
				self.notebook.set_current_page(2)
			else:
				md = Gtk.MessageDialog(self.dialog, 
				    0, Gtk.MessageType.ERROR, 
				    Gtk.ButtonsType.OK, "Not a Valid TuxFit File")
				answer = md.run()
				md.destroy()
		self.dialog.destroy()

	def back_to_main(self, widget=None):
		self.olddataModel.clear()
		box = self.builder.get_object('box7')
		box.show()
		box3 = self.builder.get_object('box3')
		box3.show()
		menubar1 = self.builder.get_object('menubar1')
		menubar1.show()
		self.notebook.set_current_page(0)

	def rmv_food_list_item(self, widget=None):
		row = self.treeSelect.get_selected()[1]
		#print self.foodarray[self.searchmodel[row][0]]
		del self.foodarray[self.searchmodel[row][0]]
		try: print self.foodarray[self.searchmodel[row][0]]
		except: self.searchmodel.remove(row)
		f = open(os.path.expanduser('~/.config/tuxfit/fday'), 'w')
		for foodname in sorted(self.foodarray):
			tempArray = self.foodarray[foodname]
			for i in tempArray:
				f.write(i + '\n')#print i
		f.close()


	def calculate_bmi(self, widget=None):
		WeightBox = self.builder.get_object('entry1')
		HeightBox = self.builder.get_object('entry8')
		BMILbl = self.builder.get_object('label15')

		x = float(WeightBox.get_text()) * 703
		y = float(HeightBox.get_text()) * float(HeightBox.get_text())
		BMILbl.set_text('BMI = ' + str(x/y))

def main():
	app = TuxFit()
	if __name__ == '__main__':
		Gtk.main()

main()
