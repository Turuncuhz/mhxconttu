# Cynex: barbaros ui.py'ye dokunmadan mobil dokunma eklentileri
import app
import wndMgr
import ui

import uiMobileLocale


def IsMobile():
	function = getattr(app, "IsMobile", None)
	if function is None:
		return False
	try:
		return bool(function())
	except Exception:
		return False


def EnableSingleTap(window):
	if hasattr(wndMgr, "SetTekDokunus") and window and getattr(window, "hWnd", None) is not None:
		wndMgr.SetTekDokunus(window.hWnd, 1)


def SetTouchNative(window, enable = True):
	if hasattr(wndMgr, "SetTouchNative") and window and getattr(window, "hWnd", None) is not None:
		wndMgr.SetTouchNative(window.hWnd, 1 if enable else 0)


# Cynex: motor yalniz ornekte OnTouch* olan pencereyi sahiplenir; sinif metodu olsaydi her pencere sahiplenirdi
def _SetTouchTapEvent(self, event):
	self.eventTouchTap = event
	self.OnTouchTap = ui.__mem_func__(self._CynexTouchTap)


def _SetTouchLongPressEvent(self, event):
	self.eventTouchLongPress = event
	self.OnTouchLongPress = ui.__mem_func__(self._CynexTouchLongPress)


def _SetTouchLongPressCancelEvent(self, event):
	self.eventTouchLongPressCancel = event
	self.OnTouchLongPressCancel = ui.__mem_func__(self._CynexTouchLongPressCancel)


def _ClearTouchEvents(self):
	for name in ("OnTouchTap", "OnTouchLongPress", "OnTouchLongPressCancel"):
		if name in self.__dict__:
			del self.__dict__[name]
	self.eventTouchTap = None
	self.eventTouchLongPress = None
	self.eventTouchLongPressCancel = None


def _CynexTouchTap(self, x, y):
	event = getattr(self, "eventTouchTap", None)
	if event:
		event(x, y)


def _CynexTouchLongPress(self, x, y):
	event = getattr(self, "eventTouchLongPress", None)
	if event:
		event(x, y)


def _CynexTouchLongPressCancel(self):
	event = getattr(self, "eventTouchLongPressCancel", None)
	if event:
		event()


def _SetTapItemEvent(self, event, *args):
	self.eventTapItem = event
	self.eventTapItemArgs = args
	self.OnTapItem = ui.__mem_func__(self._CynexTapItem)


def _SetTapEmptySlotEvent(self, event, *args):
	self.eventTapEmptySlot = event
	self.eventTapEmptySlotArgs = args
	self.OnTapEmptySlot = ui.__mem_func__(self._CynexTapEmptySlot)


def _SetLongPressItemEvent(self, event, *args):
	self.eventLongPressItem = event
	self.eventLongPressItemArgs = args
	self.OnLongPressItem = ui.__mem_func__(self._CynexLongPressItem)


def _SetLongPressEmptySlotEvent(self, event, *args):
	self.eventLongPressEmptySlot = event
	self.eventLongPressEmptySlotArgs = args
	self.OnLongPressEmptySlot = ui.__mem_func__(self._CynexLongPressEmptySlot)


def _CynexTapItem(self, slotNumber):
	event = getattr(self, "eventTapItem", None)
	if event:
		event(slotNumber, *getattr(self, "eventTapItemArgs", ()))


def _CynexTapEmptySlot(self, slotNumber):
	event = getattr(self, "eventTapEmptySlot", None)
	if event:
		event(slotNumber, *getattr(self, "eventTapEmptySlotArgs", ()))


def _CynexLongPressItem(self, slotNumber):
	event = getattr(self, "eventLongPressItem", None)
	if event:
		event(slotNumber, *getattr(self, "eventLongPressItemArgs", ()))


def _CynexLongPressEmptySlot(self, slotNumber):
	event = getattr(self, "eventLongPressEmptySlot", None)
	if event:
		event(slotNumber, *getattr(self, "eventLongPressEmptySlotArgs", ()))


def _SetSlotScale(self, slotIndex, itemIndex, width, height, icon, sx, sy, diffuseColor = (1.0, 1.0, 1.0, 1.0)):
	if hasattr(wndMgr, "SetSlotScale"):
		wndMgr.SetSlotScale(self.hWnd, slotIndex, itemIndex, width, height, icon, diffuseColor, sx, sy)
	else:
		wndMgr.SetSlot(self.hWnd, slotIndex, itemIndex, width, height, icon, diffuseColor)


def Install():
	window = ui.Window
	if getattr(window, "_cynexTouchInstalled", False):
		return
	window._cynexTouchInstalled = True
	window.SetTouchTapEvent = _SetTouchTapEvent
	window.SetTouchLongPressEvent = _SetTouchLongPressEvent
	window.SetTouchLongPressCancelEvent = _SetTouchLongPressCancelEvent
	window.ClearTouchEvents = _ClearTouchEvents
	window._CynexTouchTap = _CynexTouchTap
	window._CynexTouchLongPress = _CynexTouchLongPress
	window._CynexTouchLongPressCancel = _CynexTouchLongPressCancel

	slot = ui.SlotWindow
	slot.SetTapItemEvent = _SetTapItemEvent
	slot.SetTapEmptySlotEvent = _SetTapEmptySlotEvent
	slot.SetLongPressItemEvent = _SetLongPressItemEvent
	slot.SetLongPressEmptySlotEvent = _SetLongPressEmptySlotEvent
	slot._CynexTapItem = _CynexTapItem
	slot._CynexTapEmptySlot = _CynexTapEmptySlot
	slot._CynexLongPressItem = _CynexLongPressItem
	slot._CynexLongPressEmptySlot = _CynexLongPressEmptySlot
	if not hasattr(slot, "SetSlotScale"):
		slot.SetSlotScale = _SetSlotScale

	# Enable single-tap on all TitleBar close buttons so windows close on first tap
	titleBarClass = getattr(ui, "TitleBar", None)
	if titleBarClass:
		origMakeTitleBar = getattr(titleBarClass, "MakeTitleBar", None)
		if origMakeTitleBar:
			def HookedMakeTitleBar(self, width, color):
				origMakeTitleBar(self, width, color)
				if getattr(self, "btnClose", None):
					self.btnClose.OnTouchTap = ui.__mem_func__(self.btnClose.CallEvent)
					EnableSingleTap(self.btnClose)
				EnableSingleTap(self)
			titleBarClass.MakeTitleBar = HookedMakeTitleBar

	# Enable single-tap on all ScriptWindow instances
	scriptWindowClass = getattr(ui, "ScriptWindow", None)
	if scriptWindowClass:
		origScriptWindowInit = getattr(scriptWindowClass, "__init__", None)
		if origScriptWindowInit:
			def HookedScriptWindowInit(self, layer = "UI"):
				origScriptWindowInit(self, layer)
				EnableSingleTap(self)
			scriptWindowClass.__init__ = HookedScriptWindowInit

	# Global single-tap button dispatcher: enables 1-tap activation on ALL buttons in the game
	def _GlobalButtonOnTouchTap(self, x = 0, y = 0):
		if not self.IsShow():
			return
		if hasattr(self, "IsEnable") and not self.IsEnable():
			return
		self.CallEvent()

	buttonClass = getattr(ui, "Button", None)
	if buttonClass:
		buttonClass.OnTouchTap = _GlobalButtonOnTouchTap
		origButtonInit = getattr(buttonClass, "__init__", None)
		if origButtonInit:
			def HookedButtonInit(self, layer = "UI"):
				origButtonInit(self, layer)
				self.OnTouchTap = ui.__mem_func__(self._GlobalButtonOnTouchTap)
				EnableSingleTap(self)
			buttonClass.__init__ = HookedButtonInit
			buttonClass._GlobalButtonOnTouchTap = _GlobalButtonOnTouchTap

	rbClass = getattr(ui, "RadioButton", None)
	if rbClass:
		rbClass.OnTouchTap = _GlobalButtonOnTouchTap

	tbClass = getattr(ui, "ToggleButton", None)
	if tbClass:
		tbClass.OnTouchTap = _GlobalButtonOnTouchTap

	# Hook CharacterWindow methods at class level for mobile popup dialogs
	try:
		import uicharacter
		import player
		origSelectSkill = uicharacter.CharacterWindow.SelectSkill
		origOnPressedSlotButton = uicharacter.CharacterWindow.OnPressedSlotButton
		origClickSkillSlot = uicharacter.CharacterWindow.ClickSkillSlot
		origOnClickStatusPlusButton = uicharacter.CharacterWindow._CharacterWindow__OnClickStatusPlusButton

		def MobileSelectSkill(self, skillSlotIndex):
			try:
				srcSlotIndex = self._CharacterWindow__RealSkillSlotToSourceSlot(skillSlotIndex)
				skillIndex = player.GetSkillIndex(srcSlotIndex)
				skillGrade = player.GetSkillGrade(srcSlotIndex)
				curLevel = player.GetSkillLevel(srcSlotIndex)
				import skill
				maxLevel = skill.GetSkillMaxLevel(skillIndex) if skillIndex else 20
				statPoint = player.GetStatus(player.SKILL_ACTIVE)
				if srcSlotIndex > 8:
					statPoint = max(statPoint, player.GetStatus(player.SKILL_HORSE))
				if statPoint > 0 and skillGrade == 0 and curLevel < maxLevel and skillIndex > 0:
					import uimobilestatuspopup
					uimobilestatuspopup.OpenSkillPopup(skillIndex, srcSlotIndex)
					return
			except Exception:
				pass
			return origSelectSkill(self, skillSlotIndex)

		def MobileOnPressedSlotButton(self, slotNumber):
			try:
				srcSlotIndex = self._CharacterWindow__RealSkillSlotToSourceSlot(slotNumber)
				skillIndex = player.GetSkillIndex(srcSlotIndex)
				import uimobilestatuspopup
				uimobilestatuspopup.OpenSkillPopup(skillIndex, srcSlotIndex)
				return
			except Exception:
				pass
			return origOnPressedSlotButton(self, slotNumber)

		def MobileClickSkillSlot(self, slotIndex):
			try:
				srcSlotIndex = self._CharacterWindow__RealSkillSlotToSourceSlot(slotIndex)
				skillIndex = player.GetSkillIndex(srcSlotIndex)
				skillGrade = player.GetSkillGrade(srcSlotIndex)
				curLevel = player.GetSkillLevel(srcSlotIndex)
				import skill
				maxLevel = skill.GetSkillMaxLevel(skillIndex) if skillIndex else 20
				statPoint = player.GetStatus(player.SKILL_ACTIVE)
				if srcSlotIndex > 8:
					statPoint = max(statPoint, player.GetStatus(player.SKILL_HORSE))
				if statPoint > 0 and skillGrade == 0 and curLevel < maxLevel and skillIndex > 0:
					import uimobilestatuspopup
					uimobilestatuspopup.OpenSkillPopup(skillIndex, srcSlotIndex)
					return
			except Exception:
				pass
			return origClickSkillSlot(self, slotIndex)

		def MobileOnClickStatusPlusButton(self, statusKey):
			try:
				import uimobilestatuspopup
				uimobilestatuspopup.OpenStatusPopup(statusKey)
				return
			except Exception:
				pass
			return origOnClickStatusPlusButton(self, statusKey)

		uicharacter.CharacterWindow.SelectSkill = MobileSelectSkill
		uicharacter.CharacterWindow.OnPressedSlotButton = MobileOnPressedSlotButton
		uicharacter.CharacterWindow.ClickSkillSlot = MobileClickSkillSlot
		uicharacter.CharacterWindow._CharacterWindow__OnClickStatusPlusButton = MobileOnClickStatusPlusButton
	except Exception:
		pass

	ui.EnableSingleTap = EnableSingleTap
	ui.IsMobileClient = IsMobile


Install()
