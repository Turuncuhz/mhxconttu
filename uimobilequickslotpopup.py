# -*- coding: cp1254 -*-
from __future__ import division
import ui
import net
import player
import item
import skill
import wndMgr
import dbg
import uimobilestyle as uiMobileStyle
import uimobilecompat as uiMobileCompat

PAGE_SIZE = 15

class QuickSlotPicker(ui.Window):
	def __init__(self, targetSlotIndex):
		ui.Window.__init__(self, "TOP_MOST")
		self.AddFlag("movable")
		self.AddFlag("float")
		uiMobileCompat.EnableSingleTap(self)
		self.targetSlotIndex = targetSlotIndex
		self.tabMode = "SKILLS"
		self.curPage = 0
		self.dataList = []

		self.width = 330
		self.height = 340
		self.SetSize(self.width, self.height)

		self.panel = uiMobileStyle.CreateOrnatePanel(self, 0, 0, self.width, self.height)

		labels = ("1", "2", "3", "4", "F1", "F2", "F3", "F4")
		slotLabel = labels[targetSlotIndex % len(labels)] if targetSlotIndex < len(labels) else str(targetSlotIndex + 1)

		self.titleText = uiMobileStyle.CreateText(
			self,
			"H\xfdzl\xfd Slot Ata (Slot %s)" % slotLabel,
			self.width // 2,
			14,
			uiMobileStyle.GOLD_COLOR,
			uiMobileStyle.FONT_LARGE,
			"center"
		)

		btnW = 130
		btnH = 32
		yTab = 44

		self.btnTabSkills = uiMobileStyle.PillButton(btnW, btnH, "Beceriler", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.btnTabSkills.SetParent(self)
		self.btnTabSkills.SetPosition(25, yTab)
		self.btnTabSkills.SetEvent(lambda *args: self.__SetTab("SKILLS"))
		self.btnTabSkills.Show()

		self.btnTabItems = uiMobileStyle.PillButton(btnW, btnH, "E\xfe\xfda & \xddksir", None, "field", uiMobileStyle.SOFT_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.btnTabItems.SetParent(self)
		self.btnTabItems.SetPosition(self.width - btnW - 25, yTab)
		self.btnTabItems.SetEvent(lambda *args: self.__SetTab("ITEMS"))
		self.btnTabItems.Show()

		slotSize = 32
		slotGap = 8
		gridW = 5 * slotSize + 4 * slotGap
		gridX = (self.width - gridW) // 2
		gridY = 88

		self.slotWindow = ui.GridSlotWindow()
		self.slotWindow.SetParent(self)
		self.slotWindow.SetPosition(gridX, gridY)
		self.slotWindow.SetSlotStyle(wndMgr.SLOT_STYLE_NONE)
		self.slotWindow.ArrangeSlot(0, 5, 3, slotSize, slotSize, slotGap, slotGap)
		try:
			self.slotWindow.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)
		except Exception:
			pass
		self.slotWindow.SetSelectItemSlotEvent(ui.__mem_func__(self.__OnSelectSlot))
		self.slotWindow.SetOverInItemEvent(ui.__mem_func__(self.__OnOverIn))
		self.slotWindow.SetOverOutItemEvent(ui.__mem_func__(self.__OnOverOut))
		uiMobileCompat.EnableSingleTap(self.slotWindow)
		self.slotWindow.Show()

		self.infoText = uiMobileStyle.CreateText(
			self,
			"",
			self.width // 2,
			236,
			uiMobileStyle.BRIGHT_COLOR,
			uiMobileStyle.FONT_SMALL,
			"center"
		)

		self.btnPrevPage = uiMobileStyle.PillButton(34, 28, "<", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_SMALL)
		self.btnPrevPage.SetParent(self)
		self.btnPrevPage.SetPosition(25, 230)
		self.btnPrevPage.SetEvent(ui.__mem_func__(self.__ChangePage), -1)

		self.btnNextPage = uiMobileStyle.PillButton(34, 28, ">", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_SMALL)
		self.btnNextPage.SetParent(self)
		self.btnNextPage.SetPosition(self.width - 34 - 25, 230)
		self.btnNextPage.SetEvent(ui.__mem_func__(self.__ChangePage), 1)

		yBottom = 274
		bBtnW = 130
		bBtnH = 36

		self.btnClear = uiMobileStyle.PillButton(bBtnW, bBtnH, "Slotu Bo\xfealt", None, "field", uiMobileStyle.SOFT_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.btnClear.SetParent(self)
		self.btnClear.SetPosition(25, yBottom)
		self.btnClear.SetEvent(ui.__mem_func__(self.__ClearSlot))
		self.btnClear.Show()

		self.btnClose = uiMobileStyle.PillButton(bBtnW, bBtnH, "Kapat", None, "field", uiMobileStyle.GOLD_COLOR, uiMobileStyle.FONT_MEDIUM)
		self.btnClose.SetParent(self)
		self.btnClose.SetPosition(self.width - bBtnW - 25, yBottom)
		self.btnClose.SetEvent(ui.__mem_func__(self.Close))
		self.btnClose.Show()

		self.__LoadData()

	def Destroy(self):
		self.targetSlotIndex = None
		self.dataList = []
		self.panel = None
		self.titleText = None
		self.infoText = None
		if self.btnTabSkills:
			self.btnTabSkills.Destroy()
		if self.btnTabItems:
			self.btnTabItems.Destroy()
		if self.btnPrevPage:
			self.btnPrevPage.Destroy()
		if self.btnNextPage:
			self.btnNextPage.Destroy()
		if self.btnClear:
			self.btnClear.Destroy()
		if self.btnClose:
			self.btnClose.Destroy()
		self.btnTabSkills = None
		self.btnTabItems = None
		self.btnPrevPage = None
		self.btnNextPage = None
		self.btnClear = None
		self.btnClose = None
		self.slotWindow = None
		self.Hide()

	def Open(self, sw, sh):
		self.SetPosition((sw - self.width) // 2, (sh - self.height) // 2)
		self.SetTop()
		self.Show()

	def Close(self):
		self.Hide()

	def __SetTab(self, tab):
		self.tabMode = tab
		self.curPage = 0
		try:
			if tab == "SKILLS":
				if hasattr(self.btnTabSkills, "SetTextColor"):
					self.btnTabSkills.SetTextColor(uiMobileStyle.GOLD_COLOR)
				if hasattr(self.btnTabItems, "SetTextColor"):
					self.btnTabItems.SetTextColor(uiMobileStyle.SOFT_COLOR)
			else:
				if hasattr(self.btnTabSkills, "SetTextColor"):
					self.btnTabSkills.SetTextColor(uiMobileStyle.SOFT_COLOR)
				if hasattr(self.btnTabItems, "SetTextColor"):
					self.btnTabItems.SetTextColor(uiMobileStyle.GOLD_COLOR)
		except Exception:
			pass
		self.__LoadData()

	def __ChangePage(self, delta):
		maxPage = max(0, (len(self.dataList) - 1) // PAGE_SIZE)
		newPage = self.curPage + delta
		if 0 <= newPage <= maxPage:
			self.curPage = newPage
			self.__RefreshSlots()

	def __LoadData(self):
		if self.tabMode == "SKILLS":
			self.dataList = self.__QuerySkills()
		else:
			self.dataList = self.__QueryItems()
		self.__RefreshSlots()

	def __QuerySkills(self):
		res = []
		for slot in xrange(1, 256):
			try:
				skillIndex = player.GetSkillIndex(slot)
				if skillIndex <= 0:
					continue
				isUsable = False
				try:
					if skill.CanUseSkill(skillIndex):
						isUsable = True
					elif skill.GetSkillType(skillIndex) == skill.SKILL_TYPE_ACTIVE:
						isUsable = True
					elif skillIndex in (137, 138, 139, 140):
						isUsable = True
				except Exception:
					isUsable = True

				if isUsable and not any(s["skillIndex"] == skillIndex for s in res):
					grade = player.GetSkillGrade(slot)
					level = player.GetSkillLevel(slot)
					name = ""
					try:
						name = skill.GetSkillName(skillIndex)
					except Exception:
						name = "Beceri %d" % skillIndex
					res.append({
						"type": "SKILL",
						"srcSlot": slot,
						"skillIndex": skillIndex,
						"grade": grade,
						"level": level,
						"name": name if name else ("Beceri %d" % skillIndex)
					})
			except Exception:
				continue
		return res

	def __QueryItems(self):
		res = []
		seen = set()
		totalSlots = 180
		try:
			invCount = getattr(player, "INVENTORY_PAGE_COUNT", 4)
			pageSize = getattr(player, "INVENTORY_PAGE_SIZE", 45)
			totalSlots = invCount * pageSize
		except Exception:
			totalSlots = 180

		for slotPos in xrange(totalSlots):
			try:
				itemIndex = player.GetItemIndex(slotPos)
				if itemIndex <= 0:
					continue
				canAdd = True
				try:
					item.SelectItem(itemIndex)
					iType = item.GetItemType()
					if hasattr(item, "CanAddToQuickSlotItem"):
						try:
							canAdd = bool(item.CanAddToQuickSlotItem(itemIndex))
						except Exception:
							canAdd = (iType in (item.ITEM_TYPE_USE, item.ITEM_TYPE_QUEST))
					else:
						canAdd = (iType in (item.ITEM_TYPE_USE, item.ITEM_TYPE_QUEST))
				except Exception:
					canAdd = True

				if canAdd and itemIndex not in seen:
					seen.add(itemIndex)
					itemCount = player.GetItemCount(slotPos)
					name = ""
					try:
						item.SelectItem(itemIndex)
						name = item.GetItemName()
					except Exception:
						name = "Esya %d" % itemIndex
					res.append({
						"type": "ITEM",
						"slotPos": slotPos,
						"itemIndex": itemIndex,
						"count": itemCount,
						"name": name if name else ("Esya %d" % itemIndex)
					})
			except Exception:
				continue
		return res

	def __RefreshSlots(self):
		for i in xrange(PAGE_SIZE):
			self.slotWindow.ClearSlot(i)

		startIdx = self.curPage * PAGE_SIZE
		pageItems = self.dataList[startIdx : startIdx + PAGE_SIZE]

		for idx, entry in enumerate(pageItems):
			if entry["type"] == "SKILL":
				self.slotWindow.SetSkillSlotNew(idx, entry["skillIndex"], entry["grade"], entry["level"])
				self.slotWindow.SetSlotCountNew(idx, entry["grade"], entry["level"])
			else:
				self.slotWindow.SetItemSlot(idx, entry["itemIndex"], entry["count"])

		self.slotWindow.RefreshSlot()

		maxPage = max(0, (len(self.dataList) - 1) // PAGE_SIZE)
		if maxPage > 0:
			self.btnPrevPage.Show()
			self.btnNextPage.Show()
			self.infoText.SetText("Sayfa %d / %d (%d se\xe7enek)" % (self.curPage + 1, maxPage + 1, len(self.dataList)))
		else:
			self.btnPrevPage.Hide()
			self.btnNextPage.Hide()
			if len(self.dataList) == 0:
				emptyMsg = "Kullan\xfdlabilir beceri bulunamad\xfd" if self.tabMode == "SKILLS" else "Envanterde uygun iksir/e\xfe\xfda yok"
				self.infoText.SetText(emptyMsg)
			else:
				self.infoText.SetText("Se\xe7mek i\xe7in bir simgeye dokunun")

	def __OnSelectSlot(self, slotIndex):
		dataIndex = self.curPage * PAGE_SIZE + slotIndex
		if dataIndex < len(self.dataList):
			entry = self.dataList[dataIndex]
			if entry["type"] == "SKILL":
				player.RequestAddLocalQuickSlot(self.targetSlotIndex, player.SLOT_TYPE_SKILL, entry["srcSlot"])
			else:
				player.RequestAddLocalQuickSlot(self.targetSlotIndex, player.SLOT_TYPE_INVENTORY, entry["slotPos"])
			self.Close()

	def __OnOverIn(self, slotIndex):
		dataIndex = self.curPage * PAGE_SIZE + slotIndex
		if dataIndex < len(self.dataList):
			entry = self.dataList[dataIndex]
			self.infoText.SetText(entry["name"])

	def __OnOverOut(self):
		maxPage = max(0, (len(self.dataList) - 1) // PAGE_SIZE)
		if maxPage > 0:
			self.infoText.SetText("Sayfa %d / %d (%d se\xe7enek)" % (self.curPage + 1, maxPage + 1, len(self.dataList)))
		else:
			self.infoText.SetText("Se\xe7mek i\xe7in bir simgeye dokunun")

	def __ClearSlot(self):
		globalIdx = player.LocalQuickSlotIndexToGlobalQuickSlotIndex(self.targetSlotIndex)
		player.RequestDeleteGlobalQuickSlot(globalIdx)
		self.Close()

_pickerDialog = None

def OpenQuickSlotPicker(targetSlotIndex):
	global _pickerDialog
	try:
		if _pickerDialog:
			_pickerDialog.Destroy()
			_pickerDialog = None
		_pickerDialog = QuickSlotPicker(targetSlotIndex)
		sw = wndMgr.GetScreenWidth()
		sh = wndMgr.GetScreenHeight()
		_pickerDialog.Open(sw, sh)
	except Exception as e:
		dbg.TraceError("OpenQuickSlotPicker error: %s" % str(e))
