import ui
import player
import mouseModule
import net
import app
import snd
import item
import player
import chat
import grp
import uiScriptLocale
import uiRefine
import uiAttachMetin
import uiPickMoney
import uiCommon
import uiPrivateShopBuilder
import localeInfo
import constInfo
import ime
import dbg
import wndMgr
import pysettings

if app.ENABLE_ACCE_COSTUME_SYSTEM:
	import acce

if app.ENABLE_STYLE_ATTRIBUTE_SYSTEM:
	import uiAttachBonus

import uiPickItem
import uiitemactionpanel

if app.ENABLE_IKASHOP_RENEWAL:
	import ikashop

if app.EXCHANGE_CHECKIN_UPDATE:
	import exchange

ITEM_MALL_BUTTON_ENABLE = False

ITEM_FLAG_APPLICABLE = 1 << 14

if app.ENABLE_HIDE_COSTUME_PART:
	import time
	import chr
	class MouseReflector(ui.Window):
		def __init__(self, parent):
			ui.Window.__init__(self)
			self.SetParent(parent)
			self.AddFlag("not_pick")
			self.width = self.height = 0
			self.isDown = False

		def Down(self):
			self.isDown = True

		def Up(self):
			self.isDown = False

		def OnRender(self):

			if self.isDown:
				grp.SetColor(ui.WHITE_COLOR)
			else:
				grp.SetColor(ui.HALF_WHITE_COLOR)

			x, y = self.GetGlobalPosition()
			grp.RenderBar(x+2, y+2, self.GetWidth()-4, self.GetHeight()-4)

	class CheckBox(ui.ImageBox):
		def __init__(self, parent, x, y, event, status = True, filename = "d:/ymir work/ui/public/Parameter_Slot_01.sub"):
			ui.ImageBox.__init__(self)
			self.SetParent(parent)
			self.SetPosition(x, y)
			self.LoadImage(filename)

			self.mouseReflector = MouseReflector(self)
			self.mouseReflector.SetSize(self.GetWidth(), self.GetHeight())

			image = ui.MakeImageBox(self, "costume_hide/button_show_0.tga", 0, 0)
			image.AddFlag("not_pick")
			image.SetWindowHorizontalAlignCenter()
			image.SetWindowVerticalAlignCenter()
			image.Hide()
			self.Enable = True
			self.image = image
			self.event = event
			self.Show()

			self.mouseReflector.UpdateRect()
			
			if status == True:
				self.SetCheck(True)
			else:
				self.SetCheck(False)

		def __del__(self):
			ui.ImageBox.__del__(self)

		def wait_at_least(min_wait_time):
			def _inner(fn):
				last_call = [0]
				def _inner2(*args, **kwargs):
					elapsed = time.time() - last_call[0]
					if elapsed < min_wait_time:
						chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.COSTUME_HIDE_COOLDOWN_MESSAGE)
						return
					last_call[0] = time.time()
					return fn(*args, **kwargs)
				return _inner2
			return _inner

		def IsChecked(self):
			if self.image.IsShow():
				return True
			else:
				return False

		def SetCheck(self, flag):
			if flag == True:
				self.image.Hide()
			else:
				self.image.Show()

		def Disable(self):
			self.Enable = False

		def OnMouseOverIn(self):
			if not self.Enable:
				return
			self.mouseReflector.Show()

		def OnMouseOverOut(self):
			if not self.Enable:
				return
			self.mouseReflector.Hide()

		# @wait_at_least(1)
		def SendCostumeUpdate(self):
			if not self.IsChecked():
				if self.event == "hair":
					net.SendChangeCostumeVisibility(chr.HIDE_COSTUME_HAIR, False)
				elif self.event == "costume":
					net.SendChangeCostumeVisibility(chr.HIDE_COSTUME_BODY, False)
				elif self.event == "weapon":
					net.SendChangeCostumeVisibility(chr.HIDE_COSTUME_WEAPON, False)
				# elif self.event == "sash" and app.ENABLE_SHOULDER_SASH_SYSTEM:
					# net.SendChangeCostumeVisibility(chr.HIDE_COSTUME_SASH, False)
			
			elif self.IsChecked():
				if self.event == "hair":
					net.SendChangeCostumeVisibility(chr.HIDE_COSTUME_HAIR, True)
				elif self.event == "costume":
					net.SendChangeCostumeVisibility(chr.HIDE_COSTUME_BODY, True)
				elif self.event == "weapon":
					net.SendChangeCostumeVisibility(chr.HIDE_COSTUME_WEAPON, True)
				# elif self.event == "sash" and app.ENABLE_SHOULDER_SASH_SYSTEM:
					# net.SendChangeCostumeVisibility(chr.HIDE_COSTUME_SASH, True)

		def OnMouseLeftButtonDown(self):
			if not self.Enable:
				return
			self.mouseReflector.Down()

		def OnMouseLeftButtonUp(self):
			if not self.Enable:
				return
			self.mouseReflector.Up()
			self.SendCostumeUpdate()
## END

class CostumeWindow(ui.ScriptWindow):

	def __init__(self, wndInventory):
		import exception

		if not app.ENABLE_COSTUME_SYSTEM:
			exception.Abort("What do you do?")
			return

		if not wndInventory:
			exception.Abort("wndInventory parameter must be set to InventoryWindow")
			return

		ui.ScriptWindow.__init__(self)

		self.isLoaded = 0
		self.wndInventory = wndInventory;

		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self):
		self.__LoadWindow()
		self.RefreshCostumeSlot()

		ui.ScriptWindow.Show(self)

	def Close(self):
		if hasattr(self, "actionPanel") and self.actionPanel:
			self.actionPanel.Close()
		self.heldSlotPos = -1
		self.Hide()

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/CostumeWindow.py")
		except:
			import exception
			exception.Abort("CostumeWindow.LoadWindow.LoadObject")

		try:
			wndEquip = self.GetChild("CostumeSlot")
			self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))
		except:
			import exception
			exception.Abort("CostumeWindow.LoadWindow.BindObject")

		if app.ENABLE_HIDE_COSTUME_PART:
			def __CreateText(parent, name, x, y):
				text = ui.Button()
				text.SetParent(parent)
				text.SetPosition(x, y)
				text.SetText(name)
				text.UpdateRect()
				text.Show()
				return text
		
			self.hairBox = CheckBox(self, 105, 65, "hair", 0, "costume_hide/button_hide_0.tga")
		
			self.costumeBox = CheckBox(self, 105, 100, "costume", 0, "costume_hide/button_hide_0.tga")
		
			self.weaponBox = CheckBox(self, 58, 65, "weapon", 0, "costume_hide/button_hide_0.tga")

			# if app.ENABLE_SHOULDER_SASH_SYSTEM:
				# self.sashBox = CheckBox(self, 22, 153, "sash", 0, "costume_hide/button_hide_0.tga")

		## Equipment
		wndEquip.SetOverInItemEvent(ui.__mem_func__(self.wndInventory.OverInItem))
		wndEquip.SetOverOutItemEvent(ui.__mem_func__(self.wndInventory.OverOutItem))
		wndEquip.SetUnselectItemSlotEvent(ui.__mem_func__(self.wndInventory.UseItemSlot))
		wndEquip.SetUseSlotEvent(ui.__mem_func__(self.wndInventory.UseItemSlot))
		wndEquip.SetSelectEmptySlotEvent(ui.__mem_func__(self.wndInventory.SelectEmptySlot))
		wndEquip.SetSelectItemSlotEvent(ui.__mem_func__(self.wndInventory.SelectItemSlot))

		self.wndEquip = wndEquip

	if app.ENABLE_HIDE_COSTUME_PART:
		def UpdateCostumeBoxes(self):
			self.hairBox = None
			self.hairBox = CheckBox(self, 105, 65, "hair", constInfo.costumeHair, "costume_hide/button_hide_0.tga")

			self.costumeBox = None
			self.costumeBox = CheckBox(self, 105, 100, "costume", constInfo.costumeCostume, "costume_hide/button_hide_0.tga")

			self.weaponBox = None
			self.weaponBox = CheckBox(self, 58, 65, "weapon", constInfo.costumeWeapon, "costume_hide/button_hide_0.tga")

			# if app.ENABLE_SHOULDER_SASH_SYSTEM:
				# self.sashBox = None
				# self.sashBox = CheckBox(self, 22, 153, "sash", 1 if constInfo.costumeSash == 0 else 0, "costume_hide/button_hide_0.tga")

	def RefreshCostumeSlot(self):
		if app.ENABLE_HIDE_COSTUME_PART:
			self.UpdateCostumeBoxes()

		getItemVNum=player.GetItemIndex

		for i in xrange(item.COSTUME_SLOT_COUNT):
			slotNumber = item.COSTUME_SLOT_START + i
			self.wndEquip.SetItemSlot(slotNumber, getItemVNum(slotNumber), 0)

		if app.ENABLE_WEAPON_COSTUME_SYSTEM:
			self.wndEquip.SetItemSlot(item.COSTUME_SLOT_WEAPON, getItemVNum(item.COSTUME_SLOT_WEAPON), 0)

		if app.ENABLE_COSTUME_PET_SYSTEM:
			self.wndEquip.SetItemSlot(item.COSTUME_SLOT_PET, getItemVNum(item.COSTUME_SLOT_PET), 0)
			self.wndEquip.SetItemSlot(item.EQUIPMENT_RING1, getItemVNum(item.EQUIPMENT_RING1), 0)
			self.wndEquip.SetItemSlot(item.EQUIPMENT_RING2, getItemVNum(item.EQUIPMENT_RING2), 0)
			self.wndEquip.SetItemSlot(item.EQUIPMENT_RING3, getItemVNum(item.EQUIPMENT_RING3), 0)
			self.wndEquip.SetItemSlot(item.EQUIPMENT_RING4, getItemVNum(item.EQUIPMENT_RING4), 0)
			self.wndEquip.SetItemSlot(item.EQUIPMENT_RING5, getItemVNum(item.EQUIPMENT_RING5), 0)
			self.wndEquip.SetItemSlot(item.EQUIPMENT_RING6, getItemVNum(item.EQUIPMENT_RING6), 0)
			self.wndEquip.SetItemSlot(item.EQUIPMENT_BELT, getItemVNum(item.EQUIPMENT_BELT), 0)

		self.wndEquip.RefreshSlot()


class InventoryWindow(ui.ScriptWindow):

	USE_TYPE_TUPLE = ("USE_CLEAN_SOCKET", "USE_CHANGE_ATTRIBUTE", "USE_ADD_ATTRIBUTE", "USE_ADD_ATTRIBUTE2", "USE_ADD_ACCESSORY_SOCKET", "USE_PUT_INTO_ACCESSORY_SOCKET", "USE_PUT_INTO_BELT_SOCKET", "USE_PUT_INTO_RING_SOCKET")
	if app.ENABLE_USE_COSTUME_ATTR:
		USE_TYPE_TUPLE = tuple(list(USE_TYPE_TUPLE) + ["USE_CHANGE_COSTUME_ATTR", "USE_RESET_COSTUME_ATTR", "USE_ATTRIBUTE_COSTUME_WEAPON", ])
	if app.ENABLE_KOSTUM_SAC_BINEK_PET_EFSUNLAMA:
		USE_TYPE_TUPLE = tuple(list(USE_TYPE_TUPLE) + ["USE_ATTRIBUTE_MOUNT", "USE_ATTRIBUTE_PET"])

	questionDialog = None
	tooltipItem = None
	wndCostume = None
	dlgPickMoney = None
	interface = None
	wndBraveCape = None
	if app.ENABLE_ITEM_DELETE_SYSTEM:
		wndItemDelete = None

	if app.ENABLE_TRADABLE_ICON:
		bindWnds = []

	if app.EXCHANGE_CHECKIN_UPDATE:
		wndExchange = None

	sellingSlotNumber = -1
	isLoaded = 0
	isOpenedCostumeWindowWhenClosingInventory = 0
	isOpenedBeltWindowWhenClosingInventory = 0

	if app.ENABLE_HIGHLIGHT_NEW_ITEM:
		liHighlightedItems = []

	remaining_time = 0

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		self.isOpenedBeltWindowWhenClosingInventory = 0

		self.inventoryPageIndex = 0
		self.actionPanel = uiitemactionpanel.ItemActionPanel()
		self.heldSlotPos = -1
		self.heldSlotTime = 0.0
		self.isHeldAttached = False

		if app.ENABLE_ACCE_COSTUME_SYSTEM:
			self.wndAcceCombine = None
			self.wndAcceAbsorption = None
		if app.__RENEWAL_BRAVE_CAPE__:
			self.wndBraveCape = None

		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self):
		self.__LoadWindow()

		ui.ScriptWindow.Show(self)

		if self.isOpenedCostumeWindowWhenClosingInventory and self.wndCostume:
			self.wndCostume.Show()

		if app.__RENEWAL_BRAVE_CAPE__:
			if self.wndBraveCape:
				self.wndBraveCape.AdjustPosition(*self.GetGlobalPosition())

	def BindInterfaceClass(self, interface):
		self.interface = interface

	if app.ENABLE_TRADABLE_ICON:
		def BindWindow(self, wnd):
			self.bindWnds.append(wnd)

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/InventoryWindowEx.py")
		except:
			import exception
			exception.Abort("InventoryWindow.LoadWindow.LoadObject")

		try:
			wndItem = self.GetChild("ItemSlot")
			wndEquip = self.GetChild("EquipmentSlot")
			self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))
			self.wndMoney = self.GetChild("Money")
			self.wndMoneySlot = self.GetChild("Money_Slot")
			self.mallButton = self.GetChild2("MallButton")
			self.DSSButton = self.GetChild2("DSSButton")
			self.costumeButton = self.GetChild2("CostumeButton")
			self.editButton = self.GetChild2("EditButton")

			self.inventoryTab = []
			for i in xrange(player.INVENTORY_PAGE_COUNT):
				self.inventoryTab.append(self.GetChild("Inventory_Tab_%02d" % (i+1)))

			self.equipmentTab = []
			self.equipmentTab.append(self.GetChild("Equipment_Tab_01"))
			self.equipmentTab.append(self.GetChild("Equipment_Tab_02"))

			if self.costumeButton and not app.ENABLE_COSTUME_SYSTEM:
				self.costumeButton.Hide()
				self.costumeButton.Destroy()
				self.costumeButton = 0

			if app.__RENEWAL_BRAVE_CAPE__:
				self.wndBraveCape = None

		except:
			import exception
			exception.Abort("InventoryWindow.LoadWindow.BindObject")

		## Item
		wndItem.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		wndItem.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		wndItem.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		wndItem.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

		## Equipment
		wndEquip.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		wndEquip.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		wndEquip.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndEquip.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndEquip.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		wndEquip.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

		## PickMoneyDialog
		dlgPickMoney = uiPickItem.PickItemDialog()
		dlgPickMoney.LoadDialog()
		dlgPickMoney.Hide()

		## RefineDialog
		self.refineDialog = uiRefine.RefineDialog()
		self.refineDialog.Hide()

		## AttachMetinDialog
		self.attachMetinDialog = uiAttachMetin.AttachMetinDialog(self)
		self.BindWindow(self.attachMetinDialog)
		self.attachMetinDialog.Hide()

		if app.ENABLE_STYLE_ATTRIBUTE_SYSTEM:
			self.attachBonusDialog = uiAttachBonus.AttachBonusDialog(self)
			self.attachBonusDialog.Hide()

		## MoneySlot
		self.wndMoneySlot.SetEvent(ui.__mem_func__(self.OpenPickMoneyDialog))

		for i in xrange(player.INVENTORY_PAGE_COUNT):
			self.inventoryTab[i].SetEvent(lambda arg=i: self.SetInventoryPage(arg))
		self.inventoryTab[0].Down()

		self.equipmentTab[0].SetEvent(lambda arg=0: self.SetEquipmentPage(arg))
		self.equipmentTab[1].SetEvent(lambda arg=1: self.SetEquipmentPage(arg))
		self.equipmentTab[0].Down()
		self.equipmentTab[0].Hide()
		self.equipmentTab[1].Hide()

		self.wndItem = wndItem
		self.wndEquip = wndEquip
		self.dlgPickMoney = dlgPickMoney

		# MallButton
		if self.mallButton:
			self.mallButton.SetEvent(ui.__mem_func__(self.ClickMallButton))

		if self.DSSButton:
			self.DSSButton.SetEvent(ui.__mem_func__(self.ClickDSSButton))

		# Costume Button
		if self.costumeButton:
			self.costumeButton.SetEvent(ui.__mem_func__(self.ClickCostumeButton))

		if self.editButton:
			self.editButton.SetEvent(ui.__mem_func__(self.ClickEdit))

		self.wndCostume = None

		#####
		if app.ENABLE_ACCE_COSTUME_SYSTEM:
			self.listAttachedAcces = []

		if app.__RENEWAL_BRAVE_CAPE__:
			disbandBtn = ui.Button()
			disbandBtn.SetParent(self)
			disbandBtn.SetPosition(-5, 215)
			disbandBtn.SetUpVisual("d:/ymir work/ui/game/belt_inventory/btn_expand_normal.tga")
			disbandBtn.SetOverVisual("d:/ymir work/ui/game/belt_inventory/btn_expand_over.tga")
			disbandBtn.SetDownVisual("d:/ymir work/ui/game/belt_inventory/btn_expand_down.tga")
			disbandBtn.SAFE_SetEvent(self.ClickBraveCape)
			disbandBtn.Show()
			self.disbandBtn = disbandBtn

			self.wndBraveCape = BraveCapeWindow()
			self.OnMoveWindow(*self.GetGlobalPosition())

		## Refresh
		self.SetInventoryPage(0)
		self.SetEquipmentPage(0)
		self.RefreshItemSlot()
		self.RefreshStatus()

	def Destroy(self):
		self.ClearDictionary()

		self.dlgPickMoney.Destroy()
		self.dlgPickMoney = 0

		self.refineDialog.Destroy()
		self.refineDialog = 0

		self.attachMetinDialog.Destroy()
		self.attachMetinDialog = 0

		if app.ENABLE_STYLE_ATTRIBUTE_SYSTEM:
			self.attachBonusDialog.Hide()
			self.attachBonusDialog.Destroy()
			self.attachBonusDialog = 0

		if app.__RENEWAL_BRAVE_CAPE__:
			if self.wndBraveCape:
				self.wndBraveCape.Destroy()
				self.wndBraveCape = None

		self.tooltipItem = None
		self.wndItem = 0
		self.wndEquip = 0
		self.wndMoney = 0
		self.wndMoneySlot = 0
		self.questionDialog = None
		self.mallButton = None
		self.DSSButton = None
		self.interface = None

		if app.ENABLE_TRADABLE_ICON:
			self.bindWnds = []

		if app.__RENEWAL_BRAVE_CAPE__:
			self.wndBraveCape = None

		if app.EXCHANGE_CHECKIN_UPDATE:
			self.wndExchange = None

		if self.wndCostume:
			self.wndCostume.Destroy()
			self.wndCostume = 0

		if app.ENABLE_ACCE_COSTUME_SYSTEM:
			self.wndAcceCombine = None
			self.wndAcceAbsorption = None

		self.inventoryTab = []
		self.equipmentTab = []

	def Hide(self):
		if constInfo.GET_ITEM_QUESTION_DIALOG_STATUS():
			self.OnCloseQuestionDialog()
			return
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

		if self.wndCostume:
			self.isOpenedCostumeWindowWhenClosingInventory = self.wndCostume.IsShow()
			self.wndCostume.Close()

		if self.dlgPickMoney:
			self.dlgPickMoney.Close()

		if self.wndBraveCape:
			self.wndBraveCape.Close()

		wndMgr.Hide(self.hWnd)

	def Open(self):
		interface = constInfo.GetInterfaceInstance()
		if interface:
			if interface.wndInventory:
				interface.wndInventory.disbandBtn.Hide()
		if self.interface.wndInventory.wndBraveCape.IsShow():
			self.interface.wndInventory.wndBraveCape.Hide()
		self.Show()

	def Close(self):
		interface = constInfo.GetInterfaceInstance()
		if interface:
			if interface.wndInventory:
				try:
					interface.wndInventory.disbandBtn.Show()
				except:
					pass
		self.Hide()

	if app.ENABLE_TRADABLE_ICON:
		def RefreshLockedSlot(self):
			return
			# if self:
				# for exchangePos, (itemInvenPage, itemSlotPos) in self.lockedItems.items():
					# if self.GetInventoryPageIndex() == itemInvenPage:
						# self.wndItem.SetCantMouseEventSlot(itemSlotPos)

				# self.wndItem.RefreshSlot()

	def SetInventoryPage(self, page):
		self.inventoryPageIndex = page
		for i in xrange(player.INVENTORY_PAGE_COUNT):
			if i!=page:
				self.inventoryTab[i].SetUp()
		self.RefreshBagSlotWindow()
		if app.ENABLE_TRADABLE_ICON:
			map(lambda wnd:wnd.RefreshLockedSlot(), self.bindWnds)
			self.RefreshMarkSlots()

	def SetEquipmentPage(self, page):
		self.equipmentPageIndex = page
		self.equipmentTab[1-page].SetUp()
		self.RefreshEquipSlotWindow()

	if app.EXCHANGE_CHECKIN_UPDATE:
		def SetExchangeWindow(self, wndExchange):
			self.wndExchange = wndExchange

	def ClickMallButton(self):
		print "click_safebox_button"
		net.SendChatPacket("/click_safebox")

	# DSSButton
	def ClickDSSButton(self):
		print "click_dss_button"
		self.interface.ToggleDragonSoulWindow()

	if app.__RENEWAL_BRAVE_CAPE__:
		def ClickBraveCape(self):
			if self.wndBraveCape:
				if self.wndBraveCape.IsShow():
					self.wndBraveCape.Close()
				else:
					self.wndBraveCape.Open()

	def ClickCostumeButton(self):
		print "Click Costume Button"
		if self.wndCostume:
			if self.wndCostume.IsShow():
				self.wndCostume.Hide()
			else:
				self.wndCostume.Show()
		else:
			self.wndCostume = CostumeWindow(self)
			self.wndCostume.Show()

	def ClickEdit(self):
		if app.GetTime() > self.remaining_time:
			net.SendChatPacket("/click_sort_items")
			self.remaining_time = app.GetTime() + 5
		else:
			v = self.remaining_time - app.GetTime()
			chat.AppendChat(chat.CHAT_TYPE_NOTICE, "<Sistem> 5 saniyede bir envanterini duzenleyebilirsin. Kalan: %d" % (v))

	def OpenPickMoneyDialog(self):
		chat.AppendChat(chat.CHAT_TYPE_NOTICE, "Maalesef yere yang atamazsiniz.")

	def OnPickMoney(self, money):
		mouseModule.mouseController.AttachMoney(self, player.SLOT_TYPE_INVENTORY, money)

	def OnPickItem(self, count):
		itemSlotIndex = self.dlgPickMoney.itemGlobalSlotIndex
		selectedItemVNum = player.GetItemIndex(itemSlotIndex)
		mouseModule.mouseController.AttachObject(self, player.SLOT_TYPE_INVENTORY, itemSlotIndex, selectedItemVNum, count)

	def __InventoryLocalSlotPosToGlobalSlotPos(self, local):
		if player.IsEquipmentSlot(local) or player.IsCostumeSlot(local) or (app.ENABLE_NEW_EQUIPMENT_SYSTEM and player.IsBeltInventorySlot(local)):
			return local

		return self.inventoryPageIndex*player.INVENTORY_PAGE_SIZE + local

	def GetInventoryPageIndex(self):
		return self.inventoryPageIndex

	if app.ENABLE_TRADABLE_ICON:
		def RefreshMarkSlots(self, localIndex=None):
			if not self.interface:
				return

			onTopWnd = self.interface.GetOnTopWindow()
			if localIndex:
				slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(localIndex)
				if onTopWnd == player.ON_TOP_WND_NONE:
					self.wndItem.SetUsableSlotOnTopWnd(localIndex)

				elif onTopWnd == player.ON_TOP_WND_SHOP:
					if player.IsAntiFlagBySlot(slotNumber, item.ANTIFLAG_SELL):
						self.wndItem.SetUnusableSlotOnTopWnd(localIndex)
					else:
						self.wndItem.SetUsableSlotOnTopWnd(localIndex)

				elif onTopWnd == player.ON_TOP_WND_EXCHANGE:
					if player.IsAntiFlagBySlot(slotNumber, item.ANTIFLAG_GIVE):
						self.wndItem.SetUnusableSlotOnTopWnd(localIndex)
					else:
						self.wndItem.SetUsableSlotOnTopWnd(localIndex)

				elif onTopWnd == player.ON_TOP_WND_PRIVATE_SHOP:
					if player.IsAntiFlagBySlot(slotNumber, item.ITEM_ANTIFLAG_MYSHOP):
						self.wndItem.SetUnusableSlotOnTopWnd(localIndex)
					else:
						self.wndItem.SetUsableSlotOnTopWnd(localIndex)

				elif onTopWnd == player.ON_TOP_WND_SAFEBOX:
					if player.IsAntiFlagBySlot(slotNumber, item.ANTIFLAG_SAFEBOX):
						self.wndItem.SetUnusableSlotOnTopWnd(localIndex)
					else:
						self.wndItem.SetUsableSlotOnTopWnd(localIndex)

				return

			for i in xrange(player.INVENTORY_PAGE_SIZE):
				slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)

				if onTopWnd == player.ON_TOP_WND_NONE:
					self.wndItem.SetUsableSlotOnTopWnd(i)

				elif onTopWnd == player.ON_TOP_WND_SHOP:
					if player.IsAntiFlagBySlot(slotNumber, item.ANTIFLAG_SELL):
						self.wndItem.SetUnusableSlotOnTopWnd(i)
					else:
						self.wndItem.SetUsableSlotOnTopWnd(i)

				elif onTopWnd == player.ON_TOP_WND_EXCHANGE:
					if player.IsAntiFlagBySlot(slotNumber, item.ANTIFLAG_GIVE):
						self.wndItem.SetUnusableSlotOnTopWnd(i)
					else:
						self.wndItem.SetUsableSlotOnTopWnd(i)

				elif onTopWnd == player.ON_TOP_WND_PRIVATE_SHOP:
					if player.IsAntiFlagBySlot(slotNumber, item.ITEM_ANTIFLAG_MYSHOP):
						self.wndItem.SetUnusableSlotOnTopWnd(i)
					else:
						self.wndItem.SetUsableSlotOnTopWnd(i)

				elif onTopWnd == player.ON_TOP_WND_SAFEBOX:
					if player.IsAntiFlagBySlot(slotNumber, item.ANTIFLAG_SAFEBOX):
						self.wndItem.SetUnusableSlotOnTopWnd(i)
					else:
						self.wndItem.SetUsableSlotOnTopWnd(i)

	def RefreshBagSlotWindow(self):
		getItemVNum=player.GetItemIndex
		getItemCount=player.GetItemCount
		setItemVNum=self.wndItem.SetItemSlot

		for i in xrange(player.INVENTORY_PAGE_SIZE):
			slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)

			itemCount = getItemCount(slotNumber)
			if 0 == itemCount:
				self.wndItem.ClearSlot(i)
				continue
			elif 1 == itemCount:
				itemCount = 0

			itemVnum = getItemVNum(slotNumber)
			setItemVNum(i, itemVnum, itemCount)

			if constInfo.ENABLE_SLOT_MARKING_EX == 1:
				if self.wndItemDelete and self.wndItemDelete.IsShow():
					self.wndItem.DisableSlotHighlightedGreen(i, 1)
					for privatePos, (itemWindowType, itemSlotIndex) in constInfo.ITEM_DELETE_LIST.items():
						if itemSlotIndex == slotNumber and itemWindowType == player.INVENTORY:
							self.wndItem.SetCantMouseEventSlot(i)

			if constInfo.IS_AUTO_POTION(itemVnum):
				metinSocket = [player.GetItemMetinSocket(slotNumber, j) for j in xrange(player.METIN_SOCKET_MAX_NUM)]

				isActivated = 0 != metinSocket[0]

				if isActivated:
					self.wndItem.ActivateSlot(i)
					potionType = 0
					if constInfo.IS_AUTO_POTION_HP(itemVnum):
						potionType = player.AUTO_POTION_TYPE_HP
					elif constInfo.IS_AUTO_POTION_SP(itemVnum):
						potionType = player.AUTO_POTION_TYPE_SP

					usedAmount = int(metinSocket[1])
					totalAmount = int(metinSocket[2])
					player.SetAutoPotionInfo(potionType, isActivated, (totalAmount - usedAmount), totalAmount, self.__InventoryLocalSlotPosToGlobalSlotPos(i))

				else:
					self.wndItem.DeactivateSlot(i)

			if app.ENABLE_ACCE_COSTUME_SYSTEM:
				slotNumberChecked = 0
				if not constInfo.IS_AUTO_POTION(itemVnum):
					if app.ENABLE_HIGHLIGHT_NEW_ITEM:
						if not slotNumber in self.liHighlightedItems:
							self.wndItem.DeactivateSlot(i)
					else:
						self.wndItem.DeactivateSlot(i)

				for j in xrange(acce.WINDOW_MAX_MATERIALS):
					(isHere, iCell) = acce.GetAttachedItem(j)
					if isHere:
						if iCell == slotNumber:
							self.wndItem.ActivateSlot(i, (36.00 / 255.0), (222.00 / 255.0), (3.00 / 255.0), 1.0)
							if not slotNumber in self.listAttachedAcces:
								self.listAttachedAcces.append(slotNumber)

							slotNumberChecked = 1
					else:
						if slotNumber in self.listAttachedAcces and not slotNumberChecked:
							self.wndItem.DeactivateSlot(i)
							self.listAttachedAcces.remove(slotNumber)

			elif app.ENABLE_HIGHLIGHT_NEW_ITEM and not constInfo.IS_AUTO_POTION(itemVnum):
				if not slotNumber in self.liHighlightedItems:
					self.wndItem.DeactivateSlot(i)

			if app.ENABLE_PERMA_SET:
				if constInfo.IS_PERMA(itemVnum):
					metinSocket = [player.GetItemMetinSocket(slotNumber, j) for j in xrange(player.METIN_SOCKET_MAX_NUM)]

					if slotNumber >= player.INVENTORY_PAGE_SIZE * self.inventoryPageIndex:
						slotNumber -= player.INVENTORY_PAGE_SIZE * self.inventoryPageIndex

					isActivated = 0 != metinSocket[0]

					if isActivated:
						self.wndItem.ActivateSlot(i, (36.00 / 255.0), (222.00 / 255.0), (3.00 / 255.0), 1.0)
					else:
						self.wndItem.DeactivateSlot(i)
			if itemVnum >= 84100 and itemVnum <= 84105:
				metinSocket = [player.GetItemMetinSocket(slotNumber, j) for j in xrange(player.METIN_SOCKET_MAX_NUM)]
				if slotNumber >= player.INVENTORY_PAGE_SIZE * self.inventoryPageIndex:
					slotNumber -= player.INVENTORY_PAGE_SIZE * self.inventoryPageIndex
				isActivated = 0 != metinSocket[1]
				if isActivated:
					self.wndItem.ActivateSlot(i, (36.00 / 255.0), (222.00 / 255.0), (3.00 / 255.0), 1.0)
				else:
					self.wndItem.DeactivateSlot(i)

			if app.ENABLE_TRADABLE_ICON:
				self.RefreshMarkSlots(i)

		self.wndItem.RefreshSlot()

		if app.ENABLE_HIGHLIGHT_NEW_ITEM:
			self.__RefreshHighlights()

		if app.ENABLE_AUTO_ITEM_SELL_SYSTEM:
			self.RefreshAutoSell()

	if app.ENABLE_HIGHLIGHT_NEW_ITEM:
		def HighlightSlot(self, slot):
			if not slot in self.liHighlightedItems:
				self.liHighlightedItems.append(slot)

		def __RefreshHighlights(self):
			for i in xrange(player.INVENTORY_PAGE_SIZE):
				slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
				if slotNumber in self.liHighlightedItems:
					self.wndItem.ActivateSlot(i)

	if app.ENABLE_AUTO_ITEM_SELL_SYSTEM:
		def RefreshAutoSell(self):
			if (len(constInfo.AutoSellItemList) < 1):
				return

			for i in xrange(player.INVENTORY_PAGE_SIZE):
				slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
				iVnum = player.GetItemIndex(slotNumber)
				if (iVnum == 0):
					continue

				if not iVnum in constInfo.AutoSellItemList:
					continue

				self.wndItem.SetCantMouseEventSlot(i)

	def RefreshEquipSlotWindow(self):
		getItemVNum=player.GetItemIndex
		getItemCount=player.GetItemCount
		setItemVNum=self.wndEquip.SetItemSlot

		for i in xrange(player.EQUIPMENT_PAGE_COUNT):
			slotNumber = player.EQUIPMENT_SLOT_START + i
			itemCount = getItemCount(slotNumber)
			if itemCount <= 1:
				itemCount = 0
			setItemVNum(slotNumber, getItemVNum(slotNumber), itemCount)

		if app.ENABLE_NEW_EQUIPMENT_SYSTEM:
			for i in xrange(player.NEW_EQUIPMENT_SLOT_COUNT):
				slotNumber = player.NEW_EQUIPMENT_SLOT_START + i
				itemCount = getItemCount(slotNumber)
				if itemCount <= 1:
					itemCount = 0
				setItemVNum(slotNumber, getItemVNum(slotNumber), itemCount)
				print "ENABLE_NEW_EQUIPMENT_SYSTEM", slotNumber, itemCount, getItemVNum(slotNumber)
		setItemVNum(item.EQUIPMENT_BELT, getItemVNum(item.EQUIPMENT_BELT), 1)

		self.wndEquip.RefreshSlot()

		if self.wndCostume:
			self.wndCostume.RefreshCostumeSlot()

	def RefreshItemSlot(self):
		self.RefreshBagSlotWindow()
		self.RefreshEquipSlotWindow()

	def RefreshStatus(self):
		money = player.GetElk()
		self.wndMoney.SetText(localeInfo.NumberToMoneyString(money))

	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def SellItem(self):
		if self.sellingSlotitemIndex == player.GetItemIndex(self.sellingSlotNumber):
			if self.sellingSlotitemCount == player.GetItemCount(self.sellingSlotNumber):
				net.SendShopSellPacketNew(self.sellingSlotNumber, self.questionDialog.count, player.INVENTORY)
				snd.PlaySound("sound/ui/money.wav")
		self.OnCloseQuestionDialog()

	def OnDetachMetinFromItem(self):
		if None == self.questionDialog:
			return

		#net.SendItemUseToItemPacket(self.questionDialog.sourcePos, self.questionDialog.targetPos)
		self.__SendUseItemToItemPacket(self.questionDialog.sourcePos, self.questionDialog.targetPos)
		self.OnCloseQuestionDialog()

	def OnCloseQuestionDialog(self):
		if not self.questionDialog:
			return

		self.questionDialog.Close()
		self.questionDialog = None
		constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

	## Slot Event
	def SelectEmptySlot(self, selectedSlotPos):
		if constInfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		selectedSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(selectedSlotPos)

		if mouseModule.mouseController.isAttached():

			attachedSlotType = mouseModule.mouseController.GetAttachedType()
			attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
			attachedItemCount = mouseModule.mouseController.GetAttachedItemCount()
			attachedItemIndex = mouseModule.mouseController.GetAttachedItemIndex()

			if app.ENABLE_SPECIAL_STORAGE:
				attachedCount = mouseModule.mouseController.GetAttachedItemCount()

			if player.SLOT_TYPE_INVENTORY == attachedSlotType:
				#@fixme011 BEGIN (block ds equip)
				attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)
				if player.IsDSEquipmentSlot(attachedInvenType, attachedSlotPos):
					mouseModule.mouseController.DeattachObject()
					return
				#@fixme011 END

				itemCount = player.GetItemCount(attachedSlotPos)
				if not app.ENABLE_SPECIAL_STORAGE:
					attachedCount = mouseModule.mouseController.GetAttachedItemCount()
				attachedCount = mouseModule.mouseController.GetAttachedItemCount()
				if self.dlgPickMoney and self.dlgPickMoney.IsSplitAll():
					net.SendChatPacket("/split_items %d %d %d %d" % (attachedSlotPos, attachedCount, selectedSlotPos, attachedInvenType))
					self.dlgPickMoney.SplitClear()
				else:
					self.__SendMoveItemPacket(attachedSlotPos, selectedSlotPos, attachedCount)

				if item.IsRefineScroll(attachedItemIndex):
					self.wndItem.SetUseMode(False)

			elif player.SLOT_TYPE_PRIVATE_SHOP == attachedSlotType:
				mouseModule.mouseController.RunCallBack("INVENTORY")

			elif player.SLOT_TYPE_SHOP == attachedSlotType:
				net.SendShopBuyPacket(attachedSlotPos)

			elif app.ENABLE_SWITCHBOT and player.SLOT_TYPE_SWITCHBOT == attachedSlotType:
				attachedCount = mouseModule.mouseController.GetAttachedItemCount()
				net.SendItemMovePacket(player.SWITCHBOT, attachedSlotPos, player.INVENTORY, selectedSlotPos, attachedCount)

			elif player.SLOT_TYPE_SAFEBOX == attachedSlotType:

				if player.ITEM_MONEY == attachedItemIndex:
					net.SendSafeboxWithdrawMoneyPacket(mouseModule.mouseController.GetAttachedItemCount())
					snd.PlaySound("sound/ui/money.wav")

				else:
					net.SendSafeboxCheckoutPacket(attachedSlotPos, selectedSlotPos)

			elif player.SLOT_TYPE_MALL == attachedSlotType:
				net.SendMallCheckoutPacket(attachedSlotPos, selectedSlotPos)

			elif app.ENABLE_SPECIAL_STORAGE and player.SLOT_TYPE_UPGRADE_INVENTORY == attachedSlotType:
				net.SendSpecialMovePacket(player.UPGRADE_INVENTORY, attachedSlotPos, selectedSlotPos, attachedCount)

			elif app.ENABLE_SPECIAL_STORAGE and player.SLOT_TYPE_BOOK_INVENTORY == attachedSlotType:
				net.SendSpecialMovePacket(player.BOOK_INVENTORY, attachedSlotPos, selectedSlotPos, attachedCount)

			elif app.ENABLE_SPECIAL_STORAGE and player.SLOT_TYPE_STONE_INVENTORY == attachedSlotType:
				net.SendSpecialMovePacket(player.STONE_INVENTORY, attachedSlotPos, selectedSlotPos, attachedCount)

			elif app.ENABLE_SPECIAL_STORAGE and player.SLOT_TYPE_CHEST_INVENTORY == attachedSlotType:
				net.SendSpecialMovePacket(player.CHEST_INVENTORY, attachedSlotPos, selectedSlotPos, attachedCount)

			mouseModule.mouseController.DeattachObject()

	def SelectItemSlot(self, itemSlotIndex):
		if constInfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		itemSlotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(itemSlotIndex)

		if mouseModule.mouseController.isAttached():
			attachedSlotType = mouseModule.mouseController.GetAttachedType()
			attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
			attachedItemVID = mouseModule.mouseController.GetAttachedItemIndex()

			if self.IsChanger(attachedItemVID) and not player.IsEquipmentSlot(itemSlotIndex):
				itemVnum = player.GetItemIndex(itemSlotIndex)
				item.SelectItem(itemVnum)
				if item.GetItemType() == item.ITEM_TYPE_WEAPON or item.GetItemType() == item.ITEM_TYPE_ARMOR:
					self.interface.AddToBonusChange(itemSlotIndex, attachedSlotPos)
					mouseModule.mouseController.DeattachObject()
						# self.wndItem[itemSlotIndex].SetChangerImage()
					return

			if app.ENABLE_SPECIAL_STORAGE:
				if player.SLOT_TYPE_INVENTORY == attachedSlotType or player.SLOT_TYPE_STONE_INVENTORY == attachedSlotType:
					#@fixme011 BEGIN (block ds equip)
					attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)
					if player.IsDSEquipmentSlot(attachedInvenType, attachedSlotPos):
						mouseModule.mouseController.DeattachObject()
						return
					#@fixme011 END
					self.__DropSrcItemToDestItemInInventory(attachedItemVID, attachedSlotPos, itemSlotIndex)
			else:
				if player.SLOT_TYPE_INVENTORY == attachedSlotType:
					#@fixme011 BEGIN (block ds equip)
					attachedInvenType = player.SlotTypeToInvenType(attachedSlotType)
					if player.IsDSEquipmentSlot(attachedInvenType, attachedSlotPos):
						mouseModule.mouseController.DeattachObject()
						return
					#@fixme011 END
					self.__DropSrcItemToDestItemInInventory(attachedItemVID, attachedSlotPos, itemSlotIndex)

			mouseModule.mouseController.DeattachObject()

		else:

			curCursorNum = app.GetCursor()
			if app.SELL == curCursorNum:
				self.__SellItem(itemSlotIndex)

			elif app.BUY == curCursorNum:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.SHOP_BUY_INFO)

			elif app.IsPressed(app.DIK_LALT):
				link = player.GetItemLink(itemSlotIndex)
				ime.PasteString(link)


			elif app.IsPressed(app.DIK_LSHIFT):
				itemCount = player.GetItemCount(itemSlotIndex)

				if itemCount > 1:
					self.dlgPickMoney.SetTitleName(localeInfo.PICK_ITEM_TITLE)
					self.dlgPickMoney.SetAcceptEvent(ui.__mem_func__(self.OnPickItem))
					self.dlgPickMoney.Open(itemCount)
					self.dlgPickMoney.itemGlobalSlotIndex = itemSlotIndex

			elif app.IsPressed(app.DIK_LCONTROL):
				itemIndex = player.GetItemIndex(itemSlotIndex)

				if True == item.CanAddToQuickSlotItem(itemIndex):
					player.RequestAddToEmptyLocalQuickSlot(player.SLOT_TYPE_INVENTORY, itemSlotIndex)
				else:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.QUICKSLOT_REGISTER_DISABLE_ITEM)

			else:
				# Cynex Mobile: Tek tikla tasima KESINLIKLE iptal!
				# Tek tikta sadece aciklama ve yaninda eylem butonlari acilir.
				# Tasimak icin eylem panelindeki [ Tasi ] butonuna basilir.
				selectedItemVNum = player.GetItemIndex(itemSlotIndex)
				itemCount = player.GetItemCount(itemSlotIndex)
				self.heldSlotPos = -1
				self.ShowToolTip(itemSlotIndex)
				self.actionPanel.Open(self, itemSlotIndex, player.INVENTORY, player.SLOT_TYPE_INVENTORY)

	def IsChanger(self, itemVnum):
		changerList = [25055,25056,71084,71151,76023,78010,78011,78012,78055,78056] #Vnum bonus changer.
		if itemVnum in changerList:
			return True

		return False

	def __DropSrcItemToDestItemInInventory(self, srcItemVID, srcItemSlotPos, dstItemSlotPos):
		if app.ENABLE_SPECIAL_STORAGE:
			if srcItemSlotPos == dstItemSlotPos and not item.IsMetin(srcItemVID):
				return
		else:
			if srcItemSlotPos == dstItemSlotPos:
				return

		if player.GetItemIndex(srcItemSlotPos) == player.GetItemIndex(dstItemSlotPos):
			if (player.GetItemIndex(srcItemSlotPos) == srcItemVID and player.GetItemIndex(dstItemSlotPos) == srcItemVID):
				item.SelectItem(srcItemVID)
				if item.IsFlag(item.ITEM_FLAG_STACKABLE):
					self.__SendMoveItemPacket(srcItemSlotPos, dstItemSlotPos, 0)
					return

		if app.ENABLE_GIVE_TIME_COSTUME_SYSTEM or app.ENABLE_EVOLUTION_SYSTEM:
			if int(srcItemVID) == 11118 or int(srcItemVID) == 11119 or int(srcItemVID) == 11120 or int(srcItemVID) == 11121 or int(srcItemVID) == 11128 or int(srcItemVID) == 11129 or int(srcItemVID) == 11130 or int(srcItemVID) == 11131 or int(srcItemVID) == 95600 or int(srcItemVID) == 95601 or int(srcItemVID) == 95602 or int(srcItemVID) == 95603 or int(srcItemVID) == 95700 or int(srcItemVID) == 95701 or int(srcItemVID) == 95702 or int(srcItemVID) == 95703 or int(srcItemVID) == 95704 or int(srcItemVID) == 95705 or int(srcItemVID) == 95706 or int(srcItemVID) == 95707:
				self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

			if int(srcItemVID) == 81504 or int(srcItemVID) == 81505 or int(srcItemVID) == 81506:
				self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		# cyh itemseal 2013 11 08
		if app.ENABLE_SOULBIND_SYSTEM and item.IsSealScroll(srcItemVID):
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		elif item.IsRefineScroll(srcItemVID):
			if player.GetItemIndex(srcItemSlotPos) == player.GetItemIndex(dstItemSlotPos):
				self.__SendMoveItemPacket(srcItemSlotPos, dstItemSlotPos,0)
			else:
				self.RefineItem(srcItemSlotPos, dstItemSlotPos)
				self.wndItem.SetUseMode(False)

		if item.IsMetin(srcItemVID):
			self.AttachMetinToItem(srcItemSlotPos, dstItemSlotPos)

		elif item.IsDetachScroll(srcItemVID):
			self.DetachMetinFromItem(srcItemSlotPos, dstItemSlotPos)

		elif item.IsKey(srcItemVID):
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		elif (player.GetItemFlags(srcItemSlotPos) & ITEM_FLAG_APPLICABLE) == ITEM_FLAG_APPLICABLE:
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		elif item.GetUseType(srcItemVID) in self.USE_TYPE_TUPLE:
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		elif app.ENABLE_EXTRA_SOCKET_SYSTEM and item.IsUpgradeSocketScroll(srcItemVID):
			self.AttachUpgradeMetinToItem(srcItemSlotPos, dstItemSlotPos)
		elif app.ENABLE_STYLE_ATTRIBUTE_SYSTEM and player.GetItemIndex(srcItemSlotPos) == 11124:
			self.AttachBonusToItem(srcItemSlotPos, dstItemSlotPos)
		else:
			if player.IsEquipmentSlot(dstItemSlotPos):
				if item.IsEquipmentVID(srcItemVID):
					self.__UseItem(srcItemSlotPos)
			else:
				self.__SendMoveItemPacket(srcItemSlotPos, dstItemSlotPos, 0)

	def __SellItem(self, itemSlotPos):
		if not player.IsEquipmentSlot(itemSlotPos):
			self.sellingSlotNumber = itemSlotPos
			itemIndex = player.GetItemIndex(itemSlotPos)
			itemCount = player.GetItemCount(itemSlotPos)

			self.sellingSlotitemIndex = itemIndex
			self.sellingSlotitemCount = itemCount

			item.SelectItem(itemIndex)
			## 20140220
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

			constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	def __OnClosePopupDialog(self):
		self.pop = None

	def RefineItem(self, scrollSlotPos, targetSlotPos):

		scrollIndex = player.GetItemIndex(scrollSlotPos)
		targetIndex = player.GetItemIndex(targetSlotPos)

		if player.REFINE_OK != player.CanRefine(scrollIndex, targetSlotPos):
			return

		if app.ENABLE_REFINE_RENEWAL:
			constInfo.AUTO_REFINE_TYPE = 1
			constInfo.AUTO_REFINE_DATA["ITEM"][0] = scrollSlotPos
			constInfo.AUTO_REFINE_DATA["ITEM"][1] = targetSlotPos

		###########################################################
		self.__SendUseItemToItemPacket(scrollSlotPos, targetSlotPos)
		#net.SendItemUseToItemPacket(scrollSlotPos, targetSlotPos)
		return
		###########################################################

		###########################################################
		#net.SendRequestRefineInfoPacket(targetSlotPos)
		#return
		###########################################################

		result = player.CanRefine(scrollIndex, targetSlotPos)

		if player.REFINE_ALREADY_MAX_SOCKET_COUNT == result:
			#snd.PlaySound("sound/ui/jaeryun_fail.wav")
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_NO_MORE_SOCKET)

		elif player.REFINE_NEED_MORE_GOOD_SCROLL == result:
			#snd.PlaySound("sound/ui/jaeryun_fail.wav")
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_NEED_BETTER_SCROLL)

		elif player.REFINE_CANT_MAKE_SOCKET_ITEM == result:
			#snd.PlaySound("sound/ui/jaeryun_fail.wav")
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_SOCKET_DISABLE_ITEM)

		elif player.REFINE_NOT_NEXT_GRADE_ITEM == result:
			#snd.PlaySound("sound/ui/jaeryun_fail.wav")
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_UPGRADE_DISABLE_ITEM)

		elif player.REFINE_CANT_REFINE_METIN_TO_EQUIPMENT == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_EQUIP_ITEM)

		if player.REFINE_OK != result:
			return


		self.refineDialog.Open(scrollSlotPos, targetSlotPos)

	def DetachMetinFromItem(self, scrollSlotPos, targetSlotPos):
		scrollIndex = player.GetItemIndex(scrollSlotPos)
		targetIndex = player.GetItemIndex(targetSlotPos)

		if not player.CanDetach(scrollIndex, targetSlotPos):
			if app.ENABLE_ACCE_COSTUME_SYSTEM:
				item.SelectItem(scrollIndex)
				if item.GetValue(0) == acce.CLEAN_ATTR_VALUE0:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.ACCE_FAILURE_CLEAN)
				else:
					chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_METIN_INSEPARABLE_ITEM)
			else:
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_METIN_INSEPARABLE_ITEM)
			return

		self.questionDialog = uiCommon.QuestionDialog()
		self.questionDialog.SetText(localeInfo.REFINE_DO_YOU_SEPARATE_METIN)
		if app.ENABLE_ACCE_COSTUME_SYSTEM:
			item.SelectItem(targetIndex)
			if item.GetItemType() == item.ITEM_TYPE_COSTUME and item.GetItemSubType() == item.COSTUME_TYPE_ACCE:
				item.SelectItem(scrollIndex)
				if item.GetValue(0) == acce.CLEAN_ATTR_VALUE0:
					self.questionDialog.SetText(localeInfo.ACCE_DO_YOU_CLEAN)

		self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.OnDetachMetinFromItem))
		self.questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
		self.questionDialog.Open()
		self.questionDialog.sourcePos = scrollSlotPos
		self.questionDialog.targetPos = targetSlotPos

	def AttachMetinToItem(self, metinSlotPos, targetSlotPos):
		if app.ENABLE_SPECIAL_STORAGE:
			attachedSlotType = mouseModule.mouseController.GetAttachedType()
			if player.INVENTORY == attachedSlotType:
				metinIndex = player.GetItemIndex(metinSlotPos)
			else:
				metinIndex = player.GetItemIndex(player.STONE_INVENTORY, metinSlotPos)
		else:
			metinIndex = player.GetItemIndex(metinSlotPos)

		item.SelectItem(metinIndex)
		itemName = item.GetItemName()

		result = player.CanAttachMetin(metinIndex, targetSlotPos)

		if player.ATTACH_METIN_NOT_MATCHABLE_ITEM == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_CAN_NOT_ATTACH(itemName))

		if player.ATTACH_METIN_NO_MATCHABLE_SOCKET == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_NO_SOCKET(itemName))

		elif player.ATTACH_METIN_NOT_EXIST_GOLD_SOCKET == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_NO_GOLD_SOCKET(itemName))

		elif player.ATTACH_METIN_CANT_ATTACH_TO_EQUIPMENT == result:
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_EQUIP_ITEM)

		if player.ATTACH_METIN_OK != result:
			return

		self.attachMetinDialog.Open(metinSlotPos, targetSlotPos)

	def OnUpdate(self):
		if hasattr(self, "actionPanel") and self.actionPanel and self.actionPanel.IsShow():
			self.actionPanel.AdjustPosition()

		if app.ENABLE_STYLE_ATTRIBUTE_SYSTEM:
			if self.attachBonusDialog:
				if self.attachBonusDialog.IsShow():
					self.attachBonusDialog.Update()

	if app.ENABLE_STYLE_ATTRIBUTE_SYSTEM:
		def AttachBonusToItem(self, sourceSlotPos, targetSlotPos):
			targetIndex = player.GetItemIndex(targetSlotPos)
			item.SelectItem(targetIndex)

			if item.GetItemType() not in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
				return False

			self.attachBonusDialog.Open(sourceSlotPos, targetSlotPos)
			constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	def OverOutItem(self):
		self.wndItem.SetUsableItem(False)
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OverInItem(self,overSlotPos):
		overSlotPosGlobal = self.__InventoryLocalSlotPosToGlobalSlotPos(overSlotPos)
		self.wndItem.SetUsableItem(False)

		if app.ENABLE_HIGHLIGHT_NEW_ITEM and overSlotPosGlobal in self.liHighlightedItems:
			self.liHighlightedItems.remove(overSlotPosGlobal)
			self.wndItem.DeactivateSlot(overSlotPos)

		if mouseModule.mouseController.isAttached():
			attachedItemType = mouseModule.mouseController.GetAttachedType()
			if app.ENABLE_SPECIAL_STORAGE:
				if player.SLOT_TYPE_INVENTORY == attachedItemType or player.SLOT_TYPE_STONE_INVENTORY == attachedItemType:
					attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
					attachedItemVNum = mouseModule.mouseController.GetAttachedItemIndex()

					if attachedItemVNum==player.ITEM_MONEY: # @fixme005
						pass

					elif self.__CanUseSrcItemToDstItem(attachedItemVNum, attachedSlotPos, overSlotPosGlobal):
						self.wndItem.SetUsableItem(True)
						self.wndItem.SetUseMode(True)
						self.ShowToolTip(overSlotPosGlobal)
						return
			else:
				if player.SLOT_TYPE_INVENTORY == attachedItemType:
					attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
					attachedItemVNum = mouseModule.mouseController.GetAttachedItemIndex()

					if attachedItemVNum==player.ITEM_MONEY: # @fixme005
						pass

					elif self.__CanUseSrcItemToDstItem(attachedItemVNum, attachedSlotPos, overSlotPosGlobal):
						self.wndItem.SetUsableItem(True)
						self.ShowToolTip(overSlotPosGlobal)
						return

		self.ShowToolTip(overSlotPosGlobal)


	def __IsUsableItemToItem(self, srcItemVNum, srcSlotPos):
		if item.IsRefineScroll(srcItemVNum):
			return True
		elif item.IsMetin(srcItemVNum):
			return True
		elif item.IsDetachScroll(srcItemVNum):
			return True
		elif item.IsKey(srcItemVNum):
			return True
		elif (player.GetItemFlags(srcSlotPos) & ITEM_FLAG_APPLICABLE) == ITEM_FLAG_APPLICABLE:
			return True
		elif app.ENABLE_STYLE_ATTRIBUTE_SYSTEM and player.GetItemIndex(srcSlotPos) == 11124:
			return True
		elif app.ENABLE_STYLE_ATTRIBUTE_SYSTEM and player.GetItemIndex(srcSlotPos) == 71051:
			return True
		elif app.ENABLE_GIVE_TIME_COSTUME_SYSTEM and player.GetItemIndex(srcSlotPos) == 11118 or player.GetItemIndex(srcSlotPos) == 11119 or player.GetItemIndex(srcSlotPos) == 11120 or player.GetItemIndex(srcSlotPos) == 11121 or player.GetItemIndex(srcSlotPos) == 11128 or player.GetItemIndex(srcSlotPos) == 11129 or player.GetItemIndex(srcSlotPos) == 11130 or player.GetItemIndex(srcSlotPos) == 11131 or player.GetItemIndex(srcSlotPos) == 95600 or player.GetItemIndex(srcSlotPos) == 95601 or player.GetItemIndex(srcSlotPos) == 95602 or player.GetItemIndex(srcSlotPos) == 95603 or player.GetItemIndex(srcSlotPos) == 95700 or player.GetItemIndex(srcSlotPos) == 95701 or player.GetItemIndex(srcSlotPos) == 95702 or player.GetItemIndex(srcSlotPos) == 95703 or player.GetItemIndex(srcSlotPos) == 95704 or player.GetItemIndex(srcSlotPos) == 95705 or player.GetItemIndex(srcSlotPos) == 95706 or player.GetItemIndex(srcSlotPos) == 95707:
			return True
		elif app.ENABLE_EVOLUTION_SYSTEM and player.GetItemIndex(srcSlotPos) == 81504 or player.GetItemIndex(srcSlotPos) == 81505 or player.GetItemIndex(srcSlotPos) == 81506:
			return True
		else:
			if item.GetUseType(srcItemVNum) in self.USE_TYPE_TUPLE:
				return True

		return False

	def __CanUseSrcItemToDstItem(self, srcItemVNum, srcSlotPos, dstSlotPos):
		if app.ENABLE_SPECIAL_STORAGE:
			if srcSlotPos == dstSlotPos and not item.IsMetin(srcItemVNum):
				return False
		else:
			if srcSlotPos == dstSlotPos:
				return False

		if item.IsRefineScroll(srcItemVNum):
			if player.REFINE_OK == player.CanRefine(srcItemVNum, dstSlotPos):
				return True
		elif item.IsMetin(srcItemVNum):
			if player.ATTACH_METIN_OK == player.CanAttachMetin(srcItemVNum, dstSlotPos):
				return True
		elif item.IsDetachScroll(srcItemVNum):
			if player.DETACH_METIN_OK == player.CanDetach(srcItemVNum, dstSlotPos):
				return True
		elif item.IsKey(srcItemVNum):
			if player.CanUnlock(srcItemVNum, dstSlotPos):
				return True
		elif (player.GetItemFlags(srcSlotPos) & ITEM_FLAG_APPLICABLE) == ITEM_FLAG_APPLICABLE:
			return True
		elif app.ENABLE_STYLE_ATTRIBUTE_SYSTEM and player.GetItemIndex(srcSlotPos) == 11124:
			if self.__CanPutNewAttribute(dstSlotPos):
				return True
		elif app.ENABLE_EXTRA_SOCKET_SYSTEM and item.IsUpgradeSocketScroll(srcItemVNum):
			item.SelectItem(player.GetItemIndex(dstSlotPos))
			if item.GetItemType() == item.ITEM_TYPE_ARMOR or item.GetItemType() == item.ITEM_TYPE_WEAPON:
				return True
		elif app.ENABLE_GIVE_TIME_COSTUME_SYSTEM and int(srcItemVNum) == 11118 or int(srcItemVNum) == 11119 or int(srcItemVNum) == 11120 or int(srcItemVNum) == 11121 or int(srcItemVNum) == 11128 or int(srcItemVNum) == 11129 or int(srcItemVNum) == 11130 or int(srcItemVNum) == 11131 or int(srcItemVNum) == 95600 or int(srcItemVNum) == 95601 or int(srcItemVNum) == 95602 or int(srcItemVNum) == 95603 or int(srcItemVNum) == 95700 or int(srcItemVNum) == 95701 or int(srcItemVNum) == 95702 or int(srcItemVNum) == 95703 or int(srcItemVNum) == 95704 or int(srcItemVNum) == 95705 or int(srcItemVNum) == 95706 or int(srcItemVNum) == 95707:
			return True
		elif app.ENABLE_EVOLUTION_SYSTEM and int(srcItemVNum) == 81504 or int(srcItemVNum) == 81505 or int(srcItemVNum) == 81506:
			return True
		else:
			useType=item.GetUseType(srcItemVNum)

			if "USE_CLEAN_SOCKET" == useType:
				if self.__CanCleanBrokenMetinStone(dstSlotPos):
					return True
			elif "USE_CHANGE_ATTRIBUTE" == useType:
				if self.__CanChangeItemAttrList(dstSlotPos):
					return True
			elif "USE_ADD_ATTRIBUTE" == useType:
				if self.__CanAddItemAttr(dstSlotPos):
					return True
			elif "USE_ADD_ATTRIBUTE2" == useType:
				if self.__CanAddItemAttr(dstSlotPos):
					return True
			elif "USE_ADD_ACCESSORY_SOCKET" == useType:
				if self.__CanAddAccessorySocket(dstSlotPos):
					return True
			elif "USE_PUT_INTO_ACCESSORY_SOCKET" == useType:
				if self.__CanPutAccessorySocket(dstSlotPos, srcItemVNum):
					return True;
			elif "USE_PUT_INTO_BELT_SOCKET" == useType:
				dstItemVNum = player.GetItemIndex(dstSlotPos)
				print "USE_PUT_INTO_BELT_SOCKET", srcItemVNum, dstItemVNum

				item.SelectItem(dstItemVNum)

				if item.ITEM_TYPE_BELT == item.GetItemType():
					return True
			elif app.ENABLE_USE_COSTUME_ATTR and "USE_CHANGE_COSTUME_ATTR" == useType:
				if self.__CanChangeCostumeAttrList(dstSlotPos):
					return True
			elif app.ENABLE_USE_COSTUME_ATTR and "USE_RESET_COSTUME_ATTR" == useType:
				if self.__CanResetCostumeAttr(dstSlotPos):
					return True
			elif app.ENABLE_USE_COSTUME_ATTR and "USE_ATTRIBUTE_COSTUME_WEAPON" == useType:
				if self.__CanChangeCostumeAttrList(dstSlotPos):
					return True
			elif app.ENABLE_KOSTUM_SAC_BINEK_PET_EFSUNLAMA and "USE_ATTRIBUTE_MOUNT" == useType or "USE_ATTRIBUTE_PET" == useType:
				if self.__CanResetCostumeAttr(dstSlotPos):
					return True
		return False

	def __CanCleanBrokenMetinStone(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if item.ITEM_TYPE_WEAPON != item.GetItemType():
			return False

		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			if player.GetItemMetinSocket(dstSlotPos, i) == constInfo.ERROR_METIN_STONE:
				return True

		return False

	def __CanChangeItemAttrList(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
			return False

		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
				return True

		return False

	if app.ENABLE_USE_COSTUME_ATTR:
		def __CanChangeCostumeAttrList(self, dstSlotPos):
			dstItemVNum = player.GetItemIndex(dstSlotPos)
			if dstItemVNum == 0:
				return False

			item.SelectItem(dstItemVNum)

			if item.GetItemType() != item.ITEM_TYPE_COSTUME:
				return False

			for i in xrange(player.METIN_SOCKET_MAX_NUM):
				if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
					return True

			return False

		if app.ENABLE_KOSTUM_SAC_BINEK_PET_EFSUNLAMA:
			def __CanResetCostumeAttr(self, dstSlotPos):
				dstItemVNum = player.GetItemIndex(dstSlotPos)
				if dstItemVNum == 0:
					return False

				item.SelectItem(dstItemVNum)

				if item.GetItemType() not in (item.ITEM_TYPE_COSTUME, item.ITEM_TYPE_ARMOR):
					return False

				for i in xrange(player.METIN_SOCKET_MAX_NUM):
					if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
						return True

				return False
		else:
			def __CanResetCostumeAttr(self, dstSlotPos):
				dstItemVNum = player.GetItemIndex(dstSlotPos)
				if dstItemVNum == 0:
					return False

				item.SelectItem(dstItemVNum)

				if item.GetItemType() != item.ITEM_TYPE_COSTUME:
					return False

				for i in xrange(player.METIN_SOCKET_MAX_NUM):
					if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
						return True

				return False

	if app.ENABLE_STYLE_ATTRIBUTE_SYSTEM:
		def __CanPutNewAttribute(self, dstSlotPos):
			dstItemVNum = player.GetItemIndex(dstSlotPos)
			if dstItemVNum == 0:
				return False
			item.SelectItem(dstItemVNum)
			if item.GetItemType() not in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_UNIQUE):
				return False
			return True

	def __CanPutAccessorySocket(self, dstSlotPos, mtrlVnum):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if item.GetItemType() != item.ITEM_TYPE_ARMOR:
			return False

		if not item.GetItemSubType() in (item.ARMOR_WRIST, item.ARMOR_NECK, item.ARMOR_EAR):
			return False

		curCount = player.GetItemMetinSocket(dstSlotPos, 0)
		maxCount = player.GetItemMetinSocket(dstSlotPos, 1)

		if mtrlVnum != constInfo.GET_ACCESSORY_MATERIAL_VNUM(dstItemVNum, item.GetItemSubType()):
			return False

		if curCount>=maxCount:
			return False

		return True

	def __CanAddAccessorySocket(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if item.GetItemType() != item.ITEM_TYPE_ARMOR:
			return False

		if not item.GetItemSubType() in (item.ARMOR_WRIST, item.ARMOR_NECK, item.ARMOR_EAR):
			return False

		curCount = player.GetItemMetinSocket(dstSlotPos, 0)
		maxCount = player.GetItemMetinSocket(dstSlotPos, 1)
#ENABLE_EXTRA_SOCKET_SYSTEM
		ACCESSORY_SOCKET_MAX_SIZE = 4
		if maxCount >= ACCESSORY_SOCKET_MAX_SIZE:
			return False

		return True

	if app.ENABLE_EXTRA_SOCKET_SYSTEM:
		def AttachUpgradeMetinToItem(self, srcSlotPos, dstSlotPos):
			dstItemVNum = player.GetItemIndex(dstSlotPos)
			if dstItemVNum == 0:
				return False

			item.SelectItem(dstItemVNum)

			if item.ITEM_TYPE_WEAPON != item.GetItemType() and item.ITEM_TYPE_ARMOR != item.GetItemType() and item.ITEM_TYPE_BELT != item.GetItemType():
				return False

			item_name = item.GetItemName()
			self.questionDialog = uiCommon.QuestionDialog()
			self.questionDialog.SetText(localeInfo.UPGRADE_METIN_ITEM % (item_name))
			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.OnAcceptUpgradeMetinItem))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
			self.questionDialog.Open()
			self.questionDialog.sourcePos = srcSlotPos
			self.questionDialog.targetPos = dstSlotPos

		def OnAcceptUpgradeMetinItem(self):
			if self.questionDialog == None:
				return

			self.__SendUseItemToItemPacket(self.questionDialog.sourcePos, self.questionDialog.targetPos)
			self.OnCloseQuestionDialog()

	def __CanAddItemAttr(self, dstSlotPos):
		dstItemVNum = player.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):
			return False

		attrCount = 0
		for i in xrange(player.METIN_SOCKET_MAX_NUM):
			if player.GetItemAttribute(dstSlotPos, i)[0] != 0:
				attrCount += 1

		if app.ENABLE_EXTRA_SOCKET_SYSTEM:
			if attrCount<5:
				return True
		else:
			if attrCount<4:
				return True

		return False

	def OnTop(self):
		if None != self.tooltipItem:
			self.tooltipItem.SetTop()

		if app.ENABLE_TRADABLE_ICON:
			map(lambda wnd:wnd.RefreshLockedSlot(), self.bindWnds)
			self.RefreshMarkSlots()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def ShowToolTip(self, slotIndex):
		if None != self.tooltipItem:
			self.tooltipItem.SetInventoryItem(slotIndex)
			if app.ENABLE_IKASHOP_RENEWAL:
				board = ikashop.GetBusinessBoard()
				if board and (board.IsShow() or board.IsCreatingAuction()):
					item.SelectItem(player.GetItemIndex(player.INVENTORY, slotIndex))
					if not item.IsAntiFlag(item.ANTIFLAG_GIVE) and not item.IsAntiFlag(item.ANTIFLAG_MYSHOP):
						self.tooltipItem.AppendTextLine(localeInfo.IKASHOP_BUSINESS_SELL_ITEM_TOOLTIP)

			self.tooltipItem.AppendSpace(5)
			# self.tooltipItem.AppendTextLine(uiScriptLocale.SHIFT_CLICK_TO_USE_ITEM)

	def UseItemSlot(self, slotIndex):
		slotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(slotIndex)
		self.UseItemSlotWithoutConvert(slotIndex)

	def UseItemSlotWithoutConvert(self, slotIndex):
		if hasattr(self, "actionPanel") and self.actionPanel:
			self.actionPanel.Close()
		self.heldSlotPos = -1
		curCursorNum = app.GetCursor()
		if app.SELL == curCursorNum:
			return

		if constInfo.GET_ITEM_QUESTION_DIALOG_STATUS():
			return

		if app.EXCHANGE_CHECKIN_UPDATE:
			if self.wndExchange.IsShow() and slotIndex < player.EQUIPMENT_SLOT_START:
				for i in xrange(exchange.EXCHANGE_ITEM_MAX_NUM):
					itemVnum = exchange.GetItemVnumFromSelf(i)
					if itemVnum != 0:
						continue

					if not net.SendExchangeItemAddPacket(1, slotIndex, i):
						continue
					break
				return

		ItemVNum = player.GetItemIndex(player.INVENTORY, slotIndex)
		item.SelectItem(ItemVNum)

		if app.ENABLE_AUTO_ITEM_SELL_SYSTEM:
			if self.interface and self.interface.InventoryToAutoSellItemStatus():
				self.interface.AddUseAutoSellItem(player.INVENTORY, slotIndex)
				return

		if app.ENABLE_ITEM_DELETE_SYSTEM:
			if self.isShowDeleteItemDlg():
				self.wndItemDelete.AddItemWithoutMouse(player.INVENTORY, slotIndex)
				return

		if app.ENABLE_IKASHOP_RENEWAL:
			board = ikashop.GetBusinessBoard()
			if board:
				item.SelectItem(player.GetItemIndex(player.INVENTORY, slotIndex))
				if not item.IsAntiFlag(item.ANTIFLAG_GIVE) and not item.IsAntiFlag(item.ANTIFLAG_MYSHOP):
					if board.IsCreatingAuction():
						ikashop.AddItemOnAuction(player.INVENTORY, slotIndex)
						return
					elif board.IsShow():
						ikashop.AddItemOnShop(player.INVENTORY, slotIndex)
						return

		if app.ENABLE_DRAGON_SOUL_SYSTEM:
			if self.wndDragonSoulRefine.IsShow():
				self.wndDragonSoulRefine.AutoSetItem((player.INVENTORY, slotIndex), 1)
				return

		if app.ENABLE_ACCE_COSTUME_SYSTEM:
			if self.isShowAcceWindow():
				acce.Add(player.INVENTORY, slotIndex, 255)
				return

		if ItemVNum == 84001:
			self.interface.OpenRangeShop()

		if ItemVNum == 60006:
			self.interface.OpenPShopSearchDialog()

		self.__UseItem(slotIndex)
		mouseModule.mouseController.DeattachObject()

		self.OverOutItem()

	if app.ENABLE_FAST_ATTACH_ITEMS_SYSTEM:
		def __GetCurrentItemGrid(self):
			itemGrid = [[False for slot in xrange(player.INVENTORY_PAGE_SIZE)] for page in xrange(player.INVENTORY_PAGE_COUNT)]

			for page in xrange(player.INVENTORY_PAGE_COUNT):
				for slot in xrange(player.INVENTORY_PAGE_SIZE):
					itemVnum = player.GetItemIndex(slot + page * player.INVENTORY_PAGE_SIZE)
					if itemVnum <> 0:
						(w, h) = item.GetItemSize(item.SelectItem(itemVnum))
						for i in xrange(h):
							itemGrid[page][slot + i * 5] = True

			return itemGrid

		def __FindEmptyCellForSize(self, itemGrid, size):
			for page in xrange(player.INVENTORY_PAGE_COUNT):
				for slot in xrange(player.INVENTORY_PAGE_SIZE):
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
							return slot + page * player.INVENTORY_PAGE_SIZE

			return -1

		def AttachItemFromSafebox(self, slotIndex, itemIndex):
			itemGrid = self.__GetCurrentItemGrid()

			if item.GetItemType(item.SelectItem(itemIndex)) == item.ITEM_TYPE_DS:
				return

			emptySlotIndex = self.__FindEmptyCellForSize(itemGrid, item.GetItemSize()[1])
			if emptySlotIndex <> -1:
				net.SendSafeboxCheckoutPacket(slotIndex, player.INVENTORY, emptySlotIndex)

			return True
		
	def __UseItem(self, slotIndex):
		if app.ENABLE_FAST_ATTACH_ITEMS_SYSTEM:
			if self.interface and self.interface.AttachInvenItemToOtherWindowSlot(player.INVENTORY, slotIndex):#slotIndex is the argument of __UseItem
				return
		ItemVNum = player.GetItemIndex(slotIndex)
		item.SelectItem(ItemVNum)
		
		if app.IsPressed(app.DIK_LCONTROL):
			if ItemVNum == 71107 or ItemVNum == 71418 or ItemVNum == 71419 or ItemVNum == 71420 or ItemVNum == 71421 or ItemVNum == 71422 or ItemVNum == 71423 or ItemVNum == 71424 or ItemVNum == 71425 or ItemVNum == 71426 or ItemVNum == 27803 or ItemVNum == 27804 or ItemVNum == 27805 or ItemVNum == 27806 or ItemVNum == 27807 or ItemVNum == 27808 or ItemVNum == 27809 or ItemVNum == 27810 or ItemVNum == 27811 or ItemVNum == 27812 or ItemVNum == 27813 or ItemVNum == 27814 or ItemVNum == 27815 or ItemVNum == 27816 or ItemVNum == 27817 or ItemVNum == 27818 or ItemVNum == 27819 or ItemVNum == 27820 or ItemVNum == 27821 or ItemVNum == 27822 or ItemVNum == 27823 or ItemVNum == 27824:
				for i in xrange(50): #20 li daha stabil cok fazla olunca client login'e atabilir.
					self.__SendUseItemPacket(slotIndex)
		
		if item.IsFlag(item.ITEM_FLAG_CONFIRM_WHEN_USE):
			self.questionDialog = uiCommon.QuestionDialog()
			self.questionDialog.SetText(localeInfo.INVENTORY_REALLY_USE_ITEM)
			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnAccept))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnCancel))
			self.questionDialog.Open()
			self.questionDialog.slotIndex = slotIndex

			constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

		else:
			self.__SendUseItemPacket(slotIndex)
			#net.SendItemUsePacket(slotIndex)

	def __UseItemQuestionDialog_OnCancel(self):
		self.OnCloseQuestionDialog()

	def __UseItemQuestionDialog_OnAccept(self):
		self.__SendUseItemPacket(self.questionDialog.slotIndex)
		self.OnCloseQuestionDialog()

	def __SendUseItemToItemPacket(self, srcSlotPos, dstSlotPos):
		if uiPrivateShopBuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.USE_ITEM_FAILURE_PRIVATE_SHOP)
			return

		net.SendItemUseToItemPacket(srcSlotPos, dstSlotPos)

	def __SendUseItemPacket(self, slotPos):
		if uiPrivateShopBuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.USE_ITEM_FAILURE_PRIVATE_SHOP)
			return

		net.SendItemUsePacket(slotPos)

	def __SendMoveItemPacket(self, srcSlotPos, dstSlotPos, srcItemCount):
		if uiPrivateShopBuilder.IsBuildingPrivateShop():
			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.MOVE_ITEM_FAILURE_PRIVATE_SHOP)
			return

		net.SendItemMovePacket(srcSlotPos, dstSlotPos, srcItemCount)

	def SetDragonSoulRefineWindow(self, wndDragonSoulRefine):
		if app.ENABLE_DRAGON_SOUL_SYSTEM:
			self.wndDragonSoulRefine = wndDragonSoulRefine

	def OnMoveWindow(self, x, y):
		if app.__RENEWAL_BRAVE_CAPE__:
			if self.wndBraveCape:
				self.wndBraveCape.AdjustPosition(x, y)




	if app.ENABLE_ACCE_COSTUME_SYSTEM:
		def SetAcceWindow(self, wndAcceCombine, wndAcceAbsorption):
			self.wndAcceCombine = wndAcceCombine
			self.wndAcceAbsorption = wndAcceAbsorption

		def isShowAcceWindow(self):
			if self.wndAcceCombine:
				if self.wndAcceCombine.IsShow():
					return 1
			if self.wndAcceAbsorption:
				if self.wndAcceAbsorption.IsShow():
					return 1
			return 0

	if app.ENABLE_DROP_DIALOG_EXTENDED_SYSTEM:
		def DeleteItem(self, slotPos, invenType):
			itemIndex = player.GetItemIndex(invenType, slotPos)
			item.SelectItem(itemIndex)
			itemQuestionDialog2 = uiCommon.ItemQuestionDialog2()
			itemQuestionDialog2.SetText('[%s] nesnesine ne yapmak istiyorsun?' % item.GetItemName())
			itemQuestionDialog2.SetText2('(Fiyat: %s)' % localeInfo.NumberToMoneyString(item.GetISellItemPrice() * player.GetItemCount(invenType, slotPos)))
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

	if app.ENABLE_ITEM_DELETE_SYSTEM:
		def SetDeleteItemDlg(self, wndItemDelete):
			self.wndItemDelete = wndItemDelete

		def isShowDeleteItemDlg(self):
			if self.wndItemDelete:
				if self.wndItemDelete.IsShow():
					return 1
			return 0

if app.__RENEWAL_BRAVE_CAPE__:
	import os

	class BraveCapeWindow(ui.Board):
		class TouchSlider(ui.Window):
			def __init__(self, width = 110):
				ui.Window.__init__(self)
				self.curPos = 0.0
				self.eventChange = None
				self.width = width
				self.height = 18
				self.SetSize(self.width, self.height)

				self.track = ui.SlotBar()
				self.track.SetParent(self)
				self.track.SetPosition(0, 3)
				self.track.SetSize(self.width, 12)
				self.track.Show()

				self.fillBar = ui.Bar()
				self.fillBar.SetParent(self.track)
				self.fillBar.SetPosition(2, 2)
				self.fillBar.SetSize(0, 8)
				self.fillBar.SetColor(0xFF8B6B38)
				self.fillBar.Show()

				self.cursorWidth = 14
				self.pageSize = float(self.width - self.cursorWidth)
				self.cursor = ui.DragButton()
				self.cursor.AddFlag("movable")
				self.cursor.AddFlag("restrict_y")
				self.cursor.SetParent(self)
				self.cursor.SetPosition(0, 1)
				self.cursor.SetSize(self.cursorWidth, 16)
				IMG_DIR = "d:/ymir work/ui/game/bravery_cape/"
				self.cursor.SetUpVisual(IMG_DIR + "drag.tga")
				self.cursor.SetOverVisual(IMG_DIR + "drag.tga")
				self.cursor.SetDownVisual(IMG_DIR + "drag.tga")
				self.cursor.SetRestrictMovementArea(0, 1, self.width, 0)
				self.cursor.SetMoveEvent(ui.__mem_func__(self.__OnMove))
				self.cursor.Show()

			def __OnMove(self):
				(xLocal, yLocal) = self.cursor.GetLocalPosition()
				if self.pageSize > 0:
					self.curPos = max(0.0, min(1.0, float(xLocal) / self.pageSize))
				self.__UpdateFill()
				if self.eventChange:
					self.eventChange()

			def __UpdateFill(self):
				fillW = int(self.curPos * (self.width - 4))
				self.fillBar.SetSize(max(0, fillW), 8)

			def SetSliderPos(self, pos):
				self.curPos = max(0.0, min(1.0, pos))
				self.cursor.SetPosition(int(self.pageSize * self.curPos), 1)
				self.__UpdateFill()

			def GetSliderPos(self):
				return self.curPos

			def SetEvent(self, event):
				self.eventChange = event

			def OnMouseLeftButtonDown(self):
				(x, y) = self.GetMouseLocalPosition()
				pos = float(x - self.cursorWidth / 2) / self.pageSize
				self.SetSliderPos(pos)
				if self.eventChange:
					self.eventChange()
				return True

		def Destroy(self):
			self.SaveData()
			self.__children = {}

		def CreateWindow(self, classPtr, parent, pos):
			window = classPtr
			window.SetParent(parent)
			window.SetPosition(*pos)
			window.Show()
			return window

		def __OverOutItem(self):
			interface = constInfo.GetInterfaceInstance()
			if interface and interface.tooltipItem:
				interface.tooltipItem.HideToolTip()

		def __OverInItem(self, itemIdx):
			interface = constInfo.GetInterfaceInstance()
			if interface and interface.tooltipItem:
				interface.tooltipItem.SetItemToolTip(itemIdx)

		def __init__(self):
			ui.Board.__init__(self)
			self.__children = {}
			self.SetSize(230, 255)

			PUBLIC_DIR = "d:/ymir work/ui/public/"
			BRAVE_CAPE_ITEM_IDX = 20572

			# Close Button
			closeBtn = self.CreateWindow(ui.Button(), self, (self.GetWidth() - 25, 8))
			closeBtn.SetUpVisual(PUBLIC_DIR + "close_button_01.sub")
			closeBtn.SetOverVisual(PUBLIC_DIR + "close_button_02.sub")
			closeBtn.SetDownVisual(PUBLIC_DIR + "close_button_03.sub")
			closeBtn.SAFE_SetEvent(self.Close)
			self.__children["closeBtn"] = closeBtn

			# Cape Icon
			item.SelectItem(BRAVE_CAPE_ITEM_IDX)
			itemIcon = self.CreateWindow(ui.ImageBox(), self, ((self.GetWidth() - 32) // 2, 14))
			itemIcon.LoadImage(item.GetIconImageFileName())
			itemIcon.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.__OverOutItem)
			itemIcon.SAFE_SetStringEvent("MOUSE_OVER_IN", self.__OverInItem, BRAVE_CAPE_ITEM_IDX)
			self.__children["itemIcon"] = itemIcon

			# Title
			titleText = self.CreateWindow(ui.TextLine(), self, (self.GetWidth() // 2, 48))
			titleText.SetHorizontalAlignCenter()
			titleText.SetPackedFontColor(0xFFFEE3AE)
			titleText.SetText("Otomatik Pelerin")
			self.__children["titleText"] = titleText

			# --- SURE SECTION ---
			timeText = self.CreateWindow(ui.TextLine(), self, (self.GetWidth() // 2, 72))
			timeText.SetHorizontalAlignCenter()
			timeText.SetText("Süre: 1 sn")
			self.__children["timeText"] = timeText

			timeDecBtn = self.CreateWindow(ui.Button(), self, (14, 91))
			timeDecBtn.SetUpVisual(PUBLIC_DIR + "xsmall_button_01.sub")
			timeDecBtn.SetOverVisual(PUBLIC_DIR + "xsmall_button_02.sub")
			timeDecBtn.SetDownVisual(PUBLIC_DIR + "xsmall_button_03.sub")
			timeDecBtn.SetText("-")
			timeDecBtn.SAFE_SetEvent(self.OnClickDecTime)
			self.__children["timeDecBtn"] = timeDecBtn

			timeSlider = self.CreateWindow(self.TouchSlider(110), self, (58, 92))
			timeSlider.SetEvent(ui.__mem_func__(self.OnChangeTimeSlider))
			self.__children["timeSlider"] = timeSlider

			timeIncBtn = self.CreateWindow(ui.Button(), self, (176, 91))
			timeIncBtn.SetUpVisual(PUBLIC_DIR + "xsmall_button_01.sub")
			timeIncBtn.SetOverVisual(PUBLIC_DIR + "xsmall_button_02.sub")
			timeIncBtn.SetDownVisual(PUBLIC_DIR + "xsmall_button_03.sub")
			timeIncBtn.SetText("+")
			timeIncBtn.SAFE_SetEvent(self.OnClickIncTime)
			self.__children["timeIncBtn"] = timeIncBtn

			# --- MENZIL SECTION ---
			rangeText = self.CreateWindow(ui.TextLine(), self, (self.GetWidth() // 2, 122))
			rangeText.SetHorizontalAlignCenter()
			rangeText.SetText("Menzil: 100")
			self.__children["rangeText"] = rangeText

			rangeDecBtn = self.CreateWindow(ui.Button(), self, (14, 141))
			rangeDecBtn.SetUpVisual(PUBLIC_DIR + "xsmall_button_01.sub")
			rangeDecBtn.SetOverVisual(PUBLIC_DIR + "xsmall_button_02.sub")
			rangeDecBtn.SetDownVisual(PUBLIC_DIR + "xsmall_button_03.sub")
			rangeDecBtn.SetText("-")
			rangeDecBtn.SAFE_SetEvent(self.OnClickDecRange)
			self.__children["rangeDecBtn"] = rangeDecBtn

			rangeSlider = self.CreateWindow(self.TouchSlider(110), self, (58, 142))
			rangeSlider.SetEvent(ui.__mem_func__(self.OnChangeRangeSlider))
			self.__children["rangeSlider"] = rangeSlider

			rangeIncBtn = self.CreateWindow(ui.Button(), self, (176, 141))
			rangeIncBtn.SetUpVisual(PUBLIC_DIR + "xsmall_button_01.sub")
			rangeIncBtn.SetOverVisual(PUBLIC_DIR + "xsmall_button_02.sub")
			rangeIncBtn.SetDownVisual(PUBLIC_DIR + "xsmall_button_03.sub")
			rangeIncBtn.SetText("+")
			rangeIncBtn.SAFE_SetEvent(self.OnClickIncRange)
			self.__children["rangeIncBtn"] = rangeIncBtn

			# --- STATUS TEXT ---
			statusText = self.CreateWindow(ui.TextLine(), self, (self.GetWidth() // 2, 175))
			statusText.SetHorizontalAlignCenter()
			statusText.SetText("|cffffc700Durum: Deaktif|r")
			self.__children["statusText"] = statusText

			# --- ACTION BUTTONS ---
			startBtn = self.CreateWindow(ui.Button(), self, (24, 204))
			startBtn.SetUpVisual(PUBLIC_DIR + "middle_button_01.sub")
			startBtn.SetOverVisual(PUBLIC_DIR + "middle_button_02.sub")
			startBtn.SetDownVisual(PUBLIC_DIR + "middle_button_03.sub")
			startBtn.SAFE_SetEvent(self.__ClickStatusBtn, "ACTIVE")
			startBtn.SetText("Baþlat")
			self.__children["startBtn"] = startBtn

			stopBtn = self.CreateWindow(ui.Button(), self, (126, 204))
			stopBtn.SetUpVisual(PUBLIC_DIR + "middle_button_01.sub")
			stopBtn.SetOverVisual(PUBLIC_DIR + "middle_button_02.sub")
			stopBtn.SetDownVisual(PUBLIC_DIR + "middle_button_03.sub")
			stopBtn.SAFE_SetEvent(self.__ClickStatusBtn, "DEACTIVE")
			stopBtn.SetText("Durdur")
			self.__children["stopBtn"] = stopBtn

			self.__children["second"] = 0
			self.__children["range"] = 0
			self.__children["status"] = False
			self.Refresh()

		def Refresh(self):
			second = self.__children.get("second", 0)
			rangeVal = self.__children.get("range", 0)
			if second > 1400:
				second = 1400
			if rangeVal > 4000:
				rangeVal = 4000

			secDisplay = (second // 100) + 1
			self.__children["timeText"].SetText("Süre: %d sn" % secDisplay)
			self.__children["rangeText"].SetText("Menzil: %d" % (rangeVal + 100))

			self.__children["timeSlider"].SetSliderPos(float(second) / 1400.0)
			self.__children["rangeSlider"].SetSliderPos(float(rangeVal) / 4000.0)

			self.__children["second"] = second
			self.__children["range"] = rangeVal

			if self.__children.get("status", False):
				self.__children["statusText"].SetText("|cff00ff00Durum: Aktif|r")
			else:
				self.__children["statusText"].SetText("|cffffc700Durum: Deaktif|r")

		def Open(self):
			interface = constInfo.GetInterfaceInstance()
			if interface and interface.wndInventory:
				interface.wndInventory.disbandBtn.Hide()
			self.Show()

		def Close(self):
			interface = constInfo.GetInterfaceInstance()
			if interface and interface.wndInventory:
				interface.wndInventory.disbandBtn.Show()
			self.Hide()

		def __ClickStatusBtn(self, type):
			if type == "ACTIVE":
				self.__children["status"] = True
				net.SendChatPacket("/brave_cape active {} {}".format((self.__children["second"] // 100) + 2, self.__children["range"] + 1000))
			elif type == "DEACTIVE":
				self.__children["status"] = False
				net.SendChatPacket("/brave_cape deactive")
			self.Refresh()

		def AdjustPosition(self, x, y):
			self.SetPosition(x - self.GetWidth() - 5, y + 100)

		def OnClickDecTime(self):
			self.__children["second"] = max(0, self.__children.get("second", 0) - 100)
			self.Refresh()

		def OnClickIncTime(self):
			self.__children["second"] = min(1400, self.__children.get("second", 0) + 100)
			self.Refresh()

		def OnClickDecRange(self):
			self.__children["range"] = max(0, self.__children.get("range", 0) - 500)
			self.Refresh()

		def OnClickIncRange(self):
			self.__children["range"] = min(4000, self.__children.get("range", 0) + 500)
			self.Refresh()

		def OnChangeRangeSlider(self):
			val = int(self.__children["rangeSlider"].GetSliderPos() * 4000.0)
			self.__children["range"] = min(4000, max(0, val))
			self.Refresh()

		def OnChangeTimeSlider(self):
			val = int(self.__children["timeSlider"].GetSliderPos() * 14.0) * 100
			self.__children["second"] = min(1400, max(0, val))
			self.Refresh()

		def SetStatus(self, status):
			self.__children["status"] = True if int(status) == 1 else False
			self.Refresh()

		def SaveData(self):
			try:
				if not os.path.exists("lib/brave_cape"):
					os.makedirs("lib/brave_cape")
				f = open("lib/brave_cape/{}.cfg".format(player.GetName()), "w+")
				f.write("{}#{}#{}\n".format(1 if self.__children.get("status", False) else 0, self.__children.get("second", 0), self.__children.get("range", 0)))
				f.close()
			except:
				pass

		def LoadData(self):
			try:
				splitList = open("lib/brave_cape/{}.cfg".format(player.GetName()), "r").readlines()[0].split("#")
				self.__children["status"] = True if int(splitList[0]) == 1 else False
				self.__children["second"] = int(splitList[1])
				self.__children["range"] = int(splitList[2])
				self.Refresh()
				if self.__children["status"]:
					self.__ClickStatusBtn("ACTIVE")
				os.remove("lib/brave_cape/{}.cfg".format(player.GetName()))
			except:
				pass
