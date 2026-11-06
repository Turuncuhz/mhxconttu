# -*- coding: cp1254 -*-
from __future__ import division
import ui
import app
import net
import player
import dbg
import uimobilestyle as uiMobileStyle
import uimobilecompat as uiMobileCompat

class StatusPopupDialog(ui.Window):
	def __init__(self, key, title, curVal):
		ui.Window.__init__(self, "TOP_MOST")
		uiMobileCompat.EnableSingleTap(self)
		self.key = key
		self.title = title
		self.curVal = curVal
		self.addPoints = 0

		self.width = 310
		self.height = 210
		self.SetSize(self.width, self.height)

		self.panel = uiMobileStyle.CreateOrnatePanel(self, 0, 0, self.width, self.height)

		self.titleText = uiMobileStyle.CreateText(
			self,
			"%s Da\xf0\xfdt" % title,
			self.width // 2,
			14,
			uiMobileStyle.GOLD_COLOR,
			uiMobileStyle.FONT_LARGE,
			"center"
		)

		self.statInfoText = uiMobileStyle.CreateText(
			self,
			"",
			self.width // 2,
			42,
			uiMobileStyle.BRIGHT_COLOR,
			uiMobileStyle.FONT_MEDIUM,
			"center"
		)

		self.availText = uiMobileStyle.CreateText(
			self,
			"",
			self.width // 2,
			64,
			uiMobileStyle.SOFT_COLOR,
			uiMobileStyle.FONT_SMALL,
			"center"
		)

		yStep = 92
		btnSize = 42

		self.btnMinus10 = uiMobileStyle.PillButton(44, btnSize, "-10", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_SMALL)
		self.btnMinus10.SetParent(self)
		self.btnMinus10.SetPosition(14, yStep)
		self.btnMinus10.SetEvent(ui.__mem_func__(self.__Change), -10)
		self.btnMinus10.Show()

		self.btnMinus1 = uiMobileStyle.PillButton(36, btnSize, "-1", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.btnMinus1.SetParent(self)
		self.btnMinus1.SetPosition(64, yStep)
		self.btnMinus1.SetEvent(ui.__mem_func__(self.__Change), -1)
		self.btnMinus1.Show()

		self.valueText = uiMobileStyle.CreateText(
			self,
			"",
			self.width // 2,
			yStep + 10,
			uiMobileStyle.BRIGHT_COLOR,
			uiMobileStyle.FONT_LARGE,
			"center"
		)

		self.btnPlus1 = uiMobileStyle.PillButton(36, btnSize, "+1", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.btnPlus1.SetParent(self)
		self.btnPlus1.SetPosition(self.width - 100, yStep)
		self.btnPlus1.SetEvent(ui.__mem_func__(self.__Change), 1)
		self.btnPlus1.Show()

		self.btnPlus10 = uiMobileStyle.PillButton(44, btnSize, "+10", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_SMALL)
		self.btnPlus10.SetParent(self)
		self.btnPlus10.SetPosition(self.width - 58, yStep)
		self.btnPlus10.SetEvent(ui.__mem_func__(self.__Change), 10)
		self.btnPlus10.Show()

		yBottom = 152
		btnW = 120
		btnH = 36

		self.btnApply = uiMobileStyle.PillButton(btnW, btnH, "Uygula", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.btnApply.SetParent(self)
		self.btnApply.SetPosition(20, yBottom)
		self.btnApply.SetEvent(ui.__mem_func__(self.__Apply))
		self.btnApply.Show()

		self.btnCancel = uiMobileStyle.PillButton(btnW, btnH, "\xddptal", None, "field", uiMobileStyle.SOFT_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.btnCancel.SetParent(self)
		self.btnCancel.SetPosition(self.width - btnW - 20, yBottom)
		self.btnCancel.SetEvent(ui.__mem_func__(self.Close))
		self.btnCancel.Show()

		self.Refresh()

	def Destroy(self):
		self.key = None
		self.panel = None
		self.titleText = None
		self.statInfoText = None
		self.availText = None
		self.valueText = None
		if self.btnMinus10:
			self.btnMinus10.Destroy()
		if self.btnMinus1:
			self.btnMinus1.Destroy()
		if self.btnPlus1:
			self.btnPlus1.Destroy()
		if self.btnPlus10:
			self.btnPlus10.Destroy()
		if self.btnApply:
			self.btnApply.Destroy()
		if self.btnCancel:
			self.btnCancel.Destroy()
		self.btnMinus10 = None
		self.btnMinus1 = None
		self.btnPlus1 = None
		self.btnPlus10 = None
		self.btnApply = None
		self.btnCancel = None
		self.Hide()

	def Open(self, sw, sh):
		self.SetPosition((sw - self.width) // 2, (sh - self.height) // 2)
		self.SetTop()
		self.Show()

	def Close(self):
		self.Hide()

	def __GetCurVal(self):
		statTypeMap = {
			"HTH": getattr(player, "HT", 13),
			"INT": getattr(player, "IQ", 15),
			"STR": getattr(player, "ST", 12),
			"DEX": getattr(player, "DX", 14),
		}
		statType = statTypeMap.get(self.key, None)
		if statType is not None and hasattr(player, "GetStatus"):
			try:
				return player.GetStatus(statType)
			except Exception:
				pass
		return self.curVal

	def __Change(self, amount):
		avail = player.GetStatus(player.STAT) if hasattr(player, "GetStatus") and hasattr(player, "STAT") else 0
		# addPoints asla 0'in altina inemez (mevcut statu asla dusurulmez)
		newAdd = self.addPoints + amount
		newAdd = max(0, min(avail, newAdd))
		self.addPoints = newAdd
		self.Refresh()

	def Refresh(self):
		avail = player.GetStatus(player.STAT) if hasattr(player, "GetStatus") and hasattr(player, "STAT") else 0
		cur = self.__GetCurVal()
		newVal = cur + self.addPoints
		self.statInfoText.SetText("Mevcut: %d  |  Yeni: %d" % (cur, newVal))
		self.availText.SetText("Kullan\xfdlabilir Puan: %d" % avail)
		self.valueText.SetText("+%d" % self.addPoints)

	def __Apply(self):
		import app
		# Sadece 0'dan buyuk pozitif puanlar gonderilir, asla stat azaltilamaz
		if self.addPoints > 0:
			cmdMap = {
				"HTH": "ht",
				"INT": "iq",
				"STR": "st",
				"DEX": "dx"
			}
			cmdKey = cmdMap.get(self.key, self.key.lower())
			points = self.addPoints
			if hasattr(app, "ENABLE_STATUS_UP_RENEWAL") and app.ENABLE_STATUS_UP_RENEWAL:
				while points >= 10:
					net.SendChatPacket("/stat %s 10" % cmdKey)
					points -= 10
			while points > 0:
				net.SendChatPacket("/stat %s" % cmdKey)
				points -= 1
		self.Close()

class SkillPopupDialog(ui.Window):
	def __init__(self, skillIndex, srcSlotIndex):
		ui.Window.__init__(self, "TOP_MOST")
		uiMobileCompat.EnableSingleTap(self)
		self.skillIndex = skillIndex
		self.srcSlotIndex = srcSlotIndex
		self.addPoints = 0

		self.width = 310
		self.height = 210
		self.SetSize(self.width, self.height)

		self.panel = uiMobileStyle.CreateOrnatePanel(self, 0, 0, self.width, self.height)

		import skill
		skillName = skill.GetSkillName(skillIndex) if skillIndex else "Beceri"
		self.titleText = uiMobileStyle.CreateText(
			self,
			skillName,
			self.width // 2,
			14,
			uiMobileStyle.GOLD_COLOR,
			uiMobileStyle.FONT_LARGE,
			"center"
		)

		self.levelText = uiMobileStyle.CreateText(
			self,
			"",
			self.width // 2,
			42,
			uiMobileStyle.BRIGHT_COLOR,
			uiMobileStyle.FONT_MEDIUM,
			"center"
		)

		self.availText = uiMobileStyle.CreateText(
			self,
			"",
			self.width // 2,
			64,
			uiMobileStyle.SOFT_COLOR,
			uiMobileStyle.FONT_SMALL,
			"center"
		)

		yStep = 92
		btnSize = 42

		self.btnMinus10 = uiMobileStyle.PillButton(44, btnSize, "-10", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_SMALL)
		self.btnMinus10.SetParent(self)
		self.btnMinus10.SetPosition(14, yStep)
		self.btnMinus10.SetEvent(ui.__mem_func__(self.__Change), -10)
		self.btnMinus10.Show()

		self.btnMinus1 = uiMobileStyle.PillButton(36, btnSize, "-1", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.btnMinus1.SetParent(self)
		self.btnMinus1.SetPosition(64, yStep)
		self.btnMinus1.SetEvent(ui.__mem_func__(self.__Change), -1)
		self.btnMinus1.Show()

		self.valueText = uiMobileStyle.CreateText(
			self,
			"",
			self.width // 2,
			yStep + 10,
			uiMobileStyle.BRIGHT_COLOR,
			uiMobileStyle.FONT_LARGE,
			"center"
		)

		self.btnPlus1 = uiMobileStyle.PillButton(36, btnSize, "+1", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.btnPlus1.SetParent(self)
		self.btnPlus1.SetPosition(self.width - 100, yStep)
		self.btnPlus1.SetEvent(ui.__mem_func__(self.__Change), 1)
		self.btnPlus1.Show()

		self.btnPlus10 = uiMobileStyle.PillButton(44, btnSize, "+10", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_SMALL)
		self.btnPlus10.SetParent(self)
		self.btnPlus10.SetPosition(self.width - 58, yStep)
		self.btnPlus10.SetEvent(ui.__mem_func__(self.__Change), 10)
		self.btnPlus10.Show()

		yBottom = 152
		btnW = 120
		btnH = 36

		self.btnApply = uiMobileStyle.PillButton(btnW, btnH, "Uygula", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.btnApply.SetParent(self)
		self.btnApply.SetPosition(20, yBottom)
		self.btnApply.SetEvent(ui.__mem_func__(self.__Apply))
		self.btnApply.Show()

		self.btnCancel = uiMobileStyle.PillButton(btnW, btnH, "\xddptal", None, "field", uiMobileStyle.SOFT_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.btnCancel.SetParent(self)
		self.btnCancel.SetPosition(self.width - btnW - 20, yBottom)
		self.btnCancel.SetEvent(ui.__mem_func__(self.Close))
		self.btnCancel.Show()

		self.Refresh()

	def Destroy(self):
		self.skillIndex = None
		self.srcSlotIndex = None
		self.panel = None
		self.titleText = None
		self.levelText = None
		self.availText = None
		self.valueText = None
		if self.btnMinus10:
			self.btnMinus10.Destroy()
		if self.btnMinus1:
			self.btnMinus1.Destroy()
		if self.btnPlus1:
			self.btnPlus1.Destroy()
		if self.btnPlus10:
			self.btnPlus10.Destroy()
		if self.btnApply:
			self.btnApply.Destroy()
		if self.btnCancel:
			self.btnCancel.Destroy()
		self.btnMinus10 = None
		self.btnMinus1 = None
		self.btnPlus1 = None
		self.btnPlus10 = None
		self.btnApply = None
		self.btnCancel = None
		self.Hide()

	def Open(self, sw, sh):
		self.SetPosition((sw - self.width) // 2, (sh - self.height) // 2)
		self.SetTop()
		self.Show()

	def Close(self):
		self.Hide()

	def __GetAvailablePoints(self):
		import skill
		avail = player.GetStatus(player.SKILL_ACTIVE)
		if self.srcSlotIndex > 8:
			availHorse = player.GetStatus(player.SKILL_HORSE)
			if availHorse > 0:
				avail = availHorse
		curLevel = player.GetSkillLevel(self.srcSlotIndex)
		maxLevel = skill.GetSkillMaxLevel(self.skillIndex) if self.skillIndex else 20
		canAdd = max(0, maxLevel - curLevel)
		return min(avail, canAdd)

	def __Change(self, amount):
		maxAdd = self.__GetAvailablePoints()
		# addPoints asla 0'in altina inemez (mevcut beceri asla dusurulmez)
		newAdd = self.addPoints + amount
		newAdd = max(0, min(maxAdd, newAdd))
		self.addPoints = newAdd
		self.Refresh()

	def Refresh(self):
		import skill
		curLevel = player.GetSkillLevel(self.srcSlotIndex)
		maxLevel = skill.GetSkillMaxLevel(self.skillIndex) if self.skillIndex else 20
		avail = self.__GetAvailablePoints()
		newLevel = curLevel + self.addPoints
		self.levelText.SetText("Mevcut: %d / %d  |  Yeni: %d" % (curLevel, maxLevel, newLevel))
		self.availText.SetText("Kullan\xfdlabilir Puan: %d" % avail)
		self.valueText.SetText("+%d" % self.addPoints)

	def __Apply(self):
		# Sadece 0'dan buyuk pozitif puanlar gonderilir, asla beceri azaltilamaz
		if self.addPoints > 0:
			for _ in xrange(self.addPoints):
				net.SendChatPacket("/skillup " + str(self.skillIndex))
		self.Close()

_statusDialog = None

def OpenStatusPopup(statusKey):
	global _statusDialog
	import wndMgr
	titleMap = {
		"HTH": "Canl\xfdl\xfdk (HP)",
		"INT": "Zeka (SP)",
		"STR": "G\xfc\xe7 (STR)",
		"DEX": "\xc7eviklik (DEX)"
	}
	title = titleMap.get(statusKey, statusKey)
	curVal = 0
	if _statusDialog:
		_statusDialog.Destroy()
		_statusDialog = None
	_statusDialog = StatusPopupDialog(statusKey, title, curVal)
	sw = wndMgr.GetScreenWidth()
	sh = wndMgr.GetScreenHeight()
	_statusDialog.Open(sw, sh)

_skillDialog = None

def OpenSkillPopup(skillIndex, srcSlotIndex):
	global _skillDialog
	import wndMgr
	if _skillDialog:
		_skillDialog.Destroy()
		_skillDialog = None
	_skillDialog = SkillPopupDialog(skillIndex, srcSlotIndex)
	sw = wndMgr.GetScreenWidth()
	sh = wndMgr.GetScreenHeight()
	_skillDialog.Open(sw, sh)
