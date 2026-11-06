# -*- coding: cp1254 -*-
import ui
import item
import player
import net
import localeInfo
import snd
import wndMgr
import app
import mouseModule
import ime

class ItemActionPanel(ui.ThinBoard):
	WIDTH = 136
	BTN_WIDTH = 118
	BTN_HEIGHT = 28
	GAP = 6
	PAD_Y = 10
	PAD_X = 9

	def __init__(self):
		ui.ThinBoard.__init__(self, "UI")
		self.AddFlag("float")
		self.slotPos = -1
		self.itemVnum = 0
		self.itemCount = 0
		self.windowType = player.INVENTORY
		self.slotType = player.SLOT_TYPE_INVENTORY
		self.parentWnd = None

		self.btnUse = ui.Button()
		self.btnUse.SetParent(self)
		self.btnUse.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.btnUse.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.btnUse.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.btnUse.SetText("Kullan")
		self.btnUse.SetEvent(ui.__mem_func__(self.OnUse))
		self.btnUse.Hide()

		self.btnChest = ui.Button()
		self.btnChest.SetParent(self)
		self.btnChest.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.btnChest.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.btnChest.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.btnChest.SetText("Sandik Icerigi")
		self.btnChest.SetEvent(ui.__mem_func__(self.OnChestDrop))
		self.btnChest.Hide()

		self.btnSplit = ui.Button()
		self.btnSplit.SetParent(self)
		self.btnSplit.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.btnSplit.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.btnSplit.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.btnSplit.SetText("Nesneyi Ayir")
		self.btnSplit.SetEvent(ui.__mem_func__(self.OnSplit))
		self.btnSplit.Hide()

		self.btnLink = ui.Button()
		self.btnLink.SetParent(self)
		self.btnLink.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.btnLink.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.btnLink.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.btnLink.SetText("Yansit")
		self.btnLink.SetEvent(ui.__mem_func__(self.OnLink))
		self.btnLink.Hide()

		self.btnMove = ui.Button()
		self.btnMove.SetParent(self)
		self.btnMove.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.btnMove.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.btnMove.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.btnMove.SetText("Tasi")
		self.btnMove.SetEvent(ui.__mem_func__(self.OnMove))
		self.btnMove.Hide()

		self.btnClose = ui.Button()
		self.btnClose.SetParent(self)
		self.btnClose.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.btnClose.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.btnClose.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.btnClose.SetText("Kapat")
		self.btnClose.SetEvent(ui.__mem_func__(self.Close))
		self.btnClose.Hide()

		self.Hide()

	def __del__(self):
		ui.ThinBoard.__del__(self)

	def __GetInterface(self):
		interface = getattr(self.parentWnd, "interface", None) if self.parentWnd else None
		if not interface:
			try:
				import uiMobileHud
				ctrl = uiMobileHud.GetController()
				if ctrl and getattr(ctrl, "interface", None):
					interface = ctrl.interface
			except Exception:
				pass
		return interface

	def IsChatOrWhisperOpen(self):
		interface = self.__GetInterface()

		# 1. Check Whisper Dialogs
		if interface and hasattr(interface, "whisperDialogDict") and interface.whisperDialogDict:
			try:
				for name, dlg in interface.whisperDialogDict.items():
					if dlg and dlg.IsShow():
						return True
			except Exception:
				pass

		# 2. Check Oto Bagirma (wndShout)
		if interface and getattr(interface, "wndShout", None):
			try:
				if interface.wndShout.IsShow():
					return True
			except Exception:
				pass

		# 3. Check Mobile ChatController in uiMobileHud
		try:
			import uiMobileHud
			ctrl = uiMobileHud.GetController()
			if ctrl and getattr(ctrl, "chatController", None):
				cc = ctrl.chatController
				if cc.expanded and cc.panel and cc.panel.IsShow():
					return True
		except Exception:
			pass

		# 4. Check interface.wndChat
		if interface and getattr(interface, "wndChat", None):
			try:
				if interface.wndChat.IsShow():
					return True
			except Exception:
				pass

		return False

	def Open(self, parentWnd, slotPos, windowType = player.INVENTORY, slotType = player.SLOT_TYPE_INVENTORY):
		self.parentWnd = parentWnd
		self.slotPos = slotPos
		self.windowType = windowType
		self.slotType = slotType

		if self.windowType == player.INVENTORY:
			self.itemVnum = player.GetItemIndex(self.slotPos)
			self.itemCount = player.GetItemCount(self.slotPos)
		else:
			self.itemVnum = player.GetItemIndex(self.windowType, self.slotPos)
			self.itemCount = player.GetItemCount(self.windowType, self.slotPos)

		if self.itemVnum == 0 or self.itemCount <= 0:
			self.Close()
			return

		item.SelectItem(self.itemVnum)
		itemType = item.GetItemType()

		visibleButtons = []

		# 1. Sandik Icerigi (Chest Drop Preview)
		isChest = False
		giftboxType = getattr(item, "ITEM_TYPE_GIFTBOX", 15)
		treasureBoxType = getattr(item, "ITEM_TYPE_TREASURE_BOX", 16)
		if itemType in (giftboxType, treasureBoxType):
			isChest = True
		elif self.parentWnd and hasattr(self.parentWnd, "interface") and self.parentWnd.interface:
			dlg = getattr(self.parentWnd.interface, "dlgChestDrop", None)
			if dlg and hasattr(dlg, "HasChestDrop"):
				if dlg.HasChestDrop(self.itemVnum):
					isChest = True

		if isChest:
			self.btnChest.SetText("Sandik Icerigi")
			visibleButtons.append(self.btnChest)

		# 2. Kullan (Use / Equip / Open)
		isUsable = False
		usableTypes = (
			getattr(item, "ITEM_TYPE_USE", 3),
			getattr(item, "ITEM_TYPE_ARMOR", 2),
			getattr(item, "ITEM_TYPE_WEAPON", 1),
			getattr(item, "ITEM_TYPE_COSTUME", 28),
			getattr(item, "ITEM_TYPE_LOTTERY", 14),
			getattr(item, "ITEM_TYPE_SKILLBOOK", 17),
			getattr(item, "ITEM_TYPE_SKILLFORGET", 23),
			getattr(item, "ITEM_TYPE_QUEST", 18),
			giftboxType,
			getattr(item, "ITEM_TYPE_RING", 29),
			getattr(item, "ITEM_TYPE_BELT", 34),
		)
		if itemType in usableTypes:
			isUsable = True
		elif not item.IsAntiFlag(getattr(item, "ANTIFLAG_USE", 262144)) and itemType != getattr(item, "ITEM_TYPE_NONE", 0):
			isUsable = True

		itemName = item.GetItemName() or ""
		lowerName = itemName.lower()
		if "coin" in lowerName or "parca" in lowerName or "sandik" in lowerName:
			isUsable = True

		isEquipped = False
		if self.windowType == player.INVENTORY:
			try:
				if player.IsEquipmentSlot(self.slotPos) or player.IsCostumeSlot(self.slotPos) or (app.ENABLE_NEW_EQUIPMENT_SYSTEM and player.IsBeltInventorySlot(self.slotPos)):
					isEquipped = True
			except Exception:
				if self.slotPos >= getattr(player, "EQUIPMENT_SLOT_START", 180):
					isEquipped = True

		if isEquipped:
			self.btnUse.SetText("Cikar")
			visibleButtons.append(self.btnUse)
		elif isUsable:
			if itemType in (getattr(item, "ITEM_TYPE_ARMOR", 2), getattr(item, "ITEM_TYPE_WEAPON", 1), getattr(item, "ITEM_TYPE_COSTUME", 28), getattr(item, "ITEM_TYPE_RING", 29), getattr(item, "ITEM_TYPE_BELT", 34)):
				self.btnUse.SetText("Giy / Tak")
			elif isChest:
				self.btnUse.SetText("Sandigi Ac")
			else:
				self.btnUse.SetText("Kullan")
			visibleButtons.append(self.btnUse)

		# 3. Nesneyi Ayir (Split)
		if self.itemCount > 1:
			self.btnSplit.SetText("Nesneyi Ayir")
			visibleButtons.append(self.btnSplit)

		# 4. Yansit (Item Reflection in Chat/Whisper)
		if self.IsChatOrWhisperOpen():
			self.btnLink.SetText("Yansit")
			visibleButtons.append(self.btnLink)

		# 5. Tasi (Move)
		self.btnMove.SetText("Tasi")
		visibleButtons.append(self.btnMove)

		# 6. Kapat (Close)
		self.btnClose.SetText("Kapat")
		visibleButtons.append(self.btnClose)

		# Hide all first
		for b in (self.btnUse, self.btnChest, self.btnSplit, self.btnLink, self.btnMove, self.btnClose):
			b.Hide()

		# Layout
		curY = self.PAD_Y
		for b in visibleButtons:
			b.SetPosition(self.PAD_X, curY)
			b.Show()
			curY += self.BTN_HEIGHT + self.GAP

		totalH = curY - self.GAP + self.PAD_Y
		self.SetSize(self.WIDTH, totalH)

		self.AdjustPosition()
		self.SetTop()
		self.Show()

	def AdjustPosition(self):
		if not self.parentWnd:
			return

		(parentX, parentY) = self.parentWnd.GetGlobalPosition()

		# Fixed position docked cleanly to the LEFT side of parent window (Inventory or K Inventory)
		px = parentX - self.WIDTH - 4
		if px < 4:
			px = 4

		py = parentY + 70
		if py + self.GetHeight() > wndMgr.GetScreenHeight():
			py = max(4, wndMgr.GetScreenHeight() - self.GetHeight() - 10)

		self.SetPosition(px, py)

	def OnUse(self):
		if self.parentWnd and self.slotPos >= 0:
			if hasattr(self.parentWnd, "UseItemSlotWithoutConvert"):
				self.parentWnd.UseItemSlotWithoutConvert(self.slotPos)
			elif hasattr(self.parentWnd, "UseItemSlot"):
				self.parentWnd.UseItemSlot(self.slotPos)
			elif hasattr(self.parentWnd, "_InventoryWindow__UseItem"):
				self.parentWnd._InventoryWindow__UseItem(self.slotPos)
		self.Close()

	def OnChestDrop(self):
		if self.parentWnd and self.slotPos >= 0:
			if hasattr(self.parentWnd, "interface") and self.parentWnd.interface:
				dlg = getattr(self.parentWnd.interface, "dlgChestDrop", None)
				if dlg:
					dlg.Open(self.slotPos)
					net.SendChestDropInfo(self.slotPos)
		self.Close()

	def OnSplit(self):
		if self.parentWnd and self.slotPos >= 0 and self.itemCount > 1:
			dlg = getattr(self.parentWnd, "dlgPickMoney", None) or getattr(self.parentWnd, "dlgSplitItems", None)
			if dlg:
				dlg.SetTitleName(localeInfo.PICK_ITEM_TITLE)
				dlg.SetAcceptEvent(ui.__mem_func__(self.parentWnd.OnPickItem))
				dlg.Open(self.itemCount)
				dlg.itemGlobalSlotIndex = self.slotPos
		self.Close()

	def OnLink(self):
		if self.parentWnd and self.slotPos >= 0:
			link = ""
			try:
				if self.windowType == player.INVENTORY:
					link = player.GetItemLink(self.slotPos)
				else:
					link = player.GetItemLink(self.windowType, self.slotPos)
			except Exception:
				try:
					link = player.GetItemLink(self.slotPos)
				except Exception:
					link = ""

			if link:
				targetEdit = None
				interface = self.__GetInterface()

				# 1. Check open whisper dialogs first
				if interface and hasattr(interface, "whisperDialogDict") and interface.whisperDialogDict:
					try:
						for name, dlg in interface.whisperDialogDict.items():
							if dlg and dlg.IsShow():
								targetEdit = getattr(dlg, "chatLine", None)
								if targetEdit:
									break
					except Exception:
						pass

				# 2. Check mobile chat panel
				if not targetEdit:
					try:
						import uiMobileHud
						ctrl = uiMobileHud.GetController()
						if ctrl and getattr(ctrl, "chatController", None):
							cc = ctrl.chatController
							if cc.expanded and cc.panel and cc.panel.IsShow() and cc.panel.input:
								targetEdit = cc.panel.input
					except Exception:
						pass

				# 3. Check Oto Bagirma (wndShout)
				if not targetEdit and interface and getattr(interface, "wndShout", None):
					try:
						if interface.wndShout.IsShow():
							targetEdit = getattr(interface.wndShout, "yazi", None)
					except Exception:
						pass

				# 4. Check interface.wndChat
				if not targetEdit and interface and getattr(interface, "wndChat", None):
					try:
						if interface.wndChat.IsShow():
							targetEdit = getattr(interface.wndChat, "chatInputSet", None) or getattr(interface.wndChat, "chatLine", None)
					except Exception:
						pass

				if targetEdit:
					try:
						targetEdit.SetFocus()
					except Exception:
						pass
					try:
						ime.PasteString(link)
					except Exception:
						pass
					try:
						curText = targetEdit.GetText() or ""
						if link not in curText:
							if curText and not curText.endswith(" "):
								targetEdit.SetText(curText + " " + link + " ")
							else:
								targetEdit.SetText(curText + link + " ")
					except Exception:
						pass

				snd.PlaySound("sound/ui/click.wav")
		self.Close()

	def OnMove(self):
		if self.parentWnd and self.slotPos >= 0 and self.itemVnum > 0:
			mouseModule.mouseController.AttachObject(self.parentWnd, self.slotType, self.slotPos, self.itemVnum, self.itemCount)
			snd.PlaySound("sound/ui/pick.wav")
		self.Close()

	def Close(self):
		self.slotPos = -1
		self.Hide()
