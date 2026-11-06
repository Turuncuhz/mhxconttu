
import ui, dbg, mouseModule, constInfo, localeInfo, app
import item, player, miniMap, chat, net

RANGE_CIRCLE = 70.0

IMG_DIR = "otomatik_av/"

def SecondToDHM(time):
	second = int(time % 60)
	minute = int((time / 60) % 60)
	hour = int((time / 60) / 60) % 24
	day = int(int((time / 60) / 60) / 24)

	text = ""

	if day > 0:
		text += str(day) + " " + "G. "
		text += " "

	if hour > 0:
		text += str(hour) + " " + "Sa. "
		text += " "

	if minute > 0:
		text += str(minute) + " " + "Dk. "

	if second > 0:
		text += str(second) + " " + "Sn. "

	return text

class Window(ui.BoardWithTitleBar):
	__children = {}
	def __init__(self):
		ui.BoardWithTitleBar.__init__(self)
		self.__LoadWindow()

	def Destroy(self):
		if len(self.__children) != 0:
			if self.IsActive():
				if self.__children["newOptions"]["auto_login"] == 1:
					constInfo.autoHuntAutoLoginDict["status"] = 1
					constInfo.autoHuntAutoLoginDict["leftTime"] = 0
					constInfo.autoHuntAutoLoginDict["skillDict"] = self.__children["skillDict"] if self.__children.has_key("skillDict") else {}
					constInfo.autoHuntAutoLoginDict["newOptions"] = self.__children["newOptions"]
					slotItemDict = self.__children["slotItemDict"] if self.__children.has_key("slotItemDict") else {}
					for key, itemIdx in slotItemDict.items():
						constInfo.autoHuntAutoLoginDict["slotStatus"][key] = self.__children["slotStatus" + str(key)] if self.__children.has_key("slotStatus" + str(key)) else False

		self.__children = {}


	def __LoadWindow(self):
		self.Destroy()

		self.AddFlag("float")
		self.AddFlag("movable")
		self.SetTitleName("Otomatik Farm [O]")
		self.SetCloseEvent(self.Close)

		bg = CreateWindow(ui.ImageBox(), self, (8, 29), IMG_DIR+"thin_bg.png")
		bg.AddFlag("attach")
		self.__children["bg"] = bg

		# slotItemDict = {
			# 0 : 50821,
			# 1 : 50822,
			# 2 : 50825,
			# 3 : 50826,
		# }

		slotItemDict = {
			0 : 50821,
			1 : 50822,
			2 : 50825,
			3 : 50826,
			4 : 71430,
			5 : 71431,
			6 : 71432,
			7 : 71433,
			8 : 71434,
			9 : 71435,
			10 : 27112,
			11 : 27115,
		}

		iconCountX = 0
		iconCountY = 0
		for key, itemIdx in slotItemDict.items():
			item.SelectItem(itemIdx)
			itemImg = CreateWindow(ui.ImageBox(), bg, (20 + (iconCountX * 51), 10 + (iconCountY * 48)), item.GetIconImageFileName())
			itemImg.SAFE_SetStringEvent("MOUSE_OVER_IN",self.__OverInItem, itemIdx)
			itemImg.SAFE_SetStringEvent("MOUSE_OVER_OUT",self.__OverOut)
			itemImg.SetEvent(self.__ClickStatus, "mouse_click", key)
			self.__children["itemImg"+str(key)] = itemImg

			status = CreateWindow(ui.ImageBox(), itemImg, (itemImg.GetWidth() - 34, itemImg.GetHeight() - 34), "otomatik_av/tick_item_1.png")
			status.SetEvent(self.__ClickStatus, "mouse_click", key)
			self.__children["status"+str(key)] = status

			iconCountX += 1
			if iconCountX == 4:
				iconCountX = 0
				iconCountY += 1

		self.__children["slotItemDict"] = slotItemDict

		slot = CreateWindow(ui.SlotWindow(), bg, (10, 31), "", "", (205, 32))
		slot.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectSlot))
		slot.SetSelectItemSlotEvent(ui.__mem_func__(self.__ClickSkillSlot))
		slot.SetUnselectItemSlotEvent(ui.__mem_func__(self.__ClickSkillSlot))
		slot.SetUseSlotEvent(ui.__mem_func__(self.__ClickSkillSlot))
		for j in xrange(6):
			slot.AppendSlot(j, (j * 35), 0, 32, 32)
		slot.SetOverInItemEvent(ui.__mem_func__(self.__OverInSkill))
		slot.SetOverOutItemEvent(ui.__mem_func__(self.__OverOut))
		try:
			import wndMgr
			wndMgr.SetSlotUnitSize(slot.hWnd, 40, 40)
		except:
			pass
		slot.Hide()
		self.__children["slot"] = slot

		startBtn = CreateWindow(ui.RadioButton(), bg, (-80, 290), "", "horizontal:center")
		startBtn.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		startBtn.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		startBtn.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		startBtn.SetEvent(self.__StartBtn)
		startBtn.SetText("Baþlat")
		self.__children["startBtn"] = startBtn
		try:
			startBtn.SetButtonScale(1.25, 1.25)
		except:
			pass


		stopBtn = CreateWindow(ui.RadioButton(), bg, (20, 290), "", "horizontal:center")
		stopBtn.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		stopBtn.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		stopBtn.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		stopBtn.SetEvent(self.__StopBtn)
		stopBtn.SetText("Durdur")
		self.__children["stopBtn"] = stopBtn
		try:
			stopBtn.SetButtonScale(1.25, 1.25)
		except:
			pass

		sliderBar = CreateWindow(ui.SliderBar(), bg, (-20, 225), "", "horizontal:center")
		sliderBar.SetEvent(ui.__mem_func__(self.__OnChangeRange))
		self.__children["sliderBar"] = sliderBar

		###################################################################################

		self.Board = ui.Board()
		self.Board.SetSize(300, 75)
		self.Board.SetCenterPosition()
		self.Board.SetParent(bg)
		self.Board.SetPosition(-5,-100)
		self.Board.AddFlag('float')
		self.Board.Show()


		self.__children["Bilgi1"] = CreateWindow(ui.TextLine(), self.Board, (25, 7), "OtoAv sistemi 7/24 aktif þekilde kullanýlabilir.")
		self.__children["Bilgi2"] = CreateWindow(ui.TextLine(), self.Board, (25, 22), "Sadece tek bir oyun penceresinde (client) çalýþýr.")
		self.__children["Bilgi3"] = CreateWindow(ui.TextLine(), self.Board, (25, 37), "Baþlat ve durdur iþlemlerini dilediðiniz zaman yapabilirsiniz.")
		self.__children["Bilgi4"] = CreateWindow(ui.TextLine(), self.Board, (25, 52), "Herhangi bir günlük sýnýrlama veya süre kýsýtlamasý yoktur.")


		self.__children["mobFarmCheckBox"] = CreateWindow(ui.ImageBox(), bg, (15, 215), "otomatik_av/sec_1.png")
		self.__children["mobFarmCheckBox"].SetEvent(ui.__mem_func__(self.__ClickOption), "mouse_click", "mob")
		self.__children["mobFarmText"] = CreateWindow(ui.TextLine(), bg, (40, 215), "Canavar Avý")

		self.__children["stoneFarmCheckBox"] = CreateWindow(ui.ImageBox(), bg, (125, 215), "otomatik_av/sec_1.png")
		self.__children["stoneFarmCheckBox"].SetEvent(ui.__mem_func__(self.__ClickOption), "mouse_click", "stone")
		self.__children["stoneFarmText"] = CreateWindow(ui.TextLine(), bg, (145, 215), "Metin Farm")

		self.__children["autoLoginCheckBox"] = CreateWindow(ui.ImageBox(), bg, (60, 242), "otomatik_av/sec_1.png")
		self.__children["autoLoginCheckBox"].SetEvent(ui.__mem_func__(self.__ClickOption), "mouse_click", "auto_login")
		self.__children["autoLoginText"] = CreateWindow(ui.TextLine(), bg, (60+25, 242), "Otomatik Giriþ")

		self.__children["disableRangeCheckBox"] = CreateWindow(ui.ImageBox(), bg, (60, 267), "otomatik_av/sec_1.png")
		self.__children["disableRangeCheckBox"].SetEvent(ui.__mem_func__(self.__ClickOption), "mouse_click", "disable_range")
		self.__children["disableRangeText"] = CreateWindow(ui.TextLine(), bg, (60+25, 267), "Menzili Devredýþý Býrak")

		self.__children["huntBilgilendirmeImage"] = CreateWindow(ui.ImageBox(), bg, (40, 185), "otomatik_av/list_bg.png")

		self.__children["huntBilgilendirme2"] = CreateWindow(ui.TextLine(), self.__children["huntBilgilendirmeImage"], (80, 5), "", "horizontal:center")
		self.__children["huntBilgilendirme2"].SetFontName("Arial:14")
		self.__children["huntBilgilendirme2"].SetFeather()
		self.__children["huntBilgilendirme2"].SetOutline()

		self.__children["huntTimeImage"] = CreateWindow(ui.ImageBox(), bg, (15, 150), "otomatik_av/time_bg.png")

		self.__children["huntTime"] = CreateWindow(ui.TextLine(), self.__children["huntTimeImage"], (108, 10), "", "horizontal:center")
		self.__children["huntTime"].SetFontName("Arial:14")
		self.__children["huntTime"].SetFeather()
		self.__children["huntTime"].SetOutline()

		self.__children["huntDie"] = CreateWindow(ui.TextLine(), self.__children["huntTimeImage"], (100,38), "", "horizontal:center")
		self.__children["huntDie"].SetFontName("Arial:14")
		self.__children["huntDie"].SetFeather()
		self.__children["huntDie"].SetOutline()

		self.__children["mobRange"] = RANGE_CIRCLE
		self.__OnChangeRange()

		self.__children["newOptions"] = {
			"disable_range" : 1,
			"auto_login" : 1,
			"stone" : 1,
			"mob" : 0,
		}

		self.SetCenterPosition()

	def __ClickOption(self, emptyArg, option):
		if self.IsActive():
			chat.AppendChat(chat.CHAT_TYPE_INFO, "<Sistem> Önce oto avý devre dýþý býrakmalýsýn.")
			return

		self.__children["newOptions"][option] = 1 if not self.__children["newOptions"][option] else 0
		self.Refresh()

	def Refresh(self):
		slotItemDict = self.__children["slotItemDict"] if self.__children.has_key("slotItemDict") else {}
		for key, itemIdx in slotItemDict.items():
			slotStatus = self.__children["slotStatus" + str(key)] if self.__children.has_key("slotStatus" + str(key)) else False
			self.__children["status"+str(key)].LoadImage("otomatik_av/tick_item_1.png" if slotStatus else "otomatik_av/tick_item_2.png")

		bg = self.__children["bg"]

		miniMap.SetAutoHuntRangeStatus(True)

		self.__children["autoLoginCheckBox"].LoadImage("otomatik_av/sec_2.png" if self.__children["newOptions"]["auto_login"] else "otomatik_av/sec_1.png")
		self.__children["disableRangeCheckBox"].LoadImage("otomatik_av/sec_2.png" if self.__children["newOptions"]["disable_range"] else "otomatik_av/sec_1.png")

		player.SetAutoHuntRangeStatus(int(self.__children["newOptions"]["disable_range"]))
		player.SetAutoHuntRespawnStatus(int(self.__children["newOptions"]["auto_login"]))

		self.__children["mobFarmCheckBox"].Hide()
		self.__children["mobFarmCheckBox"].LoadImage("otomatik_av/sec_2.png" if self.__children["newOptions"]["mob"] else "otomatik_av/sec_1.png")
		self.__children["mobFarmText"].Hide()

		self.__children["stoneFarmCheckBox"].Hide()
		self.__children["stoneFarmCheckBox"].LoadImage("otomatik_av/sec_2.png" if self.__children["newOptions"]["stone"] else "otomatik_av/sec_1.png")
		self.__children["stoneFarmText"].Hide()
		#########################################

		self.SetSize(8 + bg.GetWidth() + 8, 29 + bg.GetHeight() + 10)

		slot = self.__children["slot"]
		skillDict = self.__children["skillDict"] if self.__children.has_key("skillDict") else {}
		for j in xrange(6):
			slot.ClearSlot(j)

			if not skillDict.has_key(j):
				continue

			slotNumber = skillDict[j]
			(skillIndex, skillGrade, skillLevel) = (player.GetSkillIndex(slotNumber), player.GetSkillGrade(slotNumber), player.GetSkillLevel(slotNumber))
			slot.SetSkillSlotNew(j, skillIndex, skillGrade, skillLevel)
			slot.SetSlotCountNew(j, skillGrade, skillLevel)

		slot.RefreshSlot()

		activeStatus = self.IsActive()
		self.__children["startBtn" if activeStatus else "stopBtn"].Down()
		self.__children["startBtn" if not activeStatus else "stopBtn"].SetUp()

	def CheckAutoLogin(self):
		autoHuntAutoLoginDict = constInfo.autoHuntAutoLoginDict
		if autoHuntAutoLoginDict["status"] == 1:
			constInfo.autoHuntAutoLoginDict["status"] = 0
			self.__children["skillDict"] = autoHuntAutoLoginDict["skillDict"]
			self.__children["slotStatus"] = autoHuntAutoLoginDict["slotStatus"]
			self.__children["newOptions"] = autoHuntAutoLoginDict["newOptions"]

			slotItemDict = self.__children["slotItemDict"] if self.__children.has_key("slotItemDict") else {}
			for key, itemIdx in slotItemDict.items():
				self.__children["slotStatus" + str(key)] = autoHuntAutoLoginDict["slotStatus"][key]

			self.Refresh()
			self.__StartBtn()

	def __OnChangeRange(self):
		if self.IsActive():
			chat.AppendChat(chat.CHAT_TYPE_INFO, "<Sistem> Önce oto avý devre dýþý býrakmalýsýn.")
			self.Refresh()
			return
		sliderBar = self.__children["sliderBar"]
		mobRange = ((1.0/RANGE_CIRCLE) * (sliderBar.GetSliderPos()*RANGE_CIRCLE)) * RANGE_CIRCLE
		self.__children["mobRange"] = mobRange
		miniMap.SetAutoHuntRange(mobRange)
		self.__children["sliderBar"].SetSliderPos((1.0/RANGE_CIRCLE) * mobRange if mobRange > 0 else 0.0)

	def IsActive(self):
		return self.__children["activeStatus"] if self.__children.has_key("activeStatus") else False

	def SetStatus(self, status):
		self.__children["activeStatus"] = status
		self.Refresh()

	def __StartBtn(self):
		if self.IsActive():
			self.Refresh()
			return

		self.__children["huntTime"].Show()
		self.__children["huntDie"].Show()

		self.__children["huntBilgilendirme2"].Hide()

		selectedItemText = ""
		selectedSkillText = ""
		slotItemDict = self.__children["slotItemDict"] if self.__children.has_key("slotItemDict") else {}
		for key, itemIdx in slotItemDict.items():
			if selectedItemText != "":
				selectedItemText += "?"
			selectedItemText += "1" if (self.__children["slotStatus" + str(key)] if self.__children.has_key("slotStatus" + str(key)) else False) else "0"
		if selectedItemText == "":
			selectedItemText = "empty"

		skillDict = self.__children["skillDict"] if self.__children.has_key("skillDict") else {}
		for key, skillSlotNumber in skillDict.items():
			if skillSlotNumber != -1:
				if selectedSkillText != "":
					selectedSkillText += "?"
				selectedSkillText += str(skillSlotNumber)
		if selectedSkillText == "":
			selectedSkillText = "empty"
		net.SendChatPacket("/auto_hunt start {} {} {} {} {}".format(selectedItemText, selectedSkillText, int(self.__children["mobRange"] if self.__children.has_key("mobRange") else 0.0), self.__children["newOptions"]["mob"], self.__children["newOptions"]["stone"]))
		self.Refresh()

	def __StopBtn(self):
		if not self.IsActive():
			self.Refresh()
			return
		self.__children["huntTime"].Show()
		self.__children["huntDie"].Hide()

		self.__children["huntBilgilendirme2"].Show()

		net.SendChatPacket("/auto_hunt end")
		self.Refresh()

	def __ClickStatus(self, emptyArg, slotIdx):
		if self.IsActive():
			chat.AppendChat(chat.CHAT_TYPE_INFO, "<Sistem> Önce oto avý devre dýþý býrakmalýsýn.")
			self.Refresh()
			return
		slotStatus = self.__children["slotStatus" + str(slotIdx)] if self.__children.has_key("slotStatus" + str(slotIdx)) else False
		self.__children["slotStatus" + str(slotIdx)] = not slotStatus
		self.Refresh()

	def __ClickSkillSlot(self, slotIndex):
		if self.IsActive():
			self.Refresh()
			return
		skillDict = self.__children["skillDict"] if self.__children.has_key("skillDict") else {}
		if not skillDict.has_key(slotIndex):
			return
		self.__children["skillDict"][slotIndex] = -1
		self.Refresh()

	def SelectSlot(self, slotIndex):
		if self.IsActive():
			self.Refresh()
			return
		if TRUE != mouseModule.mouseController.isAttached():
			return
		attachedSlotType = mouseModule.mouseController.GetAttachedType()
		if attachedSlotType == player.SLOT_TYPE_SKILL:
			attachedSlotNumber = mouseModule.mouseController.GetAttachedSlotNumber()
			skillDict = self.__children["skillDict"] if self.__children.has_key("skillDict") else {}
			for key, skillSlotNumber in skillDict.items():
				if skillSlotNumber == attachedSlotNumber:
					skillDict[key] = -1
					break
			skillDict[slotIndex] = attachedSlotNumber
			self.__children["skillDict"] = skillDict
			self.Refresh()
		mouseModule.mouseController.DeattachObject()

	def __OverInSkill(self, index):
		skillDict = self.__children["skillDict"] if self.__children.has_key("skillDict") else {}
		if not skillDict.has_key(index):
			return
		skillNumber = skillDict[index]
		interface = constInfo.GetInterfaceInstance()
		if interface:
			if interface.tooltipSkill:
				interface.tooltipSkill.SetSkillNew(skillNumber, player.GetSkillIndex(skillNumber), player.GetSkillGrade(skillNumber), player.GetSkillLevel(skillNumber))

	def __OverInItem(self, itemIdx):
		interface = constInfo.GetInterfaceInstance()
		if interface:
			if interface.tooltipItem:
				interface.tooltipItem.SetItemToolTip(itemIdx)

	def __OverOut(self):
		interface = constInfo.GetInterfaceInstance()
		if interface:
			if interface.tooltipItem:
				interface.tooltipItem.HideToolTip()
			if interface.tooltipSkill:
				interface.tooltipSkill.HideToolTip()

	def Open(self):
		self.Refresh()
		self.SetCenterPosition()
		self.Show()
		self.SetTop()

	def Close(self):
		miniMap.SetAutoHuntRangeStatus(False)
		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnUpdate(self):
		if self.IsActive():
			# huntTime yazýsý güncellensin ve görünür olsun
			if "huntTime" in self.__children:
				self.__children["huntTime"].SetText("Süresiz Oto Av")
				self.__children["huntTime"].SetFontName("Arial:14")
				self.__children["huntTime"].SetPosition(100, 10)
				self.__children["huntTime"].Show()
	
			# Kesilen canavar ve metin sayýsýný göster
			if self.__children["newOptions"]["mob"] and self.__children["newOptions"]["stone"]:
				self.__children["huntDie"].SetText("%d canavar, %d metin kesildi." % (
					player.AutoHuntGetEnemyCount(), player.AutoHuntGetStoneCount()))
			elif self.__children["newOptions"]["mob"]:
				self.__children["huntDie"].SetText("%d canavar kesildi." % (player.AutoHuntGetEnemyCount()))
			elif self.__children["newOptions"]["stone"]:
				self.__children["huntDie"].SetText("Toplam %d metin kýrýldý." % (player.AutoHuntGetStoneCount()))
		else:
			# Baþlatýlmamýþsa bilgilendirme metnini göster
			if "huntBilgilendirme2" in self.__children:
				self.__children["huntBilgilendirme2"].SetText("Kýrýlan Metin Sayýsý")

def CreateWindow(window, parent, windowPos, windowArgument = "", windowPositionRule = "", windowSize = (-1, -1), windowFontName = -1):
	window.SetParent(parent)
	window.SetPosition(*windowPos)
	if windowSize != (-1, -1):
		window.SetSize(*windowSize)
	if windowPositionRule:
		splitList = windowPositionRule.split(":")
		if len(splitList) == 2:
			(type, mode) = (splitList[0], splitList[1])
			if type == "horizontal":
				if isinstance(window, ui.TextLine):
					if mode == "center":
						window.SetHorizontalAlignCenter()
					elif mode == "right":
						window.SetHorizontalAlignRight()
					elif mode == "left":
						window.SetHorizontalAlignLeft()
				else:
					if mode == "center":
						window.SetWindowHorizontalAlignCenter()
					elif mode == "right":
						window.SetWindowHorizontalAlignRight()
					elif mode == "left":
						window.SetWindowHorizontalAlignLeft()
			elif type == "vertical":
				if isinstance(window, ui.TextLine):
					if mode == "center":
						window.SetVerticalAlignCenter()
					elif mode == "top":
						window.SetVerticalAlignTop()
					elif mode == "bottom":
						window.SetVerticalAlignBottom()
				else:
					if mode == "top":
						window.SetWindowVerticalAlignTop()
					elif mode == "center":
						window.SetWindowVerticalAlignCenter()
					elif mode == "bottom":
						window.SetWindowVerticalAlignBottom()
	if windowArgument:
		if isinstance(window, ui.TextLine):
			if windowFontName != -1:
				window.SetFontName(windowFontName)
			window.SetText(windowArgument)
		elif isinstance(window, ui.NumberLine):
			window.SetNumber(windowArgument)
		elif isinstance(window, ui.ExpandedImageBox) or isinstance(window, ui.ImageBox):
			window.LoadImage(windowArgument if windowArgument.find("gr2") == -1 else "icon/item/27995.tga")
	window.Show()
	return window
