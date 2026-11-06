from __future__ import division
import app
import chat
import wndMgr
import uiScriptLocale
import ui
import uiChat
import uiMobileCompat
import uiMobileStyle

PANEL_WIDTH = 560
PANEL_HEIGHT = 260
HEADER_HEIGHT = 44
INPUT_ROW_HEIGHT = 54
TAB_HEIGHT = 34
TAB_PADDING = 10
TAB_GAP = 4
TAB_LEFT = 8
COLLAPSE_SIZE = 40
LINE_PADDING_X = 16
LINE_PADDING_Y = 8
FIELD_HEIGHT = 40
FIELD_TEXT_X = 12
SEND_WIDTH = 80
PM_SIZE = 40
INPUT_GAP = 8
INPUT_SIDE = 8
INPUT_TOP = 6
KEYBOARD_TOP = 10
OPEN_DURATION = 0.15
CLOSE_DURATION = 0.11
COLLAPSED_HEIGHT = 40
MOBILE_CHAT_SET = 2
CHAT_MAX = 512
CHAT_USER_MAX = 76

DIVIDER_COLOR = uiMobileStyle.Color(110, 86, 44)
TAB_TEXT_COLOR = uiMobileStyle.Color(156, 136, 102)
PLACEHOLDER_COLOR = uiMobileStyle.Color(120, 106, 84)
SEND_TEXT_COLOR = uiMobileStyle.Color(42, 22, 8)	# Cynex: altin dugme uzerinde koyu yazi

LINE_COLORS = (
	("CHAT_TYPE_TALKING", (239, 231, 214)),
	("CHAT_TYPE_INFO", (240, 215, 122)),
	("CHAT_TYPE_PARTY", (159, 208, 255)),
	("CHAT_TYPE_GUILD", (199, 166, 255)),
	("CHAT_TYPE_SHOUT", (255, 178, 122)),
)

TABS = (
	("MOBILE_CHAT_ALL", None, ""),
	("MOBILE_CHAT_NORMAL", "CHAT_TYPE_TALKING", ""),
	("MOBILE_CHAT_PARTY", "CHAT_TYPE_PARTY", "#"),
	("MOBILE_CHAT_GUILD", "CHAT_TYPE_GUILD", "%"),
	("MOBILE_CHAT_SHOUT", "CHAT_TYPE_SHOUT", "!"),
)
COMMAND_MARKS = "#%!/"


def ApplyLineColors():
	for (typeName, (red, green, blue)) in LINE_COLORS:
		chatType = getattr(chat, typeName, None)
		if chatType is not None:
			chat.SetChatColor(chatType, red, green, blue)


def GetAllModes():
	return list(uiChat.ChatLogWindow.CHAT_MODE_INDEX)


class ChatInput(uiChat.ChatLine):
	def __init__(self):
		uiChat.ChatLine.__init__(self)
		self.prefix = ""
		self.overLay.SetText("")
		self.overLay.Hide()

	def SetPrefix(self, prefix):
		self.prefix = prefix

	def OnIMEReturn(self):
		text = self.GetText()
		if self.prefix and text.strip() and text[0] not in COMMAND_MARKS:
			self.SetText(self.prefix + text)
		return uiChat.ChatLine.OnIMEReturn(self)


class ChatTab(uiMobileStyle.Pressable):
	def __init__(self, text):
		width = uiMobileStyle.TextWidth(text, uiMobileStyle.FONT_NORMAL) + TAB_PADDING * 2
		uiMobileStyle.Pressable.__init__(self, width, TAB_HEIGHT)
		self.highlight = uiMobileStyle.NineSlicePanel("chat_tab")
		self.highlight.SetParent(self)
		self.highlight.AddFlag("not_pick")
		self.highlight.SetSize(width, TAB_HEIGHT)
		self.highlight.Hide()
		self.label = uiMobileStyle.CreateText(self, text, width // 2, TAB_HEIGHT // 2 - 8, TAB_TEXT_COLOR, uiMobileStyle.FONT_NORMAL, "center")
		self.selected = False

	def Destroy(self):
		uiMobileStyle.Pressable.Destroy(self)
		self.highlight = None
		self.label = None

	def SetSelected(self, selected):
		self.selected = selected
		self.RefreshVisual()

	def RefreshVisual(self):
		if not getattr(self, "label", None):
			return
		if self.selected:
			self.highlight.Show()
			self.label.SetPackedFontColor(uiMobileStyle.GOLD_COLOR)
		else:
			self.highlight.Hide()
			self.label.SetPackedFontColor(uiMobileStyle.SOFT_COLOR if self.pressed or self.hovered else TAB_TEXT_COLOR)


class IconButton(uiMobileStyle.Pressable):
	def __init__(self, size, iconName):
		uiMobileStyle.Pressable.__init__(self, size, size)
		self.icon = uiMobileStyle.CreateCenteredImage(self, iconName, size // 2, size // 2)

	def Destroy(self):
		uiMobileStyle.Pressable.Destroy(self)
		self.icon = None


class SendButton(uiMobileStyle.Pressable):
	def __init__(self, text):
		uiMobileStyle.Pressable.__init__(self, SEND_WIDTH, FIELD_HEIGHT)
		self.background = uiMobileStyle.CreateImage(self, "chat_send_normal")
		self.label = uiMobileStyle.CreateText(self, text, SEND_WIDTH // 2, FIELD_HEIGHT // 2 - 8, SEND_TEXT_COLOR, uiMobileStyle.FONT_NORMAL, "center")

	def Destroy(self):
		uiMobileStyle.Pressable.Destroy(self)
		self.background = None
		self.label = None

	def RefreshVisual(self):
		if getattr(self, "background", None):
			uiMobileStyle.LoadAsset(self.background, "chat_send_%s" % self.GetVisualState())


class PmButton(uiMobileStyle.Pressable):
	def __init__(self, size):
		uiMobileStyle.Pressable.__init__(self, size, size)
		self.size = size
		self.bg = uiMobileStyle.CreateBar(self, uiMobileStyle.Color(24, 20, 16, 230), 1, 1, size - 2, size - 2)
		self.topBorder = uiMobileStyle.CreateBar(self, uiMobileStyle.GOLD_COLOR, 0, 0, size, 1)
		self.botBorder = uiMobileStyle.CreateBar(self, uiMobileStyle.GOLD_COLOR, 0, size - 1, size, 1)
		self.lBorder = uiMobileStyle.CreateBar(self, uiMobileStyle.GOLD_COLOR, 0, 0, 1, size)
		self.rBorder = uiMobileStyle.CreateBar(self, uiMobileStyle.GOLD_COLOR, size - 1, 0, 1, size)
		self.label = uiMobileStyle.CreateText(self, "PM", size // 2, size // 2 - 8, uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_MEDIUM, "center")

	def Destroy(self):
		uiMobileStyle.Pressable.Destroy(self)
		self.bg = None
		self.topBorder = None
		self.botBorder = None
		self.lBorder = None
		self.rBorder = None
		self.label = None

	def RefreshVisual(self):
		if not getattr(self, "label", None):
			return
		color = uiMobileStyle.BRIGHT_COLOR if self.pressed else uiMobileStyle.GOLD_COLOR
		self.label.SetPackedFontColor(color)
		if self.topBorder:
			self.topBorder.SetColor(color)
			self.botBorder.SetColor(color)
			self.lBorder.SetColor(color)
			self.rBorder.SetColor(color)


class ChatLines(ui.Window):
	def __init__(self, chatID):
		ui.Window.__init__(self)
		self.chatID = chatID
		self.dragging = False
		self.dragStartY = 0
		self.dragStartPosition = 1.0
		self.position = 1.0

	def __del__(self):
		ui.Window.__del__(self)

	def ResetScroll(self):
		self.position = 1.0
		chat.SetEndPos(self.chatID, self.position)

	def OnMouseLeftButtonDown(self):
		self.dragging = True
		self.dragStartY = wndMgr.GetMousePosition()[1]
		self.dragStartPosition = self.position
		return True

	def OnMouseLeftButtonUp(self):
		self.dragging = False
		return True

	def OnUpdate(self):
		if not self.dragging:
			return
		hidden = chat.GetLineCount(self.chatID) - chat.GetVisibleLineCount(self.chatID)
		if hidden <= 0:
			return
		step = max(1, chat.GetLineStep(self.chatID))
		movedLines = (wndMgr.GetMousePosition()[1] - self.dragStartY) / float(step)
		position = max(0.0, min(1.0, self.dragStartPosition - movedLines / hidden))
		if position != self.position:
			self.position = position
			chat.SetEndPos(self.chatID, position)

	def OnRender(self):
		(x, y) = self.GetGlobalPosition()
		height = self.GetHeight()
		chat.ArrangeShowingChat(self.chatID)
		chat.SetPosition(self.chatID, x, y + height)
		chat.SetHeight(self.chatID, height)
		chat.Update(self.chatID)
		chat.Render(self.chatID)


class ChatPanel(ui.Window):
	def __init__(self, interface):
		ui.Window.__init__(self, "UI")
		self.interface = interface
		self.SetSize(PANEL_WIDTH, PANEL_HEIGHT)
		ui.EnableSingleTap(self)
		ApplyLineColors()

		self.collapseEvent = None
		self.selectedTab = -1
		self.homePosition = (0, 0)
		self.keyboardShift = False

		self.chatID = chat.CreateChatSet(MOBILE_CHAT_SET)
		chat.SetBoardState(self.chatID, chat.BOARD_STATE_LOG)

		self.frame = uiMobileStyle.NineSlicePanel("chat_panel")
		self.frame.SetParent(self)
		self.frame.AddFlag("not_pick")
		self.frame.SetSize(PANEL_WIDTH, PANEL_HEIGHT)
		self.frame.Show()

		self.divider = uiMobileStyle.CreateBar(self, DIVIDER_COLOR, 1, HEADER_HEIGHT - 1, PANEL_WIDTH - 2, 1)

		self.tabs = []
		x = TAB_LEFT
		for (index, (labelName, modeName, prefix)) in enumerate(TABS):
			tab = ChatTab(getattr(uiScriptLocale, labelName, labelName))
			tab.SetParent(self)
			tab.SetPosition(x, (HEADER_HEIGHT - TAB_HEIGHT) // 2)
			tab.SetEvent(ui.__mem_func__(self.SelectTab), index)
			tab.Show()
			x += tab.GetWidth() + TAB_GAP
			self.tabs.append(tab)

		self.collapseButton = IconButton(COLLAPSE_SIZE, "icon_chevron_down")
		self.collapseButton.SetParent(self)
		self.collapseButton.SetPosition(PANEL_WIDTH - COLLAPSE_SIZE - 4, (HEADER_HEIGHT - COLLAPSE_SIZE) // 2)
		self.collapseButton.SetEvent(ui.__mem_func__(self.__OnCollapse))
		self.collapseButton.Show()

		linesTop = HEADER_HEIGHT + LINE_PADDING_Y
		linesBottom = PANEL_HEIGHT - INPUT_ROW_HEIGHT - 2
		self.lines = ChatLines(self.chatID)
		self.lines.SetParent(self)
		self.lines.SetPosition(LINE_PADDING_X, linesTop)
		self.lines.SetSize(PANEL_WIDTH - LINE_PADDING_X * 2, linesBottom - linesTop)
		self.lines.Show()

		inputY = PANEL_HEIGHT - INPUT_ROW_HEIGHT + INPUT_TOP
		fieldWidth = PANEL_WIDTH - INPUT_SIDE * 2 - INPUT_GAP * 2 - PM_SIZE - SEND_WIDTH
		self.field = uiMobileStyle.Pressable(fieldWidth, FIELD_HEIGHT)
		self.field.SetParent(self)
		self.field.SetPosition(INPUT_SIDE, inputY)
		self.field.SetEvent(ui.__mem_func__(self.FocusInput))
		self.field.Show()
		self.fieldPanel = uiMobileStyle.CreatePanel(self.field, "field", 0, 0, fieldWidth, FIELD_HEIGHT, False)

		self.input = ChatInput()
		self.input.SetParent(self.field)
		self.input.SetMax(CHAT_MAX)
		self.input.SetUserMax(CHAT_USER_MAX)
		self.input.SetPosition(FIELD_TEXT_X, FIELD_HEIGHT // 2 - 7)
		self.input.SetSize(fieldWidth - FIELD_TEXT_X * 2, 16)
		self.input.SetPackedFontColor(uiMobileStyle.BRIGHT_COLOR)
		self.input.SetPlaceHolderColor(PLACEHOLDER_COLOR)
		self.input.SetPlaceHolder(getattr(uiScriptLocale, "MOBILE_CHAT_PLACEHOLDER", ""))
		self.input.SetReturnEvent(ui.__mem_func__(self.__OnEmptyReturn))
		self.input.SetEscapeEvent(ui.__mem_func__(self.__OnCollapse))
		if interface:
			self.input.BindInterface(interface)
		self.input.Show()

		pmX = INPUT_SIDE + fieldWidth + INPUT_GAP
		self.pmButton = PmButton(PM_SIZE)
		self.pmButton.SetParent(self)
		self.pmButton.SetPosition(pmX, inputY)
		self.pmButton.SetEvent(ui.__mem_func__(self.__OnClickPM))
		self.pmButton.Show()

		self.sendButton = SendButton(getattr(uiScriptLocale, "MOBILE_CHAT_SEND", ""))
		self.sendButton.SetParent(self)
		self.sendButton.SetPosition(pmX + PM_SIZE + INPUT_GAP, inputY)
		self.sendButton.SetEvent(ui.__mem_func__(self.Send))
		self.sendButton.Show()

		self.contents = [self.divider] + self.tabs + [self.collapseButton, self.lines, self.field, self.pmButton, self.sendButton]
		self.collapsedBox = (0, PANEL_HEIGHT - COLLAPSED_HEIGHT, PANEL_WIDTH, COLLAPSED_HEIGHT)
		self.animation = None
		self.closedEvent = None
		self.pendingFocus = False

		self.SelectTab(0)

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.collapseEvent = None
		self.closedEvent = None
		self.animation = None
		self.contents = []
		self.KillInputFocus()
		for tab in self.tabs:
			tab.Destroy()
		self.tabs = []
		if getattr(self, "pmButton", None):
			self.pmButton.Destroy()
			self.pmButton = None
		self.collapseButton.Destroy()
		self.sendButton.Destroy()
		self.field.Destroy()
		self.collapseButton = None
		self.sendButton = None
		self.field = None
		self.fieldPanel = None
		self.input = None
		self.lines = None
		self.frame = None
		self.divider = None
		self.Hide()

	def SetCollapseEvent(self, event):
		self.collapseEvent = event

	def SetHomePosition(self, x, y):
		self.homePosition = (x, y)
		self.keyboardShift = False
		self.SetPosition(x, y)

	def SetCollapsedBox(self, x, y, width, height):
		self.collapsedBox = (x, y, min(width, PANEL_WIDTH), min(height, PANEL_HEIGHT))

	def Open(self):
		self.closedEvent = None
		progress = self.__GetProgress() if self.IsShow() else 0.0
		self.__SetContentVisible(False)
		self.animation = (app.GetTime() - progress * OPEN_DURATION, OPEN_DURATION, True)
		self.__ApplyFrame(progress)
		self.Show()
		self.SetTop()

	def Close(self, event):
		self.KillInputFocus()
		self.pendingFocus = False
		if not self.IsShow():
			self.animation = None
			if event:
				event()
			return
		progress = self.__GetProgress()
		self.__SetContentVisible(False)
		self.closedEvent = event
		self.animation = (app.GetTime() - (1.0 - progress) * CLOSE_DURATION, CLOSE_DURATION, False)

	def CloseNow(self):
		self.KillInputFocus()
		self.pendingFocus = False
		self.animation = None
		self.closedEvent = None
		self.Hide()
		self.__ApplyFrame(1.0)

	def __GetProgress(self):
		if not self.animation:
			return 1.0
		(start, duration, opening) = self.animation
		elapsed = max(0.0, min(1.0, (app.GetTime() - start) / duration))
		return elapsed if opening else 1.0 - elapsed

	def __SetContentVisible(self, visible):
		for widget in self.contents:
			if visible:
				widget.Show()
			else:
				widget.Hide()

	def __ApplyFrame(self, progress):
		eased = 1.0 - (1.0 - progress) ** 3
		(boxX, boxY, boxWidth, boxHeight) = self.collapsedBox
		width = int(round(boxWidth + (PANEL_WIDTH - boxWidth) * eased))
		height = int(round(boxHeight + (PANEL_HEIGHT - boxHeight) * eased))
		self.frame.SetPosition(int(round(boxX * (1.0 - eased))), int(round(boxY * (1.0 - eased))))
		self.frame.SetSize(width, height)

	def __UpdateAnimation(self):
		if not self.animation:
			return
		(start, duration, opening) = self.animation
		elapsed = max(0.0, min(1.0, (app.GetTime() - start) / duration))
		self.__ApplyFrame(elapsed if opening else 1.0 - elapsed)
		if elapsed < 1.0:
			return
		self.animation = None
		if opening:
			self.__SetContentVisible(True)
			if self.pendingFocus:
				self.pendingFocus = False
				self.FocusInput()
			return
		self.Hide()
		self.__ApplyFrame(1.0)
		event = self.closedEvent
		self.closedEvent = None
		if event:
			event()

	def SelectTab(self, index):
		if index == self.selectedTab:
			return
		self.selectedTab = index
		(labelName, modeName, prefix) = TABS[index]
		selectedMode = getattr(chat, modeName, None) if modeName else None
		for mode in GetAllModes():
			if selectedMode is None or mode == selectedMode:
				chat.EnableChatMode(self.chatID, mode)
			else:
				chat.DisableChatMode(self.chatID, mode)
		for (position, tab) in enumerate(self.tabs):
			tab.SetSelected(position == index)
		self.input.SetPrefix(prefix)
		self.lines.ResetScroll()

	def FocusInput(self):
		if self.animation and self.animation[2]:
			self.pendingFocus = True
			return
		if self.input:
			self.input.SetFocus()
			import ime
			ime.EnableCaptureInput()
			if hasattr(app, "ShowKeyboard"):
				app.ShowKeyboard(1)

	def KillInputFocus(self):
		if self.input and self.input.IsFocus():
			self.input.KillFocus()

	def IsTyping(self):
		return bool(self.input and self.input.IsFocus())

	def Send(self):
		if not self.input:
			return
		if self.input.GetText().strip():
			self.input.OnIMEReturn()
			self.lines.ResetScroll()
		else:
			self.FocusInput()

	def __OnClickPM(self):
		self.KillInputFocus()
		if not self.interface:
			return
		import player
		import chr
		vid = player.GetTargetVID()
		if vid and chr.IsPC(vid):
			name = player.GetNameByVID(vid)
			if name and name != player.GetMainCharacterName():
				self.interface.OpenWhisperDialog(name)
				return
		if hasattr(self.interface, "OpenWhisperDialogWithoutTarget"):
			self.interface.OpenWhisperDialogWithoutTarget()
		elif hasattr(self.interface, "OpenWhisperDialog"):
			self.interface.OpenWhisperDialog("")

	def __OnEmptyReturn(self):
		self.KillInputFocus()

	def __OnCollapse(self):
		self.KillInputFocus()
		if self.collapseEvent:
			self.collapseEvent()

	def OnPressEscapeKey(self):
		self.__OnCollapse()
		return True

	def OnUpdate(self):
		self.__UpdateAnimation()
		if not self.input:
			return
		self.fieldPanel.SetStyle("field_focus" if self.input.IsFocus() else "field")
		shift = uiMobileCompat.IsMobile() and self.input.IsFocus()
		if shift != self.keyboardShift:
			self.keyboardShift = shift
			(x, y) = self.homePosition
			self.SetPosition(x, KEYBOARD_TOP if shift else y)

LIVE_CHAT_SET = 3

class LiveChatStream(ui.Window):
	def __init__(self, chatController = None):
		ui.Window.__init__(self, "UI")
		self.chatController = chatController
		self.SetSize(460, 85)
		self.AddFlag("not_pick")
		try:
			self.chatID = chat.CreateChatSet(LIVE_CHAT_SET)
			chat.SetBoardState(self.chatID, chat.BOARD_STATE_VIEW)
			chat.SetStep(self.chatID, 16)
			chat.SetEndPos(self.chatID, 1.0)
			chat.SetHeight(self.chatID, 85)
			for mode in GetAllModes():
				chat.EnableChatMode(self.chatID, mode)
		except Exception:
			self.chatID = None
		import uiMobileHud
		self.enabled = uiMobileHud.IsLiveChatEnabled()
		if self.enabled:
			self.Show()
		else:
			self.Hide()

	def Destroy(self):
		self.Hide()
		self.chatID = None
		self.chatController = None

	def SetEnabled(self, enabled):
		self.enabled = enabled
		if enabled:
			self.Show()
		else:
			self.Hide()

	def OnUpdate(self):
		if not self.enabled or self.chatID is None:
			return
		try:
			(x, y) = self.GetGlobalPosition()
			height = self.GetHeight()
			chat.SetPosition(self.chatID, x, y + height)
			chat.SetHeight(self.chatID, height)
			chat.Update(self.chatID)
		except Exception:
			pass

	def OnRender(self):
		if not self.enabled or self.chatID is None:
			return
		if self.chatController and getattr(self.chatController, "expanded", False):
			return
		try:
			chat.Render(self.chatID)
		except Exception:
			pass
