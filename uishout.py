import ui
import chat
import net
import constInfo
from _weakref import proxy
from itertools import islice
import app

class ShoutManager(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.board = None
		self.LoadWindow()

	def __del__(self):
		self.Destroy()
		ui.ScriptWindow.__del__(self)

	def LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "uiscript/shout.py")
		except:
			import exception
			exception.Abort("DiceClass.LoadDialog.LoadScript")

		try:
			GetObject=self.GetChild
			self.board = GetObject("board")
			self.baslat = GetObject("baslat")
			self.durdur = GetObject("durdur")
			self.temizle = GetObject("temizle")
			self.bilgi = GetObject("bilgi")
			self.yazi = GetObject("CommentValue")
			try:
				self.yazibar = GetObject("yazibar")
				self.yazibar.SetEvent(ui.__mem_func__(self.FocusEdit))
			except:
				pass

			self.baslat.SetEvent(ui.__mem_func__(self.Baslat))
			self.durdur.SetEvent(ui.__mem_func__(self.Durdur))
			self.temizle.SetEvent(ui.__mem_func__(self.Temizle))

			self.board.SetCloseEvent(ui.__mem_func__(self.__OnCloseButtonClick))

		except:
			import exception
			exception.Abort("DiceClass.LoadDialog.BindObject")

	def Destroy(self):
		self.ClearDictionary()
		self.titleBar = None

	def FocusEdit(self):
		if self.yazi:
			self.yazi.SetFocus()
			import ime
			ime.EnableCaptureInput()
			if hasattr(app, "ShowKeyboard"):
				app.ShowKeyboard(1)

	def Open(self):
		if constInfo.auto_shout_status == 1:
			self.bilgi.SetText("|cffffffff|H|h Göndermek istediðiniz mesajý yazýnýz..." + "|cff00ff00|H|h (Durum: Aktif)")
		else:
			self.bilgi.SetText("|cffffffff|H|h Göndermek istediðiniz mesajý yazýnýz..." + "|cffFDD017|H|h (Durum: Deaktif)")

		self.Show()
		self.SetCenterPosition()

	def OnUpdate(self):
		if constInfo.auto_shout_status == 1:
			self.bilgi.SetText("|cffffffff|H|h Göndermek istediðiniz mesajý yazýnýz..." + "|cff00ff00|H|h (Durum: Aktif)")
		else:
			self.bilgi.SetText("|cffffffff|H|h Göndermek istediðiniz mesajý yazýnýz..." + "|cffFDD017|H|h (Durum: Deaktif)")

	def Temizle(self):
		self.yazi.SetText("")

	def Baslat(self):
		text = self.yazi.GetText()
		if (len(text) < 1):
			chat.AppendChat(1, "Baðýracak bir kaç kelime yazýnýz!")
			return

		if '/' == text[0]: # Komut Engeli
			chat.AppendChat(1, "Bunu yapamazsýnýz!")
			return

		constInfo.auto_shout_text = text
		constInfo.auto_shout_status = 1

	def Durdur(self):
		constInfo.auto_shout_text = ""
		constInfo.auto_shout_status = 0

	def Close(self):
		self.Hide()

	def __OnCloseButtonClick(self):
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
