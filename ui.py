import app
import ime
import grp
import snd
import wndMgr
import item
import skill
import localeInfo
import dbg
# MARK_BUG_FIX
import guild
# END_OF_MARK_BUG_FIX
import constInfo

from _weakref import proxy

BACKGROUND_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
DARK_COLOR = grp.GenerateColor(0.2, 0.2, 0.2, 1.0)
BRIGHT_COLOR = grp.GenerateColor(0.7, 0.7, 0.7, 1.0)

if localeInfo.IsCANADA():
	SELECT_COLOR = grp.GenerateColor(0.9, 0.03, 0.01, 0.4)
else:
	SELECT_COLOR = grp.GenerateColor(0.0, 0.0, 0.5, 0.3)

WHITE_COLOR = grp.GenerateColor(1.0, 1.0, 1.0, 0.5)
HALF_WHITE_COLOR = grp.GenerateColor(1.0, 1.0, 1.0, 0.2)

createToolTipWindowDict = {}
def RegisterCandidateWindowClass(codePage, candidateWindowClass):
	EditLine.candidateWindowClassDict[codePage]=candidateWindowClass
def RegisterToolTipWindow(type, createToolTipWindow):
	createToolTipWindowDict[type]=createToolTipWindow

app.SetDefaultFontName(localeInfo.UI_DEF_FONT)

## Window Manager Event List##
##############################
## "OnMouseLeftButtonDown"
## "OnMouseLeftButtonUp"
## "OnMouseLeftButtonDoubleClick"
## "OnMouseRightButtonDown"
## "OnMouseRightButtonUp"
## "OnMouseRightButtonDoubleClick"
## "OnMouseDrag"
## "OnSetFocus"
## "OnKillFocus"
## "OnMouseOverIn"
## "OnMouseOverOut"
## "OnRender"
## "OnUpdate"
## "OnKeyDown"
## "OnKeyUp"
## "OnTop"
## "OnIMEUpdate" ## IME Only
## "OnIMETab"	## IME Only
## "OnIMEReturn" ## IME Only
##############################
## Window Manager Event List##


class __mem_func__:
	class __noarg_call__:
		def __init__(self, cls, obj, func):
			self.cls=cls
			self.obj=proxy(obj)
			self.func=proxy(func)

		def __call__(self, *arg):
			return self.func(self.obj)

	class __arg_call__:
		def __init__(self, cls, obj, func):
			self.cls=cls
			self.obj=proxy(obj)
			self.func=proxy(func)

		def __call__(self, *arg):
			return self.func(self.obj, *arg)

	def __init__(self, mfunc):
		if mfunc.im_func.func_code.co_argcount>1:
			self.call=__mem_func__.__arg_call__(mfunc.im_class, mfunc.im_self, mfunc.im_func)
		else:
			self.call=__mem_func__.__noarg_call__(mfunc.im_class, mfunc.im_self, mfunc.im_func)

	def __call__(self, *arg):
		return self.call(*arg)

class Window(object):
	def NoneMethod(cls):
		pass

	NoneMethod = classmethod(NoneMethod)

	def __init__(self, layer = "UI"):
		self.hWnd = None
		self.parentWindow = 0
		self.exPos = (0,0)
		self.onMouseLeftButtonUpEvent = None

		if app.ENABLE_MOUSEWHEEL_EVENT:
			self.onMouseWheelScrollEvent = None

		if app.ENABLE_MOUSEWHEEL_EVENT_OLD:
			self.onRunMouseWheelEvent = None

		if app.ENABLE_SEND_TARGET_INFO:
			self.mouseLeftButtonDownEvent = None
			self.mouseLeftButtonDownArgs = None
			self.mouseLeftButtonUpEvent = None
			self.mouseLeftButtonUpArgs = None
			self.mouseLeftButtonDoubleClickEvent = None
			self.mouseRightButtonDownEvent = None
			self.mouseRightButtonDownArgs = None
			self.moveWindowEvent = None
			self.renderEvent = None
			self.renderArgs = None

			self.overInEvent = None
			self.overInArgs = None

			self.overOutEvent = None
			self.overOutArgs = None

			self.baseX = 0
			self.baseY = 0
		self.RegisterWindow(layer)
		self.exPos = (0,0)
		self.Hide()

	def __del__(self):
		wndMgr.Destroy(self.hWnd)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.Register(self, layer)

	def Destroy(self):
		pass

	def GetWindowHandle(self):
		return self.hWnd

	def AddFlag(self, style):
		wndMgr.AddFlag(self.hWnd, style)

	def IsRTL(self):
		return wndMgr.IsRTL(self.hWnd)

	def SetWindowName(self, Name):
		wndMgr.SetName(self.hWnd, Name)

	def GetWindowName(self):
		return wndMgr.GetName(self.hWnd)

	if app.ENABLE_SEND_TARGET_INFO:
		def GetLeft(self):
			x, y = self.GetLocalPosition()
			return x

		def SetParent(self, parent):
			if parent:
				wndMgr.SetParent(self.hWnd, parent.hWnd)
			else:
				wndMgr.SetParent(self.hWnd, 0)

	if app.__BL_CLIP_MASK__:	
		def SetClippingMaskRect(self, left, top, right, bottom):
			wndMgr.SetClippingMaskRect(self.hWnd, left, top, right, bottom)
			
		def SetClippingMaskWindow(self, clipping_mask_window):
			wndMgr.SetClippingMaskWindow(self.hWnd, clipping_mask_window.hWnd)
		def SetVisible(self, is_show):
			if is_show:
				self.Show()
			else:
				self.Hide()

		def GetGlobalLeft(self):
			x, y = self.GetGlobalPosition()
			return x

		def GetTop(self):
			x, y = self.GetLocalPosition()
			return y

		def GetGlobalTop(self):
			x, y = self.GetGlobalPosition()
			return y

		def GetRight(self):
			return self.GetLeft() + self.GetWidth()

		def GetBottom(self):
			return self.GetTop() + self.GetHeight()

		def SetAttachParent(self, parent):
			wndMgr.SetAttachParent(self.hWnd, parent.hWnd)

		def SetLeft(self, x):
			wndMgr.SetWindowPosition(self.hWnd, x, self.GetTop())

		def SavePosition(self):
			self.baseX = self.GetLeft()
			self.baseY = self.GetTop()

		def IsInPosition(self):
			xMouse, yMouse = wndMgr.GetMousePosition()
			x, y = self.GetGlobalPosition()
			return xMouse >= x and xMouse < x + self.GetWidth() and yMouse >= y and yMouse < y + self.GetHeight()

		def SetMouseLeftButtonDownEvent(self, event, *args):
			self.mouseLeftButtonDownEvent = event
			self.mouseLeftButtonDownArgs = args

		def OnMouseLeftButtonDown(self):
			if self.mouseLeftButtonDownEvent:
				apply(self.mouseLeftButtonDownEvent, self.mouseLeftButtonDownArgs)

		def SetMouseLeftButtonDoubleClickEvent(self, event):
			self.mouseLeftButtonDoubleClickEvent = event

		def OnMouseLeftButtonDoubleClick(self):
			if self.mouseLeftButtonDoubleClickEvent:
				self.mouseLeftButtonDoubleClickEvent()

		def SetMouseRightButtonDownEvent(self, event, *args):
			self.mouseRightButtonDownEvent = event
			self.mouseRightButtonDownArgs = args

		def OnMouseRightButtonDown(self):
			if self.mouseRightButtonDownEvent:
				apply(self.mouseRightButtonDownEvent, self.mouseRightButtonDownArgs)

		def SetMoveWindowEvent(self, event):
			self.moveWindowEvent = event

		def OnMoveWindow(self, x, y):
			if self.moveWindowEvent:
				self.moveWindowEvent(x, y)

		def SAFE_SetOverInEvent(self, func, *args):
			self.overInEvent = __mem_func__(func)
			self.overInArgs = args

		def SetOverInEvent(self, func, *args):
			self.overInEvent = func
			self.overInArgs = args

		def SAFE_SetOverOutEvent(self, func, *args):
			self.overOutEvent = __mem_func__(func)
			self.overOutArgs = args

		def SetOverOutEvent(self, func, *args):
			self.overOutEvent = func
			self.overOutArgs = args

		def OnMouseOverIn(self):
			if self.overInEvent:
				apply(self.overInEvent, self.overInArgs)

		def OnMouseOverOut(self):
			if self.overOutEvent:
				apply(self.overOutEvent, self.overOutArgs)

		def SAFE_SetRenderEvent(self, event, *args):
			self.renderEvent = __mem_func__(event)
			self.renderArgs = args

		def ClearRenderEvent(self):
			self.renderEvent = None
			self.renderArgs = None

		def OnRender(self):
			if self.renderEvent:
				apply(self.renderEvent, self.renderArgs)

		def SetMouseLeftButtonUpEvent(self, event, *args):
			self.mouseLeftButtonUpEvent = event
			self.mouseLeftButtonUpArgs = args
	else:
		def SetParent(self, parent):
			wndMgr.SetParent(self.hWnd, parent.hWnd)

	def SetParentProxy(self, parent):
		self.parentWindow=proxy(parent)
		wndMgr.SetParent(self.hWnd, parent.hWnd)

	def GetParentProxy(self):
		return self.parentWindow

	def SetPickAlways(self):
		wndMgr.SetPickAlways(self.hWnd)

	def SetWindowHorizontalAlignLeft(self):
		wndMgr.SetWindowHorizontalAlign(self.hWnd, wndMgr.HORIZONTAL_ALIGN_LEFT)

	def SetWindowHorizontalAlignCenter(self):
		wndMgr.SetWindowHorizontalAlign(self.hWnd, wndMgr.HORIZONTAL_ALIGN_CENTER)

	def SetWindowHorizontalAlignRight(self):
		wndMgr.SetWindowHorizontalAlign(self.hWnd, wndMgr.HORIZONTAL_ALIGN_RIGHT)

	def SetWindowVerticalAlignTop(self):
		wndMgr.SetWindowVerticalAlign(self.hWnd, wndMgr.VERTICAL_ALIGN_TOP)

	def SetWindowVerticalAlignCenter(self):
		wndMgr.SetWindowVerticalAlign(self.hWnd, wndMgr.VERTICAL_ALIGN_CENTER)

	def SetWindowVerticalAlignBottom(self):
		wndMgr.SetWindowVerticalAlign(self.hWnd, wndMgr.VERTICAL_ALIGN_BOTTOM)

	def SetTop(self):
		wndMgr.SetTop(self.hWnd)

	def Show(self):
		wndMgr.Show(self.hWnd)

	def Hide(self):
		wndMgr.Hide(self.hWnd)

	def Lock(self):
		wndMgr.Lock(self.hWnd)

	def Unlock(self):
		wndMgr.Unlock(self.hWnd)

	def IsShow(self):
		return wndMgr.IsShow(self.hWnd)

	def UpdateRect(self):
		wndMgr.UpdateRect(self.hWnd)

	def SetSize(self, width, height):
		wndMgr.SetWindowSize(self.hWnd, width, height)

	def GetWidth(self):
		return wndMgr.GetWindowWidth(self.hWnd)

	def GetHeight(self):
		return wndMgr.GetWindowHeight(self.hWnd)

	def GetLocalPosition(self):
		return wndMgr.GetWindowLocalPosition(self.hWnd)

	def GetGlobalPosition(self):
		return wndMgr.GetWindowGlobalPosition(self.hWnd)

	def GetMouseLocalPosition(self):
		return wndMgr.GetMouseLocalPosition(self.hWnd)

	def GetRect(self):
		return wndMgr.GetWindowRect(self.hWnd)

	def SetPosition(self, x, y, bForce = False, flag = False):
		wndMgr.SetWindowPosition(self.hWnd, x, y,bForce)

		if flag == True:
			self.exPos = (x,y)

	def SetMouseOverInEvent(self, event, *args):
		self.mouseOverInEvent = event
		self.mouseOverInArgs = args

	def SetMouseOverOutEvent(self, event, *args):
		self.mouseOverOutEvent = event
		self.mouseOverOutArgs = args

	def SetCenterPosition(self, x = 0, y = 0):
		self.SetPosition((wndMgr.GetScreenWidth() - self.GetWidth()) / 2 + x, (wndMgr.GetScreenHeight() - self.GetHeight()) / 2 + y)

	def IsFocus(self):
		return wndMgr.IsFocus(self.hWnd)

	def SetFocus(self):
		wndMgr.SetFocus(self.hWnd)

	def KillFocus(self):
		wndMgr.KillFocus(self.hWnd)

	def GetChildCount(self):
		return wndMgr.GetChildCount(self.hWnd)

	def IsIn(self):
		return wndMgr.IsIn(self.hWnd)

	def SetOnMouseLeftButtonUpEvent(self, event):
		self.onMouseLeftButtonUpEvent = event

	def OnMouseLeftButtonUp(self):
		if self.onMouseLeftButtonUpEvent:
			self.onMouseLeftButtonUpEvent()

	if app.ENABLE_MOUSEWHEEL_EVENT:
		def SetMouseWheelScrollEvent(self, event):
			self.onMouseWheelScrollEvent = event
			wndMgr.SetScrollable(self.hWnd)

		def OnMouseWheelScroll(self, mode = "UP"): #mode could be value "UP" and "DOWN"
			print("OnMouseWheelScroll")
			if self.onMouseWheelScrollEvent:
				self.onMouseWheelScrollEvent(mode)

	if app.ENABLE_MOUSEWHEEL_EVENT_OLD:
		def OnRunMouseWheel(self, nLen):
			if not self.onRunMouseWheelEvent:
					return False

			apply(self.onRunMouseWheelEvent, (bool(nLen < 0), ))
			return True

		def SetOnRunMouseWheelEvent(self, event):
			self.onRunMouseWheelEvent = __mem_func__(event)	

class ListBoxEx(Window):

	class Item(Window):
		def __init__(self):
			Window.__init__(self)

		def __del__(self):
			Window.__del__(self)

		def SetParent(self, parent):
			Window.SetParent(self, parent)
			self.parent=proxy(parent)

		def OnMouseLeftButtonDown(self):
			self.parent.SelectItem(self)

		def OnRender(self):
			if self.parent.GetSelectedItem()==self:
				self.OnSelectedRender()

		def OnSelectedRender(self):
			x, y = self.GetGlobalPosition()
			grp.SetColor(grp.GenerateColor(0.0, 0.0, 0.7, 0.7))
			grp.RenderBar(x, y, self.GetWidth(), self.GetHeight())

	def __init__(self):
		Window.__init__(self)

		self.viewItemCount=10
		self.basePos=0
		self.itemHeight=16
		self.itemStep=20
		self.selItem=0
		self.itemList=[]
		self.onSelectItemEvent = lambda *arg: None

		if localeInfo.IsARABIC():
			self.itemWidth=130
		else:
			self.itemWidth=100

		self.scrollBar=None
		self.__UpdateSize()

	def __del__(self):
		Window.__del__(self)

	def __UpdateSize(self):
		height=self.itemStep*self.__GetViewItemCount()

		self.SetSize(self.itemWidth, height)

	def IsEmpty(self):
		if len(self.itemList)==0:
			return 1
		return 0

	def SetItemStep(self, itemStep):
		self.itemStep=itemStep
		self.__UpdateSize()

	def SetItemSize(self, itemWidth, itemHeight):
		self.itemWidth=itemWidth
		self.itemHeight=itemHeight
		self.__UpdateSize()

	def SetViewItemCount(self, viewItemCount):
		self.viewItemCount=viewItemCount

	def SetSelectEvent(self, event):
		self.onSelectItemEvent = event

	def SetBasePos(self, basePos):
		for oldItem in self.itemList[self.basePos:self.basePos+self.viewItemCount]:
			oldItem.Hide()

		self.basePos=basePos

		pos=basePos
		for newItem in self.itemList[self.basePos:self.basePos+self.viewItemCount]:
			(x, y)=self.GetItemViewCoord(pos, newItem.GetWidth())
			newItem.SetPosition(x, y)
			newItem.Show()
			pos+=1

	def GetItemIndex(self, argItem):
		return self.itemList.index(argItem)

	def GetSelectedItem(self):
		return self.selItem

	def SelectIndex(self, index):

		if index >= len(self.itemList) or index < 0:
			self.selItem = None
			return

		try:
			self.selItem=self.itemList[index]
		except:
			pass

	def SelectItem(self, selItem):
		self.selItem=selItem
		self.onSelectItemEvent(selItem)

	def RemoveAllItems(self):
		self.selItem=None
		self.itemList=[]

		if self.scrollBar:
			self.scrollBar.SetPos(0)

	def RemoveItem(self, delItem):
		if delItem==self.selItem:
			self.selItem=None

		self.itemList.remove(delItem)

	def AppendItem(self, newItem):
		newItem.SetParent(self)
		newItem.SetSize(self.itemWidth, self.itemHeight)

		pos=len(self.itemList)
		if self.__IsInViewRange(pos):
			(x, y)=self.GetItemViewCoord(pos, newItem.GetWidth())
			newItem.SetPosition(x, y)
			newItem.Show()
		else:
			newItem.Hide()

		self.itemList.append(newItem)

	def SetScrollBar(self, scrollBar):
		scrollBar.SetScrollEvent(__mem_func__(self.__OnScroll))
		self.scrollBar=scrollBar

	def __OnScroll(self):
		self.SetBasePos(int(self.scrollBar.GetPos()*self.__GetScrollLen()))

	def __GetScrollLen(self):
		scrollLen=self.__GetItemCount()-self.__GetViewItemCount()
		if scrollLen<0:
			return 0

		return scrollLen

	def __GetViewItemCount(self):
		return self.viewItemCount

	def __GetItemCount(self):
		return len(self.itemList)

	def GetItemViewCoord(self, pos, itemWidth):
		if localeInfo.IsARABIC():
			return (self.GetWidth()-itemWidth-10, (pos-self.basePos)*self.itemStep)
		else:
			return (0, (pos-self.basePos)*self.itemStep)

	def __IsInViewRange(self, pos):
		if pos<self.basePos:
			return 0
		if pos>=self.basePos+self.viewItemCount:
			return 0
		return 1

	if app.ENABLE_SWITCHBOT:
		def GetItems(self):
			return self.itemList
			
if app.ENABLE_SEND_TARGET_INFO:
	class ListBoxExNew(Window):
		class Item(Window):
			def __init__(self):
				Window.__init__(self)

				self.realWidth = 0
				self.realHeight = 0

				self.removeTop = 0
				self.removeBottom = 0

				self.SetWindowName("NONAME_ListBoxExNew_Item")
				#Window.SetSize(100,15)
				self.SetSize(100,15)

				self.realWidth = 100
				self.realHeight = 15

			def __del__(self):
				Window.__del__(self)

			def SetParent(self, parent):
				Window.SetParent(self, parent)
				self.parent=proxy(parent)

			def SetSize(self, width, height):
				self.realWidth = width
				self.realHeight = height
				Window.SetSize(self, width, height)

			def SetRemoveTop(self, height):
				self.removeTop = height
				self.RefreshHeight()

			def SetRemoveBottom(self, height):
				self.removeBottom = height
				self.RefreshHeight()

			def SetCurrentHeight(self, height):
				Window.SetSize(self, self.GetWidth(), height)

			def GetCurrentHeight(self):
				return Window.GetHeight(self)

			def ResetCurrentHeight(self):
				self.removeTop = 0
				self.removeBottom = 0
				self.RefreshHeight()

			def RefreshHeight(self):
				self.SetCurrentHeight(self.GetHeight() - self.removeTop - self.removeBottom)

			def GetHeight(self):
				return self.realHeight

		def __init__(self, stepSize, viewSteps):
			Window.__init__(self)

			self.viewItemCount=10
			self.basePos=0
			self.baseIndex=0
			self.maxSteps=0
			self.viewSteps = viewSteps
			self.stepSize = stepSize
			self.itemList=[]

			self.scrollBar=None

			self.SetWindowName("NONAME_ListBoxEx")

		def __del__(self):
			Window.__del__(self)

		def IsEmpty(self):
			if len(self.itemList)==0:
				return 1
			return 0

		def __CheckBasePos(self, pos):
			self.viewItemCount = 0

			start_pos = pos

			height = 0
			while height < self.GetHeight():
				if pos >= len(self.itemList):
					return start_pos == 0
				height += self.itemList[pos].GetHeight()
				pos += 1
				self.viewItemCount += 1
			return height == self.GetHeight()

		def SetBasePos(self, basePos, forceRefresh = True):
			if forceRefresh == False and self.basePos == basePos:
				return

			for oldItem in self.itemList[self.baseIndex:self.baseIndex+self.viewItemCount]:
				oldItem.ResetCurrentHeight()
				oldItem.Hide()

			self.basePos=basePos

			baseIndex = 0
			while basePos > 0:
				basePos -= self.itemList[baseIndex].GetHeight() / self.stepSize
				if basePos < 0:
					self.itemList[baseIndex].SetRemoveTop(self.stepSize * abs(basePos))
					break
				baseIndex += 1
			self.baseIndex = baseIndex

			stepCount = 0
			self.viewItemCount = 0
			while baseIndex < len(self.itemList):
				stepCount += self.itemList[baseIndex].GetCurrentHeight() / self.stepSize
				self.viewItemCount += 1
				if stepCount > self.viewSteps:
					self.itemList[baseIndex].SetRemoveBottom(self.stepSize * (stepCount - self.viewSteps))
					break
				elif stepCount == self.viewSteps:
					break
				baseIndex += 1

			y = 0
			for newItem in self.itemList[self.baseIndex:self.baseIndex+self.viewItemCount]:
				newItem.SetPosition(0, y)
				newItem.Show()
				y += newItem.GetCurrentHeight()

		def GetItemIndex(self, argItem):
			return self.itemList.index(argItem)

		def GetSelectedItem(self):
			return self.selItem

		def GetSelectedItemIndex(self):
			return self.selItemIdx

		def RemoveAllItems(self):
			self.itemList=[]
			self.maxSteps=0

			if self.scrollBar:
				self.scrollBar.SetPos(0)

		def RemoveItem(self, delItem):
			self.maxSteps -= delItem.GetHeight() / self.stepSize
			self.itemList.remove(delItem)

		def AppendItem(self, newItem):
			if newItem.GetHeight() % self.stepSize != 0:
				import dbg
				dbg.TraceError("Invalid AppendItem height %d stepSize %d" % (newItem.GetHeight(), self.stepSize))
				return

			self.maxSteps += newItem.GetHeight() / self.stepSize
			newItem.SetParent(self)
			self.itemList.append(newItem)

		def SetScrollBar(self, scrollBar):
			scrollBar.SetScrollEvent(__mem_func__(self.__OnScroll))
			self.scrollBar=scrollBar

		def __OnScroll(self):
			self.SetBasePos(int(self.scrollBar.GetPos()*self.__GetScrollLen()), False)

		def __GetScrollLen(self):
			scrollLen=self.maxSteps-self.viewSteps
			if scrollLen<0:
				return 0

			return scrollLen

		def __GetViewItemCount(self):
			return self.viewItemCount

		def __GetItemCount(self):
			return len(self.itemList)

		def GetViewItemCount(self):
			return self.viewItemCount

		def GetItemCount(self):
			return len(self.itemList)


class ListBoxNew(Window):
	def __del__(self):
		Window.__del__(self)
	def Destroy(self):
		for item in self.itemList:
			item.Destroy()
		self.itemList=[]
		self.scrollBar=None
		self.basePos=0
		self.scrollLen=0
		self.scrollLenExtra=0
		self.isHorizontal= 0
	def __init__(self, isHorizontal = False):
		Window.__init__(self)
		self.itemList=[]
		self.Destroy()
		self.isHorizontal= isHorizontal
	def RemoveAllItems(self):
		for item in self.itemList:
			item.Destroy()
		self.itemList=[]
		if self.scrollBar:
			self.scrollBar.SetPos(0)
		self.RefreshAll()
	def SetExtraScrollLen(self, extraLen):
		self.scrollLenExtra=extraLen
	def GetItems(self):
		return self.itemList
	def AppendItem(self, newItem):
		self.itemList.append(newItem)
	def SetScrollBar(self, scrollBar):
		scrollBar.SetScrollEvent(__mem_func__(self.__OnScroll))
		self.scrollBar=scrollBar
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
		self.SetBasePos(int(self.scrollBar.GetPos()*self.scrollLen))
	def RefreshAll(self):
		windowHeight = self.GetHeight()
		scrollBar = self.scrollBar
		screenSize = 0
		for child in self.itemList:
			if child.exPos[1] > screenSize:
				screenSize = child.exPos[1]
		if screenSize > windowHeight:
			scrollLen = screenSize-windowHeight
			if scrollLen != 0:
				scrollLen += self.scrollLenExtra
			self.scrollLen = scrollLen
			scrollBar.SetMiddleBarSize(float(windowHeight-5)/float(screenSize))
		else:
			scrollBar.SetMiddleBarSize(1.0)
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

class CandidateListBox(ListBoxEx):

	HORIZONTAL_MODE = 0
	VERTICAL_MODE = 1

	class Item(ListBoxEx.Item):
		def __init__(self, text):
			ListBoxEx.Item.__init__(self)

			self.textBox=TextLine()
			self.textBox.SetParent(self)
			self.textBox.SetText(text)
			self.textBox.Show()

		def __del__(self):
			ListBoxEx.Item.__del__(self)

	def __init__(self, mode = HORIZONTAL_MODE):
		ListBoxEx.__init__(self)
		self.itemWidth=32
		self.itemHeight=32
		self.mode = mode

	def __del__(self):
		ListBoxEx.__del__(self)

	def SetMode(self, mode):
		self.mode = mode

	def AppendItem(self, newItem):
		ListBoxEx.AppendItem(self, newItem)

	def GetItemViewCoord(self, pos):
		if self.mode == self.HORIZONTAL_MODE:
			return ((pos-self.basePos)*self.itemStep, 0)
		elif self.mode == self.VERTICAL_MODE:
			return (0, (pos-self.basePos)*self.itemStep)

class TextLine(Window):
	def __init__(self):
		Window.__init__(self)
		self.max = 0
		self.SetFontName(localeInfo.UI_DEF_FONT)

	def __del__(self):
		Window.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterTextLine(self, layer)

	def SetMax(self, max):
		wndMgr.SetMax(self.hWnd, max)

	def SetLimitWidth(self, width):
		wndMgr.SetLimitWidth(self.hWnd, width)

	def SetMultiLine(self):
		wndMgr.SetMultiLine(self.hWnd, TRUE)

	def SetHorizontalAlignArabic(self):
		wndMgr.SetHorizontalAlign(self.hWnd, wndMgr.TEXT_HORIZONTAL_ALIGN_ARABIC)

	def SetHorizontalAlignLeft(self):
		wndMgr.SetHorizontalAlign(self.hWnd, wndMgr.TEXT_HORIZONTAL_ALIGN_LEFT)

	def SetHorizontalAlignRight(self):
		wndMgr.SetHorizontalAlign(self.hWnd, wndMgr.TEXT_HORIZONTAL_ALIGN_RIGHT)

	def SetHorizontalAlignCenter(self):
		wndMgr.SetHorizontalAlign(self.hWnd, wndMgr.TEXT_HORIZONTAL_ALIGN_CENTER)

	def SetVerticalAlignTop(self):
		wndMgr.SetVerticalAlign(self.hWnd, wndMgr.TEXT_VERTICAL_ALIGN_TOP)

	def SetVerticalAlignBottom(self):
		wndMgr.SetVerticalAlign(self.hWnd, wndMgr.TEXT_VERTICAL_ALIGN_BOTTOM)

	def SetVerticalAlignCenter(self):
		wndMgr.SetVerticalAlign(self.hWnd, wndMgr.TEXT_VERTICAL_ALIGN_CENTER)

	def SetSecret(self, Value=TRUE):
		wndMgr.SetSecret(self.hWnd, Value)

	def SetOutline(self, Value=TRUE):
		wndMgr.SetOutline(self.hWnd, Value)

	def SetFeather(self, value=TRUE):
		wndMgr.SetFeather(self.hWnd, value)

	def SetFontName(self, fontName):
		wndMgr.SetFontName(self.hWnd, fontName)

	def SetDefaultFontName(self):
		wndMgr.SetFontName(self.hWnd, localeInfo.UI_DEF_FONT)

	def SetFontColor(self, red, green, blue):
		wndMgr.SetFontColor(self.hWnd, red, green, blue)

	def SetPackedFontColor(self, color):
		wndMgr.SetFontColor(self.hWnd, color)

	def SetText(self, text):
		wndMgr.SetText(self.hWnd, text)

	def SetAllAlign(self):
		self.SetHorizontalAlignCenter()
		self.SetVerticalAlignCenter()
		self.SetWindowHorizontalAlignCenter()
		self.SetWindowVerticalAlignCenter()

	def GetText(self):
		return wndMgr.GetText(self.hWnd)

	def __GetNumberText(self, text):
		try:
			text = text.replace("k", "000")
			return int(text)
		except:
			return 0

	def GetNumberText(self):
		text = self.GetText()
		if not text:
			if self.overLay.GetText():
				return self.__GetNumberText(self.overLay.GetText())
			else:
				return 0
		return self.__GetNumberText(text)

	def GetTextSize(self):
		return wndMgr.GetTextSize(self.hWnd)

	if app.ENABLE_IKASHOP_RENEWAL:
		def FitText(self):
			self.SetSize(*self.GetTextSize())

	def GetTextWidth(self):
		width, height = self.GetTextSize()
		return width

	def SetTextColor(self, color):
		self.SetPackedFontColor(color)

class TextLineNew(Window):
	def __init__(self):
		Window.__init__(self)
		textLine1 = TextLine()
		textLine1.SetParent(self)
		textLine1.SetPosition(0, 0)
		textLine1.SetHorizontalAlignCenter()
		self.TextLine1 = textLine1

		textLine2 = TextLine()
		textLine2.SetParent(self)
		textLine2.SetPosition(0, 10)
		textLine2.SetHorizontalAlignCenter()
		self.TextLine2 = textLine2

	def __del__(self):
		Window.__del__(self)
		self.TextLine1 = None
		self.TextLine2 = None

	def SetText1(self, text):
		self.TextLine1.SetText(text)
	def SetText2(self, text):
		self.TextLine2.SetText(text)

	def SetFontName(self, font):
		self.TextLine1.SetFontName(font)
		self.TextLine2.SetFontName(font)

	def SetPackedFontColor(self, color):
		self.TextLine1.SetPackedFontColor(color)
		self.TextLine2.SetPackedFontColor(color)

	def ShowTop(self):
		self.TextLine1.SetPosition(0, 0)
		self.TextLine2.SetPosition(0, 10)
		self.TextLine1.Show()
		self.TextLine2.Hide()

	def ShowAll(self):
		self.TextLine1.SetPosition(0, -7)
		self.TextLine2.SetPosition(0, 7)
		self.TextLine1.Show()
		self.TextLine2.Show()

class EmptyCandidateWindow(Window):
	def __init__(self):
		Window.__init__(self)

	def __del__(self):
		Window.__init__(self)

	def Load(self):
		pass

	def SetCandidatePosition(self, x, y, textCount):
		pass

	def Clear(self):
		pass

	def Append(self, text):
		pass

	def Refresh(self):
		pass

	def Select(self):
		pass

class EditLine(TextLine):
	candidateWindowClassDict = {}

	def __init__(self):
		TextLine.__init__(self)

		self.eventReturn = Window.NoneMethod
		self.eventEscape = Window.NoneMethod
		self.eventTab = None
		self.numberMode = False
		self.useIME = True
		self.UseCodePage = True

		self.CanClick = None
		self.CanStatus = True
		self.bCodePage = False

		if app.ENABLE_IKASHOP_RENEWAL:
			self.updateEvent = None

		self.candidateWindowClass = None
		self.candidateWindow = None
		self.SetCodePage(app.GetDefaultCodePage())

		self.readingWnd = ReadingWnd()
		self.readingWnd.Hide()

		self.placeHolder = TextLine()
		self.placeHolder.SetParent(self)
		self.placeHolder.SetText("")
		self.placeHolder.Hide()
		self.max_size = -1
		self.last_text = ""
		self.update_event = None
		self.update_event_args = None

		self.eventUpdate = None
		self.overLay = TextLine()
		self.overLay.SetParent(self)
		self.overLay.SetPosition(0, 0)
		self.overLay.SetPackedFontColor(WHITE_COLOR)
		self.overLay.Hide()

		self.backText=None
		self.isNeedEmpty=True

	def __del__(self):
		TextLine.__del__(self)

		self.eventReturn = Window.NoneMethod
		self.eventEscape = Window.NoneMethod
		self.eventTab = None
		self.CanClick = None
		self.CanStatus = True
		self.placeHolder = None
		self.max_size = -1
		self.last_text = ""

	def SetCodePage(self, codePage):
		candidateWindowClass=EditLine.candidateWindowClassDict.get(codePage, EmptyCandidateWindow)
		self.__SetCandidateClass(candidateWindowClass)

	def __SetCandidateClass(self, candidateWindowClass):
		if self.candidateWindowClass==candidateWindowClass:
			return

		self.candidateWindowClass = candidateWindowClass
		self.candidateWindow = self.candidateWindowClass()
		self.candidateWindow.Load()
		self.candidateWindow.Hide()

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterTextLine(self, layer)

	def SAFE_SetReturnEvent(self, event):
		self.eventReturn = __mem_func__(event)

	def SetReturnEvent(self, event):
		self.eventReturn = event

	def SetEscapeEvent(self, event):
		self.eventEscape = event

	def SetTabEvent(self, event):
		self.eventTab = event

	def SetInfoMessage(self, msg):
		self.infoMsg = msg
		if self.backText == None:
			self.backText = TextLine()
			self.backText.SetParent(self)
			self.backText.SetPosition(0,0)
			self.backText.SetFontColor(128,128,128)

		self.backText.SetText(msg)

		if self.isNeedEmpty:
			if len(self.GetText()) > 0:
				self.backText.Hide()
			else:
				self.backText.Show()
		else:
			self.backText.Show()

	def SetMax(self, max):
		self.max = max
		wndMgr.SetMax(self.hWnd, self.max)
		ime.SetMax(self.max)
		self.SetUserMax(self.max)

	def SetMaxSizeMode(self, forceWidht = -1):
		self.max_size = self.GetWidth() if forceWidht == -1 else forceWidht

	def SetUserMax(self, max):
		self.userMax = max
		ime.SetUserMax(self.userMax)

	def SetNumberMode(self):
		self.numberMode = True

	def SetStringMode(self):
		self.numberMode = False

	def SetOverlayText(self, text):
		self.overLay.SetText(text)
		self.__RefreshOverlay()

	def GetOverlayText(self):
		return self.overLay.GetText()

	def SetUpdateEvent(self, event):
		self.eventUpdate = event

	if app.ENABLE_IKASHOP_RENEWAL:
		def SetUpdateEventShop(self, event):
			self.updateEvent = event

	def GetDisplayText(self):
		if len(self.GetText()):
			return self.GetText()
		else:
			return self.overLay.GetText()

	def __RefreshOverlay(self):
		if len(self.GetText()):
			self.overLay.Hide()
		else:
			self.overLay.Show()

	def IsShowCursor(self):
		return wndMgr.IsShowCursor(self.hWnd)

	def CanEdit(self, flag):
		self.CanClick = flag

	def SetStatus(self, status):
		self.CanStatus = status

	def SetIMEFlag(self, flag):
		self.useIME = flag

	def SetUseCodePage(self, bUse = True):
		self.UseCodePage = bUse

	def SetText(self, text):
		if self.CanStatus == False:
			return

		wndMgr.SetText(self.hWnd, text)

		if self.IsFocus():
			ime.SetText(text)
		self.UpdatePlaceHolder()
		self.__RefreshOverlay()

	def Enable(self):
		wndMgr.ShowCursor(self.hWnd)

	def Disable(self):
		wndMgr.HideCursor(self.hWnd)

	def SetEndPosition(self):
		ime.MoveEnd()

	#PlaceHolder funcs
	def UpdatePlaceHolder(self):
		self.placeHolder.Show() if len(self.GetText()) <= 0 and self.CheckPlaceHolder() is True else self.placeHolder.Hide()

	def SetPlaceHolder(self, placeHolderText, placeHolderPos = (0, 0)):
		if not self.placeHolder:
			return

		if self.CanStatus == False:
			return

		self.placeHolder.SetText(placeHolderText)
		self.placeHolder.SetPosition(*placeHolderPos)
		self.UpdatePlaceHolder()

	def SetPlaceHolderColor(self, color):
		if not self.placeHolder:
			return

		self.placeHolder.SetPackedFontColor(color)

	def CheckPlaceHolder(self):
		return bool(len(self.placeHolder.GetText())) #return true or false
	##

	def OnMouseLeftButtonDown(self):
		if not self.CanStatus:
			return True
		self.SetFocus()
		ime.EnableCaptureInput()
		if hasattr(app, "ShowKeyboard"):
			app.ShowKeyboard(1)
		return True

	def OnSetFocus(self):
		Text = self.GetText()
		ime.SetText(Text)
		ime.SetMax(self.max)
		ime.SetUserMax(self.userMax)
		ime.SetCursorPosition(-1)

		if self.numberMode:
			ime.SetNumberMode()
		else:
			ime.SetStringMode()

		ime.EnableCaptureInput()
		if hasattr(app, "ShowKeyboard"):
			app.ShowKeyboard(1)

		if self.useIME:
			ime.EnableIME()
		else:
			ime.DisableIME()

		wndMgr.ShowCursor(self.hWnd, TRUE)
		self.UpdatePlaceHolder()

		if app.ENABLE_IKASHOP_RENEWAL:
			if self.updateEvent:
				self.updateEvent(True)

	def OnKillFocus(self):
		self.SetText(ime.GetText(self.bCodePage))
		self.OnIMECloseCandidateList()
		self.OnIMECloseReadingWnd()
		ime.DisableIME()
		ime.DisableCaptureInput()
		wndMgr.HideCursor(self.hWnd)
		self.UpdatePlaceHolder()
		if hasattr(app, "ShowKeyboard"):
			app.ShowKeyboard(0)

		if app.ENABLE_IKASHOP_RENEWAL:
			if self.updateEvent:
				self.updateEvent(False)

	def OnIMEChangeCodePage(self):
		self.SetCodePage(ime.GetCodePage())

	def OnIMEOpenCandidateList(self):
		self.candidateWindow.Show()
		self.candidateWindow.Clear()
		self.candidateWindow.Refresh()

		gx, gy = self.GetGlobalPosition()
		self.candidateWindow.SetCandidatePosition(gx, gy, len(self.GetText()))

		return TRUE

	def OnIMECloseCandidateList(self):
		self.candidateWindow.Hide()
		return TRUE

	def OnIMEOpenReadingWnd(self):
		gx, gy = self.GetGlobalPosition()
		textlen = len(self.GetText())-2
		reading = ime.GetReading()
		readinglen = len(reading)
		self.readingWnd.SetReadingPosition( gx + textlen*6-24-readinglen*6, gy )
		self.readingWnd.SetText(reading)
		if ime.GetReadingError() == 0:
			self.readingWnd.SetTextColor(0xffffffff)
		else:
			self.readingWnd.SetTextColor(0xffff0000)
		self.readingWnd.SetSize(readinglen * 6 + 4, 19)
		self.readingWnd.Show()
		return TRUE

	def OnIMECloseReadingWnd(self):
		self.readingWnd.Hide()
		return TRUE

	def CheckMaxSize(self):
		if self.max_size == -1:
			return False

		if self.GetTextSize()[0] > self.max_size and\
			len(self.last_text) < len(ime.GetText(self.bCodePage)):
			return True

		return False

	def OnIMEUpdate(self):
		if self.CanStatus == False:
			ime.SetText("")
			return

		if self.UseCodePage == False and self.IsIncludeCodePage(ime.GetText(self.bCodePage)) == True:
			ime.SetText("")

		if self.CheckMaxSize():
			ime.SetText(self.last_text)

		snd.PlaySound("sound/ui/type.wav")

		TextLine.SetText(self, ime.GetText(self.bCodePage))

		if app.ENABLE_IKASHOP_RENEWAL:
			if self.updateEvent:
				self.updateEvent(self.IsFocus())

		if self.backText:
			if self.isNeedEmpty:
				if len(self.GetText()) > 0:
					self.backText.Hide()
				else:
					self.backText.Show()
			else:
				self.backText.Show()

		self.last_text = ime.GetText(self.bCodePage)

		self.__RefreshOverlay()
		if self.eventUpdate:
			self.eventUpdate()

		self.UpdatePlaceHolder()
		self.OnUpdateEvent()

	def SetUpdateEvent(self, event, *args):
		self.update_event = event
		if len(args) != 0:
			self.update_event_args = args

	def OnUpdateEvent(self):
		if self.update_event:
			if self.update_event_args:
				self.update_event(self.update_event_args[0])
			else:
				self.update_event()

	def OnIMETab(self):
		if self.eventTab:
			self.eventTab()
			return TRUE

		return FALSE

	def OnIMEReturn(self):
		snd.PlaySound("sound/ui/click.wav")
		self.eventReturn()

		return TRUE

	def OnPressEscapeKey(self):
		self.eventEscape()
		return TRUE

	def OnKeyDown(self, key):
		if app.DIK_F1 == key:
			return FALSE
		if app.DIK_F2 == key:
			return FALSE
		if app.DIK_F3 == key:
			return FALSE
		if app.DIK_F4 == key:
			return FALSE
		if app.DIK_LALT == key:
			return FALSE
		if app.DIK_SYSRQ == key:
			return FALSE
		if app.DIK_LCONTROL == key:
			return FALSE
		if app.DIK_V == key:
			if app.IsPressed(app.DIK_LCONTROL):
				ime.PasteTextFromClipBoard()

		return TRUE

	def OnKeyUp(self, key):
		if app.DIK_F1 == key:
			return FALSE
		if app.DIK_F2 == key:
			return FALSE
		if app.DIK_F3 == key:
			return FALSE
		if app.DIK_F4 == key:
			return FALSE
		if app.DIK_LALT == key:
			return FALSE
		if app.DIK_SYSRQ == key:
			return FALSE
		if app.DIK_LCONTROL == key:
			return FALSE

		return TRUE

	def OnIMEKeyDown(self, key):
		# Left
		if app.VK_LEFT == key:
			ime.MoveLeft()
			return TRUE

		# Right
		if app.VK_RIGHT == key:
			ime.MoveRight()
			return TRUE

		# Home
		if app.VK_HOME == key:
			ime.MoveHome()
			return TRUE
		# End

		if app.VK_END == key:
			ime.MoveEnd()
			return TRUE

		# Delete
		if app.VK_DELETE == key:
			ime.Delete()
			TextLine.SetText(self, ime.GetText(self.bCodePage))
			return TRUE

		return TRUE

	def OnMouseLeftButtonDown(self):
		if False == self.IsIn():
			return False
		if False == self.CanClick:
			return

		self.SetFocus()
		PixelPosition = wndMgr.GetCursorPosition(self.hWnd)
		ime.SetCursorPosition(PixelPosition)

class EditLineNew(EditLine):
	def __init__(self):
		EditLine.__init__(self)

		self.backText = TextLine()
		self.backText.SetParent(self)
		self.backText.SetPosition(0,0)
		self.backText.SetFontColor(128,128,128)

	def __del__(self):
		EditLine.__del__(self)

	def SetInfoMessage(self, msg):
		self.backText.SetText(msg)

		if len(self.GetText()) > 0:
			self.backText.Hide()
		else:
			self.backText.Show()

	def OnIMEUpdate(self):
		EditLine.OnIMEUpdate(self)
		if len(self.GetText()) > 0:
			self.backText.Hide()
		else:
			self.backText.Show()

class MarkBox(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)

	def __del__(self):
		Window.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterMarkBox(self, layer)

	def Load(self):
		wndMgr.MarkBox_Load(self.hWnd)

	def SetScale(self, scale):
		wndMgr.MarkBox_SetScale(self.hWnd, scale)

	def SetIndex(self, guildID):
		MarkID = guild.GuildIDToMarkID(guildID)
		wndMgr.MarkBox_SetImageFilename(self.hWnd, guild.GetMarkImageFilenameByMarkID(MarkID))
		wndMgr.MarkBox_SetIndex(self.hWnd, guild.GetMarkIndexByMarkID(MarkID))

	def SetAlpha(self, alpha):
		wndMgr.MarkBox_SetDiffuseColor(self.hWnd, 1.0, 1.0, 1.0, alpha)

class ImageBox(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)

		self.eventDict={}
		self.argDict={}
		self.eventFunc = {"mouse_click" : None, "mouse_over_in" : None, "mouse_over_out" : None}
		self.eventArgs = {"mouse_click" : None, "mouse_over_in" : None, "mouse_over_out" : None}

	def __del__(self):
		Window.__del__(self)

		self.eventDict={}
		self.argDict={}
		self.eventFunc = None
		self.eventArgs = None

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterImageBox(self, layer)

	def LoadImage(self, imageName):
		self.name=imageName
		wndMgr.LoadImage(self.hWnd, imageName)

		if len(self.eventDict)!=0:
			print "LOAD IMAGE", self, self.eventDict

	def SetDiffuseColor(self, r, g, b, a):
		wndMgr.SetDiffuseColor(self.hWnd, r, g, b, a)

	def SetAlpha(self, alpha):
		wndMgr.SetDiffuseColor(self.hWnd, 1.0, 1.0, 1.0, alpha)

	def GetWidth(self):
		return wndMgr.GetWidth(self.hWnd)

	def GetHeight(self):
		return wndMgr.GetHeight(self.hWnd)

	def OnMouseOverIn(self):
		self.__OnMouseOverIn()

	def OnMouseOverOut(self):
		self.__OnMouseOverOut()

	def __OnMouseOverIn(self):
		try:
			apply(self.eventDict["MOUSE_OVER_IN"], self.argDict["MOUSE_OVER_IN"])
		except KeyError:
			pass

	def __OnMouseOverOut(self):
		try:
			apply(self.eventDict["MOUSE_OVER_OUT"], self.argDict["MOUSE_OVER_OUT"])
		except KeyError:
			pass

	def OnMouseLeftButtonDown(self):
		if self.eventDict.has_key("MOUSE_LEFT_DOWN"):
			apply(self.eventDict["MOUSE_LEFT_DOWN"], self.argDict["MOUSE_LEFT_DOWN"])

	def SetEvent(self, func, *args) :
		result = self.eventFunc.has_key(args[0])
		if result :
			self.eventFunc[args[0]] = func
			self.eventArgs[args[0]] = args
		else :
			print "[ERROR] ui.py SetEvent, Can`t Find has_key : %s" % args[0]

	def OnMouseLeftButtonUp(self):
		if app.ENABLE_IKASHOP_RENEWAL:
			super(ImageBox, self).OnMouseLeftButtonUp()
		if self.eventFunc["mouse_click"] :
			apply(self.eventFunc["mouse_click"], self.eventArgs["mouse_click"])
		else:
			try:
				self.eventDict["MOUSE_LEFT_UP"]()
			except KeyError:
				pass

	def SetOnMouseLeftButtonUpEvent(self, event, *args):
		self.eventFunc["mouse_click"] = event
		self.eventArgs["mouse_click"] = args

	def SetStringEvent(self, event, func, *args):
		self.eventDict[event]=func
		self.argDict[event]=args

	def SAFE_SetStringEvent(self, event, func, *args):
		self.eventDict[event]=__mem_func__(func)
		self.argDict[event]=args

	def SAFE_SetMouseClickEvent(self, func, *args):
		self.eventDict["MOUSE_LEFT_DOWN"]=__mem_func__(func)
		self.argDict["MOUSE_LEFT_DOWN"]=args

	def SetOnMouseLeftButtonUpEvent(self, event, *args):
		self.eventFunc["mouse_click"] = event
		self.eventArgs["mouse_click"] = args

class ExpandedImageBox(ImageBox):
	def __init__(self, layer = "UI"):
		ImageBox.__init__(self, layer)

	def __del__(self):
		ImageBox.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterExpandedImageBox(self, layer)

	def SetScale(self, xScale, yScale):
		wndMgr.SetScale(self.hWnd, xScale, yScale)

	def SetOrigin(self, x, y):
		wndMgr.SetOrigin(self.hWnd, x, y)

	def SetRotation(self, rotation):
		wndMgr.SetRotation(self.hWnd, rotation)

	def SetRenderingMode(self, mode):
		wndMgr.SetRenderingMode(self.hWnd, mode)

	# [0.0, 1.0] »çÀÌÀÇ °ª¸¸Å­ ÆÛ¼¾Æ®· ±×¸®ö ¾Ê´Â´Ù.
	def SetRenderingRect(self, left, top, right, bottom):
		wndMgr.SetRenderingRect(self.hWnd, left, top, right, bottom)

	if app.ENABLE_IMAGE_CLIP_RECT:
		def SetClipRect(self, left, top, right, bottom, isVertical = False):
			wndMgr.SetClipRect(self.hWnd, left, top, right, bottom, isVertical)

	def SetPercentage(self, curValue, maxValue):
		if maxValue:
			self.SetRenderingRect(0.0, 0.0, -1.0 + float(curValue) / float(maxValue), 0.0)
		else:
			self.SetRenderingRect(0.0, 0.0, 0.0, 0.0)

	def GetWidth(self):
		return wndMgr.GetWindowWidth(self.hWnd)

	def GetHeight(self):
		return wndMgr.GetWindowHeight(self.hWnd)


class NewShopImageBox(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)

		self.eventDict = {}
		self.eventFunc = {"mouse_click" : None, "mouse_over_in" : None, "mouse_over_out" : None}
		self.eventArgs = {"mouse_click" : None, "mouse_over_in" : None, "mouse_over_out" : None}

	def __del__(self):
		Window.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterImageBox(self, layer)

	def ImageClear(self):
		wndMgr.ImageClear(self.hWnd)

	def LoadImageInstance(self, image):
		wndMgr.LoadImageInstance(self.hWnd, image)

	def LoadImage(self, imageName):
		self.name = imageName
		wndMgr.LoadImage(self.hWnd, imageName)

		if len(self.eventDict)!=0:
			print "LOAD IMAGE", self, self.eventDict

	def SetDiffuseColor(self, r, g, b, a):
		wndMgr.SetDiffuseColor(self.hWnd, r, g, b, a)

	def SetAlpha(self, alpha):
		wndMgr.SetDiffuseColor(self.hWnd, 1.0, 1.0, 1.0, alpha)

	def GetWidth(self):
		return wndMgr.GetWidth(self.hWnd)

	def GetHeight(self):
		return wndMgr.GetHeight(self.hWnd)

	def SAFE_SetStringEvent(self, event, func, *args):
		self.eventDict[event] =__mem_func__(func)
		self.eventArgs[event] = args

	def SetMouseOverInEvent(self, func, *args):
		self.eventDict["MOUSE_OVER_IN"] = func
		self.eventArgs["MOUSE_OVER_IN"] = args

	def SetMouseOverOutEvent(self, func, *args):
		self.eventDict["MOUSE_OVER_OUT"] = func
		self.eventArgs["MOUSE_OVER_OUT"] = args

	def SetEvent(self, func, *args):
		result = self.eventFunc.has_key(args[0])
		if result:
			self.eventFunc[args[0]] = func
			self.eventArgs[args[0]] = args
		else:
			print "[ERROR] ui.py SetEvent, Can`t Find has_key : %s" % args[0]

	def OnMouseLeftButtonUp(self) :
		if self.eventFunc["mouse_click"]:
			apply(self.eventFunc["mouse_click"], self.eventArgs["mouse_click"])
		Window.OnMouseLeftButtonUp(self)

	def OnMouseOverIn(self):
		if self.eventFunc["mouse_over_in"]:
			apply(self.eventFunc["mouse_over_in"], self.eventArgs["mouse_over_in"])

		if self.eventDict.has_key("MOUSE_OVER_IN"):
			if self.eventArgs["MOUSE_OVER_IN"]:
				apply(self.eventDict["MOUSE_OVER_IN"], self.eventArgs["MOUSE_OVER_IN"])
			else:
				self.eventDict["MOUSE_OVER_IN"]()

	def OnMouseOverOut(self):
		if self.eventFunc["mouse_over_out"]:
			apply(self.eventFunc["mouse_over_out"], self.eventArgs["mouse_over_out"])

		if self.eventDict.has_key("MOUSE_OVER_OUT"):
			if self.eventArgs["MOUSE_OVER_OUT"]:
				apply(self.eventDict["MOUSE_OVER_OUT"], self.eventArgs["MOUSE_OVER_OUT"])
			else:
				self.eventDict["MOUSE_OVER_OUT"]()

class ExpandedImageBoxNewShop(NewShopImageBox):
	def __init__(self, layer = "UI"):
		NewShopImageBox.__init__(self, layer)

	def __del__(self):
		NewShopImageBox.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterExpandedImageBox(self, layer)

	def SetScale(self, xScale, yScale):
		wndMgr.SetScale(self.hWnd, xScale, yScale)

	def SetOrigin(self, x, y):
		wndMgr.SetOrigin(self.hWnd, x, y)

	def SetRotation(self, rotation):
		wndMgr.SetRotation(self.hWnd, rotation)

	def SetRenderingMode(self, mode):
		wndMgr.SetRenderingMode(self.hWnd, mode)

	def SetRenderingRect(self, left, top, right, bottom):
		wndMgr.SetRenderingRect(self.hWnd, left, top, right, bottom)

	def SetPercentage(self, curValue, maxValue):
		if maxValue:
			self.SetRenderingRect(0.0, 0.0, -1.0 + float(curValue) / float(maxValue), 0.0)
		else:
			self.SetRenderingRect(0.0, 0.0, 0.0, 0.0)

	def GetWidth(self):
		return wndMgr.GetWindowWidth(self.hWnd)

	def GetHeight(self):
		return wndMgr.GetWindowHeight(self.hWnd)

class AniImageBox(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		self.eventEndFrame = None

	def __del__(self):
		Window.__del__(self)
		self.eventEndFrame = None

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterAniImageBox(self, layer)

	def SetDelay(self, delay):
		wndMgr.SetDelay(self.hWnd, delay)

	if app.__ARE_YOU_IN_OR_NOT__:
		def ResetFrame(self):
			wndMgr.ResetFrame(self.hWnd)

	def SetOnEndFrame(self, event):
		self.eventEndFrame = event

	def OnEndFrame(self):
		if self.eventEndFrame:
			self.eventEndFrame()

	def AppendImage(self, filename):
		wndMgr.AppendImage(self.hWnd, filename)

	def SetPercentage(self, curValue, maxValue):
		wndMgr.SetRenderingRect(self.hWnd, 0.0, 0.0, -1.0 + float(curValue) / float(maxValue), 0.0)

class Button(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)

		self.eventFunc = None
		self.eventArgs = None

		self.ButtonText = None
		self.ToolTipText = None
		self.TextChild = []

		if app.ENABLE_DETAILS_INTERFACE:
			self.overFunc = None
			self.overArgs = None
			self.overOutFunc = None
			self.overOutArgs = None

		self.showtooltipevent = None
		self.showtooltiparg = None
		self.hidetooltipevent = None
		self.hidetooltiparg = None

	def __del__(self):
		Window.__del__(self)

		self.eventFunc = None
		self.eventArgs = None

		if app.ENABLE_DETAILS_INTERFACE:
			self.overFunc = None
			self.overArgs = None
			self.overOutFunc = None
			self.overOutArgs = None

	if app.ENABLE_NEW_GAMEOPTION:
		def SetListText(self, text, x = 8):
			if not self.ButtonText:
				textLine = TextLine()
				textLine.SetParent(self)
				textLine.SetPosition(x, self.GetHeight()/2)
				textLine.SetVerticalAlignCenter()
				textLine.SetHorizontalAlignLeft()
				textLine.Show()
				self.ButtonText = textLine
			self.ButtonText.SetText(text)
	
	if app.ENABLE_NEW_GAMEOPTION:
		def SetRenderingRect(self, left, top, right, bottom):
			wndMgr.SetRenderingRect(self.hWnd, left, top, right, bottom)


	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterButton(self, layer)

	def SetUpVisual(self, filename):
		wndMgr.SetUpVisual(self.hWnd, filename)

	def SetOverVisual(self, filename):
		wndMgr.SetOverVisual(self.hWnd, filename)

	def SetDownVisual(self, filename):
		wndMgr.SetDownVisual(self.hWnd, filename)

	def SetDisableVisual(self, filename):
		wndMgr.SetDisableVisual(self.hWnd, filename)

	def GetUpVisualFileName(self):
		return wndMgr.GetUpVisualFileName(self.hWnd)

	def GetOverVisualFileName(self):
		return wndMgr.GetOverVisualFileName(self.hWnd)

	def GetDownVisualFileName(self):
		return wndMgr.GetDownVisualFileName(self.hWnd)

	def Flash(self):
		wndMgr.Flash(self.hWnd)

	def Enable(self):
		wndMgr.Enable(self.hWnd)

	def Disable(self):
		wndMgr.Disable(self.hWnd)

	def Down(self):
		wndMgr.Down(self.hWnd)

	def EnableFlash(self):
		wndMgr.EnableFlash(self.hWnd)


	def SetUp(self):
		wndMgr.SetUp(self.hWnd)

	def SAFE_SetEvent(self, func, *args):
		self.eventFunc = __mem_func__(func)
		self.eventArgs = args

	def SetEvent(self, func, *args):
		self.eventFunc = func
		self.eventArgs = args

	def SetTextColor(self, color):
		if not self.ButtonText:
			return
		self.ButtonText.SetPackedFontColor(color)

	def SetTextAddPos(self, text, x_add = 0, y_add = 0, height = 4):
		if not self.ButtonText:
			textLine = TextLine()
			textLine.SetParent(self)
			textLine.SetPosition(self.GetWidth() / 2 + x_add, self.GetHeight() / 2 + y_add)
			textLine.SetVerticalAlignCenter()
			textLine.SetHorizontalAlignCenter()
			textLine.Show()
			self.ButtonText = textLine
		self.ButtonText.SetText(text)

	if app.ENABLE_DETAILS_INTERFACE:
		def OnMouseOverIn(self):
			if self.overFunc:
				apply(self.overFunc, self.overArgs )
		def OnMouseOverOut(self):
			if self.overOutFunc:
				apply(self.overOutFunc, self.overOutArgs )
		def SetOverEvent(self, func, *args):
			self.overFunc = func
			self.overArgs = args
		def SetOverOutEvent(self, func, *args):
			self.overOutFunc = func
			self.overOutArgs = args
			
	def SetText(self, text, height = 4):
		if not self.ButtonText:
			textLine = TextLine()
			textLine.SetParent(self)
			textLine.SetPosition(self.GetWidth()/2, self.GetHeight()/2)
			textLine.SetVerticalAlignCenter()
			textLine.SetHorizontalAlignCenter()
			textLine.Show()
			self.ButtonText = textLine

		self.ButtonText.SetText(text)

	if constInfo.EXTRA_UI_FEATURE:
		def GetText(self):
			if not self.ButtonText:
				return ""
			return self.ButtonText.GetText()

	def SetFormToolTipText(self, type, text, x, y):
		if not self.ToolTipText:
			toolTip=createToolTipWindowDict[type]()
			toolTip.SetParent(self)
			toolTip.SetSize(0, 0)
			toolTip.SetHorizontalAlignCenter()
			toolTip.SetOutline()
			toolTip.Hide()
			toolTip.SetPosition(x + self.GetWidth()/2, y)
			self.ToolTipText=toolTip

		self.ToolTipText.SetText(text)

	def SetToolTipWindow(self, toolTip):
		self.ToolTipText=toolTip
		self.ToolTipText.SetParentProxy(self)
	def SetToolTipWindow2(self, toolTip):		
		self.ToolTipText=toolTip	
		#self.ToolTipText.SetParentProxy(self)

	def SetToolTipText(self, text, x=0, y = -19):
		self.SetFormToolTipText("TEXT", text, x, y)

	def CallEvent(self):
		snd.PlaySound("sound/ui/click.wav")

		if self.eventFunc:
			apply(self.eventFunc, self.eventArgs)

	def ShowToolTip(self):
		if self.ToolTipText:
			self.ToolTipText.Show()

		if self.showtooltipevent:
			apply(self.showtooltipevent, self.showtooltiparg)

	def HideToolTip(self):
		if self.ToolTipText:
			self.ToolTipText.Hide()

		if self.hidetooltipevent:
			apply(self.hidetooltipevent, self.hidetooltiparg)

	def SetShowToolTipEvent(self, func, *args):
		self.showtooltipevent = func
		self.showtooltiparg = args

	def SetHideToolTipEvent(self, func, *args):
		self.hidetooltipevent = func
		self.hidetooltiparg = args

	def IsDown(self):
		return wndMgr.IsDown(self.hWnd)

	def SetButtonScale(self, xScale, yScale):
		wndMgr.SetButtonScale(self.hWnd, xScale, yScale)

	if app.ENABLE_DRAGON_COIN_SHOP_SYSTEM:
		def SetTextAlignLeft(self, text, height = 4):
			if not self.ButtonText:
				textLine = TextLine()
				textLine.SetParent(self)
				textLine.SetPosition(27, self.GetHeight()/2)
				textLine.SetVerticalAlignCenter()
				textLine.SetHorizontalAlignLeft()
				textLine.Show()
				self.ButtonText = textLine

			self.ButtonText.SetText(text)
			self.ButtonText.SetPosition(27, self.GetHeight()/2)
			self.ButtonText.SetVerticalAlignCenter()
			self.ButtonText.SetHorizontalAlignLeft()


class RadioButton(Button):
	def __init__(self):
		Button.__init__(self)

	def __del__(self):
		Button.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterRadioButton(self, layer)

class RadioButtonGroup:
	def __init__(self):
		self.buttonGroup = []
		self.selectedBtnIdx = -1

	def __del__(self):
		for button, ue, de in self.buttonGroup:
			button.__del__()

	def Show(self):
		for (button, selectEvent, unselectEvent) in self.buttonGroup:
			button.Show()

	def Hide(self):
		for (button, selectEvent, unselectEvent) in self.buttonGroup:
			button.Hide()

	def SetText(self, idx, text):
		if idx >= len(self.buttonGroup):
			return
		(button, selectEvent, unselectEvent) = self.buttonGroup[idx]
		button.SetText(text)

	def OnClick(self, btnIdx):
		if btnIdx == self.selectedBtnIdx:
			return
		(button, selectEvent, unselectEvent) = self.buttonGroup[self.selectedBtnIdx]
		if unselectEvent:
			unselectEvent()
		button.SetUp()

		self.selectedBtnIdx = btnIdx
		(button, selectEvent, unselectEvent) = self.buttonGroup[btnIdx]
		if selectEvent:
			selectEvent()

		button.Down()

	def AddButton(self, button, selectEvent, unselectEvent):
		i = len(self.buttonGroup)
		button.SetEvent(lambda : self.OnClick(i))
		self.buttonGroup.append([button, selectEvent, unselectEvent])
		button.SetUp()

	def Create(rawButtonGroup):
		radioGroup = RadioButtonGroup()
		for (button, selectEvent, unselectEvent) in rawButtonGroup:
			radioGroup.AddButton(button, selectEvent, unselectEvent)

		radioGroup.OnClick(0)

		return radioGroup

	Create=staticmethod(Create)

class ToggleButton(Button):
	def __init__(self):
		Button.__init__(self)

		self.eventUp = None
		self.eventDown = None

		if app.ENABLE_DRAGON_COIN_SHOP_SYSTEM:
			self.eventUpArgs = None
			self.eventDownArgs = None

	def __del__(self):
		Button.__del__(self)

		self.eventUp = None
		self.eventDown = None

		if app.ENABLE_DRAGON_COIN_SHOP_SYSTEM:
			self.eventUpArgs = None
			self.eventDownArgs = None

	if app.ENABLE_DRAGON_COIN_SHOP_SYSTEM:
		def SetToggleUpEvent(self, event, *args):
			self.eventUp = event
			self.eventUpArgs = args

		def SetToggleDownEvent(self, event, *args):
			self.eventDown = event
			self.eventDownArgs = args

		def OnToggleUp(self):
			if self.eventUp:
				if self.eventUpArgs:
					apply(self.eventUp, self.eventUpArgs)
				else:
					self.eventUp()

		def OnToggleDown(self):
			if self.eventDown:
				if self.eventDownArgs:
					apply(self.eventDown, self.eventDownArgs)
				else:
					self.eventDown()
	else:
		def SetToggleUpEvent(self, event):
			self.eventUp = event

		def SetToggleDownEvent(self, event):
			self.eventDown = event

		def OnToggleUp(self):
			if self.eventUp:
				self.eventUp()

		def OnToggleDown(self):
			if self.eventDown:
				self.eventDown()

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterToggleButton(self, layer)

class DragButton(Button):
	def __init__(self):
		Button.__init__(self)
		self.AddFlag("movable")

		self.callbackEnable = True
		self.eventMove = lambda: None

	def __del__(self):
		Button.__del__(self)

		self.eventMove = lambda: None

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterDragButton(self, layer)

	def SetMoveEvent(self, event):
		self.eventMove = event

	def SetRestrictMovementArea(self, x, y, width, height):
		wndMgr.SetRestrictMovementArea(self.hWnd, x, y, width, height)

	def TurnOnCallBack(self):
		self.callbackEnable = True

	def TurnOffCallBack(self):
		self.callbackEnable = False

	def OnMove(self):
		if self.callbackEnable:
			self.eventMove()

class NumberLine(Window):

	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)

	def __del__(self):
		Window.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterNumberLine(self, layer)

	def SetHorizontalAlignCenter(self):
		wndMgr.SetNumberHorizontalAlignCenter(self.hWnd)

	def SetHorizontalAlignRight(self):
		wndMgr.SetNumberHorizontalAlignRight(self.hWnd)

	def SetPath(self, path):
		wndMgr.SetPath(self.hWnd, path)

	def SetNumber(self, number):
		wndMgr.SetNumber(self.hWnd, number)

###################################################################################################
## PythonScript Element
###################################################################################################

class Box(Window):

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterBox(self, layer)

	def SetColor(self, color):
		wndMgr.SetColor(self.hWnd, color)

class Bar(Window):

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterBar(self, layer)

	def SetColor(self, color):
		wndMgr.SetColor(self.hWnd, color)

class Line(Window):

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterLine(self, layer)

	def SetColor(self, color):
		wndMgr.SetColor(self.hWnd, color)

class SlotBar(Window):

	def __init__(self):
		Window.__init__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterBar3D(self, layer)

## Same with SlotBar
class Bar3D(Window):

	def __init__(self):
		Window.__init__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterBar3D(self, layer)

	def SetColor(self, left, right, center):
		wndMgr.SetColor(self.hWnd, left, right, center)

class SlotWindow(Window):

	def __init__(self):
		Window.__init__(self)

		self.StartIndex = 0

		self.eventSelectEmptySlot = None
		self.eventSelectItemSlot = None
		self.eventUnselectEmptySlot = None
		self.eventUnselectItemSlot = None
		self.eventUseSlot = None
		self.eventOverInItem = None
		self.eventOverOutItem = None
		self.eventPressedSlotButton = None

	def __del__(self):
		Window.__del__(self)

		self.eventSelectEmptySlot = None
		self.eventSelectItemSlot = None
		self.eventUnselectEmptySlot = None
		self.eventUnselectItemSlot = None
		self.eventUseSlot = None
		self.eventOverInItem = None
		self.eventOverOutItem = None
		self.eventPressedSlotButton = None

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterSlotWindow(self, layer)

	def SetSlotStyle(self, style):
		wndMgr.SetSlotStyle(self.hWnd, style)

	def HasSlot(self, slotIndex):
		return wndMgr.HasSlot(self.hWnd, slotIndex)

	def SetSlotBaseImage(self, imageFileName, r, g, b, a):
		wndMgr.SetSlotBaseImage(self.hWnd, imageFileName, r, g, b, a)

	def SetCoverButton(self,\
						slotIndex,\
						upName="d:/ymir work/ui/public/slot_cover_button_01.sub",\
						overName="d:/ymir work/ui/public/slot_cover_button_02.sub",\
						downName="d:/ymir work/ui/public/slot_cover_button_03.sub",\
						disableName="d:/ymir work/ui/public/slot_cover_button_04.sub",\
						LeftButtonEnable = False,\
						RightButtonEnable = True):
		wndMgr.SetCoverButton(self.hWnd, slotIndex, upName, overName, downName, disableName, LeftButtonEnable, RightButtonEnable)

	def EnableCoverButton(self, slotIndex):
		wndMgr.EnableCoverButton(self.hWnd, slotIndex)

	def DisableCoverButton(self, slotIndex):
		wndMgr.DisableCoverButton(self.hWnd, slotIndex)

	def SetAlwaysRenderCoverButton(self, slotIndex, bAlwaysRender = True):
		wndMgr.SetAlwaysRenderCoverButton(self.hWnd, slotIndex, bAlwaysRender)

	def AppendSlotButton(self, upName, overName, downName):
		wndMgr.AppendSlotButton(self.hWnd, upName, overName, downName)

	def ShowSlotButton(self, slotNumber):
		wndMgr.ShowSlotButton(self.hWnd, slotNumber)

	def HideAllSlotButton(self):
		wndMgr.HideAllSlotButton(self.hWnd)

	def AppendRequirementSignImage(self, filename):
		wndMgr.AppendRequirementSignImage(self.hWnd, filename)

	def ShowRequirementSign(self, slotNumber):
		wndMgr.ShowRequirementSign(self.hWnd, slotNumber)

	def HideRequirementSign(self, slotNumber):
		wndMgr.HideRequirementSign(self.hWnd, slotNumber)

	def ActivateSlot(self, slotNumber, r = 1.0, g = 1.0, b = 1.0, a = 1.0):
		wndMgr.ActivateSlot(self.hWnd, slotNumber, r, g, b, a)

	def DeactivateSlot(self, slotNumber):
		wndMgr.DeactivateSlot(self.hWnd, slotNumber)

	def ShowSlotBaseImage(self, slotNumber):
		wndMgr.ShowSlotBaseImage(self.hWnd, slotNumber)

	def HideSlotBaseImage(self, slotNumber):
		wndMgr.HideSlotBaseImage(self.hWnd, slotNumber)

	def SAFE_SetButtonEvent(self, button, state, event):
		if "LEFT"==button:
			if "EMPTY"==state:
				self.eventSelectEmptySlot=__mem_func__(event)
			elif "EXIST"==state:
				self.eventSelectItemSlot=__mem_func__(event)
			elif "ALWAYS"==state:
				self.eventSelectEmptySlot=__mem_func__(event)
				self.eventSelectItemSlot=__mem_func__(event)
		elif "RIGHT"==button:
			if "EMPTY"==state:
				self.eventUnselectEmptySlot=__mem_func__(event)
			elif "EXIST"==state:
				self.eventUnselectItemSlot=__mem_func__(event)
			elif "ALWAYS"==state:
				self.eventUnselectEmptySlot=__mem_func__(event)
				self.eventUnselectItemSlot=__mem_func__(event)

	def SetSelectEmptySlotEvent(self, empty):
		self.eventSelectEmptySlot = empty

	def SetSelectItemSlotEvent(self, item):
		self.eventSelectItemSlot = item

	def SetUnselectEmptySlotEvent(self, empty):
		self.eventUnselectEmptySlot = empty

	def SetUnselectItemSlotEvent(self, item):
		self.eventUnselectItemSlot = item

	def SetUseSlotEvent(self, use):
		self.eventUseSlot = use

	def SetOverInItemEvent(self, event):
		self.eventOverInItem = event

	def SetOverOutItemEvent(self, event):
		self.eventOverOutItem = event

	def SetPressedSlotButtonEvent(self, event):
		self.eventPressedSlotButton = event

	def GetSlotCount(self):
		return wndMgr.GetSlotCount(self.hWnd)

	def SetUseMode(self, flag):
		wndMgr.SetUseMode(self.hWnd, flag)

	def SetUsableItem(self, flag):
		wndMgr.SetUsableItem(self.hWnd, flag)

	if app.ENABLE_TRADABLE_ICON:
		def SetCanMouseEventSlot(self, slotIndex):
			wndMgr.SetCanMouseEventSlot(self.hWnd, slotIndex)

		def SetCantMouseEventSlot(self, slotIndex):
			wndMgr.SetCantMouseEventSlot(self.hWnd, slotIndex)

		def SetUsableSlotOnTopWnd(self, slotIndex):
			wndMgr.SetUsableSlotOnTopWnd(self.hWnd, slotIndex)

		def SetUnusableSlotOnTopWnd(self, slotIndex):
			wndMgr.SetUnusableSlotOnTopWnd(self.hWnd, slotIndex)

	## Slot
	if app.ENABLE_SLOT_WINDOW_EX:
		def IsActivatedSlot(self, slotNumber):
			return wndMgr.IsActivatedSlot(self.hWnd, slotNumber)

		def GetSlotCoolTime(self, slotIndex):
			return wndMgr.GetSlotCoolTime(self.hWnd, slotIndex)

	def SetSlotCoolTime(self, slotIndex, coolTime, elapsedTime = 0.0):
		wndMgr.SetSlotCoolTime(self.hWnd, slotIndex, coolTime, elapsedTime)

	def DisableSlot(self, slotIndex):
		wndMgr.DisableSlot(self.hWnd, slotIndex)

	def EnableSlot(self, slotIndex):
		wndMgr.EnableSlot(self.hWnd, slotIndex)

	def LockSlot(self, slotIndex):
		wndMgr.LockSlot(self.hWnd, slotIndex)

	def UnlockSlot(self, slotIndex):
		wndMgr.UnlockSlot(self.hWnd, slotIndex)

	def RefreshSlot(self):
		wndMgr.RefreshSlot(self.hWnd)

	def ClearSlot(self, slotNumber):
		wndMgr.ClearSlot(self.hWnd, slotNumber)

	def ClearAllSlot(self):
		wndMgr.ClearAllSlot(self.hWnd)

	def AppendSlot(self, index, x, y, width, height):
		wndMgr.AppendSlot(self.hWnd, index, x, y, width, height)

	def SetSlot(self, slotIndex, itemIndex, width, height, icon, diffuseColor = (1.0, 1.0, 1.0, 1.0)):
		wndMgr.SetSlot(self.hWnd, slotIndex, itemIndex, width, height, icon, diffuseColor)

	def SetSlotCount(self, slotNumber, count):
		wndMgr.SetSlotCount(self.hWnd, slotNumber, count)

	def SetSlotCountNew(self, slotNumber, grade, count):
		wndMgr.SetSlotCountNew(self.hWnd, slotNumber, grade, count)

	def GetSlot(self, slotNumber):
		return wndMgr.GetSlot(self.hWnd, slotNumber)


	if app.ENABLE_OKEY_KART_EVENT:
		def SetCardSlot(self, renderingSlotNumber, CardIndex, cardIcon, diffuseColor = (1.0, 1.0, 1.0, 1.0)):
			if 0 == CardIndex or None == CardIndex:
				wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
				return

			item.SelectItem(CardIndex)
			(width, height) = item.GetItemSize()

			wndMgr.SetCardSlot(self.hWnd, renderingSlotNumber, CardIndex, width, height, cardIcon, diffuseColor)

	def SetGridSpecial(self, w, h):
		self.__gridCalculator = Grid(w, h)

	def GetEmptyGrid(self, item_size):
		return self.__gridCalculator.find_blank(1, item_size) if self.__gridCalculator != None else -1
	
	def ClearGrid(self):
		if self.__gridCalculator:
			self.__gridCalculator.reset()
	
	def PutItemGrid(self, pos, size):
		if self.__gridCalculator:
			self.__gridCalculator.put(pos, 1, size)
		
	def ClearItemGrid(self, pos, size):
		if self.__gridCalculator:
			self.__gridCalculator.clear(pos, 1, size)
	def SetItemSlot(self, renderingSlotNumber, ItemIndex, ItemCount = 0, diffuseColor = (1.0, 1.0, 1.0, 1.0)):
		if 0 == ItemIndex or None == ItemIndex:
			wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
			return

		item.SelectItem(ItemIndex)
		itemIcon = item.GetIconImage()

		item.SelectItem(ItemIndex)
		(width, height) = item.GetItemSize()

		wndMgr.SetSlot(self.hWnd, renderingSlotNumber, ItemIndex, width, height, itemIcon, diffuseColor)
		wndMgr.SetSlotCount(self.hWnd, renderingSlotNumber, ItemCount)

	def SetSkillSlot(self, renderingSlotNumber, skillIndex, skillLevel):

		skillIcon = skill.GetIconImage(skillIndex)

		if 0 == skillIcon:
			wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
			return

		wndMgr.SetSlot(self.hWnd, renderingSlotNumber, skillIndex, 1, 1, skillIcon)
		wndMgr.SetSlotCount(self.hWnd, renderingSlotNumber, skillLevel)

	def SetSkillSlotNew(self, renderingSlotNumber, skillIndex, skillGrade, skillLevel):

		skillIcon = skill.GetIconImageNew(skillIndex, skillGrade)

		if 0 == skillIcon:
			wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
			return

		wndMgr.SetSlot(self.hWnd, renderingSlotNumber, skillIndex, 1, 1, skillIcon)

	def SetEmotionSlot(self, renderingSlotNumber, emotionIndex):
		import player
		icon = player.GetEmotionIconImage(emotionIndex)

		if 0 == icon:
			wndMgr.ClearSlot(self.hWnd, renderingSlotNumber)
			return

		wndMgr.SetSlot(self.hWnd, renderingSlotNumber, emotionIndex, 1, 1, icon)

	## Event
	def OnSelectEmptySlot(self, slotNumber):
		if self.eventSelectEmptySlot:
			self.eventSelectEmptySlot(slotNumber)

	def OnSelectItemSlot(self, slotNumber):
		if self.eventSelectItemSlot:
			self.eventSelectItemSlot(slotNumber)

	def OnUnselectEmptySlot(self, slotNumber):
		if self.eventUnselectEmptySlot:
			self.eventUnselectEmptySlot(slotNumber)

	def OnUnselectItemSlot(self, slotNumber):
		if self.eventUnselectItemSlot:
			self.eventUnselectItemSlot(slotNumber)

	def OnUseSlot(self, slotNumber):
		if self.eventUseSlot:
			self.eventUseSlot(slotNumber)

	def OnOverInItem(self, slotNumber):
		if self.eventOverInItem:
			self.eventOverInItem(slotNumber)

	def OnOverOutItem(self):
		if self.eventOverOutItem:
			self.eventOverOutItem()

	def OnPressedSlotButton(self, slotNumber):
		if self.eventPressedSlotButton:
			self.eventPressedSlotButton(slotNumber)

	if constInfo.ENABLE_SLOT_MARKING_EX == 1:
		def SetSlotHighlightedGreeen(self, slotNumber, slotColor):
			wndMgr.SetSlotHighlightedGreeen(self.hWnd, slotNumber, slotColor)

		def DisableSlotHighlightedGreen(self, slotNumber, slotColor):
			wndMgr.DisableSlotHighlightedGreen(self.hWnd, slotNumber, slotColor)

	def GetStartIndex(self):
		return 0

class GridSlotWindow(SlotWindow):

	def __init__(self):
		SlotWindow.__init__(self)

		self.startIndex = 0

	def __del__(self):
		SlotWindow.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterGridSlotWindow(self, layer)

	def ArrangeSlot(self, StartIndex, xCount, yCount, xSize, ySize, xBlank, yBlank):

		self.startIndex = StartIndex

		wndMgr.ArrangeSlot(self.hWnd, StartIndex, xCount, yCount, xSize, ySize, xBlank, yBlank)
		self.startIndex = StartIndex

	def GetStartIndex(self):
		return self.startIndex

class TitleBar(Window):

	BLOCK_WIDTH = 32
	BLOCK_HEIGHT = 23

	def __init__(self):
		Window.__init__(self)
		self.AddFlag("attach")

	def __del__(self):
		Window.__del__(self)

	def MakeTitleBar(self, width, color):


		width = max(64, width)

		imgLeft = ImageBox()
		imgCenter = ExpandedImageBox()
		imgRight = ImageBox()
		imgLeft.AddFlag("not_pick")
		imgCenter.AddFlag("not_pick")
		imgRight.AddFlag("not_pick")
		imgLeft.SetParent(self)
		imgCenter.SetParent(self)
		imgRight.SetParent(self)

		if localeInfo.IsARABIC():
			imgLeft.LoadImage("locale/ae/ui/pattern/titlebar_left.tga")
			imgCenter.LoadImage("locale/ae/ui/pattern/titlebar_center.tga")
			imgRight.LoadImage("locale/ae/ui/pattern/titlebar_right.tga")
		else:
			imgLeft.LoadImage("d:/ymir work/ui/pattern/titlebar_left.tga")
			imgCenter.LoadImage("d:/ymir work/ui/pattern/titlebar_center.tga")
			imgRight.LoadImage("d:/ymir work/ui/pattern/titlebar_right.tga")

		imgLeft.Show()
		imgCenter.Show()
		imgRight.Show()

		btnClose = Button()
		btnClose.SetParent(self)
		btnClose.SetUpVisual("d:/ymir work/ui/public/close_button_01.sub")
		btnClose.SetOverVisual("d:/ymir work/ui/public/close_button_02.sub")
		btnClose.SetDownVisual("d:/ymir work/ui/public/close_button_03.sub")
		btnClose.SetToolTipText(localeInfo.UI_CLOSE, 0, -23)
		btnClose.Show()

		self.imgLeft = imgLeft
		self.imgCenter = imgCenter
		self.imgRight = imgRight
		self.btnClose = btnClose

		self.SetWidth(width)

	def SetWidth(self, width):
		self.imgCenter.SetRenderingRect(0.0, 0.0, float((width - self.BLOCK_WIDTH*2) - self.BLOCK_WIDTH) / self.BLOCK_WIDTH, 0.0)
		self.imgCenter.SetPosition(self.BLOCK_WIDTH, 0)
		self.imgRight.SetPosition(width - self.BLOCK_WIDTH, 0)

		if localeInfo.IsARABIC():
			self.btnClose.SetPosition(3, 3)
		else:
			self.btnClose.SetPosition(width - self.btnClose.GetWidth() - 3, 3)

		self.SetSize(width, self.BLOCK_HEIGHT)

	def SetCloseEvent(self, event):
		self.btnClose.SetEvent(event)

	if app.__BL_LUCKY_BOX__:
		def CloseButtonHide(self) :
			if localeInfo.IsARABIC():
				self.imgLeft.LoadImage("d:/ymir work/ui/pattern/titlebar_right.tga")
				self.btnClose.Hide()
			else:
				self.imgRight.LoadImage("d:/ymir work/ui/pattern/titlebar_right.tga")
				self.btnClose.Hide()

class HorizontalBar(Window):

	BLOCK_WIDTH = 32
	BLOCK_HEIGHT = 17

	def __init__(self):
		Window.__init__(self)
		self.AddFlag("attach")

	def __del__(self):
		Window.__del__(self)

	def Create(self, width):

		width = max(96, width)

		imgLeft = ImageBox()
		imgLeft.SetParent(self)
		imgLeft.AddFlag("not_pick")
		imgLeft.LoadImage("d:/ymir work/ui/pattern/horizontalbar_left.tga")
		imgLeft.Show()

		imgCenter = ExpandedImageBox()
		imgCenter.SetParent(self)
		imgCenter.AddFlag("not_pick")
		imgCenter.LoadImage("d:/ymir work/ui/pattern/horizontalbar_center.tga")
		imgCenter.Show()

		imgRight = ImageBox()
		imgRight.SetParent(self)
		imgRight.AddFlag("not_pick")
		imgRight.LoadImage("d:/ymir work/ui/pattern/horizontalbar_right.tga")
		imgRight.Show()

		self.imgLeft = imgLeft
		self.imgCenter = imgCenter
		self.imgRight = imgRight
		self.SetWidth(width)

	def SetWidth(self, width):
		self.imgCenter.SetRenderingRect(0.0, 0.0, float((width - self.BLOCK_WIDTH*2) - self.BLOCK_WIDTH) / self.BLOCK_WIDTH, 0.0)
		self.imgCenter.SetPosition(self.BLOCK_WIDTH, 0)
		self.imgRight.SetPosition(width - self.BLOCK_WIDTH, 0)
		self.SetSize(width, self.BLOCK_HEIGHT)

class Gauge(Window):

	SLOT_WIDTH = 16
	SLOT_HEIGHT = 7

	GAUGE_TEMPORARY_PLACE = 12
	GAUGE_WIDTH = 16

	def __init__(self):
		Window.__init__(self)
		self.width = 0
	def __del__(self):
		Window.__del__(self)

	def MakeGauge(self, width, color):

		self.width = max(48, width)

		imgSlotLeft = ImageBox()
		imgSlotLeft.SetParent(self)
		imgSlotLeft.LoadImage("d:/ymir work/ui/pattern/gauge_slot_left.tga")
		imgSlotLeft.Show()

		imgSlotRight = ImageBox()
		imgSlotRight.SetParent(self)
		imgSlotRight.LoadImage("d:/ymir work/ui/pattern/gauge_slot_right.tga")
		imgSlotRight.Show()
		imgSlotRight.SetPosition(width - self.SLOT_WIDTH, 0)

		imgSlotCenter = ExpandedImageBox()
		imgSlotCenter.SetParent(self)
		imgSlotCenter.LoadImage("d:/ymir work/ui/pattern/gauge_slot_center.tga")
		imgSlotCenter.Show()
		imgSlotCenter.SetRenderingRect(0.0, 0.0, float((width - self.SLOT_WIDTH*2) - self.SLOT_WIDTH) / self.SLOT_WIDTH, 0.0)
		imgSlotCenter.SetPosition(self.SLOT_WIDTH, 0)

		imgGauge = ExpandedImageBox()
		imgGauge.SetParent(self)
		imgGauge.LoadImage("d:/ymir work/ui/pattern/gauge_" + color + ".tga")
		imgGauge.Show()
		imgGauge.SetRenderingRect(0.0, 0.0, 0.0, 0.0)
		imgGauge.SetPosition(self.GAUGE_TEMPORARY_PLACE, 0)

		imgSlotLeft.AddFlag("attach")
		imgSlotCenter.AddFlag("attach")
		imgSlotRight.AddFlag("attach")

		self.imgLeft = imgSlotLeft
		self.imgCenter = imgSlotCenter
		self.imgRight = imgSlotRight
		self.imgGauge = imgGauge

		self.SetSize(width, self.SLOT_HEIGHT)

	def SetPercentage(self, curValue, maxValue):

		# PERCENTAGE_MAX_VALUE_ZERO_DIVISION_ERROR
		if maxValue > 0.0:
			percentage = min(1.0, float(curValue)/float(maxValue))
		else:
			percentage = 0.0
		# END_OF_PERCENTAGE_MAX_VALUE_ZERO_DIVISION_ERROR

		gaugeSize = -1.0 + float(self.width - self.GAUGE_TEMPORARY_PLACE*2) * percentage / self.GAUGE_WIDTH
		self.imgGauge.SetRenderingRect(0.0, 0.0, gaugeSize, 0.0)


class Board(Window):

	CORNER_WIDTH = 32
	CORNER_HEIGHT = 32
	LINE_WIDTH = 128
	LINE_HEIGHT = 128

	BASE_WIDTH = 777
	BASE_HEIGHT = 486

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self):
		Window.__init__(self)
		# self.MakeBoard("dragonetc/offical/Board_Corner_", "dragonetc/offical/Board_Line_")
		self.MakeBoard("dragonetc/offical/Board_Corner_", "dragonetc/offical/Board_Line_")
		self.MakeBase()

	def __del__(self):
		Window.__del__(self)

	def MakeBoard(self, cornerPath, linePath):
		CornerFileNames = [ cornerPath+dir+".tga" for dir in ("LeftTop", "LeftBottom", "RightTop", "RightBottom", ) ]
		LineFileNames = [ linePath+dir+".tga" for dir in ("Left", "Right", "Top", "Bottom", ) ]

		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)

		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	def MakeBase(self):
		self.Base = ExpandedImageBox()
		self.Base.AddFlag("not_pick")
		# self.Base.LoadImage("dragonetc/offical/Board_Base.tga")
		self.Base.LoadImage("dragonetc/offical/Board_Base.tga")
		self.Base.SetParent(self)
		self.Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Base.Show()

	def HideLine(self, line):
		self.Lines[line].Hide()
		self.SetSize(self.GetWidth(), self.GetHeight())

	def SetSize(self, width, height):

		width = max(self.CORNER_WIDTH*2, width)
		height = max(self.CORNER_HEIGHT*2, height)
		Window.SetSize(self, width, height)

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

		verticalShowingPercentage = float((height - self.CORNER_HEIGHT*2) - self.BASE_HEIGHT) / self.BASE_HEIGHT
		horizontalShowingPercentage = float((width - self.CORNER_WIDTH*2) - self.BASE_WIDTH) / self.BASE_WIDTH

		self.Base.SetRenderingRect(0, 0, horizontalShowingPercentage, verticalShowingPercentage)

class BoardBlue(Window):

	CORNER_WIDTH = 32
	CORNER_HEIGHT = 32
	LINE_WIDTH = 128
	LINE_HEIGHT = 128

	BASE_WIDTH = 777
	BASE_HEIGHT = 486

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self):
		Window.__init__(self)
		self.MakeBoard("dragonetc/blue/Board_Corner_", "dragonetc/blue/Board_Line_")
		self.MakeBase()

	def __del__(self):
		Window.__del__(self)

	def MakeBoard(self, cornerPath, linePath):
		CornerFileNames = [ cornerPath+dir+".tga" for dir in ("LeftTop", "LeftBottom", "RightTop", "RightBottom", ) ]
		LineFileNames = [ linePath+dir+".tga" for dir in ("Left", "Right", "Top", "Bottom", ) ]

		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)

		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	def MakeBase(self):
		self.Base = ExpandedImageBox()
		self.Base.AddFlag("not_pick")
		self.Base.LoadImage("dragonetc/blue/Board_Base.tga")
		self.Base.SetParent(self)
		self.Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		self.Base.Show()

	def HideLine(self, line):
		self.Lines[line].Hide()
		self.SetSize(self.GetWidth(), self.GetHeight())

	def SetSize(self, width, height):

		width = max(self.CORNER_WIDTH*2, width)
		height = max(self.CORNER_HEIGHT*2, height)
		Window.SetSize(self, width, height)

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

		verticalShowingPercentage = float((height - self.CORNER_HEIGHT*2) - self.BASE_HEIGHT) / self.BASE_HEIGHT
		horizontalShowingPercentage = float((width - self.CORNER_WIDTH*2) - self.BASE_WIDTH) / self.BASE_WIDTH

		self.Base.SetRenderingRect(0, 0, horizontalShowingPercentage, verticalShowingPercentage)

class BoardWithTitleBar(Board):
	def __init__(self):
		Board.__init__(self)

		titleBar = TitleBar()
		titleBar.SetParent(self)
		titleBar.MakeTitleBar(0, "red")
		titleBar.SetPosition(8, 7)
		titleBar.Show()

		titleName = TextLine()
		titleName.SetParent(titleBar)
		titleName.SetPosition(0, 4)
		titleName.SetWindowHorizontalAlignCenter()
		titleName.SetHorizontalAlignCenter()
		titleName.Show()

		self.titleBar = titleBar
		self.titleName = titleName

		self.SetCloseEvent(self.Hide)

	def __del__(self):
		Board.__del__(self)
		self.titleBar = None
		self.titleName = None

	def SetSize(self, width, height):
		self.titleBar.SetWidth(width - 15)
		#self.pickRestrictWindow.SetSize(width, height - 30)
		Board.SetSize(self, width, height)
		self.titleName.UpdateRect()

	def SetTitleColor(self, color):
		self.titleName.SetPackedFontColor(color)

	def SetTitleName(self, name):
		self.titleName.SetText(name)

	def SetCloseEvent(self, event):
		self.titleBar.SetCloseEvent(event)



class ThinBoard(Window):

	CORNER_WIDTH = 16
	CORNER_HEIGHT = 16
	LINE_WIDTH = 16
	LINE_HEIGHT = 16
	BOARD_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 0.51)

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)

		CornerFileNames = [ "d:/ymir work/ui/pattern/ThinBoard_Corner_"+dir+".tga" for dir in ["LeftTop","LeftBottom","RightTop","RightBottom"] ]
		LineFileNames = [ "d:/ymir work/ui/pattern/ThinBoard_Line_"+dir+".tga" for dir in ["Left","Right","Top","Bottom"] ]

		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("attach")
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("attach")
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)

		Base = Bar()
		Base.SetParent(self)
		Base.AddFlag("attach")
		Base.AddFlag("not_pick")
		Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		Base.SetColor(self.BOARD_COLOR)
		Base.Show()
		self.Base = Base

		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	def __del__(self):
		Window.__del__(self)

	if app.ENABLE_SEND_TARGET_INFO:
		def ShowCorner(self, corner):
			self.Corners[corner].Show()
			self.SetSize(self.GetWidth(), self.GetHeight())

		def HideCorners(self, corner):
			self.Corners[corner].Hide()
			self.SetSize(self.GetWidth(), self.GetHeight())

		def ShowLine(self, line):
			self.Lines[line].Show()
			self.SetSize(self.GetWidth(), self.GetHeight())

		def HideLine(self, line):
			self.Lines[line].Hide()
			self.SetSize(self.GetWidth(), self.GetHeight())
			
	def SetSize(self, width, height):

		width = max(self.CORNER_WIDTH*2, width)
		height = max(self.CORNER_HEIGHT*2, height)
		Window.SetSize(self, width, height)

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
		self.Base.SetSize(width - self.CORNER_WIDTH*2, height - self.CORNER_HEIGHT*2)

	def ShowInternal(self):
		self.Base.Show()
		for wnd in self.Lines:
			wnd.Show()
		for wnd in self.Corners:
			wnd.Show()

	def HideInternal(self):
		self.Base.Hide()
		for wnd in self.Lines:
			wnd.Hide()
		for wnd in self.Corners:
			wnd.Hide()


	def SetAlpha(self, alpha):
		color  = grp.GenerateColor(0.0, 0.0, 0.0, alpha)
		self.Base.SetColor(color)
		for wnd in self.Lines:
			wnd.SetAlpha(alpha)
		for wnd in self.Corners:
			wnd.SetAlpha(alpha)

class ThinBoardCircle(Window):
	CORNER_WIDTH = 4
	CORNER_HEIGHT = 4
	LINE_WIDTH = 4
	LINE_HEIGHT = 4

	BOARD_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 0.5)
	BOARD_ALPHA_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 0.50)

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self, layer = "UI", alpha = False):
		Window.__init__(self, layer)

		CornerFileNames = [ "d:/ymir work/ui/pattern/thinboardcircle/ThinBoard_Corner_"+dir+"_Circle.tga" for dir in ["LeftTop","LeftBottom","RightTop","RightBottom"] ]
		LineFileNames = [ "d:/ymir work/ui/pattern/thinboardcircle/ThinBoard_Line_"+dir+"_Circle.tga" for dir in ["Left","Right","Top","Bottom"] ]

		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("attach")
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			if (alpha == True):
				Corner.SetAlpha(0.50)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("attach")
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			if (alpha == True):
				Line.SetAlpha(0.50)
			Line.Show()
			self.Lines.append(Line)

		Base = Bar()
		Base.SetParent(self)
		Base.AddFlag("attach")
		Base.AddFlag("not_pick")
		Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		if (alpha == True):
			Base.SetColor(self.BOARD_ALPHA_COLOR)
		else:
			Base.SetColor(self.BOARD_COLOR)
		Base.Show()
		self.Base = Base

		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	def __del__(self):
		Window.__del__(self)

	def SetBaseColor(self, color):
		self.Base.SetColor(color)

	def SetSize(self, width, height):
		width = max(self.CORNER_WIDTH*2, width)
		height = max(self.CORNER_HEIGHT*2, height)
		Window.SetSize(self, width, height)

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
		self.Base.SetSize(width - self.CORNER_WIDTH*2, height - self.CORNER_HEIGHT*2)

	def ShowInternal(self):
		self.Base.Show()
		for wnd in self.Lines:
			wnd.Show()
		for wnd in self.Corners:
			wnd.Show()

	def HideInternal(self):
		self.Base.Hide()
		for wnd in self.Lines:
			wnd.Hide()
		for wnd in self.Corners:
			wnd.Hide()

	def SetAlpha(self, alpha):
		color = grp.GenerateColor(0.0, 0.0, 0.0, alpha)
		self.Base.SetColor(color)

class ThinBoardNew(Window):
	CORNER_WIDTH = 4
	CORNER_HEIGHT = 4
	LINE_WIDTH = 4
	LINE_HEIGHT = 4
	BOARD_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 0.43)

	BOARD_COLOR_IN = grp.GenerateColor(0.0, 0.0, 0.7, 0.7)
	BOARD_COLOR_OUT = grp.GenerateColor(0.0, 0.0, 0.0, 0.43)

	LT = 0
	LB = 1
	RT = 2
	RB = 3
	L = 0
	R = 1
	T = 2
	B = 3

	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		self.ButtonText = None
		CornerFileNames = [ "d:/ymir work/ui/pattern/thinboardcircle/ThinBoard_Corner_"+dir+"_circle.tga" for dir in ["LeftTop","LeftBottom","RightTop","RightBottom"] ]
		LineFileNames = [ "d:/ymir work/ui/pattern/thinboardcircle/ThinBoard_Line_"+dir+"_circle.tga" for dir in ["Left","Right","Top","Bottom"] ]

		self.Corners = []
		for fileName in CornerFileNames:
			Corner = ExpandedImageBox()
			Corner.AddFlag("attach")
			Corner.AddFlag("not_pick")
			Corner.LoadImage(fileName)
			Corner.SetParent(self)
			Corner.SetPosition(0, 0)
			Corner.Show()
			self.Corners.append(Corner)

		self.Lines = []
		for fileName in LineFileNames:
			Line = ExpandedImageBox()
			Line.AddFlag("attach")
			Line.AddFlag("not_pick")
			Line.LoadImage(fileName)
			Line.SetParent(self)
			Line.SetPosition(0, 0)
			Line.Show()
			self.Lines.append(Line)

		Base = Bar()
		Base.SetParent(self)
		Base.AddFlag("attach")
		Base.AddFlag("not_pick")
		Base.SetPosition(self.CORNER_WIDTH, self.CORNER_HEIGHT)
		Base.SetColor(self.BOARD_COLOR)
		Base.Show()
		self.Base = Base

		self.Lines[self.L].SetPosition(0, self.CORNER_HEIGHT)
		self.Lines[self.T].SetPosition(self.CORNER_WIDTH, 0)

	def __del__(self):
		Window.__del__(self)

	def Destroy(self):
		self.ButtonText = 0
		self.Base = 0
		self.Lines = 0
		self.Corners = 0
		self.CORNER_WIDTH = 0
		self.CORNER_HEIGHT = 0
		self.LINE_WIDTH = 0
		self.LINE_HEIGHT = 0
		self.BOARD_COLOR = 0
		self.LT = 0
		self.LB = 0
		self.RT = 0
		self.RB = 0
		self.L = 0
		self.R = 0
		self.T = 0
		self.B = 0

	def GetText(self):
		if not self.ButtonText:
			return ""
		return self.ButtonText.GetText()

	def SetTextColor(self, color):
		if not self.ButtonText:
			return
		self.ButtonText.SetPackedFontColor(color)

	def SetText(self, text, height = 4):
		if not self.ButtonText:
			textLine = TextLine()
			textLine.SetParent(self)
			textLine.SetPosition(self.GetWidth()/2, self.GetHeight()/2)
			textLine.SetVerticalAlignCenter()
			textLine.SetHorizontalAlignCenter()
			textLine.Show()
			self.ButtonText = textLine
		self.ButtonText.SetText(text)

	def SetFontName(self, font):
		if self.ButtonText:
			self.ButtonText.SetFontName(font)

	def SetColor(self, color):
		#self.BOARD_COLOR = color
		self.Base.SetColor(color)

	def SetAlpha(self, alpha):
		color  = grp.GenerateColor(0.0, 0.0, 0.0, alpha)
		self.Base.SetColor(color)

	def SetSize(self, width, height):

		#width = max(self.CORNER_WIDTH*2, width)
		#height = max(self.CORNER_HEIGHT*2, height)
		Window.SetSize(self, width, height)

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
		self.Base.SetSize(width - self.CORNER_WIDTH*2, height - self.CORNER_HEIGHT*2)

	def ShowInternal(self):
		self.Base.Show()
		for wnd in self.Lines:
			wnd.Show()
		for wnd in self.Corners:
			wnd.Show()

	def HideInternal(self):
		self.Base.Hide()
		for wnd in self.Lines:
			wnd.Hide()
		for wnd in self.Corners:
			wnd.Hide()


class Select(Button):
	def __init__(self):
		Button.__init__(self)

		self.eventUp = None
		self.eventDown = None
		self.eventDownArgs = None

	def __del__(self):
		Button.__del__(self)

		self.eventUp = None
		self.eventDown = None
		self.eventDownArgs = None

	def SetToggleDownEvent(self, event, args):
		self.eventDown = event
		self.eventDownArgs = args

	def SetToggleUpEvent(self, event):
		self.eventUp = event

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterToggleButton(self, layer)

	def OnToggleUp(self):
		if self.eventUp:
			self.eventUp()

	def OnToggleDown(self):
		if self.eventDown:
			self.eventDown(self.eventDownArgs)

class ScrollBar(Window):

	SCROLLBAR_WIDTH = 17
	SCROLLBAR_MIDDLE_HEIGHT = 9
	SCROLLBAR_BUTTON_WIDTH = 17
	SCROLLBAR_BUTTON_HEIGHT = 17
	MIDDLE_BAR_POS = 5
	MIDDLE_BAR_UPPER_PLACE = 3
	MIDDLE_BAR_DOWNER_PLACE = 4
	TEMP_SPACE = MIDDLE_BAR_UPPER_PLACE + MIDDLE_BAR_DOWNER_PLACE

	class MiddleBar(DragButton):
		def __init__(self):
			DragButton.__init__(self)
			self.AddFlag("movable")
			#self.AddFlag("restrict_x")

		def MakeImage(self):
			top = ImageBox()
			top.SetParent(self)
			top.LoadImage("d:/ymir work/ui/pattern/ScrollBar_Top.tga")
			top.SetPosition(0, 0)
			top.AddFlag("not_pick")
			top.Show()
			bottom = ImageBox()
			bottom.SetParent(self)
			bottom.LoadImage("d:/ymir work/ui/pattern/ScrollBar_Bottom.tga")
			bottom.AddFlag("not_pick")
			bottom.Show()

			middle = ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage("d:/ymir work/ui/pattern/ScrollBar_Middle.tga")
			middle.SetPosition(0, 4)
			middle.AddFlag("not_pick")
			middle.Show()

			self.top = top
			self.bottom = bottom
			self.middle = middle

		def SetSize(self, height):
			height = max(12, height)
			DragButton.SetSize(self, 10, height)
			self.bottom.SetPosition(0, height-4)

			height -= 4*3
			self.middle.SetRenderingRect(0, 0, 0, float(height)/4.0)

	def __init__(self):
		Window.__init__(self)

		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = lambda *arg: None
		self.lockFlag = False
		self.scrollStep = 0.20

		self.CreateScrollBar()

	def __del__(self):
		Window.__del__(self)

	def CreateScrollBar(self):
		barSlot = Bar3D()
		barSlot.SetParent(self)
		barSlot.AddFlag("not_pick")
		barSlot.Show()

		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.MakeImage()
		middleBar.SetSize(12)

		upButton = Button()
		upButton.SetParent(self)
		upButton.SetEvent(__mem_func__(self.OnUp))
		upButton.SetUpVisual("d:/ymir work/ui/public/scrollbar_up_button_01.sub")
		upButton.SetOverVisual("d:/ymir work/ui/public/scrollbar_up_button_02.sub")
		upButton.SetDownVisual("d:/ymir work/ui/public/scrollbar_up_button_03.sub")
		upButton.Show()

		downButton = Button()
		downButton.SetParent(self)
		downButton.SetEvent(__mem_func__(self.OnDown))
		downButton.SetUpVisual("d:/ymir work/ui/public/scrollbar_down_button_01.sub")
		downButton.SetOverVisual("d:/ymir work/ui/public/scrollbar_down_button_02.sub")
		downButton.SetDownVisual("d:/ymir work/ui/public/scrollbar_down_button_03.sub")
		downButton.Show()

		self.upButton = upButton
		self.downButton = downButton
		self.middleBar = middleBar
		self.barSlot = barSlot

		self.SCROLLBAR_WIDTH = self.upButton.GetWidth()
		self.SCROLLBAR_MIDDLE_HEIGHT = self.middleBar.GetHeight()
		self.SCROLLBAR_BUTTON_WIDTH = self.upButton.GetWidth()
		self.SCROLLBAR_BUTTON_HEIGHT = self.upButton.GetHeight()

		if app.ENABLE_MOUSEWHEEL_EVENT:
			self.upButton.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.downButton.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.middleBar.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.barSlot.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)

	if app.ENABLE_MOUSEWHEEL_EVENT:
		def OnMouseWheelScroll_ScrollBar(self, mode):
			eventDct = { "UP" : lambda : self.SetPos(self.curPos - (self.scrollStep/4)) , "DOWN" : lambda: self.SetPos(self.curPos + (self.scrollStep/4)) }

			if mode in eventDct:
				eventDct[mode]()

	def Destroy(self):
		self.middleBar = None
		self.upButton = None
		self.downButton = None
		self.eventScroll = lambda *arg: None

	def SetScrollEvent(self, event):
		self.eventScroll = event

	def SetMiddleBarSize(self, pageScale):
		realHeight = self.GetHeight() - self.SCROLLBAR_BUTTON_HEIGHT*2
		self.SCROLLBAR_MIDDLE_HEIGHT = int(pageScale * float(realHeight))
		self.middleBar.SetSize(self.SCROLLBAR_MIDDLE_HEIGHT)
		self.pageSize = (self.GetHeight() - self.SCROLLBAR_BUTTON_HEIGHT*2) - self.SCROLLBAR_MIDDLE_HEIGHT - (self.TEMP_SPACE)

	def SetScrollBarSize(self, height):
		self.pageSize = (height - self.SCROLLBAR_BUTTON_HEIGHT*2) - self.SCROLLBAR_MIDDLE_HEIGHT - (self.TEMP_SPACE)
		self.SetSize(self.SCROLLBAR_WIDTH, height)
		self.upButton.SetPosition(0, 0)
		self.downButton.SetPosition(0, height - self.SCROLLBAR_BUTTON_HEIGHT)
		self.middleBar.SetRestrictMovementArea(self.MIDDLE_BAR_POS, self.SCROLLBAR_BUTTON_HEIGHT + self.MIDDLE_BAR_UPPER_PLACE, self.MIDDLE_BAR_POS+2, height - self.SCROLLBAR_BUTTON_HEIGHT*2 - self.TEMP_SPACE)
		self.middleBar.SetPosition(self.MIDDLE_BAR_POS, 0)

		self.UpdateBarSlot()

	def UpdateBarSlot(self):
		self.barSlot.SetPosition(0, self.SCROLLBAR_BUTTON_HEIGHT)
		self.barSlot.SetSize(self.GetWidth() - 2, self.GetHeight() - self.SCROLLBAR_BUTTON_HEIGHT*2 - 2)
	if app.ENABLE_IKASHOP_RENEWAL:
		def UpdateScrollbarLenght(self, scrollableSpace):
			minheight = self.GetHeight() - self.downButton.GetHeight()*2
			scrollable = max(minheight, scrollableSpace)
			scale = float(scrollable) / max(1, minheight)
			scale = 1.0 / max(1.0, scale)
			scale = max(0.08, scale)
			self.SetScrollStep(scale/3.0)
			self.SetMiddleBarSize(scale)


	def GetPos(self):
		return self.curPos

	def SetPos(self, pos):
		pos = max(0.0, pos)
		pos = min(1.0, pos)

		newPos = float(self.pageSize) * pos
		self.middleBar.SetPosition(self.MIDDLE_BAR_POS, int(newPos) + self.SCROLLBAR_BUTTON_HEIGHT + self.MIDDLE_BAR_UPPER_PLACE)
		self.OnMove()

	def SetScrollStep(self, step):
		self.scrollStep = step

	def GetScrollStep(self):
		return self.scrollStep

	def OnUp(self):
		self.SetPos(self.curPos-self.scrollStep)

	def OnDown(self):
		self.SetPos(self.curPos+self.scrollStep)

	def OnMove(self):

		if self.lockFlag:
			return

		if 0 == self.pageSize:
			return

		(xLocal, yLocal) = self.middleBar.GetLocalPosition()
		self.curPos = float(yLocal - self.SCROLLBAR_BUTTON_HEIGHT - self.MIDDLE_BAR_UPPER_PLACE) / float(self.pageSize)

		self.eventScroll()

	def OnMouseLeftButtonDown(self):
		self.bDragging = True
		self.__ScrollToMouse()
		return True

	def OnMouseLeftButtonUp(self):
		self.bDragging = False
		return True

	def OnUpdate(self):
		if getattr(self, "bDragging", False):
			if not wndMgr.IsLButtonDown():
				self.bDragging = False
				return
			self.__ScrollToMouse()

	def __ScrollToMouse(self):
		if self.lockFlag or not self.pageSize:
			return
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		pickedPos = yMouseLocalPosition - self.SCROLLBAR_BUTTON_HEIGHT - self.SCROLLBAR_MIDDLE_HEIGHT/2
		newPos = max(0.0, min(1.0, float(pickedPos) / float(max(1, self.pageSize))))
		self.SetPos(newPos)

	def LockScroll(self):
		self.lockFlag = True

	def UnlockScroll(self):
		self.lockFlag = False

class ScrollBar2(Window):
	SCROLLBAR_WIDTH = 13
	SCROLLBAR_MIDDLE_HEIGHT = 1
	SCROLLBAR_BUTTON_WIDTH = 17
	SCROLLBAR_BUTTON_HEIGHT = 17
	SCROLL_BTN_XDIST = 2
	SCROLL_BTN_YDIST = 2

	class MiddleBar(DragButton):
		def __init__(self):
			DragButton.__init__(self)
			self.AddFlag("movable")
			self.AddFlag("animate")

			self.SetWindowName("scrollbar_middlebar")

		def MakeImage(self):
			top = ImageBox()
			top.SetParent(self)
			top.LoadImage("d:/ymir work/battle_pass/scrollbar/scrollbar_middle_top.tga")
			top.AddFlag("not_pick")
			top.Show()
			topScale = ExpandedImageBox()
			topScale.SetParent(self)
			topScale.SetPosition(0, top.GetHeight())
			topScale.LoadImage("d:/ymir work/battle_pass/scrollbar/scrollbar_middle_topscale.tga")
			topScale.AddFlag("not_pick")
			topScale.Show()

			bottom = ImageBox()
			bottom.SetParent(self)
			bottom.LoadImage("d:/ymir work/battle_pass/scrollbar/scrollbar_middle_bottom.tga")
			bottom.AddFlag("not_pick")
			bottom.Show()
			bottomScale = ExpandedImageBox()
			bottomScale.SetParent(self)
			bottomScale.LoadImage("d:/ymir work/battle_pass/scrollbar/scrollbar_middle_bottomscale.tga")
			bottomScale.AddFlag("not_pick")
			bottomScale.Show()

			middle = ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage("d:/ymir work/battle_pass/scrollbar/scrollbar_middle_middle.tga")
			middle.AddFlag("not_pick")
			middle.Show()

			self.top = top
			self.topScale = topScale
			self.bottom = bottom
			self.bottomScale = bottomScale
			self.middle = middle

		def SetSize(self, height):
			minHeight = self.top.GetHeight() + self.bottom.GetHeight() + self.middle.GetHeight()
			height = max(minHeight, height)
			DragButton.SetSize(self, 10, height)

			scale = (height - minHeight) / 2 
			extraScale = 0
			if (height - minHeight) % 2 == 1:
				extraScale = 1

			self.topScale.SetRenderingRect(0, 0, 0, scale - 1)
			self.middle.SetPosition(0, self.top.GetHeight() + scale)
			self.bottomScale.SetPosition(0, self.middle.GetBottom())
			self.bottomScale.SetRenderingRect(0, 0, 0, scale - 1 + extraScale)
			self.bottom.SetPosition(0, height - self.bottom.GetHeight())

	def __init__(self):
		Window.__init__(self)

		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = None
		self.eventArgs = None
		self.lockFlag = False

		self.CreateScrollBar()
		self.SetScrollBarSize(0)

		self.scrollStep = 0.20
		self.SetWindowName("NONAME_ScrollBar")

	def __del__(self):
		Window.__del__(self)

	def CreateScrollBar(self):
		topImage = ImageBox()
		topImage.SetParent(self)
		topImage.AddFlag("not_pick")
		topImage.LoadImage("d:/ymir work/battle_pass/scrollbar/scrollbar_top.tga")
		topImage.Show()

		bottomImage = ImageBox()
		bottomImage.SetParent(self)
		bottomImage.AddFlag("not_pick")
		bottomImage.LoadImage("d:/ymir work/battle_pass/scrollbar/scrollbar_bottom.tga")
		bottomImage.Show()

		middleImage = ExpandedImageBox()
		middleImage.SetParent(self)
		middleImage.AddFlag("not_pick")
		middleImage.SetPosition(0, topImage.GetHeight())
		middleImage.LoadImage("d:/ymir work/battle_pass/scrollbar/scrollbar_middle.tga")
		middleImage.Show()

		self.topImage = topImage
		self.bottomImage = bottomImage
		self.middleImage = middleImage

		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.MakeImage()
		middleBar.SetSize(0) # set min height
		self.middleBar = middleBar

		if app.ENABLE_MOUSEWHEEL_EVENT:
			self.topImage.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.bottomImage.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.middleImage.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.middleBar.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)

	if app.ENABLE_MOUSEWHEEL_EVENT:
		def OnMouseWheelScroll_ScrollBar(self, mode):
			eventDct = { "UP" : lambda : self.SetPos(self.curPos - (self.scrollStep/4)) , "DOWN" : lambda: self.SetPos(self.curPos + (self.scrollStep/4)) }

			if mode in eventDct:
				eventDct[mode]()

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

		self.middleBar.SetRestrictMovementArea(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST, \
			self.middleBar.GetWidth(), height - self.SCROLL_BTN_YDIST * 2)
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
		self.bDragging = True
		self.__ScrollToMouse()
		return True

	def OnMouseLeftButtonUp(self):
		self.bDragging = False
		return True

	def OnUpdate(self):
		if getattr(self, "bDragging", False):
			if not wndMgr.IsLButtonDown():
				self.bDragging = False
				return
			self.__ScrollToMouse()

	def __ScrollToMouse(self):
		if self.lockFlag or not self.GetHeight():
			return
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		newPos = max(0.0, min(1.0, float(yMouseLocalPosition) / float(self.GetHeight())))
		self.SetPos(newPos)

	def LockScroll(self):
		self.lockFlag = True

	def UnlockScroll(self):
		self.lockFlag = False

class ScrollBarTpw(Window):
	SCROLLBAR_WIDTH = 13
	SCROLLBAR_MIDDLE_HEIGHT = 1
	SCROLLBAR_BUTTON_WIDTH = 17
	SCROLLBAR_BUTTON_HEIGHT = 17
	SCROLL_BTN_XDIST = 2
	SCROLL_BTN_YDIST = 2

	class MiddleBar(DragButton):
		def __init__(self):
			DragButton.__init__(self)
			self.AddFlag("movable")

			self.SetWindowName("scrollbar_middlebar")

		def MakeImage(self):
			top = ExpandedImageBox()
			top.SetParent(self)
			top.LoadImage("d:/ymir work/dungeoninfo/tpw/scroll/scrollbar.tga")
			top.AddFlag("not_pick")
			top.Show()
			topScale = ExpandedImageBox()
			topScale.SetParent(self)
			topScale.SetPosition(0, top.GetHeight())
			topScale.LoadImage("d:/ymir work/dungeoninfo/tpw/scroll/scroll_top.tga")
			topScale.AddFlag("not_pick")
			topScale.Show()

			bottom = ExpandedImageBox()
			bottom.SetParent(self)
			bottom.LoadImage("d:/ymir work/dungeoninfo/tpw/scroll/scrollbar.tga")
			bottom.AddFlag("not_pick")
			bottom.Show()
			bottomScale = ExpandedImageBox()
			bottomScale.SetParent(self)
			bottomScale.LoadImage("d:/ymir work/dungeoninfo/tpw/scroll/scroll_bottom.tga")
			bottomScale.AddFlag("not_pick")
			bottomScale.Show()

			middle = ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage("d:/ymir work/dungeoninfo/tpw/scroll/scrollbar.tga")
			middle.AddFlag("not_pick")
			middle.Show()

			self.top = top
			self.topScale = topScale
			self.bottom = bottom
			self.bottomScale = bottomScale
			self.middle = middle

		def Resize(self, height):
			height = max(12, height)
			DragButton.SetSize(self, 10, height)
			self.bottom.SetPosition(0, height-4)

			height -= 4*3
			self.middle.SetRenderingRect(0, 0, 0, float(height)/4.0)

		def SetSize(self, height):
			minHeight = self.top.GetHeight() + self.bottom.GetHeight() + self.middle.GetHeight()
			height = max(minHeight, height)
			DragButton.SetSize(self, 10, height)

			scale = (height - minHeight) / 2 
			extraScale = 0
			if (height - minHeight) % 2 == 1:
				extraScale = 1

			self.topScale.SetRenderingRect(0, 0, 0, scale - 1)
			self.middle.SetPosition(0, self.top.GetHeight() + scale)
			self.bottomScale.SetPosition(0, self.middle.GetBottom())
			self.bottomScale.SetRenderingRect(0, 0, 0, scale - 1 + extraScale)
			self.bottom.SetPosition(0, height - self.bottom.GetHeight())

	def __init__(self):
		Window.__init__(self)

		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = None
		self.eventArgs = None
		self.lockFlag = False

		self.CreateScrollBar()
		self.SetScrollBarSize(0)

		self.scrollStep = 0.20
		self.SetWindowName("NONAME_ScrollBar")

	def __del__(self):
		Window.__del__(self)

	def CreateScrollBar(self):
		topImage = ExpandedImageBox()
		topImage.SetParent(self)
		topImage.AddFlag("not_pick")
		topImage.LoadImage("d:/ymir work/dungeoninfo/tpw/scroll/scroll_top.tga")
		topImage.Show()

		middleImage = ExpandedImageBox()
		middleImage.SetParent(self)
		middleImage.AddFlag("not_pick")
		middleImage.SetPosition(0, topImage.GetHeight())
		middleImage.LoadImage("d:/ymir work/dungeoninfo/tpw/scroll/scroll_center.tga")
		middleImage.Show()

		bottomImage = ExpandedImageBox()
		bottomImage.SetParent(self)
		bottomImage.AddFlag("not_pick")
		bottomImage.LoadImage("d:/ymir work/dungeoninfo/tpw/scroll/scroll_bottom.tga")
		bottomImage.Show()

		self.topImage = topImage
		self.bottomImage = bottomImage
		self.middleImage = middleImage

		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.MakeImage()
		middleBar.SetSize(0) # set min height
		self.middleBar = middleBar

		if app.ENABLE_MOUSEWHEEL_EVENT:
			self.topImage.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.bottomImage.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.middleImage.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.middleBar.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)

	if app.ENABLE_MOUSEWHEEL_EVENT:
		def OnMouseWheelScroll_ScrollBar(self, mode):
			eventDct = { "UP" : lambda : self.SetPos(self.curPos - (self.scrollStep/4)) , "DOWN" : lambda: self.SetPos(self.curPos + (self.scrollStep/4)) }

			if mode in eventDct:
				eventDct[mode]()

	def Destroy(self):
		self.eventScroll = None
		self.eventArgs = None

	def SetScrollEvent(self, event, *args):
		self.eventScroll = event
		self.eventArgs = args

	def SetMiddleBarSize(self, pageScale):
		self.middleBar.Resize(int(pageScale * float(self.GetHeight() - self.SCROLL_BTN_YDIST*2)))
		realHeight = self.GetHeight() - self.SCROLL_BTN_YDIST*2 - self.middleBar.GetHeight()
		self.pageSize = realHeight

	def SetScrollBarSize(self, height):
		self.SetSize(self.SCROLLBAR_WIDTH, height)

		self.pageSize = height - self.SCROLL_BTN_YDIST*2 - self.middleBar.GetHeight()

		middleImageScale = float((height-3 - self.SCROLL_BTN_YDIST*2) - self.middleImage.GetHeight()) / float(self.middleImage.GetHeight())
		self.middleImage.SetRenderingRect(0, 0, 0, middleImageScale)
		self.bottomImage.SetPosition(0, height-6)

		self.middleBar.SetRestrictMovementArea(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST, \
			self.middleBar.GetWidth(), height - self.SCROLL_BTN_YDIST * 2)
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
		self.bDragging = True
		self.__ScrollToMouse()
		return True

	def OnMouseLeftButtonUp(self):
		self.bDragging = False
		return True

	def OnUpdate(self):
		if getattr(self, "bDragging", False):
			if not wndMgr.IsLButtonDown():
				self.bDragging = False
				return
			self.__ScrollToMouse()

	def __ScrollToMouse(self):
		if self.lockFlag or not self.GetHeight():
			return
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		newPos = max(0.0, min(1.0, float(yMouseLocalPosition) / float(self.GetHeight())))
		self.SetPos(newPos)

	def LockScroll(self):
		self.lockFlag = True

	def UnlockScroll(self):
		self.lockFlag = False

class ScrollBarShop(Window):
	SCROLLBAR_WIDTH = 13
	SCROLLBAR_MIDDLE_HEIGHT = 1
	SCROLLBAR_BUTTON_WIDTH = 17
	SCROLLBAR_BUTTON_HEIGHT = 17
	SCROLL_BTN_XDIST = 2
	SCROLL_BTN_YDIST = 2

	class MiddleBar(DragButton):
		def __init__(self):
			DragButton.__init__(self)
			self.AddFlag("movable")

			self.SetWindowName("scrollbar_middlebar")

		def MakeImage(self):
			top = ExpandedImageBox()
			top.SetParent(self)
			top.LoadImage("cream/searchshop/scrollbar.tga")
			top.AddFlag("not_pick")
			top.Show()
			topScale = ExpandedImageBox()
			topScale.SetParent(self)
			topScale.SetPosition(0, top.GetHeight())
			topScale.LoadImage("cream/searchshop/scroll_top.tga")
			topScale.AddFlag("not_pick")
			topScale.Show()

			bottom = ExpandedImageBox()
			bottom.SetParent(self)
			bottom.LoadImage("cream/searchshop/scrollbar.tga")
			bottom.AddFlag("not_pick")
			bottom.Show()
			bottomScale = ExpandedImageBox()
			bottomScale.SetParent(self)
			bottomScale.LoadImage("cream/searchshop/scroll_bottom.tga")
			bottomScale.AddFlag("not_pick")
			bottomScale.Show()

			middle = ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage("cream/searchshop/scrollbar.tga")
			middle.AddFlag("not_pick")
			middle.Show()

			self.top = top
			self.topScale = topScale
			self.bottom = bottom
			self.bottomScale = bottomScale
			self.middle = middle

		def Resize(self, height):
			height = max(12, height)
			DragButton.SetSize(self, 10, height)
			self.bottom.SetPosition(0, height-4)

			height -= 4*3
			self.middle.SetRenderingRect(0, 0, 0, float(height)/4.0)

		def SetSize(self, height):
			minHeight = self.top.GetHeight() + self.bottom.GetHeight() + self.middle.GetHeight()
			height = max(minHeight, height)
			DragButton.SetSize(self, 10, height)

			scale = (height - minHeight) / 2 
			extraScale = 0
			if (height - minHeight) % 2 == 1:
				extraScale = 1

			self.topScale.SetRenderingRect(0, 0, 0, scale - 1)
			self.middle.SetPosition(0, self.top.GetHeight() + scale)
			self.bottomScale.SetPosition(0, self.middle.GetBottom())
			self.bottomScale.SetRenderingRect(0, 0, 0, scale - 1 + extraScale)
			self.bottom.SetPosition(0, height - self.bottom.GetHeight())

	def __init__(self):
		Window.__init__(self)

		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = None
		self.eventArgs = None
		self.lockFlag = False

		self.CreateScrollBar()
		self.SetScrollBarSize(0)

		self.scrollStep = 0.20
		self.SetWindowName("NONAME_ScrollBar")

	def __del__(self):
		Window.__del__(self)

	def CreateScrollBar(self):
		topImage = ExpandedImageBox()
		topImage.SetParent(self)
		topImage.AddFlag("not_pick")
		topImage.LoadImage("cream/searchshop/scroll_top.tga")
		topImage.Show()

		middleImage = ExpandedImageBox()
		middleImage.SetParent(self)
		middleImage.AddFlag("not_pick")
		middleImage.SetPosition(0, topImage.GetHeight())
		middleImage.LoadImage("cream/searchshop/scroll_center.tga")
		middleImage.Show()

		bottomImage = ExpandedImageBox()
		bottomImage.SetParent(self)
		bottomImage.AddFlag("not_pick")
		bottomImage.LoadImage("cream/searchshop/scroll_bottom.tga")
		bottomImage.Show()

		self.topImage = topImage
		self.bottomImage = bottomImage
		self.middleImage = middleImage

		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.MakeImage()
		middleBar.SetSize(0) # set min height
		self.middleBar = middleBar

		if app.ENABLE_MOUSEWHEEL_EVENT:
			self.topImage.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.bottomImage.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.middleImage.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.middleBar.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)

	if app.ENABLE_MOUSEWHEEL_EVENT:
		def OnMouseWheelScroll_ScrollBar(self, mode):
			eventDct = { "UP" : lambda : self.SetPos(self.curPos - (self.scrollStep/4)) , "DOWN" : lambda: self.SetPos(self.curPos + (self.scrollStep/4)) }

			if mode in eventDct:
				eventDct[mode]()

	def Destroy(self):
		self.eventScroll = None
		self.eventArgs = None

	def SetScrollEvent(self, event, *args):
		self.eventScroll = event
		self.eventArgs = args

	def SetMiddleBarSize(self, pageScale):
		self.middleBar.Resize(int(pageScale * float(self.GetHeight() - self.SCROLL_BTN_YDIST*2)))
		realHeight = self.GetHeight() - self.SCROLL_BTN_YDIST*2 - self.middleBar.GetHeight()
		self.pageSize = realHeight

	def SetScrollBarSize(self, height):
		self.SetSize(self.SCROLLBAR_WIDTH, height)

		self.pageSize = height - self.SCROLL_BTN_YDIST*2 - self.middleBar.GetHeight()

		middleImageScale = float((height-3 - self.SCROLL_BTN_YDIST*2) - self.middleImage.GetHeight()) / float(self.middleImage.GetHeight())
		self.middleImage.SetRenderingRect(0, 0, 0, middleImageScale)
		self.bottomImage.SetPosition(0, height-6)

		self.middleBar.SetRestrictMovementArea(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST, \
			self.middleBar.GetWidth(), height - self.SCROLL_BTN_YDIST * 2)
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
		self.bDragging = True
		self.__ScrollToMouse()
		return True

	def OnMouseLeftButtonUp(self):
		self.bDragging = False
		return True

	def OnUpdate(self):
		if getattr(self, "bDragging", False):
			if not wndMgr.IsLButtonDown():
				self.bDragging = False
				return
			self.__ScrollToMouse()

	def __ScrollToMouse(self):
		if self.lockFlag or not self.GetHeight():
			return
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		newPos = max(0.0, min(1.0, float(yMouseLocalPosition) / float(self.GetHeight())))
		self.SetPos(newPos)

	def LockScroll(self):
		self.lockFlag = True

	def UnlockScroll(self):
		self.lockFlag = False

class ThinScrollBar(ScrollBar):

	def CreateScrollBar(self):
		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.SetUpVisual("d:/ymir work/ui/public/scrollbar_thin_middle_button_01.sub")
		middleBar.SetOverVisual("d:/ymir work/ui/public/scrollbar_thin_middle_button_02.sub")
		middleBar.SetDownVisual("d:/ymir work/ui/public/scrollbar_thin_middle_button_03.sub")

		upButton = Button()
		upButton.SetParent(self)
		upButton.SetUpVisual("d:/ymir work/ui/public/scrollbar_thin_up_button_01.sub")
		upButton.SetOverVisual("d:/ymir work/ui/public/scrollbar_thin_up_button_02.sub")
		upButton.SetDownVisual("d:/ymir work/ui/public/scrollbar_thin_up_button_03.sub")
		upButton.SetEvent(__mem_func__(self.OnUp))
		upButton.Show()

		downButton = Button()
		downButton.SetParent(self)
		downButton.SetUpVisual("d:/ymir work/ui/public/scrollbar_thin_down_button_01.sub")
		downButton.SetOverVisual("d:/ymir work/ui/public/scrollbar_thin_down_button_02.sub")
		downButton.SetDownVisual("d:/ymir work/ui/public/scrollbar_thin_down_button_03.sub")
		downButton.SetEvent(__mem_func__(self.OnDown))
		downButton.Show()

		self.middleBar = middleBar
		self.upButton = upButton
		self.downButton = downButton

		self.SCROLLBAR_WIDTH = self.upButton.GetWidth()
		self.SCROLLBAR_MIDDLE_HEIGHT = self.middleBar.GetHeight()
		self.SCROLLBAR_BUTTON_WIDTH = self.upButton.GetWidth()
		self.SCROLLBAR_BUTTON_HEIGHT = self.upButton.GetHeight()
		self.MIDDLE_BAR_POS = 0
		self.MIDDLE_BAR_UPPER_PLACE = 0
		self.MIDDLE_BAR_DOWNER_PLACE = 0
		self.TEMP_SPACE = 0

		if app.ENABLE_MOUSEWHEEL_EVENT:
			self.middleBar.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.upButton.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.downButton.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)

	def UpdateBarSlot(self):
		pass

class NewScrollBar(Window):

	SCROLLBAR_WIDTH = 13
	SCROLLBAR_MIDDLE_HEIGHT = 1
	SCROLLBAR_BUTTON_WIDTH = 17
	SCROLLBAR_BUTTON_HEIGHT = 17
	SCROLL_BTN_XDIST = 1
	SCROLL_BTN_YDIST = 2

	class MiddleBar(DragButton):
		def __init__(self):
			DragButton.__init__(self)
			self.AddFlag("movable")

			self.SetWindowName("NONAME_ScrollBar_MiddleBar")

		def MakeImage(self):
			top = ImageBox()
			top.SetParent(self)
			top.LoadImage("d:/ymir work/ui/pattern/slimscroll/ScrollBar_Middle_Top_bottom.tga")
			top.AddFlag("not_pick")
			top.SetPosition(0, 0)
			top.Show()
			topScale = ExpandedImageBox()
			topScale.SetParent(self)
			topScale.SetPosition(0, top.GetHeight())
			topScale.LoadImage("d:/ymir work/ui/pattern/slimscroll/ScrollBar_Middle_TopScale.tga")
			topScale.AddFlag("not_pick")
			topScale.Show()

			bottom = ImageBox()
			bottom.SetParent(self)
			bottom.LoadImage("d:/ymir work/ui/pattern/slimscroll/ScrollBar_Middle_Top_bottom.tga")
			bottom.AddFlag("not_pick")
			bottom.Show()
			bottomScale = ExpandedImageBox()
			bottomScale.SetParent(self)
			bottomScale.LoadImage("d:/ymir work/ui/pattern/slimscroll/ScrollBar_Middle_TopScale.tga")
			bottomScale.AddFlag("not_pick")
			bottomScale.Show()

			middle = ExpandedImageBox()
			middle.SetParent(self)
			middle.LoadImage("d:/ymir work/ui/pattern/slimscroll/ScrollBar_Middle_Middle.tga")
			middle.AddFlag("not_pick")
			middle.Show()

			self.top = top
			self.topScale = topScale
			self.bottom = bottom
			self.bottomScale = bottomScale
			self.middle = middle

		def SetSize(self, height):
			minHeight = self.top.GetHeight() + self.bottom.GetHeight() + self.middle.GetHeight()
			height = max(minHeight, height)
			DragButton.SetSize(self, 10, height)

			scale = (height - minHeight) / 2
			extraScale = 0
			if (height - minHeight) % 2 == 1:
				extraScale = 1

			self.topScale.SetRenderingRect(0, 0, 0, scale - 1)
			self.middle.SetPosition(0, self.top.GetHeight() + scale)
			self.bottomScale.SetPosition(0, self.middle.GetBottom())
			self.bottomScale.SetRenderingRect(0, 0, 0, scale - 1 + extraScale)
			self.bottom.SetPosition(0, height - self.bottom.GetHeight())

	def __init__(self):
		Window.__init__(self)

		self.pageSize = 1
		self.curPos = 0.0
		self.eventScroll = None
		self.eventArgs = None
		self.lockFlag = False

		self.CreateScrollBar()
		self.SetScrollBarSize(0)

		self.scrollStep = 0.20
		self.SetWindowName("NONAME_ScrollBar")

	def __del__(self):
		Window.__del__(self)

	def CreateScrollBar(self):
		middleImage = ExpandedImageBox()
		middleImage.SetParent(self)
		middleImage.AddFlag("not_pick")
		middleImage.SetPosition(0, 1)
		middleImage.LoadImage("d:/ymir work/ui/pattern/slimscroll/SlimScrollBar_Middle.tga")
		middleImage.Show()
		self.middleImage = middleImage

		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(__mem_func__(self.OnMove))
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

		self.middleBar.SetRestrictMovementArea(self.SCROLL_BTN_XDIST, self.SCROLL_BTN_YDIST, \
			self.middleBar.GetWidth(), height - self.SCROLL_BTN_YDIST * 2)
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
		self.bDragging = True
		self.__ScrollToMouse()
		return True

	def OnMouseLeftButtonUp(self):
		self.bDragging = False
		return True

	def OnUpdate(self):
		if getattr(self, "bDragging", False):
			if not wndMgr.IsLButtonDown():
				self.bDragging = False
				return
			self.__ScrollToMouse()

	def __ScrollToMouse(self):
		if self.lockFlag or not self.GetHeight():
			return
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		newPos = max(0.0, min(1.0, float(yMouseLocalPosition) / float(self.GetHeight())))
		self.SetPos(newPos)

	def LockScroll(self):
		self.lockFlag = True

	def UnlockScroll(self):
		self.lockFlag = False

class SmallThinScrollBar(ScrollBar):

	def CreateScrollBar(self):
		middleBar = self.MiddleBar()
		middleBar.SetParent(self)
		middleBar.SetMoveEvent(__mem_func__(self.OnMove))
		middleBar.Show()
		middleBar.SetUpVisual("d:/ymir work/ui/public/scrollbar_small_thin_middle_button_01.sub")
		middleBar.SetOverVisual("d:/ymir work/ui/public/scrollbar_small_thin_middle_button_01.sub")
		middleBar.SetDownVisual("d:/ymir work/ui/public/scrollbar_small_thin_middle_button_01.sub")

		upButton = Button()
		upButton.SetParent(self)
		upButton.SetUpVisual("d:/ymir work/ui/public/scrollbar_small_thin_up_button_01.sub")
		upButton.SetOverVisual("d:/ymir work/ui/public/scrollbar_small_thin_up_button_02.sub")
		upButton.SetDownVisual("d:/ymir work/ui/public/scrollbar_small_thin_up_button_03.sub")
		upButton.SetEvent(__mem_func__(self.OnUp))
		upButton.Show()

		downButton = Button()
		downButton.SetParent(self)
		downButton.SetUpVisual("d:/ymir work/ui/public/scrollbar_small_thin_down_button_01.sub")
		downButton.SetOverVisual("d:/ymir work/ui/public/scrollbar_small_thin_down_button_02.sub")
		downButton.SetDownVisual("d:/ymir work/ui/public/scrollbar_small_thin_down_button_03.sub")
		downButton.SetEvent(__mem_func__(self.OnDown))
		downButton.Show()

		self.middleBar = middleBar
		self.upButton = upButton
		self.downButton = downButton

		self.SCROLLBAR_WIDTH = self.upButton.GetWidth()
		self.SCROLLBAR_MIDDLE_HEIGHT = self.middleBar.GetHeight()
		self.SCROLLBAR_BUTTON_WIDTH = self.upButton.GetWidth()
		self.SCROLLBAR_BUTTON_HEIGHT = self.upButton.GetHeight()
		self.MIDDLE_BAR_POS = 0
		self.MIDDLE_BAR_UPPER_PLACE = 0
		self.MIDDLE_BAR_DOWNER_PLACE = 0
		self.TEMP_SPACE = 0

		if app.ENABLE_MOUSEWHEEL_EVENT:
			self.middleBar.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.upButton.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.downButton.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)
			self.SetMouseWheelScrollEvent(self.OnMouseWheelScroll_ScrollBar)

	def UpdateBarSlot(self):
		pass

class SliderBar(Window):

	def __init__(self):
		Window.__init__(self)

		self.curPos = 1.0
		self.pageSize = 1.0
		self.eventChange = None
		self.bDragging = False
		self.cursor_y = 0

		self.__CreateBackGroundImage()
		self.__CreateCursor()

	def __del__(self):
		Window.__del__(self)

	def __CreateBackGroundImage(self):
		if app.ENABLE_NEW_GAMEOPTION:
			img = ExpandedImageBox()
		else:
			img = ImageBox()
		img.SetParent(self)
		img.AddFlag("not_pick")
		img.LoadImage("d:/ymir work/ui/game/windows/sliderbar.sub")
		img.Show()
		self.backGroundImage = img

		h = max(34, self.backGroundImage.GetHeight())
		self.SetSize(self.backGroundImage.GetWidth(), h)
		self.bar_y = (h - self.backGroundImage.GetHeight()) / 2
		self.backGroundImage.SetPosition(0, self.bar_y)

	def __CreateCursor(self):
		cursor = DragButton()
		cursor.AddFlag("movable")
		cursor.AddFlag("restrict_y")
		cursor.SetParent(self)
		cursor.SetMoveEvent(__mem_func__(self.__OnMove))
		cursor.SetUpVisual("d:/ymir work/ui/game/windows/sliderbar_cursor.sub")
		cursor.SetOverVisual("d:/ymir work/ui/game/windows/sliderbar_cursor.sub")
		cursor.SetDownVisual("d:/ymir work/ui/game/windows/sliderbar_cursor.sub")
		try:
			cursor.SetButtonScale(1.35, 1.35)
		except:
			pass
		cursor.Show()
		self.cursor = cursor

		self.cursor_y = self.bar_y + (self.backGroundImage.GetHeight() - self.cursor.GetHeight()) / 2
		self.cursor.SetRestrictMovementArea(0, self.cursor_y, self.backGroundImage.GetWidth(), max(1, self.cursor.GetHeight()))
		self.pageSize = max(1, self.backGroundImage.GetWidth() - self.cursor.GetWidth())

	def __OnMove(self):
		(xLocal, yLocal) = self.cursor.GetLocalPosition()
		self.curPos = max(0.0, min(1.0, float(xLocal) / float(max(1, self.pageSize))))

		if self.eventChange:
			self.eventChange()

	def SetSliderPos(self, pos):
		self.curPos = max(0.0, min(1.0, float(pos)))
		cursor_y = getattr(self, "cursor_y", 0)
		self.cursor.SetPosition(int(self.pageSize * self.curPos), cursor_y)

	def GetSliderPos(self):
		return self.curPos

	def SetEvent(self, event):
		self.eventChange = event

	def Enable(self):
		self.cursor.Show()

	def Disable(self):
		self.cursor.Hide()

	def OnMouseLeftButtonDown(self):
		self.bDragging = True
		self.__UpdateFromMouse()
		return True

	def OnMouseLeftButtonUp(self):
		self.bDragging = False
		return True

	def OnUpdate(self):
		if getattr(self, "bDragging", False):
			self.__UpdateFromMouse()

	def __UpdateFromMouse(self):
		(x, y) = self.GetMouseLocalPosition()
		half = self.cursor.GetWidth() / 2
		newPos = max(0.0, min(1.0, float(x - half) / float(max(1, self.pageSize))))
		self.SetSliderPos(newPos)
		if self.eventChange:
			self.eventChange()

class MouseReflector(Window):
	def __init__(self, parent):
		Window.__init__(self)
		self.SetParent(parent)
		self.AddFlag("not_pick")
		self.width = self.height = 0
		self.isDown = False
	def __del__(self):
		Window.__del__(self)
	def Down(self):
		self.isDown = True
	def Up(self):
		self.isDown = False
	def OnRender(self):
		if self.isDown:
			grp.SetColor(WHITE_COLOR)
		else:
			grp.SetColor(HALF_WHITE_COLOR)
		x, y = self.GetGlobalPosition()
		grp.RenderBar(x + 2, y + 2, self.GetWidth() - 4, self.GetHeight() - 4)
	
class CheckBoxNew(ImageBox):
	def __init__(self, parent, x, y, event, filename = "d:/ymir work/ui/chat/chattingoption_check_box_off.sub"):
		ImageBox.__init__(self)
		self.SetParent(parent)
		self.SetPosition(x, y)
		self.LoadImage(filename)
		self.mouseReflector = MouseReflector(self)
		self.mouseReflector.SetSize(self.GetWidth(), self.GetHeight())
		image = MakeImageBox(self, "d:/ymir work/ui/public/check_image.sub", 0, 0)
		image.AddFlag("not_pick")
		image.SetWindowHorizontalAlignCenter()
		image.SetWindowVerticalAlignCenter()
		image.Hide()
		self.check = False
		self.enable = True
		self.image = image
		self.event = event
		self.Show()
		self.mouseReflector.UpdateRect()
	def __del__(self):
		ImageBox.__del__(self)
	def GetCheck(self):
		return self.check
	def SetCheck(self, flag):
		if flag:
			self.check = True
			self.image.Show()
		else:
			self.check = False
			self.image.Hide()
	def Disable(self):
		self.enable = False
	def OnMouseOverIn(self):
		if not self.enable:
			return
		self.mouseReflector.Show()
	def OnMouseOverOut(self):
		if not self.enable:
			return
		self.mouseReflector.Hide()
	def OnMouseLeftButtonDown(self):
		if not self.enable:
			return
		self.mouseReflector.Down()
	def OnMouseLeftButtonUp(self):
		if not self.enable:
			return
		self.mouseReflector.Up()
		self.event()

class CheckBoxRefine(Window):
	def __init__(self):
		Window.__init__(self)

		self.backgroundImage = None
		self.checkImage = None

		self.eventFunc = { "ON_CHECK" : None, "ON_UNCKECK" : None, }
		self.eventArgs = { "ON_CHECK" : None, "ON_UNCKECK" : None, }

		self.CreateElements()

	def __del__(self):
		Window.__del__(self)

		self.backgroundImage = None
		self.checkImage = None

		self.eventFunc = { "ON_CHECK" : None, "ON_UNCKECK" : None, }
		self.eventArgs = { "ON_CHECK" : None, "ON_UNCKECK" : None, }

	def CreateElements(self):
		self.backgroundImage = ImageBox()
		self.backgroundImage.SetParent(self)
		self.backgroundImage.AddFlag("not_pick")
		self.backgroundImage.LoadImage("refine/checkbox.tga")
		self.backgroundImage.Show()

		self.checkImage = ImageBox()
		self.checkImage.SetParent(self)
		self.checkImage.AddFlag("not_pick")
		self.checkImage.SetPosition(0, -4)
		self.checkImage.LoadImage("refine/checked.tga")
		self.checkImage.Hide()

		self.textInfo = TextLine()
		self.textInfo.SetParent(self)
		self.textInfo.SetPosition(20, -2)
		self.textInfo.Show()

		self.SetSize(self.backgroundImage.GetWidth() + self.textInfo.GetTextSize()[0], self.backgroundImage.GetHeight() + self.textInfo.GetTextSize()[1])

	def SetTextInfo(self, info):
		if self.textInfo:
			self.textInfo.SetText(info)

		self.SetSize(self.backgroundImage.GetWidth() + self.textInfo.GetTextSize()[0], self.backgroundImage.GetHeight() + self.textInfo.GetTextSize()[1])

	def SetCheckStatus(self, flag):
		if flag:
			self.checkImage.Show()
		else:
			self.checkImage.Hide()

	def GetCheckStatus(self):
		if self.checkImage:
			return self.checkImage.IsShow()

		return False

	def SetEvent(self, func, *args) :
		result = self.eventFunc.has_key(args[0])
		if result :
			self.eventFunc[args[0]] = func
			self.eventArgs[args[0]] = args
		else :
			print "[ERROR] ui.py SetEvent, Can`t Find has_key : %s" % args[0]

	def OnMouseLeftButtonUp(self):
		if self.checkImage:
			if self.checkImage.IsShow():
				self.checkImage.Hide()

				if self.eventFunc["ON_UNCKECK"]:
					apply(self.eventFunc["ON_UNCKECK"], self.eventArgs["ON_UNCKECK"])
			else:
				self.checkImage.Show()

				if self.eventFunc["ON_CHECK"]:
					apply(self.eventFunc["ON_CHECK"], self.eventArgs["ON_CHECK"])

class CheckBoxBio(Window):
	def __init__(self):
		Window.__init__(self)

		self.backgroundImage = None
		self.checkImage = None

		self.eventFunc = { "ON_CHECK" : None, "ON_UNCKECK" : None, }
		self.eventArgs = { "ON_CHECK" : None, "ON_UNCKECK" : None, }

		self.CreateElements()

	def __del__(self):
		Window.__del__(self)

		self.backgroundImage = None
		self.checkImage = None

		self.eventFunc = { "ON_CHECK" : None, "ON_UNCKECK" : None, }
		self.eventArgs = { "ON_CHECK" : None, "ON_UNCKECK" : None, }

	def CreateElements(self):
		self.backgroundImage = ImageBox()
		self.backgroundImage.SetParent(self)
		self.backgroundImage.AddFlag("not_pick")
		self.backgroundImage.SetPosition(0, 0)
		self.backgroundImage.LoadImage("d:/ymir work/ui/game/bio/checkbox.png")
		self.backgroundImage.Show()

		self.checkImage = ImageBox()
		self.checkImage.SetParent(self)
		self.checkImage.AddFlag("not_pick")
		self.checkImage.SetPosition(0, 0)
		self.checkImage.LoadImage("d:/ymir work/ui/game/bio/checked.png")
		self.checkImage.Hide()

		self.textInfo = TextLine()
		self.textInfo.SetParent(self)
		self.textInfo.SetPosition(20, -2)
		self.textInfo.Show()

		# self.SetSize(self.backgroundImage.GetWidth() + self.textInfo.GetTextSize()[0], self.backgroundImage.GetHeight() + self.textInfo.GetTextSize()[1])
		self.SetSize(self.backgroundImage.GetWidth(), self.backgroundImage.GetHeight())

	def SetTextInfo(self, info):
		if self.textInfo:
			self.textInfo.SetText(info)

		# self.SetSize(self.backgroundImage.GetWidth() + self.textInfo.GetTextSize()[0], self.backgroundImage.GetHeight() + self.textInfo.GetTextSize()[1])
		self.SetSize(self.backgroundImage.GetWidth(), self.backgroundImage.GetHeight())

	def SetCheckStatus(self, flag):
		if flag:
			self.checkImage.Show()
		else:
			self.checkImage.Hide()

	def GetCheckStatus(self):
		if self.checkImage:
			return self.checkImage.IsShow()

		return False

	def SetEvent(self, func, *args) :
		result = self.eventFunc.has_key(args[0])
		if result :
			self.eventFunc[args[0]] = func
			self.eventArgs[args[0]] = args
		else :
			print "[ERROR] ui.py SetEvent, Can`t Find has_key : %s" % args[0]

	def OnMouseLeftButtonUp(self):
		if self.checkImage:
			if self.checkImage.IsShow():
				self.checkImage.Hide()

				if self.eventFunc["ON_UNCKECK"]:
					apply(self.eventFunc["ON_UNCKECK"], self.eventArgs["ON_UNCKECK"])
			else:
				self.checkImage.Show()

				if self.eventFunc["ON_CHECK"]:
					apply(self.eventFunc["ON_CHECK"], self.eventArgs["ON_CHECK"])

class ListBox(Window):

	TEMPORARY_PLACE = 3

	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		self.overLine = -1
		self.selectedLine = -1
		self.width = 0
		self.height = 0
		self.stepSize = 17
		self.basePos = 0
		self.showLineCount = 0
		self.itemCenterAlign = True
		self.itemList = []
		self.keyDict = {}
		self.textDict = {}
		self.event = lambda *arg: None
	def __del__(self):
		Window.__del__(self)

	def SetWidth(self, width):
		self.SetSize(width, self.height)

	def SetSize(self, width, height):
		Window.SetSize(self, width, height)
		self.width = width
		self.height = height

	def SetTextCenterAlign(self, flag):
		self.itemCenterAlign = flag

	def SetBasePos(self, pos):
		self.basePos = pos
		self._LocateItem()

	def ClearItem(self):
		self.keyDict = {}
		self.textDict = {}
		self.itemList = []
		self.overLine = -1
		self.selectedLine = -1

	def InsertItem(self, number, text):
		self.keyDict[len(self.itemList)] = number
		self.textDict[len(self.itemList)] = text

		textLine = TextLine()
		textLine.SetParent(self)
		textLine.SetText(text)
		textLine.Show()

		if self.itemCenterAlign:
			textLine.SetWindowHorizontalAlignCenter()
			textLine.SetHorizontalAlignCenter()

		self.itemList.append(textLine)

		self._LocateItem()

	def ChangeItem(self, number, text):
		for key, value in self.keyDict.items():
			if value == number:
				self.textDict[key] = text

				if number < len(self.itemList):
					self.itemList[key].SetText(text)

				return

	def LocateItem(self):
		self._LocateItem()

	def _LocateItem(self):

		skipCount = self.basePos
		yPos = 0
		self.showLineCount = 0

		for textLine in self.itemList:
			textLine.Hide()

			if skipCount > 0:
				skipCount -= 1
				continue

			if localeInfo.IsARABIC():
				w, h = textLine.GetTextSize()
				textLine.SetPosition(w+10, yPos + 3)
			else:
				textLine.SetPosition(0, yPos + 3)

			yPos += self.stepSize

			if yPos <= self.GetHeight():
				self.showLineCount += 1
				textLine.Show()

	def ArrangeItem(self):
		self.SetSize(self.width, len(self.itemList) * self.stepSize)
		self._LocateItem()

	def GetViewItemCount(self):
		return int(self.GetHeight() / self.stepSize)

	def GetItemCount(self):
		return len(self.itemList)

	def SetEvent(self, event):
		self.event = event

	def SelectItem(self, line):

		if not self.keyDict.has_key(line):
			return

		if line == self.selectedLine:
			return

		self.selectedLine = line
		self.event(self.keyDict.get(line, 0), self.textDict.get(line, "None"))

	def GetSelectedItem(self):
		return self.keyDict.get(self.selectedLine, 0)

	def OnMouseLeftButtonDown(self):
		if self.overLine < 0:
			return

	def OnMouseLeftButtonUp(self):
		if self.overLine >= 0:
			self.SelectItem(self.overLine+self.basePos)

	def OnUpdate(self):

		self.overLine = -1

		if self.IsIn():
			x, y = self.GetGlobalPosition()
			height = self.GetHeight()
			xMouse, yMouse = wndMgr.GetMousePosition()

			if yMouse - y < height - 1:
				self.overLine = (yMouse - y) / self.stepSize

				if self.overLine < 0:
					self.overLine = -1
				if self.overLine >= len(self.itemList):
					self.overLine = -1

	def OnRender(self):
		xRender, yRender = self.GetGlobalPosition()
		yRender -= self.TEMPORARY_PLACE
		widthRender = self.width
		heightRender = self.height + self.TEMPORARY_PLACE*2

		if localeInfo.IsCIBN10:
			if -1 != self.overLine and self.keyDict[self.overLine] != -1:
				grp.SetColor(HALF_WHITE_COLOR)
				grp.RenderBar(xRender + 2, yRender + self.overLine*self.stepSize + 4, self.width - 3, self.stepSize)

			if -1 != self.selectedLine and self.keyDict[self.selectedLine] != -1:
				if self.selectedLine >= self.basePos:
					if self.selectedLine - self.basePos < self.showLineCount:
						grp.SetColor(SELECT_COLOR)
						grp.RenderBar(xRender + 2, yRender + (self.selectedLine-self.basePos)*self.stepSize + 4, self.width - 3, self.stepSize)

		else:
			if -1 != self.overLine:
				grp.SetColor(HALF_WHITE_COLOR)
				grp.RenderBar(xRender + 2, yRender + self.overLine*self.stepSize + 4, self.width - 3, self.stepSize)

			if -1 != self.selectedLine:
				if self.selectedLine >= self.basePos:
					if self.selectedLine - self.basePos < self.showLineCount:
						grp.SetColor(SELECT_COLOR)
						grp.RenderBar(xRender + 2, yRender + (self.selectedLine-self.basePos)*self.stepSize + 4, self.width - 3, self.stepSize)

class ListBox2(ListBox):
	def __init__(self, *args, **kwargs):
		ListBox.__init__(self, *args, **kwargs)
		self.rowCount = 10
		self.barWidth = 0
		self.colCount = 0

	def SetRowCount(self, rowCount):
		self.rowCount = rowCount

	def SetSize(self, width, height):
		ListBox.SetSize(self, width, height)
		self._RefreshForm()

	def ClearItem(self):
		ListBox.ClearItem(self)
		self._RefreshForm()

	def InsertItem(self, *args, **kwargs):
		ListBox.InsertItem(self, *args, **kwargs)
		self._RefreshForm()

	def OnUpdate(self):
		mpos = wndMgr.GetMousePosition()
		self.overLine = self._CalcPointIndex(mpos)

	def OnRender(self):
		x, y = self.GetGlobalPosition()
		pos = (x + 2, y)

		if -1 != self.overLine:
			grp.SetColor(HALF_WHITE_COLOR)
			self._RenderBar(pos, self.overLine)

		if -1 != self.selectedLine:
			if self.selectedLine >= self.basePos:
				if self.selectedLine - self.basePos < self.showLineCount:
					grp.SetColor(SELECT_COLOR)
					self._RenderBar(pos, self.selectedLine-self.basePos)

	def _CalcPointIndex(self, mpos):
		if self.IsIn():
			px, py = mpos
			gx, gy = self.GetGlobalPosition()
			lx, ly = px - gx, py - gy

			col = lx / self.barWidth
			row = ly / self.stepSize
			idx = col * self.rowCount + row
			if col >= 0 and col < self.colCount:
				if row >= 0 and row < self.rowCount:
					if idx >= 0 and idx < len(self.itemList):
						return idx

		return -1

	def _CalcRenderPos(self, pos, idx):
		x, y = pos
		row = idx % self.rowCount
		col = idx / self.rowCount
		return (x + col * self.barWidth, y + row * self.stepSize)

	def _RenderBar(self, basePos, idx):
		x, y = self._CalcRenderPos(basePos, idx)
		grp.RenderBar(x, y, self.barWidth - 3, self.stepSize)

	def _LocateItem(self):
		pos = (0, self.TEMPORARY_PLACE)

		self.showLineCount = 0
		for textLine in self.itemList:
			x, y = self._CalcRenderPos(pos, self.showLineCount)
			textLine.SetPosition(x, y)
			textLine.Show()

			self.showLineCount += 1

	def _RefreshForm(self):
		if len(self.itemList) % self.rowCount:
			self.colCount = len(self.itemList) / self.rowCount + 1
		else:
			self.colCount = len(self.itemList) / self.rowCount

		if self.colCount:
			self.barWidth = self.width / self.colCount
		else:
			self.barWidth = self.width

class GifBox(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)

		self.eventDict={}
		self.arg = -1
		self.argOut = -1
		self.imageLoaded = False

	def __del__(self):
		Window.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterGifImageBox(self, layer)

	def LoadImage(self, imageName):
		self.name=imageName
		wndMgr.LoadGif(self.hWnd, imageName)
		self.imageLoaded = True

		if len(self.eventDict)!=0:
			print "LOAD IMAGE", self, self.eventDict

	def UnloadImage(self):
		if self.imageLoaded:
			wndMgr.UnloadGif(self.hWnd)
			self.imageLoaded = False

	def SetAlpha(self, alpha):
		wndMgr.SetDiffuseColor(self.hWnd, 1.0, 1.0, 1.0, alpha)

	def SetDiffuseColor(self, r,g,b,a=1.0):
		wndMgr.SetDiffuseColor(self.hWnd, r,g,b,a)

	def SetAlphaColor(self, r,g,b,alpha=1.0):
		wndMgr.SetDiffuseColor(self.hWnd, r,g,b, alpha)

	def GetWidth(self):
		return wndMgr.GetWidth(self.hWnd)

	def GetHeight(self):
		return wndMgr.GetHeight(self.hWnd)

	def SetRenderingRect(self, left, top, right, bottom):
		wndMgr.SetRenderingRect(self.hWnd, left, top, right, bottom)

	def SetPercentage(self, curValue, maxValue):
		if maxValue:
			self.SetRenderingRect(0.0, 0.0, -1.0 + float(curValue) / float(maxValue), 0.0)
		else:
			self.SetRenderingRect(0.0, 0.0, 0.0, 0.0)

	def SetScale(self, xScale, yScale):
		wndMgr.SetScale(self.hWnd, xScale, yScale)

	def OnMouseLeftButtonUp(self):
		try:
			self.eventDict["MOUSE_LEFT_UP"]()
		except KeyError:
			pass
		Window.OnMouseLeftButtonUp(self)

	def SAFE_SetStringEvent(self, event, func):
		self.eventDict[event] = __mem_func__(func)

class ComboBox(Window):

	class ListBoxWithBoard(ListBox):

		def __init__(self, layer):
			ListBox.__init__(self, layer)

		def OnRender(self):
			xRender, yRender = self.GetGlobalPosition()
			yRender -= self.TEMPORARY_PLACE
			widthRender = self.width
			heightRender = self.height + self.TEMPORARY_PLACE*2
			grp.SetColor(BACKGROUND_COLOR)
			grp.RenderBar(xRender, yRender, widthRender, heightRender)
			grp.SetColor(DARK_COLOR)
			grp.RenderLine(xRender, yRender, widthRender, 0)
			grp.RenderLine(xRender, yRender, 0, heightRender)
			grp.SetColor(BRIGHT_COLOR)
			grp.RenderLine(xRender, yRender+heightRender, widthRender, 0)
			grp.RenderLine(xRender+widthRender, yRender, 0, heightRender)

			ListBox.OnRender(self)

	def __init__(self):
		Window.__init__(self)
		self.x = 0
		self.y = 0
		self.width = 0
		self.height = 0
		self.isSelected = False
		self.isOver = False
		self.isListOpened = False
		self.event = lambda *arg: None
		self.enable = True

		self.textLine = MakeTextLine(self)
		self.textLine.SetText(localeInfo.UI_ITEM)

		self.listBox = self.ListBoxWithBoard("TOP_MOST")
		self.listBox.SetPickAlways()
		self.listBox.SetParent(self)
		self.listBox.SetEvent(__mem_func__(self.OnSelectItem))
		self.listBox.Hide()

	def __del__(self):
		Window.__del__(self)

	def Destroy(self):
		self.textLine = None
		self.listBox = None

	def SetPosition(self, x, y):
		Window.SetPosition(self, x, y)
		self.x = x
		self.y = y
		self.__ArrangeListBox()

	def SetSize(self, width, height):
		Window.SetSize(self, width, height)
		self.width = width
		self.height = height
		self.textLine.UpdateRect()
		self.__ArrangeListBox()

	def __ArrangeListBox(self):
		self.listBox.SetPosition(0, self.height + 5)
		self.listBox.SetWidth(self.width)

	def Enable(self):
		self.enable = True

	def Disable(self):
		self.enable = False
		self.textLine.SetText("")
		self.CloseListBox()

	def SetEvent(self, event):
		self.event = event

	def ClearItem(self):
		self.CloseListBox()
		self.listBox.ClearItem()

	def InsertItem(self, index, name):
		self.listBox.InsertItem(index, name)
		self.listBox.ArrangeItem()

	def SetCurrentItem(self, text):
		self.textLine.SetText(text)

	def SelectItem(self, key):
		self.listBox.SelectItem(key)

	def OnSelectItem(self, index, name):

		self.CloseListBox()
		self.event(index)

	def CloseListBox(self):
		self.isListOpened = False
		self.listBox.Hide()

	def OnMouseLeftButtonDown(self):

		if not self.enable:
			return

		self.isSelected = True

	def OnMouseLeftButtonUp(self):

		if not self.enable:
			return

		self.isSelected = False

		if self.isListOpened:
			self.CloseListBox()
		else:
			if self.listBox.GetItemCount() > 0:
				self.isListOpened = True
				self.listBox.Show()
				self.__ArrangeListBox()

	def OnUpdate(self):

		if not self.enable:
			return

		if self.IsIn():
			self.isOver = True
		else:
			self.isOver = False

	def OnRender(self):
		self.x, self.y = self.GetGlobalPosition()
		xRender = self.x
		yRender = self.y
		widthRender = self.width
		heightRender = self.height
		grp.SetColor(BACKGROUND_COLOR)
		grp.RenderBar(xRender, yRender, widthRender, heightRender)
		grp.SetColor(DARK_COLOR)
		grp.RenderLine(xRender, yRender, widthRender, 0)
		grp.RenderLine(xRender, yRender, 0, heightRender)
		grp.SetColor(BRIGHT_COLOR)
		grp.RenderLine(xRender, yRender+heightRender, widthRender, 0)
		grp.RenderLine(xRender+widthRender, yRender, 0, heightRender)

		if self.isOver:
			grp.SetColor(HALF_WHITE_COLOR)
			grp.RenderBar(xRender + 2, yRender + 3, self.width - 3, heightRender - 5)

			if self.isSelected:
				grp.SetColor(WHITE_COLOR)
				grp.RenderBar(xRender + 2, yRender + 3, self.width - 3, heightRender - 5)

###################################################################################################
## Python Script Loader
###################################################################################################

class ScriptWindow(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		self.Children = []
		self.ElementDictionary = {}
	def __del__(self):
		Window.__del__(self)

	def ClearDictionary(self):
		self.Children = []
		self.ElementDictionary = {}
	def InsertChild(self, name, child):
		self.ElementDictionary[name] = child

	def IsChild(self, name):
		return self.ElementDictionary.has_key(name)
	def GetChild(self, name):
		return self.ElementDictionary[name]

	def GetChild2(self, name):
		return self.ElementDictionary.get(name, None)


class PythonScriptLoader(object):

	BODY_KEY_LIST = ( "x", "y", "width", "height" )

	#####

	DEFAULT_KEY_LIST = ( "type", "x", "y", )
	WINDOW_KEY_LIST = ( "width", "height", )
	IMAGE_KEY_LIST = ( "image", )
	EXPANDED_IMAGE_KEY_LIST = ( "image", )
	ANI_IMAGE_KEY_LIST = ( "images", )
	SLOT_KEY_LIST = ( "width", "height", "slot", )
	CANDIDATE_LIST_KEY_LIST = ( "item_step", "item_xsize", "item_ysize", )
	GRID_TABLE_KEY_LIST = ( "start_index", "x_count", "y_count", "x_step", "y_step", )
	EDIT_LINE_KEY_LIST = ( "width", "height", "input_limit", )
	COMBO_BOX_KEY_LIST = ( "width", "height", "item", )
	TITLE_BAR_KEY_LIST = ( "width", )
	HORIZONTAL_BAR_KEY_LIST = ( "width", )
	BOARD_KEY_LIST = ( "width", "height", )
	BOARD_WITH_TITLEBAR_KEY_LIST = ( "width", "height", "title", )
	BOX_KEY_LIST = ( "width", "height", )
	BAR_KEY_LIST = ( "width", "height", )
	LINE_KEY_LIST = ( "width", "height", )
	SLOTBAR_KEY_LIST = ( "width", "height", )
	GAUGE_KEY_LIST = ( "width", "color", )
	SCROLLBAR_KEY_LIST = ( "size", )
	LIST_BOX_KEY_LIST = ( "width", "height", )
	RENDER_TARGET_KEY_LIST = ( "index", )

	def __init__(self):
		self.Clear()

	def Clear(self):
		self.ScriptDictionary = { "SCREEN_WIDTH" : wndMgr.GetScreenWidth(), "SCREEN_HEIGHT" : wndMgr.GetScreenHeight() }
		self.InsertFunction = 0

	SCALABLE_SCRIPT_NAMES = (
						"menusystemdialog.py",
		"tpwizardinfowindow.py",
		"tpwizarddropwindow.py",
		"systemdialog.py",
		"gameoptiondialog.py",
		"gameoptiondialog_formobile.py",
		"game_option_0_0.py",
		"game_option_1_0.py",
		"game_option_1_1.py",
		"game_option_1_2.py",
		"game_option_2_0.py",
		"refinedialog.py",
		"shopdialog.py",
		"exchangedialog.py",
		"privateshopbuilder.py",
		"privateshopsearchdialog.py",
	)

	def __GetScriptScale(self, fileName, body):
		fn = ""
		if fileName:
			fn = fileName.lower().replace("\\", "/").split("/")[-1]

		name = ""
		if isinstance(body, dict):
			name = str(body.get("name", "")).lower()

		# "envanter ayni kalsin": Sadece envanter pencereleri olceklenir, diger her sey 1:1 orijinal kalir
		is_inventory = (
			"inventorywindow" in fn or
			"inventorywindowex" in fn or
			name == "inventorywindow"
		)

		if not is_inventory:
			return 1.0

		try:
			import uiMobileHud
			scale = uiMobileHud.GetWindowScale()
		except:
			scale = 1.25

		if scale < 0.6:
			scale = 0.6
		elif scale > 1.8:
			scale = 1.8

		# Clamp if window exceeds screen
		try:
			bodyH = float(body.get("height", 0))
			bodyW = float(body.get("width", 0))
			if bodyH > 0:
				max_h = (wndMgr.GetScreenHeight() - 16) / bodyH
				if scale > max_h:
					scale = max_h
			if bodyW > 0:
				max_w = (wndMgr.GetScreenWidth() - 16) / bodyW
				if scale > max_w:
					scale = max_w
		except:
			pass

		return max(0.6, scale)

	def __ScaleElementValue(self, elem, s, isRoot=False):
		if s <= 1.001 and s >= 0.999:
			return
		if not isinstance(elem, dict):
			return

		elem_type = elem.get("type", "window")

		if not isRoot:
			if "x" in elem and isinstance(elem["x"], (int, float)):
				elem["x"] = int(round(elem["x"] * s))
			if "y" in elem and isinstance(elem["y"], (int, float)):
				elem["y"] = int(round(elem["y"] * s))
		else:
			try:
				sw = wndMgr.GetScreenWidth()
				sh = wndMgr.GetScreenHeight()
				new_w = int(round(elem.get("width", 0) * s))
				new_h = int(round(elem.get("height", 0) * s))
				cur_x = elem.get("x", 0)
				cur_y = elem.get("y", 0)
				if isinstance(cur_x, (int, float)):
					if cur_x + new_w > sw:
						elem["x"] = max(5, sw - new_w - 15)
				if isinstance(cur_y, (int, float)):
					if cur_y + new_h > sh:
						elem["y"] = max(5, sh - new_h - 15)
			except:
				pass

		if "width" in elem and isinstance(elem["width"], (int, float)):
			elem["width"] = int(round(elem["width"] * s))
		if "height" in elem and isinstance(elem["height"], (int, float)):
			elem["height"] = int(round(elem["height"] * s))
		if "size" in elem and isinstance(elem["size"], (int, float)):
			elem["size"] = int(round(elem["size"] * s))

		if elem_type in ("button", "radio_button", "toggle_button", "drag_button"):
			elem["x_scale"] = float(elem.get("x_scale", 1.0)) * s
			elem["y_scale"] = float(elem.get("y_scale", 1.0)) * s
			if "text_height" in elem and isinstance(elem["text_height"], (int, float)):
				elem["text_height"] = int(round(elem["text_height"] * s))
			if "text_x" in elem and isinstance(elem["text_x"], (int, float)):
				elem["text_x"] = int(round(elem["text_x"] * s))

		elif elem_type in ("image", "expanded_image", "ani_image"):
			elem["x_scale"] = float(elem.get("x_scale", 1.0)) * s
			elem["y_scale"] = float(elem.get("y_scale", 1.0)) * s

		elif elem_type == "grid_table":
			elem["slot_scale"] = s
			for k in ("x_step", "y_step", "x_blank", "y_blank"):
				if k in elem and isinstance(elem[k], (int, float)):
					elem[k] = int(round(elem[k] * s))

		elif elem_type == "slot":
			elem["slot_scale"] = s
			if "slot" in elem and isinstance(elem["slot"], (list, tuple)):
				new_slots = []
				for sl in elem["slot"]:
					if isinstance(sl, dict):
						sl_copy = dict(sl)
						for k in ("x", "y", "width", "height"):
							if k in sl_copy and isinstance(sl_copy[k], (int, float)):
								sl_copy[k] = int(round(sl_copy[k] * s))
						new_slots.append(sl_copy)
					elif isinstance(sl, (list, tuple)) and len(sl) >= 5:
						new_slots.append((sl[0], int(round(sl[1] * s)), int(round(sl[2] * s)), int(round(sl[3] * s)), int(round(sl[4] * s))))
					else:
						new_slots.append(sl)
				elem["slot"] = tuple(new_slots) if isinstance(elem["slot"], tuple) else new_slots

		if "children" in elem and isinstance(elem["children"], (list, tuple)):
			is_tuple = isinstance(elem["children"], tuple)
			new_children = []
			for ch in elem["children"]:
				if isinstance(ch, dict):
					self.__ScaleElementValue(ch, s, isRoot=False)
				new_children.append(ch)
			elem["children"] = tuple(new_children) if is_tuple else new_children

	def LoadScriptFile(self, window, FileName):
		import exception
		import exceptions
		import os
		import errno
		self.Clear()

		print "===== Load Script File : %s" % (FileName)

		import sys
		from utils import Sandbox
		sandbox = Sandbox(True, ["uiScriptLocale", "localeInfo", "sys", "item", "app", "player","utils"]) #@ikd - added 'utils' to import it in scriptfile (to use GetElementDictByName)

		import chr
		import player
		import app
		self.ScriptDictionary["PLAYER_NAME_MAX_LEN"] = chr.PLAYER_NAME_MAX_LEN
		self.ScriptDictionary["DRAGON_SOUL_EQUIPMENT_SLOT_START"] = player.DRAGON_SOUL_EQUIPMENT_SLOT_START
		self.ScriptDictionary["LOCALE_PATH"] = app.GetLocalePath()

		if __USE_EXTRA_CYTHON__:
			# sub functions
			from os.path import splitext as op_splitext, basename as op_basename, dirname as op_dirname
			def GetModName(filename):
				return op_splitext(op_basename(filename))[0]
			def IsInUiPath(filename):
				def ICmp(s1, s2):
					return s1.lower() == s2.lower()
				return ICmp(op_dirname(filename), "uiscript")
			# module name to import
			modname = GetModName(FileName)
			# lazy loading of uiscriptlib
			import uiscriptlib
			# copy scriptdictionary stuff to builtin scope (otherwise, import will fail)
			tpl2Main = (
				"SCREEN_WIDTH","SCREEN_HEIGHT",
				"PLAYER_NAME_MAX_LEN", "DRAGON_SOUL_EQUIPMENT_SLOT_START","LOCALE_PATH"
			)
			import __builtin__ as bt
			for idx in tpl2Main:
				tmpVal = self.ScriptDictionary[idx]
				exec "bt.%s = tmpVal"%idx in globals(), locals()
			# debug stuff
			# import dbg
			# dbg.TraceError("Loading %s (%s %s)"%(FileName, GetModName(FileName), IsInUiPath(FileName)))
		try:
			if __USE_EXTRA_CYTHON__ and IsInUiPath(FileName) and uiscriptlib.isExist(modname):
				m1 = uiscriptlib.moduleImport(modname)
				self.ScriptDictionary["window"] = m1.window.copy()
				del m1
			else:
				sandbox.execfile(FileName, self.ScriptDictionary)
		except IOError, err:
			import sys
			import dbg
			dbg.TraceError("Failed to load script file : %s" % (FileName))
			dbg.TraceError("error  : %s" % (err))
			exception.Abort("LoadScriptFile1")
		except RuntimeError,err:
			import sys
			import dbg
			dbg.TraceError("Failed to load script file : %s" % (FileName))
			dbg.TraceError("error  : %s" % (err))
			exception.Abort("LoadScriptFile2")
		except:
			import sys
			import dbg
			dbg.TraceError("Failed to load script file : %s" % (FileName))
			exception.Abort("LoadScriptFile!!!!!!!!!!!!!!")

		#####

		Body = self.ScriptDictionary["window"]
		self.CheckKeyList("window", Body, self.BODY_KEY_LIST)

		try:
			_sc = self.__GetScriptScale(FileName, Body)
			if _sc > 1.001 or _sc < 0.999:
				self.__ScaleElementValue(Body, _sc, isRoot=True)
		except Exception as _e:
			pass

		window.ClearDictionary()
		self.InsertFunction = window.InsertChild

		window.SetPosition(int(Body["x"]), int(Body["y"]))

		if localeInfo.IsARABIC():
			w = wndMgr.GetScreenWidth()
			h = wndMgr.GetScreenHeight()
			if Body.has_key("width"):
				w = int(Body["width"])
			if Body.has_key("height"):
				h = int(Body["height"])

			window.SetSize(w, h)
		else:
			window.SetSize(int(Body["width"]), int(Body["height"]))
			if True == Body.has_key("style"):
				for StyleList in Body["style"]:
					window.AddFlag(StyleList)


		self.LoadChildren(window, Body)

	def LoadChildren(self, parent, dicChildren):

		if localeInfo.IsARABIC():
			parent.AddFlag( "rtl" )

		if True == dicChildren.has_key("style"):
			for style in dicChildren["style"]:
				parent.AddFlag(style)

		if False == dicChildren.has_key("children"):
			return False

		Index = 0

		ChildrenList = dicChildren["children"]
		parent.Children = range(len(ChildrenList))
		for ElementValue in ChildrenList:
			try:
				Name = ElementValue["name"]
			except KeyError:
				Name = ElementValue["name"] = "NONAME"

			try:
				Type = ElementValue["type"]
			except KeyError:
				Type = ElementValue["type"] = "window"

			if False == self.CheckKeyList(Name, ElementValue, self.DEFAULT_KEY_LIST):
				del parent.Children[Index]
				continue

			if Type == "window":
				parent.Children[Index] = ScriptWindow()
				parent.Children[Index].SetParent(parent)
				self.LoadElementWindow(parent.Children[Index], ElementValue, parent)

			elif Type == "button":
				parent.Children[Index] = Button()
				parent.Children[Index].SetParent(parent)
				self.LoadElementButton(parent.Children[Index], ElementValue, parent)

			elif Type == "render_target":
				parent.Children[Index] = RenderTarget()
				parent.Children[Index].SetParent(parent)
				self.LoadElementRenderTarget(parent.Children[Index], ElementValue, parent)

			elif Type == "radio_button":
				parent.Children[Index] = RadioButton()
				parent.Children[Index].SetParent(parent)
				self.LoadElementButton(parent.Children[Index], ElementValue, parent)

			elif Type == "toggle_button":
				parent.Children[Index] = ToggleButton()
				parent.Children[Index].SetParent(parent)
				self.LoadElementButton(parent.Children[Index], ElementValue, parent)

			elif Type == "mark":
				parent.Children[Index] = MarkBox()
				parent.Children[Index].SetParent(parent)
				self.LoadElementMark(parent.Children[Index], ElementValue, parent)

			elif Type == "image":
				if ElementValue.has_key("x_scale") and ElementValue.has_key("y_scale"):
					parent.Children[Index] = ExpandedImageBox()
					parent.Children[Index].SetParent(parent)
					self.LoadElementExpandedImage(parent.Children[Index], ElementValue, parent)
				else:
					parent.Children[Index] = ImageBox()
					parent.Children[Index].SetParent(parent)
					self.LoadElementImage(parent.Children[Index], ElementValue, parent)

			elif Type == "expanded_image":
				parent.Children[Index] = ExpandedImageBox()
				parent.Children[Index].SetParent(parent)
				self.LoadElementExpandedImage(parent.Children[Index], ElementValue, parent)

			elif Type == "ani_image":
				parent.Children[Index] = AniImageBox()
				parent.Children[Index].SetParent(parent)
				self.LoadElementAniImage(parent.Children[Index], ElementValue, parent)

			elif Type == "slot":
				parent.Children[Index] = SlotWindow()
				parent.Children[Index].SetParent(parent)
				self.LoadElementSlot(parent.Children[Index], ElementValue, parent)

			elif Type == "candidate_list":
				parent.Children[Index] = CandidateListBox()
				parent.Children[Index].SetParent(parent)
				self.LoadElementCandidateList(parent.Children[Index], ElementValue, parent)

			elif Type == "grid_table":
				parent.Children[Index] = GridSlotWindow()
				parent.Children[Index].SetParent(parent)
				self.LoadElementGridTable(parent.Children[Index], ElementValue, parent)

			elif Type == "text":
				parent.Children[Index] = TextLine()
				parent.Children[Index].SetParent(parent)
				self.LoadElementText(parent.Children[Index], ElementValue, parent)

			elif Type == "editline":
				parent.Children[Index] = EditLine()
				parent.Children[Index].SetParent(parent)
				self.LoadElementEditLine(parent.Children[Index], ElementValue, parent)

			elif Type == "titlebar":
				parent.Children[Index] = TitleBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementTitleBar(parent.Children[Index], ElementValue, parent)

			elif Type == "horizontalbar":
				parent.Children[Index] = HorizontalBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementHorizontalBar(parent.Children[Index], ElementValue, parent)

			elif Type == "board":
				parent.Children[Index] = Board()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBoard(parent.Children[Index], ElementValue, parent)

			elif Type == "board_blue":
				parent.Children[Index] = BoardBlue()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBoard(parent.Children[Index], ElementValue, parent)

			elif Type == "board_with_titlebar":
				parent.Children[Index] = BoardWithTitleBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBoardWithTitleBar(parent.Children[Index], ElementValue, parent)

			elif Type == "thinboard":
				parent.Children[Index] = ThinBoard()
				parent.Children[Index].SetParent(parent)
				self.LoadElementThinBoard(parent.Children[Index], ElementValue, parent)

			elif Type == "thinboard_new":
				parent.Children[Index] = ThinBoardNew()
				parent.Children[Index].SetParent(parent)
				self.LoadElementThinBoard(parent.Children[Index], ElementValue, parent)

			elif Type == "box":
				parent.Children[Index] = Box()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBox(parent.Children[Index], ElementValue, parent)

			elif Type == "bar":
				parent.Children[Index] = Bar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementBar(parent.Children[Index], ElementValue, parent)

			elif Type == "line":
				parent.Children[Index] = Line()
				parent.Children[Index].SetParent(parent)
				self.LoadElementLine(parent.Children[Index], ElementValue, parent)

			elif Type == "slotbar":
				parent.Children[Index] = SlotBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementSlotBar(parent.Children[Index], ElementValue, parent)

			elif Type == "gauge":
				parent.Children[Index] = Gauge()
				parent.Children[Index].SetParent(parent)
				self.LoadElementGauge(parent.Children[Index], ElementValue, parent)

			elif Type == "scrollbar":
				parent.Children[Index] = ScrollBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementScrollBar(parent.Children[Index], ElementValue, parent)

			elif Type == "scrollbartpw":
				parent.Children[Index] = ScrollBarTpw()
				parent.Children[Index].SetParent(parent)
				self.LoadElementScrollBar(parent.Children[Index], ElementValue, parent)

			elif Type == "thin_scrollbar":
				parent.Children[Index] = ThinScrollBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementScrollBar(parent.Children[Index], ElementValue, parent)

			elif Type == "small_thin_scrollbar":
				parent.Children[Index] = SmallThinScrollBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementScrollBar(parent.Children[Index], ElementValue, parent)

			elif Type == "slimscrollbar":
				parent.Children[Index] = NewScrollBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementScrollBar(parent.Children[Index], ElementValue, parent)

			elif Type == "thinboard_circle":
				parent.Children[Index] = ThinBoardCircle()
				parent.Children[Index].SetParent(parent)
				self.LoadElementThinBoard(parent.Children[Index], ElementValue, parent)

			elif Type == "sliderbar":
				parent.Children[Index] = SliderBar()
				parent.Children[Index].SetParent(parent)
				self.LoadElementSliderBar(parent.Children[Index], ElementValue, parent)

			elif Type == "listbox_new":
				parent.Children[Index] = ListBoxNew()
				parent.Children[Index].SetParent(parent)
				self.LoadElementListBox(parent.Children[Index], ElementValue, parent)

			elif Type == "listbox":
				parent.Children[Index] = ListBox()
				parent.Children[Index].SetParent(parent)
				self.LoadElementListBox(parent.Children[Index], ElementValue, parent)

			elif Type == "listbox2":
				parent.Children[Index] = ListBox2()
				parent.Children[Index].SetParent(parent)
				self.LoadElementListBox2(parent.Children[Index], ElementValue, parent)

			elif Type == "listboxex":
				parent.Children[Index] = ListBoxEx()
				parent.Children[Index].SetParent(parent)
				self.LoadElementListBoxEx(parent.Children[Index], ElementValue, parent)

			else:
				Index += 1
				continue

			parent.Children[Index].SetWindowName(Name)
			if 0 != self.InsertFunction:
				self.InsertFunction(Name, parent.Children[Index])

			self.LoadChildren(parent.Children[Index], ElementValue)
			Index += 1

	def CheckKeyList(self, name, value, key_list):

		for DataKey in key_list:
			if False == value.has_key(DataKey):
				print "Failed to find data key", "[" + name + "/" + DataKey + "]"
				return False

		return True

	def LoadDefaultData(self, window, value, parentWindow):
		loc_x = int(value["x"])
		loc_y = int(value["y"])
		if value.has_key("vertical_align"):
			if "center" == value["vertical_align"]:
				window.SetWindowVerticalAlignCenter()
			elif "bottom" == value["vertical_align"]:
				window.SetWindowVerticalAlignBottom()

		if parentWindow.IsRTL():
			loc_x = int(value["x"]) + window.GetWidth()
			if value.has_key("horizontal_align"):
				if "center" == value["horizontal_align"]:
					window.SetWindowHorizontalAlignCenter()
					loc_x = - int(value["x"])
				elif "right" == value["horizontal_align"]:
					window.SetWindowHorizontalAlignLeft()
					loc_x = int(value["x"]) - window.GetWidth()
					## loc_x = parentWindow.GetWidth() - int(value["x"]) + window.GetWidth()
			else:
				window.SetWindowHorizontalAlignRight()

			if value.has_key("all_align"):
				window.SetWindowVerticalAlignCenter()
				window.SetWindowHorizontalAlignCenter()
				loc_x = - int(value["x"])
		else:
			if value.has_key("horizontal_align"):
				if "center" == value["horizontal_align"]:
					window.SetWindowHorizontalAlignCenter()
				elif "right" == value["horizontal_align"]:
					window.SetWindowHorizontalAlignRight()

		window.SetPosition(loc_x, loc_y)
		window.Show()

	## Window
	def LoadElementWindow(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.WINDOW_KEY_LIST):
			return False

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Button
	def LoadElementButton(self, window, value, parentWindow):

		if value.has_key("width") and value.has_key("height"):
			window.SetSize(int(value["width"]), int(value["height"]))

		if True == value.has_key("default_image"):
			window.SetUpVisual(value["default_image"])
		if True == value.has_key("over_image"):
			window.SetOverVisual(value["over_image"])
		if True == value.has_key("down_image"):
			window.SetDownVisual(value["down_image"])
		if True == value.has_key("disable_image"):
			window.SetDisableVisual(value["disable_image"])

		if True == value.has_key("x_scale") and True == value.has_key("y_scale"):
			window.SetButtonScale(float(value["x_scale"]), float(value["y_scale"]))

		if True == value.has_key("text"):
			if True == value.has_key("text_height"):
				window.SetText(value["text"], value["text_height"])
			elif TRUE == value.has_key("text_x") and app.ENABLE_NEW_GAMEOPTION:
				window.SetListText(value["text"], value["text_x"])
			else:
				window.SetText(value["text"])

			if value.has_key("text_color"):
				window.SetTextColor(value["text_color"])
		if True == value.has_key("tooltip_text"):
			if True == value.has_key("tooltip_x") and True == value.has_key("tooltip_y"):
				window.SetToolTipText(value["tooltip_text"], int(value["tooltip_x"]), int(value["tooltip_y"]))
			else:
				window.SetToolTipText(value["tooltip_text"])

		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Mark
	def LoadElementMark(self, window, value, parentWindow):

		#if False == self.CheckKeyList(value["name"], value, self.MARK_KEY_LIST):
		#	return False

		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Image
	def LoadElementImage(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.IMAGE_KEY_LIST):
			return False

		window.LoadImage(value["image"])
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## AniImage
	def LoadElementAniImage(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.ANI_IMAGE_KEY_LIST):
			return False

		if True == value.has_key("delay"):
			window.SetDelay(value["delay"])

		for image in value["images"]:
			window.AppendImage(image)

		if value.has_key("width") and value.has_key("height"):
			window.SetSize(value["width"], value["height"])

		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Expanded Image
	def LoadElementExpandedImage(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.EXPANDED_IMAGE_KEY_LIST):
			return False

		window.LoadImage(value["image"])

		if True == value.has_key("x_origin") and True == value.has_key("y_origin"):
			window.SetOrigin(float(value["x_origin"]), float(value["y_origin"]))

		if True == value.has_key("x_scale") and True == value.has_key("y_scale"):
			window.SetScale(float(value["x_scale"]), float(value["y_scale"]))

		if True == value.has_key("rect"):
			RenderingRect = value["rect"]
			window.SetRenderingRect(RenderingRect[0], RenderingRect[1], RenderingRect[2], RenderingRect[3])

		if True == value.has_key("mode"):
			mode = value["mode"]
			if "MODULATE" == mode:
				window.SetRenderingMode(wndMgr.RENDERING_MODE_MODULATE)

		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Slot
	def LoadElementSlot(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.SLOT_KEY_LIST):
			return False

		global_x = int(value["x"])
		global_y = int(value["y"])
		global_width = int(value["width"])
		global_height = int(value["height"])

		window.SetPosition(global_x, global_y)
		window.SetSize(global_width, global_height)
		window.Show()

		r = 1.0
		g = 1.0
		b = 1.0
		a = 1.0

		if True == value.has_key("image_r") and \
			True == value.has_key("image_g") and \
			True == value.has_key("image_b") and \
			True == value.has_key("image_a"):
			r = float(value["image_r"])
			g = float(value["image_g"])
			b = float(value["image_b"])
			a = float(value["image_a"])

		SLOT_ONE_KEY_LIST = ("index", "x", "y", "width", "height")

		for slot in value["slot"]:
			if True == self.CheckKeyList(value["name"] + " - one", slot, SLOT_ONE_KEY_LIST):
				wndMgr.AppendSlot(window.hWnd,
									int(slot["index"]),
									int(slot["x"]),
									int(slot["y"]),
									int(slot["width"]),
									int(slot["height"]))

		if True == value.has_key("image"):
			wndMgr.SetSlotBaseImage(window.hWnd,
									value["image"],
									r, g, b, a)

		if True == value.has_key("slot_scale"):
			try:
				_ss = float(value["slot_scale"])
				wndMgr.SetSlotUnitSize(window.hWnd, int(32 * _ss), int(32 * _ss))
			except:
				pass

		return True

	def LoadElementCandidateList(self, window, value, parentWindow):
		if False == self.CheckKeyList(value["name"], value, self.CANDIDATE_LIST_KEY_LIST):
			return False

		window.SetPosition(int(value["x"]), int(value["y"]))
		window.SetItemSize(int(value["item_xsize"]), int(value["item_ysize"]))
		window.SetItemStep(int(value["item_step"]))
		window.Show()

		return True

	## Table
	def LoadElementGridTable(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.GRID_TABLE_KEY_LIST):
			return False

		xBlank = 0
		yBlank = 0
		if True == value.has_key("x_blank"):
			xBlank = int(value["x_blank"])
		if True == value.has_key("y_blank"):
			yBlank = int(value["y_blank"])

		if localeInfo.IsARABIC():
			pass
		else:
			window.SetPosition(int(value["x"]), int(value["y"]))

		window.ArrangeSlot(	int(value["start_index"]),
							int(value["x_count"]),
							int(value["y_count"]),
							int(value["x_step"]),
							int(value["y_step"]),
							xBlank,
							yBlank)
		if True == value.has_key("image"):
			r = 1.0
			g = 1.0
			b = 1.0
			a = 1.0
			if True == value.has_key("image_r") and \
				True == value.has_key("image_g") and \
				True == value.has_key("image_b") and \
				True == value.has_key("image_a"):
				r = float(value["image_r"])
				g = float(value["image_g"])
				b = float(value["image_b"])
				a = float(value["image_a"])
			if True == value.has_key("slot_scale"):
				try:
					_ss = float(value["slot_scale"])
					wndMgr.SetSlotBaseImageScale(window.hWnd, value["image"], r, g, b, a, _ss, _ss)
				except:
					wndMgr.SetSlotBaseImage(window.hWnd, value["image"], r, g, b, a)
			else:
				wndMgr.SetSlotBaseImage(window.hWnd, value["image"], r, g, b, a)

		if True == value.has_key("slot_scale"):
			try:
				_ss = float(value["slot_scale"])
				wndMgr.SetSlotUnitSize(window.hWnd, int(32 * _ss), int(32 * _ss))
			except:
				pass

		if True == value.has_key("style"):
			if "select" == value["style"]:
				wndMgr.SetSlotStyle(window.hWnd, wndMgr.SLOT_STYLE_SELECT)
		if localeInfo.IsARABIC():
			self.LoadDefaultData(window, value, parentWindow)
		else:
			window.Show()

		return True

	## Text
	def LoadElementText(self, window, value, parentWindow):

		if value.has_key("fontsize"):
			fontSize = value["fontsize"]

			if "LARGE" == fontSize:
				window.SetFontName(localeInfo.UI_DEF_FONT_LARGE)

		elif value.has_key("fontname"):
			fontName = value["fontname"]
			window.SetFontName(fontName)

		if value.has_key("text_horizontal_align"):
			if "left" == value["text_horizontal_align"]:
				window.SetHorizontalAlignLeft()
			elif "center" == value["text_horizontal_align"]:
				window.SetHorizontalAlignCenter()
			elif "right" == value["text_horizontal_align"]:
				window.SetHorizontalAlignRight()

		if value.has_key("text_vertical_align"):
			if "top" == value["text_vertical_align"]:
				window.SetVerticalAlignTop()
			elif "center" == value["text_vertical_align"]:
				window.SetVerticalAlignCenter()
			elif "bottom" == value["text_vertical_align"]:
				window.SetVerticalAlignBottom()

		if value.has_key("all_align"):
			window.SetHorizontalAlignCenter()
			window.SetVerticalAlignCenter()
			window.SetWindowHorizontalAlignCenter()
			window.SetWindowVerticalAlignCenter()

		if value.has_key("all_align_2"):
			window.SetHorizontalAlignCenter()
			# window.SetVerticalAlignCenter()
			window.SetWindowHorizontalAlignCenter()
			# window.SetWindowVerticalAlignCenter()

		if value.has_key("r") and value.has_key("g") and value.has_key("b"):
			window.SetFontColor(float(value["r"]), float(value["g"]), float(value["b"]))
		elif value.has_key("color"):
			window.SetPackedFontColor(value["color"])
		else:
			window.SetFontColor(0.8549, 0.8549, 0.8549)

		if value.has_key("outline"):
			if value["outline"]:
				window.SetOutline()
		if True == value.has_key("text"):
			window.SetText(value["text"])

		self.LoadDefaultData(window, value, parentWindow)

		return True

	## EditLine
	def LoadElementEditLine(self, window, value, parentWindow):
		if False == self.CheckKeyList(value["name"], value, self.EDIT_LINE_KEY_LIST):
			return False

		if value.has_key("secret_flag"):
			window.SetSecret(value["secret_flag"])
		if value.has_key("with_codepage"):
			if value["with_codepage"]:
				window.bCodePage = True
		if value.has_key("only_number"):
			if value["only_number"]:
				window.SetNumberMode()
		if value.has_key("enable_codepage"):
			window.SetIMEFlag(value["enable_codepage"])
		if value.has_key("enable_ime"):
			window.SetIMEFlag(value["enable_ime"])
		if value.has_key("limit_width"):
			window.SetLimitWidth(value["limit_width"])
		if value.has_key("multi_line"):
			if value["multi_line"]:
				window.SetMultiLine()
		if value.has_key("info_msg"):
			window.SetOverlayText(value["info_msg"])
		window.SetMax(int(value["input_limit"]))
		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadElementText(window, value, parentWindow)

		return True

	## TitleBar
	def LoadElementTitleBar(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.TITLE_BAR_KEY_LIST):
			return False

		window.MakeTitleBar(int(value["width"]), value.get("color", "red"))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	def LoadElementRenderTarget(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.RENDER_TARGET_KEY_LIST):
			return False

		window.SetSize(value["width"], value["height"])

		if True == value.has_key("style"):
			for style in value["style"]:
				window.AddFlag(style)

		self.LoadDefaultData(window, value, parentWindow)

		if value.has_key("index"):
			window.SetRenderTarget(int(value["index"]))

		return True

	## HorizontalBar
	def LoadElementHorizontalBar(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.HORIZONTAL_BAR_KEY_LIST):
			return False

		window.Create(int(value["width"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Board
	def LoadElementBoard(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.BOARD_KEY_LIST):
			return False

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Board With TitleBar
	def LoadElementBoardWithTitleBar(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.BOARD_WITH_TITLEBAR_KEY_LIST):
			return False

		window.SetSize(int(value["width"]), int(value["height"]))
		window.SetTitleName(value["title"])
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## ThinBoard
	def LoadElementThinBoard(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.BOARD_KEY_LIST):
			return False

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Box
	def LoadElementBox(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.BOX_KEY_LIST):
			return False

		if True == value.has_key("color"):
			window.SetColor(value["color"])

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Bar
	def LoadElementBar(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.BAR_KEY_LIST):
			return False

		if True == value.has_key("color"):
			window.SetColor(value["color"])

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Line
	def LoadElementLine(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.LINE_KEY_LIST):
			return False

		if True == value.has_key("color"):
			window.SetColor(value["color"])

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Slot
	def LoadElementSlotBar(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.SLOTBAR_KEY_LIST):
			return False

		window.SetSize(int(value["width"]), int(value["height"]))
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## Gauge
	def LoadElementGauge(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.GAUGE_KEY_LIST):
			return False

		window.MakeGauge(value["width"], value["color"])
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## ScrollBar
	def LoadElementScrollBar(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.SCROLLBAR_KEY_LIST):
			return False

		window.SetScrollBarSize(value["size"])
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## SliderBar
	def LoadElementSliderBar(self, window, value, parentWindow):

		self.LoadDefaultData(window, value, parentWindow)

		return True

	## ListBox
	def LoadElementListBox(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.LIST_BOX_KEY_LIST):
			return False

		if value.has_key("item_align"):
			window.SetTextCenterAlign(value["item_align"])

		window.SetSize(value["width"], value["height"])
		self.LoadDefaultData(window, value, parentWindow)

		return True

	## ListBox2
	def LoadElementListBox2(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.LIST_BOX_KEY_LIST):
			return False

		window.SetRowCount(value.get("row_count", 10))
		window.SetSize(value["width"], value["height"])
		self.LoadDefaultData(window, value, parentWindow)

		if value.has_key("item_align"):
			window.SetTextCenterAlign(value["item_align"])

		return True
	def LoadElementListBoxEx(self, window, value, parentWindow):

		if False == self.CheckKeyList(value["name"], value, self.LIST_BOX_KEY_LIST):
			return False

		window.SetSize(value["width"], value["height"])
		self.LoadDefaultData(window, value, parentWindow)

		if value.has_key("itemsize_x") and value.has_key("itemsize_y"):
			window.SetItemSize(int(value["itemsize_x"]), int(value["itemsize_y"]))

		if value.has_key("itemstep"):
			window.SetItemStep(int(value["itemstep"]))

		if value.has_key("viewcount"):
			window.SetViewItemCount(int(value["viewcount"]))

		return True

class ReadingWnd(Bar):

	def __init__(self):
		Bar.__init__(self,"TOP_MOST")

		self.__BuildText()
		self.SetSize(80, 19)
		self.Show()

	def __del__(self):
		Bar.__del__(self)

	def __BuildText(self):
		self.text = TextLine()
		self.text.SetParent(self)
		self.text.SetPosition(4, 3)
		self.text.Show()

	def SetText(self, text):
		self.text.SetText(text)

	def SetReadingPosition(self, x, y):
		xPos = x + 2
		yPos = y  - self.GetHeight() - 2
		self.SetPosition(xPos, yPos)

	def SetTextColor(self, color):
		self.text.SetPackedFontColor(color)


def MakeBoardWithTitleBar(parent, flag, title, closeEvent, width, height):
	board = BoardWithTitleBar()
	board.SetParent(parent)
	board.SetSize(width, height)
	board.AddFlag(flag)
	board.SetTitleName(title)
	board.SetCloseEvent(closeEvent)
	board.Show()
	return board

def MakeSlotBar(parent, x, y, width, height):
	slotBar = SlotBar()
	slotBar.SetParent(parent)
	slotBar.SetSize(width, height)
	slotBar.SetPosition(x, y)
	slotBar.Show()
	return slotBar

def MakeImageBox(parent, name, x, y):
	image = ImageBox()
	image.SetParent(parent)
	image.LoadImage(name)
	image.SetPosition(x, y)
	image.Show()
	return image

def MakeTextLine(parent):
	textLine = TextLine()
	textLine.SetParent(parent)
	textLine.SetWindowHorizontalAlignCenter()
	textLine.SetWindowVerticalAlignCenter()
	textLine.SetHorizontalAlignCenter()
	textLine.SetVerticalAlignCenter()
	textLine.Show()
	return textLine

def MakeTextLineNew(parent, x, y, text):
	textLine = TextLine()
	textLine.SetParent(parent)
	textLine.SetPosition(x, y)
	textLine.SetText(text)
	textLine.Show()
	return textLine

def AddTextLine(parent, x, y, text):
	textLine = TextLine()
	textLine.SetParent(parent)
	textLine.SetPosition(x, y)
	textLine.SetText(text)
	textLine.Show()
	return textLine

def MakeTextLineNew(parent, name, x, y):
	textLine = TextLine()
	textLine.SetParent(parent)
	textLine.SetText(name)
	textLine.SetPosition(x, y)
	textLine.Show()
	return textLine

def MakeTextLineAverage(parent, x, y, text):
	textLine = TextLine()
	textLine.SetParent(parent)
	textLine.SetPosition(x, y)
	textLine.SetText(text)
	textLine.Show()
	return textLine

def MakeButton(parent, x, y, tooltipText, path, up, over, down):
	button = Button()
	button.SetParent(parent)
	button.SetPosition(x, y)
	button.SetUpVisual(path + up)
	button.SetOverVisual(path + over)
	button.SetDownVisual(path + down)
	button.SetToolTipText(tooltipText)
	button.Show()
	return button

def RenderRoundBox(x, y, width, height, color):
	grp.SetColor(color)
	grp.RenderLine(x+2, y, width-3, 0)
	grp.RenderLine(x+2, y+height, width-3, 0)
	grp.RenderLine(x, y+2, 0, height-4)
	grp.RenderLine(x+width, y+1, 0, height-3)
	grp.RenderLine(x, y+2, 2, -2)
	grp.RenderLine(x, y+height-2, 2, 2)
	grp.RenderLine(x+width-2, y, 2, 2)
	grp.RenderLine(x+width-2, y+height, 2, -2)

def GenerateColor(r, g, b):
	r = float(r) / 255.0
	g = float(g) / 255.0
	b = float(b) / 255.0
	return grp.GenerateColor(r, g, b, 1.0)

def EnablePaste(flag):
	ime.EnablePaste(flag)

def GetHyperlink():
	return wndMgr.GetHyperlink()

def calculateRect(curValue, maxValue):
	try:
		return -1.0 + float(curValue) / float(maxValue)
	except:
		return 0.0

def MakeNewTextLine(parent, horizontalAlign = True, verticalAlgin = True, x = 0, y = 0):
	textLine = TextLine()
	textLine.SetParent(parent)
	if horizontalAlign == True: textLine.SetWindowHorizontalAlignCenter()
	if verticalAlgin == True: textLine.SetWindowVerticalAlignCenter()
	textLine.SetHorizontalAlignCenter()
	textLine.SetVerticalAlignCenter()
	if x != 0 and y != 0: textLine.SetPosition(x, y)
	textLine.Show()
	return textLine

def MakeExpandedImageBox(parent, name, x, y, flag = "", scale = 0):
	image = ExpandedImageBox()
	image.SetParent(parent)
	image.LoadImage(name)
	image.SetPosition(x, y)
	if flag != "":
		image.AddFlag(flag)
	if scale > 0:
		image.SetScale(scale, scale)
	image.Show()
	return image

class RenderTarget(Window):
	def __init__(self, layer = "UI"):
		Window.__init__(self, layer)
		self.number = -1
		self.eventDict={}

	def Destroy(self):
		return

	def __del__(self):
		Window.__del__(self)

	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterRenderTarget(self, layer)

	def SetRenderTarget(self, number):
		self.number = number
		wndMgr.SetRenderTarget(self.hWnd, self.number)

	def OnMouseLeftButtonUp(self):
		try:
			self.eventDict["MOUSE_LEFT_UP"]()
		except KeyError:
			pass
		Window.OnMouseLeftButtonUp(self)

	def SAFE_SetStringEvent(self, event, func):
		self.eventDict[event] = __mem_func__(func)

class MultiTextLine(Window):
	def __del__(self):
		Window.__del__(self)
	def Destroy(self):
		self.textRules = {}
	def __init__(self):
		Window.__init__(self)
		self.Destroy()
		self.AddFlag("not_pick")
		self.textRules["textRange"] = 15
		self.textRules["text"] = ""
		self.textRules["textType"] = ""
		self.textRules["fontName"] = ""
		self.textRules["hexColor"] = 0
		self.textRules["fontColor"] = 0
		self.textRules["outline"] = 0
	def SetTextType(self, textType):
		self.textRules["textType"] = textType
		self.Refresh()
	def SetTextRange(self, textRange):
		self.textRules["textRange"] = textRange
		self.Refresh()
	def SetOutline(self, outline):
		self.textRules["outline"] = outline
		self.Refresh()
	def SetPackedFontColor(self, hexColor):
		self.textRules["hexColor"] = hexColor
		self.Refresh()
	def SetFontColor(self, r, g, b):
		self.textRules["fontColor"] =[r, g, b]
		self.Refresh()
	def SetFontName(self, fontName):
		self.textRules["fontName"] = fontName
		self.Refresh()
	def SetText(self, newText):
		self.textRules["text"] = newText
		self.Refresh()
	def Refresh(self):
		textRules = self.textRules
		if textRules["text"] == "":
			return
		self.children=[]
		outline = textRules["outline"]
		fontColor = textRules["fontColor"]
		hexColor = textRules["hexColor"]
		yRange = textRules["textRange"]
		fontName = textRules["fontName"]
		textTypeList = textRules["textType"].split("?")
		#textType = textRules["textType"].split("#")
		totalTextList = textRules["text"].split("#")

		(xPosition, yPosition) = (0, 0)
		width = 0
		for text in totalTextList:
			childText = TextLine()
			childText.SetParent(self)
			childText.AddFlag("not_pick")
			childText.SetPosition(xPosition, yPosition)
			if fontName != "":
				childText.SetFontName(fontName)
			if hexColor != 0:
				childText.SetPackedFontColor(hexColor)
			if fontColor != 0:
				childText.SetFontColor(*fontColor)
			if outline:
				childText.SetOutline()
			for textType in textTypeList:
				self.AddTextType(childText, textType.split("#"))
			childText.SetText(str(text))
			if childText.GetTextSize()[0] > width:
				width = childText.GetTextSize()[0]
			childText.Show()
			self.children.append(childText)
			yPosition+=yRange

	def AddTextType(self, text,  typeArg):
		if len(typeArg) != 2:
			return
		_typeDict = {
			"vertical": {
				"top":text.SetVerticalAlignTop,
				"bottom":text.SetVerticalAlignBottom,
				"center":text.SetVerticalAlignCenter,
			},
			"horizontal": {
				"left":text.SetHorizontalAlignLeft,
				"right":text.SetHorizontalAlignRight,
				"center":text.SetHorizontalAlignCenter,
			},
			"all_align": {
				"1" : [text.SetHorizontalAlignCenter,text.SetVerticalAlignCenter,text.SetWindowHorizontalAlignCenter,text.SetWindowVerticalAlignCenter],
			},
		}
		(firstToken, secondToken) = tuple(typeArg)
		if _typeDict.has_key(firstToken):
			textType = _typeDict[firstToken][secondToken] if _typeDict[firstToken].has_key(secondToken) else None
			if textType != None:
				if isinstance(textType, list):
					for rule in textType:
						rule()
				else:
					textType()

class Grid:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.reset()
	def find_blank(self, width, height):
		if width > self.width or height > self.height:
			return -1
		for row in range(self.height):
			for col in range(self.width):
				index = row * self.width + col
				if self.is_empty(index, width, height):
					return index
		return -1
	def put(self, pos, width, height):
		if not self.is_empty(pos, width, height):
			return False
		for row in range(height):
			start = pos + (row * self.width)
			self.grid[start] = True
			col = 1
			while col < width:
				self.grid[start + col] = True
				col += 1
		return True
	def clear(self, pos, width, height):
		if pos < 0 or pos >= (self.width * self.height):
			return
		for row in range(height):
			start = pos + (row * self.width)
			self.grid[start] = True
			col = 1
			while col < width:
				self.grid[start + col] = False
				col += 1
	def is_empty(self, pos, width, height):
		if pos < 0:
			return False
		row = pos // self.width
		if (row + height) > self.height:
			return False
		if (pos + width) > ((row * self.width) + self.width):
			return False
		for row in range(height):
			start = pos + (row * self.width)
			if self.grid[start]:
				return False
			col = 1
			while col < width:
				if self.grid[start + col]:
					return False
				col += 1
		return True
	def get_size(self):
		return self.width * self.height
	def reset(self):
		self.grid = [False] * (self.width * self.height)

class CheckBoxAverage(Window):
	def __init__(self):
		Window.__init__(self)

		self.backgroundImage = None
		self.checkImage = None

		self.eventFunc = { "ON_CHECK" : None, "ON_UNCKECK" : None, }
		self.eventArgs = { "ON_CHECK" : None, "ON_UNCKECK" : None, }

		self.CreateElements()

	def __del__(self):
		Window.__del__(self)

		self.backgroundImage = None
		self.checkImage = None

		self.eventFunc = { "ON_CHECK" : None, "ON_UNCKECK" : None, }
		self.eventArgs = { "ON_CHECK" : None, "ON_UNCKECK" : None, }

	def CreateElements(self):
		self.backgroundImage = ImageBox()
		self.backgroundImage.SetParent(self)
		self.backgroundImage.AddFlag("not_pick")
		self.backgroundImage.SetPosition(10, 0)
		self.backgroundImage.LoadImage("d:/ymir work/ui/game/refine/checkbox.tga")
		self.backgroundImage.Show()

		self.checkImage = ImageBox()
		self.checkImage.SetParent(self)
		self.checkImage.AddFlag("not_pick")
		self.checkImage.SetPosition(10, 0)
		self.checkImage.LoadImage("d:/ymir work/ui/game/refine/checked.tga")
		self.checkImage.Hide()

		self.textInfo = TextLine()
		self.textInfo.SetParent(self)
		self.textInfo.SetPosition(23, -1)
		self.textInfo.Show()
		self.textInfo.SetOutline()

		self.SetSize(self.backgroundImage.GetWidth() + self.textInfo.GetTextSize()[0], self.backgroundImage.GetHeight() + self.textInfo.GetTextSize()[1])

	def SetTextInfo(self, info):
		if self.textInfo:
			self.textInfo.SetText(info)

		self.SetSize(self.backgroundImage.GetWidth() + self.textInfo.GetTextSize()[0], self.backgroundImage.GetHeight() + self.textInfo.GetTextSize()[1])

	def SetCheckStatus(self, flag):
		if flag: self.checkImage.Show()
		else: self.checkImage.Hide()

	def GetCheckStatus(self):
		if self.checkImage:
			return self.checkImage.IsShow()

		return False

	def SetEvent(self, func, *args):
		result = self.eventFunc.has_key(args[0])
		if result :
			self.eventFunc[args[0]] = func
			self.eventArgs[args[0]] = args
		else:
			print "[ERROR] ui.py SetEvent, Can`t Find has_key : %s" % args[0]

	def OnMouseLeftButtonUp(self):
		if self.checkImage:
			if self.checkImage.IsShow():
				self.checkImage.Hide()

				if self.eventFunc["ON_UNCKECK"]:
					apply(self.eventFunc["ON_UNCKECK"], self.eventArgs["ON_UNCKECK"])
			else:
				self.checkImage.Show()

				if self.eventFunc["ON_CHECK"]:
					apply(self.eventFunc["ON_CHECK"], self.eventArgs["ON_CHECK"])

	def OnMouseLeftButtonUp(self):
		if self.checkImage:
			if self.checkImage.IsShow():
				self.checkImage.Hide()

				if self.eventFunc["ON_UNCKECK"]:
					apply(self.eventFunc["ON_UNCKECK"], self.eventArgs["ON_UNCKECK"])
			else:
				self.checkImage.Show()

				if self.eventFunc["ON_CHECK"]:
					apply(self.eventFunc["ON_CHECK"], self.eventArgs["ON_CHECK"])	

RegisterToolTipWindow("TEXT", TextLine)
