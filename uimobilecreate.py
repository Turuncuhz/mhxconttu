from __future__ import division
import chr
import dbg
import event
import net
import wndMgr
import localeInfo
import uiScriptLocale
import ui
import introCreate
import uiMobileCompat
import uiMobileStyle

from _weakref import proxy

SCREEN_MARGIN = 32
TOP_Y = 84
TILE_WIDTH = 145
TILE_HEIGHT = 100
TILE_GAP = 10
COLUMN_WIDTH = 300
OPTION_LABEL_HEIGHT = 20
OPTION_HEIGHT = 50
OPTION_GAP = 14
PANEL_PADDING = 20
PANEL_TOP = 30
DESCRIPTION_HEIGHT = 96
TAG_HEIGHT = 24
STAT_ROW_HEIGHT = 20
NAME_FIELD_HEIGHT = 58
CREATE_KEY = "primary_300x64"
CREATE_HEIGHT = 64
PAGE_BUTTON_WIDTH = 30
PAGE_BUTTON_HEIGHT = 24
ROTATION_SPEED = 0.6

RACE_PATHS = (
	(localeInfo.JOB_WARRIOR1, localeInfo.JOB_WARRIOR2),
	(localeInfo.JOB_ASSASSIN1, localeInfo.JOB_ASSASSIN2),
	(localeInfo.JOB_SURA1, localeInfo.JOB_SURA2),
	(localeInfo.JOB_SHAMAN1, localeInfo.JOB_SHAMAN2),
)
EMPIRE_NAMES = {
	net.EMPIRE_A : localeInfo.EMPIRE_A,
	net.EMPIRE_B : getattr(localeInfo, "EMPIRE_B", ""),
	net.EMPIRE_C : localeInfo.EMPIRE_C,
}
STAT_LABELS = ("MOBILE_STAT_HP", "MOBILE_STAT_INT", "MOBILE_STAT_STR", "MOBILE_STAT_DEX")
HIDDEN_NAMES = ("character_board", "left_button", "right_button", "name_warrior", "name_assassin", "name_sura", "name_shaman", "name_wolfman", "right_line", "bottom_line", "left_line", "top_line")


def Locale(name):
	return getattr(uiScriptLocale, name, name)


class RaceTile(uiMobileStyle.Pressable):
	def __init__(self, owner, slotIndex):
		uiMobileStyle.Pressable.__init__(self, TILE_WIDTH, TILE_HEIGHT)
		self.owner = proxy(owner)
		self.slotIndex = slotIndex
		self.raceKey = uiMobileStyle.RACE_KEYS[slotIndex]
		self.selected = None
		self.panel = uiMobileStyle.CreatePanel(self, "card", 0, 0, TILE_WIDTH, TILE_HEIGHT, False)
		emblemName = "class_%s" % self.raceKey
		if uiMobileStyle.HasAsset(emblemName):
			self.icon = uiMobileStyle.CreateCenteredImage(self, emblemName, TILE_WIDTH // 2, 36)
		else:
			self.icon = uiMobileStyle.CreateCenteredImage(self, "icon_race_%s_34" % self.raceKey, TILE_WIDTH // 2, 38)
		self.name = uiMobileStyle.CreateCenteredImage(self, "race_%s" % self.raceKey, TILE_WIDTH // 2, 74)
		self.SetEvent(ui.__mem_func__(self.__Notify))

	def Destroy(self):
		uiMobileStyle.Pressable.Destroy(self)
		self.owner = None
		self.panel = None
		self.icon = None
		self.name = None

	def __Notify(self):
		if self.owner:
			self.owner.OnSelectRace(self.slotIndex)

	def SetSelected(self, selected):
		if selected == self.selected:
			return
		self.selected = selected
		self.panel.SetStyle("race_%s" % self.raceKey if selected else "card")


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


class MobileCreateCharacterWindow(introCreate.CreateCharacterWindow):
	def __init__(self, stream):
		self.mobileReady = False
		self.tiles = []
		self.widgets = []
		self.texts = []
		self.tags = []
		self.pipRows = []
		self.topBar = None
		self.panel = None
		self.raceTitle = None
		self.genderControl = None
		self.shapeControl = None
		self.nameField = None
		self.createButton = None
		self.rotationArea = None
		self.rotations = {}
		self.shownState = None
		self.shownDescription = None
		self.descriptionWidth = 0
		introCreate.CreateCharacterWindow.__init__(self, stream)

	def Open(self):
		introCreate.CreateCharacterWindow.Open(self)
		try:
			self.__ApplyMobileLayout()
			self.mobileReady = True
		except Exception as error:
			dbg.TraceError("MobileCreateCharacterWindow.Open - layout error: %s" % error)
		self.__SafeRefresh()

	def __SafeRefresh(self):
		if not self.mobileReady:
			return
		try:
			self.__RefreshMobile()
			self.__RefreshDescriptionWidth()
		except Exception as error:
			self.mobileReady = False
			dbg.TraceError("MobileCreateCharacterWindow - refresh error: %s" % error)

	def Close(self):
		for tile in self.tiles:
			tile.Destroy()
		for widget in self.widgets:
			widget.Destroy()
		if self.topBar:
			self.topBar.Destroy()
			self.topBar = None
		if self.rotationArea:
			self.rotationArea.Destroy()
			self.rotationArea = None
		self.tiles = []
		self.widgets = []
		self.texts = []
		self.tags = []
		self.pipRows = []
		self.panel = None
		self.raceTitle = None
		self.genderControl = None
		self.shapeControl = None
		self.nameField = None
		self.createButton = None
		self.mobileReady = False
		introCreate.CreateCharacterWindow.Close(self)

	def __Keep(self, widget):
		self.widgets.append(widget)
		return widget

	def __ApplyMobileLayout(self):
		board = self.dlgBoard
		screenWidth = wndMgr.GetScreenWidth()
		screenHeight = wndMgr.GetScreenHeight()
		columnX = screenWidth - SCREEN_MARGIN - COLUMN_WIDTH
		createY = screenHeight - SCREEN_MARGIN - CREATE_HEIGHT
		nameY = TOP_Y
		panelTop = nameY + NAME_FIELD_HEIGHT + 10

		parked = [self.btnCancel, self.btnCreate, self.btnPrev, self.btnNext, self.btnLeft, self.btnRight] + list(self.genderButtonList) + list(self.shapeButtonList)
		for button in parked:
			if button:
				uiMobileStyle.ParkWindow(button)
		for name in HIDDEN_NAMES:
			child = board.GetChild2(name)
			if child:
				child.Hide()

		self.topBar = uiMobileStyle.TopBar(board, screenWidth, getattr(uiScriptLocale, "CANCEL", ""), "title_create", EMPIRE_NAMES.get(net.GetEmpireID(), ""), ui.__mem_func__(self.CancelCreate))

		for index in range(len(uiMobileStyle.RACE_KEYS)):
			tile = RaceTile(self, index)
			tile.SetParent(board)
			tile.SetPosition(SCREEN_MARGIN + (index % 2) * (TILE_WIDTH + TILE_GAP), TOP_Y + (index // 2) * (TILE_HEIGHT + TILE_GAP))
			tile.Show()
			self.tiles.append(tile)

		optionY = TOP_Y + TILE_HEIGHT * 2 + TILE_GAP + OPTION_GAP
		options = (
			("MOBILE_GENDER", (Locale("MOBILE_MALE"), Locale("MOBILE_FEMALE")), "genderControl", self.__OnSelectGender),
			("MOBILE_SHAPE", ("1", "2"), "shapeControl", self.__OnSelectShape),
		)
		for (labelName, labels, attribute, handler) in options:
			self.texts.append(uiMobileStyle.CreateText(board, Locale(labelName), SCREEN_MARGIN, optionY, uiMobileStyle.LABEL_COLOR, uiMobileStyle.FONT_SMALL, "left", True))
			control = self.__Keep(uiMobileStyle.SegmentedControl(TILE_WIDTH * 2 + TILE_GAP, OPTION_HEIGHT, labels))
			control.SetParent(board)
			control.SetPosition(SCREEN_MARGIN, optionY + OPTION_LABEL_HEIGHT)
			control.SetEvent(ui.__mem_func__(handler))
			control.Show()
			setattr(self, attribute, control)
			optionY += OPTION_LABEL_HEIGHT + OPTION_HEIGHT + OPTION_GAP

		self.nameField = self.__Keep(uiMobileStyle.Field(COLUMN_WIDTH, NAME_FIELD_HEIGHT, Locale("MOBILE_CHARACTER_NAME")))
		self.nameField.SetParent(board)
		self.nameField.SetPosition(columnX, nameY)
		self.nameField.Attach(self.editCharacterName)
		self.nameField.Show()

		self.__BuildPanel(board, columnX, panelTop, createY - 12)

		self.createButton = self.__Keep(uiMobileStyle.PrimaryButton(CREATE_KEY, "label_create"))
		self.createButton.SetParent(board)
		self.createButton.SetPosition(columnX, createY)
		self.createButton.SetEvent(ui.__mem_func__(self.CreateCharacter))
		self.createButton.Show()

		areaX = SCREEN_MARGIN + TILE_WIDTH * 2 + TILE_GAP * 2
		self.rotationArea = RotationArea(self)
		self.rotationArea.SetParent(board)
		self.rotationArea.SetPosition(areaX, TOP_Y)
		self.rotationArea.SetSize(max(1, columnX - areaX - TILE_GAP), createY - TOP_Y)
		self.rotationArea.Show()

		self.texts.append(uiMobileStyle.CreateText(board, Locale("MOBILE_ROTATE_HINT"), screenWidth // 2, screenHeight - SCREEN_MARGIN - 18, uiMobileStyle.LABEL_COLOR, uiMobileStyle.FONT_NORMAL, "center", True))

	def __BuildPanel(self, board, x, panelTop, bottom):
		panel = uiMobileStyle.CreateOrnatePanel(board, x, panelTop, COLUMN_WIDTH, 100, False)
		self.panel = panel
		inner = COLUMN_WIDTH - PANEL_PADDING * 2

		self.raceTitle = uiMobileStyle.CreateImage(panel, "race_warrior_large", PANEL_PADDING - 6, PANEL_TOP - 8)
		y = PANEL_TOP + 38

		self.textBoard.SetParent(panel)
		self.textBoard.SetPosition(PANEL_PADDING - 7, y - 7)
		self.textBoard.SetSize(inner + 14, DESCRIPTION_HEIGHT)
		self.textBoard.Show()
		self.descriptionWidth = inner
		for (index, (label, handler)) in enumerate((("<", self.PrevDescriptionPage), (">", self.NextDescriptionPage))):
			button = self.__Keep(uiMobileStyle.PillButton(PAGE_BUTTON_WIDTH, PAGE_BUTTON_HEIGHT, label, None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_NORMAL))
			button.SetParent(panel)
			button.SetPosition(COLUMN_WIDTH - PANEL_PADDING - (2 - index) * PAGE_BUTTON_WIDTH - (1 - index) * 6, y + DESCRIPTION_HEIGHT - PAGE_BUTTON_HEIGHT)
			button.SetEvent(ui.__mem_func__(handler))
			button.Show()
		y += DESCRIPTION_HEIGHT + 10

		self.tagY = y
		y += TAG_HEIGHT + 14

		for labelName in STAT_LABELS:
			self.pipRows.append(uiMobileStyle.PipRow(panel, Locale(labelName), PANEL_PADDING, y, inner))
			y += STAT_ROW_HEIGHT
		y += PANEL_PADDING - 6

		panel.SetSize(COLUMN_WIDTH, min(y, max(100, bottom - panelTop)))

	def __SetTags(self, texts):
		for tag in self.tags:
			tag.Hide()
			tag.Destroy()
		self.tags = []
		x = PANEL_PADDING
		for text in texts:
			width = uiMobileStyle.TextWidth(text, uiMobileStyle.FONT_SMALL) + 22
			tag = uiMobileStyle.CreatePanel(self.panel, "field", x, self.tagY, width, TAG_HEIGHT, False)
			tag.text = uiMobileStyle.CreateText(tag, text, width // 2, 5, uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_SMALL, "center")
			self.tags.append(tag)
			x += width + 6

	def __InstallNameFocus(self):
		pass

	def __CurrentShape(self):
		try:
			return self.shapeList[self.gender][self.slot]
		except Exception:
			return 0

	def __RefreshMobile(self):
		slot = self.slot
		gender = self.gender
		shape = self.__CurrentShape()
		self.shownState = (slot, gender, shape)

		for tile in self.tiles:
			tile.SetSelected(tile.slotIndex == slot)
		self.genderControl.SetSelected(gender)
		self.shapeControl.SetSelected(shape)

		if not 0 <= slot < len(uiMobileStyle.RACE_KEYS):
			return

		uiMobileStyle.LoadAsset(self.raceTitle, "race_%s_large" % uiMobileStyle.RACE_KEYS[slot])
		self.__SetTags(RACE_PATHS[slot])
		for (row, value) in zip(self.pipRows, self.stat):
			row.SetValue(value)

	def __RefreshDescriptionWidth(self):
		if self.descIndex == self.shownDescription:
			return
		self.shownDescription = self.descIndex
		if hasattr(event, "SetEventSetWidth"):
			event.SetEventSetWidth(self.descIndex, self.descriptionWidth)

	def OnSelectRace(self, slotIndex):
		self._CreateCharacterWindow__SelectSlot(slotIndex)
		self.__SafeRefresh()

	def __OnSelectGender(self, index):
		if index != self.gender:
			self._CreateCharacterWindow__SelectGender(index)
		self.__SafeRefresh()

	def __OnSelectShape(self, index):
		self._CreateCharacterWindow__SelectShape(index)
		self.__SafeRefresh()

	def RotateSelected(self, delta):
		chrId = introCreate.BASE_CHR_ID + introCreate.GetRealIDnSlot(self.gender, self.slot)
		if not chr.HasInstance(chrId):
			return
		rotation = (self.rotations.get(chrId, 0.0) + delta) % 360.0
		self.rotations[chrId] = rotation
		chr.SelectInstance(chrId)
		chr.SetRotation(rotation)

	def OnUpdate(self):
		introCreate.CreateCharacterWindow.OnUpdate(self)
		if not self.mobileReady:
			return
		if (self.slot, self.gender, self.__CurrentShape()) != self.shownState or self.descIndex != self.shownDescription:
			self.__SafeRefresh()
