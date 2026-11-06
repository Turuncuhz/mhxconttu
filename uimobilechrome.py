from __future__ import division
import app
import chat
import math
import net
import player
import wndMgr
import uiScriptLocale
import ui
import uiMobileCompat
import uiMobileStyle
import uiMobileChat

from _weakref import proxy

STATUS_WIDTH = 332
STATUS_HEIGHT = 82
FACE_CENTER = (37, 40)
FACE_SIZE = 52
LEVEL_CENTER_Y = 72
BAR_X = 81
BAR_WIDTH = 220
NAME_Y = 9
HP_Y = 27
SP_Y = 42
ST_Y = 55
EXP_Y = 66
GAUGE_INSET = 1
STATUS_REFRESH_INTERVAL = 0.2
LOW_HP_RATIO = 0.3

LOW_HP_TEXT_COLOR = uiMobileStyle.Color(255, 176, 150)
BAR_TEXT_COLOR = uiMobileStyle.Color(246, 236, 214)

MENU_BUTTONS = ("quickmenu", "character", "inventory", "specialstorage", "messenger", "itemshop", "system")
UTILITY_BUTTONS = ("pickup", "autohunt", "teleport", "mount")
HUD_BUTTON_SIZES = (54, 60, 68)
HUD_BUTTON_LABELS = {
	"character" : "MOBILE_MENU_CHARACTER",
	"inventory" : "MOBILE_MENU_INVENTORY",
	"specialstorage" : "MOBILE_MENU_SPECIAL_STORAGE",
	"messenger" : "MOBILE_MENU_MESSENGER",
	"itemshop" : "MOBILE_MENU_ITEMSHOP",
	"system" : "MOBILE_MENU_SYSTEM",
	"pickup" : "MOBILE_MENU_PICKUP",
	"autohunt" : "MOBILE_MENU_AUTOHUNT",
	"mount" : "MOBILE_MENU_MOUNT",
	"target" : "MOBILE_MENU_TARGET",
	"quickmenu" : "MOBILE_MENU_QUICKMENU",
	"teleport" : "MOBILE_MENU_TELEPORT",
}
HUD_LABEL_FONT = "AlegreyaSans:15"
HUD_LABEL_BOTTOM = 18
HUD_LABEL_COLOR = uiMobileStyle.Color(240, 207, 135)
HUD_ALERT_ASSET = "hudbtn_alert_%d"
HUD_ALERT_SPEED = 5.0
HUD_ALERT_MIN_ALPHA = 0.25

CHAT_ICON = "chat_icon"
CHAT_EXPAND_ICON = "icon_chevron_up"
CHAT_BAR_FRAME = "chat_bar"
CHAT_TITLE_ASSET = "chat_title_%s"
CHAT_ORNAMENT_ASSET = "chat_ornament_%s"
CHAT_ORNAMENT_GAP = 8
CHAT_RIGHT_RESERVED = 60
PILL_PADDING = 14
BADGE_HEIGHT = 20
BADGE_MIN_WIDTH = 22
BADGE_LIMIT = 9
BOTTOM_MARGIN = 20
SCREEN_GAP = 8

NOTIFICATION_ORDER = ("QUEST", "HELP", "BUILD", "EXIT_OBSERVER")
HIDDEN_NOTIFICATIONS = ("STATUS", "SKILL")
NOTIFICATION_STEP = 48


def FormatNumber(value):
	return "{:,}".format(int(value)).replace(",", ".")


def HudButtonSize(size):
	return min(HUD_BUTTON_SIZES, key=lambda candidate: abs(candidate - size))


class HudButton(ui.Window):
	def __init__(self, size, name):
		ui.Window.__init__(self, "UI")
		self.SetSize(size, size)
		ui.EnableSingleTap(self)

		self.event = None
		self.active = False
		self.pressed = False
		self.alert = None
		self.alertOn = False
		self.assetPrefix = "hudbtn_%s_%d" % (name, HudButtonSize(size))
		self.assetScale = float(size) / HudButtonSize(size)
		self.state = None

		self.image = ui.ExpandedImageBox()
		self.image.SetParent(self)
		self.image.AddFlag("not_pick")
		self.image.Show()
		self.__Refresh()

		labelName = HUD_BUTTON_LABELS.get(name)
		labelText = ""
		if labelName:
			if hasattr(uiScriptLocale, labelName):
				labelText = getattr(uiScriptLocale, labelName)
			if not labelText:
				try:
					import uiMobileLocale
					labelText = uiMobileLocale.STRINGS.get(labelName, "")
				except Exception:
					pass
			if not labelText and labelName == "MOBILE_MENU_SPECIAL_STORAGE":
				labelText = "K-Envanter"
		self.label = uiMobileStyle.CreateText(self, labelText, size // 2, size - HUD_LABEL_BOTTOM, HUD_LABEL_COLOR, HUD_LABEL_FONT, "center", True)

		self.SetTouchTapEvent(ui.__mem_func__(self.__OnTap))

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.event = None
		self.longPressEvent = None
		self.eventTouchTap = None
		self.eventTouchLongPress = None
		self.image = None
		self.label = None
		self.alert = None
		self.alertOn = False
		self.Hide()

	def SetEvent(self, event):
		self.event = event

	# Cynex: uzun basis ikinci islev (Menu: mobil ayarlar)
	def SetLongPressEvent(self, event):
		self.longPressEvent = event
		self.SetTouchLongPressEvent(ui.__mem_func__(self.__OnLongPress))

	def __OnLongPress(self, x, y):
		event = getattr(self, "longPressEvent", None)
		if event:
			event()

	def SetAlert(self, enabled):
		if enabled == self.alertOn:
			return
		self.alertOn = enabled
		if enabled and not self.alert:
			self.alert = ui.ExpandedImageBox()
			self.alert.SetParent(self)
			self.alert.AddFlag("not_pick")
			uiMobileStyle.LoadAsset(self.alert, HUD_ALERT_ASSET % HudButtonSize(self.GetWidth()))
			if self.assetScale != 1.0:
				self.alert.SetScale(self.assetScale, self.assetScale)
		if not self.alert:
			return
		if enabled:
			self.alert.Show()
		else:
			self.alert.Hide()

	def OnUpdate(self):
		if not self.alertOn or not self.alert:
			return
		phase = (math.sin(app.GetTime() * HUD_ALERT_SPEED) + 1.0) / 2.0
		alpha = HUD_ALERT_MIN_ALPHA + (1.0 - HUD_ALERT_MIN_ALPHA) * phase
		wndMgr.SetDiffuseColor(self.alert.hWnd, 1.0, 1.0, 1.0, alpha)

	def SetHighlight(self, enabled):
		self.active = enabled
		self.__Refresh()

	def __Refresh(self):
		if not self.image:
			return
		if self.pressed:
			state = "down"
		elif self.active or getattr(self, "hover", False):
			state = "active"
		else:
			state = "normal"
		if state == self.state:
			return
		self.state = state
		uiMobileStyle.LoadAsset(self.image, "%s_%s" % (self.assetPrefix, state))
		if self.assetScale != 1.0:
			self.image.SetScale(self.assetScale, self.assetScale)

	def __Run(self):
		if self.event:
			self.event()

	def __OnTap(self, x, y):
		self.__Run()

	def OnMouseOverIn(self):
		self.hover = True
		self.__Refresh()

	def OnMouseOverOut(self):
		self.hover = False
		if self.pressed:
			self.pressed = False
		self.__Refresh()

	def OnMouseLeftButtonDown(self):
		self.pressed = True
		self.__Refresh()
		return True

	def OnMouseLeftButtonUp(self):
		wasPressed = self.pressed
		self.pressed = False
		self.__Refresh()
		if wasPressed and self.IsIn():
			self.__Run()
		return True


class Gauge(object):
	def __init__(self, parent, track, fill, x, y, showText):
		self.track = uiMobileStyle.CreateImage(parent, track, x, y)
		(width, height) = uiMobileStyle.AssetSize(track)
		inset = GAUGE_INSET if fill.startswith("gauge_") else 0
		self.fill = uiMobileStyle.CreateImage(parent, fill, x + inset, y + inset)
		self.ratio = -1.0
		self.text = None
		if showText:
			self.text = uiMobileStyle.CreateText(parent, "", x + width // 2, y + height // 2 - 8, BAR_TEXT_COLOR, uiMobileStyle.FONT_SMALL, "center", True)

	def SetValue(self, current, maximum):
		ratio = 0.0
		if maximum > 0:
			ratio = max(0.0, min(1.0, float(current) / maximum))
		if ratio != self.ratio:
			self.ratio = ratio
			self.fill.SetRenderingRect(0.0, 0.0, ratio - 1.0, 0.0)
		if self.text:
			self.text.SetText("%s / %s" % (FormatNumber(min(current, maximum)), FormatNumber(maximum)))
		return ratio


class StatusBar(ui.Window):
	def __init__(self):
		ui.Window.__init__(self, "UI")
		self.SetSize(STATUS_WIDTH, STATUS_HEIGHT)
		ui.EnableSingleTap(self)

		self.event = None
		self.nextRefreshTime = 0.0
		self.race = -1
		self.lowHealth = None

		self.frame = uiMobileStyle.CreateImage(self, "status_frame")

		self.face = ui.ExpandedImageBox()
		self.face.SetParent(self)
		self.face.AddFlag("not_pick")
		self.face.SetPosition(FACE_CENTER[0] - FACE_SIZE // 2, FACE_CENTER[1] - FACE_SIZE // 2)
		self.face.Show()

		self.levelText = uiMobileStyle.CreateText(self, "", FACE_CENTER[0], LEVEL_CENTER_Y - 8, uiMobileStyle.BRIGHT_COLOR, uiMobileStyle.FONT_SMALL, "center", True)
		self.nameText = uiMobileStyle.CreateText(self, "", BAR_X, NAME_Y, uiMobileStyle.BRIGHT_COLOR, uiMobileStyle.FONT_NORMAL, "left", True)
		self.expText = uiMobileStyle.CreateText(self, "", BAR_X + BAR_WIDTH, NAME_Y + 1, uiMobileStyle.LABEL_COLOR, uiMobileStyle.FONT_SMALL, "right", True)

		self.hpGauge = Gauge(self, "gauge_hp_trough", "gauge_hp_fill", BAR_X, HP_Y, True)
		self.spGauge = Gauge(self, "gauge_sp_trough", "gauge_sp_fill", BAR_X, SP_Y, True)
		self.stGauge = Gauge(self, "gauge_st_trough", "gauge_st_fill", BAR_X, ST_Y, False)
		self.expGauge = Gauge(self, "bar_exp_track", "bar_exp_fill", BAR_X, EXP_Y, False)

		self.SetTouchTapEvent(ui.__mem_func__(self.__OnTap))
		self.RefreshStatus()

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.event = None
		self.eventTouchTap = None
		self.frame = None
		self.face = None
		self.levelText = None
		self.nameText = None
		self.expText = None
		self.hpGauge = None
		self.spGauge = None
		self.stGauge = None
		self.expGauge = None
		self.Hide()

	def SetEvent(self, event):
		self.event = event

	def __OnTap(self, x, y):
		if self.event:
			self.event()

	def OnMouseLeftButtonDown(self):
		return True

	def OnMouseLeftButtonUp(self):
		if self.event and self.IsIn():
			self.event()
		return True

	def __RefreshFace(self):
		race = player.GetRace()
		if race == self.race:
			return
		self.race = race
		try:
			import uiCharacter
			fileName = uiCharacter.FACE_IMAGE_DICT[race]
		except Exception:
			return
		face = "status_face_%s" % fileName.replace("\\", "/").split("/")[-1].split(".")[0].lower()
		if uiMobileStyle.HasAsset(face):
			uiMobileStyle.LoadAsset(self.face, face)
			return
		self.face.LoadImage(fileName)
		width = max(1, self.face.GetWidth())
		height = max(1, self.face.GetHeight())
		self.face.SetScale(float(FACE_SIZE) / width, float(FACE_SIZE) / height)

	def RefreshStatus(self):
		self.__RefreshFace()

		currentHP = player.GetStatus(player.HP)
		maximumHP = player.GetStatus(player.MAX_HP)
		currentEXP = player.GetStatus(player.EXP)
		nextEXP = player.GetStatus(player.NEXT_EXP)

		healthRatio = self.hpGauge.SetValue(currentHP, maximumHP)
		self.spGauge.SetValue(player.GetStatus(player.SP), player.GetStatus(player.MAX_SP))
		self.stGauge.SetValue(player.GetStatus(player.STAMINA), player.GetStatus(player.MAX_STAMINA))
		self.expGauge.SetValue(currentEXP, nextEXP)

		lowHealth = maximumHP > 0 and healthRatio < LOW_HP_RATIO
		if lowHealth != self.lowHealth:
			self.lowHealth = lowHealth
			self.hpGauge.text.SetPackedFontColor(LOW_HP_TEXT_COLOR if lowHealth else BAR_TEXT_COLOR)

		self.nameText.SetText(player.GetName())
		self.levelText.SetText(str(player.GetStatus(player.LEVEL)))

		percent = 0.0
		if nextEXP > 0:
			percent = min(100.0, 100.0 * currentEXP / nextEXP)
		self.expText.SetText(("EXP %%%.1f" % percent).replace(".", ","))

	def OnUpdate(self):
		now = app.GetTime()
		if now < self.nextRefreshTime:
			return
		self.nextRefreshTime = now + STATUS_REFRESH_INTERVAL
		self.RefreshStatus()


class ButtonRow(object):
	def __init__(self, names, size):
		self.buttons = {}
		self.order = []
		self.size = size
		self.gap = 0
		self.x = 0
		self.y = 0
		self.orientation = "horizontal"
		self.visible = True
		for name in names:
			button = HudButton(size, name)
			self.buttons[name] = button
			self.order.append(name)

	def Destroy(self):
		for button in self.buttons.values():
			button.Destroy()
		self.buttons = {}
		self.order = []

	def SetEvent(self, name, event):
		if event is None:
			self.buttons[name].Hide()
			self.order.remove(name)
			return
		self.buttons[name].SetEvent(event)

	def GetButton(self, name):
		return self.buttons.get(name)

	def SetLongPressEvent(self, name, event):
		button = self.buttons.get(name)
		if button:
			button.SetLongPressEvent(event)

	def PlaceHorizontal(self, x, y, size, gap):
		self.x = x
		self.y = y
		self.size = size
		self.gap = gap
		self.orientation = "horizontal"
		for (index, name) in enumerate(self.order):
			self.buttons[name].SetPosition(x + index * (size + gap), y)

	def PlaceVertical(self, positions):
		self.orientation = "vertical"
		if positions:
			self.x, self.y = positions[0]
			if len(positions) > 1:
				self.gap = positions[1][1] - positions[0][1] - self.size
		for (name, (x, y)) in zip(self.order, positions):
			self.buttons[name].SetPosition(x, y)

	def SetPosition(self, x, y):
		self.x = x
		self.y = y
		if self.orientation == "horizontal":
			self.PlaceHorizontal(x, y, self.size, self.gap)
		else:
			positions = [(x, y + i * (self.size + self.gap)) for i in range(len(self.order))]
			self.PlaceVertical(positions)

	def GetLocalPosition(self):
		return (getattr(self, "x", 0), getattr(self, "y", 0))

	def IsShow(self):
		return getattr(self, "visible", True)

	def Show(self):
		self.visible = True
		for name in self.order:
			self.buttons[name].Show()

	def Hide(self):
		self.visible = False
		for button in self.buttons.values():
			button.Hide()


class ChatToggle(uiMobileStyle.Pressable):
	def __init__(self, width, height):
		uiMobileStyle.Pressable.__init__(self, width, height)

		self.frame = uiMobileStyle.NineSlicePanel(CHAT_BAR_FRAME)
		self.frame.SetParent(self)
		self.frame.AddFlag("not_pick")
		self.frame.SetSize(width, height)
		self.frame.Show()

		self.icon = uiMobileStyle.CreateImage(self, CHAT_ICON)
		(iconWidth, iconHeight) = uiMobileStyle.ImageSize(self.icon)
		self.icon.SetPosition(PILL_PADDING + 4, (height - iconHeight) // 2)

		self.title = uiMobileStyle.CreateImage(self, CHAT_TITLE_ASSET % "normal")
		(titleWidth, titleHeight) = uiMobileStyle.ImageSize(self.title)
		titleX = (width - titleWidth) // 2
		self.title.SetPosition(titleX, (height - titleHeight) // 2)
		self.titleState = "normal"

		self.ornaments = []
		iconRight = PILL_PADDING + 4 + iconWidth
		rightLimit = width - PILL_PADDING - CHAT_RIGHT_RESERVED
		for side in ("left", "right"):
			ornament = uiMobileStyle.CreateImage(self, CHAT_ORNAMENT_ASSET % side)
			(ornamentWidth, ornamentHeight) = uiMobileStyle.ImageSize(ornament)
			if side == "left":
				ornamentX = titleX - CHAT_ORNAMENT_GAP - ornamentWidth
			else:
				ornamentX = titleX + titleWidth + CHAT_ORNAMENT_GAP
			ornament.SetPosition(ornamentX, (height - ornamentHeight) // 2)
			if ornamentX < iconRight + CHAT_ORNAMENT_GAP or ornamentX + ornamentWidth > rightLimit:
				ornament.Hide()
			self.ornaments.append(ornament)

		self.arrow = uiMobileStyle.CreateImage(self, CHAT_EXPAND_ICON)
		(arrowWidth, arrowHeight) = uiMobileStyle.ImageSize(self.arrow)
		self.arrow.SetPosition(width - PILL_PADDING - arrowWidth, (height - arrowHeight) // 2)
		self.arrowLeft = width - PILL_PADDING - arrowWidth

		self.badge = uiMobileStyle.NineSlicePanel("chat_badge")
		self.badge.SetParent(self)
		self.badge.AddFlag("not_pick")
		self.badge.Hide()
		self.badgeText = uiMobileStyle.CreateText(self, "", 0, height // 2 - 7, uiMobileStyle.BRIGHT_COLOR, uiMobileStyle.FONT_SMALL, "center")
		self.badgeText.Hide()
		self.badgeValue = 0

	def Destroy(self):
		uiMobileStyle.Pressable.Destroy(self)
		self.frame = None
		self.icon = None
		self.title = None
		self.ornaments = []
		self.arrow = None
		self.badge = None
		self.badgeText = None

	def RefreshVisual(self):
		if not getattr(self, "title", None):
			return
		state = "active" if self.pressed or self.hovered else "normal"
		if state != self.titleState:
			self.titleState = state
			uiMobileStyle.LoadAsset(self.title, CHAT_TITLE_ASSET % state)

	def SetUnreadCount(self, count):
		count = max(0, count)
		if count == self.badgeValue:
			return
		self.badgeValue = count
		if count <= 0:
			self.badge.Hide()
			self.badgeText.Hide()
			return
		text = str(min(count, BADGE_LIMIT)) + ("+" if count > BADGE_LIMIT else "")
		width = max(BADGE_MIN_WIDTH, uiMobileStyle.TextWidth(text, uiMobileStyle.FONT_SMALL) + 12)
		x = self.arrowLeft - 8 - width
		self.badge.SetSize(width, BADGE_HEIGHT)
		self.badge.SetPosition(x, (self.GetHeight() - BADGE_HEIGHT) // 2)
		self.badgeText.SetText(text)
		self.badgeText.SetPosition(x + width // 2, self.GetHeight() // 2 - 7)
		self.badge.Show()
		self.badgeText.Show()


class ChatController(object):
	def __init__(self, interface, toggle):
		self.interface = proxy(interface)
		self.toggle = toggle
		self.expanded = False
		self.visible = True
		self.panel = uiMobileChat.ChatPanel(interface)
		self.panel.SetCollapseEvent(ui.__mem_func__(self.Collapse))
		self.panel.Hide()
		self.seenLineCount = self.__GetLineCount()
		self.toggle.SetEvent(ui.__mem_func__(self.Expand))

	def __GetChatWindow(self):
		try:
			return self.interface.wndChat
		except ReferenceError:
			return None

	def __GetLineCount(self):
		chatID = getattr(self.panel, "chatID", None) if self.panel else None
		if chatID is None:
			return 0
		try:
			return chat.GetLineCount(chatID)
		except Exception:
			return 0

	def Place(self):
		(toggleX, toggleY) = self.toggle.GetGlobalPosition()
		centerX = toggleX + self.toggle.GetWidth() // 2
		x = max(SCREEN_GAP, min(wndMgr.GetScreenWidth() - SCREEN_GAP - uiMobileChat.PANEL_WIDTH, centerX - uiMobileChat.PANEL_WIDTH // 2))
		y = toggleY + self.toggle.GetHeight() - uiMobileChat.PANEL_HEIGHT
		self.panel.SetHomePosition(x, y)
		self.panel.SetCollapsedBox(toggleX - x, toggleY - y, self.toggle.GetWidth(), self.toggle.GetHeight())

	def Restore(self):
		window = self.__GetChatWindow()
		if window:
			window.Show()
			window.Refresh()

	def Destroy(self):
		if self.panel:
			self.panel.Destroy()
		self.panel = None
		self.toggle = None
		self.interface = None

	def Expand(self):
		self.expanded = True
		self.toggle.Hide()
		self.panel.Open()
		self.toggle.SetUnreadCount(0)

	def Collapse(self, animate = True):
		self.expanded = False
		self.seenLineCount = self.__GetLineCount()
		if not self.panel:
			self.__OnPanelClosed()
			return
		if animate:
			self.panel.Close(ui.__mem_func__(self.__OnPanelClosed))
			return
		self.panel.CloseNow()
		self.__OnPanelClosed()

	def __OnPanelClosed(self):
		if self.toggle and self.visible and not self.expanded:
			self.toggle.Show()

	def Hide(self):
		self.visible = False
		if self.expanded:
			self.Collapse(False)
		elif self.panel:
			self.panel.CloseNow()
		self.toggle.Hide()

	def Show(self):
		self.visible = True
		if not self.expanded and not (self.panel and self.panel.IsShow()):
			self.toggle.Show()

	def __ReleaseDesktopChat(self, window):
		if window.IsEditMode():
			window.CloseChat()
			if not self.expanded:
				self.Expand()
			self.panel.FocusInput()
		if window.IsShow():
			window.Hide()

	def Update(self):
		window = self.__GetChatWindow()
		if window:
			self.__ReleaseDesktopChat(window)

		lineCount = self.__GetLineCount()
		if self.expanded:
			self.seenLineCount = lineCount
		else:
			self.toggle.SetUnreadCount(lineCount - self.seenLineCount)


class NotificationLayout(object):
	def __init__(self, gameButtonWindow):
		self.window = proxy(gameButtonWindow)
		self.originalPositions = {}

	def Apply(self, x, y):
		try:
			buttons = self.window.gameButtonDict
		except ReferenceError:
			return
		for (index, name) in enumerate(NOTIFICATION_ORDER):
			button = buttons.get(name)
			if not button:
				continue
			if name not in self.originalPositions:
				self.originalPositions[name] = button.GetLocalPosition()
			button.SetPosition(x + index * NOTIFICATION_STEP, y)

	def HidePointButtons(self):
		try:
			buttons = self.window.gameButtonDict
		except ReferenceError:
			return
		for name in HIDDEN_NOTIFICATIONS:
			button = buttons.get(name)
			if button and button.IsShow():
				button.Hide()

	def Restore(self):
		try:
			buttons = self.window.gameButtonDict
		except ReferenceError:
			return
		for (name, (x, y)) in self.originalPositions.items():
			button = buttons.get(name)
			if button:
				button.SetPosition(x, y)
		self.originalPositions = {}


def RunMount():
	net.SendChatPacket("/ride")


def RunPickup():
	player.PickCloseItem()


def RunAutoTarget():
	priority = 0
	try:
		import uiMobileHud
		priority = uiMobileHud.GetTargetPriority()
	except Exception:
		pass
	if hasattr(player, "AutoTarget"):
		try:
			player.AutoTarget(priority)
			targetVID = player.GetTargetVID()
			if targetVID != 0 and (chr.IsEnemy(targetVID) or chr.IsStone(targetVID)):
				player.SetAutoAttackTargetActorID(targetVID)
		except Exception:
			pass
