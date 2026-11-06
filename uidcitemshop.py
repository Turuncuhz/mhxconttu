import uiMobileCompat

import app
import item
import chat
import net
import dbg
import chr
import player
import uicommon
import localeInfo as locale

import ui, os, constInfo, localeInfo
from _weakref import proxy

itemshopData = {}
itemShopCategoryData = {}
itemShopCategoryIdx = {}
itemShopPriceType = 0

if app.ENABLE_DRAGON_COIN_EM_MARKET:
	itemshopEmData = {}
	itemShopEmCategoryData = {}
	itemShopEmCategoryIdx = {}

	openTheCache = False
	itemshopCache = {}
	itemShopCategoryCache = {}
	itemShopCategoryIdxCache = {}

	def CopyDataToCache():
		global openTheCache

		global itemshopData
		global itemShopCategoryData
		global itemShopCategoryIdx
		global itemshopCache
		global itemShopCategoryCache
		global itemShopCategoryIdxCache

		itemshopCache = {}
		itemShopCategoryCache = {}
		itemShopCategoryIdxCache = {}

		itemshopCache = itemshopData
		itemShopCategoryCache = itemShopCategoryData
		itemShopCategoryIdxCache = itemShopCategoryIdx

		openTheCache = True

	def CopyCacheToData():
		global itemshopData
		global itemShopCategoryData
		global itemShopCategoryIdx
		global itemshopCache
		global itemShopCategoryCache
		global itemShopCategoryIdxCache

		itemshopData = {}
		itemShopCategoryData = {}
		itemShopCategoryIdx = {}

		itemshopData = itemshopCache
		itemShopCategoryData = itemShopCategoryCache
		itemShopCategoryIdx = itemShopCategoryIdxCache

	def LoadToEmData():
		global itemshopData
		global itemShopCategoryData
		global itemShopCategoryIdx
		global itemshopEmData
		global itemShopEmCategoryData
		global itemShopEmCategoryIdx

		itemshopData = {}
		itemShopCategoryData = {}
		itemShopCategoryIdx = {}

		itemshopData = itemshopEmData
		itemShopCategoryData = itemShopEmCategoryData
		itemShopCategoryIdx = itemShopEmCategoryIdx

	###-----------------------------------------------###

playerLog = []
def ItemShopLogClear():
	global playerLog
	playerLog = []

def ItemShopAppendLog(dateText, dateTime, playerName, ipAdress, itemVnum, itemCount, itemPrice, itemPriceType):
	dateTimeReal = "None"
	dateSplit = dateText.split(" ")
	if len(dateSplit) > 1:
		dateFirst = dateSplit[0].split("-")
		if len(dateFirst) == 3:
			dateTimeReal = dateFirst[2]+"/"+dateFirst[1]+"/"+dateFirst[0]
			dateTimeReal+=" "
			dateSecond = dateSplit[1].split(":")
			if len(dateSecond) == 3:
				dateTimeReal += dateSecond[0]+":"+dateSecond[1]

	global playerLog
	playerLog.append([dateTimeReal, dateTime, playerName, ipAdress, itemVnum, itemCount, itemPrice, itemPriceType])

def ItemShopClear():
	global openTheCache
	global itemshopData
	global itemShopCategoryData
	global itemShopCategoryIdx
	global itemShopPriceType
	##----------------------##
	openTheCache = False
	itemshopData = {}
	itemShopCategoryData = {}
	itemShopCategoryIdx = {}
	itemShopPriceType = 0
	##----------------------##
	##----------------------##
	global itemshopCache
	global itemShopCategoryCache
	global itemShopCategoryIdxCache

	itemshopCache = {}
	itemShopCategoryCache = {}
	itemShopCategoryIdxCache = {}
	##----------------------##

def ItemShopAppendItem(SubIndex, itemID, itemVnum, itemPrice, itemDiscount, itemTimeType, itemStock, itemOffertime, itemTopSelling, itemSellType, itemAddedTime, itemSellingCount, itemSockets, itemAttrs):
	global itemshopData
	global itemShopCategoryData
	global itemShopCategoryIdx

	categoryIndex = int(itemShopCategoryIdx[int(SubIndex)]["main"])
	categorySubIndex = int(itemShopCategoryIdx[int(SubIndex)]["subIndex"])

	if not itemshopData.has_key(categoryIndex):
		subCategoryList = []
		for x in xrange(10):
			subCategoryList.append([])
		itemshopData[categoryIndex] = subCategoryList

	itemshopData[categoryIndex][categorySubIndex].append([itemID, itemVnum, itemPrice, itemDiscount, itemTimeType, itemStock, itemOffertime, itemTopSelling, itemSellType, itemAddedTime, itemSellingCount, itemSockets, itemAttrs])

def ItemShopAddCategory(categoryID, categoryName):
	global itemShopCategoryData
	if itemShopCategoryData.has_key(int(categoryID)):
		return

	itemShopCategoryData[int(categoryID)] = {"name": str(categoryName), "subCategory":[]}

def ItemShopFillCategory(mainID, categoryName, categoryID):
	global itemShopCategoryData
	if not itemShopCategoryData.has_key(int(mainID)):
		return

	subNameList = itemShopCategoryData[int(mainID)]["subCategory"]
	itemShopCategoryIdx[int(categoryID)] = {"main": int(mainID), "name": str(categoryName), "subIndex": int(len(subNameList))}
	subNameList.append((str(categoryName), int(categoryID), int(len(subNameList))))

if app.ENABLE_DRAGON_COIN_EM_MARKET:
	def ItemShopEmClear():
		global itemshopData
		global itemShopCategoryData
		global itemShopCategoryIdx
		global itemshopEmData
		global itemShopEmCategoryData
		global itemShopEmCategoryIdx
		global itemShopPriceType
		##----------------------##
		itemshopData = {}
		itemShopCategoryData = {}
		itemShopCategoryIdx = {}

		itemshopEmData = {}
		itemShopEmCategoryData = {}
		itemShopEmCategoryIdx = {}

		itemShopPriceType = 2
		##----------------------##

	def ItemShopEmAddCategory(categoryID, categoryName):
		global itemShopEmCategoryData
		if itemShopEmCategoryData.has_key(int(categoryID)):
			return

		itemShopEmCategoryData[int(categoryID)] = {"name": str(categoryName), "subCategory":[]}

	def ItemShopEmFillCategory(mainID, categoryName, categoryID):
		global itemShopEmCategoryData
		if not itemShopEmCategoryData.has_key(int(mainID)):
			return

		subNameList = itemShopEmCategoryData[int(mainID)]["subCategory"]
		itemShopEmCategoryIdx[int(categoryID)] = {"main": int(mainID), "name": str(categoryName), "subIndex": int(len(subNameList))}
		subNameList.append((str(categoryName), int(categoryID), int(len(subNameList))))

	def ItemShopEmAppendItem(SubIndex, itemID, itemVnum, itemPrice, itemDiscount, itemTimeType, itemStock, itemOffertime, itemTopSelling, itemSellType, itemAddedTime, itemSellingCount, itemSockets, itemAttrs):
		global itemshopEmData
		global itemShopEmCategoryData
		global itemShopEmCategoryIdx

		categoryIndex = int(itemShopEmCategoryIdx[int(SubIndex)]["main"])
		categorySubIndex = int(itemShopEmCategoryIdx[int(SubIndex)]["subIndex"])

		if not itemshopEmData.has_key(categoryIndex):
			subCategoryList = []
			for x in xrange(10):
				subCategoryList.append([])
			itemshopEmData[categoryIndex] = subCategoryList

		itemshopEmData[categoryIndex][categorySubIndex].append([itemID, itemVnum, itemPrice, itemDiscount, itemTimeType, itemStock, itemOffertime, itemTopSelling, itemSellType, itemAddedTime, itemSellingCount, itemSockets, itemAttrs])


buyQuestionDialog = None

LIST_ITEM_ID=0
LIST_ITEM_VNUM=1
LIST_ITEM_PRICE=2
LIST_ITEM_DISCOUNT=3
LIST_ITEM_TIME_TYPE=4
LIST_ITEM_STOCK=5
LIST_ITEM_OFFER_TIME=6
LIST_ITEM_TOP_SELLING_INDEX=7
LIST_ITEM_SELL_TYPE=8
LIST_ITEM_ADDED_TIME=9
LIST_ITEM_SELLING_COUNT=10
LIST_ITEM_SOCKET=11
LIST_ITEM_ATTR=12

def ItemShopUpdateItem(itemID, itemStock):
	global itemshopData
	for key, items in itemshopData.items():
		for subCategory in items:
			for shopItem in subCategory:
				if shopItem[LIST_ITEM_ID] == itemID:
					shopItem = [shopItem[LIST_ITEM_ID], shopItem[LIST_ITEM_VNUM], shopItem[LIST_ITEM_PRICE], shopItem[LIST_ITEM_DISCOUNT], shopItem[LIST_ITEM_TIME_TYPE], itemStock]
					return

LOG_DATE_TEXT = 0
LOG_DATE = 1
LOG_ACCOUNT = 2
LOG_IP = 3
LOG_ITEM = 4
LOG_COUNT = 5
LOG_PRICE = 6
LOG_PRICE_TYPE = 7

HOT_ITEM=1
NEW_ITEM=2
OFFER_ITEM=3

#Config
eventCategory = [
	[["img.png","img.png"],[1,4]],
]

# ADMIN_DIR ="d:/ymir work/ui/game/ishop/admin/"

IMG_DIR ="d:/ymir work/ui/game/ishop/"

class ItemShopWindow(ui.Window):
	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		ItemShopLogClear()

		if self.children.has_key("categoryListBox"):
			self.children["categoryListBox"].RemoveAllItems()

		if self.children.has_key("subCategoryListBox"):
			self.children["subCategoryListBox"].RemoveAllItems()

		if self.children.has_key("itemListBox"):
			self.children["itemListBox"].RemoveAllItems()

		if self.children.has_key("PurchasesListBox"):
			self.children["PurchasesListBox"].RemoveAllItems()

		self.CloseWeb()

		global buyQuestionDialog
		if buyQuestionDialog != None:
			buyQuestionDialog.Hide()
			buyQuestionDialog.Destroy()
			buyQuestionDialog = None

		self.MoneySellType = 0

		self.RealMoneyCash = 0
		self.RealMoneyCoins = 0
		self.RealMoneyEm = 0

		self.NewMoneyCash = 0
		self.NewMoneyCoins = 0
		self.NewMoneyEm = 0

		self.MoneyRangeCash = 0
		self.MoneyRangeCoins = 0
		self.MoneyRangeEm = 0

		self.MoneyFlagCash = False
		self.MoneyFlagCoins = False
		self.MoneyFlagEm = False

		self.moneySizeCash = 0
		self.moneySizeCoins = 0
		self.moneySizeEm = 0

		self.children = {}

		self.popupDialog = None

	def OpenPopupDialog(self, message, data = 0, seconds = 6):
		message = getattr(locale, message, message)
		if self.popupDialog == None:
			self.popupDialog = uicommon.PopupDialog()
		if (data != 0):
			self.popupDialog.SetText(message % data)
		else:
			self.popupDialog.SetText(message)
		self.popupDialog.SetWidth(self.popupDialog.message.GetTextSize()[0] + 40)
		self.popupDialog.Open()
		self.popupDialog.SetAutoClose(seconds)

	def __init__(self):
		ui.Window.__init__(self)

		self.children = {}
		self.Destroy()
		self.LoadWindow()

	def LoadWindow(self):
		self.AddFlag("movable")
		self.AddFlag("float")
		#self.SetCenterPosition()

		boardImage = ui.ImageBox()
		boardImage.SetParent(self)
		boardImage.LoadImage(IMG_DIR+"bg.png")
		self.SetSize(boardImage.GetWidth(),boardImage.GetHeight())
		boardImage.SetPosition(0, 0)
		boardImage.Show()
		self.children["boardImage"] = boardImage

		closeBtn = ui.Button()
		closeBtn.SetParent(boardImage)
		closeBtn.SetUpVisual(IMG_DIR+"close_0.png")
		closeBtn.SetOverVisual(IMG_DIR+"close_1.png")
		closeBtn.SetDownVisual(IMG_DIR+"close_2.png")
		closeBtn.SetEvent(self.Close)
		closeBtn.SetPosition(boardImage.GetWidth()-closeBtn.GetWidth()-5, 5)
		closeBtn.Show()
		self.children["closeBtn"] = closeBtn

		# adminBgBtn = ui.Button()
		# adminBgBtn.SetParent(boardImage)
		# adminBgBtn.SetUpVisual(ADMIN_DIR+"admin_0.png")
		# adminBgBtn.SetOverVisual(ADMIN_DIR+"admin_1.png")
		# adminBgBtn.SetDownVisual(ADMIN_DIR+"admin_2.png")
		# adminBgBtn.SetEvent(self.AdminBgOpenBtn)
		# adminBgBtn.SetPosition(boardImage.GetWidth()-adminBgBtn.GetWidth()-1, 5)
		# adminBgBtn.Hide()
		# if chr.IsGameMaster(player.GetMainCharacterIndex()):
			# adminBgBtn.Show()
		# self.children["adminBgBtn"] = adminBgBtn

		leftDragonCoinImage = ui.ImageBox()
		leftDragonCoinImage.SetParent(boardImage)
		# leftDragonCoinImage.LoadImage(IMG_DIR+"coin.png")
		leftDragonCoinImage.LoadImage(IMG_DIR+"logo.png")
		leftDragonCoinImage.SetPosition(2, 3)
		leftDragonCoinImage.Show()
		self.children["leftDragonCoinImage"] = leftDragonCoinImage

		CASH_BUTTON_DIR = "d:/ymir work/ui/game/ishop/"
		dragonCashBtn = ui.RadioButton()
		dragonCashBtn.SetParent(boardImage)
		dragonCashBtn.SetUpVisual(CASH_BUTTON_DIR+"circle_bos.png")
		dragonCashBtn.SetOverVisual(CASH_BUTTON_DIR+"circle_bos.png")
		dragonCashBtn.SetDownVisual(CASH_BUTTON_DIR+"circle_dolu.png")
		dragonCashBtn.SetEvent(self.SetSellTypeBtn, 0)
		dragonCashBtn.SetPosition(leftDragonCoinImage.GetRight()+2, 7+(24*0))
		dragonCashBtn.Show()
		self.children["dragonCashBtn"] = dragonCashBtn

		dragonCoinBtn = ui.RadioButton()
		dragonCoinBtn.SetParent(boardImage)
		dragonCoinBtn.SetUpVisual(CASH_BUTTON_DIR+"circle_bos.png")
		dragonCoinBtn.SetOverVisual(CASH_BUTTON_DIR+"circle_bos.png")
		dragonCoinBtn.SetDownVisual(CASH_BUTTON_DIR+"circle_dolu.png")
		dragonCoinBtn.SetEvent(self.SetSellTypeBtn, 1)
		dragonCoinBtn.SetPosition(leftDragonCoinImage.GetRight()+2, 7+(24*1))
		dragonCoinBtn.Show()
		self.children["dragonCoinBtn"] = dragonCoinBtn

		dragonEmBtn = ui.RadioButton()
		dragonEmBtn.SetParent(boardImage)
		dragonEmBtn.SetUpVisual(CASH_BUTTON_DIR+"circle_bos.png")
		dragonEmBtn.SetOverVisual(CASH_BUTTON_DIR+"circle_bos.png")
		dragonEmBtn.SetDownVisual(CASH_BUTTON_DIR+"circle_dolu.png")
		dragonEmBtn.SetEvent(self.SetSellTypeBtn, 2)
		dragonEmBtn.SetPosition(leftDragonCoinImage.GetRight()+2, 7+(24*2))
		dragonEmBtn.Show()
		self.children["dragonEmBtn"] = dragonEmBtn

		global itemShopPriceType
		if (self.MoneySellType == 0):
			itemShopPriceType = 0
			self.children["dragonCashBtn"].Down()
			self.children["dragonCoinBtn"].SetUp()
			self.children["dragonEmBtn"].SetUp()
		elif (self.MoneySellType == 1):
			itemShopPriceType = 1
			self.children["dragonCashBtn"].SetUp()
			self.children["dragonCoinBtn"].Down()
			self.children["dragonEmBtn"].SetUp()
		elif (self.MoneySellType == 2):
			itemShopPriceType = 2
			self.children["dragonCashBtn"].SetUp()
			self.children["dragonCoinBtn"].SetUp()
			self.children["dragonEmBtn"].Down()

		dragonCoinText = MultiTextLine()
		dragonCoinText.SetParent(boardImage)
		dragonCoinText.SetPosition(dragonCoinBtn.GetRight()+3, 7+(24*0))
		dragonCoinText.SetTextRange(17)
		dragonCoinText.SetTextType("horizontal#left")
		dragonCoinText.SetFontName("Arial:15")
		dragonCoinText.SetOutline(True)
		dragonCoinText.SetText("None")
		dragonCoinText.Show()
		self.children["dragonCoinText"] = dragonCoinText
		self.SetDragonCoinReal(0)

		dragonCashText = MultiTextLine()
		dragonCashText.SetParent(boardImage)
		dragonCashText.SetPosition(dragonCashBtn.GetRight()+3, 7+(24*1))
		dragonCashText.SetTextRange(17)
		dragonCashText.SetTextType("horizontal#left")
		dragonCashText.SetFontName("Arial:15")
		dragonCashText.SetOutline(True)
		dragonCashText.SetText("None")
		dragonCashText.Show()
		self.children["dragonCashText"] = dragonCashText
		self.SetDragonCashReal(0)

		dragonEmText = MultiTextLine()
		dragonEmText.SetParent(boardImage)
		dragonEmText.SetPosition(dragonEmBtn.GetRight()+3, 7+(24*2))
		dragonEmText.SetTextRange(17)
		dragonEmText.SetTextType("horizontal#left")
		dragonEmText.SetFontName("Arial:15")
		dragonEmText.SetOutline(True)
		dragonEmText.SetText("None")
		dragonEmText.Show()
		self.children["dragonEmText"] = dragonEmText
		self.SetDragonEmReal(0)

		MAIN_X = 170+25
		MAIN_Y = 11

		MAIN_A_X = 5
		MAIN_A_Y = 12

		ADD_X = 0
		ADD_Y = 17

		mainPageBtn = ui.Button()
		mainPageBtn.SetParent(boardImage)
		mainPageBtn.SetUpVisual(IMG_DIR+"home_normal.png")
		mainPageBtn.SetOverVisual(IMG_DIR+"home_hover.png")
		mainPageBtn.SetDownVisual(IMG_DIR+"home_down.png")
		mainPageBtn.SetEvent(self.MainPage)
		mainPageBtn.SetPosition(MAIN_X, MAIN_Y+MAIN_A_Y)
		mainPageBtn.Show()
		self.children["mainPageBtn"] = mainPageBtn

		MainPageItemsBtnText = MultiTextLine()
		MainPageItemsBtnText.SetParent(mainPageBtn)
		MainPageItemsBtnText.SetTextRange(17)
		MainPageItemsBtnText.SetPosition(mainPageBtn.GetWidth()/2, 3)
		MainPageItemsBtnText.SetTextType("horizontal#center")
		MainPageItemsBtnText.SetFontName("Arial:16")
		# MainPageItemsBtnText.SetText(localeInfo.ITEMSHOP_MAIN_PAGE)
		MainPageItemsBtnText.Show()
		mainPageBtn.multiText = MainPageItemsBtnText

		buyCoinBtn = ui.Button()
		buyCoinBtn.SetParent(boardImage)
		buyCoinBtn.SetUpVisual(IMG_DIR+"coin_n.png")
		buyCoinBtn.SetOverVisual(IMG_DIR+"coin_h.png")
		buyCoinBtn.SetDownVisual(IMG_DIR+"coin_d.png")
		buyCoinBtn.SetEvent(self.BuyDragonCoin)
		buyCoinBtn.SetPosition(mainPageBtn.GetRight()+MAIN_A_X, MAIN_Y+MAIN_A_Y)
		buyCoinBtn.Show()
		self.children["buyCoinBtn"] = buyCoinBtn

		buyCoinBtnText = MultiTextLine()
		buyCoinBtnText.SetParent(buyCoinBtn)
		buyCoinBtnText.SetTextRange(17)
		buyCoinBtnText.SetPosition(buyCoinBtn.GetWidth()/2+12, 1)
		buyCoinBtnText.SetTextType("horizontal#center")
		buyCoinBtnText.SetFontName("Arial:16")
		buyCoinBtnText.SetText(localeInfo.ITEMSHOP_BUY_COIN1+"\n"+localeInfo.ITEMSHOP_BUY_COIN2)
		buyCoinBtnText.Show()
		buyCoinBtn.multiText = buyCoinBtnText

		purchasesBtn = ui.Button()
		purchasesBtn.SetParent(boardImage)
		purchasesBtn.SetUpVisual(IMG_DIR+"purchases_n.png")
		purchasesBtn.SetOverVisual(IMG_DIR+"purchases_h.png")
		purchasesBtn.SetDownVisual(IMG_DIR+"purchases_d.png")
		purchasesBtn.SetEvent(self.PurchaseBtn)
		purchasesBtn.SetPosition(buyCoinBtn.GetRight()+MAIN_A_X, MAIN_Y+MAIN_A_Y)
		purchasesBtn.Show()
		self.children["purchasesBtn"] = purchasesBtn

		purchasesBtnText = MultiTextLine()
		purchasesBtnText.SetParent(purchasesBtn)
		purchasesBtnText.SetTextRange(17)
		purchasesBtnText.SetPosition(purchasesBtn.GetWidth()/2+12, 1)
		purchasesBtnText.SetTextType("horizontal#center")
		purchasesBtnText.SetFontName("Arial:16")
		purchasesBtnText.SetText(localeInfo.ITEMSHOP_PURCHASES1+"\n"+localeInfo.ITEMSHOP_PURCHASES2)
		purchasesBtnText.Show()
		purchasesBtn.multiText = purchasesBtnText

		hotItemsBtn = ui.Button()
		hotItemsBtn.SetParent(boardImage)
		hotItemsBtn.SetUpVisual(IMG_DIR+"hot_n.png")
		hotItemsBtn.SetOverVisual(IMG_DIR+"hot_h.png")
		hotItemsBtn.SetDownVisual(IMG_DIR+"hot_d.png")
		hotItemsBtn.SetEvent(self.HotItems)
		hotItemsBtn.SetPosition(purchasesBtn.GetRight()+MAIN_A_X, MAIN_Y+MAIN_A_Y)
		hotItemsBtn.Show()
		self.children["hotItemsBtn"] = hotItemsBtn

		hotItemsBtnText = MultiTextLine()
		hotItemsBtnText.SetParent(hotItemsBtn)
		hotItemsBtnText.SetTextRange(17)
		hotItemsBtnText.SetPosition(hotItemsBtn.GetWidth()/2+12, 9)
		hotItemsBtnText.SetTextType("horizontal#center")
		hotItemsBtnText.SetFontName("Arial:16")
		hotItemsBtnText.SetText(localeInfo.ITEMSHOP_HOTITEMS)
		hotItemsBtnText.Show()
		hotItemsBtn.multiText = hotItemsBtnText

		offersBtn = ui.Button()
		offersBtn.SetParent(boardImage)
		offersBtn.SetUpVisual(IMG_DIR+"offer_n.png")
		offersBtn.SetOverVisual(IMG_DIR+"offer_h.png")
		offersBtn.SetDownVisual(IMG_DIR+"offer_d.png")
		offersBtn.SetEvent(self.OfferItems)
		offersBtn.SetPosition(hotItemsBtn.GetRight()+MAIN_A_X, MAIN_Y+MAIN_A_Y)
		offersBtn.Show()
		self.children["offersBtn"] = offersBtn

		offersBtnText = MultiTextLine()
		offersBtnText.SetParent(offersBtn)
		offersBtnText.SetTextRange(17)
		offersBtnText.SetPosition(offersBtn.GetWidth()/2+12, 9)
		offersBtnText.SetTextType("horizontal#center")
		offersBtnText.SetFontName("Arial:16")
		offersBtnText.SetText(localeInfo.ITEMSHOP_OFFERS)
		offersBtnText.Show()
		offersBtn.multiText = offersBtnText

		wheelBtn = ui.Button()
		wheelBtn.SetParent(boardImage)
		wheelBtn.SetUpVisual(IMG_DIR+"wheel_n.png")
		wheelBtn.SetOverVisual(IMG_DIR+"wheel_h.png")
		wheelBtn.SetDownVisual(IMG_DIR+"wheel_d.png")
		wheelBtn.SetEvent(self.WheelPage)
		wheelBtn.SetPosition(offersBtn.GetRight()+MAIN_A_X, MAIN_Y+MAIN_A_Y)
		wheelBtn.Show()
		self.children["wheelBtn"] = wheelBtn

		wheelBtnText = MultiTextLine()
		wheelBtnText.SetParent(wheelBtn)
		wheelBtnText.SetTextRange(17)
		wheelBtnText.SetPosition(wheelBtn.GetWidth()/2, 3)
		wheelBtnText.SetTextType("horizontal#center")
		wheelBtnText.SetFontName("Rail Regular:14")
		# wheelBtnText.SetText(localeInfo.ITEMSHOP_MAIN_PAGE)
		wheelBtnText.Show()
		wheelBtn.multiText = wheelBtnText

		itemSearchBg = ui.ImageBox()
		itemSearchBg.SetParent(boardImage)
		itemSearchBg.LoadImage(IMG_DIR+"search_box.png")
		itemSearchBg.SetPosition(813, 30+MAIN_A_Y)
		itemSearchBg.Show()
		self.children["itemSearchBg"] = itemSearchBg

		itemSearch = ui.EditLine()
		itemSearch.SetParent(itemSearchBg)
		itemSearch.SetMax(40)
		itemSearch.SetPosition(16, 9)
		itemSearch.SetSize(itemSearchBg.GetWidth()-16, itemSearchBg.GetHeight()-10)
		itemSearch.OnIMEUpdate = ui.__mem_func__(self.__OnValueUpdate)
		itemSearch.OnPressEscapeKey = ui.__mem_func__(self.Close)
		itemSearch.SetFontColor(0, 0, 0)
		itemSearch.Show()
		self.children["itemSearch"] = itemSearch

		itemSearchText = MultiTextLine()
		itemSearchText.SetParent(itemSearch)
		itemSearchText.SetTextRange(15)
		itemSearchText.SetPosition(1, -2)
		itemSearchText.SetTextType("horizontal#left")
		itemSearchText.SetFontName("Rail Regular:16")
		itemSearchText.SetText("|cFF949494%s|r" % localeInfo.ITEMSHOP_ITEMSEARCH_DEFAULT_TEXT)
		itemSearchText.SetFontColor(0, 0, 0)
		itemSearchText.Show()
		itemSearch.backText = itemSearchText

		categoryScrollBar = ScrollBar()
		categoryScrollBar.SetParent(boardImage)
		categoryScrollBar.SetPosition(169+5, 72+ADD_Y)
		categoryScrollBar.SetScrollBarSize(435)
		categoryScrollBar.SetScrollStep(0.07)
		categoryScrollBar.Show()
		self.children["categoryScrollBar"] = categoryScrollBar

		categoryListBox = ListBox()
		categoryListBox.SetParent(boardImage)
		categoryListBox.SetPosition(10, 73+ADD_Y)
		categoryListBox.SetSize(150,54*8)
		categoryListBox.SetItemStep(6)
		categoryListBox.SetItemSize(150,55)
		categoryListBox.SetScrollBar(categoryScrollBar)
		categoryListBox.Show()
		self.children["categoryListBox"] = categoryListBox
		self.children["subCategoryListBox"] = categoryListBox

		itemScrollBar = ScrollBar()
		itemScrollBar.SetParent(boardImage)
		itemScrollBar.SetPosition(200+750+15, 72+ADD_Y)
		itemScrollBar.SetScrollBarSize(435)
		itemScrollBar.SetScrollStep(0.07)
		itemScrollBar.Show()
		self.children["itemScrollBar"] = itemScrollBar

		itemListBox = ListBox()
		itemListBox.SetParent(boardImage)
		itemListBox.SetPosition(200, 73+ADD_Y)
		itemListBox.SetSize(750,445)
		itemListBox.SetItemStep(8)
		itemListBox.SetItemSize(750,122)
		itemListBox.SetScrollBar(itemScrollBar)
		#itemListBox.OnUpdate = self.OnUpdate()
		itemListBox.Show()
		self.children["itemListBox"] = itemListBox

		PurchasesScrollBar = ScrollBar()
		PurchasesScrollBar.SetParent(boardImage)
		PurchasesScrollBar.SetPosition(200+750+10, 76+ADD_Y)
		PurchasesScrollBar.SetScrollBarSize(435)
		PurchasesScrollBar.SetScrollStep(0.07)
		PurchasesScrollBar.Show()
		self.children["PurchasesScrollBar"] = PurchasesScrollBar

		PurchasesListBox = ListBox()
		PurchasesListBox.SetParent(boardImage)
		PurchasesListBox.SetPosition(16, 75+ADD_Y)
		PurchasesListBox.SetSize(927,440)
		PurchasesListBox.SetItemStep(8)
		PurchasesListBox.SetItemSize(927,28)
		PurchasesListBox.SetScrollBar(PurchasesScrollBar)
		PurchasesListBox.Show()
		self.children["PurchasesListBox"] = PurchasesListBox

		LoadingImage = ui.ExpandedImageBox()
		LoadingImage.SetParent(boardImage)
		LoadingImage.SetPosition(boardImage.GetWidth()/2, boardImage.GetHeight()/2)
		LoadingImage.LoadImage(IMG_DIR+"load_.png")
		self.children["LoadingImage"] = LoadingImage
		self.children["LoadingImageRotation"] = 0
		self.children["sendPacketDataLog"] = 0

		self.OfferItems()
		self.HotItems()

	def OnUpdate(self):
		if self.children.has_key("itemListBox"):
			listboxData = self.children["itemListBox"].GetItems()
			for itemPointer in listboxData:
				itemPointer.OnUpdate()

		if self.children.has_key("LoadingImage"):
			LoadingImage = self.children["LoadingImage"]
			if LoadingImage.IsShow():
				self.children["LoadingImageRotation"] += 15
				LoadingImage.SetRotation(self.children["LoadingImageRotation"])

		if self.MoneyFlagCash == True:
			if self.moneySizeCash >= 0 and self.moneySizeCash <= 15:
				if self.NewMoneyCash > self.RealMoneyCash:
					self.RealMoneyCash += ((self.MoneyRangeCash)/15)
					self.SetDragonCashReal(self.RealMoneyCash)
				else:
					self.RealMoneyCash -= ((self.MoneyRangeCash)/15)
					self.SetDragonCashReal(self.RealMoneyCash)

				self.moneySizeCash += 1

				if self.moneySizeCash == 15:
					self.RealMoneyCash = self.NewMoneyCash
					self.SetDragonCashReal(self.RealMoneyCash)
					self.MoneyFlagCash = False

		if self.MoneyFlagCoins == True:
			if self.moneySizeCoins >= 0 and self.moneySizeCoins <= 15:
				if self.NewMoneyCoins > self.RealMoneyCoins:
					self.RealMoneyCoins += ((self.MoneyRangeCoins)/15)
					self.SetDragonCoinReal(self.RealMoneyCoins)
				else:
					self.RealMoneyCoins -= ((self.MoneyRangeCoins)/15)
					self.SetDragonCoinReal(self.RealMoneyCoins)

				self.moneySizeCoins += 1

				if self.moneySizeCoins == 15:
					self.RealMoneyCoins = self.NewMoneyCoins
					self.SetDragonCoinReal(self.RealMoneyCoins)
					self.MoneyFlagCoins = False

		if self.MoneyFlagEm == True:
			if self.moneySizeEm >= 0 and self.moneySizeEm <= 15:
				if self.NewMoneyEm > self.RealMoneyEm:
					self.RealMoneyEm += ((self.MoneyRangeEm)/15)
					self.SetDragonEmReal(self.RealMoneyEm)
				else:
					self.RealMoneyEm -= ((self.MoneyRangeEm)/15)
					self.SetDragonEmReal(self.RealMoneyEm)

				self.moneySizeEm += 1

				if self.moneySizeEm == 15:
					self.RealMoneyEm = self.NewMoneyEm
					self.SetDragonEmReal(self.RealMoneyEm)
					self.MoneyFlagEm = False

	def __OnValueUpdate(self):
		global itemShopPriceType

		itemSearch = self.children["itemSearch"]
		ui.EditLine.OnIMEUpdate(itemSearch)

		self.ClearItemList()
		searchItemList = []

		def normalize(string):
			"""Verilen kelimenin tm harflerini kk harf yapar"""
			return (
				string.replace("", "a")
				.replace("", "a")
				.replace("", "i")
				.replace("", "i")
				.replace("I", "")
				.replace("", "i")
				.replace("", "")
				.replace("", "")
				.replace("", "")
				.replace("", "")
				.replace("", "")
				.lower()
			)

		# searchText = itemSearch.GetText().lower()
		searchText = normalize(itemSearch.GetText())

		if len(searchText) > 0:
			for key, data in itemshopData.items():
				for itemList in data:
					for itemData in itemList:
						if (itemShopPriceType != 0 and itemData[LIST_ITEM_SELL_TYPE] == net.DC_ISHOP_SELL_TYPE_COINS):
							continue
						elif (itemShopPriceType != 1 and itemData[LIST_ITEM_SELL_TYPE] == net.DC_ISHOP_SELL_TYPE_CASH):
							continue
						elif (itemShopPriceType != 2 and itemData[LIST_ITEM_SELL_TYPE] == net.DC_ISHOP_SELL_TYPE_EM):
							continue

						item.SelectItem(itemData[LIST_ITEM_VNUM])
						# if item.GetItemName().lower().find(searchText) != -1:
						if normalize(item.GetItemName()).find(searchText) != -1:
							searchItemList.append(itemData)

			self.RefreshItemList(searchItemList)
		else:
			self.LoadFirstOpening()

	def LoadShopCategory(self):
		self.categoryIndex = -1
		self.categorySubIndex = -1
		categoryListBox = self.children["categoryListBox"]

		for key, data in itemShopCategoryData.items():
			categoryItem = CategoryItem()
			categoryItem.SetParent(categoryListBox)
			categoryItem.SetPosition(0, len(categoryListBox.GetItems())*32, False, True)
			categoryItem.SetData(key, data["name"], categoryListBox)
			categoryItem.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OverInCategory, key, proxy(categoryItem))
			categoryItem.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OverOutCategory, key, proxy(categoryItem))
			categoryItem.SetEvent(self.ClickCategory, "mouse_click", key, -1)
			categoryItem.Show()
			categoryListBox.AppendItem(categoryItem)

		categoryListBox.SetBasePos(1)

	def ClearCategory(self):
		categoryListBox = self.children["categoryListBox"]
		if categoryListBox:
			categoryListBox.RemoveAllItems()

	def RefreshCategory(self):
		self.ClearCategory()
		self.ClearSubCategory()
		self.LoadShopCategory()

	def LoadShopSubCategory(self, categoryIndex):
		key = categoryIndex

		categoryData = itemShopCategoryData[key]["subCategory"]
		if len(categoryData) == 0:
			return

		subCategoryListBox = self.children["subCategoryListBox"]

		subCategoryItem = SubCategoryItem()
		subCategoryItem.SetParent(subCategoryListBox)
		subCategoryItem.SetPosition(0, 0, False, True)
		subCategoryItem.SetData(255, "Geri Dn", subCategoryListBox)
		subCategoryItem.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OverInSubCategory, 255, proxy(subCategoryItem))
		subCategoryItem.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OverOutSubCategory, 255, proxy(subCategoryItem))
		subCategoryItem.SetEvent(self.ClickSubCategory2, "mouse_click", 0, 0)
		subCategoryItem.Show()
		subCategoryListBox.AppendItem(subCategoryItem)

		for j in xrange(len(categoryData)):
			subCategoryItem = SubCategoryItem()
			subCategoryItem.SetParent(subCategoryListBox)
			subCategoryItem.SetPosition(0, len(subCategoryListBox.GetItems())*32, False, True)
			subCategoryItem.SetData(j, categoryData[j][0], subCategoryListBox)
			subCategoryItem.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OverInSubCategory, j, proxy(subCategoryItem))
			subCategoryItem.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OverOutSubCategory, j, proxy(subCategoryItem))
			subCategoryItem.SetEvent(self.ClickSubCategory, "mouse_click", key, j)
			subCategoryItem.Show()
			subCategoryListBox.AppendItem(subCategoryItem)

		subCategoryListBox.SetBasePos(1)

	def ClearSubCategory(self):
		subCategoryListBox = self.children["subCategoryListBox"]
		if subCategoryListBox:
			subCategoryListBox.RemoveAllItems()

	def ClickCategory(self, emptyArg, categoryIndex, categorySubIndex = -1):
		if self.categoryIndex == categoryIndex:
			if categorySubIndex == self.categorySubIndex:
				return

		oldIndex = self.categoryIndex
		self.categoryIndex = categoryIndex
		self.categorySubIndex = categorySubIndex

		categoryItems = self.children["categoryListBox"].GetItems()
		for category in categoryItems:
			if category.categoryIndex == oldIndex:
				self.OverOutCategory(oldIndex, category)
			elif category.categoryIndex == categoryIndex:
				self.OverInCategory(categoryIndex, category)

		subCats = itemShopCategoryData.get(categoryIndex, {}).get("subCategory", [])
		if len(subCats) > 0:
			self.OverInCategoryClick(categoryIndex, None)

		self.RefreshItem()

	def ClickSubCategory(self, emptyArg, categoryIndex, categorySubIndex = -1):
		if self.categoryIndex == categoryIndex:
			if categorySubIndex == self.categorySubIndex:
				return

		self.ClearSubCategoryImage(categorySubIndex)

		self.categoryIndex = categoryIndex
		self.categorySubIndex = categorySubIndex
		self.RefreshItem()

	def ClearSubCategoryImage(self, categorySubIndex = -1):
		subCategoryItems = self.children["subCategoryListBox"].GetItems()
		for subCategory in subCategoryItems:
			if (subCategory.GetSubIndex() == categorySubIndex):
				continue

			subCategory.LoadImage(IMG_DIR+"sub_category_no_selected.png")
			subCategory.OnRender()

	def ClickSubCategory2(self, emptyArg, categoryIndex, categorySubIndex = -1):
		self.RefreshCategory()
		self.LoadFirstOpening()

	def OverOutCategory(self, categoryIndex, categoryItem):
		if categoryIndex == self.categoryIndex:
			return

		categoryItem.LoadImage(IMG_DIR+"category_no_selected.png")
		categoryItem.OnRender()

	def OverInCategory(self, categoryIndex, categoryItem):
		categoryItem.LoadImage(IMG_DIR+"category_selected.png")
		categoryItem.OnRender()

	def OverInCategoryClick(self, categoryIndex, categoryItem):
		self.ClearCategory()
		self.ClearSubCategory()
		self.LoadShopSubCategory(categoryIndex)

	def OverOutSubCategory(self, subCategoryIndex, subCategoryItem):
		if subCategoryIndex == self.categorySubIndex:
			return

		subCategoryItem.LoadImage(IMG_DIR+"sub_category_no_selected.png")
		subCategoryItem.OnRender()

	def OverInSubCategory(self, subCategoryIndex, subCategoryItem):
		subCategoryItem.LoadImage(IMG_DIR+"sub_category_selected.png")
		subCategoryItem.OnRender()

	def RefreshItem(self):
		self.ClearItemList()

		if itemshopData.has_key(self.categoryIndex):
			itemData = itemshopData[self.categoryIndex]
			if self.categorySubIndex == -1:
				allList = []

				for itemList in itemData:
					for shopItem in itemList:
						allList.append(shopItem)

				self.RefreshItemList(allList)
			else:
				if self.categorySubIndex >= len(itemData):
					return

				itemList = itemData[self.categorySubIndex]
				self.RefreshItemList(itemList)

	def SortList(self, itemDataList):
		sortData = []

		for itemData in itemDataList:
			sortItem = SortClass(itemData)
			sortData.append(sortItem)

		sortData.sort()

		itemDataListEx = []
		for shortItem in sortData:
			itemDataListEx.append(shortItem.arg)

		return itemDataListEx

	def ClearItemList(self):
		itemListBox = self.children["itemListBox"]
		itemListBox.RemoveAllItems()

	def RefreshItemList(self, itemDataList):
		global itemShopPriceType

		self.ClosePurchasesWindow()

		if len(itemDataList) == 0:
			return

		itemListBox = self.children["itemListBox"]

		itemDataList = self.SortList(itemDataList)
		itemWindowPtr = ItemWindow(itemListBox)
		itemWindowPtr.SetParent(itemListBox)
		itemWindowPtr.SetPosition(0, len(itemListBox.GetItems())*132, False, True)
		itemWindowPtr.Show()

		for shopItem in itemDataList:
			if (itemShopPriceType != 0 and shopItem[LIST_ITEM_SELL_TYPE] == net.DC_ISHOP_SELL_TYPE_COINS):
				continue
			elif (itemShopPriceType != 1 and shopItem[LIST_ITEM_SELL_TYPE] == net.DC_ISHOP_SELL_TYPE_CASH):
				continue
			elif (itemShopPriceType != 2 and shopItem[LIST_ITEM_SELL_TYPE] == net.DC_ISHOP_SELL_TYPE_EM):
				continue

			xItem = ItemShopItem()
			xItem.SetParent(itemWindowPtr)
			xItem.SetMouseWheelScrollEvent(itemListBox.OnMouseWheelScroll_ScrollBar)
			xItem.SetPosition(len(itemWindowPtr.children)*250, 0)
			xItem.LoadData(shopItem)
			xItem.Show()
			itemWindowPtr.AppendWindow(xItem)

			if len(itemWindowPtr.children) == 3:
				itemListBox.AppendItem(itemWindowPtr)
				itemWindowPtr = ItemWindow(itemListBox)
				itemWindowPtr.SetParent(itemListBox)
				itemWindowPtr.SetPosition(0, len(itemListBox.GetItems())*132, False, True)
				itemWindowPtr.Show()

		if itemWindowPtr != None:
			if len(itemWindowPtr.children) > 0:
				itemListBox.AppendItem(itemWindowPtr)

	def InsertItemWithType(self, itemDataList, insertType):
		global itemShopPriceType

		currentTime = app.GetGlobalTimeStamp()
		for key, data in itemshopData.items():
			for categoryItems in data:
				for itemData in categoryItems:
					if (itemShopPriceType != 0 and itemData[LIST_ITEM_SELL_TYPE] == net.DC_ISHOP_SELL_TYPE_COINS):
						continue
					elif (itemShopPriceType != 1 and itemData[LIST_ITEM_SELL_TYPE] == net.DC_ISHOP_SELL_TYPE_CASH):
						continue
					elif (itemShopPriceType != 2 and itemData[LIST_ITEM_SELL_TYPE] == net.DC_ISHOP_SELL_TYPE_EM):
						continue

					if insertType == LIST_ITEM_DISCOUNT:
						if itemData[LIST_ITEM_DISCOUNT] > 0 or itemData[LIST_ITEM_OFFER_TIME] > 0:
							if not itemData in itemDataList:
								itemDataList.append(itemData)
					elif insertType == LIST_ITEM_TOP_SELLING_INDEX:
						if itemData[LIST_ITEM_TOP_SELLING_INDEX] >= 0 and itemData[LIST_ITEM_TOP_SELLING_INDEX] <= 10:
							if not itemData in itemDataList:
								itemDataList.append(itemData)
					elif insertType == LIST_ITEM_ADDED_TIME:
						if itemData[LIST_ITEM_ADDED_TIME] > currentTime-(60*60*24*3):
							if not itemData in itemDataList:
								itemDataList.append(itemData)
					else:
						itemDataList.append(itemData)

		return itemDataList

	def OfferItems(self):
		self.ClearItemList()
		itemDataList = []
		itemDataList = self.InsertItemWithType(itemDataList, LIST_ITEM_DISCOUNT)
		self.RefreshItemList(itemDataList)

	def HotItems(self):
		self.ClearItemList()

		itemDataList = []
		itemDataList = self.InsertItemWithType(itemDataList, LIST_ITEM_TOP_SELLING_INDEX)
		self.RefreshItemList(itemDataList)

	def LoadFirstOpening(self):
		self.categoryIndex = -1
		self.categorySubIndex = -1

		self.RefreshCategory()
		self.ClearItemList()

		itemListBox = self.children["itemListBox"]

		if len(eventCategory) <= 3:
			itemWindowPtr = ItemWindow(itemListBox)
			itemWindowPtr.SetParent(itemListBox)
			itemWindowPtr.SetPosition(0, len(itemListBox.GetItems())*132, False, True)
			itemWindowPtr.Show()

			for banner in xrange(len(eventCategory)):
				xBanner = ItemShopBanner()
				xBanner.SetParent(itemWindowPtr)
				xBanner.SetMouseWheelScrollEvent(itemListBox.OnMouseWheelScroll_ScrollBar)
				xBanner.SetPosition(len(itemWindowPtr.children)*250, 0)
				xBanner.LoadData(banner)
				xBanner.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OverInBanner, banner, proxy(xBanner))
				xBanner.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OverOutBanner, banner, proxy(xBanner))
				xBanner.SetEvent(self.ClickBanner, "mouse_click", eventCategory[banner][1][0], eventCategory[banner][1][1])
				xBanner.Show()
				itemWindowPtr.AppendWindow(xBanner)

			if itemWindowPtr != None:
				if len(itemWindowPtr.children) > 0:
					itemListBox.AppendItem(itemWindowPtr)

		itemDataList = []
		itemDataList = self.InsertItemWithType(itemDataList, LIST_ITEM_TOP_SELLING_INDEX)
		itemDataList = self.InsertItemWithType(itemDataList, LIST_ITEM_DISCOUNT)
		itemDataList = self.InsertItemWithType(itemDataList, LIST_ITEM_ADDED_TIME)

		if len(itemDataList) == 0:
			itemDataList = self.InsertItemWithType(itemDataList, 99)

		itemDataList = self.SortList(itemDataList)
		self.RefreshItemList(itemDataList)

	def ClickBanner(self, emptyArg, categoryIndex, categorySubIndex):
		self.categoryIndex = categoryIndex
		self.categorySubIndex = categorySubIndex
		self.RefreshItem()

	def MainPage(self):
		self.LoadFirstOpening()

	def WheelPage(self):
		if app.ENABLE_WHEEL_OF_FORTUNE:
			net.SendChatPacket("/wheel_of_fortune open %d" % int(net.WHEEL_TYPE_EP))
			return

			wheelDialog = uicommon.QuestionDialog()
			wheelDialog.SetText("Hangi ark evirmek istiyorsun?")
			wheelDialog.SetAcceptText("Ep ark")
			wheelDialog.SetCancelText("Mp ark")
			wheelDialog.SetAcceptEvent(lambda arg = net.WHEEL_TYPE_EP: self.OpenWheelWindow(arg))
			wheelDialog.SetCancelEvent(lambda arg = net.WHEEL_TYPE_MP: self.OpenWheelWindow(arg))
			wheelDialog.Open()
			self.children["wheelDialog"] = wheelDialog
		else:
			pass

	def OpenWheelWindow(self, wheel):
		if app.ENABLE_WHEEL_OF_FORTUNE:
			net.SendChatPacket("/wheel_of_fortune open %d" % int(wheel))
			self.children["wheelDialog"].Close()
		else:
			pass

	def SetSellTypeBtn(self, index):
		global itemShopPriceType
		global CopyCacheToData

		itemShopPriceType = index

		OldInex = self.MoneySellType
		self.MoneySellType = index

		if (self.MoneySellType == 0):
			self.children["dragonCashBtn"].Down()
			self.children["dragonCoinBtn"].SetUp()
			self.children["dragonEmBtn"].SetUp()
			if (OldInex == 2):
				CopyCacheToData()
		elif (self.MoneySellType == 1):
			self.children["dragonCashBtn"].SetUp()
			self.children["dragonCoinBtn"].Down()
			self.children["dragonEmBtn"].SetUp()
			if (OldInex == 2):
				CopyCacheToData()
		elif (self.MoneySellType == 2):
			self.children["dragonCashBtn"].SetUp()
			self.children["dragonCoinBtn"].SetUp()
			self.children["dragonEmBtn"].Down()
			net.SendItemShopPacket(net.DC_ISHOP_EM_REFRESH, 0, long(0), int(0), "_GirisYenile_")
			return

		self.LoadFirstOpening()

	def BuyDragonCoin(self):
		net.SendChatPacket("/in_game_mall")

	def PurchaseBtn(self):
		self.OpenPurchasesWindow()

	def OpenWeb(self, url):
		self.CloseWeb()
		webWnd = WebWindow(self)
		webWnd.Open(url)
		self.children["WebWindow"] = webWnd

	def CloseWeb(self):
		if self.children.has_key("WebWindow"):
			webWnd = self.children["WebWindow"]
			webWnd.Close()
			webWnd.Destroy()
			del self.children["WebWindow"]

	def OverOutBanner(self, index, bannerItem):
		bannerItem.LoadImage(IMG_DIR+eventCategory[index][0][0])
		bannerItem.OnRender(self.children["itemListBox"])

	def OverInBanner(self, index, bannerItem):
		bannerItem.LoadImage(IMG_DIR+eventCategory[index][0][1])
		bannerItem.OnRender(self.children["itemListBox"])

	def SetDragonCashReal(self, dragonCashValue):
		text = "|cffF8BE47"+localeInfo.ITEMSHOP_DRAGONCASHT+"|r |cffffffff"+NumberToMoneyFormat(dragonCashValue)+"|r"
		self.children["dragonCashText"].SetText(text)

	def SetDragonCoinReal(self, dragonCoinValue):
		text = "|cffF8BE47"+localeInfo.ITEMSHOP_DRAGONCOINT+"|r |cffffffff"+NumberToMoneyFormat(dragonCoinValue)+"|r"
		self.children["dragonCoinText"].SetText(text)

	def SetDragonEmReal(self, dragonEmValue):
		text = "|cffF8BE47"+localeInfo.ITEMSHOP_DRAGONEMT+"|r |cffffffff"+NumberToMoneyFormat(dragonEmValue)+"|r"
		self.children["dragonEmText"].SetText(text)

	def UpdateItem(self, itemID, itemStock):
		itemList = self.children["itemListBox"].GetItems()
		for listBox in itemList:
			for shopItem in listBox.children:
				if isinstance(shopItem, ItemShopItem):
					if shopItem.data[LIST_ITEM_ID] == itemID:
						shopItem.data[LIST_ITEM_STOCK] = itemStock
						shopItem.LoadData(shopItem.data)

	def SetDragonCash(self, dragonCashValue):
		if self.RealMoneyCash == 0:
			self.RealMoneyCash = dragonCashValue
			self.SetDragonCashReal(self.RealMoneyCash)
		else:
			self.NewMoneyCash = dragonCashValue
			if self.NewMoneyCash == self.RealMoneyCash:
				self.MoneyFlagCash = False
			else:
				self.MoneyFlagCash = True
				self.MoneyRangeCash = self.NewMoneyCash - self.RealMoneyCash
				self.moneySizeCash = 0

	def SetDragonCoin(self, dragonCoinValue):
		if self.RealMoneyCoins == 0:
			self.RealMoneyCoins = dragonCoinValue
			self.SetDragonCoinReal(self.RealMoneyCoins)
		else:
			self.NewMoneyCoins = dragonCoinValue
			if self.NewMoneyCoins == self.RealMoneyCoins:
				self.MoneyFlagCoins = False
			else:
				self.MoneyFlagCoins = True
				self.MoneyRangeCoins = self.NewMoneyCoins - self.RealMoneyCoins
				self.moneySizeCoins = 0

	def SetDragonEm(self, dragonEmValue):
		if self.RealMoneyEm == 0:
			self.RealMoneyEm = dragonEmValue
			self.SetDragonEmReal(self.RealMoneyEm)
		else:
			self.NewMoneyEm = dragonEmValue
			if self.NewMoneyEm == self.RealMoneyEm:
				self.MoneyFlagEm = False
			else:
				self.MoneyFlagEm = True
				self.MoneyRangeEm = self.NewMoneyEm - self.RealMoneyEm
				self.moneySizeEm = 0

	def Open(self):
		global openTheCache
		global CopyDataToCache
		global CopyCacheToData
		global itemShopPriceType

		if (openTheCache == False):
			CopyDataToCache()
		else:
			CopyCacheToData()

		itemShopPriceType = 0
		self.MoneySellType = 0

		self.children["LoadingImage"].Show()
		self.children["dragonCashBtn"].Down()
		self.children["dragonCoinBtn"].SetUp()
		self.children["dragonEmBtn"].SetUp()
		self.LoadFirstOpening()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()
		self.children["LoadingImage"].Hide()

	if app.ENABLE_DRAGON_COIN_EM_MARKET:
		def OpenEm(self):
			global itemShopPriceType
			global LoadToEmData

			LoadToEmData()

			itemShopPriceType = 2
			self.MoneySellType = 2

			self.children["LoadingImage"].Show()
			self.children["dragonCashBtn"].SetUp()
			self.children["dragonCoinBtn"].SetUp()
			self.children["dragonEmBtn"].Down()
			self.LoadFirstOpening()
			self.SetCenterPosition()
			self.SetTop()
			self.Show()
			self.children["LoadingImage"].Hide()

	def CloseLoading(self):
		self.children["LoadingImage"].Hide()

	def Close(self):
		self.CloseWeb()

		global buyQuestionDialog
		if buyQuestionDialog != None:
			buyQuestionDialog.Hide()
			buyQuestionDialog.Destroy()
			buyQuestionDialog = None

		self.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def __ClickRadioButton(self, buttonList, buttonIndex):
		try:
			btn=buttonList[buttonIndex]
		except IndexError:
			return
		for eachButton in buttonList:
			eachButton.SetUp()
		btn.Down()

	# def AdminBgOpenBtn(self):
		# self.Close()
		# if not chr.IsGameMaster(player.GetMainCharacterIndex()):
			# return
		# net.SendItemShopAdminPacket()

	def OpenPurchasesWindow(self):
		# self.BackToItemShop()
		self.children["itemListBox"].Hide()
		self.children["itemScrollBar"].Hide()
		self.children["categoryListBox"].Hide()
		self.children["subCategoryListBox"].Hide()
		self.children["categoryScrollBar"].Hide()

		self.children["PurchasesScrollBar"].Show()
		self.children["PurchasesListBox"].Show()

		if self.children["sendPacketDataLog"] == 0:
			self.children["sendPacketDataLog"] = 1
			self.children["LoadingImage"].Show()
			net.SendChatPacket("/dc_shop_open_log")
		else:
			self.RefreshPurchasesWindow()

	def ItemShopLogRefresh(self):
		if self.children["sendPacketDataLog"] == 1:
			self.children["sendPacketDataLog"] = 0

	def SortPurchasesWindow(self):
		global playerLog
		sortData = []
		for logData in playerLog:
			sortLog = SortClass(logData,True)
			sortData.append(sortLog)
		sortData.sort()
		logDataList = []
		for sortLog in sortData:
			logDataList.append(sortLog.arg)
		return logDataList

	def RefreshPurchasesWindow(self):
		PurchasesListBox = self.children["PurchasesListBox"]
		PurchasesListBox.Show()
		PurchasesListBox.RemoveAllItems()

		global playerLog
		playerLog = self.SortPurchasesWindow()

		logTitle = PurchasesLog(PurchasesListBox)
		logTitle.SetParent(PurchasesListBox)
		logTitle.LoadData(-1)
		logTitle.SetPosition(0, 0, False, True)
		logTitle.Show()
		PurchasesListBox.AppendItem(logTitle)

		for j in xrange(len(playerLog)):
			logItem = PurchasesLog(PurchasesListBox)
			logItem.SetParent(PurchasesListBox)
			logItem.LoadData(j)
			logItem.SetPosition(0, len(PurchasesListBox.GetItems())*35, False, True)
			logItem.Show()
			PurchasesListBox.AppendItem(logItem)
		PurchasesListBox.Render(0)

	def ClosePurchasesWindow(self):
		self.children["PurchasesScrollBar"].Hide()
		self.children["PurchasesListBox"].Hide()

		self.children["itemListBox"].Show()
		self.children["itemScrollBar"].Show()
		self.children["categoryListBox"].Show()
		self.children["categoryScrollBar"].Show()

class PurchasesLog(ui.ExpandedImageBoxNewShop):
	def __del__(self):
		ui.ExpandedImageBoxNewShop.__del__(self)

	def Destroy(self):
		self.childrenImages = {}
		self.childrenTextLine = {}
		self.parent = None

	def __init__(self, parent):
		ui.ExpandedImageBoxNewShop.__init__(self)
		self.Destroy()
		self.parent = proxy(parent)

	def LoadData(self, index):
		if index >= 0:
			self.childrenImages["self"] = self
			self.LoadImage(IMG_DIR+"purch_img.png")

		try:
			logData = playerLog[index]
		except:
			return

		if index >= 0:
			dateText = logData[LOG_DATE_TEXT]
			accountText = logData[LOG_ACCOUNT]
			ipText = logData[LOG_IP]
			if logData[LOG_ITEM] == 1:
				itemText = localeInfo.ITEMSHOP_WHEEL_PURCHASE
			else:
				item.SelectItem(logData[LOG_ITEM])
				if logData[LOG_COUNT] > 1:
					itemText = "|cffF7BD48%sx%d|r" % (item.GetItemName(),logData[LOG_COUNT])
				else:
					itemText = "|cffF7BD48%s|r" % item.GetItemName()

			if (logData[LOG_PRICE_TYPE] == 1):
				priceText = localeInfo.PURCHASES_PRICE_TEXT % NumberToMoneyFormat(logData[LOG_PRICE])
			elif (logData[LOG_PRICE_TYPE] == 2):
				priceText = localeInfo.PURCHASES_PRICE_MP_TEXT % NumberToMoneyFormat(logData[LOG_PRICE])
			elif (logData[LOG_PRICE_TYPE] == 3):
				priceText = localeInfo.PURCHASES_PRICE_EM_TEXT % NumberToMoneyFormat(logData[LOG_PRICE])
		else:
			dateText = localeInfo.PURCHASES_DATE
			accountText = localeInfo.PURCHASES_ACCOUNTID
			ipText = localeInfo.PURCHASES_IP
			itemText = localeInfo.PURCHASES_ITEMBOUGHT
			priceText = localeInfo.PURCHASES_PRICE

		# LOG_PRICE_TYPE

		textList = [
			[75,5,dateText],
			[260,5,accountText],
			[400,5,ipText],
			[600,5,itemText],
			[800,5,priceText],
		]

		for j in xrange(len(textList)):
			text = textList[j]
			logText = ui.TextLine()
			logText.SetParent(self)
			logText.SetFontName("Rail Regular:13")
			logText.SetText(text[2])
			logText.SetHorizontalAlignCenter()
			if index >= 0:
				logText.SetPosition(text[0], text[1])
			else:
				logText.SetPosition(text[0], 0)
			logText.Show()
			self.childrenTextLine["text%d"%j] = logText

	def OnRender(self):
		listboxHeight = self.parent.GetHeight()
		(pgx,pgy) = self.parent.GetGlobalPosition()

		for key, textline in self.childrenTextLine.items():
			(igx,igy) = textline.GetGlobalPosition()
			if igy < pgy:
				textline.Hide()
			elif igy > (pgy+listboxHeight-25):
				textline.Hide()
			else:
				textline.Show()

		for key, image in self.childrenImages.items():
			(jgx,jgy) = image.GetGlobalPosition()
			imageHeight = image.GetHeight()
			if (jgy + imageHeight) <= pgy or jgy >= (pgy + listboxHeight):
				image.Hide()
				image.SetRenderingRect(0, 0, 0, 0)
			elif jgy < pgy:
				image.Show()
				image.SetRenderingRect(0,ui.calculateRect(imageHeight-abs(jgy-pgy),imageHeight),0,0)
			elif jgy+imageHeight > (pgy+listboxHeight-8):
				calculate = (pgy+listboxHeight-8) - (jgy+imageHeight)
				if calculate == 0:
					continue
				image.Show()
				image.SetRenderingRect(0.0,0.0,0.0,ui.calculateRect(imageHeight-abs(calculate),imageHeight))
			else:
				image.Show()
				image.SetRenderingRect(0,0,0,0)

class ItemShopBoard(ui.Window):
	CORNER_WIDTH = 7
	CORNER_HEIGHT = 7
	LINE_WIDTH = 7
	LINE_HEIGHT = 7
	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self):
		ui.Window.__init__(self)
		self.MakeBoard()
		self.MakeBase()

	def MakeBoard(self):
		cornerPath = IMG_DIR+"board/corner_"
		linePath = IMG_DIR+"board/"
		CornerFileNames = [ cornerPath+dir+".png" for dir in ("left_top", "left_bottom", "right_top", "right_bottom") ]
		LineFileNames = [ linePath+dir+".png" for dir in ("left", "right", "top", "bottom") ]
		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ui.ExpandedImageBoxNewShop()
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)
		self.Lines = []
		for fileName in LineFileNames:
			Line = ui.ExpandedImageBoxNewShop()
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)
		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	def MakeBase(self):
		self.Base = ui.ExpandedImageBoxNewShop()
		self.Base.AddFlag("not_pick")
		self.Base.LoadImage(IMG_DIR+"board/base.png")
		self.Base.SetParent(self)
		self.Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Base.Show()

	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.Base=0
		self.Corners=0
		self.Lines=0
		self.CORNER_WIDTH = 0
		self.CORNER_HEIGHT = 0
		self.LINE_WIDTH = 0
		self.LINE_HEIGHT = 0
		self.LT = 0
		self.LB = 0
		self.RT = 0
		self.RB = 0
		self.L = 0
		self.R = 0
		self.T = 0
		self.B = 0

	def SetSize(self, width, height):
		width = max(self.CORNER_WIDTH*2, width)
		height = max(self.CORNER_HEIGHT*2, height)
		ui.Window.SetSize(self, width, height)
		self.Corners[self.LB].SetPosition(0, height - self.CORNER_HEIGHT)
		self.Corners[self.RT].SetPosition(width - self.CORNER_WIDTH, 0)
		self.Corners[self.RB].SetPosition(width - self.CORNER_WIDTH, height - self.CORNER_HEIGHT)
		self.Lines[self.R].SetPosition(width - self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Lines[self.B].SetPosition(self.CORNER_HEIGHT, height - self.CORNER_HEIGHT)
		verticalShowingPercentage = float((height - self.CORNER_HEIGHT*2) - self.LINE_HEIGHT) / self.LINE_HEIGHT
		horizontalShowingPercentage = float((width - self.CORNER_WIDTH*2) - self.LINE_WIDTH) / self.LINE_WIDTH
		self.Lines[self.L].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.R].SetRenderingRect(0, 0, 0, verticalShowingPercentage)
		self.Lines[self.T].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)
		self.Lines[self.B].SetRenderingRect(0, 0, horizontalShowingPercentage, 0)
		if self.Base:
			self.Base.SetRenderingRect(0, 0, horizontalShowingPercentage, verticalShowingPercentage)

class WebWindow(ItemShopBoard):
	def __del__(self):
		ItemShopBoard.__del__(self)

	def Destroy(self):
		self.oldPos=(0,0)
		self.closeBtn=None
		self.parent = None

	def __init__(self, parent):
		ItemShopBoard.__init__(self)
		self.Destroy()
		self.parent = proxy(parent)
		self.LoadWindow()

	def LoadWindow(self):
		self.AddFlag("attach")
		self.AddFlag("float")
		#self.AddFlag("movable")
		self.SetSize(450*2,450)
		closeBtn = ui.Button()
		closeBtn.SetParent(self)
		closeBtn.SetUpVisual(IMG_DIR+"close_0.png")
		closeBtn.SetOverVisual(IMG_DIR+"close_1.png")
		closeBtn.SetDownVisual(IMG_DIR+"close_2.png")
		closeBtn.SetPosition(self.GetWidth()-closeBtn.GetWidth(), 0)
		closeBtn.SetEvent(self.parent.CloseWeb)
		closeBtn.Show()
		self.closeBtn=closeBtn

	def Close(self):
		app.HideWebPage()
		self.Hide()

	def Open(self, url):
		self.SetSize(450*2,450)
		self.Show()
		self.SetTop()
		self.SetCenterPosition()

		x, y = self.GetGlobalPosition()
		sx, sy = x + 10, y + 30
		ex, ey = sx + self.GetWidth() - 20, sy + self.GetHeight() - 40
		app.ShowWebPage(url, (sx, sy, ex, ey))

	def OnUpdate(self):
		newPos = self.GetGlobalPosition()
		if newPos == self.oldPos:
			return
		self.oldPos = newPos
		x, y = newPos
		sx, sy = x + 10, y + 30
		ex, ey = sx + self.GetWidth() - 20, sy + self.GetHeight() - 40
		app.MoveWebPage((sx, sy, ex, ey))

class BuyWindow(ItemShopBoard):
	def __del__(self):
		ItemShopBoard.__del__(self)

	def __init__(self):
		ItemShopBoard.__init__(self)
		self.AddFlag("attach")
		self.AddFlag("float")
		self.Destroy()

		buyText = MultiTextLine()
		buyText.SetParent(self)
		buyText.SetTextRange(25)
		buyText.SetPosition(self.GetWidth()+65/2, 90)
		buyText.SetTextType("horizontal#center")
		buyText.SetFontName("Rail Regular:16")
		buyText.Show()
		self.children["buyText"] = buyText

		yesBtn = ui.Button()
		yesBtn.SetParent(self)
		yesBtn.SetUpVisual(IMG_DIR+"sell_btn_n.png")
		yesBtn.SetOverVisual(IMG_DIR+"sell_btn_h.png")
		yesBtn.SetDownVisual(IMG_DIR+"sell_btn_d.png")
		yesBtn.SetText("Evet")
		yesBtn.Show()
		self.children["yesBtn"] = yesBtn

		cancelBtn = ui.Button()
		cancelBtn.SetParent(self)
		cancelBtn.SetUpVisual(IMG_DIR+"sell_btn_n.png")
		cancelBtn.SetOverVisual(IMG_DIR+"sell_btn_h.png")
		cancelBtn.SetDownVisual(IMG_DIR+"sell_btn_d.png")
		cancelBtn.SetText("Hayr")
		cancelBtn.Show()
		self.children["cancelBtn"] = cancelBtn

	def Destroy(self):
		self.children={}

	def SetText(self, text):
		buyText = self.children["buyText"]
		buyText.SetText(text)

		(x, y) = buyText.GetTextSize()
		(minWidth, minHeight) = (256, 142)

		if x+40 > minWidth:
			minWidth = x+40

		if not ((minWidth % 2) == 0):
			minWidth += 1

		self.SetSize(minWidth,minHeight)
		buyText.SetPosition(self.GetWidth()/2, 28)

		self.children["yesBtn"].SetPosition((self.GetWidth()/2)-self.children["yesBtn"].GetWidth()-15,94)
		self.children["cancelBtn"].SetPosition((self.GetWidth()/2)+15,94)

	def SetAcceptEvent(self, func):
		self.children["yesBtn"].SetEvent(func)

	def SetCancelEvent(self, func):
		self.children["cancelBtn"].SetEvent(func)

	def OnPressEscapeKey(self):
		self.children["cancelBtn"].CallEvent()
		return True

class SortClass:
	def __init__(self, arg, isLog = False):
		self.arg = arg
		self.isLog = isLog

	def __del__(self):
		self.arg = []

	def __lt__(self, other):
		if self.isLog:
			return self.arg[LOG_DATE] >= other.arg[LOG_DATE]
		else:
			currentTime = app.GetGlobalTimeStamp()

			# hot item
			if self.arg[LIST_ITEM_TOP_SELLING_INDEX] <= 10 or other.arg[LIST_ITEM_TOP_SELLING_INDEX] <= 10:
				return self.arg[LIST_ITEM_TOP_SELLING_INDEX] <= other.arg[LIST_ITEM_TOP_SELLING_INDEX]

			# time offer
			if self.arg[LIST_ITEM_OFFER_TIME] != 0 or other.arg[LIST_ITEM_OFFER_TIME] != 0:
				if self.arg[LIST_ITEM_OFFER_TIME] > 0 and other.arg[LIST_ITEM_OFFER_TIME] > 0:
					return ((self.arg[LIST_ITEM_OFFER_TIME]-currentTime) <= (other.arg[LIST_ITEM_OFFER_TIME]-currentTime))
				else:
					return self.arg[LIST_ITEM_OFFER_TIME] >= other.arg[LIST_ITEM_OFFER_TIME]

			# discount
			if self.arg[LIST_ITEM_DISCOUNT] != 0 or other.arg[LIST_ITEM_DISCOUNT] != 0:
				return self.arg[LIST_ITEM_DISCOUNT] >= other.arg[LIST_ITEM_DISCOUNT]

			# added time
			if self.arg[LIST_ITEM_ADDED_TIME] > currentTime-(60*60*24*3) or other.arg[LIST_ITEM_ADDED_TIME] > currentTime-(60*60*24*3):
				return self.arg[LIST_ITEM_ADDED_TIME] >= other.arg[LIST_ITEM_ADDED_TIME]

			return self.arg[LIST_ITEM_ID] >= other.arg[LIST_ITEM_ID]

class ItemShopBanner(ui.ExpandedImageBoxNewShop):
	def __del__(self):
		ui.ExpandedImageBoxNewShop.__del__(self)

	def Destroy(self):
		self.bannerIndex = -1
		self.childrenImages = {}

	def __init__(self):
		ui.ExpandedImageBoxNewShop.__init__(self)
		self.Destroy()

	def LoadData(self, bannerIndex):
		self.bannerIndex=bannerIndex
		if bannerIndex >= len(eventCategory):
			return

		self.LoadImage(IMG_DIR+eventCategory[bannerIndex][0][0])
		self.childrenImages["self"] = self

	def OnUpdate(self):
		pass

	def OnRender(self, parent):
		listboxHeight = parent.GetHeight()
		(pgx,pgy) = parent.GetGlobalPosition()

		for key, image in self.childrenImages.items():
			(jgx,jgy) = image.GetGlobalPosition()
			imageHeight = image.GetHeight()

			if (jgy + imageHeight) <= pgy or jgy >= (pgy + listboxHeight):
				image.Hide()
				image.SetRenderingRect(0, 0, 0, 0)
			elif jgy < pgy:
				image.Show()
				image.SetRenderingRect(0,ui.calculateRect(imageHeight-abs(jgy-pgy),imageHeight),0,0)
			elif jgy+imageHeight > (pgy+listboxHeight-8):
				calculate = (pgy+listboxHeight-8) - (jgy+imageHeight)
				if calculate == 0:
					continue
				image.Show()
				image.SetRenderingRect(0.0,0.0,0.0,ui.calculateRect(imageHeight-abs(calculate),imageHeight))
			else:
				image.Show()
				image.SetRenderingRect(0,0,0,0)

class ItemShopItem(ui.ExpandedImageBoxNewShop):
	def __del__(self):
		ui.ExpandedImageBoxNewShop.__del__(self)

	def __init__(self):
		ui.ExpandedImageBoxNewShop.__init__(self)
		self.Destroy()
		self.buyCount=1
		self.LoadImage(IMG_DIR+"item_box.png")
		self.childrenImages["self"] = self
		self.ShopStockTime = 0
		self.ShopStockStatus = False

	def Destroy(self):
		self.data = []
		self.buyCount=0
		self.butButtonSet = False
		self.childrenImages = {}
		self.childrenTextLine = {}
		self.ShopStockTime = 0
		self.ShopStockStatus = False

	def LoadData(self, itemData):
		self.data = itemData
		itemSockets = itemData[LIST_ITEM_SOCKET]
		itemAttrs = itemData[LIST_ITEM_ATTR]
		itemTimeType = itemData[LIST_ITEM_TIME_TYPE]

		iSocketList = itemSockets.split("|")
		metinSlot = []
		for i in range(0, int(len(iSocketList))):
			metinSlot.append(int(iSocketList[i]))

####################################################
		attrSlot = []
		iAttrList = itemAttrs.split("`")
		for j in range(0, int(len(iAttrList))):
			attrData = iAttrList[j].split("|")
			attrSlot.append((int(attrData[0]), int(attrData[1])))

		ATTRIBUTE_COUNT = int(player.ATTRIBUTE_SLOT_MAX_NUM - int(len(iAttrList)))
		for j2 in xrange(ATTRIBUTE_COUNT):
			attrSlot.append((0, 0))
	####################################################

		self.SetItem(itemData[LIST_ITEM_VNUM], metinSlot, attrSlot, itemTimeType)
		self.SetCount()
		self.SetItemName(itemData[LIST_ITEM_SELLING_COUNT])
		self.SetBuyButton(itemData[LIST_ITEM_OFFER_TIME], itemData[LIST_ITEM_STOCK])
		self.SetPrice(itemData[LIST_ITEM_PRICE], itemData[LIST_ITEM_DISCOUNT])
		self.SetTime(itemData[LIST_ITEM_OFFER_TIME])
		self.SetLastSellCount(itemData[LIST_ITEM_STOCK])

		if itemData[LIST_ITEM_TOP_SELLING_INDEX] >= 0 and itemData[LIST_ITEM_TOP_SELLING_INDEX] <= 10:
			self.SetItemType(1)
		elif itemData[LIST_ITEM_DISCOUNT] > 0:
			self.SetItemType(3)
		elif itemData[LIST_ITEM_ADDED_TIME] > app.GetGlobalTimeStamp()-(60*60*24*3):
			self.SetItemType(2)

	def SetLastSellCount(self, maxSellingCount):
		if maxSellingCount != -1:
			self.ClearChildren("maxSelling")
			maxSelling = MultiTextLine()
			maxSelling.SetParent(self)
			maxSelling.SetTextRange(20)
			maxSelling.SetTextType("horizontal#right")
			maxSelling.SetFontName("Rail Regular:13")
			maxSelling.SetText(localeInfo.ITEMSHOP_STOCK_COUNT % maxSellingCount)
			maxSelling.SetPosition(self.GetWidth()-5, 4)
			maxSelling.Show()
			self.childrenTextLine["maxSelling"] = maxSelling

	def ClearChildren(self, childrenName):
		if self.childrenTextLine.has_key(childrenName):
			self.childrenTextLine[childrenName].Hide()
			self.childrenTextLine[childrenName].Destroy()
			del self.childrenTextLine[childrenName]

		if self.childrenImages.has_key(childrenName):
			self.childrenImages[childrenName].Hide()
			self.childrenImages[childrenName].Destroy()
			del self.childrenImages[childrenName]

	def FormatTime(self, seconds):
		if seconds <= 0:
			if self.butButtonSet == False:
				self.SetBuyButton(self.data[LIST_ITEM_OFFER_TIME])
			return "|cffFF7B7B0h 0m 0s"

		m, s = divmod(seconds, 60)
		h, m = divmod(m, 60)
		d, h = divmod(h, 24)

		if d > 0:
			return "|cffFF7B7B%dd %dh %dm %ds"%(d,h,m,s)
		return "|cffFF7B7B%dh %dm %ds" % (h,m,s)

	def IsSkipQuestionDialog(self):
		global buyQuestionDialog
		# global whellPageStatus

		if buyQuestionDialog != None:
			return True

		# if whellPageStatus == True:
			# return True

		return False

	def OnUpdate(self):
		if self.childrenTextLine.has_key("timeText"):
			self.childrenTextLine["timeText"].SetText(self.FormatTime(self.data[LIST_ITEM_OFFER_TIME]-app.GetGlobalTimeStamp()))

		if self.childrenTextLine.has_key("maxSelling"):
			if (self.IsSkipQuestionDialog() == True):
				return

			if (app.GetTime() > self.ShopStockTime + 0.5):
				self.ShopStockTime = app.GetTime()

				iStock = self.childrenTextLine["maxSelling"]
				if (self.ShopStockStatus == False):
					self.ShopStockStatus = True
					iStock.SetText("")
				else:
					self.ShopStockStatus = False
					GetStock = self.data[LIST_ITEM_STOCK]
					if GetStock != -1:
						iStock.SetText("")
						iStock.SetText(localeInfo.ITEMSHOP_STOCK_COUNT % GetStock)

	def SetTime(self, time):
		self.ClearChildren("timeText")
		if time != 0:
			self.butButtonSet = False

			timeText = ui.TextLine()
			timeText.SetParent(self)
			timeText.AddFlag("not_pick")
			timeText.SetPosition(168, 65)
			timeText.SetWindowHorizontalAlignLeft()
			timeText.SetFontName("Rail Regular:13")
			timeText.Show()
			self.childrenTextLine["timeText"] = timeText

	def SetBuyButton(self, time, maxSellingCount = -1):
		self.ClearChildren("buyButton")
		self.butButtonSet = False

		############################################
		##############---n-zleme--################
		if app.ENABLE_SHOW_CHEST_DROP:
			self.ClearChildren("previewButton")
			item.SelectItem(self.data[LIST_ITEM_VNUM])
			if item.GetItemType() == item.ITEM_TYPE_GIFTBOX:
				previewButton = ui.ExpandedImageBoxNewShop()
				previewButton.SetParent(self)
				previewButton.SetPosition(103, 82)
				previewButton.LoadImage(IMG_DIR+"chest_n.png")
				previewButton.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OverInPreviewBtn)
				previewButton.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OverOutPreviewBtn)
				previewButton.SetEvent(ui.__mem_func__(self.ClickPreviewBtn), "mouse_click")
				previewButton.Show()
				self.childrenImages["previewButton"] = previewButton
				previewBtnText = ui.TextLine()
				previewBtnText.SetParent(previewButton)
				previewBtnText.AddFlag("not_pick")
				previewBtnText.SetHorizontalAlignCenter()
				previewBtnText.SetVerticalAlignCenter()
				previewBtnText.SetWindowHorizontalAlignCenter()
				previewBtnText.SetWindowVerticalAlignCenter()
				previewBtnText.SetText("erik")
				previewBtnText.Show()
				self.childrenTextLine["previewBtnText"] = previewBtnText
		############################################

		buyButton = ui.ExpandedImageBoxNewShop()
		buyButton.SetParent(self)

		if ((time != 0 and app.GetGlobalTimeStamp() > time)):
			buyButton.LoadImage(IMG_DIR+"button_buy_disabled.png")
			self.butButtonSet = True
		elif (self.data[LIST_ITEM_STOCK] == 0):
			buyButton.LoadImage(IMG_DIR+"button_buy_disabled.png")
			self.butButtonSet = True
		else:
			buyButton.LoadImage(IMG_DIR+"sell_btn_n.png")
			buyButton.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OverInBuyBtn)
			buyButton.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OverOutBuyBtn)
			buyButton.SetEvent(ui.__mem_func__(self.ClickBuyBtn), "mouse_click")

		buyButton.SetPosition(175, 82)
		buyButton.Show()
		self.childrenImages["buyButton"] = buyButton

		buyBtnText = ui.TextLine()
		buyBtnText.SetParent(buyButton)
		buyBtnText.AddFlag("not_pick")
		buyBtnText.SetHorizontalAlignCenter()
		buyBtnText.SetVerticalAlignCenter()
		buyBtnText.SetWindowHorizontalAlignCenter()
		buyBtnText.SetWindowVerticalAlignCenter()
		buyBtnText.SetText(localeInfo.ITEMSHOP_BUY)
		buyBtnText.Show()
		self.childrenTextLine["buyBtnText"] = buyBtnText

	if app.ENABLE_SHOW_CHEST_DROP:
		def ClickPreviewBtn(self, emptyArg):
			interface = constInfo.GetInterfaceInstance()
			if interface:
				if interface.dlgChestDrop:
					if not interface.dlgChestDrop.IsShow():
						interface.dlgChestDrop.Open(-1, self.data[LIST_ITEM_VNUM], 1)
						net.SendChestDropVnumInfo(self.data[LIST_ITEM_VNUM])
						return

	def ClickBuyBtn(self, emptyArg):
		time = self.data[LIST_ITEM_OFFER_TIME]
		if time != 0 and app.GetGlobalTimeStamp() > time:
			return

		global buyQuestionDialog
		if buyQuestionDialog == None:
			buyQuestionDialog = BuyWindow()

		text = ""

		price = self.data[LIST_ITEM_PRICE]*self.buyCount
		discount = self.data[LIST_ITEM_DISCOUNT]
		if discount > 0:
			price = int((float(price)/100.0)*float(100-discount))

		item.SelectItem(self.data[LIST_ITEM_VNUM])

		if self.buyCount > 1:
			text += localeInfo.ITEMSHOP_BUY_TEXT_COUNT % (item.GetItemName(), self.buyCount)
		else:
			text += localeInfo.ITEMSHOP_BUY_TEXT % item.GetItemName()

		text += "\n"
		global itemShopPriceType
		if (itemShopPriceType == 0):
			text += localeInfo.ITEMSHOP_PRICE_NEW_EP % str(price)
		elif (itemShopPriceType == 1):
			text += localeInfo.ITEMSHOP_PRICE_NEW_MP % str(price)
		elif (itemShopPriceType == 2):
			text += localeInfo.ITEMSHOP_PRICE_NEW_EM % str(price)
		else:
			text += localeInfo.ITEMSHOP_PRICE_NEW_EP % str(price)

		buyQuestionDialog.SetText(text)
		buyQuestionDialog.SetAcceptEvent(self.AcceptBuy)
		buyQuestionDialog.SetCancelEvent(self.CloseQuestionDialog)
		buyQuestionDialog.SetCenterPosition()
		buyQuestionDialog.SetTop()
		buyQuestionDialog.Show()

	def CloseQuestionDialog(self):
		global buyQuestionDialog
		if buyQuestionDialog != None:
			buyQuestionDialog.Hide()
			buyQuestionDialog.Destroy()
			buyQuestionDialog = None

	def AcceptBuy(self):
		global itemShopPriceType

		pType = 0
		if (itemShopPriceType == 0):
			pType = net.DC_ISHOP_SELL_TYPE_COINS
		elif (itemShopPriceType == 1):
			pType = net.DC_ISHOP_SELL_TYPE_CASH
		elif (itemShopPriceType == 2):
			pType = net.DC_ISHOP_SELL_TYPE_EM
		else:
			return

		net.SendItemShopPacket(net.DC_ISHOP_BUY, self.buyCount, long(self.data[LIST_ITEM_ID]), int(pType), "")
		self.CloseQuestionDialog()

	def EmptyFunction(self):
		pass

	def OverOutBuyBtn(self):
		if self.childrenImages.has_key("buyButton"):
			self.childrenImages["buyButton"].LoadImage(IMG_DIR+"sell_btn_n.png")

	def OverInBuyBtn(self):
		if self.childrenImages.has_key("buyButton"):
			self.childrenImages["buyButton"].LoadImage(IMG_DIR+"sell_btn_h.png")

	def OverOutPreviewBtn(self):
		if self.childrenImages.has_key("previewButton"):
			self.childrenImages["previewButton"].LoadImage(IMG_DIR+"chest_d.png")

	def OverInPreviewBtn(self):
		if self.childrenImages.has_key("previewButton"):
			self.childrenImages["previewButton"].LoadImage(IMG_DIR+"chest_h.png")

	def SetPrice(self, price, discount):
		self.ClearChildren("lineImage")
		self.ClearChildren("itemPrice")

		itemPrice = MultiTextLine()
		itemPrice.AddFlag("not_pick")
		itemPrice.SetParent(self)
		itemPrice.SetTextRange(20)
		itemPrice.SetPosition(80, 35)
		itemPrice.SetTextType("horizontal#left")
		itemPrice.SetFontName("Rail Regular:14")

		price = price*self.buyCount

		text = ""
		if discount > 0:
			newPrice = int((float(price)/100.0)*float(100-discount))

			text = localeInfo.ITEMSHOP_PRICE_ONLY_TEXT % NumberToMoneyFormat(price)
			itemPriceEx = ui.TextLine()
			itemPriceEx.SetParent(self)
			itemPriceEx.SetText(text)
			(xSize, ySize) = itemPriceEx.GetTextSize()

			text = localeInfo.ITEMSHOP_PRICE_WITH_DISCOUNT % (NumberToMoneyFormat(price), discount)
			text += "\n"
			text += localeInfo.ITEMSHOP_PRICE_ONLY_TEXT % NumberToMoneyFormat(newPrice)

			lineImage = ui.ExpandedImageBoxNewShop()
			lineImage.SetParent(itemPrice)
			lineImage.AddFlag("not_pick")
			lineImage.LoadImage(IMG_DIR+"line.png")
			lineImage.SetDiffuseColor(0.5,0.0,0.0,0.9)
			scaleCalc = float(xSize)*(1.0/10.0)
			lineImage.SetScale(scaleCalc, 1.0)
			lineImage.SetPosition(-1, (ySize/2)+1)
			lineImage.Show()
			self.childrenImages["lineImage"] = lineImage

			self.SetItemType(3)#Bak
		else:
			text = ""
			global itemShopPriceType
			if (itemShopPriceType == 0):
				text = localeInfo.ITEMSHOP_PRICE_NEW_EP % NumberToMoneyFormat(price)
			elif (itemShopPriceType == 1):
				text = localeInfo.ITEMSHOP_PRICE_NEW_MP % NumberToMoneyFormat(price)
			elif (itemShopPriceType == 2):
				text = localeInfo.ITEMSHOP_PRICE_NEW_EM % NumberToMoneyFormat(price)
			else:
				text = localeInfo.ITEMSHOP_PRICE_NEW_EP % NumberToMoneyFormat(price)

		itemPrice.SetText(text)
		itemPrice.Show()
		self.childrenTextLine["itemPrice"] = itemPrice

	def SetItemName(self,count = 0):
		self.ClearChildren("itemName")
		itemName = ui.TextLine()
		itemName.SetParent(self)
		itemName.AddFlag("not_pick")
		itemName.SetWindowHorizontalAlignLeft()
		itemName.SetFontName("Rail Regular:15")
		itemName.SetPosition(80, 15)
		if (int(count) > 1):
			itemName.SetText("|cffF7BD48"+item.GetItemName() + " x"+str(count))
		else:
			itemName.SetText("|cffF7BD48"+item.GetItemName())
		itemName.Show()
		self.childrenTextLine["itemName"] = itemName

	def SetCount(self):
		self.ClearChildren("CountBg")
		self.ClearChildren("CountText")
		self.ClearChildren("CountLeft")
		self.ClearChildren("CountRight")

		if not item.IsFlag(item.ITEM_FLAG_STACKABLE):
			return

		CountLeft = ui.ExpandedImageBoxNewShop()
		CountLeft.SetParent(self)
		CountLeft.LoadImage(IMG_DIR+"count_left.png")
		CountLeft.SetPosition(10, 90)
		CountLeft.SetEvent(ui.__mem_func__(self.ClickCount), "mouse_click", 0)
		CountLeft.Show()
		self.childrenImages["CountLeft"] = CountLeft

		CountBg = ui.ExpandedImageBoxNewShop()
		CountBg.SetParent(self)
		CountBg.AddFlag("not_pick")
		CountBg.LoadImage(IMG_DIR+"count_back.png")
		CountBg.SetPosition(15+CountLeft.GetWidth(), 88)
		CountBg.Show()
		self.childrenImages["CountBg"] = CountBg

		CountText = ui.TextLine()
		CountText.SetParent(CountBg)
		CountText.AddFlag("not_pick")
		CountText.SetHorizontalAlignCenter()
		CountText.SetVerticalAlignCenter()
		CountText.SetWindowHorizontalAlignCenter()
		CountText.SetWindowVerticalAlignCenter()
		CountText.SetText("1")
		CountText.Show()
		self.childrenTextLine["CountText"] = CountText

		CountRight = ui.ExpandedImageBoxNewShop()
		CountRight.SetParent(self)
		CountRight.LoadImage(IMG_DIR+"count_right.png")
		CountRight.SetPosition(20+CountLeft.GetWidth()+CountBg.GetWidth(), 90)
		CountRight.SetEvent(ui.__mem_func__(self.ClickCount), "mouse_click", 1)
		CountRight.Show()
		self.childrenImages["CountRight"] = CountRight

	def ClickCount(self,emptyArg, btnType):
		value = 1

		if app.IsPressed(app.DIK_LCONTROL):
			value += 4

		buyCount = self.buyCount

		if btnType == 0:
			buyCount -= value
			if buyCount <= 0:
				buyCount = 1
		else:
			buyCount += value
			if buyCount <= 0:
				buyCount = 1
			elif buyCount > 200:
				buyCount = 200

		self.buyCount = buyCount

		if self.childrenTextLine.has_key("CountText"):
			self.childrenTextLine["CountText"].SetText(str(self.buyCount))

		itemData = self.data
		self.SetPrice(itemData[LIST_ITEM_PRICE], itemData[LIST_ITEM_DISCOUNT])

	def SetItem(self, itemVnum, metinSlot, attrSlot, itemTimeType):
		self.ClearChildren("itemImage")
		self.ClearChildren("itemCount")
		item.SelectItem(itemVnum)
		(width,height) = item.GetItemSize()
		(xPos, yPos) = (36,46)

		if height == 1:
			xPos = 30
		elif height == 2:
			yPos -= 20
		elif height == 3:
			yPos -= 30
			xPos -= 5

		itemImage = ui.ExpandedImageBoxNewShop()
		itemImage.SetParent(self)
		itemImage.LoadImage(item.GetIconImageFileName())
		itemImage.SetPosition(xPos, yPos)
		itemImage.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OverInItem, itemVnum, metinSlot, attrSlot, itemTimeType)
		itemImage.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OverOutItem)
		itemImage.Show()
		self.childrenImages["itemImage"] = itemImage

	def OverInItem(self, itemVnum, metinSlot, attrSlot, itemTimeType):
		interface = constInfo.GetInterfaceInstance()
		if interface:
			if interface.tooltipItem:
				interface.tooltipItem.SetItemToolTipNewMall(itemVnum, metinSlot, attrSlot, itemTimeType)

	def OverOutItem(self):
		interface = constInfo.GetInterfaceInstance()
		if interface:
			if interface.tooltipItem:
				interface.tooltipItem.HideToolTip()

	def SetItemType(self, itemType):
		self.ClearChildren("itemType")
		typeImages = ["hot.png","new.png","offer.png"]

		if itemType == 0:
			return

		itemType-=1
		if itemType >= len(typeImages):
			return

		typeImage = ui.ExpandedImageBoxNewShop()
		typeImage.AddFlag("not_pick")
		typeImage.SetParent(self)
		typeImage.LoadImage(IMG_DIR+typeImages[itemType])
		typeImage.SetPosition(0,0)
		typeImage.Show()
		self.childrenImages["typeImage"] = typeImage

	def OnRender(self, parent):
		listboxHeight = parent.GetHeight()
		(pgx,pgy) = parent.GetGlobalPosition()

		for key, textline in self.childrenTextLine.items():
			(igx,igy) = textline.GetGlobalPosition()
			if igy < pgy:
				textline.Hide()
			elif igy > (pgy+listboxHeight-25):
				textline.Hide()
			else:
				textline.Show()

		for key, image in self.childrenImages.items():
			(jgx,jgy) = image.GetGlobalPosition()
			imageHeight = image.GetHeight()
			if (jgy + imageHeight) <= pgy or jgy >= (pgy + listboxHeight):
				image.Hide()
				image.SetRenderingRect(0, 0, 0, 0)
			elif jgy < pgy:
				if key == "buyButton" and (jgy + (imageHeight / 2)) < pgy:
					image.Hide()
				else:
					image.Show()
					image.SetRenderingRect(0, ui.calculateRect(imageHeight-abs(jgy-pgy), imageHeight), 0, 0)
			elif jgy+imageHeight > (pgy+listboxHeight-8):
				calculate = (pgy+listboxHeight-8) - (jgy+imageHeight)
				if calculate == 0:
					continue
				if key == "buyButton" and (jgy + (imageHeight / 2)) > (pgy + listboxHeight - 8):
					image.Hide()
				else:
					image.Show()
					image.SetRenderingRect(0.0, 0.0, 0.0, ui.calculateRect(imageHeight-abs(calculate), imageHeight))
			else:
				image.Show()
				image.SetRenderingRect(0, 0, 0, 0)

class ItemWindow(ui.Window):
	def __del__(self):
		ui.Window.__del__(self)

	def __init__(self, parent):
		ui.Window.__init__(self)
		self.children=[]
		self.Destroy()
		self.parent=proxy(parent)
		self.SetSize(750,122)

	def OnUpdate(self):
		for children in self.children:
			children.OnUpdate()

	def Destroy(self):
		for children in self.children:
			children.Destroy()
			children=None
		self.children=[]
		self.parent = None

	def AppendWindow(self, window):
		self.children.append(window)
		self.OnRender()

	def OnRender(self):
		for children in self.children:
			children.OnRender(self.parent)

class CategoryItem(ui.ExpandedImageBoxNewShop):
	def __del__(self):
		ui.ExpandedImageBoxNewShop.__del__(self)

	def __init__(self):
		ui.ExpandedImageBoxNewShop.__init__(self)
		self.Destroy()
		self.categoryIndex = -1
		self.LoadImage(IMG_DIR+"category_no_selected.png")

	def Destroy(self):
		self.parent = None
		self.categoryIndex = 0
		self.categoryText = None

	def SetData(self, categoryIndex, categoryName, categoryListBox):
		self.categoryIndex = categoryIndex
		self.parent = proxy(categoryListBox)
		categoryText = MultiTextLine()
		categoryText.SetParent(self)
		categoryText.SetPosition((self.GetWidth()/2)+8, 5)
		categoryText.SetTextRange(15)
		categoryText.SetTextType("horizontal#center")
		categoryText.SetFontName("Arial:14")
		categoryText.SetText(categoryName)
		categoryText.Show()
		self.categoryText = categoryText

	def OnRender(self):
		parent = self.parent
		if parent == None:
			return

		listboxHeight = parent.GetHeight()
		(pgx,pgy) = parent.GetGlobalPosition()
		(igx,igy) = self.categoryText.GetGlobalPosition()

		if igy < pgy:
			self.categoryText.Hide()
		elif igy > (pgy+listboxHeight-25):
			self.categoryText.Hide()
		else:
			self.categoryText.Show()

		(jgx,jgy) = self.GetGlobalPosition()
		imageHeight = self.GetHeight()

		if (jgy + imageHeight) <= pgy or jgy >= (pgy + listboxHeight):
			self.Hide()
			self.SetRenderingRect(0, 0, 0, 0)
		elif jgy < pgy:
			self.Show()
			self.SetRenderingRect(0, ui.calculateRect(imageHeight-abs(jgy-pgy), imageHeight), 0, 0)
		elif jgy+imageHeight > (pgy+listboxHeight-4):
			calculate = (pgy+listboxHeight-4) - (jgy+imageHeight)
			if calculate == 0:
				return
			self.Show()
			self.SetRenderingRect(0.0, 0.0, 0.0, ui.calculateRect(imageHeight-abs(calculate), imageHeight))
		else:
			self.Show()
			self.SetRenderingRect(0, 0, 0, 0)

class SubCategoryItem(ui.ExpandedImageBoxNewShop):
	def __del__(self):
		ui.ExpandedImageBoxNewShop.__del__(self)

	def __init__(self):
		ui.ExpandedImageBoxNewShop.__init__(self)
		self.Destroy()
		self.subCategoryIndex = -1
		self.LoadImage(IMG_DIR+"sub_category_no_selected.png")

	def Destroy(self):
		self.parent = None
		self.subCategoryIndex = 0
		self.subCategoryText = None

	def SetData(self, subCategoryIndex, subCategoryName, subCategoryListBox):
		self.subCategoryIndex = subCategoryIndex
		self.parent = proxy(subCategoryListBox)
		subCategoryText = MultiTextLine()
		subCategoryText.SetParent(self)
		subCategoryText.SetPosition((self.GetWidth()/2)+8, 5)
		subCategoryText.SetTextRange(15)
		subCategoryText.SetTextType("horizontal#center")
		subCategoryText.SetFontName("Arial:14")
		subCategoryText.SetText(subCategoryName)
		subCategoryText.Show()
		self.subCategoryText = subCategoryText

	def GetSubIndex(self):
		return int(self.subCategoryIndex)

	def OnRender(self):
		parent = self.parent
		if parent == None:
			return

		listboxHeight = parent.GetHeight()
		(pgx,pgy) = parent.GetGlobalPosition()
		(igx,igy) = self.subCategoryText.GetGlobalPosition()

		if igy < pgy:
			self.subCategoryText.Hide()
		elif igy > (pgy+listboxHeight-25):
			self.subCategoryText.Hide()
		else:
			self.subCategoryText.Show()

		(jgx,jgy) = self.GetGlobalPosition()
		imageHeight = self.GetHeight()

		if jgy < pgy:
			self.SetRenderingRect(0, ui.calculateRect(imageHeight-abs(jgy-pgy),imageHeight),0,0)
		elif jgy+imageHeight > (pgy+listboxHeight-4):
			calculate = (pgy+listboxHeight-4) - (jgy+imageHeight)
			if calculate == 0:
				return

			self.SetRenderingRect(0.0,0.0,0.0, ui.calculateRect(imageHeight-abs(calculate),imageHeight))
		else:
			self.SetRenderingRect(0,0,0,0)

class ScrollBar(ui.Window):
	SCROLLBAR_WIDTH = 13
	SCROLLBAR_MIDDLE_HEIGHT = 1
	SCROLLBAR_BUTTON_WIDTH = 17
	SCROLLBAR_BUTTON_HEIGHT = 17
	SCROLL_BTN_XDIST = 2
	SCROLL_BTN_YDIST = 2

	class MiddleBar(ui.DragButton):
		def __init__(self):
			ui.DragButton.__init__(self)
			self.AddFlag("movable")
			self.SetWindowName("scrollbar_middlebar")

		def MakeImage(self):
			top = ui.ExpandedImageBoxNewShop()
			top.SetParent(self)
			top.LoadImage(IMG_DIR+"scroll/scroll_top.png")
			top.AddFlag("not_pick")
			top.Show()
			bottom = ui.ExpandedImageBoxNewShop()
			bottom.SetParent(self)
			bottom.LoadImage(IMG_DIR+"scroll/scroll_bottom.png")
			bottom.AddFlag("not_pick")
			bottom.Show()
			middle = ui.ExpandedImageBoxNewShop()
			middle.SetParent(self)
			middle.LoadImage(IMG_DIR+"scroll/scroll_mid.png")
			middle.AddFlag("not_pick")
			middle.Show()
			self.top = top
			self.bottom = bottom
			self.middle = middle

		def SetSize(self, height):
			minHeight = self.top.GetHeight() + self.bottom.GetHeight() + self.middle.GetHeight()
			height = max(minHeight, height)
			ui.DragButton.SetSize(self, 11, height)
			scale = (height - minHeight) / 2 
			extraScale = 0
			if (height - minHeight) % 2 == 1:
				extraScale = 1
			self.middle.SetPosition(0, self.top.GetHeight() + scale)
			self.bottom.SetPosition(0, height - self.bottom.GetHeight())

	def __init__(self):
		ui.Window.__init__(self)

		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = None
		self.eventArgs = None
		self.lockFlag = False

		self.CreateScrollBar()
		self.SetScrollBarSize(0)

		self.scrollStep = 0.03
		self.SetWindowName("NONAME_ScrollBar")

	def __del__(self):
		ui.Window.__del__(self)

	def CreateScrollBar(self):
		topImage = ui.ExpandedImageBoxNewShop()
		topImage.SetParent(self)
		topImage.AddFlag("not_pick")
		topImage.LoadImage(IMG_DIR+"scroll/scrollbar_top.png")
		topImage.Show()
		bottomImage = ui.ExpandedImageBoxNewShop()
		bottomImage.SetParent(self)
		bottomImage.AddFlag("not_pick")
		bottomImage.LoadImage(IMG_DIR+"scroll/scrollbar_bottom.png")
		bottomImage.Show()
		middleImage = ui.ExpandedImageBoxNewShop()
		middleImage.SetParent(self)
		middleImage.AddFlag("not_pick")
		middleImage.SetPosition(0, topImage.GetHeight())
		middleImage.LoadImage(IMG_DIR+"scroll/scrollbar_mid.png")
		middleImage.Show()
		self.topImage = topImage
		self.bottomImage = bottomImage
		self.middleImage = middleImage

		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(ui.__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.MakeImage()
		middleBar.SetSize(0) # set min height
		self.middleBar = middleBar

	def Destroy(self):
		self.eventScroll = None
		self.eventArgs = None

	def SetScrollEvent(self, event, *args):
		self.eventScroll = event
		self.eventArgs = args

	def SetMiddleBarSize(self, pageScale):
		self.middleBar.SetSize(int(pageScale * float(self.GetHeight() - self.SCROLL_BTN_YDIST*2)))
		realHeight = self.GetHeight() - self.SCROLL_BTN_YDIST*2 - self.middleBar.GetHeight()
		self.pageSize = realHeight

	def SetScrollBarSize(self, height):
		self.SetSize(self.SCROLLBAR_WIDTH, height)
		self.pageSize = height - self.SCROLL_BTN_YDIST*2 - self.middleBar.GetHeight()
		middleImageScale = float((height - self.SCROLL_BTN_YDIST*2) - self.middleImage.GetHeight()) / float(self.middleImage.GetHeight())
		self.middleImage.SetRenderingRect(0, 0, 0, middleImageScale)
		self.bottomImage.SetPosition(0, height - self.bottomImage.GetHeight())
		self.middleBar.SetRestrictMovementArea(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST, self.middleBar.GetWidth(), height - self.SCROLL_BTN_YDIST * 2)
		self.middleBar.SetPosition(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST)

	def SetScrollStep(self, step):
		self.scrollStep = step

	def GetScrollStep(self):
		return self.scrollStep

	def GetPos(self):
		return self.curPos

	def OnUp(self):
		self.SetPos(self.curPos-self.scrollStep)

	def OnDown(self):
		self.SetPos(self.curPos+self.scrollStep)

	def SetPos(self, pos, moveEvent = True):
		pos = max(0.0, pos)
		pos = min(1.0, pos)
		newPos = float(self.pageSize) * pos
		self.middleBar.SetPosition(self.SCROLL_BTN_XDIST, int(newPos) + self.SCROLL_BTN_YDIST)
		if moveEvent == True:
			self.OnMove()

	def OnMove(self):
		if self.lockFlag:
			return
		if 0 == self.pageSize:
			return
		(xLocal, yLocal) = self.middleBar.GetLocalPosition()
		self.curPos = float(yLocal - self.SCROLL_BTN_YDIST) / float(self.pageSize)
		if self.eventScroll:
			apply(self.eventScroll, self.eventArgs)

	def OnMouseLeftButtonDown(self):
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		newPos = float(yMouseLocalPosition) / float(self.GetHeight())
		self.SetPos(newPos)

	def LockScroll(self):
		self.lockFlag = True

	def UnlockScroll(self):
		self.lockFlag = False

def NumberToMoneyFormat(n):
	if n <= 0 :
		return "0"
	return "%s" % ('.'.join([ i-3<0 and str(n)[:i] or str(n)[i-3:i] for i in range(len(str(n))%3, len(str(n))+1, 3) if i ]))

class MultiTextLine(ui.Window):
	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.children = []
		self.rangeText = 0

	def __init__(self):
		ui.Window.__init__(self)
		self.children = []
		self.rangeText = 15
		self.textType = ""
		self.fontName = ""
		self.outline = False
		self.rgb = (0,0,0)

	def SetFontColor(self, r, g, b):
		self.rgb = (r, g, b)
		for text in self.children:
			if self.rgb[0] != 0:
				text.SetFontColor(self.rgb[0],self.rgb[1],self.rgb[2])

	def SetOutline(self, flag):
		self.outline = flag
		for text in self.children:
			if self.outline:
				text.SetOutline()

	def SetTextType(self, textType):
		self.textType = textType
		for text in self.children:
			self.AddTextType(self.textType.split("#"),text)

	def SetFontName(self, fontName):
		self.fontName = fontName
		for text in self.children:
			text.SetFontName(fontName)

	def GetTextSize(self, index = 0):
		if len(self.children) == 0:
			return (0,0)
		elif index >= len(self.children):
			return (0,0)
		return self.children[index].GetTextSize()

	def SetTextRange(self, range):
		self.rangeText = range
		yPosition = 0
		for text in self.children:
			text.SetPosition(0, yPosition)
			yPosition+=self.rangeText

	def AddTextType(self, typeArg, text):
		if len(typeArg) > 1:
			if typeArg[0] == "vertical":
				if typeArg[1] == "top":
					text.SetVerticalAlignTop()
				elif typeArg[1] == "bottom":
					text.SetVerticalAlignBottom()
				elif typeArg[1] == "center":
					text.SetVerticalAlignCenter()
			elif typeArg[0] == "horizontal":
				if typeArg[1] == "left":
					text.SetHorizontalAlignLeft()
				elif typeArg[1] == "right":
					text.SetHorizontalAlignRight()
				elif typeArg[1] == "center":
					text.SetHorizontalAlignCenter()

	def SetText(self, cmd):
		if len(self.children) > 1:
			self.children=[]
		multi_arg = cmd.split("\n")
		yPosition = 0
		for text in multi_arg:
			childText = ui.TextLine()
			childText.SetParent(self)
			childText.SetPosition(0, yPosition)
			if self.rgb[0] != 0:
				childText.SetFontColor(self.rgb[0],self.rgb[1],self.rgb[2])
			if self.textType != "":
				self.AddTextType(self.textType.split("#"),childText)
			if self.fontName != "":
				childText.SetFontName(self.fontName)
			if self.outline:
				childText.SetOutline()
			childText.SetText(str(text))
			childText.Show()
			self.children.append(childText)
			yPosition+=self.rangeText

class ListBox(ui.Window):
	def __init__(self, isHorizontal = False):
		ui.Window.__init__(self)
		self.viewItemCount=10
		self.basePos=0
		self.itemHeight=16
		self.itemStep=20
		self.itemList=[]
		self.itemWidth=100
		self.scrollBar=None
		self.isHorizontal= isHorizontal

	def __del__(self):
		ui.Window.__del__(self)

	def __GetItemCount(self):
		return len(self.itemList)

	def SetItemStep(self, itemStep):
		self.itemStep=itemStep

	def SetItemSize(self, itemWidth, itemHeight):
		self.itemWidth=itemWidth
		self.itemHeight=itemHeight

	def SetViewItemCount(self, viewItemCount):
		self.viewItemCount=viewItemCount

	def RemoveAllItems(self):
		for item in self.itemList:
			item.Destroy()
		self.itemList = []
		if self.scrollBar:
			self.scrollBar.SetPos(0)

	def GetItems(self):
		return self.itemList

	def GetItemCount(self):
		return len(self.itemList)

	def RemoveItem(self, delItem):
		self.itemList.remove(delItem)

	def AppendItem(self, newItem):
		self.itemList.append(newItem)
		if app.ENABLE_MOUSEWHEEL_EVENT:
			newItem.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)

	def SetScrollBar(self, scrollBar):
		scrollBar.SetScrollEvent(ui.__mem_func__(self.__OnScroll))
		self.scrollBar = scrollBar
		if app.ENABLE_MOUSEWHEEL_EVENT:
			self.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)

	if app.ENABLE_MOUSEWHEEL_EVENT:
		def OnMouseWheelScroll_ScrollBar(self,mode):
			if self.scrollBar:
				if mode == "UP":
					self.scrollBar.OnUp()
				else:
					self.scrollBar.OnDown()

	def OnMouseWheel(self, nLen):
		if self.scrollBar:
			if self.scrollBar.IsShow():
				if nLen > 0:
					self.scrollBar.OnUp()
				else:
					self.scrollBar.OnDown()
				return True
		return False

	def __OnScroll(self):
		self.SetBasePos(int(self.scrollBar.GetPos()*self.__GetScrollLen()))

	def __GetScrollLen(self):
		if self.__GetItemCount() == 0:
			return 0

		(lx,ly) = self.itemList[len(self.itemList)-1].exPos
		return ly

	def Render(self,basePos):
		for item in self.itemList:
			(ex,ey) = item.exPos

			if self.isHorizontal:
				item.SetPosition(ex-(basePos), ey)
			else:
				item.SetPosition(ex, ey-(basePos))
			item.OnRender()

	def SetBasePos(self, basePos):
		if self.basePos == basePos:
			return
		self.Render(basePos)
		self.basePos=basePos

class ImageBoxSpecial(ui.Window):
	def __del__(self):
		ui.Window.__del__(self)

	def Destroy(self):
		self.imageList=[]
		self.waitingTime = 0.0
		self.sleepTime = 0.0
		self.alphaValue = 0.0
		self.increaseValue = 0.0
		self.minAlpha = 0.0
		self.maxAlpha = 0.0
		self.alphaStatus = False
		self.imageIndex = 0
		self.img = None
		self.numberText = None

	def __init__(self):
		ui.Window.__init__(self)
		self.Destroy()
		self.waitingTime = 2.0
		self.alphaValue = 0.3
		self.increaseValue = 0.05
		self.minAlpha = 0.3
		self.maxAlpha = 1.0

	def SetImage(self, folder, itemVnum, itemCount):
		(x, y) = (0,0)

		if self.img != None:
			(x, y) = self.img.GetLocalPosition()

		if self.img == None:
			img = ui.ImageBox()
			img.SetParent(self)
			img.SAFE_SetStringEvent("MOUSE_OVER_OUT",self.OverOutItem)
			img.SAFE_SetStringEvent("MOUSE_OVER_IN",self.OverInItem)
			self.img = img

		if self.numberText == None:
			numberText = ui.NumberLine()
			numberText.SetParent(self.img)
			numberText.SetPosition(20, 20)
			self.numberText = numberText

		self.numberText.SetNumber(str(itemCount))
		self.numberText.Show()

		self.img.LoadImage(folder)
		self.img.SetPosition(x, y)
		self.img.Show()

	def OverOutItem(self):
		interface = constInfo.GetInterfaceInstance()
		if interface:
			if interface.tooltipItem:
				interface.tooltipItem.HideToolTip()

	def OverInItem(self):
		interface = constInfo.GetInterfaceInstance()
		if interface:
			if interface.tooltipItem:
				interface.tooltipItem.SetItemToolTip(self.imageList[self.imageIndex][1])

	def Clear(self):
		self.img = None
		self.numberText = None
		self.imageList = []

	def LoadImage(self, imageFolder, itemVnum, itemCount):
		item_list = [imageFolder, itemVnum, itemCount]
		if item_list in self.imageList:
			return

		self.imageList.append(item_list)
		if self.img == None:
			self.SetImage(imageFolder, itemVnum, itemCount)

	def GetNextImage(self, listIndex):
		if listIndex >= len(self.imageList):
			if len(self.imageList) > 0:
				return (0,self.imageList[0][0],self.imageList[0][1],self.imageList[0][2])
			return (0,"",0,0)
		return (listIndex, self.imageList[listIndex][0],self.imageList[listIndex][0], self.imageList[listIndex][2])

	def OnUpdate(self):
		if len(self.imageList) <= 1:
			self.imageIndex=0
			return
		elif self.sleepTime > app.GetTime():
			return

		if self.alphaStatus == True:
			self.alphaValue -= self.increaseValue
			if self.alphaValue < self.minAlpha:
				self.alphaValue = self.minAlpha
				self.alphaStatus = False
				(imageIndex, imageFolder, itemVnum, itemCount) = self.GetNextImage(self.imageIndex+1)
				if imageFolder != "":
					self.SetImage(imageFolder, itemVnum, itemCount)
				self.imageIndex = imageIndex
		else:
			self.alphaValue += self.increaseValue
			if self.alphaValue > self.maxAlpha:
				self.alphaStatus = True
				self.sleepTime = app.GetTime()+self.waitingTime

		if self.img != None:
			self.img.SetAlpha(self.alphaValue)
