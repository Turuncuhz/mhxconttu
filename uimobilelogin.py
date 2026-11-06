from __future__ import division
# Cynex: barbaros giris ekraninin dokunmatik yerlesimi - giris/kanal/hesap mantigi barbaros'un kendi kodu
import app
import dbg
import os
import wndMgr
import constInfo
import localeInfo
import serverInfo
import uiScriptLocale
import ui
import introLogin
import uiMobileCompat
import uiMobileHud
import uiMobileStyle

from _weakref import proxy
from uiMobileWidgets import GuardAutoFocus

SCREEN_EDGE = 48
TOP_MARGIN = 10
PARK_POSITION = -4000

ACCOUNT_PANEL_WIDTH = 340
ACCOUNT_INSET = 8
ACCOUNT_HEADER_HEIGHT = 44
ACCOUNT_ROW_HEIGHT = 60
ACCOUNT_ROW_WIDTH = ACCOUNT_PANEL_WIDTH - ACCOUNT_INSET * 2
ACCOUNT_SLOT_COUNT = 4
ACCOUNT_TEXT_X = 66
AVATAR_SIZE = 44
DELETE_SIZE = 40
DELETE_CONFIRM_TIME = 3.0

CARD_WIDTH = 440
CARD_PADDING_X = 24
CARD_PADDING_Y = 22
CARD_GAP = 12
INNER_WIDTH = CARD_WIDTH - CARD_PADDING_X * 2
SELECTOR_HEIGHT = 56
SELECTOR_GAP = 8
SELECTOR_TOP = 30
FIELD_HEIGHT = 54
FIELD_GAP = 10
TOGGLE_HEIGHT = 30
LOGIN_BUTTON_KEY = "primary_392x58"
LOGIN_BUTTON_HEIGHT = 58
EXIT_BUTTON_HEIGHT = 48

CHIP_WIDTH = 104
CHIP_HEIGHT = 56
CHIP_GAP = 8
CHIP_COLUMNS = 4
SERVER_CARD_HEIGHT = 56
PICKER_PADDING_X = 30
PICKER_TOP = 28
PICKER_TITLE_HEIGHT = 44
PICKER_LABEL_HEIGHT = 22
PICKER_SECTION_GAP = 16
PICKER_CLOSE_WIDTH = 180
PICKER_CLOSE_HEIGHT = 48
PICKER_BOTTOM = 28
PICKER_DIM_ALPHA = 150
PICKER_EMPTY_HEIGHT = 56
REGION_ID = 0

REFRESH_INTERVAL = 1.0
CONFIG_REMEMBER_ACCOUNT = "REMEMBER_ACCOUNT"
CONFIG_PREFERRED_SERVER = "PREFERRED_SERVER"

FIELD_NAMES = (
	("ID_EditLine", "LOGIN_ID"),
	("Password_EditLine", "LOGIN_PASSWORD"),
	("pin_EditLine", "MOBILE_LOGIN_PIN"),
)
PARKED_NAMES = ("ConnectBoard", "ConnectBoard2", "LoginBoard", "KayitBoard")
PARKED_BUTTONS = ("idButton", "sifreButton", "pinButton", "LoginButton", "LoginExitButton", "SelectConnectButton", "KaydetConnectButton")
# Cynex: serverInfo.STATE_DICT sirasi: kapali, onerilen, yogun, dolu
CHANNEL_STATES = {
	1 : ("dot_normal", "MOBILE_CHANNEL_NORMAL"),
	2 : ("dot_busy", "MOBILE_CHANNEL_BUSY"),
	3 : ("dot_full", "MOBILE_CHANNEL_FULL"),
}


def Locale(name):
	return getattr(uiScriptLocale, name, name)


def SetVisible(window, visible):
	if not window:
		return
	if visible and not window.IsShow():
		window.Show()
	elif not visible and window.IsShow():
		window.Hide()


def StripColor(text):
	# Cynex: |cAARRGGBB ... |r renk kodlari
	result = ""
	index = 0
	length = len(text)
	while index < length:
		if text[index] == "|" and index + 1 < length:
			mark = text[index + 1]
			if mark in "cC" and index + 10 <= length:
				index += 10
				continue
			if mark in "rRhH":
				index += 2
				continue
		result += text[index]
		index += 1
	return result.strip()


def ChannelStateKey(stateName):
	for (key, name) in serverInfo.STATE_DICT.items():
		if name == stateName:
			return key
	return 0


def ChannelStateVisual(stateKey):
	(dotName, labelName) = CHANNEL_STATES.get(stateKey, ("dot_closed", "MOBILE_CHANNEL_CLOSED"))
	return (dotName, Locale(labelName))


def GetRegionDict():
	try:
		return serverInfo.REGION_DICT[REGION_ID]
	except (KeyError, AttributeError):
		return {}


def ServerName(serverID):
	try:
		return StripColor(GetRegionDict()[serverID]["name"])
	except (KeyError, TypeError):
		return str(serverID)


def ServerChannelCount(serverID):
	try:
		return len(GetRegionDict()[serverID]["channel"])
	except (KeyError, TypeError):
		return 0


def AccountFileName(slot):
	return "%soldhesap%d.cfg" % (getattr(constInfo, "CLIENT_YOL2", ""), slot)


class ChannelChip(uiMobileStyle.Pressable):
	def __init__(self, width):
		uiMobileStyle.Pressable.__init__(self, width, CHIP_HEIGHT)
		self.panel = uiMobileStyle.CreatePanel(self, "field", 0, 0, width, CHIP_HEIGHT, False)
		self.name = uiMobileStyle.CreateText(self, "", width // 2, 9, uiMobileStyle.BRIGHT_COLOR, uiMobileStyle.FONT_MEDIUM, "center")
		self.dot = uiMobileStyle.CreateImage(self, "dot_closed")
		self.state = uiMobileStyle.CreateText(self, "", 0, 31, uiMobileStyle.MUTED_COLOR, uiMobileStyle.FONT_SMALL)
		self.stateKey = None

	def Destroy(self):
		uiMobileStyle.Pressable.Destroy(self)
		self.panel = None
		self.name = None
		self.dot = None
		self.state = None

	def SetChannel(self, name, stateKey):
		self.name.SetText(name)
		if stateKey == self.stateKey:
			return
		self.stateKey = stateKey
		(dotName, label) = ChannelStateVisual(stateKey)
		uiMobileStyle.LoadAsset(self.dot, dotName)
		self.state.SetText(label)
		textWidth = uiMobileStyle.TextWidth(label, uiMobileStyle.FONT_SMALL)
		startX = (self.GetWidth() - 7 - 5 - textWidth) // 2
		self.dot.SetPosition(startX, 36)
		self.state.SetPosition(startX + 12, 31)

	def SetSelected(self, selected):
		self.panel.SetStyle("chip_active" if selected else "field")


class ServerCard(uiMobileStyle.Pressable):
	def __init__(self, width):
		uiMobileStyle.Pressable.__init__(self, width, SERVER_CARD_HEIGHT)
		self.panel = uiMobileStyle.CreatePanel(self, "field", 0, 0, width, SERVER_CARD_HEIGHT, False)
		self.name = uiMobileStyle.CreateText(self, "", width // 2, 9, uiMobileStyle.BRIGHT_COLOR, uiMobileStyle.FONT_MEDIUM, "center")
		self.detail = uiMobileStyle.CreateText(self, "", width // 2, 31, uiMobileStyle.MUTED_COLOR, uiMobileStyle.FONT_SMALL, "center")
		self.selected = False

	def Destroy(self):
		uiMobileStyle.Pressable.Destroy(self)
		self.panel = None
		self.name = None
		self.detail = None

	def SetServer(self, name, channelCount, selected):
		self.name.SetText(name)
		self.detail.SetText(Locale("MOBILE_SERVER_CHANNEL_COUNT") % channelCount if channelCount else "")
		self.selected = selected
		self.RefreshVisual()

	def RefreshVisual(self):
		if not getattr(self, "panel", None):
			return
		self.panel.SetStyle("chip_active" if self.selected else "field")
		self.name.SetPackedFontColor(uiMobileStyle.GOLD_COLOR if self.selected or self.pressed else uiMobileStyle.BRIGHT_COLOR)


class SelectorButton(uiMobileStyle.Pressable):
	def __init__(self, width, header):
		uiMobileStyle.Pressable.__init__(self, width, SELECTOR_HEIGHT)
		self.panel = uiMobileStyle.CreatePanel(self, "field", 0, 0, width, SELECTOR_HEIGHT, False)
		self.header = uiMobileStyle.CreateText(self, header, 14, 8, uiMobileStyle.MUTED_COLOR, uiMobileStyle.FONT_SMALL)
		self.dot = uiMobileStyle.CreateImage(self, "dot_closed", 14, 33)
		self.dot.Hide()
		self.value = uiMobileStyle.CreateText(self, "", 14, 26, uiMobileStyle.BRIGHT_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.chevron = uiMobileStyle.CreateCenteredImage(self, "icon_chevron", width - 18, SELECTOR_HEIGHT // 2)

	def Destroy(self):
		uiMobileStyle.Pressable.Destroy(self)
		self.panel = None
		self.header = None
		self.dot = None
		self.value = None
		self.chevron = None

	def SetValue(self, text, dotName = None):
		if dotName:
			uiMobileStyle.LoadAsset(self.dot, dotName)
			self.dot.Show()
			self.value.SetPosition(26, 26)
		else:
			self.dot.Hide()
			self.value.SetPosition(14, 26)
		self.value.SetText(text)

	def RefreshVisual(self):
		if getattr(self, "panel", None):
			self.panel.SetStyle("chip_active" if self.pressed or self.hovered else "field")


class SelectionPicker(uiMobileStyle.Pressable):
	def __init__(self, owner, screenWidth, screenHeight):
		uiMobileStyle.Pressable.__init__(self, screenWidth, screenHeight)
		self.owner = proxy(owner)
		self.dim = uiMobileStyle.CreateBar(self, uiMobileStyle.Color(0, 0, 0, PICKER_DIM_ALPHA), 0, 0, screenWidth, screenHeight)
		self.panel = uiMobileStyle.CreateOrnatePanel(self, 0, 0, 200, 200)
		self.title = uiMobileStyle.CreateText(self.panel, "", 0, PICKER_TOP, uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_LARGE, "center")
		self.serverLabel = uiMobileStyle.CreateText(self.panel, Locale("MOBILE_SERVER_HEADER"), 0, 0, uiMobileStyle.LABEL_COLOR, uiMobileStyle.FONT_SMALL)
		self.channelLabel = uiMobileStyle.CreateText(self.panel, Locale("MOBILE_CHANNEL_HEADER"), 0, 0, uiMobileStyle.LABEL_COLOR, uiMobileStyle.FONT_SMALL)
		self.emptyText = uiMobileStyle.CreateText(self.panel, Locale("MOBILE_CHANNELS_WAIT"), 0, 0, uiMobileStyle.MUTED_COLOR, uiMobileStyle.FONT_NORMAL, "center")
		self.closeButton = uiMobileStyle.PillButton(PICKER_CLOSE_WIDTH, PICKER_CLOSE_HEIGHT, Locale("MOBILE_CLOSE"), None, "pill", uiMobileStyle.SOFT_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.closeButton.SetParent(self.panel)
		self.closeButton.SetEvent(ui.__mem_func__(self.Close))
		self.closeButton.Show()
		self.serverCards = []
		self.chips = []
		self.layoutKey = None
		self.SetEvent(ui.__mem_func__(self.Close))

	def Destroy(self):
		for widget in self.serverCards + self.chips:
			widget.Destroy()
		self.serverCards = []
		self.chips = []
		self.closeButton.Destroy()
		self.closeButton = None
		uiMobileStyle.Pressable.Destroy(self)
		self.owner = None
		self.dim = None
		self.panel = None
		self.title = None
		self.serverLabel = None
		self.channelLabel = None
		self.emptyText = None

	def Close(self):
		if self.owner:
			self.owner.OnClosePicker()

	def __OnPickServer(self, index):
		if self.owner:
			self.owner.OnPickServer(index)

	def __OnPickChannel(self, index):
		if self.owner:
			self.owner.OnPickChannel(index)

	def __Rebuild(self, widgets, count, factory, event):
		while len(widgets) > count:
			widgets.pop().Destroy()
		while len(widgets) < count:
			widget = factory()
			widget.SetParent(self.panel)
			widget.SetEvent(ui.__mem_func__(event), len(widgets))
			widget.Show()
			widgets.append(widget)

	def __Layout(self, serverCount, channelCount):
		gridWidth = CHIP_COLUMNS * CHIP_WIDTH + (CHIP_COLUMNS - 1) * CHIP_GAP
		width = gridWidth + PICKER_PADDING_X * 2
		left = PICKER_PADDING_X
		y = PICKER_TOP + PICKER_TITLE_HEIGHT

		showServers = serverCount > 1
		SetVisible(self.serverLabel, showServers)
		if showServers:
			self.serverLabel.SetPosition(left, y)
			y += PICKER_LABEL_HEIGHT
			cardWidth = (gridWidth - CHIP_GAP * (serverCount - 1)) // serverCount
			for (index, card) in enumerate(self.serverCards):
				card.SetPosition(left + index * (cardWidth + CHIP_GAP), y)
			y += SERVER_CARD_HEIGHT + PICKER_SECTION_GAP

		self.channelLabel.SetPosition(left, y)
		y += PICKER_LABEL_HEIGHT
		if channelCount:
			self.emptyText.Hide()
			rows = (channelCount + CHIP_COLUMNS - 1) // CHIP_COLUMNS
			for (index, chip) in enumerate(self.chips):
				chip.SetPosition(left + (index % CHIP_COLUMNS) * (CHIP_WIDTH + CHIP_GAP), y + (index // CHIP_COLUMNS) * (CHIP_HEIGHT + CHIP_GAP))
			y += rows * CHIP_HEIGHT + (rows - 1) * CHIP_GAP
		else:
			self.emptyText.SetPosition(width // 2, y + PICKER_EMPTY_HEIGHT // 2 - 9)
			self.emptyText.Show()
			y += PICKER_EMPTY_HEIGHT

		y += PICKER_SECTION_GAP + 2
		self.closeButton.SetPosition((width - PICKER_CLOSE_WIDTH) // 2, y)
		height = y + PICKER_CLOSE_HEIGHT + PICKER_BOTTOM
		self.panel.SetSize(width, height)
		self.panel.SetPosition((self.GetWidth() - width) // 2, max(TOP_MARGIN, (self.GetHeight() - height) // 2))
		self.title.SetPosition(width // 2, PICKER_TOP)
		self.title.SetText(Locale("MOBILE_SELECT_SERVER_TITLE" if showServers else "MOBILE_SELECT_CHANNEL_TITLE"))

	def SetContent(self, servers, channels, selectedChannel):
		serverCount = len(servers)
		if serverCount > 1:
			gridWidth = CHIP_COLUMNS * CHIP_WIDTH + (CHIP_COLUMNS - 1) * CHIP_GAP
			cardWidth = (gridWidth - CHIP_GAP * (serverCount - 1)) // serverCount
			if self.serverCards and self.serverCards[0].GetWidth() != cardWidth:
				self.__Rebuild(self.serverCards, 0, None, None)
			self.__Rebuild(self.serverCards, serverCount, lambda: ServerCard(cardWidth), self.__OnPickServer)
		else:
			self.__Rebuild(self.serverCards, 0, None, None)
		self.__Rebuild(self.chips, len(channels), lambda: ChannelChip(CHIP_WIDTH), self.__OnPickChannel)

		layoutKey = (serverCount, len(channels))
		if layoutKey != self.layoutKey:
			self.layoutKey = layoutKey
			self.__Layout(serverCount, len(channels))

		for (card, (name, channelCount, selected)) in zip(self.serverCards, servers):
			card.SetServer(name, channelCount, selected)
		for (index, (name, state)) in enumerate(channels):
			self.chips[index].SetChannel(name, state)
			self.chips[index].SetSelected(index == selectedChannel)


class AccountRow(uiMobileStyle.Pressable):
	def __init__(self, owner):
		uiMobileStyle.Pressable.__init__(self, ACCOUNT_ROW_WIDTH, ACCOUNT_ROW_HEIGHT)
		self.owner = proxy(owner)
		self.slot = 0
		self.isAddRow = False
		self.selected = False
		self.confirmUntil = 0.0
		self.confirmShown = None

		self.highlight = uiMobileStyle.CreateBar(self, uiMobileStyle.LIST_SELECT_COLOR, 0, 0, ACCOUNT_ROW_WIDTH, ACCOUNT_ROW_HEIGHT)
		self.highlight.Hide()
		self.accent = uiMobileStyle.CreateBar(self, uiMobileStyle.LIST_ACCENT_COLOR, 0, 10, 2, ACCOUNT_ROW_HEIGHT - 20)
		self.accent.Hide()
		self.divider = uiMobileStyle.CreateBar(self, uiMobileStyle.DIVIDER_COLOR, ACCOUNT_TEXT_X, ACCOUNT_ROW_HEIGHT - 1, ACCOUNT_ROW_WIDTH - ACCOUNT_TEXT_X - 10, 1)

		avatarY = (ACCOUNT_ROW_HEIGHT - AVATAR_SIZE) // 2
		self.avatar = uiMobileStyle.CreateImage(self, "avatar_gold", 10, avatarY)
		self.initial = uiMobileStyle.CreateText(self, "", 10 + AVATAR_SIZE // 2, avatarY + 11, uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_LARGE, "center")
		self.plus = uiMobileStyle.CreateCenteredImage(self, "icon_plus", 10 + AVATAR_SIZE // 2, ACCOUNT_ROW_HEIGHT // 2)
		self.name = uiMobileStyle.CreateText(self, "", ACCOUNT_TEXT_X, 11, uiMobileStyle.BRIGHT_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.detail = uiMobileStyle.CreateText(self, "", ACCOUNT_TEXT_X, 33, uiMobileStyle.MUTED_COLOR, uiMobileStyle.FONT_SMALL)

		self.deleteButton = uiMobileStyle.Pressable(DELETE_SIZE, DELETE_SIZE)
		self.deleteButton.SetParent(self)
		self.deleteButton.SetPosition(ACCOUNT_ROW_WIDTH - DELETE_SIZE - 4, (ACCOUNT_ROW_HEIGHT - DELETE_SIZE) // 2)
		self.deleteIcon = uiMobileStyle.CreateCenteredImage(self.deleteButton, "icon_close", DELETE_SIZE // 2, DELETE_SIZE // 2)
		self.deleteButton.SetEvent(ui.__mem_func__(self.__OnDelete))
		self.deleteButton.Show()

		self.SetEvent(ui.__mem_func__(self.__OnSelect))

	def Destroy(self):
		self.deleteButton.Destroy()
		uiMobileStyle.Pressable.Destroy(self)
		self.deleteButton = None
		self.owner = None
		self.highlight = None
		self.accent = None
		self.divider = None
		self.avatar = None
		self.initial = None
		self.plus = None
		self.name = None
		self.detail = None
		self.deleteIcon = None

	def __OnSelect(self):
		if not self.owner:
			return
		if self.isAddRow:
			self.owner.OnAddAccount()
		else:
			self.owner.OnSelectAccount(self.slot)

	def __OnDelete(self):
		if not self.owner or self.isAddRow:
			return
		if self.confirmUntil > app.GetTime():
			self.__SetConfirm(False)
			self.owner.OnDeleteAccount(self.slot)
		else:
			self.__SetConfirm(True)

	def __SetConfirm(self, confirm):
		self.confirmUntil = app.GetTime() + DELETE_CONFIRM_TIME if confirm else 0.0
		self.confirmShown = confirm
		uiMobileStyle.SetCenteredAsset(self.deleteIcon, "icon_trash" if confirm else "icon_close", DELETE_SIZE // 2, DELETE_SIZE // 2)
		self.detail.SetText(Locale("MOBILE_DELETE_CONFIRM") if confirm else Locale("MOBILE_ACCOUNT_HINT"))
		self.detail.SetPackedFontColor(uiMobileStyle.DANGER_COLOR if confirm else uiMobileStyle.MUTED_COLOR)

	def SetAccount(self, slot, accountId, selected):
		self.slot = slot
		self.isAddRow = False
		self.selected = selected
		uiMobileStyle.LoadAsset(self.avatar, "avatar_gold")
		self.initial.SetText(accountId[:1].upper())
		self.initial.Show()
		self.plus.Hide()
		self.name.SetText(accountId)
		self.name.SetPackedFontColor(uiMobileStyle.BRIGHT_COLOR)
		self.deleteButton.Show()
		if self.confirmUntil <= app.GetTime() and self.confirmShown is not False:
			self.__SetConfirm(False)
		self.RefreshVisual()

	def SetAddRow(self):
		self.slot = 0
		self.isAddRow = True
		self.selected = False
		self.confirmUntil = 0.0
		self.confirmShown = None
		uiMobileStyle.LoadAsset(self.avatar, "avatar_empty")
		self.initial.Hide()
		self.plus.Show()
		self.name.SetText(Locale("MOBILE_ADD_ACCOUNT"))
		self.name.SetPackedFontColor(uiMobileStyle.LABEL_COLOR)
		self.detail.SetText(Locale("MOBILE_ADD_ACCOUNT_HINT"))
		self.detail.SetPackedFontColor(uiMobileStyle.MUTED_COLOR)
		self.deleteButton.Hide()
		self.RefreshVisual()

	def SetDividerVisible(self, visible):
		SetVisible(self.divider, visible)

	def RefreshVisual(self):
		if not getattr(self, "highlight", None):
			return
		SetVisible(self.highlight, self.selected or self.pressed)
		SetVisible(self.accent, self.selected)

	def OnUpdate(self):
		if self.confirmUntil and self.confirmUntil <= app.GetTime():
			self.__SetConfirm(False)


class AccountPanel(ui.Window):
	def __init__(self, owner):
		ui.Window.__init__(self)
		self.panel = uiMobileStyle.WindowPanel()
		self.panel.SetParent(self)
		self.panel.AddFlag("not_pick")
		self.panel.Show()
		self.header = uiMobileStyle.CreateText(self, Locale("MOBILE_SAVED_ACCOUNTS_HEADER"), 18, 16, uiMobileStyle.LABEL_COLOR, uiMobileStyle.FONT_SMALL)
		self.count = uiMobileStyle.CreateText(self, "", ACCOUNT_PANEL_WIDTH - 18, 16, uiMobileStyle.MUTED_COLOR, uiMobileStyle.FONT_SMALL, "right")
		self.headerLine = uiMobileStyle.CreateBar(self, uiMobileStyle.DIVIDER_COLOR, ACCOUNT_INSET + 10, ACCOUNT_HEADER_HEIGHT - 4, ACCOUNT_ROW_WIDTH - 20, 1)
		self.rows = []
		for index in range(ACCOUNT_SLOT_COUNT + 1):
			row = AccountRow(owner)
			row.SetParent(self)
			row.Hide()
			self.rows.append(row)
		self.signature = None

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		for row in self.rows:
			row.Destroy()
		self.rows = []
		self.panel = None
		self.header = None
		self.count = None
		self.headerLine = None

	def SetAccounts(self, accounts, selectedSlot):
		saved = [(slot, accountId) for (slot, accountId) in accounts if accountId]
		hasFreeSlot = len(saved) < len(accounts)
		visibleRows = len(saved) + (1 if hasFreeSlot else 0)

		for (index, (slot, accountId)) in enumerate(saved):
			self.rows[index].SetAccount(slot, accountId, slot == selectedSlot)
		if hasFreeSlot:
			self.rows[len(saved)].SetAddRow()

		for (index, row) in enumerate(self.rows):
			if index < visibleRows:
				row.SetPosition(ACCOUNT_INSET, ACCOUNT_HEADER_HEIGHT + index * ACCOUNT_ROW_HEIGHT)
				row.SetDividerVisible(index < visibleRows - 1)
				row.Show()
			else:
				row.Hide()

		self.count.SetText("%d/%d" % (len(saved), len(accounts)))
		height = ACCOUNT_HEADER_HEIGHT + visibleRows * ACCOUNT_ROW_HEIGHT + ACCOUNT_INSET
		if height != self.GetHeight():
			self.SetSize(ACCOUNT_PANEL_WIDTH, height)
			self.panel.SetSize(ACCOUNT_PANEL_WIDTH, height)
			(x, y) = self.GetLocalPosition()
			self.SetPosition(x, max(TOP_MARGIN, (wndMgr.GetScreenHeight() - height) // 2))




class MobileLoginWindow(introLogin.LoginWindow):
	def __init__(self, stream):
		self.mobileLayoutReady = False
		self.mobileWidgets = []
		self.fields = []
		self.accountPanel = None
		self.loginCard = None
		self.channelButton = None
		self.serverButton = None
		self.picker = None
		self.pickerRequested = False
		self.rememberToggle = None
		self.loginButton = None
		self.exitButton = None
		self.cardPosition = (0, 0)
		self.cardShifted = False
		self.autoConfirmPending = True
		self.preferredServerApplied = False
		self.selectedAccount = 0
		self.nextRefreshTime = 0.0
		introLogin.LoginWindow.__init__(self, stream)

	def Open(self):
		introLogin.LoginWindow.Open(self)
		try:
			self.__GuardFieldFocus()
			self.__ApplyMobileLayout()
		except Exception, error:
			dbg.TraceError("MobileLoginWindow.Open - layout error: %s" % error)

	# Cynex: barbaros Open() sonunda kimlik alanina odaklaniyor - telefonda klavye kendiliginden acilmasin
	def _LoginWindow__LoadScript(self, fileName):
		result = introLogin.LoginWindow._LoginWindow__LoadScript(self, fileName)
		try:
			self.__GuardFieldFocus()
		except Exception, error:
			dbg.TraceError("MobileLoginWindow focus guard: %s" % error)
		return result

	def __GuardFieldFocus(self):
		editLines = [self.GetChild2(editLineName) for (editLineName, labelName) in FIELD_NAMES]
		GuardAutoFocus([editLine for editLine in editLines if editLine])

	def Close(self):
		self.__DestroyMobileLayout()
		introLogin.LoginWindow.Close(self)

	def __DestroyMobileLayout(self):
		self.mobileLayoutReady = False
		if self.accountPanel:
			self.accountPanel.Destroy()
		if self.picker:
			self.picker.Destroy()
		for widget in self.mobileWidgets:
			destroy = getattr(widget, "Destroy", None)
			if destroy:
				destroy()
		self.accountPanel = None
		self.picker = None
		self.mobileWidgets = []
		self.fields = []
		self.loginCard = None
		self.channelButton = None
		self.serverButton = None
		self.rememberToggle = None
		self.loginButton = None
		self.exitButton = None

	def __Keep(self, widget):
		self.mobileWidgets.append(widget)
		return widget

	def __ApplyMobileLayout(self):
		if not self.GetChild2("LoginBoard"):
			return

		screenWidth = wndMgr.GetScreenWidth()
		screenHeight = wndMgr.GetScreenHeight()

		for name in PARKED_NAMES:
			child = self.GetChild2(name)
			if child:
				uiMobileStyle.ParkWindow(child)

		self.__ParkServerBoard()
		self.__BuildAccountPanel()
		self.__BuildLoginCard(screenWidth, screenHeight)

		self.picker = SelectionPicker(self, screenWidth, screenHeight)
		self.picker.SetParent(self)
		self.picker.SetPosition(0, 0)
		self.picker.Hide()

		self.mobileLayoutReady = True
		self.__RefreshAccounts()
		self.__RefreshChannels()
		self.__SyncVisibility()

	def __ParkServerBoard(self):
		# Cynex: barbaros __OpenServerBoard bu konumu kullanir - kanal secimi mobil secicide
		self.xServerBoard = PARK_POSITION
		self.yServerBoard = PARK_POSITION
		board = self.GetChild2("ServerBoard")
		if board:
			board.SetWindowHorizontalAlignLeft()
			board.SetWindowVerticalAlignTop()
			board.SetPosition(PARK_POSITION, PARK_POSITION)

	def __BuildAccountPanel(self):
		panel = AccountPanel(self)
		panel.SetParent(self)
		panel.SetPosition(SCREEN_EDGE, TOP_MARGIN)
		panel.SetSize(ACCOUNT_PANEL_WIDTH, 0)
		panel.Show()
		self.accountPanel = panel

	def __BuildLoginCard(self, screenWidth, screenHeight):
		card = self.__Keep(uiMobileStyle.OrnatePanel())
		card.SetParent(self)
		card.Show()
		self.loginCard = card

		selectorWidth = (INNER_WIDTH - SELECTOR_GAP) // 2
		self.channelButton = self.__Keep(SelectorButton(selectorWidth, Locale("MOBILE_CHANNEL_HEADER")))
		self.channelButton.SetParent(card)
		self.channelButton.SetEvent(ui.__mem_func__(self.__OpenPicker))
		self.channelButton.Show()
		self.serverButton = self.__Keep(SelectorButton(selectorWidth, Locale("MOBILE_SERVER_HEADER")))
		self.serverButton.SetParent(card)
		self.serverButton.SetEvent(ui.__mem_func__(self.__OpenPicker))
		self.serverButton.Show()

		for (editLineName, labelName) in FIELD_NAMES:
			field = self.__Keep(uiMobileStyle.Field(INNER_WIDTH, FIELD_HEIGHT, Locale(labelName)))
			field.SetParent(card)
			field.Show()
			editLine = self.GetChild2(editLineName)
			if editLine:
				field.Attach(editLine)
			self.fields.append(field)

		for name in PARKED_BUTTONS:
			child = self.GetChild2(name)
			if child:
				uiMobileStyle.ParkWindow(child)

		self.rememberToggle = self.__Keep(uiMobileStyle.Toggle(Locale("MOBILE_REMEMBER_ACCOUNT"), uiMobileHud.LoadConfig().get(CONFIG_REMEMBER_ACCOUNT, "0") == "1"))
		self.rememberToggle.SetParent(card)
		self.rememberToggle.SetChangeEvent(ui.__mem_func__(self.__OnRememberChanged))
		self.rememberToggle.Show()

		self.loginButton = self.__Keep(uiMobileStyle.PrimaryButton(LOGIN_BUTTON_KEY, "label_login"))
		self.loginButton.SetParent(card)
		self.loginButton.SetEvent(ui.__mem_func__(self.__OnClickLogin))
		self.loginButton.Show()

		self.exitButton = self.__Keep(uiMobileStyle.PillButton(INNER_WIDTH, EXIT_BUTTON_HEIGHT, Locale("MOBILE_EXIT_GAME"), None, "pill", uiMobileStyle.SOFT_COLOR, uiMobileStyle.FONT_MEDIUM))
		self.exitButton.SetParent(card)
		self.exitButton.SetEvent(ui.__mem_func__(self.__OnClickExit))
		self.exitButton.Show()

		self.__LayoutCard()

	def __LayoutCard(self):
		screenWidth = wndMgr.GetScreenWidth()
		screenHeight = wndMgr.GetScreenHeight()

		y = SELECTOR_TOP
		self.channelButton.SetPosition(CARD_PADDING_X, y)
		self.serverButton.SetPosition(CARD_PADDING_X + self.channelButton.GetWidth() + SELECTOR_GAP, y)
		y += SELECTOR_HEIGHT + CARD_GAP + 4
		for field in self.fields:
			field.SetPosition(CARD_PADDING_X, y)
			y += FIELD_HEIGHT + FIELD_GAP
		y += CARD_GAP - FIELD_GAP
		self.rememberToggle.SetPosition(CARD_PADDING_X, y)
		y += TOGGLE_HEIGHT + CARD_GAP
		self.loginButton.SetPosition(CARD_PADDING_X, y)
		y += LOGIN_BUTTON_HEIGHT + FIELD_GAP
		self.exitButton.SetPosition(CARD_PADDING_X, y)
		y += EXIT_BUTTON_HEIGHT + CARD_PADDING_Y + 8

		self.loginCard.SetSize(CARD_WIDTH, y)
		cardX = screenWidth - SCREEN_EDGE - CARD_WIDTH
		cardY = max(TOP_MARGIN, (screenHeight - y) // 2)
		self.cardPosition = (cardX, cardY)
		self.cardShifted = False
		self.loginCard.SetPosition(cardX, cardY)

	def __RunOriginalButton(self, buttonName):
		button = self.GetChild2(buttonName)
		if button:
			uiMobileStyle.RunButtonEvent(button)

	def __CallBase(self, name, *arguments):
		function = getattr(self, "_LoginWindow__%s" % name, None)
		if function is None:
			return False
		function(*arguments)
		return True

	def __ConfirmServer(self):
		if not self.__CallBase("OnClickSelectServerButton"):
			self.__RunOriginalButton("ServerSelectButton")

	def __IsServerBoardOpen(self):
		board = self.GetChild2("ServerBoard")
		return bool(board and board.IsShow())

	def __IsAwaitingServer(self):
		return self.autoConfirmPending and self.__IsServerBoardOpen()

	def __GetServerList(self):
		return self.GetChild2("ServerList")

	def __GetChannelList(self):
		return self.GetChild2("ChannelList")

	def __GetServerEntries(self):
		serverList = self.__GetServerList()
		if not serverList:
			return []
		return [serverList.keyDict.get(index, 0) for index in xrange(serverList.GetItemCount())]

	def __GetSelectedServerKey(self):
		serverList = self.__GetServerList()
		if not serverList or serverList.selectedLine < 0:
			return None
		return serverList.GetSelectedItem()

	def __GetPreferredServerIndex(self):
		entries = self.__GetServerEntries()
		if not entries:
			return -1
		try:
			savedServer = int(uiMobileHud.LoadConfig().get(CONFIG_PREFERRED_SERVER, "0"))
		except ValueError:
			savedServer = 0
		for (index, serverID) in enumerate(entries):
			if serverID == savedServer:
				return index
		return -1

	def __ApplyPreferredServer(self):
		self.preferredServerApplied = True
		index = self.__GetPreferredServerIndex()
		if index < 0:
			return False
		if self.__GetServerEntries()[index] == self.__GetSelectedServerKey():
			return False
		self.OnPickServer(index)
		return True

	def __AutoConfirmServer(self):
		if not self.autoConfirmPending:
			return
		channelList = self.__GetChannelList()
		if not channelList or not self.__IsServerBoardOpen():
			return
		if not self.preferredServerApplied and self.__ApplyPreferredServer():
			return
		if channelList.GetItemCount() == 0:
			return
		self.autoConfirmPending = False
		if not channelList.keyDict.has_key(channelList.selectedLine):
			channelList.SelectItem(0)
		self.__ConfirmServer()

	def __EnsureServerReady(self):
		self.__AutoConfirmServer()
		if self.__IsAwaitingServer():
			self.PopupRiot(Locale("MOBILE_CHANNELS_LOADING"))
			return False
		return True

	def __GetChannelEntries(self):
		channelList = self.__GetChannelList()
		if not channelList:
			return ([], -1)
		serverID = self.__GetSelectedServerKey()
		try:
			channelDict = GetRegionDict()[serverID]["channel"]
		except (KeyError, TypeError):
			channelDict = {}
		entries = []
		for index in xrange(channelList.GetItemCount()):
			data = channelDict.get(channelList.keyDict.get(index, -1))
			if data:
				entries.append((StripColor(data.get("name", "")), ChannelStateKey(data.get("state", ""))))
			else:
				entries.append((StripColor(channelList.textDict.get(index, "")), 0))
		return (entries, channelList.selectedLine)

	def __RefreshPicker(self):
		if not self.picker:
			return
		currentKey = self.__GetSelectedServerKey()
		servers = [(ServerName(serverID), ServerChannelCount(serverID), serverID == currentKey) for serverID in self.__GetServerEntries()]
		(channels, selectedChannel) = self.__GetChannelEntries()
		self.picker.SetContent(servers, channels, selectedChannel)

	def __OpenPicker(self):
		if not self.__GetServerEntries():
			self.__CallBase("RefreshServerList")
		if self.__GetSelectedServerKey() is None and self.__GetServerEntries():
			index = self.__GetPreferredServerIndex()
			self.OnPickServer(max(0, index))
		self.pickerRequested = True
		self.__RefreshPicker()
		self.picker.Show()
		self.picker.SetTop()

	def OnClosePicker(self):
		self.pickerRequested = False
		self.picker.Hide()
		if self.__IsServerBoardOpen() and not self.autoConfirmPending:
			if not self.__CallBase("OnClickExitServerButton"):
				self.__RunOriginalButton("ServerExitButton")
		self.__RefreshChannels()

	def OnPickServer(self, index):
		serverList = self.__GetServerList()
		if not serverList or not 0 <= index < serverList.GetItemCount():
			return
		try:
			serverList.SelectItem(index)
		except Exception, error:
			dbg.TraceError("MobileLoginWindow.OnPickServer: %s" % error)
		self.__RefreshPicker()

	def OnPickChannel(self, index):
		channelList = self.__GetChannelList()
		if channelList:
			channelList.SelectItem(index)
			self.autoConfirmPending = False
			self.__RememberServer()
			self.__ConfirmServer()
		self.pickerRequested = False
		self.picker.Hide()
		self.__RefreshChannels()

	def __RememberServer(self):
		serverKey = self.__GetSelectedServerKey()
		if serverKey is None:
			return
		uiMobileHud.LoadConfig()[CONFIG_PREFERRED_SERVER] = str(serverKey)
		uiMobileHud.SaveConfig()

	def OnPressEscapeKey(self):
		if self.picker and self.picker.IsShow():
			self.OnClosePicker()
			return True
		baseHandler = getattr(introLogin.LoginWindow, "OnPressEscapeKey", None)
		if baseHandler:
			return baseHandler(self)
		return False

	def __RefreshChannels(self):
		if not self.channelButton:
			return

		connectName = self.GetChild2("ConnectName")
		if connectName:
			rawText = StripColor(connectName.GetText())
			if rawText.startswith("K:") or rawText.startswith("Y:") or ":" in rawText:
				srvName = getattr(serverInfo, "SERVER_ADI", "Lucifer2")
				self.serverButton.SetValue(srvName)
				channelText = ""
			else:
				parts = rawText.split(",")
				self.serverButton.SetValue(parts[0].strip() if parts[0].strip() else getattr(serverInfo, "SERVER_ADI", "Lucifer2"))
				channelText = parts[1].strip() if len(parts) > 1 else ""
		else:
			channelText = ""

		(entries, selectedIndex) = self.__GetChannelEntries()
		if 0 <= selectedIndex < len(entries):
			(name, state) = entries[selectedIndex]
			(dotName, label) = ChannelStateVisual(state)
			self.channelButton.SetValue("%s %s %s" % (name, Locale("MOBILE_SEPARATOR"), label), dotName)
		elif channelText:
			self.channelButton.SetValue(channelText)
		else:
			self.channelButton.SetValue("-")

		if self.picker and self.picker.IsShow():
			self.__RefreshPicker()

	# Cynex: barbaros kayitli hesap dosyasi "|id|sifre|pin|"
	def __GetSavedAccount(self, slot):
		try:
			fileName = AccountFileName(slot)
			if not os.path.exists(fileName):
				return None
			value = old_open(fileName, "r").read()
		except Exception:
			return None
		parts = value.split("|")
		if len(parts) < 4 or not parts[1]:
			return None
		return (parts[1], parts[2], parts[3])

	def __RefreshAccounts(self):
		if not self.accountPanel:
			return
		accounts = []
		for slot in xrange(1, ACCOUNT_SLOT_COUNT + 1):
			account = self.__GetSavedAccount(slot)
			accounts.append((slot, account[0] if account else ""))
		self.accountPanel.SetAccounts(accounts, self.selectedAccount)

	def __GetEditLine(self, index):
		return self.GetChild2(FIELD_NAMES[index][0])

	def __GetFieldValues(self):
		values = []
		for index in xrange(len(FIELD_NAMES)):
			editLine = self.__GetEditLine(index)
			values.append(editLine.GetText() if editLine else "")
		return values

	def OnSelectAccount(self, slot):
		account = self.__GetSavedAccount(slot)
		if not account:
			self.__RefreshAccounts()
			return
		for index in xrange(len(FIELD_NAMES)):
			editLine = self.__GetEditLine(index)
			if editLine:
				editLine.SetText(account[index])
		self.selectedAccount = slot
		self.__RefreshAccounts()
		if self.__EnsureServerReady():
			self.__RunOriginalButton("LoginButton")

	def OnAddAccount(self):
		for slot in xrange(1, ACCOUNT_SLOT_COUNT + 1):
			if not self.__GetSavedAccount(slot):
				self.__SaveAccountToSlot(slot, True)
				return

	def OnDeleteAccount(self, slot):
		try:
			fileName = AccountFileName(slot)
			if os.path.exists(fileName):
				os.remove(fileName)
		except Exception, error:
			dbg.TraceError("MobileLoginWindow.OnDeleteAccount: %s" % error)
		if self.selectedAccount == slot:
			self.selectedAccount = 0
		self.__RefreshAccounts()

	def __SaveAccountToSlot(self, slot, notify):
		(accountId, password, pin) = self.__GetFieldValues()
		if not accountId or not password or not pin:
			if notify:
				self.PopupRiot(Locale("MOBILE_NO_SAVED_ACCOUNT"))
			return False
		try:
			fileName = AccountFileName(slot)
			folder = os.path.dirname(fileName)
			if folder and not os.path.isdir(folder):
				os.makedirs(folder)
			old_open(fileName, "w").write("|%s|%s|%s|" % (accountId, password, pin))
		except Exception, error:
			dbg.TraceError("MobileLoginWindow.SaveAccount: %s" % error)
			return False
		self.selectedAccount = slot
		self.__RefreshAccounts()
		if notify:
			self.PopupRiot(Locale("MOBILE_ACCOUNT_SAVED"))
		return True

	def __RememberAccount(self):
		(accountId, password, pin) = self.__GetFieldValues()
		if not accountId or not password or not pin:
			return
		emptySlot = 0
		for slot in xrange(1, ACCOUNT_SLOT_COUNT + 1):
			account = self.__GetSavedAccount(slot)
			if account and account[0] == accountId:
				if account[1] != password or account[2] != pin:
					self.__SaveAccountToSlot(slot, False)
				return
			if not account and not emptySlot:
				emptySlot = slot
		if emptySlot:
			self.__SaveAccountToSlot(emptySlot, False)

	def __OnRememberChanged(self, value):
		uiMobileHud.LoadConfig()[CONFIG_REMEMBER_ACCOUNT] = "1" if value else "0"
		uiMobileHud.SaveConfig()

	def __OnClickLogin(self):
		if not self.__EnsureServerReady():
			return
		# Cynex: barbaros bos pin'de olmayan SetPinEditLineFocus'u cagiriyor - once burada sor
		(accountId, password, pin) = self.__GetFieldValues()
		if accountId and password and not pin:
			self.PopupRiot(localeInfo.LOGIN_INPUT_PASSWORD)
			return
		if self.rememberToggle and self.rememberToggle.GetValue():
			self.__RememberAccount()
		self.__RunOriginalButton("LoginButton")

	def __OnClickExit(self):
		self.__RunOriginalButton("LoginExitButton")

	def __SyncVisibility(self):
		loginBoard = self.GetChild2("LoginBoard")
		serverOpen = self.__IsServerBoardOpen()
		awaiting = self.autoConfirmPending and serverOpen
		loginVisible = bool(loginBoard and loginBoard.IsShow()) or awaiting
		pickerVisible = self.pickerRequested or (serverOpen and not awaiting)

		SetVisible(self.accountPanel, loginVisible and not self.cardShifted and not pickerVisible)
		SetVisible(self.loginCard, loginVisible and not pickerVisible)
		if self.picker:
			if pickerVisible and not self.picker.IsShow():
				self.__RefreshPicker()
				self.picker.Show()
				self.picker.SetTop()
			elif not pickerVisible and self.picker.IsShow():
				self.picker.Hide()

	def __IsTyping(self):
		for index in xrange(len(FIELD_NAMES)):
			editLine = self.__GetEditLine(index)
			if editLine and editLine.IsFocus():
				return True
		return False

	def __UpdateCardShift(self):
		if not self.loginCard:
			return
		shift = uiMobileCompat.IsMobile() and self.__IsTyping()
		if shift == self.cardShifted:
			return
		self.cardShifted = shift
		(cardX, cardY) = self.cardPosition
		self.loginCard.SetPosition(cardX, TOP_MARGIN if shift else cardY)

	def OnUpdate(self):
		introLogin.LoginWindow.OnUpdate(self)
		if not self.mobileLayoutReady:
			return
		self.__AutoConfirmServer()
		self.__UpdateCardShift()
		self.__SyncVisibility()
		now = app.GetTime()
		if now >= self.nextRefreshTime:
			self.nextRefreshTime = now + REFRESH_INTERVAL
			self.__RefreshChannels()
			self.__RefreshAccounts()
