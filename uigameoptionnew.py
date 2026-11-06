# -*- coding: cp1254 -*-
import ui, constInfo, uiSelectMusic, musicInfo, localeInfo, uiScriptLocale,pysettings
import dbg, player, chat, wndMgr, net, systemSetting, snd, pack, app, background
import ikashop

MUSIC_FILENAME_MAX_LEN = 25
blockMode = 0
IMG_DIR = "d:/ymir work/ui/game/gameoption/"

class OptionContentWindow(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.isTouchDragging = False
		self.touchStartY = 0
		self.touchStartPos = 0.0
		self.scrollLen = 0

	def OnMouseLeftButtonDown(self):
		if getattr(self, "scrollBar", None) and self.scrollBar.IsShow():
			self.isTouchDragging = True
			self.touchStartY = wndMgr.GetMousePosition()[1]
			self.touchStartPos = self.scrollBar.GetPos()
		return True

	def OnMouseLeftButtonUp(self):
		self.isTouchDragging = False
		return True

	def OnUpdate(self):
		ui.ScriptWindow.OnUpdate(self)
		if getattr(self, "isTouchDragging", False):
			if not wndMgr.IsLButtonDown():
				self.isTouchDragging = False
				return
			scrollBar = getattr(self, "scrollBar", None)
			if scrollBar and scrollBar.IsShow() and getattr(self, "scrollLen", 0) > 0:
				currentY = wndMgr.GetMousePosition()[1]
				dy = currentY - self.touchStartY
				newPos = max(0.0, min(1.0, self.touchStartPos - float(dy) / float(self.scrollLen)))
				scrollBar.SetPos(newPos)

class GameOptionWindow(ui.BoardWithTitleBar):
	def __del__(self):
		ui.BoardWithTitleBar.__del__(self)

	def Destroy(self):
		self.ctrlFovValue = None
		self.pvpModeButtonDict={}
		self.blockButtonList=[]
		self.questLetterButtonList=[]
		self.viewChatButtonList = []
		self.nameColorModeButtonList = []
		self.viewTargetBoardButtonList=[]
		self.alwaysShowNameButtonList=[]
		self.parlamaButtonList=[]
		self.showDamageButtonList=[]
		self.showsalesTextButtonList=[]
		self.cameraModeButtonList=[]
		self.fogModeButtonList = []
		self.AutoPickUpButtonList = []
		self.AutoPickUpButtonList1 = []
		self.AutoPickUpButtonList2 = []
		self.MadaraModelShow = []
		self.YangdropButtonList = []
		self.DogeModeButtonList = []
		self.fpsBoostBtnList = []

		self.affectIconsButtonList=[]
		self.nightModeButtonList=[]
		if app.ENABLE_DISCORD_STUFF:
			self.wndNotificationButtonList=[]
		if app.__BL_HIDE_EFFECT__:
			self.BLEffectGroupList = []
		if app.ENABLE_EFFECT_SCALE:
			self.changeEffectScale = None

		if app.WJ_SHOW_MOB_INFO:
			self.showMobInfoButtonList = []

		self.ctrlSoundVolume = None
		self.ctrlMusicVolume = None
		self.selectMusicFile = None
		self.musicListDlg = None

		for j in xrange(10):
			for x in xrange(10):
				if self.children.has_key("optionWindow%d%d"%(j,x)):
					window = self.children["optionWindow%d%d"%(j,x)]
					if window:
						window.Hide()
						window.scrollBar = None
						window.ClearDictionary()
						window.Destroy()
		self.children = {}
		self.Hide()

	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		self.children = {}
		self.Destroy()
		self.__LoadWindow()
		self.SetTitleName(uiScriptLocale.GAMEOPTION_TITLE)
		self.SetCloseEvent(self.Close)

	def __LoadWindow(self):
		self.AddFlag("movable")
		self.AddFlag("attach")
		option_data = {
			"Oyun Ayarlar":{
				"index": 0,
				"Genel":{"index": 0,},
				"Mobil Ayarlar":{"index": 1,},
			},
			"Grnt Ayarlar":{
			"index": 1,
				"Genel":{"index": 0,},
				"Arayz":{"index": 1,},
				"Performans":{"index": 2,},
			},
			"Ses Ayarlar":{
				"index": 2,
				"General":{"index": 0,},
			},
		}

		for key, optionTitles in option_data.items():
			if self.IsCanContinue(key):
				continue

			if not optionTitles.has_key("index"):
				continue
			optionIndex = optionTitles["index"]

			bg = ui.ImageBox()
			bg.SetParent(self)
			bg.AddFlag("attach")
			bg.SetPosition(8,65)
			bg.LoadImage(IMG_DIR+"bg.tga")
			bg.Show()
			self.children["bg%d"%optionIndex] = bg

			titleButton = ui.RadioButton()
			titleButton.SetParent(self)
			if optionIndex == 0:
				titleButton.SetUpVisual(IMG_DIR+"first_title_0.tga")
				titleButton.SetOverVisual(IMG_DIR+"first_title_1.tga")
				titleButton.SetDownVisual(IMG_DIR+"first_title_2.tga")
				titleButton.SetPosition(21+(optionIndex*(titleButton.GetWidth()+5)), 40)
			elif optionIndex == len(option_data)-1:
				titleButton.SetUpVisual(IMG_DIR+"end_title_0.tga")
				titleButton.SetOverVisual(IMG_DIR+"end_title_1.tga")
				titleButton.SetDownVisual(IMG_DIR+"end_title_2.tga")
				titleButton.SetPosition(21+(optionIndex*(titleButton.GetWidth()+5))-5, 40)
			else:
				titleButton.SetUpVisual(IMG_DIR+"middle_title_0.tga")
				titleButton.SetOverVisual(IMG_DIR+"middle_title_1.tga")
				titleButton.SetDownVisual(IMG_DIR+"middle_title_2.tga")
				titleButton.SetPosition(21+(optionIndex*(titleButton.GetWidth()+5)), 40)
			titleButton.SetText(key)
			titleButton.SAFE_SetEvent(self.SetOptionType, optionIndex)
			titleButton.Show()
			self.children["titleBtn%d"%optionIndex] = titleButton

			for keyEx, optionTypes in optionTitles.items():
				if self.IsCanContinue(keyEx):
					continue
				if not optionTypes.has_key("index"):
					continue

				categoryIndex = optionTypes["index"]
				optionCategory = ui.RadioButton()
				optionCategory.SetParent(bg)
				optionCategory.SetUpVisual(IMG_DIR+"category_0.tga")
				optionCategory.SetOverVisual(IMG_DIR+"category_1.tga")
				optionCategory.SetDownVisual(IMG_DIR+"category_2.tga")
				optionCategory.SetPosition(7, 10+(categoryIndex*(optionCategory.GetHeight()+5)))
				optionCategory.SAFE_SetEvent(self.SetCategoryType, categoryIndex)
				optionCategory.SetText(keyEx)
				optionCategory.Show()
				self.children["optionCategory%d%d"%(optionIndex,categoryIndex)] = optionCategory

				optionWindow = self.CreateOptionWindow(bg, optionIndex,categoryIndex)
				self.children["optionWindow%d%d"%(optionIndex,categoryIndex)] = optionWindow

		self.SetOptionType(0)
		self.SetSize(8+bg.GetWidth()+10,65+bg.GetHeight()+10)
		self.SetCenterPosition()
		self.UpdateScrollBar()
	def Open(self):
		self.RefreshBlock()
		self.Show()
	def Close(self):
		systemSetting.SaveConfig()
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True
	def __ClickRadioButton(self, buttonList, buttonIndex):
		try:
			btn=buttonList[buttonIndex]
		except IndexError:
			return
		for eachButton in buttonList:
			eachButton.SetUp()
		btn.Down()

	def IsCanContinue(self, dictKey):
		if dictKey == "index":
			return True
		return False

	def SetOptionType(self, optionType):
		self.children["optionType"] = optionType
		for j in xrange(10):
			if self.children.has_key("titleBtn%d"%j):
				titleBtn = self.children["titleBtn%d"%j]
				if j == optionType:
					titleBtn.Down()
				else:
					titleBtn.SetUp()
			if self.children.has_key("bg%d"%j):
				bg = self.children["bg%d"%j]
				if j == optionType:
					bg.Show()
				else:
					bg.Hide()
		self.SetCategoryType(0)

	def SetCategoryType(self, categoryType):
		for j in xrange(3):
			for x in xrange(5):
				if self.children.has_key("optionWindow%d%d" % (j,x)):
					self.children["optionWindow%d%d"%(j,x)].Hide()

		self.children["categoryType"] = categoryType
		currentCategoryType = self.children["optionType"]
		for j in xrange(10):
			if self.children.has_key("optionCategory%d%d"%(currentCategoryType,j)):
				categoryBtn = self.children["optionCategory%d%d"%(currentCategoryType,j)]
				if j == categoryType:
					categoryBtn.Down()
				else:
					categoryBtn.SetUp()

		if self.children.has_key("optionWindow%d%d" % (currentCategoryType,categoryType)):
			self.children["optionWindow%d%d"%(currentCategoryType,categoryType)].Show()

		self.UpdateScrollBar()

	def CreateOptionWindow(self, windowBG, optionIndex, categoryIndex):
		scriptWindow = OptionContentWindow()
		scriptWindow.SetParent(windowBG)

		if optionIndex == 0 and categoryIndex == 1:
			self.__BuildMobileCategory(scriptWindow)
		else:
			fileName = "UIScript/game_option_%d_%d.py"%(optionIndex, categoryIndex)
			pyScrLoader = ui.PythonScriptLoader()
			if pack.Exist(fileName):
				pyScrLoader.LoadScriptFile(scriptWindow, fileName)
				self.LoadCatetoryOptions(scriptWindow, optionIndex, categoryIndex)
			else:
				dbg.TraceError("[GameOption]Can't find script window for optionIndex: %d categoryIndex: %d"%(optionIndex, categoryIndex))

		if scriptWindow.GetWidth() > 0:
		#Auto add scrollbar
			scrollBar = ScrollBarNew()
			scrollBar.SetParent(scriptWindow)
			scrollBar.SetPosition(scriptWindow.GetWidth()-scrollBar.GetWidth(),0)
			scrollBar.SetScrollBarSize(scriptWindow.GetHeight()-5)
			scrollBar.Hide()
			scrollBar.SetScrollEvent(ui.__mem_func__(self.UpdateScrollBar))
			scriptWindow.scrollBar = scrollBar
			scriptWindow.OnRunMouseWheel = ui.__mem_func__(self.OnRunMouseWheel)

			scriptChildrens = scriptWindow.Children
			for child in scriptChildrens:
				(_x,_y) = child.GetLocalPosition()
				child.SetPosition(_x,_y, False,True)

			scriptWindow.Show()
		else:
			scriptWindow.scrollBar = None

		return scriptWindow

	def LoadCatetoryOptions(self, scriptWindow, optionIndex, categoryIndex):
		#try:
		GetObject = scriptWindow.GetChild

		if optionIndex == 0:#Game-Options

			if categoryIndex == 0:#General
				self.pvpModeButtonDict[player.PK_MODE_PEACE] = GetObject("pvp_peace")
				self.pvpModeButtonDict[player.PK_MODE_PEACE].SAFE_SetEvent(self.__OnClickPvPModePeaceButton)
				self.pvpModeButtonDict[player.PK_MODE_REVENGE] = GetObject("pvp_revenge")
				self.pvpModeButtonDict[player.PK_MODE_REVENGE].SAFE_SetEvent(self.__OnClickPvPModeRevengeButton)
				self.pvpModeButtonDict[player.PK_MODE_GUILD] = GetObject("pvp_guild")
				self.pvpModeButtonDict[player.PK_MODE_GUILD].SAFE_SetEvent(self.__OnClickPvPModeGuildButton)
				self.pvpModeButtonDict[player.PK_MODE_FREE] = GetObject("pvp_free")
				self.pvpModeButtonDict[player.PK_MODE_FREE].SAFE_SetEvent(self.__OnClickPvPModeFreeButton)
				self.__SetPeacePKMode()

				block_exchange_button = GetObject("block_exchange_button")
				block_exchange_button.SetToggleUpEvent(self.__OnClickBlockExchangeButton)
				block_exchange_button.SetToggleDownEvent(self.__OnClickBlockExchangeButton)
				self.blockButtonList.append(block_exchange_button)

				block_party_button = GetObject("block_party_button")
				block_party_button.SetToggleUpEvent(self.__OnClickBlockPartyButton)
				block_party_button.SetToggleDownEvent(self.__OnClickBlockPartyButton)
				self.blockButtonList.append(block_party_button)

				block_guild_button = GetObject("block_guild_button")
				block_guild_button.SetToggleUpEvent(self.__OnClickBlockGuildButton)
				block_guild_button.SetToggleDownEvent(self.__OnClickBlockGuildButton)
				self.blockButtonList.append(block_guild_button)

				block_whisper_button = GetObject("block_whisper_button")
				block_whisper_button.SetToggleUpEvent(self.__OnClickBlockWhisperButton)
				block_whisper_button.SetToggleDownEvent(self.__OnClickBlockWhisperButton)
				self.blockButtonList.append(block_whisper_button)

				block_friend_button = GetObject("block_friend_button")
				block_friend_button.SetToggleUpEvent(self.__OnClickBlockFriendButton)
				block_friend_button.SetToggleDownEvent(self.__OnClickBlockFriendButton)
				self.blockButtonList.append(block_friend_button)

				block_party_request_button = GetObject("block_party_request_button")
				block_party_request_button.SetToggleUpEvent(self.__OnClickBlockPartyRequest)
				block_party_request_button.SetToggleDownEvent(self.__OnClickBlockPartyRequest)
				self.blockButtonList.append(block_party_request_button)

				showQuestLetterBtn = GetObject("show_letter")
				showQuestLetterBtn.SAFE_SetEvent(self.__OnClickQuestLetter)
				self.questLetterButtonList.append(showQuestLetterBtn)

				hideQuestLetterBtn = GetObject("hide_letter")
				hideQuestLetterBtn.SAFE_SetEvent(self.__OnClickQuestLetter)
				self.questLetterButtonList.append(hideQuestLetterBtn)
				self.RefreshQuestLetter()

				self.viewChatButtonList.append(GetObject("view_chat_on_button"))
				self.viewChatButtonList[0].SAFE_SetEvent(self.__OnClickViewChat)
				self.viewChatButtonList.append(GetObject("view_chat_off_button"))
				self.viewChatButtonList[1].SAFE_SetEvent(self.__OnClickViewChat)
				self.RefreshViewChat()

				self.nameColorModeButtonList.append(GetObject("name_color_normal"))
				self.nameColorModeButtonList[0].SAFE_SetEvent(self.__OnClickNameColorMode)
				self.nameColorModeButtonList.append(GetObject("name_color_empire"))
				self.nameColorModeButtonList[1].SAFE_SetEvent(self.__OnClickNameColorMode)
				self.RefreshNameColor()

				self.viewTargetBoardButtonList.append(GetObject("target_board_view"))
				self.viewTargetBoardButtonList[0].SAFE_SetEvent(self.__SetTargetBoardViewMode)
				self.viewTargetBoardButtonList.append(GetObject("target_board_no_view"))
				self.viewTargetBoardButtonList[1].SAFE_SetEvent(self.__SetTargetBoardViewMode)
				self.RefreshTargetBoard()

				if app.WJ_SHOW_MOB_INFO:
					self.showMobInfoButtonList.append(GetObject("show_mob_level_button"))
					self.showMobInfoButtonList.append(GetObject("show_mob_AI_flag_button"))
					self.showMobInfoButtonList[0].SetToggleUpEvent(self.__OnClickShowMobLevelButton)
					self.showMobInfoButtonList[0].SetToggleDownEvent(self.__OnClickShowMobLevelButton)
					self.showMobInfoButtonList[1].SetToggleUpEvent(self.__OnClickShowMobAIFlagButton)
					self.showMobInfoButtonList[1].SetToggleDownEvent(self.__OnClickShowMobAIFlagButton)
					self.RefreshShowMobInfo()

				self.AutoPickUpButtonList.append(GetObject("metin_on_button"))
				self.AutoPickUpButtonList[0].SAFE_SetEvent(self.__OnClickEnableMetin)
				self.AutoPickUpButtonList.append(GetObject("metin_off_button"))
				self.AutoPickUpButtonList[1].SAFE_SetEvent(self.__OnClickDisableMetin)
				self.RefreshShowAutoPickUp()

				self.AutoPickUpButtonList1.append(GetObject("canavar_on_button"))
				self.AutoPickUpButtonList1[0].SAFE_SetEvent(self.__OnClickEnableCanavar)
				self.AutoPickUpButtonList1.append(GetObject("canavar_off_button"))
				self.AutoPickUpButtonList1[1].SAFE_SetEvent(self.__OnClickDisableCanavar)
				self.RefreshShowAutoPickUp2()

				self.AutoPickUpButtonList2.append(GetObject("patron_on_button"))
				self.AutoPickUpButtonList2[0].SAFE_SetEvent(self.__OnClickEnablePatron)
				self.AutoPickUpButtonList2.append(GetObject("patron_off_button"))
				self.AutoPickUpButtonList2[1].SAFE_SetEvent(self.__OnClickDisablePatron)
				self.RefreshShowAutoPickUp3()



			# elif categoryIndex == 1:#Pickup
				# self.AutoPickUpButtonList.append(GetObject("metin_on_button"))
				# self.AutoPickUpButtonList[0].SAFE_SetEvent(self.__OnClickEnableMetin)
				# self.AutoPickUpButtonList.append(GetObject("metin_off_button"))
				# self.AutoPickUpButtonList[1].SAFE_SetEvent(self.__OnClickDisableMetin)
				# self.RefreshShowAutoPickUp()

				# self.AutoPickUpButtonList1.append(GetObject("canavar_on_button"))
				# self.AutoPickUpButtonList1[0].SAFE_SetEvent(self.__OnClickEnableCanavar)
				# self.AutoPickUpButtonList1.append(GetObject("canavar_off_button"))
				# self.AutoPickUpButtonList1[1].SAFE_SetEvent(self.__OnClickDisableCanavar)
				# self.RefreshShowAutoPickUp2()

				# self.AutoPickUpButtonList2.append(GetObject("patron_on_button"))
				# self.AutoPickUpButtonList2[0].SAFE_SetEvent(self.__OnClickEnablePatron)
				# self.AutoPickUpButtonList2.append(GetObject("patron_off_button"))
				# self.AutoPickUpButtonList2[1].SAFE_SetEvent(self.__OnClickDisablePatron)
				# self.RefreshShowAutoPickUp3()

		elif optionIndex == 1:#Graphic-Options
			if categoryIndex == 0:#General
				self.showDamageButtonList.append(GetObject("show_damage_on_button"))
				self.showDamageButtonList[0].SAFE_SetEvent(self.__OnClickShowDamage)
				self.showDamageButtonList.append(GetObject("show_damage_off_button"))
				self.showDamageButtonList[1].SAFE_SetEvent(self.__OnClickShowDamage)
				self.RefreshShowDamage()

				self.cameraModeButtonList.append(GetObject("camera_short"))
				self.cameraModeButtonList[0].SAFE_SetEvent(self.__OnClickCameraMode)
				self.cameraModeButtonList.append(GetObject("camera_long"))
				self.cameraModeButtonList[1].SAFE_SetEvent(self.__OnClickCameraMode)
				self.RefreshCameraMode()

				if app.ENABLE_FOG_FIX:
					self.fogModeButtonList.append(GetObject("fog_on"))
					self.fogModeButtonList[0].SAFE_SetEvent(self.__OnClickFogModeOn)
					self.fogModeButtonList.append(GetObject("fog_off"))
					self.fogModeButtonList[1].SAFE_SetEvent(self.__OnClickFogModeOff)
					self.RefreshFogMode()

				self.nightModeButtonList.append(GetObject("nightmode_on"))
				self.nightModeButtonList[0].SAFE_SetEvent(self.__OnClickNightModeOptionEnableButton)
				self.nightModeButtonList.append(GetObject("nightmode_off"))
				self.nightModeButtonList[1].SAFE_SetEvent(self.__OnClickNightModeOptionDisableButton)
				self.RefreshNightOption()

				if app.ENABLE_DISCORD_STUFF:
					self.wndNotificationButtonList.append(GetObject("windows_message_on"))
					self.wndNotificationButtonList[0].SAFE_SetEvent(self.__OnClickWindowsNotification)
					self.wndNotificationButtonList.append(GetObject("windows_message_off"))
					self.wndNotificationButtonList[1].SAFE_SetEvent(self.__OnClickWindowsNotification)
					self.UpdateWindowsNotification()
				else:
					GetObject("windows_message_window").Hide()

			elif categoryIndex == 1:#Interface
				self.showsalesTextButtonList.append(GetObject("salestext_on_button"))
				self.showsalesTextButtonList[0].SAFE_SetEvent(self.__OnClickSalesText)
				self.showsalesTextButtonList.append(GetObject("salestext_off_button"))
				self.showsalesTextButtonList[1].SAFE_SetEvent(self.__OnClickSalesText)
				self.RefreshShowSalesText()

				ctrlFovValue = GetObject("perspective_controller")
				pos = 0.0
				fog = float(systemSetting.GetFOVLevel())
				if fog < 30.0 or fog > 100.0:
					fog = 30.0
					systemSetting.SetFOVLevel(fog)

				if fog > 30.0:
					fog -= 30.0
					value =1.0/70.0
					pos = value*fog

				ctrlFovValue.SetSliderPos(pos)
				ctrlFovValue.SetEvent(ui.__mem_func__(self.OnChangeFOV))
				self.ctrlFovValue = ctrlFovValue

				self.YangdropButtonList.append(GetObject("yangdrop_on_button"))
				self.YangdropButtonList[0].SAFE_SetEvent(self.__OnClickYangShow)
				self.YangdropButtonList.append(GetObject("yangdrop_off_button"))
				self.YangdropButtonList[1].SAFE_SetEvent(self.__OnClickYangShow)
				self.RefreshYangShow()

			elif categoryIndex == 2:#Performance
				self.alwaysShowNameButtonList.append(GetObject("always_show_name_on_button"))
				self.alwaysShowNameButtonList[0].SAFE_SetEvent(self.__OnClickAlwaysShowName)
				self.alwaysShowNameButtonList.append(GetObject("always_show_name_off_button"))
				self.alwaysShowNameButtonList[1].SAFE_SetEvent(self.__OnClickAlwaysShowName)
				self.RefreshAlwaysShowName()

				self.affectIconsButtonList.append(GetObject("show_affect_icons"))
				self.affectIconsButtonList[0].SAFE_SetEvent(self.__OnClickAffectIcons)
				self.affectIconsButtonList.append(GetObject("hide_affect_icons"))
				self.affectIconsButtonList[1].SAFE_SetEvent(self.__OnClickAffectIcons)
				self.RefreshAffectIcons()

				self.MadaraModelShow.append(GetObject("ShowMadaraPetButton"))
				self.MadaraModelShow.append(GetObject("ShowMadaraMountButton"))
				self.MadaraModelShow[0].SetToggleUpEvent(self.__OnClickHidePetsButton)
				self.MadaraModelShow[0].SetToggleDownEvent(self.__OnClickHidePetsButton)
				self.MadaraModelShow[1].SetToggleUpEvent(self.__OnClickHideMountsButton)
				self.MadaraModelShow[1].SetToggleDownEvent(self.__OnClickHideMountsButton)
				self.UpdateMadaraModel()

				self.parlamaButtonList.append(GetObject("parlama_on"))
				self.parlamaButtonList[0].SAFE_SetEvent(self.highlightacik)
				self.parlamaButtonList.append(GetObject("parlama_off"))
				self.parlamaButtonList[1].SAFE_SetEvent(self.highlightkapali)
				self.RefreshShowHighlight()

				if app.ENABLE_EFFECT_SCALE:
					self.changeEffectScale = GetObject("effect_scale")
					self.changeEffectScale.SetSliderPos(float(systemSetting.GetEffectScale()) / 3500.0)
					self.changeEffectScale.SetEvent(ui.__mem_func__(self.OnEffectScale))

				if app.__BL_HIDE_EFFECT__:
					for BLEffectNames in ('BUFF_EFFECT', 'SKILL_EFFECT'):
						self.BLEffectGroupList.append(GetObject(BLEffectNames))

				if app.__BL_HIDE_EFFECT__:
					for (Index, Button) in enumerate(self.BLEffectGroupList):
						Button.SetToggleDownEvent(lambda arg=Index: self.__OnClickBLEffectButton(arg))
						Button.SetToggleUpEvent(lambda arg=Index: self.__OnClickBLEffectButton(arg))
					self.__RefreshBLEffectButton()

				self.DogeModeButtonList.append(GetObject("dogemode_on_button"))
				self.DogeModeButtonList[0].SAFE_SetEvent(self.__OnClickDogeMode)
				self.DogeModeButtonList.append(GetObject("dogemode_off_button"))
				self.DogeModeButtonList[1].SAFE_SetEvent(self.__OnClickDogeMode)
				self.RefreshDogeMode()

		elif optionIndex == 2:#Sound-Options
			if categoryIndex == 0:#General

				ctrlSoundVolume = GetObject("sound_volume_controller")
				ctrlSoundVolume.SetSliderPos(float(systemSetting.GetSoundVolume()) / 5.0)
				ctrlSoundVolume.SetEvent(ui.__mem_func__(self.OnChangeSoundVolume))
				self.ctrlSoundVolume = ctrlSoundVolume

				ctrlMusicVolume = GetObject("music_volume_controller")
				ctrlMusicVolume.SetSliderPos(float(systemSetting.GetMusicVolume()))
				ctrlMusicVolume.SetEvent(ui.__mem_func__(self.OnChangeMusicVolume))
				self.ctrlMusicVolume = ctrlMusicVolume
				GetObject("bgm_button").SAFE_SetEvent(self.__OnClickChangeMusicButton)
				self.selectMusicFile = GetObject("bgm_file")
		#except:
		#	dbg.TraceError("[GameOption]LoadCatetoryOptions optionIndex: %d categoryIndex: %d"%(optionIndex, categoryIndex))

	def OpenMobileTab(self):
		self.Show()
		self.SetOptionType(0)
		self.SetCategoryType(1)

	def __CreateOptionHeader(self, parent, text, y):
		headerWnd = ui.Window()
		headerWnd.SetParent(parent)
		headerWnd.SetPosition(0, y)
		headerWnd.SetSize(290, 22)

		img = ui.ExpandedImageBox()
		img.SetParent(headerWnd)
		img.SetPosition(0, 0)
		img.LoadImage(IMG_DIR + "option_title.tga")
		img.AddFlag("not_pick")
		img.Show()
		headerWnd.img = img

		txt = ui.TextLine()
		txt.SetParent(headerWnd)
		txt.SetPosition(5, 3)
		txt.SetText(text)
		txt.Show()
		headerWnd.txt = txt

		headerWnd.Show()
		return headerWnd

	def __AddMobileToggle(self, parent, y, title, getter, setter, isHudConfig=False):
		row = ui.Window()
		row.SetParent(parent)
		row.SetPosition(0, y)
		row.SetSize(290, 28)
		row.Show()

		lbl = ui.TextLine()
		lbl.SetParent(row)
		lbl.SetPosition(10, 6)
		lbl.SetText(title)
		lbl.Show()
		row.lbl = lbl

		btnToggle = ui.ToggleButton()
		btnToggle.SetParent(row)
		btnToggle.SetUpVisual(IMG_DIR + "toggle_unselected.tga")
		btnToggle.SetOverVisual(IMG_DIR + "toggle_unselected.tga")
		btnToggle.SetDownVisual(IMG_DIR + "toggle_selected.tga")
		btnToggle.SetPosition(245, 6)
		btnToggle.Show()

		import systemSetting, uiMobileHud
		def _Get():
			if isHudConfig:
				fn = getattr(uiMobileHud, getter, None)
			else:
				fn = getattr(systemSetting, getter, None)
				if fn is None:
					fn = getattr(uiMobileHud, getter, None)
			if fn:
				try: return bool(fn())
				except: pass
			return False

		def _Set(val):
			if isHudConfig:
				fn = getattr(uiMobileHud, setter, None)
			else:
				fn = getattr(systemSetting, setter, None)
				if fn is None:
					fn = getattr(uiMobileHud, setter, None)
			if fn:
				try: fn(val)
				except: pass
			try: systemSetting.SaveConfig()
			except: pass

		def _OnClick():
			newVal = not _Get()
			_Set(newVal)
			if newVal:
				btnToggle.Down()
			else:
				btnToggle.SetUp()

		if _Get():
			btnToggle.Down()
		else:
			btnToggle.SetUp()

		btnToggle.SAFE_SetEvent(_OnClick)
		row.btnToggle = btnToggle
		return y + 30

	def __AddMobileStepper(self, parent, y, title, getter, setter, low, high, step, isScale=False, isInt=False, isPercent=False, rebuild=False):
		row = ui.Window()
		row.SetParent(parent)
		row.SetPosition(0, y)
		row.SetSize(290, 28)
		row.Show()

		lbl = ui.TextLine()
		lbl.SetParent(row)
		lbl.SetPosition(10, 6)
		lbl.SetText(title)
		lbl.Show()
		row.lbl = lbl

		btnMinus = ui.Button()
		btnMinus.SetParent(row)
		btnMinus.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		btnMinus.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		btnMinus.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		btnMinus.SetPosition(175, 4)
		btnMinus.SetText("-")
		btnMinus.Show()

		valText = ui.TextLine()
		valText.SetParent(row)
		valText.SetPosition(220, 6)
		valText.SetHorizontalAlignCenter()
		valText.Show()
		row.valText = valText

		btnPlus = ui.Button()
		btnPlus.SetParent(row)
		btnPlus.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		btnPlus.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		btnPlus.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		btnPlus.SetPosition(245, 4)
		btnPlus.SetText("+")
		btnPlus.Show()

		import systemSetting, uiMobileHud
		def _Get():
			fn = getattr(systemSetting, getter, None)
			if fn is None:
				fn = getattr(uiMobileHud, getter, None)
			if fn:
				try: return float(fn())
				except: pass
			return 0.0

		def _Refresh():
			val = _Get()
			if isPercent:
				txt = "%%%d" % int(round(val * 100))
			elif isInt:
				txt = "%d" % int(round(val))
			elif isScale:
				txt = "x%.2f" % val
			else:
				txt = "%.2f" % val
			valText.SetText(txt)

		def _Set(val):
			fn = getattr(systemSetting, setter, None)
			if fn is None:
				fn = getattr(uiMobileHud, setter, None)
			if fn:
				try: fn(val)
				except: pass
			if rebuild:
				uiMobileHud.RequestRefresh()
			try:
				systemSetting.SaveConfig()
			except:
				pass
			_Refresh()

		def _Change(direction):
			val = _Get() + (step * direction)
			val = max(low, min(high, val))
			_Set(val)

		btnMinus.SAFE_SetEvent(_Change, -1)
		btnPlus.SAFE_SetEvent(_Change, 1)
		_Refresh()

		row.btnMinus = btnMinus
		row.btnPlus = btnPlus
		return y + 30

	def __BuildMobileCategory(self, scriptWindow):
		import uiMobileHud

		scriptWindow.SetSize(300, 324)
		scriptWindow.SetPosition(171, 3)

		y = 0
		# 1. HEDEF SECIMI
		self.__CreateOptionHeader(scriptWindow, "HEDEF SEÇİMİ", y)
		y += 24

		rowTarget = ui.Window()
		rowTarget.SetParent(scriptWindow)
		rowTarget.SetPosition(0, y)
		rowTarget.SetSize(290, 52)
		rowTarget.Show()

		titleTarget = ui.TextLine()
		titleTarget.SetParent(rowTarget)
		titleTarget.SetPosition(10, 2)
		titleTarget.SetText("Hedef Değiş Buton Önceliği:")
		titleTarget.Show()
		rowTarget.title = titleTarget

		btnMob = ui.RadioButton()
		btnMob.SetParent(rowTarget)
		btnMob.SetUpVisual(IMG_DIR + "radio_unselected.tga")
		btnMob.SetOverVisual(IMG_DIR + "radio_unselected.tga")
		btnMob.SetDownVisual(IMG_DIR + "radio_selected.tga")
		btnMob.SetPosition(15, 24)
		btnMob.SetText("Mob && Metin")
		btnMob.Show()

		btnPC = ui.RadioButton()
		btnPC.SetParent(rowTarget)
		btnPC.SetUpVisual(IMG_DIR + "radio_unselected.tga")
		btnPC.SetOverVisual(IMG_DIR + "radio_unselected.tga")
		btnPC.SetDownVisual(IMG_DIR + "radio_selected.tga")
		btnPC.SetPosition(145, 24)
		btnPC.SetText("Karakter (PC)")
		btnPC.Show()

		curPriority = uiMobileHud.GetTargetPriority()
		if curPriority == 1:
			btnPC.Down()
			btnMob.SetUp()
		else:
			btnMob.Down()
			btnPC.SetUp()

		def _SelectMob():
			btnMob.Down()
			btnPC.SetUp()
			uiMobileHud.SetTargetPriority(0)

		def _SelectPC():
			btnPC.Down()
			btnMob.SetUp()
			uiMobileHud.SetTargetPriority(1)

		btnMob.SAFE_SetEvent(_SelectMob)
		btnPC.SAFE_SetEvent(_SelectPC)
		rowTarget.btnMob = btnMob
		rowTarget.btnPC = btnPC
		y += 56

		# 2. ARAYUZ OLCEKLERI
		self.__CreateOptionHeader(scriptWindow, "ARAYÜz ÖLÇEKLERİ", y)
		y += 26

		y = self.__AddMobileStepper(scriptWindow, y, "Buton Boyutu", "GetHudButtonScale", "SetHudButtonScale", 0.70, 1.50, 0.05, isScale=True, rebuild=True)
		y = self.__AddMobileStepper(scriptWindow, y, "Menü Boyutu", "GetMenuScale", "SetMenuScale", 0.70, 1.50, 0.05, isScale=True, rebuild=True)
		y = self.__AddMobileStepper(scriptWindow, y, "Pencere Boyutu", "GetWindowScale", "SetWindowScale", 0.80, 1.60, 0.05, isScale=True, rebuild=True)
		y += 6

		# 3. KAMERA AYARLARI
		self.__CreateOptionHeader(scriptWindow, "KAMERA AYARLARI", y)
		y += 26

		y = self.__AddMobileStepper(scriptWindow, y, "Kamera Açısı", "GetCameraReturnPitch", "SetCameraReturnPitch", 0.0, 45.0, 1.0, isInt=True)
		y = self.__AddMobileStepper(scriptWindow, y, "Kamera Hassasiyeti", "GetCameraDragSens", "SetCameraDragSens", 0.25, 3.0, 0.25, isScale=True)
		y = self.__AddMobileStepper(scriptWindow, y, "Yakınlaşırma (Pinch)", "GetPinchZoomSens", "SetPinchZoomSens", 0.25, 3.0, 0.25, isScale=True)
		y = self.__AddMobileToggle(scriptWindow, y, "Otomatik Kamera Dönüşü", "IsCameraReturn", "SetCameraReturn")
		y += 6

		# 4. KONTROLLER
		self.__CreateOptionHeader(scriptWindow, "KONTROLLER", y)
		y += 26

		y = self.__AddMobileStepper(scriptWindow, y, "Joystick Boyutu", "GetJoystickSize", "SetJoystickSize", 80.0, 320.0, 20.0, isInt=True, rebuild=True)
		y = self.__AddMobileStepper(scriptWindow, y, "Joystick Ölü Bölge", "GetJoystickDeadZone", "SetJoystickDeadZone", 0.0, 0.50, 0.05, isPercent=True)
		y = self.__AddMobileStepper(scriptWindow, y, "Saldırı Buton Boyutu", "GetAttackButtonSize", "SetAttackButtonSize", 80.0, 320.0, 20.0, isInt=True, rebuild=True)
		y = self.__AddMobileToggle(scriptWindow, y, "Dinamik Joystick", "IsDynamicJoystick", "SetDynamicJoystick", isHudConfig=True)
		y += 6

		# 5. DIGER MOBIL AYARLAR
		self.__CreateOptionHeader(scriptWindow, "DİĞER AYARLAR", y)
		y += 26

		y = self.__AddMobileToggle(scriptWindow, y, "Canlı Sohbet Akışı", "IsLiveChatEnabled", "SetLiveChatEnabled", isHudConfig=True)

		# HUD Duzenleme Butonlari
		btnRow = ui.Window()
		btnRow.SetParent(scriptWindow)
		btnRow.SetPosition(0, y)
		btnRow.SetSize(290, 40)
		btnRow.Show()

		btnEdit = ui.Button()
		btnEdit.SetParent(btnRow)
		btnEdit.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		btnEdit.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		btnEdit.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		btnEdit.SetPosition(15, 6)
		btnEdit.SetText("HUD Düzenle")
		def _OnEditHud():
			self.Close()
			uiMobileHud.StartHudEditMode()
		btnEdit.SAFE_SetEvent(_OnEditHud)
		btnEdit.Show()

		btnReset = ui.Button()
		btnReset.SetParent(btnRow)
		btnReset.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		btnReset.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		btnReset.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		btnReset.SetPosition(150, 6)
		btnReset.SetText("Varsayılana Dön")
		def _OnResetHud():
			uiMobileHud.ResetHudPositions()
		btnReset.SAFE_SetEvent(_OnResetHud)
		btnReset.Show()

		btnRow.btnEdit = btnEdit
		btnRow.btnReset = btnReset
		y += 44

	# Dont Touch #
	def GetCurrentWindow(self):
		if self.children.has_key("optionType") and self.children.has_key("categoryType"):
			(optionType,categoryType) = (self.children["optionType"],self.children["categoryType"])
			if self.children.has_key("optionWindow%d%d"%(optionType,categoryType)):
				return self.children["optionWindow%d%d"%(optionType,categoryType)]
		return None
	def GetCurrentScrollBar(self):
		window = self.GetCurrentWindow()
		if window != None:
			return window.scrollBar
		return None
	def OnRunMouseWheel(self, nLen):
		scrollBar = self.GetCurrentScrollBar()
		if scrollBar:
			if scrollBar.IsShow():
				if nLen > 0:
					scrollBar.OnUp()
				else:
					scrollBar.OnDown()
				return True
		return False

	def UpdateScrollBar(self):
		window = self.GetCurrentWindow()
		if window == None:
			return
		scrollBar = window.scrollBar
		if scrollBar == None:
			return
		scriptChildrens = window.Children
		if len(scriptChildrens) == 0:
			return

		windowHeight = window.GetHeight()

		# OLD SHIT
		#lastChildren = scriptChildrens[len(scriptChildrens)-1]
		#screenSize = lastChildren.exPos[1]+lastChildren.GetHeight()

		screenSize = 0
		for child in scriptChildrens:
			childHeight = child.exPos[1] + child.GetHeight()
			if childHeight > screenSize:
				screenSize=childHeight

		if screenSize > windowHeight:
			scrollLen = screenSize-windowHeight
			window.scrollLen = scrollLen
			basePos = int(scrollBar.GetPos()*scrollLen)
			for child in scriptChildrens:
				(_x,_y) = child.exPos
				child.SetPosition(_x,_y-basePos)

			scrollBar.SetMiddleBarSize(float(windowHeight-5)/float(screenSize))
			scrollBar.Show()
		else:
			window.scrollLen = 0
			scrollBar.Hide()

		_wy = window.GetGlobalPosition()[1]
		elementDictionary = window.ElementDictionary
		for childName, child in elementDictionary.items():
			(_x,_y) = child.GetGlobalPosition()
			childHeight = child.GetHeight()
			textLines = []
			images = []
			if isinstance(child, ui.ExpandedImageBox):
				images.append(child)
			elif isinstance(child, ui.TextLine):
				textLines.append(child)
			elif isinstance(child, ui.ToggleButton) or isinstance(child, ui.RadioButton):
				if child.ButtonText != None:
					textLines.append(child.ButtonText)
				images.append(child)
			elif isinstance(child, ui.SliderBar):
				if child.backGroundImage != None:
					images.append(child.backGroundImage)
				if child.cursor != None:
					images.append(child.cursor)

			for childItem in textLines:
				if _y < _wy:
					if childItem.IsShow():
						childItem.Hide()
				elif _y > (_wy+windowHeight-20):
					if childItem.IsShow():
						childItem.Hide()
				else:
					if not childItem.IsShow():
						childItem.Show()

			for childItem in images:
				if _y < _wy:
					childItem.SetRenderingRect(0,ui.calculateRect(childHeight-abs(_y-_wy),childHeight),0,0)
				elif _y+childHeight > (_wy+windowHeight-4):
					calculate = (_wy+windowHeight-4) - (_y+childHeight)
					if calculate == 0:
						return
					f = ui.calculateRect(childHeight-abs(calculate),childHeight)
					childItem.SetRenderingRect(0,0,0,f)
				else:
					childItem.SetRenderingRect(0,0,0,0)
	# Dont Touch #

	# PvP - Mode
	def __SetPeacePKMode(self):
		self.__SetPKMode(player.PK_MODE_PEACE)
	def __SetPKMode(self, mode):
		for btn in self.pvpModeButtonDict.values():
			btn.SetUp()
		if self.pvpModeButtonDict.has_key(mode):
			self.pvpModeButtonDict[mode].Down()
	def __CheckPvPProtectedLevelPlayer(self):
		if player.GetStatus(player.LEVEL)<constInfo.PVPMODE_PROTECTED_LEVEL:
			self.__SetPeacePKMode()
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.OPTION_PVPMODE_PROTECT % (constInfo.PVPMODE_PROTECTED_LEVEL))
			return True
		return False
	def __RefreshPVPButtonList(self):
		self.__SetPKMode(player.GetPKMode())
	def __OnClickPvPModePeaceButton(self):
		if self.__CheckPvPProtectedLevelPlayer():
			return
		self.__RefreshPVPButtonList()
		if constInfo.PVPMODE_ENABLE:
			net.SendChatPacket("/pkmode 0", chat.CHAT_TYPE_TALKING)
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.OPTION_PVPMODE_NOT_SUPPORT)
	def __OnClickPvPModeRevengeButton(self):
		if self.__CheckPvPProtectedLevelPlayer():
			return
		self.__RefreshPVPButtonList()
		if constInfo.PVPMODE_ENABLE:
			net.SendChatPacket("/pkmode 1", chat.CHAT_TYPE_TALKING)
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.OPTION_PVPMODE_NOT_SUPPORT)
	def __OnClickPvPModeFreeButton(self):
		if self.__CheckPvPProtectedLevelPlayer():
			return
		self.__RefreshPVPButtonList()
		if constInfo.PVPMODE_ENABLE:
			net.SendChatPacket("/pkmode 2", chat.CHAT_TYPE_TALKING)
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.OPTION_PVPMODE_NOT_SUPPORT)
	def __OnClickPvPModeGuildButton(self):
		if self.__CheckPvPProtectedLevelPlayer():
			return
		self.__RefreshPVPButtonList()
		if 0 == player.GetGuildID():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.OPTION_PVPMODE_CANNOT_SET_GUILD_MODE)
			return
		if constInfo.PVPMODE_ENABLE:
			net.SendChatPacket("/pkmode 4", chat.CHAT_TYPE_TALKING)
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.OPTION_PVPMODE_NOT_SUPPORT)
	def OnChangePKMode(self):
		self.__RefreshPVPButtonList()
	# PvP - Mode

	# Skill / Buff - Mode
	if app.__BL_HIDE_EFFECT__:
		def __OnClickBLEffectButton(self, Index):
			systemSetting.SetBLEffectOption(Index, not systemSetting.GetBLEffectOption(Index))
			self.__RefreshBLEffectButton()
		
		def __RefreshBLEffectButton(self):
			for (Index, Button) in enumerate(self.BLEffectGroupList):
				if systemSetting.GetBLEffectOption(Index):
					Button.Down()
				else:
					Button.SetUp()
	# Skill / Buff - Mode
	
	# Block - Mode
	def RefreshBlock(self):
		global blockMode
		for i in xrange(len(self.blockButtonList)):
			if 0 != (blockMode & (1 << i)):
				self.blockButtonList[i].Down()
			else:
				self.blockButtonList[i].SetUp()
	def OnBlockMode(self, mode):
		global blockMode
		blockMode = mode
		self.RefreshBlock()
	def __OnClickBlockExchangeButton(self):
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_EXCHANGE))
	def __OnClickBlockPartyButton(self):
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_PARTY))
	def __OnClickBlockGuildButton(self):
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_GUILD))
	def __OnClickBlockWhisperButton(self):
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_WHISPER))
	def __OnClickBlockFriendButton(self):
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_FRIEND))
	def __OnClickBlockPartyRequest(self):
		self.RefreshBlock()
		global blockMode
		net.SendChatPacket("/setblockmode " + str(blockMode ^ player.BLOCK_PARTY_REQUEST))
	# Block - Mode

	# Quest Letter - Mode
	def RefreshQuestLetter(self):
		if systemSetting.GetQuestIconMode():
			self.questLetterButtonList[0].Down()
			self.questLetterButtonList[1].SetUp()
		else:
			self.questLetterButtonList[0].SetUp()
			self.questLetterButtonList[1].Down()
		interface = constInfo.GetInterfaceInstance()
		if interface != None:
			if systemSetting.GetQuestIconMode():
				interface.ShowAllQuestButton()
			else:
				interface.HideAllQuestButton()

	def __OnClickQuestLetter(self):
		systemSetting.SetQuestIconMode(not systemSetting.GetQuestIconMode())
		self.RefreshQuestLetter()
	# Quest Letter - Mode

	# Chat - Mode
	def RefreshViewChat(self):
		if systemSetting.IsViewChat():
			self.viewChatButtonList[0].Down()
			self.viewChatButtonList[1].SetUp()
		else:
			self.viewChatButtonList[0].SetUp()
			self.viewChatButtonList[1].Down()

	def __OnClickViewChat(self):
		systemSetting.SetViewChatFlag(not systemSetting.IsViewChat())
		systemSetting.SaveConfig()
		self.RefreshViewChat()
	# Chat - Mode

	# Name Color - Mode
	def __OnClickNameColorMode(self):
		constInfo.SET_CHRNAME_COLOR_INDEX(not constInfo.GET_CHRNAME_COLOR_INDEX())
		self.RefreshNameColor()

	def RefreshNameColor(self):
		index = constInfo.GET_CHRNAME_COLOR_INDEX()
		self.nameColorModeButtonList[index].Down()
		self.nameColorModeButtonList[not index].SetUp()
	# Name Color - Mode

	# Target Board - Mode
	def RefreshTargetBoard(self):
		index = constInfo.GET_VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD()
		self.viewTargetBoardButtonList[index].Down()
		self.viewTargetBoardButtonList[not index].SetUp()

	def __SetTargetBoardViewMode(self):
		constInfo.SET_VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD(not constInfo.GET_VIEW_OTHER_EMPIRE_PLAYER_TARGET_BOARD())
		self.RefreshTargetBoard()
	# Target Board - Mode

	#Yang Info - Mode
	def RefreshYangShow(self):
		if systemSetting.IsYangDropMode():
			self.YangdropButtonList[0].Down()
			self.YangdropButtonList[1].SetUp()
			chat.AppendChat(chat.CHAT_TYPE_INFO, "|cffFFC125Yang Bilgisi Aktif.")
		else:
			self.YangdropButtonList[0].SetUp()
			self.YangdropButtonList[1].Down()
			chat.AppendChat(chat.CHAT_TYPE_INFO, "|cffFFC125Yang Bilgisi Deaktif.")

	def __OnClickYangShow(self):
		systemSetting.SetYangDropMode(not systemSetting.IsYangDropMode())
		self.RefreshYangShow()
	#Yang Info - Mode

	#Doge - Mode
	def RefreshDogeMode(self):
		if systemSetting.IsPolyDogMode():
			self.DogeModeButtonList[0].Down()
			self.DogeModeButtonList[1].SetUp()
			chat.AppendChat(chat.CHAT_TYPE_INFO, "|cffFFC125Kpek Modu Aktif.")
		else:
			self.DogeModeButtonList[0].SetUp()
			self.DogeModeButtonList[1].Down()
			chat.AppendChat(chat.CHAT_TYPE_INFO, "|cffFFC125Kpek Modu Deaktif.")

	def __OnClickDogeMode(self):
		bStatus = (not systemSetting.IsPolyDogMode())
		systemSetting.SetPolyDogMode(bStatus)
		background.SetPolyAllMobDog(bStatus)
		self.RefreshDogeMode()
	#Doge - Mode

	# Show Always Name - Mode
	def RefreshAlwaysShowName(self):
		index = systemSetting.IsAlwaysShowName()
		self.alwaysShowNameButtonList[index].SetUp()
		self.alwaysShowNameButtonList[not index].Down()

	def __OnClickAlwaysShowName(self):
		systemSetting.SetAlwaysShowNameFlag(not systemSetting.IsAlwaysShowName())
		self.RefreshAlwaysShowName()
	# Show Always Name - Mode

	def EngelMap(self):
		turmap = [
			"metin2_map_deviltower1",
			"metin2_map_devilscatacomb",
		]
		if str(background.GetCurrentMapName()) in turmap: 
			return True

		return False

	# def RefreshFpsBoost(self):
		# if self.EngelMap() == True:
			# chat.AppendChat(chat.CHAT_TYPE_INFO, "|cffFFC125Bu Haritada kullanamazsiniz.")
			# return
		# self.ToggleFpsBoost(systemSetting.GetExtremeFpsBoost())

	# def ToggleFpsBoost(self, bOnOff):
		# if self.EngelMap() == True:
			# chat.AppendChat(chat.CHAT_TYPE_INFO, "|cffFFC125Bu Haritada kullanamazsiniz.")
			# return
		# systemSetting.SetExtremeFpsBoost(bOnOff)
		# self.__ClickRadioButton(self.fpsBoostBtnList, int(bOnOff))

	# Pet & Mount Hide/Show - Mode
	def __OnClickHidePetsButton(self):
		systemSetting.SetHidePets(not systemSetting.IsHidePets())
		self.UpdateMadaraModel()

	def __OnClickHideMountsButton(self):
		systemSetting.SetHideMounts(not systemSetting.IsHideMounts())
		self.UpdateMadaraModel()

	def UpdateMadaraModel(self):
		if systemSetting.IsHidePets():
			self.MadaraModelShow[0].Down()
		else:
			self.MadaraModelShow[0].SetUp()

		if systemSetting.IsHideMounts():
			self.MadaraModelShow[1].Down()
		else:
			self.MadaraModelShow[1].SetUp()
	# Pet & Mount Hide/Show - Mode

	# Auto Pickup - Mode
	if app.ENABLE_AUTO_PICKUP_SYSTEM:
		def __OnClickEnableMetin(self):
			self.AutoPickUpButtonList[0].Down()
			self.AutoPickUpButtonList[1].SetUp()
			systemSetting.SetAutoPickupMetin(1)
			net.SendChatPacket("/oto_toplama 0 1")

		def __OnClickDisableMetin(self):
			self.AutoPickUpButtonList[0].SetUp()
			self.AutoPickUpButtonList[1].Down()
			systemSetting.SetAutoPickupMetin(0)
			net.SendChatPacket("/oto_toplama 0 0")

		def __OnClickEnableCanavar(self):
			self.AutoPickUpButtonList1[0].Down()
			self.AutoPickUpButtonList1[1].SetUp()
			systemSetting.SetAutoPickupMonster(1)
			net.SendChatPacket("/oto_toplama 1 1")

		def __OnClickDisableCanavar(self):
			self.AutoPickUpButtonList1[0].SetUp()
			self.AutoPickUpButtonList1[1].Down()
			systemSetting.SetAutoPickupMonster(0)
			net.SendChatPacket("/oto_toplama 1 0")

		def __OnClickEnablePatron(self):
			self.AutoPickUpButtonList2[0].Down()
			self.AutoPickUpButtonList2[1].SetUp()
			systemSetting.SetAutoPickupBoss(1)
			net.SendChatPacket("/oto_toplama 2 1")

		def __OnClickDisablePatron(self):
			self.AutoPickUpButtonList2[0].SetUp()
			self.AutoPickUpButtonList2[1].Down()
			systemSetting.SetAutoPickupBoss(0)
			net.SendChatPacket("/oto_toplama 2 0")

		def RefreshShowAutoPickUp(self):
			# if player.GetOtoMetin() == 1:
			if (systemSetting.IsAutoPickupMetin() == True):
				self.AutoPickUpButtonList[0].Down()
				self.AutoPickUpButtonList[1].SetUp()
			else:
				self.AutoPickUpButtonList[0].SetUp()
				self.AutoPickUpButtonList[1].Down()

		def RefreshShowAutoPickUp2(self):
			# if player.GetOtoCanavar() == 1:
			if (systemSetting.IsAutoPickupMonster() == True):
				self.AutoPickUpButtonList1[0].Down()
				self.AutoPickUpButtonList1[1].SetUp()
			else:
				self.AutoPickUpButtonList1[0].SetUp()
				self.AutoPickUpButtonList1[1].Down()

		def RefreshShowAutoPickUp3(self):
			# if player.GetOtoPatron() == 1:
			if (systemSetting.IsAutoPickupBoss() == True):
				self.AutoPickUpButtonList2[0].Down()
				self.AutoPickUpButtonList2[1].SetUp()
			else:
				self.AutoPickUpButtonList2[0].SetUp()
				self.AutoPickUpButtonList2[1].Down()
	# Auto Pickup - Mode

	# Show Damage - Mode
	def RefreshShowDamage(self):
		index = systemSetting.IsShowDamage()
		self.showDamageButtonList[index].SetUp()
		self.showDamageButtonList[not index].Down()

	def __OnClickShowDamage(self):
		systemSetting.SetShowDamageFlag(not systemSetting.IsShowDamage())
		systemSetting.SaveConfig()
		self.RefreshShowDamage()
	# Show Damage - Mode

	# Sales Text - Mode
	def __OnClickSalesText(self):
		systemSetting.SetShowSalesTextFlag(not systemSetting.IsShowSalesText())
		systemSetting.SaveConfig()
		self.RefreshShowSalesText()

	def RefreshShowSalesText(self):
		index = systemSetting.IsShowSalesText()
		self.showsalesTextButtonList[index].Down()
		self.showsalesTextButtonList[not index].SetUp()

		if int(index == 0):
			ikashop.ShowShopNames()
		elif int(index == 1):
			ikashop.HideShopNames()
	# Sales Text - Mode

	# Sound - Mode
	def OnChangeSoundVolume(self):
		pos = self.ctrlSoundVolume.GetSliderPos()
		snd.SetSoundVolumef(pos)
		systemSetting.SetSoundVolumef(pos)
		systemSetting.SaveConfig()
	# Sound - Mode

	# Music - Mode
	def OnChangeMusicVolume(self):
		pos = self.ctrlMusicVolume.GetSliderPos()
		snd.SetMusicVolume(pos * net.GetFieldMusicVolume())
		systemSetting.SetMusicVolume(pos)
		systemSetting.SaveConfig()
	def __OnChangeMusic(self, fileName):
		self.selectMusicFile.SetText(fileName[:MUSIC_FILENAME_MAX_LEN])
		if musicInfo.fieldMusic != "":
			snd.FadeOutMusic("BGM/"+ musicInfo.fieldMusic)
		if fileName==uiSelectMusic.DEFAULT_THEMA:
			musicInfo.fieldMusic=musicInfo.METIN2THEMA
		else:
			musicInfo.fieldMusic=fileName
		musicInfo.SaveLastPlayFieldMusic()
		if musicInfo.fieldMusic != "":
			snd.FadeInMusic("BGM/" + musicInfo.fieldMusic)
	def __OnClickChangeMusicButton(self):
		if not self.musicListDlg:
			self.musicListDlg=uiSelectMusic.FileListDialog()
			self.musicListDlg.SAFE_SetSelectEvent(self.__OnChangeMusic)
		self.musicListDlg.Open()
	# Music - Mode

	# Camera - Mode
	def RefreshCameraMode(self):
		index = constInfo.GET_CAMERA_MAX_DISTANCE_INDEX()
		self.cameraModeButtonList[index].Down()
		self.cameraModeButtonList[not index].SetUp()
	def __OnClickCameraMode(self):
		constInfo.SET_CAMERA_MAX_DISTANCE_INDEX(not constInfo.GET_CAMERA_MAX_DISTANCE_INDEX())
		self.RefreshCameraMode()
	# Camera - Mode

	# Fog - Mode
	if app.ENABLE_FOG_FIX:
		def __OnClickFogModeOn(self):
			systemSetting.SetFogMode(True)
			background.SetEnvironmentFog(True)
			systemSetting.SaveConfig()
			self.RefreshFogMode()

		def __OnClickFogModeOff(self):
			systemSetting.SetFogMode(False)
			background.SetEnvironmentFog(False)
			systemSetting.SaveConfig()
			self.RefreshFogMode()

		def RefreshFogMode(self):
			if systemSetting.IsFogMode():
				self.fogModeButtonList[0].Down()
				self.fogModeButtonList[1].SetUp()
			else:
				self.fogModeButtonList[0].SetUp()
				self.fogModeButtonList[1].Down()
	# Fog - Mode

	# Mob Info - Mode
	if app.WJ_SHOW_MOB_INFO:
		def RefreshShowMobInfo(self):
			if systemSetting.IsShowMobLevel():
				self.showMobInfoButtonList[0].Down()
			else:
				self.showMobInfoButtonList[0].SetUp()
			if systemSetting.IsShowMobAIFlag():
				self.showMobInfoButtonList[1].Down()
			else:
				self.showMobInfoButtonList[1].SetUp()
		def __OnClickShowMobLevelButton(self):
			systemSetting.SetShowMobLevel(not systemSetting.IsShowMobLevel())
			systemSetting.SaveConfig()
			self.RefreshShowMobInfo()
		def __OnClickShowMobAIFlagButton(self):
			systemSetting.SetShowMobAIFlag(not systemSetting.IsShowMobAIFlag())
			systemSetting.SaveConfig()
			self.RefreshShowMobInfo()
	# Mob Info - Mode

	# Affect Icons - Mode
	def RefreshAffectIcons(self):
		index = systemSetting.GetAffectIcons()
		self.affectIconsButtonList[not index].Down()
		self.affectIconsButtonList[index].SetUp()

		game = constInfo.GetGameInstance()
		if game != None:
			if game.affectShower != None:
				if systemSetting.GetAffectIcons():
					game.affectShower.Show()
				else:
					game.affectShower.Hide()

	def __OnClickAffectIcons(self):
		systemSetting.SetAffectIcons(not systemSetting.GetAffectIcons())
		systemSetting.SaveConfig()
		self.RefreshAffectIcons()
	# Affect Icons - Mode

	# Highlight - Mode
	def highlightacik(self):
		systemSetting.SetShowHighlight(True)
		chat.AppendChat(chat.CHAT_TYPE_INFO, "Yeni item efekti aktif.")
		self.RefreshShowHighlight()

	def highlightkapali(self):
		systemSetting.SetShowHighlight(False)
		chat.AppendChat(chat.CHAT_TYPE_INFO, "Yeni item efekti deaktif.")
		self.RefreshShowHighlight()
	# Highlight - Mode

	def RefreshShowHighlight(self):
		if systemSetting.IsShowHighlight():
			self.parlamaButtonList[0].Down()
			self.parlamaButtonList[1].SetUp()
		else:
			self.parlamaButtonList[0].SetUp()
			self.parlamaButtonList[1].Down()

	def OnChangeFOV(self):
		pos = self.ctrlFovValue.GetSliderPos()*70
		value =1.0/70.0
		realpos = (value*pos)*70
		realpos+=30.0
		systemSetting.SetFOVLevel(realpos)

	if app.ENABLE_EFFECT_SCALE:
		def OnEffectScale(self):
			pos = self.changeEffectScale.GetSliderPos()
			systemSetting.SetEffectScale(pos * 3500)

	def __OnClickNightModeOptionEnableButton(self):
		systemSetting.SetNightMode(True)
		background.RegisterEnvironmentData(1, constInfo.ENVIRONMENT_NIGHT)
		background.SetEnvironmentData(1)
		systemSetting.SaveConfig()
		self.RefreshNightOption()

	def __OnClickNightModeOptionDisableButton(self):
		systemSetting.SetNightMode(False)
		background.SetEnvironmentData(0)
		systemSetting.SaveConfig()
		self.RefreshNightOption()

	def RefreshNightOption(self):
		if systemSetting.GetNightMode():
			self.nightModeButtonList[0].Down()
			self.nightModeButtonList[1].SetUp()
		else:
			self.nightModeButtonList[0].SetUp()
			self.nightModeButtonList[1].Down()
			
	if app.ENABLE_DISCORD_STUFF:
		def __OnClickWindowsNotification(self):
			systemSetting.SetStuffMessage(not systemSetting.GetStuffMessage())
			self.UpdateWindowsNotification()
		def UpdateWindowsNotification(self):
			self.__ClickRadioButton(self.wndNotificationButtonList, not systemSetting.GetStuffMessage())



class ScrollBarNew(ui.Window):
	SCROLLBAR_WIDTH = 20
	SCROLL_BTN_XDIST = 0
	SCROLL_BTN_YDIST = 0
	class MiddleBar(ui.DragButton):
		def __init__(self):
			ui.DragButton.__init__(self)
			self.AddFlag("movable")
			self.SetWindowName("scrollbar_middlebar")
		def MakeImage(self):
			top = ui.ExpandedImageBox()
			top.SetParent(self)
			top.LoadImage(IMG_DIR+"scrollbar/scrollbar_top.tga")
			top.AddFlag("not_pick")
			top.Show()
			topScale = ui.ExpandedImageBox()
			topScale.SetParent(self)
			topScale.SetPosition(0, top.GetHeight())
			topScale.LoadImage(IMG_DIR+"scrollbar/scrollbar_scale.tga")
			topScale.AddFlag("not_pick")
			topScale.Show()
			bottom = ui.ExpandedImageBox()
			bottom.SetParent(self)
			bottom.LoadImage(IMG_DIR+"scrollbar/scrollbar_bottom.tga")
			bottom.AddFlag("not_pick")
			bottom.Show()
			bottomScale = ui.ExpandedImageBox()
			bottomScale.SetParent(self)
			bottomScale.LoadImage(IMG_DIR+"scrollbar/scrollbar_scale.tga")
			bottomScale.AddFlag("not_pick")
			bottomScale.Show()
			middle = ui.ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage(IMG_DIR+"scrollbar/scrollbar_mid.tga")
			middle.AddFlag("not_pick")
			middle.Show()
			self.top = top
			self.topScale = topScale
			self.bottom = bottom
			self.bottomScale = bottomScale
			self.middle = middle
		def SetSize(self, height):
			minHeight = self.top.GetHeight() + self.bottom.GetHeight() + self.middle.GetHeight()
			height = max(minHeight, height)
			ui.DragButton.SetSize(self, 14, height)
			scale = (height - minHeight) / 2 
			extraScale = 0
			if (height - minHeight) % 2 == 1:
				extraScale = 1
			self.topScale.SetRenderingRect(0, 0, 0, scale - 1)
			self.middle.SetPosition(0, self.top.GetHeight() + scale)
			self.bottomScale.SetPosition(0, self.middle.GetBottom())
			self.bottomScale.SetRenderingRect(0, 0, 0, scale - 1 + extraScale)
			self.bottom.SetPosition(0, height - self.bottom.GetHeight())
	def __init__(self):
		ui.Window.__init__(self)
		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = None
		self.eventArgs = None
		self.lockFlag = False
		self.bDragging = False
		self.CreateScrollBar()
		self.SetScrollBarSize(0)
		self.scrollStep = 0.1
		self.SetWindowName("NONAME_ScrollBar")
	def __del__(self):
		ui.Window.__del__(self)
	def CreateScrollBar(self):
		topImage = ui.ExpandedImageBox()
		topImage.SetParent(self)
		topImage.AddFlag("not_pick")
		topImage.LoadImage(IMG_DIR+"scrollbar/scroll_top.tga")
		topImage.Show()
		bottomImage = ui.ExpandedImageBox()
		bottomImage.SetParent(self)
		bottomImage.AddFlag("not_pick")
		bottomImage.LoadImage(IMG_DIR+"scrollbar/scroll_bottom.tga")
		bottomImage.Show()
		middleImage = ui.ExpandedImageBox()
		middleImage.SetParent(self)
		middleImage.AddFlag("not_pick")
		middleImage.SetPosition(0, topImage.GetHeight())
		middleImage.LoadImage(IMG_DIR+"scrollbar/scroll_mid.tga")
		middleImage.Show()
		self.topImage = topImage
		self.bottomImage = bottomImage
		self.middleImage = middleImage
		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(ui.__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.MakeImage()
		middleBar.SetSize(12)
		self.middleBar = middleBar
	def Destroy(self):
		self.eventScroll = None
		self.eventArgs = None
	def SetScrollEvent(self, event, *args):
		self.eventScroll = event
		self.eventArgs = args
	def SetMiddleBarSize(self, pageScale):
		self.middleBar.SetSize(int(pageScale * float(self.GetHeight() - (self.SCROLL_BTN_YDIST*2))))
		realHeight = self.GetHeight() - (self.SCROLL_BTN_YDIST*2) - self.middleBar.GetHeight()
		self.pageSize = realHeight

	def SetScrollBarSize(self, height):
		self.SetSize(self.SCROLLBAR_WIDTH, height)
		self.pageSize = height - self.SCROLL_BTN_YDIST*2 - self.middleBar.GetHeight()
		middleImageScale = float((height - self.SCROLL_BTN_YDIST*2) - self.middleImage.GetHeight()) / float(self.middleImage.GetHeight())
		self.middleImage.SetRenderingRect(0, 0, 0, middleImageScale)
		self.bottomImage.SetPosition(0, height - self.bottomImage.GetHeight())
		self.middleBar.SetRestrictMovementArea(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST, \
			self.middleBar.GetWidth(), height - self.SCROLL_BTN_YDIST * 2)
		self.middleBar.SetPosition(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST)
	def SetScrollStep(self, step):
		self.scrollStep = step
	def OnUp(self):
		self.SetPos(self.curPos-self.scrollStep)
	def OnDown(self):
		self.SetPos(self.curPos+self.scrollStep)
	def GetScrollStep(self):
		return self.scrollStep
	def GetPos(self):
		return self.curPos
	def SetPos(self, pos, moveEvent = True):
		pos = max(0.0, pos)
		pos = min(1.0, pos)
		newPos = float(self.pageSize) * pos
		self.middleBar.SetPosition(self.SCROLL_BTN_XDIST, int(newPos) + self.SCROLL_BTN_YDIST)
		if moveEvent == True:
			self.OnMove()
	def OnMove(self):
		if self.lockFlag:
			return
		if 0 == self.pageSize:
			return
		(xLocal, yLocal) = self.middleBar.GetLocalPosition()
		self.curPos = float(yLocal - self.SCROLL_BTN_YDIST) / float(self.pageSize)
		if self.eventScroll:
			apply(self.eventScroll, self.eventArgs)
	def OnMouseLeftButtonDown(self):
		self.bDragging = True
		self.__ScrollToMouse()
		return True
	def OnMouseLeftButtonUp(self):
		self.bDragging = False
		return True
	def OnUpdate(self):
		if getattr(self, "bDragging", False):
			if not wndMgr.IsLButtonDown():
				self.bDragging = False
				return
			self.__ScrollToMouse()
	def __ScrollToMouse(self):
		if self.lockFlag or not self.pageSize:
			return
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		pickedPos = yMouseLocalPosition - self.SCROLL_BTN_YDIST - (self.middleBar.GetHeight() / 2)
		newPos = max(0.0, min(1.0, float(pickedPos) / float(max(1, self.pageSize))))
		self.SetPos(newPos)
	def LockScroll(self):
		self.lockFlag = True
	def UnlockScroll(self):
		self.lockFlag = False
