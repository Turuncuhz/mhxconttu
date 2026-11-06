from __future__ import division
import dbg
import net
import wndMgr
import uiScriptLocale
import ui
import introEmpire
import uiMobileCompat
import uiMobileStyle

from _weakref import proxy

TOP_Y = 86
CARD_WIDTH = 360
CARD_MAX_HEIGHT = 370
CARD_MIN_HEIGHT = 300
CARD_GAP = 24
CARD_PADDING = 26
DIM_INSET = 6
FLAG_WIDTH = 128
SELECT_KEY = "primary_300x64"
SELECT_HEIGHT = 64
BOTTOM_SPACE = 49
LINE_HEIGHT = 22

HIDDEN_NAMES = ("Atlas", "left_button", "right_button", "empire_board", "Title", "desc_phase")
EMPIRE_TEXTS = {
	net.EMPIRE_A : ("MOBILE_EMPIRE_A_COLOR", "MOBILE_EMPIRE_A_TEXT", "MOBILE_EMPIRE_A_VILLAGES"),
	net.EMPIRE_B : ("MOBILE_EMPIRE_B_COLOR", "MOBILE_EMPIRE_B_TEXT", "MOBILE_EMPIRE_B_VILLAGES"),
	net.EMPIRE_C : ("MOBILE_EMPIRE_C_COLOR", "MOBILE_EMPIRE_C_TEXT", "MOBILE_EMPIRE_C_VILLAGES"),
}


def Locale(name):
	return getattr(uiScriptLocale, name, name)


class EmpireCard(uiMobileStyle.Pressable):
	def __init__(self, owner, empireId, height):
		uiMobileStyle.Pressable.__init__(self, CARD_WIDTH, height)
		self.owner = proxy(owner)
		self.empireId = empireId
		self.key = uiMobileStyle.EMPIRE_KEYS.get(empireId, "a")
		self.selected = None
		inner = CARD_WIDTH - CARD_PADDING * 2
		(colorName, textName, villagesName) = EMPIRE_TEXTS.get(empireId, EMPIRE_TEXTS[net.EMPIRE_A])

		self.panel = uiMobileStyle.CreateOrnatePanel(self, 0, 0, CARD_WIDTH, height, False)
		self.flag = uiMobileStyle.CreateFlag(self, empireId, (CARD_WIDTH - FLAG_WIDTH) // 2, 28, FLAG_WIDTH)
		y = 28 + uiMobileStyle.FlagHeight(self.flag, FLAG_WIDTH) + 22
		self.name = uiMobileStyle.CreateCenteredImage(self, "empire_%s" % self.key, CARD_WIDTH // 2, y)
		y += 26
		self.colorText = uiMobileStyle.CreateText(self, Locale(colorName), CARD_WIDTH // 2, y, uiMobileStyle.EMPIRE_COLORS.get(empireId, uiMobileStyle.GOLD_COLOR), uiMobileStyle.FONT_SMALL, "center")
		y += 28
		self.lines = uiMobileStyle.CreateWrappedText(self, Locale(textName), CARD_PADDING, y, inner, uiMobileStyle.DESCRIPTION_COLOR, uiMobileStyle.FONT_MEDIUM, LINE_HEIGHT, "center")
		footerY = height - CARD_PADDING - 18
		self.divider = uiMobileStyle.CreateBar(self, uiMobileStyle.DIVIDER_COLOR, CARD_PADDING, footerY - 12, inner, 1)
		self.villages = uiMobileStyle.CreateText(self, Locale(villagesName), CARD_WIDTH // 2, footerY, uiMobileStyle.MUTED_COLOR, uiMobileStyle.FONT_NORMAL, "center")
		self.dim = uiMobileStyle.CreateBar(self, uiMobileStyle.DIM_COLOR, DIM_INSET, DIM_INSET, CARD_WIDTH - DIM_INSET * 2, height - DIM_INSET * 2)

		self.SetEvent(ui.__mem_func__(self.__Notify))

	def Destroy(self):
		uiMobileStyle.Pressable.Destroy(self)
		self.owner = None
		self.panel = None
		self.flag = None
		self.name = None
		self.colorText = None
		self.lines = []
		self.divider = None
		self.villages = None
		self.dim = None

	def __Notify(self):
		if self.owner:
			self.owner.OnSelectEmpire(self.empireId)

	def SetSelected(self, selected):
		if selected == self.selected:
			return
		self.selected = selected
		if selected:
			self.dim.Hide()
		else:
			self.dim.Show()


class MobileEmpireLayout(object):
	def Open(self):
		self.mobileCards = []
		self.mobileTexts = []
		self.mobileTopBar = None
		self.mobileSelectButton = None
		self.mobileReady = False
		self.shownEmpire = None
		super(MobileEmpireLayout, self).Open()
		if not getattr(self, "selectButton", None):
			return
		try:
			self.__ApplyMobileLayout()
			self.mobileReady = True
		except Exception as error:
			dbg.TraceError("MobileEmpireLayout.Open - layout error: %s" % error)

	def Close(self):
		for card in getattr(self, "mobileCards", []):
			card.Destroy()
		if getattr(self, "mobileTopBar", None):
			self.mobileTopBar.Destroy()
		if getattr(self, "mobileSelectButton", None):
			self.mobileSelectButton.Destroy()
		self.mobileCards = []
		self.mobileTexts = []
		self.mobileTopBar = None
		self.mobileSelectButton = None
		self.mobileReady = False
		super(MobileEmpireLayout, self).Close()

	def __ApplyMobileLayout(self):
		screenWidth = wndMgr.GetScreenWidth()
		screenHeight = wndMgr.GetScreenHeight()
		selectY = screenHeight - BOTTOM_SPACE - SELECT_HEIGHT

		for name in HIDDEN_NAMES:
			child = self.GetChild2(name)
			if child:
				child.Hide()
		for button in list(self.empireAreaButton.values()):
			button.Hide()
		for button in (self.selectButton, self.exitButton):
			uiMobileStyle.ParkWindow(button)
		descriptionBox = getattr(self, "descriptionBox", None)
		if descriptionBox:
			descriptionBox.Hide()

		self.mobileTopBar = uiMobileStyle.TopBar(self, screenWidth, getattr(uiScriptLocale, "EMPIRE_EXIT", ""), "title_empire", Locale("MOBILE_SERVER_NAME"), ui.__mem_func__(self.__OnClickExit))

		empireIds = sorted(self.EMPIRE_DESCRIPTION_TEXT_FILE_NAME.keys())
		cardHeight = max(CARD_MIN_HEIGHT, min(CARD_MAX_HEIGHT, selectY - 24 - TOP_Y))
		cardWidth = CARD_WIDTH
		rowWidth = len(empireIds) * cardWidth + (len(empireIds) - 1) * CARD_GAP
		startX = (screenWidth - rowWidth) // 2
		for (index, empireId) in enumerate(empireIds):
			card = EmpireCard(self, empireId, cardHeight)
			card.SetParent(self)
			card.SetPosition(startX + index * (cardWidth + CARD_GAP), TOP_Y)
			card.Show()
			self.mobileCards.append(card)

		self.mobileSelectButton = uiMobileStyle.PrimaryButton(SELECT_KEY, "label_select_empire")
		self.mobileSelectButton.SetParent(self)
		self.mobileSelectButton.SetPosition((screenWidth - self.mobileSelectButton.GetWidth()) // 2, selectY)
		self.mobileSelectButton.SetEvent(ui.__mem_func__(self.__OnClickSelect))
		self.mobileSelectButton.Show()

		self.mobileTexts.append(uiMobileStyle.CreateText(self, Locale("MOBILE_EMPIRE_WARNING"), screenWidth // 2, screenHeight - 31, uiMobileStyle.LABEL_COLOR, uiMobileStyle.FONT_NORMAL, "center", True))

		self.__RefreshCards()

	def __OnClickSelect(self):
		uiMobileStyle.RunButtonEvent(self.selectButton)

	def __OnClickExit(self):
		uiMobileStyle.RunButtonEvent(self.exitButton)

	def __RefreshCards(self):
		self.shownEmpire = self.empireID
		for card in self.mobileCards:
			card.SetSelected(card.empireId == self.empireID)

	def OnUpdate(self):
		super(MobileEmpireLayout, self).OnUpdate()
		if getattr(self, "mobileReady", False) and self.empireID != self.shownEmpire:
			self.__RefreshCards()


class MobileSelectEmpireWindow(MobileEmpireLayout, introEmpire.SelectEmpireWindow):
	pass


class MobileReselectEmpireWindow(MobileEmpireLayout, introEmpire.ReselectEmpireWindow):
	pass
