from __future__ import division
import app
import chr
import dbg
import net
import wndMgr
import localeInfo
import uiScriptLocale
import ui
import introSelect
import uiMobileCompat
import uiMobileStyle

from _weakref import proxy

SCREEN_MARGIN = 32
TOP_Y = 84
CARD_WIDTH = 300
CARD_MAX_HEIGHT = 76
CARD_MIN_HEIGHT = 56
CARD_GAP = 10
EMBLEM_SIZE = 52
FLAG_WIDTH = 30
PANEL_WIDTH = 300
PANEL_PADDING = 20
PANEL_TOP = 30
ROW_HEIGHT = 22
START_KEY = "primary_300x64"
START_HEIGHT = 64
DOUBLE_TAP_TIME = 0.35
ROTATION_SPEED = 0.6
STAT_REFERENCE = 90.0

JOB_NAMES = (localeInfo.JOB_WARRIOR, localeInfo.JOB_ASSASSIN, localeInfo.JOB_SURA, localeInfo.JOB_SHAMAN, getattr(localeInfo, "JOB_WOLFMAN", ""))
EMPIRE_NAMES = {
	net.EMPIRE_A : localeInfo.EMPIRE_A,
	net.EMPIRE_B : getattr(localeInfo, "EMPIRE_B", ""),
	net.EMPIRE_C : localeInfo.EMPIRE_C,
}
STAT_LABELS = ("MOBILE_STAT_HP", "MOBILE_STAT_INT", "MOBILE_STAT_STR", "MOBILE_STAT_DEX")
STAT_SLOTS = ("ACCOUNT_CHARACTER_SLOT_HTH", "ACCOUNT_CHARACTER_SLOT_INT", "ACCOUNT_CHARACTER_SLOT_STR", "ACCOUNT_CHARACTER_SLOT_DEX")
HIDDEN_NAMES = ("character_board", "left_button", "right_button", "name_warrior", "name_assassin", "name_sura", "name_shaman", "name_wolfman")


def Locale(name):
	if hasattr(uiScriptLocale, name):
		return getattr(uiScriptLocale, name)
	try:
		import uimobilelocale
		return uimobilelocale.STRINGS.get(name, name)
	except Exception:
		return name


def FormatPlayTime(minutes):
	hours = minutes // 60
	if hours > 0:
		fmt = Locale("MOBILE_HOURS")
		if "%" in fmt:
			try:
				return fmt % hours
			except Exception:
				pass
		return "%d saat" % hours
	return "%d %s" % (minutes, localeInfo.MINUTE)


def GetSlotInteger(slot, name):
	return net.GetAccountCharacterSlotDataInteger(slot, getattr(net, name))


def PortraitName(race):
	try:
		import uiCharacter
		path = uiCharacter.FACE_IMAGE_DICT.get(race)
	except Exception:
		path = None
	if not path:
		return None
	return "portrait_%s" % path.replace("\\", "/").split("/")[-1].split(".")[0].lower()


def DescribeCharacter(slot):
	race = GetSlotInteger(slot, "ACCOUNT_CHARACTER_SLOT_RACE")
	level = GetSlotInteger(slot, "ACCOUNT_CHARACTER_SLOT_LEVEL")
	job = chr.RaceToJob(race)
	jobName = JOB_NAMES[job] if 0 <= job < len(JOB_NAMES) else ""
	fmt = Locale("MOBILE_CHARACTER_DETAIL")
	if "%" in fmt:
		try:
			return (job, fmt % (level, jobName))
		except Exception:
			pass
	return (job, "Lv. %d %s" % (level, jobName))


class CharacterCard(uiMobileStyle.Pressable):
	def __init__(self, owner, slotIndex, height):
		uiMobileStyle.Pressable.__init__(self, CARD_WIDTH, height)
		self.owner = proxy(owner)
		self.slotIndex = slotIndex
		self.job = -1
		self.empireId = None

		self.panel = uiMobileStyle.CreatePanel(self, "card_empty", 0, 0, CARD_WIDTH, height, False)
		emblemY = (height - EMBLEM_SIZE) // 2
		self.emblem = uiMobileStyle.CreateImage(self, "emblem_empty", 12, emblemY)
		self.icon = uiMobileStyle.CreateCenteredImage(self, "icon_plus", 12 + EMBLEM_SIZE // 2, height // 2)
		self.name = uiMobileStyle.CreateText(self, "", 76, height // 2 - 19, uiMobileStyle.CREAM_COLOR, uiMobileStyle.FONT_LARGE)
		self.detail = uiMobileStyle.CreateText(self, "", 76, height // 2 + 3, uiMobileStyle.MUTED_COLOR, uiMobileStyle.FONT_NORMAL)
		self.flag = None

		self.SetEvent(ui.__mem_func__(self.__Notify))

	def Destroy(self):
		uiMobileStyle.Pressable.Destroy(self)
		self.owner = None
		self.panel = None
		self.emblem = None
		self.icon = None
		self.name = None
		self.detail = None
		self.flag = None

	def __Notify(self):
		if self.owner:
			self.owner.OnSelectCard(self.slotIndex)

	def __SetFlag(self, empireId):
		if not self.flag:
			self.flag = uiMobileStyle.CreateFlag(self, empireId, 0, 0, FLAG_WIDTH)
		elif empireId != self.empireId:
			uiMobileStyle.SetFlagImage(self.flag, empireId, FLAG_WIDTH)
		self.empireId = empireId
		flagHeight = uiMobileStyle.FlagHeight(self.flag, FLAG_WIDTH)
		self.flag.SetPosition(CARD_WIDTH - 14 - FLAG_WIDTH, (self.GetHeight() - flagHeight) // 2)
		self.flag.Show()

	def Refresh(self, selected):
		slot = self.slotIndex
		height = self.GetHeight()
		if not GetSlotInteger(slot, "ACCOUNT_CHARACTER_SLOT_ID"):
			self.panel.SetStyle("card_empty")
			uiMobileStyle.LoadAsset(self.emblem, "emblem_empty")
			if self.job != -1:
				self.job = -1
				uiMobileStyle.SetCenteredAsset(self.icon, "icon_plus", 12 + EMBLEM_SIZE // 2, height // 2)
			self.icon.Show()
			self.name.SetText(Locale("MOBILE_NEW_CHARACTER"))
			self.name.SetPackedFontColor(uiMobileStyle.MUTED_COLOR)
			self.name.SetPosition(76, height // 2 - 9)
			self.detail.SetText("")
			if self.flag:
				self.flag.Hide()
			return

		(job, detail) = DescribeCharacter(slot)
		raceKey = uiMobileStyle.RaceKey(job)
		self.panel.SetStyle("card_active" if selected else "card")
		portrait = PortraitName(GetSlotInteger(slot, "ACCOUNT_CHARACTER_SLOT_RACE"))
		if portrait:
			uiMobileStyle.LoadAsset(self.emblem, portrait)
			self.icon.Hide()
		else:
			uiMobileStyle.LoadAsset(self.emblem, "emblem_%s" % raceKey)
			self.icon.Show()
		if job != self.job:
			self.job = job
			uiMobileStyle.SetCenteredAsset(self.icon, "icon_race_%s_28" % raceKey, 12 + EMBLEM_SIZE // 2, height // 2)
		self.name.SetText(net.GetAccountCharacterSlotDataString(slot, net.ACCOUNT_CHARACTER_SLOT_NAME))
		self.name.SetPackedFontColor(uiMobileStyle.CREAM_COLOR)
		self.name.SetPosition(76, height // 2 - 19)
		self.detail.SetText(detail)
		self.__SetFlag(net.GetEmpireID())


class RotationArea(ui.Window):
	def __init__(self, owner):
		ui.Window.__init__(self)
		self.owner = proxy(owner)
		self.dragging = False
		self.lastX = 0

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.owner = None

	def OnMouseLeftButtonDown(self):
		self.dragging = True
		self.lastX = wndMgr.GetMousePosition()[0]
		return True

	def OnMouseLeftButtonUp(self):
		self.dragging = False
		return True

	def OnUpdate(self):
		if not self.dragging or not self.owner:
			return
		x = wndMgr.GetMousePosition()[0]
		delta = x - self.lastX
		self.lastX = x
		if delta:
			self.owner.RotateSelected(delta * ROTATION_SPEED)


class InfoPanel(object):
	def __init__(self, parent, x, y):
		self.panel = uiMobileStyle.CreateOrnatePanel(parent, x, y, PANEL_WIDTH, 100, False)
		panel = self.panel
		inner = PANEL_WIDTH - PANEL_PADDING * 2
		right = PANEL_WIDTH - PANEL_PADDING

		self.name = uiMobileStyle.CreateText(panel, "", PANEL_PADDING, PANEL_TOP, uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_TITLE)
		self.detail = uiMobileStyle.CreateText(panel, "", PANEL_PADDING, PANEL_TOP + 32, uiMobileStyle.SOFT_COLOR, uiMobileStyle.FONT_MEDIUM)

		rowY = PANEL_TOP + 62
		self.decorations = [uiMobileStyle.CreateBar(panel, uiMobileStyle.DIVIDER_COLOR, PANEL_PADDING, rowY, inner, 1)]
		rowY += 10
		self.values = {}
		for (key, labelName) in (("empire", "MOBILE_EMPIRE"), ("guild", "MOBILE_GUILD"), ("playTime", "MOBILE_PLAYTIME")):
			self.decorations.append(uiMobileStyle.CreateText(panel, Locale(labelName), PANEL_PADDING, rowY, uiMobileStyle.MUTED_COLOR, uiMobileStyle.FONT_NORMAL))
			self.values[key] = uiMobileStyle.CreateText(panel, "", right, rowY, uiMobileStyle.CREAM_COLOR, uiMobileStyle.FONT_NORMAL, "right")
			if key == "empire":
				self.empireRowY = rowY
			rowY += ROW_HEIGHT
		rowY += 4
		self.decorations.append(uiMobileStyle.CreateBar(panel, uiMobileStyle.DIVIDER_COLOR, PANEL_PADDING, rowY, inner, 1))
		rowY += 12

		self.stats = []
		for labelName in STAT_LABELS:
			self.stats.append(uiMobileStyle.StatRow(panel, Locale(labelName), PANEL_PADDING, rowY, inner))
			rowY += ROW_HEIGHT
		rowY += 6

		self.deleteButton = uiMobileStyle.TextButton(Locale("MOBILE_DELETE_CHARACTER"), "icon_trash", uiMobileStyle.DANGER_COLOR, uiMobileStyle.FONT_NORMAL, 36)
		self.deleteButton.SetParent(panel)
		self.deleteButton.SetPosition(PANEL_PADDING, rowY)
		self.deleteButton.Show()
		rowY += 36 + 12

		panel.SetSize(PANEL_WIDTH, rowY)
		self.flag = None
		self.flagEmpire = None

	def Destroy(self):
		self.deleteButton.Destroy()
		self.deleteButton = None
		self.decorations = []
		self.panel = None
		self.flag = None

	def Show(self):
		self.panel.Show()

	def Hide(self):
		self.panel.Hide()

	def __SetEmpire(self, empireId):
		name = EMPIRE_NAMES.get(empireId, "")
		self.values["empire"].SetText(name)
		if not self.flag:
			self.flag = uiMobileStyle.CreateFlag(self.panel, empireId, 0, 0, 22)
		elif empireId != self.flagEmpire:
			uiMobileStyle.SetFlagImage(self.flag, empireId, 22)
		self.flagEmpire = empireId
		flagHeight = uiMobileStyle.FlagHeight(self.flag, 22)
		textWidth = uiMobileStyle.TextWidth(name, uiMobileStyle.FONT_NORMAL)
		self.flag.SetPosition(PANEL_WIDTH - PANEL_PADDING - textWidth - 8 - 22, self.empireRowY + 7 - flagHeight // 2)

	def Refresh(self, slot):
		(job, detail) = DescribeCharacter(slot)
		self.name.SetText(net.GetAccountCharacterSlotDataString(slot, net.ACCOUNT_CHARACTER_SLOT_NAME))
		self.detail.SetText(detail)
		self.__SetEmpire(net.GetEmpireID())
		guildName = net.GetAccountCharacterSlotDataString(slot, net.ACCOUNT_CHARACTER_SLOT_GUILD_NAME)
		self.values["guild"].SetText(guildName if guildName else Locale("MOBILE_NO_GUILD"))
		self.values["playTime"].SetText(FormatPlayTime(GetSlotInteger(slot, "ACCOUNT_CHARACTER_SLOT_PLAYTIME")))

		values = [GetSlotInteger(slot, name) for name in STAT_SLOTS]
		reference = max([STAT_REFERENCE] + values)
		for (row, value) in zip(self.stats, values):
			row.SetValue(value, reference)


class MobileSelectCharacterWindow(introSelect.SelectCharacterWindow):
	def __init__(self, stream):
		self.mobileReady = False
		self.cards = []
		self.topBar = None
		self.infoPanel = None
		self.startButton = None
		self.startMode = None
		self.shownSlot = None
		self.mobileTexts = []
		self.rotationArea = None
		self.rotations = {}
		self.lastTapSlot = -1
		self.lastTapTime = 0.0
		introSelect.SelectCharacterWindow.__init__(self, stream)

	def Open(self):
		introSelect.SelectCharacterWindow.Open(self)
		if not self.dlgBoard:
			return
		try:
			self.__ApplyMobileLayout()
			self.mobileReady = True
		except Exception as error:
			dbg.TraceError("MobileSelectCharacterWindow.Open - layout error: %s" % error)
		self.__SafeRefresh()

	def Close(self):
		for card in self.cards:
			card.Destroy()
		self.cards = []
		if self.rotationArea:
			self.rotationArea.Destroy()
			self.rotationArea = None
		if self.topBar:
			self.topBar.Destroy()
			self.topBar = None
		if self.infoPanel:
			self.infoPanel.Destroy()
			self.infoPanel = None
		if self.startButton:
			self.startButton.Destroy()
			self.startButton = None
		self.mobileTexts = []
		self.mobileReady = False
		introSelect.SelectCharacterWindow.Close(self)

	def SelectSlot(self, index):
		introSelect.SelectCharacterWindow.SelectSlot(self, index)
		self.__SafeRefresh()

	def DeleteCharacter(self, index):
		introSelect.SelectCharacterWindow.DeleteCharacter(self, index)
		self.__SafeRefresh()

	def __SafeRefresh(self):
		if not self.mobileReady:
			return
		try:
			self.__RefreshMobile()
		except Exception as error:
			self.mobileReady = False
			dbg.TraceError("MobileSelectCharacterWindow - refresh error: %s" % error)

	def __ApplyMobileLayout(self):
		board = self.dlgBoard
		screenWidth = wndMgr.GetScreenWidth()
		screenHeight = wndMgr.GetScreenHeight()
		panelX = screenWidth - SCREEN_MARGIN - PANEL_WIDTH
		startY = screenHeight - SCREEN_MARGIN - START_HEIGHT

		for button in (self.btnStart, self.btnCreate, self.btnExit, self.btnDelete):
			if button:
				uiMobileStyle.ParkWindow(button)
		for name in HIDDEN_NAMES:
			child = board.GetChild2(name)
			if child:
				child.Hide()

		serverInfo = ""
		try:
			serverInfo = (" %s " % Locale("MOBILE_SEPARATOR")).join([part.strip() for part in net.GetServerInfo().split(",") if part.strip()])
		except Exception:
			pass
		self.topBar = uiMobileStyle.TopBar(board, screenWidth, getattr(uiScriptLocale, "SELECT_EXIT", ""), "title_select", serverInfo, ui.__mem_func__(self.ExitSelect))

		slotCount = self.SLOT_COUNT
		available = screenHeight - TOP_Y - SCREEN_MARGIN - 34
		cardHeight = max(CARD_MIN_HEIGHT, min(CARD_MAX_HEIGHT, (available - (slotCount - 1) * CARD_GAP) // slotCount))
		for index in range(slotCount):
			card = CharacterCard(self, index, cardHeight)
			card.SetParent(board)
			card.SetPosition(SCREEN_MARGIN, TOP_Y + index * (cardHeight + CARD_GAP))
			card.Show()
			self.cards.append(card)

		listBottom = TOP_Y + slotCount * cardHeight + (slotCount - 1) * CARD_GAP
		self.mobileTexts.append(uiMobileStyle.CreateText(board, Locale("MOBILE_DOUBLE_TAP_HINT"), SCREEN_MARGIN + CARD_WIDTH // 2, listBottom + 14, uiMobileStyle.LABEL_COLOR, uiMobileStyle.FONT_NORMAL, "center", True))

		self.infoPanel = InfoPanel(board, panelX, TOP_Y)
		self.infoPanel.deleteButton.SetEvent(ui.__mem_func__(self.__OnClickDelete))

		self.startButton = uiMobileStyle.PrimaryButton(START_KEY, "label_start")
		self.startButton.SetParent(board)
		self.startButton.SetPosition(panelX, startY)
		self.startButton.SetEvent(ui.__mem_func__(self.__OnClickStart))
		self.startButton.Show()

		areaX = SCREEN_MARGIN + CARD_WIDTH + CARD_GAP
		self.rotationArea = RotationArea(self)
		self.rotationArea.SetParent(board)
		self.rotationArea.SetPosition(areaX, TOP_Y)
		self.rotationArea.SetSize(max(1, panelX - areaX - CARD_GAP), startY - TOP_Y)
		self.rotationArea.Show()

		self.mobileTexts.append(uiMobileStyle.CreateText(board, Locale("MOBILE_ROTATE_HINT"), screenWidth // 2, screenHeight - SCREEN_MARGIN - 18, uiMobileStyle.LABEL_COLOR, uiMobileStyle.FONT_NORMAL, "center", True))

	def __IsSlotUsed(self, slot):
		return slot >= 0 and bool(GetSlotInteger(slot, "ACCOUNT_CHARACTER_SLOT_ID"))

	def __RefreshMobile(self):
		self.shownSlot = self.slot
		for card in self.cards:
			card.Refresh(card.slotIndex == self.slot)

		used = self.__IsSlotUsed(self.slot)
		mode = "start" if used else "create"
		if mode != self.startMode:
			self.startMode = mode
			self.startButton.SetLabel("label_start" if used else "label_create")

		if not used:
			self.infoPanel.Hide()
			return
		self.infoPanel.Show()
		self.infoPanel.Refresh(self.slot)

	def __OnClickStart(self):
		if self.__IsSlotUsed(self.slot):
			self.StartGame()
		else:
			self.CreateCharacter()

	def __OnClickDelete(self):
		if self.btnDelete:
			uiMobileStyle.RunButtonEvent(self.btnDelete)

	def OnSelectCard(self, slotIndex):
		now = app.GetTime()
		isDoubleTap = slotIndex == self.lastTapSlot and now - self.lastTapTime <= DOUBLE_TAP_TIME
		self.lastTapSlot = slotIndex
		self.lastTapTime = now

		if slotIndex != self.slot:
			self.SelectSlot(slotIndex)

		if not self.__IsSlotUsed(slotIndex):
			self.CreateCharacter()
		elif isDoubleTap:
			self.StartGame()

	def OnUpdate(self):
		introSelect.SelectCharacterWindow.OnUpdate(self)
		if self.mobileReady and self.slot != self.shownSlot:
			self.__SafeRefresh()

	def RotateSelected(self, delta):
		if self.slot < 0 or not chr.HasInstance(self.slot):
			return
		rotation = (self.rotations.get(self.slot, 0.0) + delta) % 360.0
		self.rotations[self.slot] = rotation
		chr.SelectInstance(self.slot)
		chr.SetRotation(rotation)
