# -*- coding: cp1254 -*-
from __future__ import division
import app
import systemSetting
import wndMgr
import uiScriptLocale
import ui
import uiMobileHud
import uiMobileStyle
import dbg

PANEL_WIDTH = 540
PADDING = 24
TITLE_TOP = 20
ROW_TOP = 65
ROW_HEIGHT = 44
STEP_BUTTON = 40
STEP_SIGN_FONT = "AlegreyaSansBold:28"
VALUE_WIDTH = 100
CLOSE_SIZE = 30

ROWS = (
	("MOBILE_OPT_BUTTON_SCALE", "GetHudButtonScale", "SetHudButtonScale", 0.70, 1.50, 0.05, False, True),
	("MOBILE_OPT_MENU_SCALE", "GetMenuScale", "SetMenuScale", 0.70, 1.50, 0.05, False, True),
	("MOBILE_OPT_WINDOW_SCALE", "GetWindowScale", "SetWindowScale", 0.80, 1.60, 0.05, False, True),
	("MOBILE_OPT_CAMERA_PITCH", "GetCameraReturnPitch", "SetCameraReturnPitch", 0.0, 45.0, 1.0, False, False),
	("MOBILE_OPT_CAMERA_SENS", "GetCameraDragSens", "SetCameraDragSens", 0.25, 3.0, 0.25, False, False),
	("MOBILE_OPT_PINCH_SENS", "GetPinchZoomSens", "SetPinchZoomSens", 0.25, 3.0, 0.25, False, False),
	("MOBILE_OPT_JOYSTICK_SIZE", "GetJoystickSize", "SetJoystickSize", 80.0, 320.0, 20.0, True, True),
	("MOBILE_OPT_JOYSTICK_DEADZONE", "GetJoystickDeadZone", "SetJoystickDeadZone", 0.0, 0.5, 0.05, False, False),
	("MOBILE_OPT_ATTACK_SIZE", "GetAttackButtonSize", "SetAttackButtonSize", 80.0, 320.0, 20.0, True, True),
)


def Locale(name):
	if hasattr(uiScriptLocale, name):
		return getattr(uiScriptLocale, name)
	try:
		import uiMobileLocale
		return uiMobileLocale.STRINGS.get(name, name)
	except Exception:
		return name


class StepperRow(object):
	def __init__(self, parent, y, spec, owner):
		(self.labelName, self.getter, self.setter, self.low, self.high, self.step, self.allowAuto, self.rebuild) = spec
		self.owner = owner
		self.label = uiMobileStyle.CreateText(parent, Locale(self.labelName), PADDING, y + 12, uiMobileStyle.SOFT_COLOR, uiMobileStyle.FONT_MEDIUM)
		right = PANEL_WIDTH - PADDING
		self.plus = uiMobileStyle.PillButton(STEP_BUTTON, STEP_BUTTON - 6, "+", None, "field", uiMobileStyle.GOLD_COLOR, STEP_SIGN_FONT)
		self.plus.SetParent(parent)
		self.plus.SetPosition(right - STEP_BUTTON, y + 2)
		self.plus.SetEvent(ui.__mem_func__(self.__Change), 1)
		self.plus.Show()
		self.value = uiMobileStyle.CreateText(parent, "", right - STEP_BUTTON - VALUE_WIDTH // 2, y + 12, uiMobileStyle.BRIGHT_COLOR, uiMobileStyle.FONT_MEDIUM, "center")
		self.minus = uiMobileStyle.PillButton(STEP_BUTTON, STEP_BUTTON - 6, "-", None, "field", uiMobileStyle.GOLD_COLOR, STEP_SIGN_FONT)
		self.minus.SetParent(parent)
		self.minus.SetPosition(right - STEP_BUTTON * 2 - VALUE_WIDTH, y + 2)
		self.minus.SetEvent(ui.__mem_func__(self.__Change), -1)
		self.minus.Show()
		self.Refresh()

	def Destroy(self):
		if self.plus:
			self.plus.Destroy()
		if self.minus:
			self.minus.Destroy()
		self.plus = None
		self.minus = None
		self.label = None
		self.value = None
		self.owner = None

	def __Get(self):
		function = getattr(systemSetting, self.getter, None)
		if function is None:
			function = getattr(uiMobileHud, self.getter, None)
		if function is None:
			return 0.0
		try:
			return float(function())
		except Exception:
			return 0.0

	def __Change(self, direction):
		current = self.__Get()
		if self.allowAuto and current <= 0.0:
			current = self.low if direction > 0 else 0.0
		else:
			current += self.step * direction
			if self.allowAuto and current < self.low:
				current = 0.0
			else:
				current = max(self.low, min(self.high, current))
		function = getattr(systemSetting, self.setter, None)
		if function is None:
			function = getattr(uiMobileHud, self.setter, None)
		if function:
			function(current)
		if self.rebuild:
			uiMobileHud.RequestRefresh()
		self.Refresh()
		try:
			systemSetting.SaveConfig()
		except Exception:
			pass

	def Refresh(self):
		current = self.__Get()
		if self.allowAuto and current <= 0.0:
			text = Locale("MOBILE_OPT_AUTO")
			text = "%%%d" % int(round(current * 100))
		elif self.labelName == "MOBILE_OPT_CAMERA_PITCH":
			text = "%d" % int(round(current))
		elif self.labelName == "MOBILE_OPT_JOYSTICK_DEADZONE":
			text = "%%%d" % int(round(current * 100))
		elif self.step < 1.0:
			text = "x%.2f" % current
		else:
			text = "%d" % int(round(current))
		self.value.SetText(text)


class MobileSettingsDialog(ui.Window):
	def __init__(self):
		ui.Window.__init__(self, "TOP_MOST")
		self.rows = []
		self.toggles = []

		btnBarHeight = 40
		toggleCount = 3
		height = ROW_TOP + len(ROWS) * ROW_HEIGHT + toggleCount * 36 + btnBarHeight + PADDING * 2

		self.SetSize(PANEL_WIDTH, height)
		self.panel = uiMobileStyle.CreateOrnatePanel(self, 0, 0, PANEL_WIDTH, height)
		self.title = uiMobileStyle.CreateText(self, Locale("MOBILE_SETTINGS_TITLE"), PANEL_WIDTH // 2, TITLE_TOP, uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_LARGE, "center")

		self.closeButton = uiMobileStyle.StateImageButton("close_30")
		self.closeButton.SetParent(self)
		self.closeButton.SetPosition(PANEL_WIDTH - CLOSE_SIZE - 14, 14)
		self.closeButton.SetEvent(ui.__mem_func__(self.Close))
		self.closeButton.Show()

		y = ROW_TOP
		for spec in ROWS:
			self.rows.append(StepperRow(self, y, spec, self))
			y += ROW_HEIGHT

		y += 4
		self.cameraReturn = self.__AddToggle(Locale("MOBILE_OPT_CAMERA_RETURN"), bool(self.__Call("IsCameraReturn", 1)), self.__OnCameraReturn, y)
		y += 36
		self.dynamicJoystick = self.__AddToggle(Locale("MOBILE_OPT_DYNAMIC_JOYSTICK"), uiMobileHud.IsDynamicJoystick(), self.__OnDynamicJoystick, y)
		y += 36
		self.liveChatToggle = self.__AddToggle(Locale("MOBILE_OPT_LIVE_CHAT"), uiMobileHud.IsLiveChatEnabled(), self.__OnLiveChat, y)
		y += 42

		btnW = 160
		btnH = 34
		gap = 10
		totalW = btnW * 3 + gap * 2
		startX = (PANEL_WIDTH - totalW) // 2

		self.btnCustomizeHud = uiMobileStyle.PillButton(btnW, btnH, Locale("MOBILE_OPT_CUSTOMIZE_HUD"), None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_SMALL)
		self.btnCustomizeHud.SetParent(self)
		self.btnCustomizeHud.SetPosition(startX, y)
		self.btnCustomizeHud.SetEvent(ui.__mem_func__(self.__OnCustomizeHud))
		self.btnCustomizeHud.Show()

		self.btnResetHud = uiMobileStyle.PillButton(btnW, btnH, Locale("MOBILE_OPT_RESET_HUD_DEFAULT"), None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_SMALL)
		self.btnResetHud.SetParent(self)
		self.btnResetHud.SetPosition(startX + btnW + gap, y)
		self.btnResetHud.SetEvent(ui.__mem_func__(self.__OnResetHud))
		self.btnResetHud.Show()

		self.btnSystemMenu = uiMobileStyle.PillButton(btnW, btnH, Locale("MOBILE_OPT_SYSTEM_MENU"), None, "field", uiMobileStyle.SOFT_COLOR, uiMobileStyle.FONT_SMALL)
		self.btnSystemMenu.SetParent(self)
		self.btnSystemMenu.SetPosition(startX + (btnW + gap) * 2, y)
		self.btnSystemMenu.SetEvent(ui.__mem_func__(self.__OnSystemMenu))
		self.btnSystemMenu.Show()

		self.SetPosition((wndMgr.GetScreenWidth() - PANEL_WIDTH) // 2, max(6, (wndMgr.GetScreenHeight() - height) // 2))
		self.Hide()

	def __del__(self):
		ui.Window.__del__(self)

	def __Call(self, name, default):
		function = getattr(systemSetting, name, None)
		if function is None:
			return default
		try:
			return function()
		except Exception:
			return default

	def __AddToggle(self, text, value, event, y):
		toggle = uiMobileStyle.Toggle(text, value)
		toggle.SetParent(self)
		toggle.SetPosition(PADDING, y)
		toggle.SetChangeEvent(ui.__mem_func__(event))
		toggle.Show()
		self.toggles.append(toggle)
		return toggle

	def __OnCameraReturn(self, value):
		function = getattr(systemSetting, "SetCameraReturn", None)
		if function:
			function(1 if value else 0)

	def __OnDynamicJoystick(self, value):
		if value != uiMobileHud.IsDynamicJoystick():
			uiMobileHud.SetDynamicJoystick(value)
			uiMobileHud.RequestRefresh()

	def __OnLiveChat(self, value):
		uiMobileHud.SetLiveChatEnabled(value)

	def __OnCustomizeHud(self):
		self.Close()
		uiMobileHud.StartHudEditMode()

	def __OnResetHud(self):
		uiMobileHud.ResetCustomHudPositions()
		uiMobileHud.RequestRefresh()
		try:
			import chat
			chat.AppendChat(chat.CHAT_TYPE_INFO, Locale("MOBILE_HUD_RESET_DONE"))
		except Exception:
			pass

	def __OnSystemMenu(self):
		self.Close()
		ctrl = uiMobileHud.GetController()
		if ctrl and hasattr(ctrl, "interface") and hasattr(ctrl.interface, "OpenSystemDialog"):
			ctrl.interface.OpenSystemDialog()

	def Destroy(self):
		for row in self.rows:
			row.Destroy()
		for toggle in self.toggles:
			toggle.Destroy()
		self.rows = []
		self.toggles = []
		self.cameraReturn = None
		self.dynamicJoystick = None
		self.liveChatToggle = None
		if self.btnCustomizeHud:
			self.btnCustomizeHud.Destroy()
		if self.btnResetHud:
			self.btnResetHud.Destroy()
		if self.btnSystemMenu:
			self.btnSystemMenu.Destroy()
		self.btnCustomizeHud = None
		self.btnResetHud = None
		self.btnSystemMenu = None
		if self.closeButton:
			self.closeButton.Destroy()
		self.closeButton = None
		self.panel = None
		self.title = None
		self.Hide()

	def Open(self):
		for row in self.rows:
			row.Refresh()
		if self.cameraReturn:
			self.cameraReturn.SetValue(bool(self.__Call("IsCameraReturn", 1)))
		if self.dynamicJoystick:
			self.dynamicJoystick.SetValue(uiMobileHud.IsDynamicJoystick())
		if self.liveChatToggle:
			self.liveChatToggle.SetValue(uiMobileHud.IsLiveChatEnabled())
		self.Show()
		self.SetTop()

	def Close(self):
		try:
			systemSetting.SaveConfig()
		except Exception:
			pass
		self.Hide()

	def Toggle(self):
		if self.IsShow():
			self.Close()
		else:
			self.Open()

	def OnPressEscapeKey(self):
		self.Close()
		return True


dialog = None


def Toggle():
	global dialog
	if dialog is None:
		try:
			dialog = MobileSettingsDialog()
		except Exception as e:
			dbg.TraceError("MobileSettingsDialog init error: %s" % str(e))
			return
	dialog.Toggle()


def Hide():
	if dialog:
		dialog.Close()
