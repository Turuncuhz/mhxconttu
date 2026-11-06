
import ui
import app
import item
import net
import chat
import constInfo
import localeInfo
import wndMgr
import grp
import snd
import os
import mouseModule
import player

SLOT_COUNT = player.AUTO_ITEM_SELL_MAX#225
SLOT_X = 15
SLOT_Y = 15

g_isAutoSellItemStatus = False

def Clear():
	global g_isAutoSellItemStatus
	g_isAutoSellItemStatus = False

def IsAutoSellStatus():
	global g_isAutoSellItemStatus

	if g_isAutoSellItemStatus:
		return True
	else:
		return False

class AutoSellDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__Initialize()
		self.__Load()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Destroy(self):
		self.ClearDictionary()
		self.__Initialize()

	def __Initialize(self):
		self.titleBar = 0
		self.interface = None
		self.tooltipItem = None
		self.itemSlot = None
		self.board = None
		self.infoBoard1 = None
		self.infoBoard2 = None
		self.itemStock = {}
		self.LastItemStock = []
		self.autoSellStatus = False

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.interface = 0
			self.wndInventory = 0
			if app.ENABLE_SPECIAL_STORAGE:
				self.wndInventorySpecial = 0

	def BindInterfaceClass(self, interface):
		self.interface = interface

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def __Load(self):
		try:
			PythonScriptLoader = ui.PythonScriptLoader()
			PythonScriptLoader.LoadScriptFile(self, "UIScript/autoselldialog.py")
		except:
			import exception
			exception.Abort("AutoSellDialog.LoadWindow.LoadObject")

		try:
			self.titleBar = self.GetChild("TitleBar")
			self.board = self.GetChild("board")

			self.infoBoard1 = self.GetChild("InfoBoard1")
			self.infoBoard2 = self.GetChild("InfoBoard2")

			self.itemSlot = self.GetChild("ItemSlot")

			self.infoText = self.GetChild("InfoB2Text1")

			self.onButton = self.GetChild("OnButton")
			self.offButton = self.GetChild("OffButton")
			self.resetButton = self.GetChild("ResetButton")

		except:
			import exception
			exception.Abort("AutoSellDialog.__LoadWindow.BindObject")

		self.titleBar.SetCloseEvent(ui.__mem_func__(self.Close))

		self.infoText.SetText("|cFF8bb391x0|r adet eþya otomatik satýlmak için eklendi.")

		self.infoBoard1.SetBaseColor(grp.GenerateColor(0.0, 0.0, 0.0, 0.40))
		self.infoBoard2.SetBaseColor(grp.GenerateColor(0.0, 0.0, 0.0, 0.40))

		#-------------------------------------------------------#
		self.onButton.SetEvent(ui.__mem_func__(self.ActiveButton))
		self.offButton.SetEvent(ui.__mem_func__(self.DisableButton))
		#----------------------------#
		self.onButton.SetUp()
		self.offButton.Down()
		self.autoSellStatus = False
		#-------------------------------------------------------#

		self.resetButton.SetEvent(ui.__mem_func__(self.ResetItems))

		## Item
		self.itemSlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.OnSelectEmptySlot))
		self.itemSlot.SetSelectItemSlotEvent(ui.__mem_func__(self.OnSelectItemSlot))
		self.itemSlot.SetUnselectItemSlotEvent(ui.__mem_func__(self.OnSelectItemSlot))
		self.itemSlot.SetUseSlotEvent(ui.__mem_func__(self.OnSelectItemSlot))
		self.itemSlot.SetOverInItemEvent(ui.__mem_func__(self.OnOverInItem))
		self.itemSlot.SetOverOutItemEvent(ui.__mem_func__(self.OnOverOutItem))

	def SetCount(self, count):
		self.infoText.SetText("|cFF8bb391x%d|r adet eþya otomatik satýlmak için eklendi." % int(count))

	def Close(self):
		Clear()

		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.TradableClearIcon()
			self.TradableRefreshIcon()

		self.Hide()

	def ActiveButton(self, firstLogin = True):
		self.onButton.Down()
		self.offButton.SetUp()
		self.autoSellStatus = True
		if firstLogin == True:
			net.SendAutoItemSell(net.SUBHEADER_CG_AUTO_SELL_ACTIVE)
			chat.AppendChat(chat.CHAT_TYPE_INFO, "|cFF8bb391[Oto Sat]|r Sistem aktif edildi.")

	def DisableButton(self, firstLogin = True):
		self.onButton.SetUp()
		self.offButton.Down()
		self.autoSellStatus = False
		if firstLogin == True:
			net.SendAutoItemSell(net.SUBHEADER_CG_AUTO_SELL_PASSIVE)
			chat.AppendChat(chat.CHAT_TYPE_INFO, "|cFF8bb391[Oto Sat]|r Sistem devre disi birakildi.")

	def ResetItems(self):
		self.itemStock = {}
		self.Refresh()
		net.SendAutoItemSell(net.SUBHEADER_CG_AUTO_SELL_RESET)
		if app.WJ_ENABLE_TRADABLE_ICON:
			self.TradableClearIcon()
			self.TradableRefreshIcon()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def OnOverInItem(self, slotIndex):
		if self.tooltipItem:
			if self.itemStock.has_key(slotIndex):
				self.tooltipItem.SetAutoSellItem(self.itemStock[slotIndex])

	def OnOverOutItem(self):
		if self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def Open(self):
		global g_isAutoSellItemStatus
		g_isAutoSellItemStatus = True
		self.itemStock = {}
		self.Refresh()
		self.SetCenterPosition()
		ui.ScriptWindow.Show(self)
		net.SendAutoItemSell(net.SUBHEADER_CG_AUTO_SELL_OPEN)

	def Clear(self):
		self.itemStock = {}
		self.LastItemStock = []

	def SetMod(self, status):
		if status:
			self.onButton.Down()
			self.offButton.SetUp()
			self.autoSellStatus = True
		else:
			self.onButton.SetUp()
			self.offButton.Down()
			self.autoSellStatus = False

		self.RefreshItemLoad()

	def AddItem(self, itemVnum):
		item.SelectItem(itemVnum)
		if (item.IsAntiFlag(item.ANTIFLAG_SELL)): return
		self.LastItemStock.append({"item_idx" : itemVnum, "item_size" : item.GetItemSize()[1]})
		def myFunc(e): return e['item_size']
		self.LastItemStock.sort(reverse=True, key=myFunc)

	def RefreshItemLoad(self):
		if app.WJ_ENABLE_TRADABLE_ICON:
			self.TradableClearIcon()

		for index in xrange(len(self.LastItemStock)):
			itemVnum = self.LastItemStock[index]['item_idx']
			itemGrid = self.__GetCurrentItemGrid()
			item.SelectItem(itemVnum)
			emptySlot = self.__FindEmptyCellForSize(itemGrid, item.GetItemSize()[1])
			self.itemStock[emptySlot] = (itemVnum)
			# self.Refresh()

			if app.WJ_ENABLE_TRADABLE_ICON:
				self.TradableAddIcon(itemVnum)

		self.SetCount(len(self.LastItemStock))
		self.LastItemStock = []
		self.Refresh()

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.TradableRefreshIcon()

	def Refresh(self):
		global SLOT_COUNT

		setitemVNum = self.itemSlot.SetItemSlot
		delItem = self.itemSlot.ClearSlot

		for i in xrange(SLOT_COUNT):
			if not self.itemStock.has_key(i):
				delItem(i)
				continue

			itemVnum = self.itemStock[i]
			if itemVnum == 0:
				continue

			setitemVNum(i, itemVnum, 0)

		self.itemSlot.RefreshSlot()

	###############################################################################
	def __GetCurrentItemGrid(self):
		global SLOT_COUNT
		global SLOT_X

		itemGrid = [[False for cell in xrange(SLOT_COUNT)] for page in xrange(1)]

		for slot in xrange(SLOT_COUNT):
			if self.itemStock.has_key(slot):
				itemVnum = self.itemStock[slot]
				if itemVnum <> 0:
					item.SelectItem(itemVnum)
					(w, h) = item.GetItemSize()

					for i in xrange(h):
						itemGrid[0][slot + i * SLOT_X] = True

		return itemGrid

	def __FindEmptyCellForSize(self, itemGrid, size):
		global SLOT_COUNT
		global SLOT_X

		for slot in xrange(SLOT_COUNT):
			if itemGrid[0][slot] == False:
				possible = True

				for i in xrange(size):
					p = slot + SLOT_X * i

					try:
						if itemGrid[0][p] == True:
							possible = False
							break
					except IndexError:
						possible = False
						break

				if possible:
					return slot

		return -1
	###############################################################################

	def OnSelectEmptySlot(self, selectedSlotPos):
		isAttached = mouseModule.mouseController.isAttached()
		if isAttached:
			attachedSlotType = mouseModule.mouseController.GetAttachedType()
			attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
			mouseModule.mouseController.DeattachObject()

			if player.SLOT_TYPE_INVENTORY != attachedSlotType and\
				player.SLOT_TYPE_DRAGON_SOUL_INVENTORY != attachedSlotType and\
				player.SLOT_TYPE_UPGRADE_INVENTORY != attachedSlotType and\
				player.SLOT_TYPE_BOOK_INVENTORY != attachedSlotType and\
				player.SLOT_TYPE_STONE_INVENTORY != attachedSlotType and\
				player.SLOT_TYPE_CHEST_INVENTORY != attachedSlotType:
				return

			attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)
			self.AddUseItem(attachedInvenType, attachedSlotPos)

	def OnSelectItemSlot(self, selectedSlotPos):
		isAttached = mouseModule.mouseController.isAttached()
		if isAttached:
			snd.PlaySound("sound/ui/loginfail.wav")
			mouseModule.mouseController.DeattachObject()
		else:
			if not selectedSlotPos in self.itemStock:
				return

			snd.PlaySound("sound/ui/drop.wav")

			self.DisableButton()
			if self.itemStock.has_key(selectedSlotPos):
				net.SendAutoItemSell(net.SUBHEADER_CG_AUTO_SELL_REMOVE, self.itemStock[selectedSlotPos])
			del self.itemStock[selectedSlotPos]
			self.RefreshGrid()

	def OnUseEmptySlot(self, slotWindow, slotIndex, emptySlot):
		if app.ENABLE_SPECIAL_STORAGE:
			if (player.INVENTORY != slotWindow and\
				player.DRAGON_SOUL_INVENTORY != slotWindow and\
				player.UPGRADE_INVENTORY != slotWindow and\
				player.BOOK_INVENTORY != slotWindow and\
				player.STONE_INVENTORY != slotWindow and\
				player.CHEST_INVENTORY != slotWindow):
				return
		else:
			if (player.INVENTORY != slotWindow and player.DRAGON_SOUL_INVENTORY != slotWindow):
				return

		itemVNum = player.GetItemIndex(slotWindow, slotIndex)
		if itemVNum == 0:
			return

		item.SelectItem(itemVNum)
		if (item.IsAntiFlag(item.ANTIFLAG_SELL)):
			return

		attrCount = 0
		attrSlot = []
		for i in xrange(player.ATTRIBUTE_SLOT_MAX_NUM):
			attrSlot.append(player.GetItemAttribute(slotWindow, slotIndex, i))
			if attrSlot:
				type = attrSlot[i][0]
				if 0 != type:
					attrCount += 1

		attrSlot = []
		if (attrCount >= 4):
			return

		itemName = item.GetItemName()
		try: itemName = itemName.split("+")[1]
		except: pass

		if (len(itemName) == 1):
			if (int(itemName) > 6):
				return

		for LastPos, (itemLastVnum) in self.itemStock.items():
			if itemLastVnum == itemVNum:
				return

		self.DisableButton()
		self.itemStock[emptySlot] = (itemVNum)
		net.SendAutoItemSell(net.SUBHEADER_CG_AUTO_SELL_ADD, itemVNum)
		self.RefreshGrid()

	def AddUseItem(self, slotWindow, slotIndex):
		if slotWindow == player.INVENTORY:
			if slotIndex >= 180 and slotIndex <= 208:
				return False

		attachedItemID = player.GetItemIndex(slotWindow, slotIndex)
		if attachedItemID == 0:
			return

		item.SelectItem(attachedItemID)
		itemGrid = self.__GetCurrentItemGrid()
		item.SelectItem(attachedItemID)
		emptySlot = self.__FindEmptyCellForSize(itemGrid, item.GetItemSize()[1])

		if emptySlot == -1 or item.GetItemType() == item.ITEM_TYPE_ELK:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "<Sistem> Yeterli alan yok.")
			return

		self.OnUseEmptySlot(slotWindow, slotIndex, emptySlot)

	def RefreshGrid(self):
		LastItemStock = []
		for LastPos, (itemVnum) in self.itemStock.items():
			item.SelectItem(itemVnum)
			LastItemStock.append({"item_idx" : itemVnum, "item_size" : item.GetItemSize()[1]})

		self.SetCount(len(LastItemStock))

		if (len(LastItemStock) < 1):
			LastItemStock = []
			self.itemStock = {}
			self.Refresh()
			if app.WJ_ENABLE_TRADABLE_ICON:
				self.TradableClearIcon()
				self.TradableRefreshIcon()
			return

		def myFunc(e):
			return e['item_size']

		LastItemStock.sort(reverse=True, key=myFunc)

		self.itemStock = {}

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.TradableClearIcon()

		for index in xrange(len(LastItemStock)):
			itemVnum = LastItemStock[index]['item_idx']
			itemGrid = self.__GetCurrentItemGrid()
			item.SelectItem(itemVnum)
			emptySlot = self.__FindEmptyCellForSize(itemGrid, item.GetItemSize()[1])
			self.itemStock[emptySlot] = (itemVnum)
			self.Refresh()

			if app.WJ_ENABLE_TRADABLE_ICON:
				self.TradableAddIcon(itemVnum)

		LastItemStock = []

		if app.WJ_ENABLE_TRADABLE_ICON:
			self.TradableRefreshIcon()

	if app.WJ_ENABLE_TRADABLE_ICON:
		def RefreshLockedSlot(self):
			pass

		def BindInterface(self, interface):
			self.interface = interface

		def SetInven(self, wndInventory):
			from _weakref import proxy
			self.wndInventory = proxy(wndInventory)

		if app.ENABLE_SPECIAL_STORAGE:
			def SetInvenSpecial(self, wndInventorySp):
				from _weakref import proxy
				self.wndInventorySpecial = proxy(wndInventorySp)

		def TradableClearIcon(self):
			constInfo.AutoSellItemList = []

		def TradableAddIcon(self, itemVnum):
			constInfo.AutoSellItemList.append((itemVnum))

		def TradableRefreshIcon(self):
			if self.wndInventory:
				self.wndInventory.RefreshBagSlotWindow()

			if app.ENABLE_SPECIAL_STORAGE:
				if self.wndInventorySpecial:
					self.wndInventorySpecial.RefreshBagSlotWindow()

