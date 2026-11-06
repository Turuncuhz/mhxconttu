import ui
import player
import mouseModule
import ime
import net
import app
import snd
import item
import chat
import uiScriptLocale
import uiCommon
import uiPrivateShopBuilder
import uiPickMoney
import uiToolTip
import localeInfo
import constInfo
import shop
import grp
import systemSetting
import uiPickItem
import uiitemactionpanel
import pysettings
import exchange

if app.ENABLE_IKASHOP_RENEWAL:
	import ikashop

class SpecialStorageWindow(ui.ScriptWindow):
	UPGRADE_TYPE = 0
	BOOK_TYPE = 1
	STONE_TYPE = 2
	CHEST_TYPE = 3
	remaining_time = 0

	InventoryMode = []
	if app.ENABLE_ITEM_DELETE_SYSTEM:
		wndItemDelete = None

	SLOT_WINDOW_TYPE = {
		UPGRADE_TYPE	:	{"window" : player.UPGRADE_INVENTORY, "slot" : player.SLOT_TYPE_UPGRADE_INVENTORY},
		BOOK_TYPE	:	{"window" : player.BOOK_INVENTORY, "slot" : player.SLOT_TYPE_BOOK_INVENTORY},
		STONE_TYPE	:	{"window" : player.STONE_INVENTORY, "slot" : player.SLOT_TYPE_STONE_INVENTORY},
		CHEST_TYPE	:	{"window" : player.CHEST_INVENTORY, "slot" : player.SLOT_TYPE_CHEST_INVENTORY}
	}

	WINDOW_NAMES = {
		UPGRADE_TYPE	:	uiScriptLocale.INVENTORY1_TITLE,
		BOOK_TYPE	:	uiScriptLocale.INVENTORY2_TITLE,
		STONE_TYPE	:	uiScriptLocale.INVENTORY3_TITLE,
		CHEST_TYPE	:	uiScriptLocale.INVENTORY4_TITLE
	}

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.questionDialog = None
		self.tooltipItem = None
		self.dlgSplitItems = None
		self.sellingSlotNumber = -1
		self.isLoaded = 0
		self.inventoryPageIndex = 0
		self.categoryPageIndex = 0
		self.actionPanel = uiitemactionpanel.ItemActionPanel()
		self.heldSlotPos = -1
		self.heldSlotTime = 0.0
		self.isHeldAttached = False
		self.interface = None
		self.SetWindowName("SpecialStorageWindow")
		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self):
		self.__LoadWindow()
		ui.ScriptWindow.Show(self)

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1
		self.InventoryMode = []

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/SpecialStorageWindow.py")
		except:
			import exception
			exception.Abort("SpecialStorageWindow.LoadWindow.LoadObject")

		try:
			wndItem = self.GetChild("ItemSlot")
			self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))
			self.titleName = self.GetChild("TitleName")
			self.inventoryTab = []
			self.inventoryTab.append(self.GetChild("Inventory_Tab_01"))
			self.inventoryTab.append(self.GetChild("Inventory_Tab_02"))
			self.inventoryTab.append(self.GetChild("Inventory_Tab_03"))
			self.inventoryTab.append(self.GetChild("Inventory_Tab_04"))
			self.InventoryMode.append(self.GetChild("InventoryMode_On"))
			self.InventoryMode.append(self.GetChild("InventoryMode_Off"))
			self.MalzemeDeposuInfo = self.GetChild("MalzemeDeposuInfo")

			self.categoryTab = []
			self.categoryTab.append(self.GetChild("Category_Tab_01"))
			self.categoryTab.append(self.GetChild("Category_Tab_02"))
			self.categoryTab.append(self.GetChild("Category_Tab_03"))
			self.categoryTab.append(self.GetChild("Category_Tab_04"))

			self.SiralaButton = self.GetChild("SiralaButton")

		except:
			import exception
			exception.Abort("SpecialStorageWindow.LoadWindow.BindObject")

		## Info
		self.tlInfo = uiToolTip.ItemToolTip()
		self.tlInfo.Hide()
		self.tooltipInfo = [self.tlInfo]*7
		self.InformationText = [localeInfo.MALZEME_DEPOSU,
								localeInfo.BK_ENVANTER_TEXT1,
								localeInfo.BK_ENVANTER_TEXT2,
								localeInfo.BK_ENVANTER_TEXT3,
								localeInfo.BK_ENVANTER_TEXT4,
								localeInfo.BK_ENVANTER_TEXT5,
								localeInfo.BK_ENVANTER_TEXT6
		]
		
		for i in xrange(7):
			self.tooltipInfo[i].SetFollow(True)
			self.tooltipInfo[i].AlignHorizonalCenter()
			if i == 0:
				TITLE_COLOR = grp.GenerateColor(0.9490, 0.9058, 0.7568, 1.0)
				self.tooltipInfo[i].AutoAppendTextLine(self.InformationText[i], TITLE_COLOR)
			else:
				self.tooltipInfo[i].AutoAppendTextLine(self.InformationText[i])
			self.tooltipInfo[i].Hide()
			self.tooltipInfo[i].toolTipWidth += 10

		## Item
		wndItem.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		wndItem.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		wndItem.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		wndItem.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		wndItem.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))


		## Grade button
		self.inventoryTab[0].SetEvent(lambda arg=0: self.SetInventoryPage(arg))
		self.inventoryTab[1].SetEvent(lambda arg=1: self.SetInventoryPage(arg))
		self.inventoryTab[2].SetEvent(lambda arg=2: self.SetInventoryPage(arg))
		self.inventoryTab[3].SetEvent(lambda arg=3: self.SetInventoryPage(arg))
		self.inventoryTab[0].Down()

		self.categoryTab[0].SetEvent(lambda arg=0: self.SetCategoryPage(arg))
		self.categoryTab[1].SetEvent(lambda arg=1: self.SetCategoryPage(arg))
		self.categoryTab[2].SetEvent(lambda arg=2: self.SetCategoryPage(arg))
		self.categoryTab[3].SetEvent(lambda arg=3: self.SetCategoryPage(arg))
		self.categoryTab[0].Down()

		## On Off button
		self.InventoryMode[0].SAFE_SetEvent(self.InventoryMode_On)
		self.InventoryMode[1].SAFE_SetEvent(self.InventoryMode_Off)

		## Etc
		self.wndItem = wndItem

		self.wndPopupDialog = uiCommon.PopupDialog()

		self.dlgSplitItems = uiPickItem.PickItemDialog()
		self.dlgSplitItems.LoadDialog()
		self.dlgSplitItems.Hide()

		if self.SiralaButton:
			self.SiralaButton.SetEvent(ui.__mem_func__(self.ClickSirala))

		if app.ENABLE_HIGHLIGHT_NEW_ITEM:
			self.listHighlightedSlotBook = []
			self.listHighlightedSlotUpgrade = []
			self.listHighlightedSlotStone = []
			self.listHighlightedSlotChest = []

		self.SetCategoryPage(0)
		self.RefreshItemSlot()
		self.RefreshBagSlotWindow()
		self.InventoryMode_Refresh()

	def OnRunMouseWheel(self, a):
		if a > 0:
			index = self.inventoryPageIndex-1
			if index < 0:
				self.inventoryPageIndex = 3
				index = 3
			else:
				self.inventoryPageIndex = index
		else:
			index = 1 + self.inventoryPageIndex
			if index > 3:
				self.inventoryPageIndex = 0
				index = 0
			else:
				self.inventoryPageIndex = index

		for i in xrange(4):
			self.inventoryTab[i].SetUp()

		self.inventoryTab[index].Down()

		self.RefreshBagSlotWindow()

	def SetInventoryPage(self, page):
		self.inventoryTab[self.inventoryPageIndex].SetUp()
		self.inventoryPageIndex = page
		self.inventoryTab[self.inventoryPageIndex].Down()

		self.RefreshBagSlotWindow()

	def Destroy(self):
		self.ClearDictionary()
		self.tooltipItem = None
		self.wndItem = 0
		self.questionDialog = None
		self.dlgSplitItems.Destroy()
		self.dlgSplitItems = None
		self.inventoryTab = []
		self.categoryTab = []
		self.titleName = None
		self.interface = None

	if app.ENABLE_HIGHLIGHT_NEW_ITEM:
		def HighlightSlot(self, slot, inven_type):
			if inven_type == player.BOOK_INVENTORY:
				if not slot in self.listHighlightedSlotBook:
					self.listHighlightedSlotBook.append(slot)
			elif inven_type == player.UPGRADE_INVENTORY:
				if not slot in self.listHighlightedSlotUpgrade:
					self.listHighlightedSlotUpgrade.append(slot)
			elif inven_type == player.STONE_INVENTORY:
				if not slot in self.listHighlightedSlotStone:
					self.listHighlightedSlotStone.append(slot)
			elif inven_type == player.CHEST_INVENTORY:
				if not slot in self.listHighlightedSlotChest:
					self.listHighlightedSlotChest.append(slot)

		def __RefreshHighlights(self):
			for i in xrange(player.SPECIAL_PAGE_SIZE*player.SPECIAL_PAGE_COUNT):
				slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
				if self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"] == player.BOOK_INVENTORY:
					if slotNumber in self.listHighlightedSlotBook:
						self.wndItem.ActivateSlot(i)
				elif self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"] == player.UPGRADE_INVENTORY:
					if slotNumber in self.listHighlightedSlotUpgrade:
						self.wndItem.ActivateSlot(i)
				elif self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"] == player.STONE_INVENTORY:
					if slotNumber in self.listHighlightedSlotStone:
						self.wndItem.ActivateSlot(i)
				elif self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"] == player.CHEST_INVENTORY:
					if slotNumber in self.listHighlightedSlotChest:
						self.wndItem.ActivateSlot(i)

	def Close(self):
		if hasattr(self, "actionPanel") and self.actionPanel:
			self.actionPanel.Close()
		self.heldSlotPos = -1
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()
		for i in xrange(7):
			if self.tooltipInfo != None:
				self.tooltipInfo[i].Hide()
		if self.dlgSplitItems:
			self.dlgSplitItems.Close()
		self.Hide()

	def OnUpdate(self):
		if hasattr(self, "actionPanel") and self.actionPanel and self.actionPanel.IsShow():
			self.actionPanel.AdjustPosition()
		for i in xrange(7):
			if self.MalzemeDeposuInfo.IsIn():
				self.tooltipInfo[i].Show()
			else:
				self.tooltipInfo[i].Hide()

	def SetCategoryPage(self, page):
		self.categoryTab[self.categoryPageIndex].SetUp()
		self.categoryPageIndex = page
		self.categoryTab[self.categoryPageIndex].Down()

		self.titleName.SetText(self.WINDOW_NAMES[self.categoryPageIndex])
		self.RefreshBagSlotWindow()

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def RefreshItemSlot(self):
		self.RefreshBagSlotWindow()

	def RefreshStatus(self):
		self.RefreshItemSlot()

	def __InventoryLocalSlotPosToGlobalSlotPos(self, localSlotPos):
		return self.inventoryPageIndex * player.SPECIAL_PAGE_SIZE + localSlotPos

	def RefreshBagSlotWindow(self):
		getItemVNum=player.GetItemIndex
		getItemCount=player.GetItemCount
		setItemVnum=self.wndItem.SetItemSlot

		for i in xrange(player.SPECIAL_PAGE_SIZE*player.SPECIAL_PAGE_COUNT):
			self.wndItem.EnableSlot(i)
			slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)

			itemCount = getItemCount(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slotNumber)
			itemVnum = getItemVNum(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slotNumber)

			if 0 == itemCount:
				self.wndItem.ClearSlot(i)
				continue
			elif 1 == itemCount:
				itemCount = 0

			setItemVnum(i, itemVnum, itemCount)

			if constInfo.ENABLE_SLOT_MARKING_EX == 1:
				if self.wndItemDelete and self.wndItemDelete.IsShow():
					self.wndItem.DisableSlotHighlightedGreen(i, 1)
					for privatePos, (itemWindowType, itemSlotIndex) in constInfo.ITEM_DELETE_LIST.items():
						if itemSlotIndex == slotNumber and (itemWindowType == self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"]):
							self.wndItem.SetCantMouseEventSlot(i)

			if app.ENABLE_HIGHLIGHT_NEW_ITEM:
				if self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"] == player.BOOK_INVENTORY:
					if slotNumber in self.listHighlightedSlotBook:
						self.wndItem.ActivateSlot(slotNumber)
				elif self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"] == player.UPGRADE_INVENTORY:
					if slotNumber in self.listHighlightedSlotUpgrade:
						self.wndItem.ActivateSlot(slotNumber)
				elif self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"] == player.STONE_INVENTORY:
					if slotNumber in self.listHighlightedSlotStone:
						self.wndItem.ActivateSlot(slotNumber)
				elif self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"] == player.CHEST_INVENTORY:
					if slotNumber in self.listHighlightedSlotChest:
						self.wndItem.ActivateSlot(slotNumber)

		self.wndItem.RefreshSlot()

		if app.ENABLE_AUTO_ITEM_SELL_SYSTEM:
			self.RefreshAutoSell()

	if app.ENABLE_AUTO_ITEM_SELL_SYSTEM:
		def RefreshAutoSell(self):
			if (len(constInfo.AutoSellItemList) < 1):
				return

			for i in xrange(player.SPECIAL_PAGE_SIZE):
				slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
				iVnum = player.GetItemIndex(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slotNumber)
				if (iVnum == 0):
					continue

				if not iVnum in constInfo.AutoSellItemList:
					continue

				self.wndItem.SetCantMouseEventSlot(i)

	def ShowToolTip(self, slotIndex):
		if None != self.tooltipItem:
			self.tooltipItem.SetInventoryItem(slotIndex, self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"])

			if app.ENABLE_IKASHOP_RENEWAL:
				board = ikashop.GetBusinessBoard()
				if board and (board.IsShow() or board.IsCreatingAuction()):
					item.SelectItem(player.GetItemIndex(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slotIndex))
					if not item.IsAntiFlag(item.ANTIFLAG_GIVE) and not item.IsAntiFlag(item.ANTIFLAG_MYSHOP):
						self.tooltipItem.AppendTextLine(localeInfo.IKASHOP_BUSINESS_SELL_ITEM_TOOLTIP)

			self.tooltipItem.AppendSpace(5)
			# self.tooltipItem.AppendTextLine(uiScriptLocale.SHIFT_CLICK_TO_USE_ITEM)

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnTop(self):
		if None != self.tooltipItem:
			self.tooltipItem.SetTop()

	def OverOutItem(self):
		self.wndItem.SetUsableItem(False)
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OverInItem(self, overSlotPos):
		overSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(overSlotPos)
		if app.ENABLE_HIGHLIGHT_NEW_ITEM:
			if self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"] == player.BOOK_INVENTORY:
				if overSlotPos in self.listHighlightedSlotBook:
					self.listHighlightedSlotBook.remove(overSlotPos)
					self.wndItem.DeactivateSlot(overSlotPos)
			elif self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"] == player.UPGRADE_INVENTORY:
				if overSlotPos in self.listHighlightedSlotUpgrade:
					self.listHighlightedSlotUpgrade.remove(overSlotPos)
					self.wndItem.DeactivateSlot(overSlotPos)
			elif self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"] == player.STONE_INVENTORY:
				if overSlotPos in self.listHighlightedSlotStone:
					self.listHighlightedSlotStone.remove(overSlotPos)
					self.wndItem.DeactivateSlot(overSlotPos)
			elif self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"] == player.CHEST_INVENTORY:
				if overSlotPos in self.listHighlightedSlotChest:
					self.listHighlightedSlotChest.remove(overSlotPos)
					self.wndItem.DeactivateSlot(overSlotPos)

		self.wndItem.SetUsableItem(False)
		self.ShowToolTip(overSlotPos)

	def OnPickItem(self, count):
		itemSlotIndex = self.dlgSplitItems.itemGlobalSlotIndex
		selectedItemVNum = player.GetItemIndex(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], itemSlotIndex)
		mouseModule.mouseController.AttachObject(self, self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["slot"], itemSlotIndex, selectedItemVNum, count)

	def SelectItemSlot(self, itemSlotIndex):
		if constInfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		itemSlotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(itemSlotIndex)
		selectedItemVNum = player.GetItemIndex(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], itemSlotIndex)
		itemCount = player.GetItemCount(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], itemSlotIndex)

		if mouseModule.mouseController.isAttached():
			attachedSlotType = mouseModule.mouseController.GetAttachedType()
			attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
			attachedItemVID = mouseModule.mouseController.GetAttachedItemIndex()
			attachedItemCount  = mouseModule.mouseController.GetAttachedItemCount()

			if self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["slot"] == attachedSlotType:
				#if attachedItemVID == selectedItemVNum:
				if item.IsKey(attachedItemVID):
					net.SendItemUseToItemPacket(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], attachedSlotPos, self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], itemSlotIndex)
				else:
					net.SendItemMovePacket(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], attachedSlotPos, self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], itemSlotIndex, 0) #This modifi: last value: attachedItemCount
				#else:
					#net.SendItemUseToItemPacket(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], attachedSlotPos, self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], itemSlotIndex)

			mouseModule.mouseController.DeattachObject()
		else:
			curCursorNum = app.GetCursor()

			if app.SELL == curCursorNum:
				self.__SellItem(itemSlotIndex)
			elif app.BUY == curCursorNum:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.SHOP_BUY_INFO)
			elif app.IsPressed(app.DIK_LALT):
				link = player.GetItemLink(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], itemSlotIndex)
				ime.PasteString(link)

			elif app.IsPressed(app.DIK_LSHIFT):
				itemCount = player.GetItemCount(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], itemSlotIndex)

				if itemCount > 1:
					self.dlgSplitItems.SetTitleName(localeInfo.PICK_ITEM_TITLE)
					self.dlgSplitItems.SetAcceptEvent(ui.__mem_func__(self.OnPickItem))
					self.dlgSplitItems.Open(itemCount)
					self.dlgSplitItems.itemGlobalSlotIndex = itemSlotIndex
			else:
				# Cynex Mobile: K Envanteri tek tikla tasima KESINLIKLE iptal!
				# Tek tikta sadece aciklama ve eylem butonlari acilir.
				wnd = self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"]
				slotType = self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["slot"]
				selectedItemVNum = player.GetItemIndex(wnd, itemSlotIndex)
				itemCount = player.GetItemCount(wnd, itemSlotIndex)
				self.heldSlotPos = -1
				self.ShowToolTip(itemSlotIndex)
				self.actionPanel.Open(self, itemSlotIndex, wnd, slotType)

	def __SellItem(self, itemSlotPos):
		self.sellingSlotNumber = itemSlotPos
		itemIndex = player.GetItemIndex(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], itemSlotPos)
		itemCount = player.GetItemCount(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], itemSlotPos)

		item.SelectItem(itemIndex)

		if item.IsAntiFlag(item.ANTIFLAG_SELL):
			popup = uiCommon.PopupDialog()
			popup.SetText(localeInfo.SHOP_CANNOT_SELL_ITEM)
			popup.SetAcceptEvent(self.__OnClosePopupDialog)
			popup.Open()
			self.popup = popup
			return

		itemPrice = item.GetISellItemPrice()

		if item.Is1GoldItem():
			itemPrice = itemCount / itemPrice / 5
		else:
			itemPrice = itemPrice * itemCount / 5

		item.GetItemName(itemIndex)
		itemName = item.GetItemName()

		self.questionDialog = uiCommon.QuestionDialog()
		self.questionDialog.SetText(localeInfo.DO_YOU_SELL_ITEM(itemName, itemCount, itemPrice))
		self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.SellItem))
		self.questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
		self.questionDialog.Open()
		self.questionDialog.count = itemCount

	def SellItem(self):
		net.SendShopSellPacket(self.sellingSlotNumber, self.questionDialog.count, self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"])
		snd.PlaySound("sound/ui/money.wav")
		self.OnCloseQuestionDialog()

	def OnCloseQuestionDialog(self):
		if self.questionDialog:
			self.questionDialog.Close()

		self.questionDialog = None

	def __OnClosePopupDialog(self):
		self.pop = None

	def SelectEmptySlot(self, selectedSlotPos):
		if constInfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		selectedSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(selectedSlotPos)
		if mouseModule.mouseController.isAttached():

			attachedSlotType = mouseModule.mouseController.GetAttachedType()
			attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
			attachedItemCount = mouseModule.mouseController.GetAttachedItemCount()
			attachedItemIndex = mouseModule.mouseController.GetAttachedItemIndex()


			attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)

			if player.SLOT_TYPE_PRIVATE_SHOP == attachedSlotType:
				mouseModule.mouseController.RunCallBack("INVENTORY")

			elif player.SLOT_TYPE_SHOP == attachedSlotType:
				net.SendShopBuyPacket(attachedSlotPos)

			elif player.SLOT_TYPE_SAFEBOX == attachedSlotType:
				net.SendSafeboxCheckoutPacket(attachedSlotPos, self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], selectedSlotPos)
			elif player.SLOT_TYPE_MALL == attachedSlotType:
				net.SendMallCheckoutPacket(attachedSlotPos, self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], selectedSlotPos)
			elif player.RESERVED_WINDOW != attachedInvenType:
				itemCount = player.GetItemCount(attachedInvenType, attachedSlotPos)
				attachedCount = mouseModule.mouseController.GetAttachedItemCount()

				if self.dlgSplitItems and self.dlgSplitItems.IsSplitAll():
					net.SendChatPacket("/split_items %d %d %d %d" % (attachedSlotPos, attachedCount, selectedSlotPos, attachedInvenType))
					self.dlgSplitItems.SplitClear()
				else:
					self.__SendMoveItemPacket(attachedInvenType, attachedSlotPos, self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], selectedSlotPos, attachedCount)
			mouseModule.mouseController.DeattachObject()

	if app.ENABLE_FAST_ATTACH_ITEMS_SYSTEM:
		def __GetCurrentItemGrid(self):
			itemGrid = [[False for slot in xrange(player.SPECIAL_PAGE_SIZE)] for page in xrange(player.SPECIAL_PAGE_COUNT)]

			for page in xrange(player.SPECIAL_PAGE_COUNT):
				for slot in xrange(player.SPECIAL_PAGE_SIZE):
					itemVnum = player.GetItemIndex(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slot + page * player.SPECIAL_PAGE_SIZE)
					if itemVnum <> 0:
						(w, h) = item.GetItemSize(item.SelectItem(itemVnum))
						for i in xrange(h):
							itemGrid[page][slot + i * 5] = True

			return itemGrid

		def __FindEmptyCellForSize(self, itemGrid, size):
			for page in xrange(player.SPECIAL_PAGE_COUNT):
				for slot in xrange(player.SPECIAL_PAGE_SIZE):
					if itemGrid[page][slot] == False:
						possible = True
						for i in xrange(size):
							p = slot + (i * 5)

							try:
								if itemGrid[page][p] == True:
									possible = False
									break
							except IndexError:
								possible = False
								break

						if possible:
							return slot + page * player.SPECIAL_PAGE_SIZE

			return -1

		def AttachItemFromSafebox(self, slotIndex, itemIndex):
			itemGrid = self.__GetCurrentItemGrid()

			emptySlotIndex = self.__FindEmptyCellForSize(itemGrid, item.GetItemSize()[1])
			if emptySlotIndex <> -1:
				net.SendSafeboxCheckoutPacket(slotIndex, self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], emptySlotIndex)

			return True

	def UseItemSlot(self, slotIndex):
		slotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(slotIndex)
		self.UseItemSlotWithoutConvert(slotIndex)

	def UseItemSlotWithoutConvert(self, slotIndex):
		if hasattr(self, "actionPanel") and self.actionPanel:
			self.actionPanel.Close()
		self.heldSlotPos = -1
		if constInfo.GET_ITEM_QUESTION_DIALOG_STATUS():
			return

		windowIndex = self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"]
		ItemVNum = player.GetItemIndex(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slotIndex)
		item.SelectItem(ItemVNum)

		if app.ENABLE_AUTO_ITEM_SELL_SYSTEM:
			if self.interface and self.interface.InventoryToAutoSellItemStatus():
				self.interface.AddUseAutoSellItem(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slotIndex)
				return

		if app.ENABLE_ITEM_DELETE_SYSTEM:
			if self.isShowDeleteItemDlg():
				self.wndItemDelete.AddItemWithoutMouse(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slotIndex)
				return

		if app.ENABLE_FAST_ATTACH_ITEMS_SYSTEM:
			if self.interface and self.interface.AttachInvenItemToOtherWindowSlot(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slotIndex):#slotIndex is the argument of __UseItem
				return

		if app.ENABLE_IKASHOP_RENEWAL:
			board = ikashop.GetBusinessBoard()
			if board:
				item.SelectItem(player.GetItemIndex(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slotIndex))
				if not item.IsAntiFlag(item.ANTIFLAG_GIVE) and not item.IsAntiFlag(item.ANTIFLAG_MYSHOP):
					# if board.IsCreatingAuction():
						# ikashop.AddItemOnAuction(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slotIndex)
						# return
					if board.IsShow():
						ikashop.AddItemOnShop(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slotIndex)
						return

		if app.IsPressed(app.DIK_LCONTROL):
			itemIndex = player.GetItemIndex(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slotIndex)
			item.SelectItem(itemIndex)
			if (item.GetItemType() == item.ITEM_TYPE_GIFTBOX) or (item.GetItemType() == item.ITEM_TYPE_USE and item.GetItemSubType() == item.USE_SPECIAL):
				net.SendInstantChestOpenPacket(self.SLOT_WINDOW_TYPE[self.categoryPageIndex]["window"], slotIndex)
				return

		elif app.ENABLE_SHOW_CHEST_DROP:
			if app.IsPressed(app.DIK_LALT):
				if windowIndex == player.CHEST_INVENTORY:
					ItemVNum = player.GetItemIndex(player.CHEST_INVENTORY, slotIndex)
					item.SelectItem(ItemVNum)

					if player.GetItemTypeBySlot(player.CHEST_INVENTORY, slotIndex) == item.ITEM_TYPE_GIFTBOX:
						if self.interface:
							if self.interface.dlgChestDrop:
								if not self.interface.dlgChestDrop.IsShow():
									self.interface.dlgChestDrop.Open(slotIndex)
									net.SendChestDropInfo(slotIndex)
									return

		mouseModule.mouseController.DeattachObject()
		self.OverOutItem()
		net.SendItemUsePacket(windowIndex, slotIndex)

	def __SendMoveItemPacket(self, srcSlotWindow, srcSlotPos, dstSlotWindow, dstSlotPos, srcItemCount):
		if uiPrivateShopBuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.MOVE_ITEM_FAILURE_PRIVATE_SHOP)
			return
		net.SendItemMovePacket(srcSlotWindow , srcSlotPos, dstSlotWindow, dstSlotPos, srcItemCount)

	if app.ENABLE_DROP_DIALOG_EXTENDED_SYSTEM:
		def DeleteItem(self, slotPos, invenType):
			itemIndex = player.GetItemIndex(invenType, slotPos)
			item.SelectItem(itemIndex)
			itemQuestionDialog2 = uiCommon.ItemQuestionDialog2()
			itemQuestionDialog2.SetText('[%s] nesnesine ne yapmak istiyorsun?' % item.GetItemName())
			itemQuestionDialog2.SetText2('(Fiyat: %s)' % localeInfo.NumberToMoneyString(item.GetISellItemPrice() * player.GetItemCount(invenType, slotPos) * 97 / 100))
			itemQuestionDialog2.SetDeleteAcceptEvent(lambda arg = 0: self.__AnswerDeleteItem(arg))
			itemQuestionDialog2.SetSellAcceptEvent(lambda arg = 1: self.__AnswerDeleteItem(arg))
			itemQuestionDialog2.SetCancelEvent(lambda arg = 2: self.__AnswerDeleteItem(arg))
			itemQuestionDialog2.Open()
			itemQuestionDialog2.slotPos = slotPos
			itemQuestionDialog2.invenType = invenType
			self.itemQuestionDialog2 = itemQuestionDialog2

		def __AnswerDeleteItem(self, answer):
			if not self.itemQuestionDialog2:
				return
			else:
				if answer == 0:
					net.SendItemDeletePacket(self.itemQuestionDialog2.slotPos, self.itemQuestionDialog2.invenType)
					snd.PlaySound('sound/ui/drop.wav')
				elif answer == 1:
					net.SendItemSellPacket(self.itemQuestionDialog2.slotPos, self.itemQuestionDialog2.invenType)
					snd.PlaySound('sound/ui/money.wav')
				self.itemQuestionDialog2.Close()
				self.itemQuestionDialog2 = None
				return

	def InventoryMode_On(self):
		systemSetting.SetStorageOpenWithInventory(True)
		self.InventoryMode[0].Down()
		self.InventoryMode[1].SetUp()

	def InventoryMode_Off(self):
		systemSetting.SetStorageOpenWithInventory(False)
		self.InventoryMode[1].Down()
		self.InventoryMode[0].SetUp()

	def InventoryMode_Refresh(self):
		if systemSetting.IsStorageOpenWithInventory() == True:
			self.InventoryMode[0].Down()
			self.InventoryMode[1].SetUp()
		else:
			self.InventoryMode[0].SetUp()
			self.InventoryMode[1].Down()

	def BindInterface(self, interface):
		self.interface = interface

	if app.ENABLE_ITEM_DELETE_SYSTEM:
		def SetDeleteItemDlg(self, wndItemDelete):
			self.wndItemDelete = wndItemDelete

		def isShowDeleteItemDlg(self):
			if self.wndItemDelete:
				if self.wndItemDelete.IsShow():
					return 1
			return 0

	def ClickSirala(self):
		if app.GetTime() > self.remaining_time:
			net.SendChatPacket("/click_sort_special_storage")
			self.remaining_time = app.GetTime() + 5
		else:
			v = self.remaining_time - app.GetTime()
			chat.AppendChat(chat.CHAT_TYPE_NOTICE, "<Sistem> 5 saniyede bir envanterini düzenleyebilirsin. Kalan: %d" % (v))
