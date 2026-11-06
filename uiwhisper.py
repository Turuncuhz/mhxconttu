import ui
import net
import chat
import player
import app
import localeInfo
import ime
import constInfo
import chr
import messenger
class WhisperButton(ui.Button):
	def __init__(self):
		ui.Button.__init__(self, "TOP_MOST")

	def __del__(self):
		ui.Button.__del__(self)

	def SetToolTipText(self, text, x=0, y = 32):
		ui.Button.SetToolTipText(self, text, x, y)
		self.ToolTipText.Show()

	def SetToolTipTextWithColor(self, text, color, x=0, y = 32):
		ui.Button.SetToolTipText(self, text, x, y)
		self.ToolTipText.SetPackedFontColor(color)
		self.ToolTipText.Show()

	def ShowToolTip(self):
		if 0 != self.ToolTipText:
			self.ToolTipText.Show()

	def HideToolTip(self):
		if 0 != self.ToolTipText:
			self.ToolTipText.Show()

class WhisperDialog(ui.ScriptWindow):

	class TextRenderer(ui.Window):
		def SetTargetName(self, targetName):
			self.targetName = targetName

		def OnRender(self):
			(x, y) = self.GetGlobalPosition()
			chat.RenderWhisper(self.targetName, x, y)

	class ResizeButton(ui.DragButton):

		def __init__(self):
			ui.DragButton.__init__(self)

		def __del__(self):
			ui.DragButton.__del__(self)

		def OnMouseOverIn(self):
			app.SetCursor(app.HVSIZE)

		def OnMouseOverOut(self):
			app.SetCursor(app.NORMAL)

	def __init__(self, eventMinimize, eventClose):
		print "NEW WHISPER DIALOG  ----------------------------------------------------------------------------"
		ui.ScriptWindow.__init__(self)
		self.targetName = ""
		self.eventMinimize = eventMinimize
		self.eventClose = eventClose
		self.eventAcceptTarget = None
	def __del__(self):
		print "---------------------------------------------------------------------------- DELETE WHISPER DIALOG"
		ui.ScriptWindow.__del__(self)

	def LoadDialog(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/WhisperDialog.py")
		except:
			import exception
			exception.Abort("WhisperDialog.LoadDialog.LoadScript")

		try:
			GetObject=self.GetChild
			self.titleName = GetObject("titlename")
			self.titleNameEdit = GetObject("titlename_edit")
			self.closeButton = GetObject("closebutton")
			self.scrollBar = GetObject("scrollbar")
			self.chatLine = GetObject("chatline")
			self.minimizeButton = GetObject("minimizebutton")
			self.blockButton = GetObject("blockButton")
			self.acceptButton = GetObject("acceptbutton")
			self.sendButton = GetObject("sendbutton")
			self.board = GetObject("board")
			self.editBar = GetObject("editbar")
			self.gamemasterMark = GetObject("gamemastermark")
		except:
			import exception
			exception.Abort("DialogWindow.LoadDialog.BindObject")

		self.gamemasterMark.Hide()
		self.titleName.SetText("")
		self.titleNameEdit.SetText("")
		self.minimizeButton.SetEvent(ui.__mem_func__(self.Minimize))
		self.closeButton.SetEvent(ui.__mem_func__(self.Close))
		self.scrollBar.SetPos(1.0)
		self.scrollBar.SetScrollEvent(ui.__mem_func__(self.OnScroll))
		self.chatLine.SetReturnEvent(ui.__mem_func__(self.SendWhisper))
		self.chatLine.SetEscapeEvent(ui.__mem_func__(self.Minimize))
		self.chatLine.SetMultiLine()
		if self.editBar:
			self.editBar.SetEvent(ui.__mem_func__(self.FocusChatLine))
		self.sendButton.SetEvent(ui.__mem_func__(self.SendWhisper))
		self.titleNameEdit.SetReturnEvent(ui.__mem_func__(self.AcceptTarget))
		self.titleNameEdit.SetEscapeEvent(ui.__mem_func__(self.Close))
		self.blockButton.SetToggleDownEvent(ui.__mem_func__(self.blockTarget))
		self.blockButton.SetToggleUpEvent(ui.__mem_func__(self.unblockTarget))
		self.acceptButton.SetEvent(ui.__mem_func__(self.AcceptTarget))

		self.textRenderer = self.TextRenderer()
		self.textRenderer.SetParent(self)
		self.textRenderer.SetPosition(20, 28)
		self.textRenderer.SetTargetName("")
		self.textRenderer.Show()

		self.resizeButton = self.ResizeButton()
		self.resizeButton.SetParent(self)
		self.resizeButton.SetSize(20, 20)
		self.resizeButton.SetPosition(280, 180)
		self.resizeButton.SetMoveEvent(ui.__mem_func__(self.ResizeWhisperDialog))
		self.resizeButton.Show()

		self.ResizeWhisperDialog()

	def Destroy(self):

		self.eventMinimize = None
		self.eventClose = None
		self.eventAcceptTarget = None

		self.ClearDictionary()
		self.scrollBar.Destroy()
		self.titleName = None
		self.titleNameEdit = None
		self.closeButton = None
		self.scrollBar = None
		self.chatLine = None
		self.sendButton = None
		self.blockButton = None
		self.acceptButton = None
		self.minimizeButton = None
		self.textRenderer = None
		self.board = None
		self.editBar = None
		self.resizeButton = None

	def ResizeWhisperDialog(self):
		(xPos, yPos) = self.resizeButton.GetLocalPosition()
		if xPos < 280:
			self.resizeButton.SetPosition(280, yPos)
			return
		if yPos < 150:
			self.resizeButton.SetPosition(xPos, 150)
			return
		self.SetWhisperDialogSize(xPos + 20, yPos + 20)

	def SetWhisperDialogSize(self, width, height):
		try:

			max = int((width-90)/6) * 3 - 6

			self.board.SetSize(width, height)
			self.scrollBar.SetPosition(width-25, 35)
			self.scrollBar.SetScrollBarSize(height-100)
			self.scrollBar.SetPos(1.0)
			self.editBar.SetSize(width-18, 50)
			self.chatLine.SetSize(width-90, 40)
			self.chatLine.SetLimitWidth(width-90)
			self.SetSize(width, height)

			if 0 != self.targetName:
				chat.SetWhisperBoxSize(self.targetName, width - 50, height - 90)

			self.textRenderer.SetPosition(20, 28)
			self.scrollBar.SetPosition(width-25, 35)
			self.editBar.SetPosition(10, height-60)
			self.sendButton.SetPosition(width-80, 10)
			self.minimizeButton.SetPosition(width-42, 12)
			self.closeButton.SetPosition(width-24, 12)

			self.SetChatLineMax(max)

		except:
			import exception
			exception.Abort("WhisperDialog.SetWhisperDialogSize.BindObject")

	def SetChatLineMax(self, max):
		if max > 230:
			max = 230
		self.chatLine.SetMax(max)

		from grpText import GetSplitingTextLine

		text = self.chatLine.GetText()
		if text:
			self.chatLine.SetText(GetSplitingTextLine(text, max, 0))

	def OpenWithTarget(self, targetName):
		chat.CreateWhisper(targetName)
		chat.SetWhisperBoxSize(targetName, self.GetWidth() - 60, self.GetHeight() - 90)
		self.FocusChatLine()
		self.titleName.SetText(targetName)
		self.targetName = targetName
		self.textRenderer.SetTargetName(targetName)
		self.titleNameEdit.Hide()

		self.blockButton.Show()
		self.acceptButton.Hide()
		# if not targetName in constInfo.WARNING_WHISPER_GM:
			# constInfo.WARNING_WHISPER_GM.update({targetName : {}})
			# chat.AppendWhisper(chat.WHISPER_TYPE_SYSTEM, self.targetName, localeInfo.WARNING_PASSWORD)
		self.gamemasterMark.Hide()
		self.minimizeButton.Show()

		if not messenger.IsFriendByName(self.targetName):
			self.friendButton = ui.Button()
			self.friendButton.SetParent(self.board)
			self.friendButton.SetPosition(122, 10)
			self.friendButton.SetUpVisual("d:/ymir work/ui/game/windows/messenger_add_friend_01.sub")
			self.friendButton.SetOverVisual("d:/ymir work/ui/game/windows/messenger_add_friend_02.sub")
			self.friendButton.SetDownVisual("d:/ymir work/ui/game/windows/messenger_add_friend_03.sub")
			self.friendButton.SetText("")
			self.friendButton.SetEvent(ui.__mem_func__(self.AddFrind))
			self.friendButton.Show()
	def AddFrind(self):
		net.SendMessengerAddByNamePacket(self.targetName)
		self.friendButton.Hide()
	def OpenWithoutTarget(self, event):
		self.eventAcceptTarget = event
		self.titleName.SetText("")
		self.titleNameEdit.SetText("")
		self.titleNameEdit.SetFocus()
		self.targetName = 0
		self.titleNameEdit.Show()
		self.blockButton.Hide()
		self.acceptButton.Show()
		self.minimizeButton.Hide()
		self.gamemasterMark.Hide()

	def SetGameMasterLook(self):
		self.gamemasterMark.Show()
		self.blockButton.Hide()

	def Minimize(self):
		self.titleNameEdit.KillFocus()
		self.chatLine.KillFocus()
		self.Hide()

		if None != self.eventMinimize:
			self.eventMinimize(self.targetName)

	def Close(self):
		chat.ClearWhisper(self.targetName)
		self.titleNameEdit.KillFocus()
		self.chatLine.KillFocus()
		self.Hide()

		if None != self.eventClose:
			self.eventClose(self.targetName)



	def blockTarget(self):
		net.SendMessengerAddBlockByNamePacket(self.targetName)
	def unblockTarget(self):
		messenger.RemoveBlock(constInfo.ME_KEY)
		net.SendMessengerRemoveBlockPacket(constInfo.ME_KEY, self.targetName)

	def AcceptTarget(self):
		name = self.titleNameEdit.GetText()
		if len(name) <= 0:
			self.Close()
			return

		if None != self.eventAcceptTarget:
			self.titleNameEdit.KillFocus()
			self.eventAcceptTarget(name)

	def OnScroll(self):
		chat.SetWhisperPosition(self.targetName, self.scrollBar.GetPos())

	def SendWhisper(self):

		text = self.chatLine.GetText()
		textLength = len(text)

		if app.ENABLE_PM_ALL_SEND_SYSTEM:
			if self.targetName == "[Sistem]":
				return;

			if self.targetName == "[Biyolog]":
				return;

		if textLength > 0:
			if net.IsInsultIn(text):
				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.CHAT_INSULT_STRING)
				return

			net.SendWhisperPacket(self.targetName, text)
			self.chatLine.SetText("")

			chat.AppendWhisper(chat.WHISPER_TYPE_CHAT, self.targetName, player.GetName() + " : " + text)

	def FocusChatLine(self):
		if self.chatLine:
			self.chatLine.SetFocus()
			import ime
			ime.EnableCaptureInput()
			if hasattr(app, "ShowKeyboard"):
				app.ShowKeyboard(1)

	def OnTop(self):
		self.FocusChatLine()

	def BindInterface(self, interface):
		self.interface = interface

	def OnPressEscapeKey(self):
		self.Minimize()
		return True
	def OnMouseLeftButtonDown(self):
		hyperlink = ui.GetHyperlink()
		if hyperlink:
			if app.IsPressed(app.DIK_LALT):
				link = chat.GetLinkFromHyperlink(hyperlink)
				ime.PasteString(link)
			else:
				self.interface.MakeHyperlinkTooltip(hyperlink)

if "__main__" == __name__:
	import uiTest

	class TestApp(uiTest.App):
		def OnInit(self):
			wnd = WhisperDialog(self.OnMax, self.OnMin)
			wnd.LoadDialog()
			wnd.OpenWithoutTarget(self.OnNew)
			wnd.SetPosition(0, 0)
			wnd.Show()

			self.wnd = wnd

		def OnMax(self):
			pass

		def OnMin(self):
			pass

		def OnNew(self):
			pass

	TestApp().MainLoop()
