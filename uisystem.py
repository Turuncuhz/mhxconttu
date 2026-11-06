# -*- coding: cp1254 -*-
import net
import app
import ui
import uiOption
import uiGameOption
import uiScriptLocale
import networkModule
import pysettings
import chr
import player
import constInfo
import chat
import localeInfo
if app.ENABLE_NEW_GAMEOPTION:
	import uiGameOptionNew
###################################################################################################
## System
class SystemDialog(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__Initialize()

	def __Initialize(self):
		self.gameOptionDlg = None
		self.wndInterface = None

	def BindInterface(self, wInterface):
		self.wndInterface = wInterface

	def LoadDialog(self):
		self.__LoadSystemMenu_Default()
		if app.ENABLE_NEW_GAMEOPTION:
			if self.gameOptionDlg == None:
				self.gameOptionDlg = uiGameOptionNew.GameOptionWindow()

	def __LoadSystemMenu_Default(self):
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(self, "uiscript/systemdialog.py")

		self.GetChild("game_option_button").SAFE_SetEvent(self.__ClickGameOptionButton)
		mobileBtn = self.GetChild2("mobile_option_button")
		if mobileBtn:
			mobileBtn.SAFE_SetEvent(self.__ClickMobileOptionButton)
		self.GetChild("change_button").SAFE_SetEvent(self.__ClickChangeCharacterButton)
		self.GetChild("logout_button").SAFE_SetEvent(self.__ClickLogOutButton)
		self.GetChild("exit_button").SAFE_SetEvent(self.__ClickExitButton)
		self.GetChild("move_channel_button").SAFE_SetEvent(self.__ClickMoveChannelButton)
		self.GetChild("cancel_button").SAFE_SetEvent(self.Close)

		self.GetChild("mall_button").SAFE_SetEvent(self.__ClickInGameShopButton)

	def Destroy(self):
		self.ClearDictionary()

		if self.gameOptionDlg:
			self.gameOptionDlg.Destroy()

		self.__Initialize()

	def OpenDialog(self):
		self.Show()

	def __ClickChangeCharacterButton(self):
		self.Close()

		net.ExitGame()

	def __OnClosePopupDialog(self):
		self.popup = None

	def __ClickLogOutButton(self):
		self.Close()
		net.LogOutGame()


	def __ClickExitButton(self):
		if chr.IsGameMaster(player.GetMainCharacterIndex()):
			app.Exit()
		else:
			import uiCommon
			questionDialogExit=uiCommon.QuestionDialog()
			questionDialogExit.SetText(localeInfo.EXIT_BUTTON_DIALOG)
			questionDialogExit.Open()
			questionDialogExit.SetAcceptEvent(lambda arg=True: app.Exit())
			questionDialogExit.SetCancelEvent(lambda arg=False: self.questionDialogExit.Close())
			self.Close()
			self.questionDialogExit=questionDialogExit
			return

	def __ClickMobileOptionButton(self):
		self.Close()
		if not self.gameOptionDlg:
			if app.ENABLE_NEW_GAMEOPTION:
				self.gameOptionDlg = uiGameOptionNew.GameOptionWindow()
			else:
				self.gameOptionDlg = uiGameOption.OptionDialog()
		if hasattr(self.gameOptionDlg, "OpenMobileTab"):
			self.gameOptionDlg.OpenMobileTab()
		else:
			self.gameOptionDlg.Show()

	def __ClickGameOptionButton(self):
		self.Close()

		if not self.gameOptionDlg:
			if app.ENABLE_NEW_GAMEOPTION:
				self.gameOptionDlg = uiGameOptionNew.GameOptionWindow()
			else:
				self.gameOptionDlg = uiGameOption.OptionDialog()

		self.gameOptionDlg.Show()


	def __ClickMoveChannelButton(self):
		self.Close()
		self.changewnd = MoveChannelDialog()
		self.changewnd.Open()

	def __ClickInGameShopButton(self):
		self.Close()
		if app.ENABLE_DRAGON_COIN_SHOP_SYSTEM:
			self.wndInterface.ItemShopSendOpen()

	def Close(self):
		self.Hide()
		return True

	def RefreshMobile(self):
		if self.gameOptionDlg:
			self.gameOptionDlg.RefreshMobile()
		#self.optionDialog.RefreshMobile()

	def OnMobileAuthority(self):
		if self.gameOptionDlg:
			self.gameOptionDlg.OnMobileAuthority()
		#self.optionDialog.OnMobileAuthority()

	def OnBlockMode(self, mode):
		uiGameOption.blockMode = mode
		if self.gameOptionDlg:
			self.gameOptionDlg.OnBlockMode(mode)
		#self.optionDialog.OnBlockMode(mode)

	def OnChangePKMode(self):
		if self.gameOptionDlg:
			self.gameOptionDlg.OnChangePKMode()
		#self.optionDialog.OnChangePKMode()

	def OnPressExitKey(self):
		self.Close()
		return True

	def OnPressEscapeKey(self):
		self.Close()
		return True

class MoveChannelDialog(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.sch = 0
		self._MoveChannelDialog__LoadDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def _MoveChannelDialog__LoadDialog(self):
		self.dialog = ui.BoardWithTitleBar()
		self.dialog.AddFlag("movable")
		self.dialog.AddFlag("float")
		self.dialog.SetTitleName("Kanal Secimi")
		self.dialog.SetCloseEvent(self.Close)
		x = 0
		y = 0 
		self.button_list = []
		
		for ch in xrange(10):
			channel_button = ui.Select()
			channel_button.SetParent(self.dialog) 
			channel_button.SetSize(100, 100)
			channel_button.SetPosition(11, 33 + (25 * x + x))
			channel_button.SetUpVisual("d:/ymir work/ui/channel_button/3.tga")
			channel_button.SetOverVisual("d:/ymir work/ui/channel_button/2.tga")
			channel_button.SetDownVisual("d:/ymir work/ui/channel_button/1.tga")
			channel_button.SetToggleDownEvent(ui.__mem_func__(self._MoveChannelDialog__SelectChannel), (ch + 1))
			channel_button.SetText("Kanal: %s" % str(ch + 1))
			channel_button.Show()
			self.button_list.append(channel_button)
			x += 1
			if x == 10:
				for bt in xrange(2):
					buttons = ui.Button()
					buttons.SetParent(self.dialog) 
					buttons.SetSize(100, 100)
					buttons.SetPosition(15 + (y * 85) , 40+(25 * x + x))
					
					if y == 1:
						buttons.SetEvent(ui.__mem_func__(self.Close))
						buttons.SetUpVisual("d:/ymir work/ui/channel_button/public/canclebutton00.sub")
						buttons.SetOverVisual("d:/ymir work/ui/channel_button/public/canclebutton01.sub")
						buttons.SetDownVisual("d:/ymir work/ui/channel_button/public/canclebutton02.sub")
					elif y == 0:
						buttons.SetEvent(ui.__mem_func__(self.AcceptButton))
						buttons.SetUpVisual("d:/ymir work/ui/channel_button/public/acceptbutton00.sub")
						buttons.SetOverVisual("d:/ymir work/ui/channel_button/public/acceptbutton01.sub")
						buttons.SetDownVisual("d:/ymir work/ui/channel_button/public/acceptbutton02.sub")
					buttons.Show()
					self.button_list.append(buttons)
					y += 1

		self.dialog.SetSize(177, 90 + 10 +20 + (20 * x + x)) 
		self.dialog.SetCenterPosition()
		self._MoveChannelDialog__SelectChannel(pysettings.ch)

	def Open(self):
		self.dialog.Show()
		# Cynex: ESC gosterilen karta gider, ScriptWindow'a degil
		if getattr(app, "IsMobile", None):
			self.dialog.OnPressEscapeKey = ui.__mem_func__(self.OnPressEscapeKey)

	def Close(self):
		self.dialog.Hide()
		return True

	def AcceptButton(self):
		self.Close()
		net.SendChatPacket("/channel %d" % self.sch)

	def _MoveChannelDialog__SelectChannel(self, button):
		self.sch = button
		try:
			selButton = self.button_list[button-1]
		except IndexError:
			return

		for eachButton in self.button_list:
			eachButton.SetUp()

		selButton.Down()

	def OnPressExitKey(self):
		self.Close()
		return True

	def OnPressEscapeKey(self):
		self.Close()
		return True

if __name__ == "__main__":

	import app
	import wndMgr
	import systemSetting
	import mouseModule
	import grp
	import ui
	import chr
	import background
	import player

	#wndMgr.SetOutlineFlag(True)

	app.SetMouseHandler(mouseModule.mouseController)
	app.SetHairColorEnable(True)
	wndMgr.SetMouseHandler(mouseModule.mouseController)
	wndMgr.SetScreenSize(systemSetting.GetWidth(), systemSetting.GetHeight())
	app.Create("METIN2 CLOSED BETA", systemSetting.GetWidth(), systemSetting.GetHeight(), 1)
	mouseModule.mouseController.Create()


	wnd = SystemDialog()
	wnd.LoadDialog()
	wnd.Show()

	app.Loop()

