from __future__ import division
import app
import dbg
import grp
import math
import player
import skill
import systemSetting
import wndMgr
import mouseModule
import constInfo
import ui
import uiMobileCompat
import snd
import chat

from _weakref import proxy

DESKTOP_CAMERA_PITCH = 27.0
DEFAULT_CAMERA_PITCH = 14.0

JOYSTICK_DEFAULT_SIZE = 200
ATTACK_DEFAULT_SIZE = 140
ATTACK_GROWTH = 1.15

LEFT_MARGIN = 40
RIGHT_MARGIN = 24
BOTTOM_MARGIN = 20
TOP_MARGIN = 10
SCREEN_EDGE = 12
WINDOW_GAP = 8

INNER_SLOT_SIZE = 56
OUTER_SLOT_SIZE = 48
ROUND_ICON_RATIO = 0.72	# yuvarlak beceri ikonu / yuva capi (disk duz alani ~0.75)
PAGE_BUTTON_SIZE = 44
INNER_RING_GAP = 14
OUTER_RING_GAP = 18
INNER_ANGLES = (180.0, 210.0, 240.0, 270.0)
OUTER_ANGLES = (185.0, 210.0, 235.0, 260.0)
PAGE_BUTTON_ANGLE = 300.0
LOCK_BUTTON_ANGLE = 328.0
LOCK_BUTTON_SIZE = 34
QUICKSLOT_LOCKED = True

UTILITY_SIZE = 54
UTILITY_GAP = 6
UTILITY_COUNT = 4
TARGET_BUTTON_SIZE = 54
MINIMAP_RESERVED_WIDTH = 210
MINIMAP_RESERVED_HEIGHT = 200

STATUS_BAR_HEIGHT = 82
NOTIFICATION_GAP = 12
NOTIFICATION_HEIGHT = 48
MENU_BUTTON_SIZE = 60
MENU_BUTTON_GAP = 6
MENU_BUTTON_COUNT = 6
STATUS_BAR_WIDTH = 332
AFFECT_GAP = 6
AFFECT_ROW_HEIGHT = 44	# uiAffectShower MOBILE_IMAGE_STEP: 40 px ikon + 4 aralik

CHAT_PILL_WIDTH = 520
CHAT_PILL_MIN_WIDTH = 160
CHAT_PILL_HEIGHT = 40
CHAT_PILL_GAP = 16

RUN_LOCK_SIZE = 40
RUN_LOCK_GAP = 12

SLOT_ICON_SIZE = 32
SLOT_TEXTURE_SIZE = 64.0
DISC_TEXTURE = "mobile_ui/cynex/hud_disc.png"
RING_TEXTURE = "mobile_ui/cynex/hud_ring.png"
SLOT_KEY_LABELS = ("1", "2", "3", "4", "F1", "F2", "F3", "F4")
KEY_LABEL_HEIGHT = 16
KEY_PLATE_WIDTH = 26
KEY_PLATE_TEXTURE = "mobile_ui/cynex/hud_key_plate.png"
PAGE_TEXTURE = "mobile_ui/cynex/hud_page_%d.png"
PAGE_TEXTURE_SIZE = 44.0
KEY_LABEL_TEXT_COLOR = grp.GenerateColor(0.94, 0.81, 0.53, 1.0)

CONFIG_FILE_NAME = "mobile_hud.cfg"	# Cynex: config/ klasoru telefonda olmayabilir
CONFIG_DYNAMIC_JOYSTICK = "DYNAMIC_JOYSTICK"
CONFIG_SHOW_FPS = "SHOW_FPS"
CONFIG_LIVE_CHAT = "LIVE_CHAT"
CONFIG_TARGET_PRIORITY = "TARGET_PRIORITY"
CONFIG_CUSTOM_HUD = "mobile_hud_custom.json"

QUICK_PAGE_COUNT = 4

supportCache = None
enabledState = False
missingApiReported = False
refreshRequest = None
configCache = None


def IsSupported():
	global supportCache
	if supportCache is None:
		supportCache = getattr(app, "TOUCH_API_VERSION", 0) >= 1 and hasattr(systemSetting, "IsMobileHud")
	return supportCache


def Refresh():
	global enabledState, missingApiReported
	requested = False
	if hasattr(systemSetting, "IsMobileHud"):
		try:
			requested = bool(systemSetting.IsMobileHud())
		except Exception:
			requested = False

	if requested and not IsSupported():
		if not missingApiReported:
			missingApiReported = True
			dbg.TraceError("uiMobileHud: MOBIL_HUD is on but the client has no touch API, HUD disabled")
		requested = False

	enabledState = requested
	return enabledState


def IsEnabled():
	return enabledState


def SetEnabled(value):
	if hasattr(systemSetting, "SetMobileHud"):
		systemSetting.SetMobileHud(1 if int(value) else 0)
		systemSetting.SaveConfig()
	return Refresh()


def SetDoubleTapGate(enabled):
	if IsSupported() and hasattr(app, "SetIkiDokunusKapisi"):
		app.SetIkiDokunusKapisi(1 if enabled else 0)


def IsCameraMode():
	if hasattr(player, "IsCameraMode"):
		try:
			return bool(player.IsCameraMode())
		except Exception:
			return False
	return False


def IsCameraSettingSupported():
	return getattr(app, "TOUCH_API_VERSION", 0) >= 2


def GetCameraPitch():
	if IsCameraSettingSupported():
		try:
			return float(systemSetting.GetCameraReturnPitch())
		except Exception:
			pass
	return DESKTOP_CAMERA_PITCH


def BindRefreshRequest(function):
	global refreshRequest
	refreshRequest = function


def RequestRefresh():
	if refreshRequest is not None:
		try:
			refreshRequest()
		except ReferenceError:
			pass
	try:
		RefreshOpenWindowsScale()
	except Exception:
		pass


def IsSettingsCategoryVisible():
	if not IsSupported():
		return False
	try:
		return bool(systemSetting.IsMobileHud())
	except Exception:
		return False


def LoadConfig():
	global configCache
	if configCache is not None:
		return configCache

	configCache = {}
	try:
		for line in old_open(CONFIG_FILE_NAME, "r").read().splitlines():
			tokens = line.split()
			if len(tokens) == 2:
				configCache[tokens[0]] = tokens[1]
	except Exception:
		pass
	return configCache


def SaveConfig():
	config = LoadConfig()
	try:
		old_open(CONFIG_FILE_NAME, "w").write("".join("%s %s\n" % (key, value) for (key, value) in sorted(config.items())))
	except Exception:
		dbg.TraceError("uiMobileHud: cannot write %s" % CONFIG_FILE_NAME)


def IsDynamicJoystick():
	return LoadConfig().get(CONFIG_DYNAMIC_JOYSTICK, "0") == "1"


def SetDynamicJoystick(enabled):
	LoadConfig()[CONFIG_DYNAMIC_JOYSTICK] = "1" if enabled else "0"
	SaveConfig()


def IsLiveChatEnabled():
	return LoadConfig().get(CONFIG_LIVE_CHAT, "1") == "1"


def SetLiveChatEnabled(enabled):
	LoadConfig()[CONFIG_LIVE_CHAT] = "1" if enabled else "0"
	SaveConfig()


def GetTargetPriority():
	try:
		return int(LoadConfig().get(CONFIG_TARGET_PRIORITY, "0"))
	except Exception:
		return 0


def SetTargetPriority(priority):
	LoadConfig()[CONFIG_TARGET_PRIORITY] = str(int(priority))
	SaveConfig()


def LoadCustomHudPositions():
	try:
		import os, json, __builtin__
		if not os.path.exists(CONFIG_CUSTOM_HUD):
			return {}
		func = getattr(__builtin__, "old_open", open)
		return json.loads(func(CONFIG_CUSTOM_HUD, "r").read())
	except Exception:
		return {}


def SaveCustomHudPositions(positions):
	try:
		import json, __builtin__
		func = getattr(__builtin__, "old_open", open)
		func(CONFIG_CUSTOM_HUD, "w").write(json.dumps(positions))
	except Exception:
		pass


def ResetCustomHudPositions():
	try:
		import os
		if os.path.exists(CONFIG_CUSTOM_HUD):
			os.remove(CONFIG_CUSTOM_HUD)
	except Exception:
		pass


def IsShowFps():
	return LoadConfig().get(CONFIG_SHOW_FPS, "1") == "1"


def SetShowFps(enabled):
	LoadConfig()[CONFIG_SHOW_FPS] = "1" if enabled else "0"
	SaveConfig()


def GetScreenFactor(screenHeight):
	return max(1.0, screenHeight / 720.0)


def GetUIScale():
	function = getattr(wndMgr, "GetUIScale", None)
	if function is None:
		return 1.0
	try:
		scale = float(function())
	except Exception:
		return 1.0
	return scale if scale > 0.0 else 1.0


def GetSettingSize(getterName):
	function = getattr(systemSetting, getterName, None)
	if function is None:
		return 0
	try:
		size = float(function())
	except Exception:
		return 0
	if size <= 0.0:
		return 0
	return int(round(size / GetUIScale()))


def GetAttackSettingSize(drawnSize):
	size = int(drawnSize / ATTACK_GROWTH) + 1
	while size > 1 and int(size * ATTACK_GROWTH + 1e-6) > drawnSize:
		size -= 1
	return size


def PlaceOnRing(centerX, centerY, radius, angle, size):
	radians = math.radians(angle)
	x = int(round(centerX + radius * math.cos(radians) - size / 2.0))
	y = int(round(centerY + radius * math.sin(radians) - size / 2.0))
	return (x, y)



_hud_button_scale = 1.0
_menu_scale = 1.0
CONFIG_MOBILE_SCALES = "mobile_scales.json"
_hud_controller = None

def RegisterController(controller):
	global _hud_controller
	_hud_controller = controller

def GetController():
	return _hud_controller

def StartHudEditMode():
	if _hud_controller and hasattr(_hud_controller, "StartHudEditMode"):
		_hud_controller.StartHudEditMode()

def GetHudButtonScale():
	global _hud_button_scale
	return _hud_button_scale

def SetHudButtonScale(scale):
	global _hud_button_scale
	try:
		_hud_button_scale = max(0.6, min(1.6, float(scale)))
		SaveMobileScales()
	except Exception:
		pass

def GetMenuScale():
	global _menu_scale
	return _menu_scale

def SetMenuScale(scale):
	global _menu_scale
	try:
		_menu_scale = max(0.6, min(1.6, float(scale)))
		SaveMobileScales()
	except Exception:
		pass

_window_scale = 1.25

def GetWindowScale():
	global _window_scale
	return _window_scale

def SetWindowScale(scale):
	global _window_scale
	try:
		_window_scale = max(0.6, min(1.6, float(scale)))
		SaveMobileScales()
	except Exception:
		pass

def RefreshOpenWindowsScale():
	pass

def LoadMobileScales():
	global _hud_button_scale, _menu_scale, _window_scale
	try:
		cfg = LoadConfig()
		if "BUTTON_SCALE" in cfg:
			_hud_button_scale = float(cfg["BUTTON_SCALE"])
		if "MENU_SCALE" in cfg:
			_menu_scale = float(cfg["MENU_SCALE"])
		if "WINDOW_SCALE" in cfg:
			_window_scale = float(cfg["WINDOW_SCALE"])
		else:
			_window_scale = 1.25
	except Exception:
		_window_scale = 1.25

def SaveMobileScales():
	try:
		cfg = LoadConfig()
		cfg["BUTTON_SCALE"] = "%.2f" % _hud_button_scale
		cfg["MENU_SCALE"] = "%.2f" % _menu_scale
		cfg["WINDOW_SCALE"] = "%.2f" % _window_scale
		SaveConfig()
	except Exception:
		pass
	try:
		import __builtin__
		func = getattr(__builtin__, "old_open", open)
		f = func(CONFIG_MOBILE_SCALES, "w")
		f.write(json.dumps({
			"buttonScale": _hud_button_scale,
			"menuScale": _menu_scale,
			"windowScale": _window_scale
		}))
		f.close()
	except Exception:
		pass

LoadMobileScales()

def GetTouchLayout(screenWidth, screenHeight):
	btnScale = GetHudButtonScale()
	menuScale = GetMenuScale()
	factor = GetScreenFactor(screenHeight) * btnScale

	joystickSize = GetSettingSize("GetJoystickSize") or int(round(JOYSTICK_DEFAULT_SIZE * factor))
	attackBase = GetSettingSize("GetAttackButtonSize") or ATTACK_DEFAULT_SIZE * factor
	attackSize = int(attackBase * ATTACK_GROWTH + 1e-6)

	innerSize = int(round(INNER_SLOT_SIZE * factor))
	outerSize = int(round(OUTER_SLOT_SIZE * factor))
	pageSize = int(round(PAGE_BUTTON_SIZE * factor))
	utilitySize = int(round(UTILITY_SIZE * factor))

	joystickX = LEFT_MARGIN
	joystickY = screenHeight - BOTTOM_MARGIN - joystickSize

	attackX = screenWidth - RIGHT_MARGIN - attackSize
	attackY = screenHeight - BOTTOM_MARGIN - attackSize
	centerX = attackX + attackSize / 2.0
	centerY = attackY + attackSize / 2.0

	innerRadius = attackSize / 2.0 + innerSize / 2.0 + INNER_RING_GAP
	outerRadius = innerRadius + innerSize / 2.0 + outerSize / 2.0 + OUTER_RING_GAP

	slots = [(PlaceOnRing(centerX, centerY, innerRadius, angle, innerSize), innerSize) for angle in INNER_ANGLES]
	slots += [(PlaceOnRing(centerX, centerY, outerRadius, angle, outerSize), outerSize) for angle in OUTER_ANGLES]

	utilityX = screenWidth - SCREEN_EDGE - utilitySize
	utilities = [(utilityX, MINIMAP_RESERVED_HEIGHT + index * (utilitySize + UTILITY_GAP)) for index in range(UTILITY_COUNT)]

	affectY = TOP_MARGIN + STATUS_BAR_HEIGHT + AFFECT_GAP
	notificationY = affectY + AFFECT_ROW_HEIGHT + NOTIFICATION_GAP
	menuSize = int(round(MENU_BUTTON_SIZE * menuScale))
	menuGap = int(round(MENU_BUTTON_GAP * menuScale))
	menuWidth = MENU_BUTTON_COUNT * menuSize + (MENU_BUTTON_COUNT - 1) * menuGap

	ringLeft = centerX - outerRadius - outerSize / 2.0
	pillLeftLimit = joystickX + joystickSize + CHAT_PILL_GAP
	pillRightLimit = ringLeft - CHAT_PILL_GAP
	pillWidth = int(max(CHAT_PILL_MIN_WIDTH, min(CHAT_PILL_WIDTH, pillRightLimit - pillLeftLimit)))
	pillX = int((pillLeftLimit + pillRightLimit - pillWidth) / 2)
	pillY = screenHeight - BOTTOM_MARGIN - CHAT_PILL_HEIGHT

	zoneY = notificationY + NOTIFICATION_HEIGHT + NOTIFICATION_GAP

	targetSize = int(round(TARGET_BUTTON_SIZE * factor))
	targetDefaultX = attackX - targetSize - 12
	targetDefaultY = screenHeight - BOTTOM_MARGIN - targetSize

	customPos = LoadCustomHudPositions()
	if "joystick" in customPos:
		jx, jy = customPos["joystick"]
		if jy >= screenHeight * 0.4:
			joystickX, joystickY = jx, jy
	if "attack" in customPos:
		attackX, attackY = customPos["attack"]
		centerX = attackX + attackSize / 2.0
		centerY = attackY + attackSize / 2.0
		innerRadius = attackSize / 2.0 + innerSize / 2.0 + INNER_RING_GAP
		outerRadius = innerRadius + innerSize / 2.0 + outerSize / 2.0 + OUTER_RING_GAP
		slots = [(PlaceOnRing(centerX, centerY, innerRadius, angle, innerSize), innerSize) for angle in INNER_ANGLES]
		slots += [(PlaceOnRing(centerX, centerY, outerRadius, angle, outerSize), outerSize) for angle in OUTER_ANGLES]

	# Custom per-slot positions if user customized individual skill buttons
	for idx in range(len(slots)):
		key = "slot_%d" % idx
		if key in customPos:
			slots[idx] = ((customPos[key][0], customPos[key][1]), slots[idx][1])

	pageBtnPos = PlaceOnRing(centerX, centerY, innerRadius, PAGE_BUTTON_ANGLE, pageSize)
	if "slot_page" in customPos:
		pageBtnPos = (customPos["slot_page"][0], customPos["slot_page"][1])

	lockBtnSize = int(round(LOCK_BUTTON_SIZE * factor))
	rawLockPos = PlaceOnRing(centerX, centerY, innerRadius, LOCK_BUTTON_ANGLE, lockBtnSize)
	lockBtnX = min(screenWidth - lockBtnSize - 4, rawLockPos[0] - int(round(25 * factor)))
	lockBtnY = rawLockPos[1]
	lockBtnPos = (lockBtnX, lockBtnY)
	if "slot_lock" in customPos:
		lockBtnPos = (customPos["slot_lock"][0], customPos["slot_lock"][1])

	if "statusBar" in customPos:
		statusBarPos = tuple(customPos["statusBar"])
	else:
		statusBarPos = (SCREEN_EDGE, TOP_MARGIN)
	if "menuBar" in customPos:
		menuBarPos = (customPos["menuBar"][0], customPos["menuBar"][1], menuSize, menuGap)
	else:
		menuBarPos = (screenWidth - MINIMAP_RESERVED_WIDTH - WINDOW_GAP - menuWidth, TOP_MARGIN, menuSize, menuGap)
	if "chatPill" in customPos:
		pillX, pillY = customPos["chatPill"]
	if "utilities" in customPos:
		ux, uy = customPos["utilities"]
		utilities = [(ux, uy + index * (utilitySize + UTILITY_GAP)) for index in range(UTILITY_COUNT)]
	if "target" in customPos:
		targetX, targetY = customPos["target"]
	else:
		targetX, targetY = targetDefaultX, targetDefaultY

	return {
		"joystick" : (joystickX, joystickY, joystickSize),
		"attack" : (attackX, attackY, attackSize),
		"target" : (targetX, targetY, targetSize),
		"slots" : slots,
		"pageButton" : (pageBtnPos, pageSize),
		"lockButton" : (lockBtnPos, lockBtnSize),
		"utilities" : (utilities, utilitySize),
		"runLock" : (RUN_LOCK_SIZE, RUN_LOCK_GAP),
		"statusBar" : statusBarPos,
		"notificationY" : notificationY,
		"menuBar" : menuBarPos,
		"eventRow" : (screenWidth - MINIMAP_RESERVED_WIDTH - WINDOW_GAP, TOP_MARGIN + menuSize + WINDOW_GAP),
		"affectToggle" : (SCREEN_EDGE + STATUS_BAR_WIDTH + WINDOW_GAP, TOP_MARGIN + 4),
		"affectShower" : (SCREEN_EDGE, affectY),
		"chatPill" : (pillX, pillY, pillWidth, CHAT_PILL_HEIGHT),
		"joystickZone" : (0, zoneY, max(joystickX + joystickSize, pillX - WINDOW_GAP), screenHeight - zoneY),
	}


class SkillSlot(ui.Window):
	def __init__(self, slotIndex, size, taskBar):
		ui.Window.__init__(self, "UI")

		self.slotIndex = slotIndex
		self.taskBar = taskBar
		self.SetSize(size, size)
		self.SetWindowName("MobileSkillSlot%d" % slotIndex)
		self.AddFlag("float")	# SkillArc.SetTop: C paneli acikken onun ustunde
		ui.EnableSingleTap(self)

		iconSize = SLOT_ICON_SIZE
		if hasattr(wndMgr, "SetSlotUnitSize"):
			iconSize = max(SLOT_ICON_SIZE, int(size * ROUND_ICON_RATIO) // 2 * 2)
		iconOffset = (size - iconSize) // 2

		self.disc = self.__CreateImage(DISC_TEXTURE, size)

		self.slot = ui.GridSlotWindow()
		self.slot.SetParent(self)
		self.slot.AddFlag("not_pick")
		self.slot.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
		self.slot.ArrangeSlot(slotIndex, 1, 1, iconSize, iconSize, 0, 0)
		if iconSize != SLOT_ICON_SIZE:
			wndMgr.SetSlotUnitSize(self.slot.hWnd, iconSize, iconSize, 1)
		if uiMobileCompat.IsMobile() and hasattr(wndMgr, "SetSlotRoundIcons"):
			wndMgr.SetSlotRoundIcons(self.slot.hWnd, 1)
		self.slot.SetPosition(iconOffset, iconOffset)
		self.slot.SetSelectItemSlotEvent(ui.__mem_func__(self.__OnSlotSelect))
		self.slot.SetSelectEmptySlotEvent(ui.__mem_func__(self.__OnSlotEmptySelect))
		self.slot.SetUnselectItemSlotEvent(ui.__mem_func__(self.__OnSlotSelect))
		self.slot.SetUseSlotEvent(ui.__mem_func__(self.__OnSlotSelect))
		if hasattr(self.slot, "SetTapEmptySlotEvent"):
			self.slot.SetTapEmptySlotEvent(ui.__mem_func__(self.__OnSlotEmptySelect))
		if hasattr(self.slot, "SetTapItemEvent"):
			self.slot.SetTapItemEvent(ui.__mem_func__(self.__OnSlotSelect))
		ui.EnableSingleTap(self.slot)
		self.slot.Show()

		self.ring = self.__CreateImage(RING_TEXTURE, size)

		self.keyBack = ui.ImageBox()
		self.keyBack.SetParent(self)
		self.keyBack.AddFlag("not_pick")
		self.keyBack.LoadImage(KEY_PLATE_TEXTURE)
		self.keyText = ui.TextLine()
		self.keyText.SetParent(self)
		self.keyText.AddFlag("not_pick")
		self.keyText.SetPackedFontColor(KEY_LABEL_TEXT_COLOR)
		self.keyText.SetHorizontalAlignCenter()
		self.keyText.SetText(SLOT_KEY_LABELS[slotIndex % len(SLOT_KEY_LABELS)])
		keyWidth = KEY_PLATE_WIDTH
		keyX = size - keyWidth
		keyY = size - KEY_LABEL_HEIGHT
		self.keyBack.SetPosition(keyX, keyY)
		self.keyBack.Show()
		self.keyText.SetPosition(keyX + keyWidth // 2, keyY + 1)
		self.keyText.Show()

		self.cooldownText = ui.TextLine()
		self.cooldownText.SetParent(self)
		self.cooldownText.AddFlag("not_pick")
		self.cooldownText.SetOutline()
		self.cooldownText.SetHorizontalAlignCenter()
		self.cooldownText.SetPosition(size // 2, size // 2 - 7)
		self.cooldownText.Hide()
		self.cooldownValue = ""
		self.hasCooldownQuery = hasattr(self.slot, "GetSlotCoolTime")

		self.plusText = ui.TextLine()
		self.plusText.SetParent(self)
		self.plusText.AddFlag("not_pick")
		self.plusText.SetOutline()
		self.plusText.SetHorizontalAlignCenter()
		self.plusText.SetPosition(size // 2, size // 2 - 7)
		self.plusText.SetPackedFontColor(0xFFE0C060)
		self.plusText.SetText("+")
		self.plusText.Hide()

		self.SetTouchTapEvent(ui.__mem_func__(self.__OnTap))
		self.SetTouchLongPressEvent(ui.__mem_func__(self.__OnLongPress))

	def __del__(self):
		ui.Window.__del__(self)

	def __CreateImage(self, fileName, size):
		try:
			image = ui.ExpandedImageBox()
			image.SetParent(self)
			image.AddFlag("not_pick")
			image.LoadImage(fileName)
			image.SetScale(size / SLOT_TEXTURE_SIZE, size / SLOT_TEXTURE_SIZE)
			image.SetPosition(0, 0)
			image.Show()
			return image
		except Exception:
			return None

	def Destroy(self):
		self.taskBar = None
		self.eventTouchTap = None
		self.eventTouchLongPress = None
		self.disc = None
		self.slot = None
		self.ring = None
		self.keyBack = None
		self.keyText = None
		self.cooldownText = None
		self.plusText = None
		self.Hide()

	def __CallTaskBar(self, name, *args):
		if self.taskBar is None:
			return None
		try:
			return getattr(self.taskBar, name)(*args)
		except ReferenceError:
			return None

	def __OnSlotEmptySelect(self, *args):
		if mouseModule.mouseController.isAttached():
			self.__Drop()
			return
		try:
			import uimobilequickslotpopup
			uimobilequickslotpopup.OpenQuickSlotPicker(self.slotIndex)
		except Exception as e:
			dbg.TraceError("__OnSlotEmptySelect error: %s" % str(e))

	def __OnSlotSelect(self, *args):
		if mouseModule.mouseController.isAttached():
			self.__Drop()
			return
		(slotType, position) = player.GetLocalQuickSlot(self.slotIndex)
		if player.SLOT_TYPE_NONE == slotType:
			self.__OnSlotEmptySelect()
		else:
			if not QUICKSLOT_LOCKED:
				globalSlot = player.LocalQuickSlotIndexToGlobalQuickSlotIndex(self.slotIndex)
				player.RequestDeleteGlobalQuickSlot(globalSlot)
				snd.PlaySound("sound/ui/drop.wav")
				chat.AppendChat(chat.CHAT_TYPE_INFO, "<Yetenek Cubugu> Slot temizlendi.")
				self.RefreshContent()
			else:
				self.__Use()

	def __Use(self):
		player.RequestUseLocalQuickSlot(self.slotIndex)

	def __Take(self):
		(slotType, slotPosition) = player.GetLocalQuickSlot(self.slotIndex)
		if player.SLOT_TYPE_NONE == slotType:
			return
		self.__CallTaskBar("SelectItemQuickSlot", self.slotIndex)

	def __Drop(self):
		controller = mouseModule.mouseController
		if player.SLOT_TYPE_QUICK_SLOT == controller.GetAttachedType() \
				and controller.GetAttachedSlotNumber() == player.LocalQuickSlotIndexToGlobalQuickSlotIndex(self.slotIndex):
			controller.DeattachObject()
			return
		self.__CallTaskBar("AddQuickSlot", self.slotIndex)

	def __OnTap(self, x, y):
		if mouseModule.mouseController.isAttached():
			self.__Drop()
		else:
			(slotType, position) = player.GetLocalQuickSlot(self.slotIndex)
			if player.SLOT_TYPE_NONE == slotType:
				self.__OnSlotEmptySelect()
			else:
				if not QUICKSLOT_LOCKED:
					globalSlot = player.LocalQuickSlotIndexToGlobalQuickSlotIndex(self.slotIndex)
					player.RequestDeleteGlobalQuickSlot(globalSlot)
					snd.PlaySound("sound/ui/drop.wav")
					chat.AppendChat(chat.CHAT_TYPE_INFO, "<Yetenek Cubugu> Slot temizlendi.")
					self.RefreshContent()
				else:
					self.__Use()

	def __OnLongPress(self, x, y):
		if not QUICKSLOT_LOCKED:
			if not mouseModule.mouseController.isAttached():
				self.__Take()

	def OnMouseLeftButtonDown(self):
		if mouseModule.mouseController.isAttached():
			self.__Drop()
		elif (app.IsPressed(app.DIK_LSHIFT) or app.IsPressed(app.DIK_RSHIFT)) and not QUICKSLOT_LOCKED:
			self.__Take()
		else:
			(slotType, position) = player.GetLocalQuickSlot(self.slotIndex)
			if player.SLOT_TYPE_NONE == slotType:
				self.__OnSlotEmptySelect()
			else:
				if not QUICKSLOT_LOCKED:
					globalSlot = player.LocalQuickSlotIndexToGlobalQuickSlotIndex(self.slotIndex)
					player.RequestDeleteGlobalQuickSlot(globalSlot)
					snd.PlaySound("sound/ui/drop.wav")
					chat.AppendChat(chat.CHAT_TYPE_INFO, "<Yetenek Cubugu> Slot temizlendi.")
					self.RefreshContent()
				else:
					self.__Use()
		return True

	def OnMouseLeftButtonUp(self):
		if mouseModule.mouseController.isAttached() and wndMgr.IsDragging():
			if self.IsIn():
				self.__Drop()
				return True
			return False
		return True

	def OnMouseRightButtonDown(self):
		if mouseModule.mouseController.isAttached():
			mouseModule.mouseController.DeattachObject()
		else:
			self.__Use()
		return True

	def OnMouseOverIn(self):
		if not uiMobileCompat.IsMobile():
			self.__CallTaskBar("OverInItem", self.slotIndex)

	def OnMouseOverOut(self):
		self.__CallTaskBar("OverOutItem")

	def RefreshContent(self):
		index = self.slotIndex
		slot = self.slot
		(slotType, position) = player.GetLocalQuickSlot(index)

		if player.SLOT_TYPE_NONE == slotType:
			slot.ClearSlot(index)
			slot.RefreshSlot()
			if getattr(self, "plusText", None):
				self.plusText.Show()
			if getattr(self, "cooldownText", None):
				self.cooldownText.Hide()
			return

		if getattr(self, "plusText", None):
			self.plusText.Hide()

		if player.SLOT_TYPE_INVENTORY == slotType:
			itemIndex = player.GetItemIndex(position)
			itemCount = player.GetItemCount(position)
			if itemCount <= 1:
				itemCount = 0

			if constInfo.IS_AUTO_POTION(itemIndex):
				sockets = [player.GetItemMetinSocket(position, socket) for socket in range(player.METIN_SOCKET_MAX_NUM)]
				if 0 != int(sockets[0]):
					slot.ActivateSlot(index)
				else:
					slot.DeactivateSlot(index)

			slot.SetItemSlot(index, itemIndex, itemCount)

		elif player.SLOT_TYPE_SKILL == slotType:
			skillIndex = player.GetSkillIndex(position)
			if 0 == skillIndex:
				slot.ClearSlot(index)
			else:
				if skill.SKILL_TYPE_GUILD == skill.GetSkillType(skillIndex):
					import guild
					skillGrade = 0
					skillLevel = guild.GetSkillLevel(position)
				else:
					skillGrade = player.GetSkillGrade(position)
					skillLevel = player.GetSkillLevel(position)

				slot.SetSkillSlotNew(index, skillIndex, skillGrade, skillLevel)
				slot.SetSlotCountNew(index, skillGrade, skillLevel)

				if player.IsSkillCoolTime(position):
					(coolTime, elapsedTime) = player.GetSkillCoolTime(position)
					slot.SetSlotCoolTime(index, coolTime, elapsedTime)

				if player.IsSkillActive(position):
					slot.ActivateSlot(index)
				else:
					slot.DeactivateSlot(index)

		elif player.SLOT_TYPE_EMOTION == slotType:
			slot.SetEmotionSlot(index, position)
			slot.SetSlotCount(index, 0)

		slot.RefreshSlot()

	def IsSkillSlot(self, skillSlotIndex):
		(slotType, position) = player.GetLocalQuickSlot(self.slotIndex)
		return player.SLOT_TYPE_SKILL == slotType and skillSlotIndex == position

	def OnUpdate(self):
		if not self.hasCooldownQuery or not self.cooldownText:
			return

		remaining = 0.0
		try:
			(coolTime, elapsedTime) = self.slot.GetSlotCoolTime(self.slotIndex)
			if coolTime > 0.0:
				remaining = coolTime - elapsedTime
		except Exception:
			remaining = 0.0

		if remaining > 0.05:
			if remaining >= 10.0:
				text = "%d" % int(remaining + 0.999)
			else:
				text = "%.1f" % remaining
			if text != self.cooldownValue:
				self.cooldownValue = text
				self.cooldownText.SetText(text)
			if not self.cooldownText.IsShow():
				self.cooldownText.Show()
		elif self.cooldownText.IsShow():
			self.cooldownText.Hide()
			self.cooldownValue = ""


class QuickPageButton(ui.Window):
	def __init__(self, size):
		ui.Window.__init__(self, "UI")
		self.SetSize(size, size)
		self.SetWindowName("MobileQuickPageButton")
		self.AddFlag("float")
		ui.EnableSingleTap(self)

		self.faceScale = size / PAGE_TEXTURE_SIZE
		self.face = ui.ExpandedImageBox()
		self.face.SetParent(self)
		self.face.AddFlag("not_pick")
		self.face.LoadImage(PAGE_TEXTURE % 1)
		self.face.SetScale(self.faceScale, self.faceScale)
		self.face.Show()

		self.pageIndex = -1
		self.SetTouchTapEvent(ui.__mem_func__(self.__OnTap))
		self.Refresh()

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.eventTouchTap = None
		self.face = None
		self.Hide()

	def __NextPage(self):
		player.SetQuickPage((player.GetQuickPage() + 1) % QUICK_PAGE_COUNT)
		self.Refresh()

	def __OnTap(self, x, y):
		self.__NextPage()

	def OnMouseLeftButtonDown(self):
		self.__NextPage()
		return True

	def Refresh(self):
		pageIndex = player.GetQuickPage()
		if pageIndex == self.pageIndex:
			return
		self.pageIndex = pageIndex
		self.face.LoadImage(PAGE_TEXTURE % (pageIndex % QUICK_PAGE_COUNT + 1))
		self.face.SetScale(self.faceScale, self.faceScale)


class QuickSlotLockButton(ui.Window):
	def __init__(self, size):
		ui.Window.__init__(self, "UI")
		self.SetSize(size, size)
		self.SetWindowName("MobileQuickSlotLockButton")
		self.AddFlag("float")
		ui.EnableSingleTap(self)

		self.size = size
		self.face = ui.ExpandedImageBox()
		self.face.SetParent(self)
		self.face.AddFlag("not_pick")
		self.face.Show()

		self.__UpdateVisual()
		self.SetTouchTapEvent(ui.__mem_func__(self.__ToggleLock))

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.eventTouchTap = None
		self.face = None
		self.Hide()

	def __ToggleLock(self, *args):
		global QUICKSLOT_LOCKED
		QUICKSLOT_LOCKED = not QUICKSLOT_LOCKED
		self.__UpdateVisual()
		snd.PlaySound("sound/ui/click.wav")
		if QUICKSLOT_LOCKED:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "<Yetenek Cubugu> Kilitlendi. Skiller koruma altinda.")
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "<Yetenek Cubugu> Kilit acildi. Skile tiklayarak slotu silebilirsiniz.")

	def OnMouseLeftButtonDown(self):
		self.__ToggleLock()
		return True

	def __UpdateVisual(self):
		global QUICKSLOT_LOCKED
		img_path = "mobile_ui/cynex/quickslot_lock_closed.png" if QUICKSLOT_LOCKED else "mobile_ui/cynex/quickslot_lock_opened.png"
		self.face.LoadImage(img_path)
		scale = float(self.size) / 32.0
		self.face.SetScale(scale, scale)


class SkillArc(object):
	def __init__(self, taskBar, layout):
		self.slots = []
		weakTaskBar = proxy(taskBar)
		for (index, ((x, y), size)) in enumerate(layout["slots"]):
			slot = SkillSlot(index, size, weakTaskBar)
			slot.SetPosition(x, y)
			self.slots.append(slot)

		((x, y), size) = layout["pageButton"]
		self.pageButton = QuickPageButton(size)
		self.pageButton.SetPosition(x, y)

		((lx, ly), lsize) = layout["lockButton"]
		self.lockButton = QuickSlotLockButton(lsize)
		self.lockButton.SetPosition(lx, ly)

		self.RefreshQuickSlot()

	def Destroy(self):
		for slot in self.slots:
			slot.Destroy()
		self.slots = []
		if self.pageButton:
			self.pageButton.Destroy()
			self.pageButton = None
		if self.lockButton:
			self.lockButton.Destroy()
			self.lockButton = None

	def Show(self):
		for slot in self.slots:
			slot.Show()
		self.pageButton.Show()
		if self.lockButton:
			self.lockButton.Show()

	def Hide(self):
		for slot in self.slots:
			slot.Hide()
		self.pageButton.Hide()
		if self.lockButton:
			self.lockButton.Hide()

	def SetTop(self):
		for slot in self.slots:
			slot.SetTop()
		self.pageButton.SetTop()
		if self.lockButton:
			self.lockButton.SetTop()

	def RefreshQuickSlot(self):
		for slot in self.slots:
			slot.RefreshContent()
		if self.pageButton:
			self.pageButton.Refresh()

	def OnUseSkill(self, usedSlotIndex, coolTime):
		for slot in self.slots:
			if slot.IsSkillSlot(usedSlotIndex):
				slot.slot.SetSlotCoolTime(slot.slotIndex, coolTime)
				return

	def OnActivateSkill(self, usedSlotIndex):
		for slot in self.slots:
			if slot.IsSkillSlot(usedSlotIndex):
				slot.slot.ActivateSlot(slot.slotIndex)
				return

	def OnDeactivateSkill(self, usedSlotIndex):
		for slot in self.slots:
			if slot.IsSkillSlot(usedSlotIndex):
				slot.slot.DeactivateSlot(slot.slotIndex)
				return
