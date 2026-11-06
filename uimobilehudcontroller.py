# -*- coding: cp1254 -*-

from __future__ import division

import app

import mouseModule

import player

import wndMgr

import ui

import uiScriptLocale

import uiMobileCompat

import uiMobileHud

import uiMobileStyle

import uiMobileChrome

import uiMobileChat

import uiVirtualJoystick

import uiAttackButton

import dbg



from _weakref import proxy



STATE_HIDDEN = 0

STATE_MOVEMENT_ONLY = 1

STATE_FULL = 2



BLOCKING_WINDOW_NAMES = ("wndInventory", "wndCharacter", "wndSpecialStorage", "wndMessenger", "wndDragonSoul", "dlgExchange", "dlgShop", "wndSafebox", "wndMall")

QUICK_SLOT_REFRESH_INTERVAL = 0.5

EVENT_BUTTON_NAMES = ("wheelShowButton", "wheelEventShowButton", "publisherShowButton")

AFFECT_TOGGLE_NAME = "AffectShowHideBtn"

AFFECT_LABEL_NAME = "AffectShowHideLabel"

AFFECT_SWITCH_IMAGE = "mobile_ui/cynex/affect_switch_%s.png"

AFFECT_DESKTOP_IMAGES = ("refine/checkbox.tga", "refine/checked.tga")

AFFECT_DESKTOP_CHECK_Y = -4

AFFECT_LABEL_GAP = 6

AFFECT_DESKTOP_LABEL_COLOR = 0xFFFFFFFF

# Cynex: barbaros mini harita kisayollari (biyolog, uzaktan market, siralama) dokunmayla da calisiyor - gizlenmez

MINIMAP_HIDDEN_BUTTONS = ()

MINIMAP_DESKTOP_BUTTONS = ("AtlasShowButton", "MiniMapHideButton", "ScaleUpButton", "ScaleDownButton", "MiniMapShowButton")

MINIMAP_ROUND_SIZE = 36

MINIMAP_MINUS_BAR = (16, 3)

MINIMAP_ROUND_BUTTONS = (

	("OpenWindow", 0, 0, "menu_icon_grid", "ToggleAtlasWindow"),

	("OpenWindow", 100, 0, "icon_close", "HideMiniMap"),

	("OpenWindow", 0, 101, None, "ScaleDown"),

	("OpenWindow", 100, 101, "icon_plus", "ScaleUp"),

	("CloseWindow", 96, 6, "icon_chevron_down", "ShowMiniMap"),

)

PUBLISHER_BUTTON_NAME = "publisherShowButton"

PUBLISHER_CLOSE_NAME = "publisherCloseButton"

PUBLISHER_SCALE = 0.7

PUBLISHER_SIZE = (175, 150)

PUBLISHER_CLOSE_ASSET = "close_28"

PUBLISHER_CLOSE_TOP = 10

TASKBAR_TOOLTIP_NAMES = ("tooltipHP", "tooltipSP", "tooltipST", "tooltipEXP")

# Cynex: gorev cubugu gizliyken beceri yayi da ayni olaylari alsin

TASKBAR_HOOKS = (("RefreshQuickSlot", "RefreshQuickSlot"), ("OnUseSkill", "OnUseSkill"), ("OnActivateSkill", "OnActivateSkill"), ("OnDeactivateSkill", "OnDeactivateSkill"))





def _MakeTaskBarHook(function, taskBar, arc, arcName):

	def Hooked(*args):

		result = function(taskBar, *args)

		try:

			getattr(arc, arcName)(*args)

		except ReferenceError:

			pass

		return result

	return Hooked





class HudDragOverlay(ui.Window):

	def __init__(self, name, title, getPosFunc, setPosFunc, width, height):

		ui.Window.__init__(self, "TOP_MOST")

		self.AddFlag("movable")

		self.AddFlag("float")

		self.name = name

		self.getPosFunc = getPosFunc

		self.setPosFunc = setPosFunc

		self.width = max(36, width)

		self.height = max(36, height)

		self.isDragging = False

		self.dragStartX = 0

		self.dragStartY = 0

		self.initialPos = (0, 0)



		self.SetSize(self.width, self.height)

		x, y = getPosFunc()

		self.SetPosition(x, y)



		self.bg = ui.Bar()

		self.bg.SetParent(self)

		self.bg.AddFlag("not_pick")

		self.bg.SetPosition(0, 0)

		self.bg.SetSize(self.width, self.height)

		self.bg.SetColor(0x88204060)

		self.bg.Show()



		self.text = ui.TextLine()

		self.text.SetParent(self)

		self.text.AddFlag("not_pick")

		self.text.SetText(title)

		self.text.SetPosition(self.width // 2, max(2, self.height // 2 - 8))

		self.text.SetHorizontalAlignCenter()

		self.text.Show()

		self.Show()



	def Destroy(self):

		self.isDragging = False

		self.bg = None

		self.text = None

		self.getPosFunc = None

		self.setPosFunc = None

		self.Hide()



	def OnMouseLeftButtonDown(self):

		self.isDragging = True

		mx, my = wndMgr.GetMousePosition()

		self.dragStartX = mx

		self.dragStartY = my

		self.initialPos = (self.GetLeft(), self.GetTop())

		self.bg.SetColor(0xccb87720)

		return True



	def OnMouseLeftButtonUp(self):

		if self.isDragging:

			self.isDragging = False

			self.bg.SetColor(0x88204060)

			if self.setPosFunc:

				self.setPosFunc(self.GetLeft(), self.GetTop())

		return True



	def OnMoveWindow(self, x, y):

		if self.setPosFunc:

			self.setPosFunc(x, y)



	def OnUpdate(self):

		if self.isDragging:

			mx, my = wndMgr.GetMousePosition()

			dx = mx - self.dragStartX

			dy = my - self.dragStartY

			initX, initY = self.initialPos

			sw = wndMgr.GetScreenWidth()

			sh = wndMgr.GetScreenHeight()

			newX = max(0, min(sw - self.width, initX + dx))

			newY = max(0, min(sh - self.height, initY + dy))

			self.SetPosition(newX, newY)

			if self.setPosFunc:

				self.setPosFunc(newX, newY)



class MobileHudController(object):

	def __init__(self, gameWindow, interface):

		self.interface = proxy(interface)

		self.gameWindow = proxy(gameWindow)

		self.state = None

		self.arcVisible = None

		self.arcAttached = False

		self.floatingPositions = {}

		self.hiddenMinimapButtons = {}

		self.minimapDesktopButtons = {}

		self.minimapButtons = []

		self.minimapTapWindow = None

		self.publisherStyled = None

		self.affectToggleDesktop = None

		self.nextQuickSlotRefresh = 0.0

		self.menuHighlights = {}

		self.inventoryEnhanced = False

		self.__EnhanceInventory()



		layout = uiMobileHud.GetTouchLayout(wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())

		self.eventRow = layout["eventRow"]

		uiMobileHud.RegisterController(self)

		self.affectTogglePosition = layout["affectToggle"]



		(x, y, size) = layout["joystick"]

		zone = layout["joystickZone"] if uiMobileHud.IsDynamicJoystick() else None

		self.joystick = uiVirtualJoystick.VirtualJoystick(gameWindow, size, zone, layout["runLock"])

		self.joystick.Place(x, y)



		(x, y, size) = layout["attack"]

		self.attackButton = uiAttackButton.AttackButton(size)

		self.attackButton.SetPosition(x, y)



		self.skillArc = uiMobileHud.SkillArc(interface.wndTaskBar, layout)

		self.taskBarHooks = []

		self.__HookTaskBar(interface.wndTaskBar)



		(utilityPositions, utilitySize) = layout["utilities"]

		self.utilities = uiMobileChrome.ButtonRow(uiMobileChrome.UTILITY_BUTTONS, utilitySize)

		self.utilities.SetEvent("pickup", uiMobileChrome.RunPickup)

		self.utilities.SetEvent("autohunt", self.__GetInterfaceEvent("OpenAutoHunt") if getattr(app, "__AUTO_HUNT__", 0) else None)

		self.utilities.SetEvent("teleport", self.__ToggleTeleportWizard)

		self.utilities.SetEvent("mount", uiMobileChrome.RunMount)

		self.utilities.PlaceVertical(utilityPositions)

		self.utilityOrigin = utilityPositions[0]



		# Cynex: Hedef Sec butonu (Saldiri butonunun solunda, F1 altinda)

		try:

			(tx, ty, tSize) = layout.get("target", (x - 60, y, 54))

			self.targetButton = uiMobileChrome.HudButton(tSize, "target")

			self.targetButton.SetPosition(tx, ty)

			self.targetButton.SetEvent(uiMobileChrome.RunAutoTarget)

			self.targetButton.Show()

		except Exception as e:

			dbg.TraceError("TouchHudController targetButton error: %s" % str(e))

			self.targetButton = None



		self.statusBar = uiMobileChrome.StatusBar()

		self.statusBar.SetPosition(*layout["statusBar"])

		self.statusBar.SetEvent(self.__GetInterfaceEvent("ToggleCharacterWindowStatusPage"))



		self.menuBarUserVisible = True

		(menuX, menuY, menuSize, menuGap) = layout["menuBar"]

		self.menuBarPos = (menuX, menuY, menuSize, menuGap)

		self.menuBar = uiMobileChrome.ButtonRow(uiMobileChrome.MENU_BUTTONS, menuSize)

		self.menuBar.SetEvent("quickmenu", self.__ToggleQuickMenu)

		self.menuBar.SetEvent("character", self.__GetInterfaceEvent("ToggleCharacterWindowStatusPage"))

		self.menuBar.SetEvent("inventory", self.__GetInterfaceEvent("ToggleInventoryWindow"))
		self.menuBar.SetEvent("specialstorage", self.__ToggleSpecialStorage)

		self.menuBar.SetEvent("messenger", self.__GetInterfaceEvent("ToggleMessenger"))

		self.menuBar.SetEvent("itemshop", self.__GetInterfaceEvent("ItemShopSendOpen"))

		self.menuBar.SetEvent("system", self.__GetInterfaceEvent("ToggleSystemDialog"))

		self.menuBar.SetLongPressEvent("system", self.__ToggleSettings)

		self.menuBar.PlaceHorizontal(menuX, menuY, menuSize, menuGap)



		try:

			menuWidth = len(uiMobileChrome.MENU_BUTTONS) * menuSize + (len(uiMobileChrome.MENU_BUTTONS) - 1) * menuGap

			self.menuToggle = uiMobileStyle.PillButton(32, 32, ">", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_SMALL)

			self.menuToggle.SetPosition(menuX + menuWidth + 4, menuY + (menuSize - 36) // 2)

			self.menuToggle.SetEvent(ui.__mem_func__(self.__ToggleMenuBar))

			self.menuToggle.Show()

		except Exception as e:

			dbg.TraceError("TouchHudController menuToggle error: %s" % str(e))

			self.menuToggle = None



		(pillX, pillY, pillWidth, pillHeight) = layout["chatPill"]

		self.chatToggle = uiMobileChrome.ChatToggle(pillWidth, pillHeight)

		self.chatToggle.SetPosition(pillX, pillY)

		self.chatController = uiMobileChrome.ChatController(interface, self.chatToggle)

		self.chatController.Place()

		self.chatController.Collapse()



		try:

			self.liveChatStream = uiMobileChat.LiveChatStream(self.chatController)

			self.liveChatStream.SetPosition(pillX, max(10, pillY - 90))

			self.liveChatStream.Show()

		except Exception as e:

			self.liveChatStream = None

		self.hudEditBar = None

		self.isHudEditMode = False



		self.notifications = None

		gameButtonWindow = getattr(interface, "wndGameButton", None)

		if gameButtonWindow:

			self.notifications = uiMobileChrome.NotificationLayout(gameButtonWindow)

			self.notifications.Apply(uiMobileHud.SCREEN_EDGE, layout["notificationY"])



		self.affectShower = None

		self.affectShowerPosition = None

		affectShower = getattr(gameWindow, "affectShower", None)

		if affectShower:

			self.affectShower = proxy(affectShower)

			self.affectShowerPosition = affectShower.GetGlobalPosition()

			affectShower.SetPosition(*layout["affectShower"])



		self.__ArrangeFloatingWindows()



	def __HookTaskBar(self, taskBar):

		if not taskBar:

			return

		taskBarProxy = proxy(taskBar)

		arcProxy = proxy(self.skillArc)

		for (name, arcName) in TASKBAR_HOOKS:

			method = getattr(taskBar.__class__, name, None)

			function = getattr(method, "im_func", None)

			if function is None:

				continue

			setattr(taskBar, name, _MakeTaskBarHook(function, taskBarProxy, arcProxy, arcName))

			self.taskBarHooks.append(name)

		self.taskBarProxy = taskBarProxy



	def __UnhookTaskBar(self):

		taskBar = getattr(self, "taskBarProxy", None)

		for name in getattr(self, "taskBarHooks", []):

			try:

				if name in taskBar.__dict__:

					del taskBar.__dict__[name]

			except (ReferenceError, AttributeError):

				pass

		self.taskBarHooks = []

		self.taskBarProxy = None



	def __EnhanceInventory(self):

		wndInv = getattr(self.interface, "wndInventory", None)

		if not wndInv:

			return



		if not getattr(wndInv, "_mobileEnhanced", False):

			wndInv._mobileEnhanced = True



			if hasattr(wndMgr, "SetTekDokunus"):

				try:

					wndMgr.SetTekDokunus(wndInv.hWnd, 1)

				except Exception:

					pass



			tabs = getattr(wndInv, "inventoryTab", [])

			for idx, tab in enumerate(tabs):

				if hasattr(wndMgr, "SetTekDokunus"):

					try:

						wndMgr.SetTekDokunus(tab.hWnd, 1)

					except Exception:

						pass

				def _MakeTabHandler(pageIndex):

					def _OnTabTap(*args):

						wndInv.SetInventoryPage(pageIndex)

						for i, t in enumerate(tabs):

							if i == pageIndex:

								t.Down()

							else:

								t.SetUp()

					return _OnTabTap

				handler = _MakeTabHandler(idx)

				tab.SetEvent(handler)

				if hasattr(tab, "SetTouchTapEvent"):

					tab.SetTouchTapEvent(handler)

				if hasattr(ui, "EnableSingleTap"):

					ui.EnableSingleTap(tab)



	def __EnhanceSpecialStorage(self):

		wndStorage = getattr(self.interface, "wndSpecialStorage", None)

		if not wndStorage or not wndStorage.IsShow():

			return



		if not getattr(wndStorage, "_mobileEnhanced", False):

			wndStorage._mobileEnhanced = True

			if hasattr(wndMgr, "SetTekDokunus"):

				try:

					wndMgr.SetTekDokunus(wndStorage.hWnd, 1)

				except Exception:

					pass



	def __EnhanceCharacter(self):
		pass

	def __KeepWindowInBounds(self, window):

		if not window or not window.IsShow():

			return

		sw = wndMgr.GetScreenWidth()

		sh = wndMgr.GetScreenHeight()

		x, y = window.GetLocalPosition()

		w, h = window.GetWidth(), window.GetHeight()

		margin = 8

		newX = max(margin, min(sw - w - margin, x))

		newY = max(margin, min(sh - h - margin, y))

		if (newX, newY) != (x, y):

			window.SetPosition(newX, newY)



	def __ToggleMenuBar(self):

		self.menuBarUserVisible = not getattr(self, "menuBarUserVisible", True)

		if not self.menuBarUserVisible:

			self.menuBar.Hide()

			self.menuToggle.SetText("< Men\xfc")

			self.menuToggle.SetSize(72, 34)

			self.menuToggle.SetPosition(wndMgr.GetScreenWidth() - uiMobileHud.MINIMAP_RESERVED_WIDTH - 80, uiMobileHud.TOP_MARGIN + 12)

		else:

			(menuX, menuY, menuSize, menuGap) = self.menuBarPos

			self.menuBar.Show()

			self.menuToggle.SetText(">")

			self.menuToggle.SetSize(32, 32)

			menuWidth = len(self.menuBar.order) * menuSize + (len(self.menuBar.order) - 1) * menuGap

			self.menuToggle.SetPosition(menuX + menuWidth + 4, menuY + (menuSize - 36) // 2)

		self.menuToggle.SetTop()



	def __ToggleSpecialStorage(self):
		if not self.interface:
			return
		if hasattr(self.interface, "ToggleSpecialStorageWindow"):
			self.interface.ToggleSpecialStorageWindow()
		elif hasattr(self.interface, "wndSpecialStorage") and self.interface.wndSpecialStorage:
			if self.interface.wndSpecialStorage.IsShow():
				self.interface.wndSpecialStorage.Close()
			else:
				self.interface.wndSpecialStorage.Show()

	def __ToggleQuickMenu(self):

		collectiveMenu = getattr(self.gameWindow, "CollectiveMenu", None)

		if collectiveMenu:

			collectiveMenu.OpenDialog()



	def __ToggleTeleportWizard(self):

		if not self.gameWindow:

			return

		if hasattr(self.gameWindow, "SendOpenTeleportWizardInfo"):

			if hasattr(self.gameWindow, "interface") and hasattr(self.gameWindow.interface, "wndTpWizardDataInfo"):

				if self.gameWindow.interface.wndTpWizardDataInfo and self.gameWindow.interface.wndTpWizardDataInfo.IsShow():

					self.gameWindow.interface.ToggleTpWizardInfoWindow()

					return

			self.gameWindow.SendOpenTeleportWizardInfo()

		else:

			import net

			net.SendChatPacket("/teleportion_wizard open")



	@staticmethod

	def __ToggleSettings():

		import uiMobileSettings

		uiMobileSettings.Toggle()



	def __GetInterfaceEvent(self, name):

		method = getattr(self.interface, name, None)

		if method is None:

			return None

		return ui.__mem_func__(method)



	def Destroy(self, restoreDesktop):

		self.__UnhookTaskBar()



		if restoreDesktop:

			self.__RestoreDesktop()

		else:

			import uiMobileSettings

			uiMobileSettings.Hide()



		self.skillArc.Destroy()

		self.attackButton.Destroy()

		self.joystick.Destroy()

		self.utilities.Destroy()

		self.menuBar.Destroy()

		if getattr(self, "targetButton", None):

			self.targetButton.Destroy()

			self.targetButton = None

		if getattr(self, "menuToggle", None):

			self.menuToggle.Destroy()

			self.menuToggle = None

		self.statusBar.Destroy()

		self.chatController.Destroy()

		self.chatToggle.Destroy()

		if getattr(self, "liveChatStream", None):

			self.liveChatStream.Destroy()

			self.liveChatStream = None

		if getattr(self, "hudEditBar", None):

			self.hudEditBar.Destroy()

			self.hudEditBar = None



		self.skillArc = None

		self.attackButton = None

		self.joystick = None

		self.utilities = None

		self.menuBar = None

		self.statusBar = None

		self.chatController = None

		self.chatToggle = None

		self.notifications = None

		self.affectShower = None

		self.floatingPositions = {}

		self.gameWindow = None

		self.interface = None



	def __RestoreDesktop(self):

		try:

			taskBar = self.interface.wndTaskBar

		except ReferenceError:

			return

		if taskBar:

			taskBar.Show()

		self.chatController.Restore()

		if self.notifications:

			self.notifications.Restore()

		if self.affectShower and self.affectShowerPosition:

			try:

				self.affectShower.SetPosition(*self.affectShowerPosition)

			except ReferenceError:

				pass

		for (window, position) in self.floatingPositions.values():

			try:

				window.SetPosition(*position)

			except ReferenceError:

				pass

		for button in self.hiddenMinimapButtons.values():

			try:

				button.Show()

			except ReferenceError:

				pass

		self.hiddenMinimapButtons = {}

		self.__RestoreMinimapButtons()

		self.__RestorePublisher()

		self.__RestoreAffectToggle()



	def __GetGameWindowChild(self, name):

		try:

			return getattr(self.gameWindow, name, None)

		except ReferenceError:

			return None



	def __IsTracked(self, name, window):

		stored = self.floatingPositions.get(name)

		if not stored:

			return False

		try:

			return stored[0] == window

		except ReferenceError:

			return False



	def __MoveFloatingWindow(self, name, window, x, y):

		if not self.__IsTracked(name, window):

			self.floatingPositions[name] = (proxy(window), tuple(window.GetLocalPosition()))

		if tuple(window.GetLocalPosition()) != (x, y):

			window.SetPosition(x, y)



	def __ArrangeFloatingWindows(self):

		self.__StylePublisher()

		(rightX, rowY) = self.eventRow

		for name in EVENT_BUTTON_NAMES:

			window = self.__GetGameWindowChild(name)

			if not window or not window.IsShow():

				continue

			rightX -= window.GetWidth()

			self.__MoveFloatingWindow(name, window, rightX, rowY)

			rightX -= uiMobileHud.WINDOW_GAP



		toggle = self.__GetGameWindowChild(AFFECT_TOGGLE_NAME)

		if toggle:

			self.__StyleAffectToggle(toggle)

			self.__MoveFloatingWindow(AFFECT_TOGGLE_NAME, toggle, *self.affectTogglePosition)



		self.__HideMinimapButtons()

		self.__BuildMinimapButtons()

		self.__ArrangeWhisperButtons()



	def __ArrangeWhisperButtons(self):

		# Cynex: fisilti/[DUYURU] dugmeleri sag sutundaki Topla/Oto Av/Binek ile cakismasin - solunda dizilir

		buttons = getattr(self.interface, "whisperButtonList", None)

		if not buttons:

			return

		(utilityX, utilityY) = self.utilityOrigin

		y = utilityY

		for button in buttons:

			x = utilityX - button.GetWidth() - uiMobileHud.WINDOW_GAP * 2

			if button.GetLocalPosition() != (x, y):

				button.SetPosition(x, y)

			y += button.GetHeight() + uiMobileHud.WINDOW_GAP



	def __StyleAffectToggle(self, toggle):

		if self.affectToggleDesktop:

			return

		label = self.__GetGameWindowChild(AFFECT_LABEL_NAME)

		if not label or not toggle.backgroundImage or not toggle.checkImage:

			return

		self.affectToggleDesktop = (proxy(toggle), proxy(label), label.GetText(), tuple(label.GetLocalPosition()), (toggle.GetWidth(), toggle.GetHeight()))

		toggle.backgroundImage.LoadImage(AFFECT_SWITCH_IMAGE % "off")

		toggle.checkImage.LoadImage(AFFECT_SWITCH_IMAGE % "on")

		toggle.checkImage.SetPosition(0, 0)

		switchWidth = toggle.backgroundImage.GetWidth()

		switchHeight = toggle.backgroundImage.GetHeight()

		label.SetText(uiScriptLocale.MOBILE_AFFECT_TOGGLE)

		label.SetPackedFontColor(uiMobileStyle.GOLD_COLOR)

		label.SetPosition(switchWidth + AFFECT_LABEL_GAP, (switchHeight - 14) // 2)

		toggle.SetSize(switchWidth + AFFECT_LABEL_GAP + label.GetTextSize()[0], switchHeight)



	def __RestoreAffectToggle(self):

		if not self.affectToggleDesktop:

			return

		(toggle, label, text, position, size) = self.affectToggleDesktop

		self.affectToggleDesktop = None

		try:

			toggle.backgroundImage.LoadImage(AFFECT_DESKTOP_IMAGES[0])

			toggle.checkImage.LoadImage(AFFECT_DESKTOP_IMAGES[1])

			toggle.checkImage.SetPosition(0, AFFECT_DESKTOP_CHECK_Y)

			toggle.SetSize(*size)

			label.SetText(text)

			label.SetPackedFontColor(AFFECT_DESKTOP_LABEL_COLOR)

			label.SetPosition(*position)

		except ReferenceError:

			pass



	def __HideMinimapButtons(self):

		miniMap = getattr(self.interface, "wndMiniMap", None)

		if not miniMap:

			return

		for name in MINIMAP_HIDDEN_BUTTONS:

			button = getattr(miniMap, name, None)

			if button and button.IsShow():

				button.Hide()

				self.hiddenMinimapButtons[name] = proxy(button)



	def __BuildMinimapButtons(self):

		miniMap = getattr(self.interface, "wndMiniMap", None)

		if not miniMap:

			return

		for name in MINIMAP_DESKTOP_BUTTONS:

			button = getattr(miniMap, name, None)

			if button and button.IsShow():

				button.Hide()

				self.minimapDesktopButtons[name] = proxy(button)



		if not self.minimapButtons and getattr(miniMap, "OpenWindow", None) and getattr(miniMap, "CloseWindow", None):

			for (parentName, x, y, iconName, methodName) in MINIMAP_ROUND_BUTTONS:

				method = getattr(miniMap, methodName, None)

				if not method:

					continue

				button = uiMobileStyle.RoundIconButton(MINIMAP_ROUND_SIZE, iconName)

				if not iconName:

					button.AddBar(*MINIMAP_MINUS_BAR)

				button.SetParent(getattr(miniMap, parentName))

				button.SetPosition(x, y)

				button.SetEvent(ui.__mem_func__(method))

				button.Show()

				self.minimapButtons.append(button)



		mapWindow = getattr(miniMap, "MiniMapWindow", None)

		if mapWindow and not self.minimapTapWindow:

			toggle = ui.__mem_func__(miniMap.ToggleAtlasWindow)

			mapWindow.SetTouchTapEvent(lambda x, y: toggle())

			self.minimapTapWindow = proxy(mapWindow)



	def __RestoreMinimapButtons(self):

		for button in self.minimapButtons:

			button.Hide()

			button.Destroy()

		self.minimapButtons = []

		for button in self.minimapDesktopButtons.values():

			try:

				button.Show()

			except ReferenceError:

				pass

		self.minimapDesktopButtons = {}

		if self.minimapTapWindow:

			try:

				self.minimapTapWindow.eventTouchTap = None

				if "OnTouchTap" in self.minimapTapWindow.__dict__:

					del self.minimapTapWindow.OnTouchTap

			except ReferenceError:

				pass

			self.minimapTapWindow = None



	def __StylePublisher(self):

		button = self.__GetGameWindowChild(PUBLISHER_BUTTON_NAME)

		if not button:

			return

		if self.publisherStyled:

			try:

				if self.publisherStyled[0] == button:

					return

			except ReferenceError:

				pass

			self.__RestorePublisher()

		desktopClose = self.__GetGameWindowChild(PUBLISHER_CLOSE_NAME)

		(width, height) = PUBLISHER_SIZE

		scaledWidth = int(width * PUBLISHER_SCALE)

		scaledHeight = int(height * PUBLISHER_SCALE)

		button.SetButtonScale(PUBLISHER_SCALE, PUBLISHER_SCALE)

		button.SetSize(scaledWidth, scaledHeight)

		close = uiMobileStyle.StateImageButton(PUBLISHER_CLOSE_ASSET)

		close.SetParent(button)

		close.SetPosition(scaledWidth - close.GetWidth(), PUBLISHER_CLOSE_TOP)

		if desktopClose:

			desktopClose.Hide()

			close.SetEvent(ui.__mem_func__(desktopClose.CallEvent))

		close.Show()

		self.publisherStyled = (proxy(button), proxy(desktopClose) if desktopClose else None, close)



	def __RestorePublisher(self):

		if not self.publisherStyled:

			return

		(button, desktopClose, close) = self.publisherStyled

		self.publisherStyled = None

		close.Hide()

		close.Destroy()

		try:

			button.SetButtonScale(1.0, 1.0)

			button.SetSize(*PUBLISHER_SIZE)

			if desktopClose and button.IsShow():

				desktopClose.Show()

		except ReferenceError:

			pass



	def __IsWindowOpen(self, name):

		window = self.interface.__dict__.get(name)

		if not window:

			return False

		try:

			return bool(window.IsShow())

		except Exception:

			return False



	def __IsCombatBlocked(self):

		for name in BLOCKING_WINDOW_NAMES:

			if self.__IsWindowOpen(name):

				return True

		return False



	def __GetState(self):

		if uiMobileHud.IsCameraMode():

			return STATE_HIDDEN

		if player.IsObserverMode() or self.__IsCombatBlocked():

			return STATE_MOVEMENT_ONLY

		return STATE_FULL



	def __ApplyState(self, state):

		if state == STATE_HIDDEN:

			self.joystick.Stop()

			self.joystick.Hide()

			self.statusBar.Hide()

			self.menuBar.Hide()

			if getattr(self, "menuToggle", None):

				self.menuToggle.Hide()

			self.chatController.Hide()

		else:

			self.joystick.Show()

			self.statusBar.Show()

			if getattr(self, "menuToggle", None):

				self.menuToggle.Show()

			if getattr(self, "menuBarUserVisible", True):

				self.menuBar.Show()

			else:

				self.menuBar.Hide()

			self.chatController.Show()



		if state == STATE_FULL:

			self.attackButton.Show()

			self.utilities.Show()

			if getattr(self, "targetButton", None):

				self.targetButton.Show()

		else:

			self.attackButton.Stop()

			self.attackButton.Hide()

			self.utilities.Hide()

			if getattr(self, "targetButton", None):

				self.targetButton.Hide()



	def __RefreshSkillArc(self, state):

		attached = bool(mouseModule.mouseController.isAttached())

		attachedType = None

		if attached and hasattr(mouseModule.mouseController, "GetAttachedType"):

			try:

				attachedType = mouseModule.mouseController.GetAttachedType()

			except Exception:

				attachedType = None



		if state == STATE_FULL:

			wanted = True

		elif state == STATE_HIDDEN or player.IsObserverMode():

			wanted = False

		else:

			if self.__IsWindowOpen("wndInventory") or self.__IsWindowOpen("wndSpecialStorage"):

				wanted = False

			elif attached:

				wanted = bool(attachedType == player.SLOT_TYPE_SKILL)

			else:

				wanted = bool(self.__IsWindowOpen("wndCharacter"))



		raiseArc = wanted and state != STATE_FULL and (not self.arcVisible or (attached and not self.arcAttached))

		self.arcAttached = attached

		if wanted != self.arcVisible:

			self.arcVisible = wanted

			if wanted:

				self.skillArc.Show()

			else:

				self.skillArc.Hide()

		if raiseArc and wanted:

			self.skillArc.SetTop()



	def __HideTaskBar(self):

		taskBar = self.interface.wndTaskBar

		if not taskBar:

			return

		if taskBar.IsShow():

			taskBar.Hide()

		for name in TASKBAR_TOOLTIP_NAMES:

			tooltip = getattr(taskBar, name, None)

			if tooltip and tooltip.IsShow():

				tooltip.Hide()



	def __RefreshMenuHighlights(self):

		for (buttonName, windowName) in (

			("inventory", "wndInventory"),

			("character", "wndCharacter"),

			("system", "dlgSystem"),

			("messenger", "wndMessenger"),

			("itemshop", "wndItemShop"),

		):

			button = self.menuBar.GetButton(buttonName)

			if not button:

				continue

			isOpen = self.__IsWindowOpen(windowName)

			if self.menuHighlights.get(buttonName) != isOpen:

				self.menuHighlights[buttonName] = isOpen

				button.SetHighlight(isOpen)



		qmButton = self.menuBar.GetButton("quickmenu")

		if qmButton:

			collectiveMenu = getattr(self.gameWindow, "CollectiveMenu", None)

			isQmOpen = bool(collectiveMenu and collectiveMenu.IsShow())

			if self.menuHighlights.get("quickmenu") != isQmOpen:

				self.menuHighlights["quickmenu"] = isQmOpen

				qmButton.SetHighlight(isQmOpen)



		tpButton = self.utilities.GetButton("teleport") if self.utilities else None

		if tpButton:

			tpOpen = False

			if hasattr(self.gameWindow, "interface") and hasattr(self.gameWindow.interface, "wndTpWizardDataInfo"):

				wnd = self.gameWindow.interface.wndTpWizardDataInfo

				tpOpen = bool(wnd and wnd.IsShow())

			if self.menuHighlights.get("teleport") != tpOpen:

				self.menuHighlights["teleport"] = tpOpen

				tpButton.SetHighlight(tpOpen)



		ahButton = self.utilities.GetButton("autohunt") if self.utilities else None

		if ahButton:

			ahOpen = False

			if hasattr(self.interface, "wndAutoHunt") and self.interface.wndAutoHunt:

				ahOpen = bool(self.interface.wndAutoHunt.IsShow())

			if self.menuHighlights.get("autohunt") != ahOpen:

				self.menuHighlights["autohunt"] = ahOpen

				ahButton.SetHighlight(ahOpen)



	def __RefreshPointAlert(self):

		if self.notifications:

			self.notifications.HidePointButtons()

		button = self.menuBar.GetButton("character")

		if button:

			button.SetAlert(player.GetStatus(player.STAT) > 0 or player.GetStatus(player.SKILL_ACTIVE) > 0)



	def Update(self):

		state = self.__GetState()

		if state != self.state:

			self.state = state

			self.__ApplyState(state)

		self.__RefreshSkillArc(state)



		self.__HideTaskBar()

		self.__RefreshMenuHighlights()

		self.__RefreshPointAlert()



		if state != STATE_HIDDEN:

			self.chatController.Update()

			# Heartbeat keepalive: sunucu oturumunun arka planda kopmasini engeller

			curTime = app.GetTime()

			if not hasattr(self, "_lastKeepAlive"):

				self._lastKeepAlive = curTime

			elif curTime - self._lastKeepAlive > 20.0:

				self._lastKeepAlive = curTime

				try:

					import net

					net.SendCharacterPositionPacket(0)

				except Exception:

					pass



		# 1. Enhance and scale inventory / storage / character windows

		self.__EnhanceInventory()

		self.__EnhanceSpecialStorage()

		self.__EnhanceCharacter()



		# 2. Auto page switch when dragging item over inventory tabs

		if mouseModule.mouseController.isAttached():

			wndInv = getattr(self.interface, "wndInventory", None)

			if wndInv and wndInv.IsShow():

				mx, my = wndMgr.GetMousePosition()

				tabs = getattr(wndInv, "inventoryTab", [])

				for idx, tab in enumerate(tabs):

					gx, gy = tab.GetGlobalPosition()

					gw, gh = tab.GetWidth(), tab.GetHeight()

					if (gx - 12 <= mx <= gx + gw + 12) and (gy - 12 <= my <= gy + gh + 12):

						if wndInv.inventoryPageIndex != idx:

							now = app.GetTime()

							if now - getattr(self, "_lastTabHoverSwitch", 0.0) > 0.25:

								self._lastTabHoverSwitch = now

								wndInv.SetInventoryPage(idx)

								for i, t in enumerate(tabs):

									if i == idx:

										t.Down()

									else:

										t.SetUp()

						break



				eqTabs = getattr(wndInv, "equipmentTab", [])

				for idx, eqTab in enumerate(eqTabs):

					gx, gy = eqTab.GetGlobalPosition()

					gw, gh = eqTab.GetWidth(), eqTab.GetHeight()

					if (gx - 8 <= mx <= gx + gw + 8) and (gy - 8 <= my <= gy + gh + 8):

						if getattr(wndInv, "equipmentPageIndex", 0) != idx:

							now = app.GetTime()

							if now - getattr(self, "_lastEqTabHoverSwitch", 0.0) > 0.25:

								self._lastEqTabHoverSwitch = now

								wndInv.SetEquipmentPage(idx)

								for i, t in enumerate(eqTabs):

									if i == idx:

										t.Down()

									else:

										t.SetUp()

						break



		# 3. Safe-Area / Notch protection: clamp windows inside visible screen

		for wndName in ("wndInventory", "wndCharacter", "dlgSystem", "wndSpecialStorage"):

			wnd = getattr(self.interface, wndName, None)

			if wnd and wnd.IsShow():

				self.__KeepWindowInBounds(wnd)



		now = app.GetTime()

		if now >= self.nextQuickSlotRefresh:

			self.nextQuickSlotRefresh = now + QUICK_SLOT_REFRESH_INTERVAL

			self.skillArc.RefreshQuickSlot()

			self.__ArrangeFloatingWindows()



	def StartHudEditMode(self):

		if self.isHudEditMode:

			return

		self.isHudEditMode = True

		import uiMobileStyle

		import uiMobileLocale

		import uiScriptLocale



		def Loc(n):

			if hasattr(uiScriptLocale, n):

				return getattr(uiScriptLocale, n)

			return uiMobileLocale.STRINGS.get(n, n)



		sw, sh = wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight()

		barW, barH = 520, 48

		self.hudEditBar = ui.Window("TOP_MOST")

		self.hudEditBar.SetSize(barW, barH)

		self.hudEditBar.SetPosition((sw - barW) // 2, 10)

		self.hudEditBar.panel = uiMobileStyle.CreateOrnatePanel(self.hudEditBar, 0, 0, barW, barH)

		self.hudEditBar.title = uiMobileStyle.CreateText(self.hudEditBar, Loc("MOBILE_HUD_EDIT_TITLE"), 16, 16, uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_SMALL)



		btnSave = uiMobileStyle.PillButton(70, 30, Loc("MOBILE_HUD_SAVE"), None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_SMALL)

		btnSave.SetParent(self.hudEditBar)

		btnSave.SetPosition(barW - 230, 9)

		btnSave.SetEvent(ui.__mem_func__(self.__SaveCustomHudLayout))

		btnSave.Show()

		self.hudEditBar.btnSave = btnSave



		btnReset = uiMobileStyle.PillButton(70, 30, Loc("MOBILE_HUD_RESET"), None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_SMALL)

		btnReset.SetParent(self.hudEditBar)

		btnReset.SetPosition(barW - 150, 9)

		btnReset.SetEvent(ui.__mem_func__(self.__ResetCustomHudLayout))

		btnReset.Show()

		self.hudEditBar.btnReset = btnReset



		btnClose = uiMobileStyle.PillButton(60, 30, Loc("MOBILE_HUD_CLOSE"), None, "field", uiMobileStyle.SOFT_COLOR, uiMobileStyle.FONT_SMALL)

		btnClose.SetParent(self.hudEditBar)

		btnClose.SetPosition(barW - 70, 9)

		btnClose.SetEvent(ui.__mem_func__(self.__CloseHudEditMode))

		btnClose.Show()

		self.hudEditBar.btnClose = btnClose

		self.hudEditBar.Show()



		self.hudDragOverlays = []



		# Joystick Overlay

		if getattr(self, "joystick", None):

			jw = getattr(self.joystick, "baseSize", self.joystick.GetWidth())
			jh = getattr(self.joystick, "baseSize", self.joystick.GetHeight())

			def _GetJoy():
				if hasattr(self.joystick, "GetBasePosition"):
					return self.joystick.GetBasePosition()
				return self.joystick.GetLocalPosition()

			def _SetJoy(x, y):
				if hasattr(self.joystick, "SetBasePosition"):
					self.joystick.SetBasePosition(x, y)
				else:
					self.joystick.SetPosition(x, y)

			self.hudDragOverlays.append(HudDragOverlay("joystick", "Joystick", _GetJoy, _SetJoy, jw, jh))



		# Attack Button Overlay

		if self.attackButton:

			w, h = self.attackButton.GetWidth(), self.attackButton.GetHeight()

			def _GetAttack(): return self.attackButton.GetLocalPosition()

			def _SetAttack(x, y): self.attackButton.SetPosition(x, y)

			self.hudDragOverlays.append(HudDragOverlay("attack", "Sald\xfdr\xfd", _GetAttack, _SetAttack, w, h))



		# Skill Slots Overlays (1, 2, 3, 4, F1, F2, F3, F4 and Page)

		if getattr(self, "skillArc", None) and hasattr(self.skillArc, "slots"):

			slotLabels = ("1", "2", "3", "4", "F1", "F2", "F3", "F4")

			for idx, s in enumerate(self.skillArc.slots):

				sw, sh = s.GetWidth(), s.GetHeight()

				lbl = slotLabels[idx] if idx < len(slotLabels) else str(idx + 1)

				def _MakeGetter(targetSlot): return lambda: targetSlot.GetLocalPosition()

				def _MakeSetter(targetSlot): return lambda x, y: targetSlot.SetPosition(x, y)

				self.hudDragOverlays.append(HudDragOverlay("slot_%d" % idx, lbl, _MakeGetter(s), _MakeSetter(s), sw, sh))

			if getattr(self.skillArc, "pageButton", None):

				pb = self.skillArc.pageButton

				pw, ph = pb.GetWidth(), pb.GetHeight()

				def _GetPage(): return pb.GetLocalPosition()

				def _SetPage(x, y): pb.SetPosition(x, y)

				self.hudDragOverlays.append(HudDragOverlay("slot_page", "Sayfa", _GetPage, _SetPage, pw, ph))

			if getattr(self.skillArc, "lockButton", None):

				lb = self.skillArc.lockButton

				lw, lh = lb.GetWidth(), lb.GetHeight()

				def _GetLock(): return lb.GetLocalPosition()

				def _SetLock(x, y): lb.SetPosition(x, y)

				self.hudDragOverlays.append(HudDragOverlay("slot_lock", "Kilit", _GetLock, _SetLock, lw, lh))



		# Target Button Overlay

		if getattr(self, "targetButton", None):

			w, h = self.targetButton.GetWidth(), self.targetButton.GetHeight()

			def _GetTarget(): return self.targetButton.GetLocalPosition()

			def _SetTarget(x, y): self.targetButton.SetPosition(x, y)

			self.hudDragOverlays.append(HudDragOverlay("target", "Hedef Se\xe7", _GetTarget, _SetTarget, w, h))



		# Utilities Overlay

		if self.utilities:

			count = len(self.utilities.order)

			size = self.utilities.size

			gap = self.utilities.gap

			totalH = count * size + max(0, count - 1) * gap

			def _GetUtil(): return self.utilities.GetLocalPosition()

			def _SetUtil(x, y):

				self.utilities.SetPosition(x, y)

				self.utilityOrigin = (x, y)

			self.hudDragOverlays.append(HudDragOverlay("utilities", "\xdd\xfelemler", _GetUtil, _SetUtil, size, totalH))



		# Menu Bar Overlay

		if self.menuBar:

			count = len(self.menuBar.order)

			size = self.menuBar.size

			gap = self.menuBar.gap

			totalW = count * size + max(0, count - 1) * gap

			def _GetMenu(): return self.menuBar.GetLocalPosition()

			def _SetMenu(x, y):

				self.menuBar.SetPosition(x, y)

				self.menuBarPos = (x, y, size, gap)

				if getattr(self, "menuToggle", None) and self.menuBar.IsShow():

					self.menuToggle.SetPosition(x + totalW + 4, y + (size - 30) // 2)

			self.hudDragOverlays.append(HudDragOverlay("menuBar", "Men\xfc", _GetMenu, _SetMenu, totalW, size))



		# Status Bar Overlay

		if self.statusBar:

			w, h = self.statusBar.GetWidth(), self.statusBar.GetHeight()

			def _GetStatus(): return self.statusBar.GetLocalPosition()

			def _SetStatus(x, y): self.statusBar.SetPosition(x, y)

			self.hudDragOverlays.append(HudDragOverlay("statusBar", "Durum", _GetStatus, _SetStatus, w, h))



		# Chat Toggle Overlay

		if self.chatToggle:

			w, h = self.chatToggle.GetWidth(), self.chatToggle.GetHeight()

			def _GetChat(): return self.chatToggle.GetLocalPosition()

			def _SetChat(x, y):

				self.chatToggle.SetPosition(x, y)

				if getattr(self, "liveChatStream", None):

					self.liveChatStream.SetPosition(x, max(10, y - 90))

			self.hudDragOverlays.append(HudDragOverlay("chatPill", "Sohbet", _GetChat, _SetChat, w, h))



	def __SaveCustomHudLayout(self):

		pos = {}

		if getattr(self, "joystick", None):

			if hasattr(self.joystick, "GetBasePosition"):
				pos["joystick"] = list(self.joystick.GetBasePosition())
			else:
				pos["joystick"] = list(self.joystick.GetLocalPosition())

		if self.attackButton:

			pos["attack"] = list(self.attackButton.GetLocalPosition())

		if getattr(self, "targetButton", None):

			pos["target"] = list(self.targetButton.GetLocalPosition())

		if self.utilities:

			pos["utilities"] = list(self.utilities.GetLocalPosition())

		if self.menuBar:

			pos["menuBar"] = list(self.menuBar.GetLocalPosition())

		if self.statusBar:

			pos["statusBar"] = list(self.statusBar.GetLocalPosition())

		if self.chatToggle:

			pos["chatPill"] = list(self.chatToggle.GetLocalPosition())

		if getattr(self, "skillArc", None) and hasattr(self.skillArc, "slots"):

			for idx, s in enumerate(self.skillArc.slots):

				pos["slot_%d" % idx] = list(s.GetLocalPosition())

			if getattr(self.skillArc, "pageButton", None):

				pos["slot_page"] = list(self.skillArc.pageButton.GetLocalPosition())

		uiMobileHud.SaveCustomHudPositions(pos)

		self.__CloseHudEditMode()



	def __ResetCustomHudLayout(self):

		uiMobileHud.ResetCustomHudPositions()

		self.__CloseHudEditMode()

		uiMobileHud.RequestRefresh()



	def __CloseHudEditMode(self):

		self.isHudEditMode = False

		if hasattr(self, "hudDragOverlays"):

			for overlay in self.hudDragOverlays:

				overlay.Destroy()

			self.hudDragOverlays = []

		if self.hudEditBar:

			self.hudEditBar.Hide()

			self.hudEditBar = None

