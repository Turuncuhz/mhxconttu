import os

import app

import dbg

import grp

import item

import background

import chr

import chrmgr

import player

import snd

import chat

import textTail

import snd

import net

import effect

import wndMgr

import fly

import systemSetting

import quest

import guild

import skill

import messenger

import localeInfo

import constInfo

import exchange

import ime



import ui

import uiCommon

import uiPhaseCurtain

import uiMapNameShower

import uiAffectShower

import uiPlayerGauge

import uiCharacter

import uiTarget

import uiMenuSystem



import savbec

import surabec

import ninjabec

import samanbec



import pysettings

# PRIVATE_SHOP_PRICE_LIST

import uiPrivateShopBuilder

# END_OF_PRIVATE_SHOP_PRICE_LIST



import mouseModule

import consoleModule



import playerSettingModule

import interfaceModule

import uiMobileHud	# Cynex: dokunmatik arayuz

import uiMobileHudController



if app.ENABLE_DRAGON_COIN_SHOP_SYSTEM:

	import uiDcItemShop



if app.ENABLE_DRAGON_COIN_SHOP_ADMIN_SYSTEM:

	import uiDcItemShopAdmin



if app.ENABLE_PM_ALL_SEND_SYSTEM:

	import uiWhisperAdmin



if app.ENABLE_WHEEL_OF_FORTUNE:

	import uiWheelofFortune



if app.ENABLE_TELEPORTION_WIZARD_SYSTEM:

	import uiTpWizardInfo



if app.ENABLE_RONARK_SYSTEM:

	import uiRonark

if app.SPIN_WHEEL:

	import uispinwheel



import musicInfo

import debugInfo

import stringCommander



svsidedia = None

svsidedi_cp =  ""

from svsideoi import SvsideDialog

import binascii



from _weakref import proxy



# SCREENSHOT_CWDSAVE

SCREENSHOT_CWDSAVE = True

SCREENSHOT_DIR = None



cameraDistance = 1550.0

cameraPitch = 27.0

cameraRotation = 0.0

cameraHeight = 100.0



# Cynex: telefonda giris kamerasi suruklemeden sonraki egimle ayni

if uiMobileHud.IsCameraSettingSupported():

	cameraPitch = uiMobileHud.GetCameraPitch()



testAlignment = 0



class GameWindow(ui.ScriptWindow):

	def __init__(self, stream):

		ui.ScriptWindow.__init__(self, "GAME")

		self.SetWindowName("game")

		net.SetPhaseWindow(net.PHASE_WINDOW_GAME, self)

		player.SetGameWindow(self)



		if app.__BACK_DUNGEON__:

			self.questionReJoinDialogDict = {}



		global svsidedia

		if svsidedia == None:

			svsidedia = SvsideDialog()

		svsidedia.Board.Hide()



		self.quickSlotPageIndex = 0

		self.lastPKModeSendedTime = 0

		self.shouttime = 0

		self.pressNumber = None



		if app.ENABLE_WHEEL_OF_FORTUNE:

			self.wheelShowButton = None

			self.wheelEventShowButton = None



		if app.ENABLE_TANAKA_EVENT:

			self.TanakaEventQuestDialog = None

			import uitanakaevent

			self.tanakaBoard = uitanakaevent.TanakaEventBoard()

			self.tanakaBoard.Hide()

			self.tanakaBoard.LoadDialog()



		if app.ENABLE_PUBLISHER_SYSTEM:

			self.publisherShowButton = None

			self.publisherCloseButton = None



		self.OtoToplamaDurum = 0

		self.OtoToplamaTime = 0



		self.guildWarQuestionDialog = None

		self.interface = None

		self.targetBoard = None

		self.console = None

		self.mapNameShower = None

		self.affectShower = None

		self.playerGauge = None

		self.loopList = []



		self.SelectSkill = None



		self.mobileHud = None

		self.touchRefreshPending = False



		self.stream=stream

		self.interface = interfaceModule.Interface()

		self.interface.MakeInterface()

		self.interface.ShowDefaultWindows()



		if app.ENABLE_MULTI_FARM_BLOCK:

			constInfo.SetInterfaceInstance(self.interface)



		self.curtain = uiPhaseCurtain.PhaseCurtain()

		self.curtain.speed = 0.03

		self.curtain.Hide()



		self.targetBoard = uiTarget.TargetBoard()

		self.targetBoard.SetWhisperEvent(ui.__mem_func__(self.interface.OpenWhisperDialog))

		self.targetBoard.Hide()



		self.console = consoleModule.ConsoleWindow()

		self.console.BindGameClass(self)

		self.console.SetConsoleSize(wndMgr.GetScreenWidth(), 200)

		self.console.Hide()



		self.mapNameShower = uiMapNameShower.MapNameShower()

		if app.ENABLE_EXCHANGE_LOG:

			constInfo.SetGameInstance(self)

		self.affectShower = uiAffectShower.AffectShower()



		self.playerGauge = uiPlayerGauge.PlayerGauge(self)

		self.playerGauge.Hide()



		if app.ENABLE_RONARK_SYSTEM:

			self.ronarkWarScoreBoard = uiRonark.RonarkWarScoreBoard()

			self.ronarkWarScoreBoard.LoadDialog()

			self.ronarkWarScoreBoard.Hide()



		if app.ENABLE_PM_ALL_SEND_SYSTEM:

			import uiwhisperadmin

			self.whisperAdmin = uiwhisperadmin.AdminWhisperManager()

			self.whisperAdmin.Close()

		if app.SPIN_WHEEL:

			self.wheelWindow = uispinwheel.WheelWindow()

			self.wheelWindow.Hide()

		self.CollectiveMenu = uiMenuSystem.MenuSystemDialog()

		self.CollectiveMenu.Hide()



		self.itemDropQuestionDialog = None



		self.__SetQuickSlotMode()



		self.__ServerCommand_Build()

		self.__ProcessPreservedServerCommand()



		# Cynex: masaustu arayuzunun ustune dokunmatik katman

		uiMobileHud.Refresh()

		self.RefreshTouchLayout()

		uiMobileHud.BindRefreshRequest(ui.__mem_func__(self.RequestTouchRefresh))







	def __del__(self):

		player.SetGameWindow(0)

		net.ClearPhaseWindow(net.PHASE_WINDOW_GAME, self)

		ui.ScriptWindow.__del__(self)



	def Open(self):

		app.SetFrameSkip(1)



		self.SetSize(wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())



		self.quickSlotPageIndex = 0

		self.PickingCharacterIndex = -1

		self.PickingItemIndex = -1

		self.consoleEnable = False

		self.isShowDebugInfo = False

		self.ShowNameFlag = False
		if app.ENABLE_IKASHOP_RENEWAL:
			try:
				import ikashop
				ikashop.ShowShopNames()
			except Exception:
				pass



		self.enableXMasBoom = False

		self.startTimeXMasBoom = 0.0

		self.indexXMasBoom = 0



		global cameraDistance, cameraPitch, cameraRotation, cameraHeight



		app.SetCamera(cameraDistance, cameraPitch, cameraRotation, cameraHeight)



		constInfo.SET_DEFAULT_CAMERA_MAX_DISTANCE()

		constInfo.SET_DEFAULT_CHRNAME_COLOR()

		constInfo.SET_DEFAULT_FOG_LEVEL()

		constInfo.SET_DEFAULT_CONVERT_EMPIRE_LANGUAGE_ENABLE()

		constInfo.SET_DEFAULT_USE_ITEM_WEAPON_TABLE_ATTACK_BONUS()

		constInfo.SET_DEFAULT_USE_SKILL_EFFECT_ENABLE()



		# TWO_HANDED_WEAPON_ATTACK_SPEED_UP

		constInfo.SET_TWO_HANDED_WEAPON_ATT_SPEED_DECREASE_VALUE()

		# END_OF_TWO_HANDED_WEAPON_ATTACK_SPEED_UP



		import event

		event.SetLeftTimeString(localeInfo.UI_LEFT_TIME)



		textTail.EnablePKTitle(constInfo.PVPMODE_ENABLE)



		if constInfo.PVPMODE_TEST_ENABLE:

			self.testPKMode = ui.TextLine()

			self.testPKMode.SetFontName(localeInfo.UI_DEF_FONT)

			self.testPKMode.SetPosition(0, 15)

			self.testPKMode.SetWindowHorizontalAlignCenter()

			self.testPKMode.SetHorizontalAlignCenter()

			self.testPKMode.SetFeather()

			self.testPKMode.SetOutline()

			self.testPKMode.Show()



			self.testAlignment = ui.TextLine()

			self.testAlignment.SetFontName(localeInfo.UI_DEF_FONT)

			self.testAlignment.SetPosition(0, 35)

			self.testAlignment.SetWindowHorizontalAlignCenter()

			self.testAlignment.SetHorizontalAlignCenter()

			self.testAlignment.SetFeather()

			self.testAlignment.SetOutline()

			self.testAlignment.Show()



		self.__BuildKeyDict()

		self.__BuildDebugInfo()



		# PRIVATE_SHOP_PRICE_LIST

		uiPrivateShopBuilder.Clear()

		# END_OF_PRIVATE_SHOP_PRICE_LIST



		# UNKNOWN_UPDATE

		exchange.InitTrading()

		# END_OF_UNKNOWN_UPDATE





		## Sound

		snd.SetMusicVolume(systemSetting.GetMusicVolume()*net.GetFieldMusicVolume())

		snd.SetSoundVolume(systemSetting.GetSoundVolume())



		netFieldMusicFileName = net.GetFieldMusicFileName()

		if netFieldMusicFileName:

			snd.FadeInMusic("BGM/" + netFieldMusicFileName)

		elif musicInfo.fieldMusic != "":

			snd.FadeInMusic("BGM/" + musicInfo.fieldMusic)



		self.__SetQuickSlotMode()

		self.__SelectQuickPage(self.quickSlotPageIndex)



		self.SetFocus()

		self.Show()

		app.ShowCursor()



		net.SendEnterGamePacket()



		try:

			self.StartGame()

		except:

			import exception

			exception.Abort("GameWindow.Open")



		self.cubeInformation = {}

		self.currentCubeNPC = 0

		self.shouttime = app.GetTime()+5



		################################

		if app.ENABLE_DRAGON_COIN_SHOP_SYSTEM:

			uiDcItemShop.ItemShopClear()

			uiDcItemShop.ItemShopLogClear()



		if app.ENABLE_DRAGON_COIN_EM_MARKET:

			uiDcItemShop.ItemShopEmClear()

		################################



		if app.ENABLE_FPS:

			systemSetting.SetFPS(2)



		if app.ENABLE_ANTI_EXP:

			self.SetAntiExp()



		if app.ENABLE_FOG_FIX:

			if systemSetting.IsFogMode():

				background.SetEnvironmentFog(True)

			else:

				background.SetEnvironmentFog(False)



		if systemSetting.GetNightMode():

			systemSetting.SetNightMode(True)

			background.RegisterEnvironmentData(1, constInfo.ENVIRONMENT_NIGHT)

			background.SetEnvironmentData(1)

		else:

			systemSetting.SetNightMode(False)

			background.SetEnvironmentData(0)



		# if str(background.GetCurrentMapName()) in "metin2_map_deviltower1":

		# if str(background.GetCurrentMapName()) in "metin2_map_devilscatacomb":

			# systemSetting.SetExtremeFpsBoost(False)

		systemSetting.SetExtremeFpsBoost(False)



		if systemSetting.GetAffectIcons():

			self.affectShower.Show()

		else:

			self.affectShower.Hide()



		self.OtoToplamaTime = app.GetTime()+4



	def Close(self):

		self.Hide()



		# Cynex: hud ana karakterden once kapanir (yuruyus ve saldiri durur)

		self.__DestroyMobileHud(False)

		uiMobileHud.BindRefreshRequest(None)

		uiMobileHud.SetDoubleTapGate(False)



		if app.ENABLE_MULTI_FARM_BLOCK:

			app.SetMultiFarmExeIcon(0)



		if app.__BACK_DUNGEON__:

			self.__CancelReJoinDungeon()



		global cameraDistance, cameraPitch, cameraRotation, cameraHeight

		(cameraDistance, cameraPitch, cameraRotation, cameraHeight) = app.GetCamera()



		if musicInfo.fieldMusic != "":

			snd.FadeOutMusic("BGM/"+ musicInfo.fieldMusic)



		self.onPressKeyDict = None

		self.onClickKeyDict = None

		self.loopList = []

		# if app.__WHISPER_FUTURES__:

			# chat.SaveWhispers()

		chat.Close()

		snd.StopAllSound()

		grp.InitScreenEffect()

		chr.Destroy()

		textTail.Clear()

		quest.Clear()

		background.Destroy()

		guild.Destroy()

		messenger.Destroy()

		skill.ClearSkillData()

		wndMgr.Unlock()

		mouseModule.mouseController.DeattachObject()



		if self.guildWarQuestionDialog:

			self.guildWarQuestionDialog.Close()



		self.guildNameBoard = None

		self.partyRequestQuestionDialog = None

		self.partyInviteQuestionDialog = None

		self.guildInviteQuestionDialog = None

		self.guildWarQuestionDialog = None

		self.messengerAddFriendQuestion = None



		self.OtoToplamaDurum = 0

		self.OtoToplamaTime = 0



		# UNKNOWN_UPDATE

		self.itemDropQuestionDialog = None

		# END_OF_UNKNOWN_UPDATE



		# QUEST_CONFIRM

		self.confirmDialog = None

		# END_OF_QUEST_CONFIRM



		self.PrintCoord = None

		self.FrameRate = None

		self.Pitch = None

		self.Splat = None

		self.TextureNum = None

		self.ObjectNum = None

		self.ViewDistance = None

		self.PrintMousePos = None



		self.ClearDictionary()



		if app.SPIN_WHEEL:

			if self.wheelWindow:

				self.wheelWindow.Destroy()

				self.wheelWindow = None

		self.playerGauge = None

		self.mapNameShower = None

		self.affectShower = None



		if self.SelectSkill:

			self.SelectSkill.Hide()

			self.SelectSkill = None



		if self.console:

			self.console.BindGameClass(0)

			self.console.Close()

			self.console=None



		if self.targetBoard:

			self.targetBoard.Destroy()

			self.targetBoard = None



		if self.interface:

			self.interface.HideAllWindows()

			self.interface.Close()

			self.interface=None



		if app.ENABLE_RONARK_SYSTEM:

			if self.ronarkWarScoreBoard:

				self.ronarkWarScoreBoard.Hide()

				self.ronarkWarScoreBoard.Destroy()

				self.ronarkWarScoreBoard = None



		if app.ENABLE_PM_ALL_SEND_SYSTEM:

			if self.whisperAdmin:

				self.whisperAdmin.Close()

				self.whisperAdmin = None



		if app.ENABLE_WHEEL_OF_FORTUNE:

			if self.wheelShowButton:

				self.wheelShowButton.Hide()

				self.wheelShowButton = None



			if self.wheelEventShowButton:

				self.wheelEventShowButton.Hide()

				self.wheelEventShowButton = None



		if app.ENABLE_TANAKA_EVENT:

			if self.TanakaEventQuestDialog:

				self.TanakaEventQuestDialog.Close()

				self.TanakaEventQuestDialog = None



			if self.tanakaBoard:

				self.tanakaBoard.Hide()

				self.tanakaBoard = None



		if self.CollectiveMenu:

			self.CollectiveMenu.Hide()

			self.CollectiveMenu = None



		if app.ENABLE_PUBLISHER_SYSTEM:

			if self.publisherShowButton:

				self.publisherShowButton.Hide()

				self.publisherShowButton = None



			if self.publisherCloseButton:

				self.publisherCloseButton.Hide()

				self.publisherCloseButton = None



		player.ClearSkillDict()

		player.ResetCameraRotation()



		self.KillFocus()

		app.HideCursor()



		if app.ENABLE_EXCHANGE_LOG:

			constInfo.SetGameInstance(None)



		if app.ENABLE_MULTI_FARM_BLOCK:

			constInfo.SetInterfaceInstance(None)



		print "---------------------------------------------------------------------------- CLOSE GAME WINDOW"



	def __BuildKeyDict(self):

		onPressKeyDict = {}





		onPressKeyDict[app.DIK_1]	= lambda : self.__PressNumKey(1)

		onPressKeyDict[app.DIK_2]	= lambda : self.__PressNumKey(2)

		onPressKeyDict[app.DIK_3]	= lambda : self.__PressNumKey(3)

		onPressKeyDict[app.DIK_4]	= lambda : self.__PressNumKey(4)

		onPressKeyDict[app.DIK_5]	= lambda : self.__PressNumKey(5)

		onPressKeyDict[app.DIK_6]	= lambda : self.__PressNumKey(6)

		onPressKeyDict[app.DIK_7]	= lambda : self.__PressNumKey(7)

		onPressKeyDict[app.DIK_8]	= lambda : self.__PressNumKey(8)

		onPressKeyDict[app.DIK_9]	= lambda : self.__PressNumKey(9)

		onPressKeyDict[app.DIK_F1]	= lambda : self.__PressQuickSlot(4)

		onPressKeyDict[app.DIK_F2]	= lambda : self.__PressQuickSlot(5)

		onPressKeyDict[app.DIK_F3]	= lambda : self.__PressQuickSlot(6)

		onPressKeyDict[app.DIK_F4]	= lambda : self.__PressQuickSlot(7)



		if app.ENABLE_SPECIAL_STORAGE:

			onPressKeyDict[app.DIK_K]	= lambda: self.interface.ToggleSpecialStorageWindow()



		onPressKeyDict[app.DIK_LALT]		= lambda : self.ShowName()

		onPressKeyDict[app.DIK_LCONTROL]	= lambda : self.ShowMouseImage()

		onPressKeyDict[app.DIK_SYSRQ]		= lambda : self.SaveScreen()

		onPressKeyDict[app.DIK_SPACE]		= lambda : self.StartAttack()

		onPressKeyDict[app.DIK_TAB]			= lambda : self.__PressTabKey()



		onPressKeyDict[app.DIK_UP]			= lambda : self.MoveUp()

		onPressKeyDict[app.DIK_DOWN]		= lambda : self.MoveDown()

		onPressKeyDict[app.DIK_LEFT]		= lambda : self.MoveLeft()

		onPressKeyDict[app.DIK_RIGHT]		= lambda : self.MoveRight()

		onPressKeyDict[app.DIK_W]			= lambda : self.MoveUp()

		onPressKeyDict[app.DIK_S]			= lambda : self.MoveDown()

		onPressKeyDict[app.DIK_A]			= lambda : self.MoveLeft()

		onPressKeyDict[app.DIK_D]			= lambda : self.MoveRight()



		onPressKeyDict[app.DIK_E]			= lambda: app.RotateCamera(app.CAMERA_TO_POSITIVE)

		onPressKeyDict[app.DIK_R]			= lambda: app.ZoomCamera(app.CAMERA_TO_NEGATIVE)

		onPressKeyDict[app.DIK_T]			= lambda: app.PitchCamera(app.CAMERA_TO_NEGATIVE)

		onPressKeyDict[app.DIK_G]			= self.__PressGKey

		onPressKeyDict[app.DIK_Q]			= self.__PressQKey



		onPressKeyDict[app.DIK_NUMPAD9]		= lambda: app.MovieResetCamera()

		onPressKeyDict[app.DIK_NUMPAD4]		= lambda: app.MovieRotateCamera(app.CAMERA_TO_NEGATIVE)

		onPressKeyDict[app.DIK_NUMPAD6]		= lambda: app.MovieRotateCamera(app.CAMERA_TO_POSITIVE)

		onPressKeyDict[app.DIK_PGUP]		= lambda: app.MovieZoomCamera(app.CAMERA_TO_NEGATIVE)

		onPressKeyDict[app.DIK_PGDN]		= lambda: app.MovieZoomCamera(app.CAMERA_TO_POSITIVE)

		onPressKeyDict[app.DIK_NUMPAD8]		= lambda: app.MoviePitchCamera(app.CAMERA_TO_NEGATIVE)

		onPressKeyDict[app.DIK_NUMPAD2]		= lambda: app.MoviePitchCamera(app.CAMERA_TO_POSITIVE)

		onPressKeyDict[app.DIK_GRAVE]		= lambda : self.PickUpItem()

		onPressKeyDict[app.DIK_Z]			= lambda : self.PickUpItem()

		onPressKeyDict[app.DIK_C]			= lambda state = "STATUS": self.interface.ToggleCharacterWindow(state)

		onPressKeyDict[app.DIK_V]			= lambda state = "SKILL": self.interface.ToggleCharacterWindow(state)

		onPressKeyDict[app.DIK_N]			= lambda state = "QUEST": self.interface.ToggleCharacterWindow(state)

		onPressKeyDict[app.DIK_I]			= lambda : self.interface.ToggleInventoryWindow()

		onPressKeyDict[app.DIK_O]			= lambda : self.interface.OpenAutoHunt()

		onPressKeyDict[app.DIK_M]			= lambda : self.interface.PressMKey()

		onPressKeyDict[app.DIK_ADD]			= lambda : self.interface.MiniMapScaleUp()

		onPressKeyDict[app.DIK_SUBTRACT]	= lambda : self.interface.MiniMapScaleDown()

		onPressKeyDict[app.DIK_L]			= lambda : self.interface.ToggleChatLogWindow()

		onPressKeyDict[app.DIK_COMMA]		= lambda : self.ShowConsole()		# "`" key

		onPressKeyDict[app.DIK_LSHIFT]		= lambda : self.__SetQuickPageMode()

		onPressKeyDict[app.DIK_J]			= lambda : self.interface.OpenBiologWindow()

		# onPressKeyDict[app.DIK_J]			= lambda : self.__PressJKey()

		onPressKeyDict[app.DIK_H]			= lambda : self.__PressHKey()

		onPressKeyDict[app.DIK_B]			= lambda : self.__PressBKey()

		onPressKeyDict[app.DIK_F]			= lambda : self.__PressFKey()



		if app.ENABLE_IKASHOP_RENEWAL:

			onPressKeyDict[app.DIK_Y]		= lambda : self.__PressYKey()



		##Balýk

		onPressKeyDict[app.DIK_P]			= lambda : self.interface.OpenFishBot()



		onPressKeyDict[app.DIK_F5]			= lambda : self.CollectiveMenu.OpenDialog()



		# #Efsun Botu

		# if app.ENABLE_SWITCHBOT:

			# onPressKeyDict[app.DIK_F6]		= lambda : self.interface.ToggleSwitchbotWindow()



		# OtomatikSatiþ

		onPressKeyDict[app.DIK_F6]		= lambda : self.interface.OpenAutoSell()



		#Biyolog 

		onPressKeyDict[app.DIK_F7]			= lambda : self.interface.OpenBiologWindow()



		if app.ENABLE_REWARD_SYSTEM:

			onPressKeyDict[app.DIK_F8]		= lambda : self.OpenRewardPlayers()



		onPressKeyDict[app.DIK_F9]			= lambda : net.SendBattlePassAction(1)



		if app.ENABLE_EXCHANGE_LOG:

			onPressKeyDict[app.DIK_F11]		= lambda : self.interface.OpenExchangeLog()



		if app.__AUTO_HUNT__:

			onPressKeyDict[app.DIK_F12]		= lambda : self.interface.OpenAutoHunt()



		self.onPressKeyDict = onPressKeyDict



		onClickKeyDict = {}

		onClickKeyDict[app.DIK_UP] = lambda : self.StopUp()

		onClickKeyDict[app.DIK_DOWN] = lambda : self.StopDown()

		onClickKeyDict[app.DIK_LEFT] = lambda : self.StopLeft()

		onClickKeyDict[app.DIK_RIGHT] = lambda : self.StopRight()

		onClickKeyDict[app.DIK_SPACE] = lambda : self.EndAttack()



		onClickKeyDict[app.DIK_W] = lambda : self.StopUp()

		onClickKeyDict[app.DIK_S] = lambda : self.StopDown()

		onClickKeyDict[app.DIK_A] = lambda : self.StopLeft()

		onClickKeyDict[app.DIK_D] = lambda : self.StopRight()

		onClickKeyDict[app.DIK_Q] = lambda: app.RotateCamera(app.CAMERA_STOP)

		onClickKeyDict[app.DIK_E] = lambda: app.RotateCamera(app.CAMERA_STOP)

		onClickKeyDict[app.DIK_R] = lambda: app.ZoomCamera(app.CAMERA_STOP)

		onClickKeyDict[app.DIK_F] = lambda: app.ZoomCamera(app.CAMERA_STOP)

		onClickKeyDict[app.DIK_T] = lambda: app.PitchCamera(app.CAMERA_STOP)

		onClickKeyDict[app.DIK_G] = lambda: self.__ReleaseGKey()

		onClickKeyDict[app.DIK_NUMPAD4] = lambda: app.MovieRotateCamera(app.CAMERA_STOP)

		onClickKeyDict[app.DIK_NUMPAD6] = lambda: app.MovieRotateCamera(app.CAMERA_STOP)

		onClickKeyDict[app.DIK_PGUP] = lambda: app.MovieZoomCamera(app.CAMERA_STOP)

		onClickKeyDict[app.DIK_PGDN] = lambda: app.MovieZoomCamera(app.CAMERA_STOP)

		onClickKeyDict[app.DIK_NUMPAD8] = lambda: app.MoviePitchCamera(app.CAMERA_STOP)

		onClickKeyDict[app.DIK_NUMPAD2] = lambda: app.MoviePitchCamera(app.CAMERA_STOP)

		onClickKeyDict[app.DIK_LALT] = lambda: self.HideName()

		onClickKeyDict[app.DIK_LCONTROL] = lambda: self.HideMouseImage()

		onClickKeyDict[app.DIK_LSHIFT] = lambda: self.__SetQuickSlotMode()



		#if constInfo.PVPMODE_ACCELKEY_ENABLE:

		#	onClickKeyDict[app.DIK_B] = lambda: self.ChangePKMode()



		self.onClickKeyDict=onClickKeyDict



	if app.ENABLE_IKASHOP_RENEWAL:

		def __PressYKey(self):

			self.interface.ToggleIkashopBusinessBoard()



	def __PressNumKey(self,num):

		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):



			if num >= 1 and num <= 9:

				if(chrmgr.IsPossibleEmoticon(-1)):

					chrmgr.SetEmoticon(-1,int(num)-1)

					net.SendEmoticon(int(num)-1)

		else:

			if num >= 1 and num <= 4:

				self.pressNumber(num-1)



	def __ClickBKey(self):

		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):

			return

		else:

			if constInfo.PVPMODE_ACCELKEY_ENABLE:

				self.ChangePKMode()





	# def	__PressJKey(self):

		# if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):

			# if player.IsMountingHorse():

				# net.SendChatPacket("/unmount")

			# else:

				net.SendChatPacket("/user_horse_ride")

				# if not uiPrivateShopBuilder.IsBuildingPrivateShop():

					# for i in xrange(player.INVENTORY_PAGE_SIZE*player.INVENTORY_PAGE_COUNT):

						# if player.GetItemIndex(i) in (71114, 71116, 71118, 71120):

							# net.SendItemUsePacket(i)

							# break

	def	__PressHKey(self):

		net.SendChatPacket("/user_horse_ride")





	def	__PressBKey(self):

		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):

			net.SendChatPacket("/user_horse_back")

		else:

			state = "EMOTICON"

			self.interface.ToggleCharacterWindow(state)



	def	__PressFKey(self):

		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):

			net.SendChatPacket("/user_horse_feed")

		else:

			app.ZoomCamera(app.CAMERA_TO_POSITIVE)



	def __PressGKey(self):

		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):

			net.SendChatPacket("/ride")

		else:

			if self.ShowNameFlag:

				self.interface.ToggleGuildWindow()

			else:

				app.PitchCamera(app.CAMERA_TO_POSITIVE)



	def	__ReleaseGKey(self):

		app.PitchCamera(app.CAMERA_STOP)



	def __PressQKey(self):

		if app.IsPressed(app.DIK_LCONTROL) or app.IsPressed(app.DIK_RCONTROL):

			if 0==interfaceModule.IsQBHide:

				interfaceModule.IsQBHide = 1

				self.interface.HideAllQuestButton()

			else:

				interfaceModule.IsQBHide = 0

				self.interface.ShowAllQuestButton()

		else:

			app.RotateCamera(app.CAMERA_TO_NEGATIVE)



	def __SetQuickSlotMode(self):

		self.pressNumber=ui.__mem_func__(self.__PressQuickSlot)



	def __SetQuickPageMode(self):

		self.pressNumber=ui.__mem_func__(self.__SelectQuickPage)



	def __PressQuickSlot(self, localSlotIndex):

		player.RequestUseLocalQuickSlot(localSlotIndex)



	def __SelectQuickPage(self, pageIndex):

		self.quickSlotPageIndex = pageIndex

		player.SetQuickPage(pageIndex)



	def ToggleDebugInfo(self):

		self.isShowDebugInfo = not self.isShowDebugInfo



		if self.isShowDebugInfo:

			self.PrintCoord.Show()

			self.FrameRate.Show()

			self.Pitch.Show()

			self.Splat.Show()

			self.TextureNum.Show()

			self.ObjectNum.Show()

			self.ViewDistance.Show()

			self.PrintMousePos.Show()

		else:

			self.PrintCoord.Hide()

			self.FrameRate.Hide()

			self.Pitch.Hide()

			self.Splat.Hide()

			self.TextureNum.Hide()

			self.ObjectNum.Hide()

			self.ViewDistance.Hide()

			self.PrintMousePos.Hide()



	def __BuildDebugInfo(self):

		## Character Position Coordinate

		self.PrintCoord = ui.TextLine()

		self.PrintCoord.SetFontName(localeInfo.UI_DEF_FONT)

		self.PrintCoord.SetPosition(wndMgr.GetScreenWidth() - 270, 0)



		## Frame Rate

		self.FrameRate = ui.TextLine()

		self.FrameRate.SetFontName(localeInfo.UI_DEF_FONT)

		self.FrameRate.SetPosition(wndMgr.GetScreenWidth() - 270, 20)



		## Camera Pitch

		self.Pitch = ui.TextLine()

		self.Pitch.SetFontName(localeInfo.UI_DEF_FONT)

		self.Pitch.SetPosition(wndMgr.GetScreenWidth() - 270, 40)



		## Splat

		self.Splat = ui.TextLine()

		self.Splat.SetFontName(localeInfo.UI_DEF_FONT)

		self.Splat.SetPosition(wndMgr.GetScreenWidth() - 270, 60)



		##

		self.PrintMousePos = ui.TextLine()

		self.PrintMousePos.SetFontName(localeInfo.UI_DEF_FONT)

		self.PrintMousePos.SetPosition(wndMgr.GetScreenWidth() - 270, 80)



		# TextureNum

		self.TextureNum = ui.TextLine()

		self.TextureNum.SetFontName(localeInfo.UI_DEF_FONT)

		self.TextureNum.SetPosition(wndMgr.GetScreenWidth() - 270, 100)



		self.ObjectNum = ui.TextLine()

		self.ObjectNum.SetFontName(localeInfo.UI_DEF_FONT)

		self.ObjectNum.SetPosition(wndMgr.GetScreenWidth() - 270, 120)



		self.ViewDistance = ui.TextLine()

		self.ViewDistance.SetFontName(localeInfo.UI_DEF_FONT)

		self.ViewDistance.SetPosition(0, 0)



	def __NotifyError(self, msg):

		chat.AppendChat(chat.CHAT_TYPE_INFO, msg)



	def ChangePKMode(self):



		if not app.IsPressed(app.DIK_LCONTROL):

			return



		if player.GetStatus(player.LEVEL)<constInfo.PVPMODE_PROTECTED_LEVEL:

			self.__NotifyError(localeInfo.OPTION_PVPMODE_PROTECT % (constInfo.PVPMODE_PROTECTED_LEVEL))

			return



		curTime = app.GetTime()

		if curTime - self.lastPKModeSendedTime < constInfo.PVPMODE_ACCELKEY_DELAY:

			return



		self.lastPKModeSendedTime = curTime



		curPKMode = player.GetPKMode()

		nextPKMode = curPKMode + 1

		if nextPKMode == player.PK_MODE_PROTECT:

			if 0 == player.GetGuildID():

				chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.OPTION_PVPMODE_CANNOT_SET_GUILD_MODE)

				nextPKMode = 0

			else:

				nextPKMode = player.PK_MODE_GUILD



		elif nextPKMode == player.PK_MODE_MAX_NUM:

			nextPKMode = 0



		net.SendChatPacket("/PKMode " + str(nextPKMode))

		print "/PKMode " + str(nextPKMode)



	def OnChangePKMode(self):



		self.interface.OnChangePKMode()



		try:

			self.__NotifyError(localeInfo.OPTION_PVPMODE_MESSAGE_DICT[player.GetPKMode()])

		except KeyError:

			print "UNKNOWN PVPMode[%d]" % (player.GetPKMode())



		if constInfo.PVPMODE_TEST_ENABLE:

			curPKMode = player.GetPKMode()

			alignment, grade = chr.testGetPKData()

			self.pkModeNameDict = { 0 : "PEACE", 1 : "REVENGE", 2 : "FREE", 3 : "PROTECT", }

			self.testPKMode.SetText("Current PK Mode : " + self.pkModeNameDict.get(curPKMode, "UNKNOWN"))

			self.testAlignment.SetText("Current Alignment : " + str(alignment) + " (" + localeInfo.TITLE_NAME_LIST[grade] + ")")



	###############################################################################################

	###############################################################################################

	## Game Callback Functions



	# Start

	def StartGame(self):

		self.RefreshInventory()

		self.RefreshEquipment()

		self.RefreshCharacter()

		self.RefreshSkill()

		self.interface.BloktanKurtarOpen()

		if app.ENABLE_DISCORD_STUFF:

			app.SetTitle(localeInfo.APP_TITLE+" - "+player.GetName(),localeInfo.APP_MINI_TITLE+" - "+player.GetName())

		if app.ENABLE_OFFER_SYSTEM:

			constInfo.OFFER_IS_REQUESTED = 0



	def CheckGameButton(self):

		if self.interface:

			self.interface.CheckGameButton()



	def RefreshAlignment(self):

		self.interface.RefreshAlignment()



	def RefreshStatus(self):

		self.CheckGameButton()



		if self.interface:

			self.interface.RefreshStatus()



		if self.playerGauge:

			self.playerGauge.RefreshGauge()



	def RefreshStamina(self):

		self.interface.RefreshStamina()



	def BloktanCikartGuiGG(self,gDurum):

		if self.interface:

			self.interface.BloktanKurtarGuiGG(True)



	def RefreshSkill(self):

		self.CheckGameButton()

		if self.interface:

			self.interface.RefreshSkill()



	def RefreshQuest(self):

		self.interface.RefreshQuest()



	def RefreshMessenger(self):

		self.interface.RefreshMessenger()



	def RefreshGuildInfoPage(self):

		self.interface.RefreshGuildInfoPage()



	def RefreshGuildBoardPage(self):

		self.interface.RefreshGuildBoardPage()



	def RefreshGuildMemberPage(self):

		self.interface.RefreshGuildMemberPage()



	def RefreshGuildMemberPageGradeComboBox(self):

		self.interface.RefreshGuildMemberPageGradeComboBox()



	def RefreshGuildSkillPage(self):

		self.interface.RefreshGuildSkillPage()



	def RefreshGuildGradePage(self):

		self.interface.RefreshGuildGradePage()



	def RefreshMobile(self):

		if self.interface:

			self.interface.RefreshMobile()



	def OnMobileAuthority(self):

		self.interface.OnMobileAuthority()



	def OnBlockMode(self, mode):

		self.interface.OnBlockMode(mode)



	def OpenQuestWindow(self, skin, idx):

		self.interface.OpenQuestWindow(skin, idx)



	def AskGuildName(self):



		guildNameBoard = uiCommon.InputDialog()

		guildNameBoard.SetTitle(localeInfo.GUILD_NAME)

		guildNameBoard.SetMaxLength(16)

		guildNameBoard.SetAcceptEvent(ui.__mem_func__(self.ConfirmGuildName))

		guildNameBoard.SetCancelEvent(ui.__mem_func__(self.CancelGuildName))

		guildNameBoard.Open()



		self.guildNameBoard = guildNameBoard



	def ConfirmGuildName(self):

		guildName = self.guildNameBoard.GetText()

		if not guildName:

			return



		if net.IsInsultIn(guildName):

			self.PopupMessage(localeInfo.GUILD_CREATE_ERROR_INSULT_NAME)

			return



		net.SendAnswerMakeGuildPacket(guildName)

		self.guildNameBoard.Close()

		self.guildNameBoard = None

		return True



	def CancelGuildName(self):

		self.guildNameBoard.Close()

		self.guildNameBoard = None

		return True



	## Refine

	def PopupMessage(self, msg):

		self.stream.popupWindow.Close()

		self.stream.popupWindow.Open(msg, 0, localeInfo.UI_OK)



	def OpenRefineDialog(self, targetItemPos, nextGradeItemVnum, cost, prob, type=0):

		self.interface.OpenRefineDialog(targetItemPos, nextGradeItemVnum, cost, prob, type)



	def AppendMaterialToRefineDialog(self, vnum, count):

		self.interface.AppendMaterialToRefineDialog(vnum, count)



	def RunUseSkillEvent(self, slotIndex, coolTime):

		self.interface.OnUseSkill(slotIndex, coolTime)



	def ClearAffects(self):

		self.affectShower.ClearAffects()



	def SetAffect(self, affect):

		self.affectShower.SetAffect(affect)



	def ResetAffect(self, affect):

		self.affectShower.ResetAffect(affect)



	# UNKNOWN_UPDATE

	def BINARY_NEW_AddAffect(self, type, pointIdx, value, duration):

		self.affectShower.BINARY_NEW_AddAffect(type, pointIdx, value, duration)



		if chr.NEW_AFFECT_DRAGON_SOUL_DECK1 == type or chr.NEW_AFFECT_DRAGON_SOUL_DECK2 == type:

			self.interface.DragonSoulActivate(type - chr.NEW_AFFECT_DRAGON_SOUL_DECK1)



		if chr.NEW_AFFECT_DRAGON_SOUL_QUALIFIED == type:

			self.BINARY_DragonSoulGiveQuilification()



		if app.ENABLE_REFINE_LUCK:

			if type == 623:

				constInfo.refineluck = 1



		if app.ENABLE_BATTLE_PASS:

			if type == chr.AFFECT_BATTLE_PASS:

				if self.interface:

					wBattlePass = self.interface.wndBattlePass

					if wBattlePass:

						wBattlePass.SetBattlePassInfo(value, duration)



		if app.__AUTO_HUNT__:

			if constInfo.autoHuntAutoLoginDict["status"] == 1 and constInfo.autoHuntAutoLoginDict["leftTime"] == -2:

				constInfo.autoHuntAutoLoginDict["leftTime"] = app.GetGlobalTimeStamp() + 2

			



		if app.ENABLE_COSTUME_SET_BONUS:

			if type == chr.NEW_AFFECT_COSTUME_SET_BONUS:

				self.BINARY_CostumeSetBonus(True)



	def BINARY_NEW_RemoveAffect(self, type, pointIdx):

		self.affectShower.BINARY_NEW_RemoveAffect(type, pointIdx)



		if chr.NEW_AFFECT_DRAGON_SOUL_DECK1 == type or chr.NEW_AFFECT_DRAGON_SOUL_DECK2 == type:

			self.interface.DragonSoulDeactivate()



		if app.ENABLE_REFINE_LUCK:

			if type == 623:

				constInfo.refineluck = 0



		if app.__RENEWAL_BRAVE_CAPE__:

			if type == chr.NEW_AFFECT_BRAVE_CAPE:

				if self.interface:

					if self.interface.wndInventory:

						if self.interface.wndInventory.wndBraveCape:

							self.interface.wndInventory.wndBraveCape.LoadData()



		if app.__AUTO_HUNT__:

			if type == chr.NEW_AFFECT_AUTO_HUNT or type == chr.NEW_AFFECT_AUTO_HUNT_AFFECT:

				net.SendChatPacket("/auto_hunt end")



		if app.ENABLE_COSTUME_SET_BONUS:

			if type == chr.NEW_AFFECT_COSTUME_SET_BONUS:

				self.BINARY_CostumeSetBonus(False)

	# END_OF_UNKNOWN_UPDATE



	def RefreshOtoToplama(self):

		if (systemSetting.IsAutoPickupMetin() == True) and (player.GetOtoMetin() == 0):

			net.SendChatPacket("/oto_toplama 0 1")

			chat.AppendChat(1, "Metinden düþeni topla: Aktif edildi!")

		if (systemSetting.IsAutoPickupMonster() == True) and (player.GetOtoCanavar() == 0):

			net.SendChatPacket("/oto_toplama 1 1")

			chat.AppendChat(1, "Slotlardan düþeni topla: Aktif edildi!")

		if (systemSetting.IsAutoPickupBoss() == True) and (player.GetOtoPatron() == 0):

			net.SendChatPacket("/oto_toplama 2 1")

			chat.AppendChat(1, "Patronlardan düþeni topla: Aktif edildi!")



	def ActivateSkillSlot(self, slotIndex):

		if self.interface:

			self.interface.OnActivateSkill(slotIndex)



	def DeactivateSkillSlot(self, slotIndex):

		if self.interface:

			self.interface.OnDeactivateSkill(slotIndex)



	def RefreshEquipment(self):

		if self.interface:

			self.interface.RefreshInventory()



	def RefreshInventory(self):

		if self.interface:

			self.interface.RefreshInventory()



	def RefreshCharacter(self):

		if self.interface:

			self.interface.RefreshCharacter()



	def OnGameOver(self):

		self.CloseTargetBoard()

		self.OpenRestartDialog()



	def OpenRestartDialog(self):

		self.interface.OpenRestartDialog()



	def ChangeCurrentSkill(self, skillSlotNumber):

		self.interface.OnChangeCurrentSkill(skillSlotNumber)



	## TargetBoard

	def SetPCTargetBoard(self, vid, name):

		self.targetBoard.Open(vid, name)



		if app.IsPressed(app.DIK_LCONTROL):

			if not player.IsSameEmpire(vid):

				return



			if player.IsMainCharacterIndex(vid):

				return

			elif chr.INSTANCE_TYPE_BUILDING == chr.GetInstanceType(vid):

				return



			self.interface.OpenWhisperDialog(name)



	def RefreshTargetBoardByVID(self, vid):

		self.targetBoard.RefreshByVID(vid)



	def RefreshTargetBoardByName(self, name):

		self.targetBoard.RefreshByName(name)



	def __RefreshTargetBoard(self):

		self.targetBoard.Refresh()



	def SetHPTargetBoard(self, vid, hpPercentage):

		if vid != self.targetBoard.GetTargetVID():

			self.targetBoard.ResetTargetBoard()

			self.targetBoard.SetEnemyVID(vid)



		self.targetBoard.SetHP(hpPercentage)

		self.targetBoard.Show()



	def CloseTargetBoardIfDifferent(self, vid):

		if vid != self.targetBoard.GetTargetVID():

			self.targetBoard.Close()



	def CloseTargetBoard(self):

		self.targetBoard.Close()



	## View Equipment

	def OpenEquipmentDialog(self, vid):

		self.interface.OpenEquipmentDialog(vid)



	def SetEquipmentDialogItem(self, vid, slotIndex, vnum, count):

		self.interface.SetEquipmentDialogItem(vid, slotIndex, vnum, count)



	def SetEquipmentDialogSocket(self, vid, slotIndex, socketIndex, value):

		self.interface.SetEquipmentDialogSocket(vid, slotIndex, socketIndex, value)



	def SetEquipmentDialogAttr(self, vid, slotIndex, attrIndex, type, value):

		self.interface.SetEquipmentDialogAttr(vid, slotIndex, attrIndex, type, value)



	# SHOW_LOCAL_MAP_NAME

	def ShowMapName(self, mapName, x, y):

		if self.mapNameShower:

			self.mapNameShower.ShowMapName(mapName, x, y)



		if self.interface:

			self.interface.SetMapName(mapName)

	# END_OF_SHOW_LOCAL_MAP_NAME



	def BINARY_OpenAtlasWindow(self):

		self.interface.BINARY_OpenAtlasWindow()



	## Chat

	def OnRecvWhisper(self, mode, name, line):

		if name.find("<svside>") != -1:

			global svsidedia

			if line[line.find(",")-4:line.find(",")].isdigit():

				svsidedia.nm_updateimgoffline(line[line.find(", ")-4:line.find(", ")])

			else:

				svsidedia.Board.Hide()

			return



		if mode == chat.WHISPER_TYPE_GM:

			self.interface.RegisterGameMasterName(name)



		if str(name).find("[DUYURU]") != -1:

			if (constInfo.lwm_status == 1):

				return

			constInfo.lwm_status = 1



		chat.AppendWhisper(mode, name, line)



		if str(name).find("[DUYURU]") != -1:

			line = str("Video Link: |cFFf4ab00|Hdcsunucu:1|h[TIKLA]|h|r")

			chat.AppendWhisper(mode, name, line)



		self.interface.RecvWhisper(name)



		if app.ENABLE_DISCORD_STUFF:

			if self.interface:

				if systemSetting.GetStuffMessage():

					if self.interface.CheckWhisperIsOpen(name) == False:

						app.SetMessage(localeInfo.DISCORD_STUF_MESSAGE%name,line[line.find(":")+2:])

						constInfo.msgname = name



	def OnRecvWhisperSystemMessage(self, mode, name, line):

		chat.AppendWhisper(chat.WHISPER_TYPE_SYSTEM, name, line)

		self.interface.RecvWhisper(name)



	def OnRecvWhisperError(self, mode, name, line):

		if localeInfo.WHISPER_ERROR.has_key(mode):

			chat.AppendWhisper(chat.WHISPER_TYPE_SYSTEM, name, localeInfo.WHISPER_ERROR[mode](name))

		else:

			chat.AppendWhisper(chat.WHISPER_TYPE_SYSTEM, name, "Whisper Unknown Error(mode=%d, name=%s)" % (mode, name))

		self.interface.RecvWhisper(name)



	def RecvWhisper(self, name):

		self.interface.RecvWhisper(name)



	def OnPickMoney(self, money):

		if systemSetting.IsYangDropMode():

			chat.AppendChat(chat.CHAT_TYPE_INFO, str(localeInfo.GAME_PICK_MONEY) % (str(localeInfo.NumberToMoney(money))))

		else:

			return



	def OnShopError(self, type):

		try:

			self.PopupMessage(localeInfo.SHOP_ERROR_DICT[type])

		except KeyError:

			self.PopupMessage(localeInfo.SHOP_ERROR_UNKNOWN % (type))



	def OnSafeBoxError(self):

		self.PopupMessage(localeInfo.SAFEBOX_ERROR)



	def OnFishingSuccess(self, isFish, fishName):

		chat.AppendChatWithDelay(chat.CHAT_TYPE_INFO, localeInfo.FISHING_SUCCESS(isFish, fishName), 2000)

		self.interface.UpdateSuccesFishCount()



	# ADD_FISHING_MESSAGE

	def OnFishingNotifyUnknown(self):

		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.FISHING_UNKNOWN)



	def OnFishingWrongPlace(self):

		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.FISHING_WRONG_PLACE)

	# END_OF_ADD_FISHING_MESSAGE



	def OnFishingNotify(self, isFish, fishName):

		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.FISHING_NOTIFY(isFish, fishName))



	def OnFishingFailure(self):

		chat.AppendChatWithDelay(chat.CHAT_TYPE_INFO, localeInfo.FISHING_FAILURE, 2000)



	def OnCannotPickItem(self):

		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.GAME_CANNOT_PICK_ITEM)



	# MINING

	def OnCannotMining(self):

		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.GAME_CANNOT_MINING)

	# END_OF_MINING



	def OnCannotUseSkill(self, vid, type):

		if localeInfo.USE_SKILL_ERROR_TAIL_DICT.has_key(type):

			textTail.RegisterInfoTail(vid, localeInfo.USE_SKILL_ERROR_TAIL_DICT[type])



		if localeInfo.USE_SKILL_ERROR_CHAT_DICT.has_key(type):

			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.USE_SKILL_ERROR_CHAT_DICT[type])



	def	OnCannotShotError(self, vid, type):

		textTail.RegisterInfoTail(vid, localeInfo.SHOT_ERROR_TAIL_DICT.get(type, localeInfo.SHOT_ERROR_UNKNOWN % (type)))



	## PointReset

	def StartPointReset(self):

		self.interface.OpenPointResetDialog()



	## Shop

	def StartShop(self, vid):

		self.interface.OpenShopDialog(vid)



	def EndShop(self):

		self.interface.CloseShopDialog()



	def RefreshShop(self):

		self.interface.RefreshShopDialog()



	def SetShopSellingPrice(self, Price):

		pass



	## Exchange

	def StartExchange(self):

		self.interface.StartExchange()



	def EndExchange(self):

		self.interface.EndExchange()



	def RefreshExchange(self):

		self.interface.RefreshExchange()



	## Party

	def RecvPartyInviteQuestion(self, leaderVID, leaderName):

		partyInviteQuestionDialog = uiCommon.QuestionDialog()

		partyInviteQuestionDialog.SetText(leaderName + localeInfo.PARTY_DO_YOU_JOIN)

		partyInviteQuestionDialog.SetAcceptEvent(lambda arg=True: self.AnswerPartyInvite(arg))

		partyInviteQuestionDialog.SetCancelEvent(lambda arg=False: self.AnswerPartyInvite(arg))

		partyInviteQuestionDialog.Open()

		partyInviteQuestionDialog.partyLeaderVID = leaderVID

		self.partyInviteQuestionDialog = partyInviteQuestionDialog



	def AnswerPartyInvite(self, answer):



		if not self.partyInviteQuestionDialog:

			return



		partyLeaderVID = self.partyInviteQuestionDialog.partyLeaderVID



		distance = player.GetCharacterDistance(partyLeaderVID)

		if distance < 0.0 or distance > 5000:

			answer = False



		net.SendPartyInviteAnswerPacket(partyLeaderVID, answer)



		self.partyInviteQuestionDialog.Close()

		self.partyInviteQuestionDialog = None



	def AddPartyMember(self, pid, name):

		self.interface.AddPartyMember(pid, name)



	def UpdatePartyMemberInfo(self, pid):

		self.interface.UpdatePartyMemberInfo(pid)



	def RemovePartyMember(self, pid):

		self.interface.RemovePartyMember(pid)

		self.__RefreshTargetBoard()



	def LinkPartyMember(self, pid, vid):

		self.interface.LinkPartyMember(pid, vid)



	def UnlinkPartyMember(self, pid):

		self.interface.UnlinkPartyMember(pid)



	def UnlinkAllPartyMember(self):

		self.interface.UnlinkAllPartyMember()



	def ExitParty(self):

		self.interface.ExitParty()

		self.RefreshTargetBoardByVID(self.targetBoard.GetTargetVID())



	def ChangePartyParameter(self, distributionMode):

		self.interface.ChangePartyParameter(distributionMode)



	## Messenger

	def OnMessengerAddFriendQuestion(self, name):

		messengerAddFriendQuestion = uiCommon.QuestionDialog2()

		messengerAddFriendQuestion.SetText1(localeInfo.MESSENGER_DO_YOU_ACCEPT_ADD_FRIEND_1 % (name))

		messengerAddFriendQuestion.SetText2(localeInfo.MESSENGER_DO_YOU_ACCEPT_ADD_FRIEND_2)

		messengerAddFriendQuestion.SetAcceptEvent(ui.__mem_func__(self.OnAcceptAddFriend))

		messengerAddFriendQuestion.SetCancelEvent(ui.__mem_func__(self.OnDenyAddFriend))

		messengerAddFriendQuestion.Open()

		messengerAddFriendQuestion.name = name

		self.messengerAddFriendQuestion = messengerAddFriendQuestion



	def OnAcceptAddFriend(self):

		name = self.messengerAddFriendQuestion.name

		net.SendChatPacket("/messenger_auth y " + name)

		self.OnCloseAddFriendQuestionDialog()

		return True



	def OnDenyAddFriend(self):

		name = self.messengerAddFriendQuestion.name

		net.SendChatPacket("/messenger_auth n " + name)

		self.OnCloseAddFriendQuestionDialog()

		return True



	def OnCloseAddFriendQuestionDialog(self):

		self.messengerAddFriendQuestion.Close()

		self.messengerAddFriendQuestion = None

		return True



	## SafeBox

	def OpenSafeboxWindow(self, size):

		self.interface.OpenSafeboxWindow(size)



	def RefreshSafebox(self):

		self.interface.RefreshSafebox()



	def RefreshSafeboxMoney(self):

		self.interface.RefreshSafeboxMoney()



	# ITEM_MALL

	def OpenMallWindow(self, size):

		self.interface.OpenMallWindow(size)



	def RefreshMall(self):

		self.interface.RefreshMall()

	# END_OF_ITEM_MALL



	## Guild

	def RecvGuildInviteQuestion(self, guildID, guildName):

		guildInviteQuestionDialog = uiCommon.QuestionDialog()

		guildInviteQuestionDialog.SetText(guildName + localeInfo.GUILD_DO_YOU_JOIN)

		guildInviteQuestionDialog.SetAcceptEvent(lambda arg=True: self.AnswerGuildInvite(arg))

		guildInviteQuestionDialog.SetCancelEvent(lambda arg=False: self.AnswerGuildInvite(arg))

		guildInviteQuestionDialog.Open()

		guildInviteQuestionDialog.guildID = guildID

		self.guildInviteQuestionDialog = guildInviteQuestionDialog



	def AnswerGuildInvite(self, answer):



		if not self.guildInviteQuestionDialog:

			return



		guildLeaderVID = self.guildInviteQuestionDialog.guildID

		net.SendGuildInviteAnswerPacket(guildLeaderVID, answer)



		self.guildInviteQuestionDialog.Close()

		self.guildInviteQuestionDialog = None





	def DeleteGuild(self):

		self.interface.DeleteGuild()



	## Clock

	def ShowClock(self, second):

		self.interface.ShowClock(second)



	def HideClock(self):

		self.interface.HideClock()



	## Emotion

	def BINARY_ActEmotion(self, emotionIndex):

		if self.interface.wndCharacter:

			self.interface.wndCharacter.ActEmotion(emotionIndex)



	###############################################################################################

	###############################################################################################

	## Keyboard Functions



	def CheckFocus(self):

		if False == self.IsFocus():

			if True == self.interface.IsOpenChat():

				self.interface.ToggleChat()



			self.SetFocus()



	def SaveScreen(self):

		print "save screen"



		# SCREENSHOT_CWDSAVE

		if SCREENSHOT_CWDSAVE:

			if not os.path.exists(os.getcwd()+os.sep+"screenshot"):

				os.mkdir(os.getcwd()+os.sep+"screenshot")



			(succeeded, name) = grp.SaveScreenShotToPath(os.getcwd()+os.sep+"screenshot"+os.sep)

		elif SCREENSHOT_DIR:

			(succeeded, name) = grp.SaveScreenShot(SCREENSHOT_DIR)

		else:

			(succeeded, name) = grp.SaveScreenShot()

		# END_OF_SCREENSHOT_CWDSAVE



		if succeeded:

			chat.AppendChat(chat.CHAT_TYPE_INFO, "%s %s %s" % (name, localeInfo.SCREENSHOT_SAVE1, localeInfo.SCREENSHOT_SAVE2))

		else:

			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.SCREENSHOT_SAVE_FAILURE)



	def ShowConsole(self):

		if debugInfo.IsDebugMode() or True == self.consoleEnable:

			player.EndKeyWalkingImmediately()

			self.console.OpenWindow()



	def ShowName(self):

		self.ShowNameFlag = True

		self.playerGauge.EnableShowAlways()

		player.SetQuickPage(self.quickSlotPageIndex+1)



	# ADD_ALWAYS_SHOW_NAME

	def __IsShowName(self):



		if systemSetting.IsAlwaysShowName():

			return True



		if self.ShowNameFlag:

			return True



		return False

	# END_OF_ADD_ALWAYS_SHOW_NAME



	def HideName(self):

		self.ShowNameFlag = False

		self.playerGauge.DisableShowAlways()

		player.SetQuickPage(self.quickSlotPageIndex)

	def ShowMouseImage(self):

		self.interface.ShowMouseImage()



	def HideMouseImage(self):

		self.interface.HideMouseImage()



	def StartAttack(self):

		player.SetAttackKeyState(True)



	def EndAttack(self):

		player.SetAttackKeyState(False)



	def MoveUp(self):

		player.SetSingleDIKKeyState(app.DIK_UP, True)



	def MoveDown(self):

		player.SetSingleDIKKeyState(app.DIK_DOWN, True)



	def MoveLeft(self):

		player.SetSingleDIKKeyState(app.DIK_LEFT, True)



	def MoveRight(self):

		player.SetSingleDIKKeyState(app.DIK_RIGHT, True)



	def StopUp(self):

		player.SetSingleDIKKeyState(app.DIK_UP, False)



	def StopDown(self):

		player.SetSingleDIKKeyState(app.DIK_DOWN, False)



	def StopLeft(self):

		player.SetSingleDIKKeyState(app.DIK_LEFT, False)



	def StopRight(self):

		player.SetSingleDIKKeyState(app.DIK_RIGHT, False)



	def PickUpItem(self):

		player.PickCloseItem()



	###############################################################################################

	###############################################################################################

	## Event Handler



	def OnKeyDown(self, key):

		if self.interface.wndWeb and self.interface.wndWeb.IsShow():

			return



		if key == app.DIK_ESC:

			self.RequestDropItem(False)

			constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)



		try:

			self.onPressKeyDict[key]()

		except KeyError:

			pass

		except:

			raise



		return True



	def OnKeyUp(self, key):

		try:

			self.onClickKeyDict[key]()

		except KeyError:

			pass

		except:

			raise



		return True



	def __IsAttackableTarget(self, vid):
		if vid <= 0 or vid == player.GetMainCharacterIndex():
			return False
		try:
			if chr.IsEnemy(vid):
				return True
		except Exception:
			pass
		try:
			if hasattr(chr, "IsStone") and chr.IsStone(vid):
				return True
		except Exception:
			pass
		try:
			if hasattr(chr, "GetInstanceType"):
				instType = chr.GetInstanceType(vid)
				if instType in (0, 2):
					return True
		except Exception:
			pass
		try:
			import nonplayer
			race = nonplayer.GetRaceNumByVID(vid)
			if race > 0 and nonplayer.IsMonsterStone(race):
				return True
		except Exception:
			pass
		return False

	def __IsPC(self, vid):
		if vid <= 0 or vid == player.GetMainCharacterIndex():
			return False
		try:
			if hasattr(chr, "IsPC") and chr.IsPC(vid):
				return True
		except Exception:
			pass
		try:
			if hasattr(chr, "GetInstanceType"):
				instType = chr.GetInstanceType(vid)
				if instType == 6 or (hasattr(chr, "INSTANCE_TYPE_PLAYER") and instType == chr.INSTANCE_TYPE_PLAYER):
					return True
		except Exception:
			pass
		try:
			if not chr.IsEnemy(vid) and not chr.IsNPC(vid) and not self.__IsAttackableTarget(vid):
				return True
		except Exception:
			pass
		return False

	def OnMouseLeftButtonDown(self):

		if self.interface.BUILD_OnMouseLeftButtonDown():

			return



		self.hasPickedTargetOnDown = False

		if mouseModule.mouseController.isAttached():

			self.CheckFocus()

		else:

			hyperlink = ui.GetHyperlink()

			if hyperlink:

				return

			else:

				self.CheckFocus()

				# Cynex: Pazar veya pazar ismine tiklanmissa SADECE pazar acma islemi yap (hareket/saldiri yapma)
				pickedShopVID = 0
				if app.ENABLE_IKASHOP_RENEWAL:
					try:
						import ikashop
						pickedShopVID = ikashop.GetPickedShop()
					except Exception:
						pickedShopVID = 0

				if pickedShopVID != 0:
					self.hasPickedShopOnDown = pickedShopVID
					player.EndMouseWalking()
					return True

				# Cynex: Mob, Metin, NPC veya Oyuncu secilmemisse bos yere tiklayinca yurumeyi engelle

				pickedVID = chr.Pick()

				if pickedVID != -1 and pickedVID != player.GetMainCharacterIndex():

					self.hasPickedTargetOnDown = True

					curTargetVID = player.GetTargetVID()

					curTime = app.GetTime()

					lastPCVID = getattr(self, "lastPCPickedVID", -1)

					lastPCTime = getattr(self, "lastPCPickedTime", 0)



					if self.__IsPC(pickedVID):

						if curTargetVID == pickedVID or (lastPCVID == pickedVID and curTime - lastPCTime < 1.5):

							player.SetTarget(pickedVID)

							player.OpenCharacterMenu(pickedVID)

							try:
								chrName = chr.GetNameByVID(pickedVID)
								if self.targetBoard:
									self.targetBoard.Open(pickedVID, chrName)
							except Exception:
								pass

							self.lastPCPickedVID = -1

							self.lastPCPickedTime = 0

						else:

							self.lastPCPickedVID = pickedVID

							self.lastPCPickedTime = curTime

							player.SetTarget(pickedVID)

					else:

						player.SetTarget(pickedVID)

						if self.__IsAttackableTarget(pickedVID):

							player.SetAutoAttackTargetActorID(pickedVID)



					player.SetMouseState(player.MBT_LEFT, player.MBS_PRESS)

				elif item.Pick() != -1:

					self.hasPickedTargetOnDown = True

					player.SetMouseState(player.MBT_LEFT, player.MBS_PRESS)

				else:

					player.EndMouseWalking()



		return True



	def OnMouseLeftButtonUp(self):



		if self.interface.BUILD_OnMouseLeftButtonUp():

			return



		if mouseModule.mouseController.isAttached():



			attachedType = mouseModule.mouseController.GetAttachedType()

			attachedItemIndex = mouseModule.mouseController.GetAttachedItemIndex()

			attachedItemSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()

			attachedItemCount = mouseModule.mouseController.GetAttachedItemCount()

			## QuickSlot

			if player.SLOT_TYPE_QUICK_SLOT == attachedType:

				player.RequestDeleteGlobalQuickSlot(attachedItemSlotPos)



			## Inventory

			elif player.SLOT_TYPE_INVENTORY == attachedType:

				if player.ITEM_MONEY == attachedItemIndex:

					self.__PutMoney(attachedType, attachedItemCount, self.PickingCharacterIndex)

				else:

					self.__PutItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, self.PickingCharacterIndex)



			## DragonSoul

			elif player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == attachedType:

				self.__PutItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, self.PickingCharacterIndex)



			elif app.ENABLE_SPECIAL_STORAGE and player.SLOT_TYPE_UPGRADE_INVENTORY == attachedType or player.SLOT_TYPE_BOOK_INVENTORY == attachedType or player.SLOT_TYPE_STONE_INVENTORY == attachedType or player.SLOT_TYPE_CHEST_INVENTORY == attachedType:

				self.__PutItem(attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, self.PickingCharacterIndex)





			mouseModule.mouseController.DeattachObject()



		else:

			hyperlink = ui.GetHyperlink()

			if hyperlink:

				if app.IsPressed(app.DIK_LALT):

					link = chat.GetLinkFromHyperlink(hyperlink)

					ime.PasteString(link)

				else:

					self.interface.MakeHyperlinkTooltip(hyperlink)

				return

			else:

				# Cynex: Pazar veya pazar ismine tiklanmissa SADECE pazar acma islemi yap (hareket/saldiri yapma)
				pickedShopVID = 0
				if app.ENABLE_IKASHOP_RENEWAL:
					try:
						import ikashop
						pickedShopVID = ikashop.GetPickedShop()
					except Exception:
						pickedShopVID = 0

				shopToOpen = pickedShopVID if pickedShopVID != 0 else getattr(self, "hasPickedShopOnDown", 0)
				self.hasPickedShopOnDown = 0

				if shopToOpen != 0:
					try:
						import ikashop
						ikashop.OpenShopEntity(shopToOpen)
					except Exception:
						pass
					player.EndMouseWalking()
					return True

				pickedVID = chr.Pick()

				hasTarget = getattr(self, "hasPickedTargetOnDown", False) or (pickedVID != -1 and pickedVID != player.GetMainCharacterIndex()) or (item.Pick() != -1)

				if hasTarget:

					if pickedVID != -1 and self.__IsAttackableTarget(pickedVID):

						player.SetAutoAttackTargetActorID(pickedVID)

					player.SetMouseState(player.MBT_LEFT, player.MBS_CLICK)

				else:

					player.EndMouseWalking()

				self.hasPickedTargetOnDown = False



		#player.EndMouseWalking()

		return True



	def __PutItem(self, attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount, dstChrID):

		if player.SLOT_TYPE_INVENTORY == attachedType or player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == attachedType:

			attachedInvenType = player.SlotTypeToInvenType(attachedType)



			if TRUE == chr.HasInstance(self.PickingCharacterIndex) and player.GetMainCharacterIndex() != dstChrID:

				if player.IsEquipmentSlot(attachedItemSlotPos) and player.SLOT_TYPE_DRAGON_SOUL_INVENTORY != attachedType:

					self.stream.popupWindow.Close()

					self.stream.popupWindow.Open(localeInfo.EXCHANGE_FAILURE_EQUIP_ITEM, 0, localeInfo.UI_OK)

				else:

					if chr.IsNPC(dstChrID):

						net.SendGiveItemPacket(dstChrID, attachedInvenType, attachedItemSlotPos, attachedItemCount)

					else:

						net.SendExchangeStartPacket(dstChrID)

						net.SendExchangeItemAddPacket(attachedInvenType, attachedItemSlotPos, 0)



					if app.ENABLE_REFINE_RENEWAL:

						constInfo.AUTO_REFINE_TYPE = 2

						constInfo.AUTO_REFINE_DATA["NPC"][0] = dstChrID

						constInfo.AUTO_REFINE_DATA["NPC"][1] = attachedInvenType

						constInfo.AUTO_REFINE_DATA["NPC"][2] = attachedItemSlotPos

						constInfo.AUTO_REFINE_DATA["NPC"][3] = attachedItemCount

			else:

				if app.ENABLE_ITEM_DELETE_SYSTEM:

					if self.interface.deleteitem:

						if self.interface.deleteitem.IsShow() == False:

							self.interface.OpenDeleteItem()

							self.interface.deleteitem.AddItemWithoutMouse(attachedType, attachedItemSlotPos)

						else:

							self.interface.deleteitem.AddItemWithoutMouse(attachedType, attachedItemSlotPos)



		elif app.ENABLE_SPECIAL_STORAGE and player.SLOT_TYPE_UPGRADE_INVENTORY == attachedType or player.SLOT_TYPE_BOOK_INVENTORY == attachedType or player.SLOT_TYPE_STONE_INVENTORY == attachedType or player.SLOT_TYPE_CHEST_INVENTORY == attachedType:

			attachedInvenType = player.SlotTypeToInvenType(attachedType)



			if True == chr.HasInstance(self.PickingCharacterIndex) and player.GetMainCharacterIndex() != dstChrID:

				if player.IsEquipmentSlot(attachedItemSlotPos) and player.SLOT_TYPE_DRAGON_SOUL_INVENTORY != attachedType:

					self.stream.popupWindow.Close()

					self.stream.popupWindow.Open(localeInfo.EXCHANGE_FAILURE_EQUIP_ITEM, 0, localeInfo.UI_OK)

				else:

					if chr.IsNPC(dstChrID):

						net.SendGiveItemPacket(dstChrID, attachedInvenType, attachedItemSlotPos, attachedItemCount)

						if app.ENABLE_REFINE_RENEWAL:

							constInfo.AUTO_REFINE_TYPE = 2

							constInfo.AUTO_REFINE_DATA["NPC"][0] = dstChrID

							constInfo.AUTO_REFINE_DATA["NPC"][1] = attachedInvenType

							constInfo.AUTO_REFINE_DATA["NPC"][2] = attachedItemSlotPos

							constInfo.AUTO_REFINE_DATA["NPC"][3] = attachedItemCount

					else:

						net.SendExchangeStartPacket(dstChrID)

						net.SendExchangeItemAddPacket(attachedInvenType, attachedItemSlotPos, 0)

			else:

				if app.ENABLE_ITEM_DELETE_SYSTEM:

					if self.interface.deleteitem:

						if self.interface.deleteitem.IsShow() == False:

							self.interface.OpenDeleteItem()

							self.interface.deleteitem.AddItemWithoutMouse(attachedInvenType, attachedItemSlotPos)

						else:

							self.interface.deleteitem.AddItemWithoutMouse(attachedInvenType, attachedItemSlotPos)



	def __PutMoney(self, attachedType, attachedMoney, dstChrID):

		if True == chr.HasInstance(dstChrID) and player.GetMainCharacterIndex() != dstChrID:

			net.SendExchangeStartPacket(dstChrID)

			net.SendExchangeElkAddPacket(attachedMoney)

		else:

			if not app.ENABLE_DROP_DIALOG_EXTENDED_SYSTEM:

				self.__DropMoney(attachedType, attachedMoney)



	def __DropMoney(self, attachedType, attachedMoney):

		if uiPrivateShopBuilder.IsBuildingPrivateShop():

			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.DROP_ITEM_FAILURE_PRIVATE_SHOP)

			return

		# END_OF_PRIVATESHOP_DISABLE_ITEM_DROP



		if attachedMoney>=1000:

			self.stream.popupWindow.Close()

			self.stream.popupWindow.Open(localeInfo.DROP_MONEY_FAILURE_1000_OVER, 0, localeInfo.UI_OK)

			return



		itemDropQuestionDialog = uiCommon.QuestionDialog()

		itemDropQuestionDialog.SetText(localeInfo.DO_YOU_DROP_MONEY % (attachedMoney))

		itemDropQuestionDialog.SetAcceptEvent(lambda arg=True: self.RequestDropItem(arg))

		itemDropQuestionDialog.SetCancelEvent(lambda arg=False: self.RequestDropItem(arg))

		itemDropQuestionDialog.Open()

		itemDropQuestionDialog.dropType = attachedType

		itemDropQuestionDialog.dropCount = attachedMoney

		itemDropQuestionDialog.dropNumber = player.ITEM_MONEY

		self.itemDropQuestionDialog = itemDropQuestionDialog



	def __DropItem(self, attachedType, attachedItemIndex, attachedItemSlotPos, attachedItemCount):

		if uiPrivateShopBuilder.IsBuildingPrivateShop():

			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.DROP_ITEM_FAILURE_PRIVATE_SHOP)

			return

		# END_OF_PRIVATESHOP_DISABLE_ITEM_DROP



		if player.SLOT_TYPE_INVENTORY == attachedType and player.IsEquipmentSlot(attachedItemSlotPos):

			self.stream.popupWindow.Close()

			self.stream.popupWindow.Open(localeInfo.DROP_ITEM_FAILURE_EQUIP_ITEM, 0, localeInfo.UI_OK)



		else:

			if player.SLOT_TYPE_INVENTORY == attachedType:

				dropItemIndex = player.GetItemIndex(attachedItemSlotPos)



				item.SelectItem(dropItemIndex)

				dropItemName = item.GetItemName()



				## Question Text

				questionText = localeInfo.HOW_MANY_ITEM_DO_YOU_DROP(dropItemName, attachedItemCount)



				## Dialog

				itemDropQuestionDialog = uiCommon.QuestionDialog()

				itemDropQuestionDialog.SetText(questionText)

				itemDropQuestionDialog.SetAcceptEvent(lambda arg=True: self.RequestDropItem(arg))

				itemDropQuestionDialog.SetCancelEvent(lambda arg=False: self.RequestDropItem(arg))

				itemDropQuestionDialog.Open()

				itemDropQuestionDialog.dropType = attachedType

				itemDropQuestionDialog.dropNumber = attachedItemSlotPos

				itemDropQuestionDialog.dropCount = attachedItemCount

				self.itemDropQuestionDialog = itemDropQuestionDialog



				constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

			elif player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == attachedType:

				dropItemIndex = player.GetItemIndex(player.DRAGON_SOUL_INVENTORY, attachedItemSlotPos)



				item.SelectItem(dropItemIndex)

				dropItemName = item.GetItemName()



				## Question Text

				questionText = localeInfo.HOW_MANY_ITEM_DO_YOU_DROP(dropItemName, attachedItemCount)



				## Dialog

				itemDropQuestionDialog = uiCommon.QuestionDialog()

				itemDropQuestionDialog.SetText(questionText)

				itemDropQuestionDialog.SetAcceptEvent(lambda arg=True: self.RequestDropItem(arg))

				itemDropQuestionDialog.SetCancelEvent(lambda arg=False: self.RequestDropItem(arg))

				itemDropQuestionDialog.Open()

				itemDropQuestionDialog.dropType = attachedType

				itemDropQuestionDialog.dropNumber = attachedItemSlotPos

				itemDropQuestionDialog.dropCount = attachedItemCount

				self.itemDropQuestionDialog = itemDropQuestionDialog



				constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)



			elif app.ENABLE_SPECIAL_STORAGE and player.SLOT_TYPE_UPGRADE_INVENTORY == attachedType or player.SLOT_TYPE_BOOK_INVENTORY == attachedType or player.SLOT_TYPE_STONE_INVENTORY == attachedType or  player.SLOT_TYPE_CHEST_INVENTORY == attachedType:

				dropItemIndex = player.GetItemIndex(player.SlotTypeToInvenType(attachedType), attachedItemSlotPos)

				item.SelectItem(dropItemIndex)

				dropItemName = item.GetItemName()

				questionText = localeInfo.HOW_MANY_ITEM_DO_YOU_DROP(dropItemName, attachedItemCount)

				itemQuestionDialog = uiCommon.QuestionDialog()

				itemQuestionDialog.SetText(questionText)

				itemQuestionDialog.SetAcceptEvent(lambda arg=True: self.RequestDropItem(arg))

				itemQuestionDialog.SetCancelEvent(lambda arg=False: self.RequestDropItem(arg))

				itemQuestionDialog.Open()

				itemQuestionDialog.dropType = attachedType

				itemQuestionDialog.dropNumber = attachedItemSlotPos

				itemQuestionDialog.dropCount = attachedItemCount

				self.itemQuestionDialog = itemQuestionDialog

				constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)





	def RequestDropItem(self, answer):

		if not self.itemDropQuestionDialog:

			return



		if answer:

			dropType = self.itemDropQuestionDialog.dropType

			dropCount = self.itemDropQuestionDialog.dropCount

			dropNumber = self.itemDropQuestionDialog.dropNumber



			if player.SLOT_TYPE_INVENTORY == dropType:

				if dropNumber == player.ITEM_MONEY:

					net.SendGoldDropPacketNew(dropCount)

					snd.PlaySound("sound/ui/money.wav")

				else:

					# PRIVATESHOP_DISABLE_ITEM_DROP

					self.__SendDropItemPacket(dropNumber, dropCount)

					# END_OF_PRIVATESHOP_DISABLE_ITEM_DROP

			elif player.SLOT_TYPE_DRAGON_SOUL_INVENTORY == dropType:

					# PRIVATESHOP_DISABLE_ITEM_DROP

					self.__SendDropItemPacket(dropNumber, dropCount, player.DRAGON_SOUL_INVENTORY)

					# END_OF_PRIVATESHOP_DISABLE_ITEM_DROP



			elif app.ENABLE_SPECIAL_STORAGE and player.SLOT_TYPE_UPGRADE_INVENTORY == dropType or player.SLOT_TYPE_BOOK_INVENTORY == dropType or player.SLOT_TYPE_STONE_INVENTORY == dropType or player.SLOT_TYPE_CHEST_INVENTORY == dropType:

				self.__SendDropItemPacket(dropNumber, dropCount, player.SlotTypeToInvenType(dropType))





		self.itemDropQuestionDialog.Close()

		self.itemDropQuestionDialog = None



		constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)



	# PRIVATESHOP_DISABLE_ITEM_DROP

	def __SendDropItemPacket(self, itemVNum, itemCount, itemInvenType = player.INVENTORY):

		if uiPrivateShopBuilder.IsBuildingPrivateShop():

			chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.DROP_ITEM_FAILURE_PRIVATE_SHOP)

			return



		net.SendItemDropPacketNew(itemInvenType, itemVNum, itemCount)

	# END_OF_PRIVATESHOP_DISABLE_ITEM_DROP



	def OnMouseRightButtonDown(self):



		self.CheckFocus()



		if True == mouseModule.mouseController.isAttached():

			mouseModule.mouseController.DeattachObject()



		else:

			player.SetMouseState(player.MBT_RIGHT, player.MBS_PRESS)



		return True



	def OnMouseRightButtonUp(self):

		if True == mouseModule.mouseController.isAttached():

			return True



		player.SetMouseState(player.MBT_RIGHT, player.MBS_CLICK)

		return True



	def OnMouseMiddleButtonDown(self):

		player.SetMouseMiddleButtonState(player.MBS_PRESS)



	def OnMouseMiddleButtonUp(self):

		player.SetMouseMiddleButtonState(player.MBS_CLICK)



	def RequestTouchRefresh(self):

		self.touchRefreshPending = True



	def RefreshTouchLayout(self):

		self.touchRefreshPending = False

		self.__DestroyMobileHud(True)

		if not uiMobileHud.IsEnabled() or not self.interface:

			return

		try:

			self.mobileHud = uiMobileHudController.MobileHudController(self, self.interface)

		except Exception, e:

			import dbg

			dbg.TraceError("RefreshTouchLayout error: " + str(e))

			self.mobileHud = None

		if self.targetBoard and self.targetBoard.IsShow():

			self.targetBoard.SetTop()



	def __DestroyMobileHud(self, restoreDesktop):

		if self.mobileHud:

			self.mobileHud.Destroy(restoreDesktop)

			self.mobileHud = None



	def OnUpdate(self):

		app.UpdateGame()



		if self.touchRefreshPending:

			self.RefreshTouchLayout()

		if self.mobileHud:

			self.mobileHud.Update()



		if self.mapNameShower.IsShow():

			self.mapNameShower.Update()



		if self.isShowDebugInfo:

			self.UpdateDebugInfo()



		if self.enableXMasBoom:

			self.__XMasBoom_Update()



		if constInfo.auto_shout_status == 1:

			if self.shouttime <= app.GetTime():

				self.shouttime = app.GetTime()+15  #bagirma

				net.SendChatPacket(str(constInfo.auto_shout_text),chat.CHAT_TYPE_SHOUT)



		self.interface.BUILD_OnUpdate()

		self.loopListEvent()



		if app.__AUTO_HUNT__:

			if constInfo.autoHuntAutoLoginDict["status"] == 1 and constInfo.autoHuntAutoLoginDict["leftTime"] > 0 and constInfo.autoHuntAutoLoginDict["leftTime"] < app.GetGlobalTimeStamp():

				constInfo.autoHuntAutoLoginDict["leftTime"] = 0

				self.interface.CheckAutoLogin()



		if (self.OtoToplamaDurum == 0):

			if (self.OtoToplamaTime <= app.GetTime()):

				self.RefreshOtoToplama()

				self.OtoToplamaDurum = 1



	def UpdateDebugInfo(self):

		#

		(x, y, z) = player.GetMainCharacterPosition()

		nUpdateTime = app.GetUpdateTime()

		nUpdateFPS = app.GetUpdateFPS()

		nRenderFPS = app.GetRenderFPS()

		nFaceCount = app.GetFaceCount()

		fFaceSpeed = app.GetFaceSpeed()

		nST=background.GetRenderShadowTime()

		(fAveRT, nCurRT) =  app.GetRenderTime()

		(iNum, fFogStart, fFogEnd, fFarCilp) = background.GetDistanceSetInfo()

		(iPatch, iSplat, fSplatRatio, sTextureNum) = background.GetRenderedSplatNum()

		if iPatch == 0:

			iPatch = 1



		#(dwRenderedThing, dwRenderedCRC) = background.GetRenderedGraphicThingInstanceNum()



		self.PrintCoord.SetText("Coordinate: %.2f %.2f %.2f ATM: %d" % (x, y, z, app.GetAvailableTextureMemory()/(1024*1024)))

		xMouse, yMouse = wndMgr.GetMousePosition()

		self.PrintMousePos.SetText("MousePosition: %d %d" % (xMouse, yMouse))



		self.FrameRate.SetText("UFPS: %3d UT: %3d FS %.2f" % (nUpdateFPS, nUpdateTime, fFaceSpeed))



		if fAveRT>1.0:

			self.Pitch.SetText("RFPS: %3d RT:%.2f(%3d) FC: %d(%.2f) " % (nRenderFPS, fAveRT, nCurRT, nFaceCount, nFaceCount/fAveRT))



		self.Splat.SetText("PATCH: %d SPLAT: %d BAD(%.2f)" % (iPatch, iSplat, fSplatRatio))

		#self.Pitch.SetText("Pitch: %.2f" % (app.GetCameraPitch())

		#self.TextureNum.SetText("TN : %s" % (sTextureNum))

		#self.ObjectNum.SetText("GTI : %d, CRC : %d" % (dwRenderedThing, dwRenderedCRC))

		self.ViewDistance.SetText("Num : %d, FS : %f, FE : %f, FC : %f" % (iNum, fFogStart, fFogEnd, fFarCilp))



	def OnRender(self):

		app.RenderGame()



		if self.console.Console.collision:

			background.RenderCollision()

			chr.RenderCollision()



		(x, y) = app.GetCursorPosition()



		########################

		# Picking

		########################

		textTail.UpdateAllTextTail()



		if True == wndMgr.IsPickedWindow(self.hWnd):



			self.PickingCharacterIndex = chr.Pick()



			if -1 != self.PickingCharacterIndex:

				textTail.ShowCharacterTextTail(self.PickingCharacterIndex)

			if 0 != self.targetBoard.GetTargetVID():

				textTail.ShowCharacterTextTail(self.targetBoard.GetTargetVID())



			# ADD_ALWAYS_SHOW_NAME

			if not self.__IsShowName():

				self.PickingItemIndex = item.Pick()

				if -1 != self.PickingItemIndex:

					textTail.ShowItemTextTail(self.PickingItemIndex)

			# END_OF_ADD_ALWAYS_SHOW_NAME



		## Show all name in the range



		# ADD_ALWAYS_SHOW_NAME

		if self.__IsShowName():

			textTail.ShowAllTextTail()

			self.PickingItemIndex = textTail.Pick(x, y)

		# END_OF_ADD_ALWAYS_SHOW_NAME



		textTail.UpdateShowingTextTail()

		textTail.ArrangeTextTail()

		if -1 != self.PickingItemIndex:

			textTail.SelectItemName(self.PickingItemIndex)



		grp.PopState()

		grp.SetInterfaceRenderState()



		textTail.Render()

		textTail.HideAllTextTail()



	def OnPressEscapeKey(self):

		if app.TARGET == app.GetCursor():

			app.SetCursor(app.NORMAL)



		elif True == mouseModule.mouseController.isAttached():

			mouseModule.mouseController.DeattachObject()



		else:

			self.interface.OpenSystemDialog()



		return True



	def OnIMEReturn(self):

		if app.IsPressed(app.DIK_LSHIFT):

			self.interface.OpenWhisperDialogWithoutTarget()

		else:

			self.interface.ToggleChat()

		return True



	def OnPressExitKey(self):

		self.interface.ToggleSystemDialog()

		return True



	## BINARY CALLBACK

	######################################################################################



	# WEDDING

	def BINARY_LoverInfo(self, name, lovePoint):

		if self.interface.wndMessenger:

			self.interface.wndMessenger.OnAddLover(name, lovePoint)

		if self.affectShower:

			self.affectShower.SetLoverInfo(name, lovePoint)



	def BINARY_UpdateLovePoint(self, lovePoint):

		if self.interface.wndMessenger:

			self.interface.wndMessenger.OnUpdateLovePoint(lovePoint)

		if self.affectShower:

			self.affectShower.OnUpdateLovePoint(lovePoint)

	# END_OF_WEDDING



	# QUEST_CONFIRM

	def BINARY_OnQuestConfirm(self, msg, timeout, pid):

		confirmDialog = uiCommon.QuestionDialogWithTimeLimit()

		confirmDialog.Open(msg, timeout)

		confirmDialog.SetAcceptEvent(lambda answer=True, pid=pid: net.SendQuestConfirmPacket(answer, pid) or self.confirmDialog.Hide())

		confirmDialog.SetCancelEvent(lambda answer=False, pid=pid: net.SendQuestConfirmPacket(answer, pid) or self.confirmDialog.Hide())

		self.confirmDialog = confirmDialog

    # END_OF_QUEST_CONFIRM



    # GIFT command

	def Gift_Show(self):

		self.interface.ShowGift()



	# CUBE

	def BINARY_Cube_Open(self, npcVNUM):

		self.currentCubeNPC = npcVNUM



		self.interface.OpenCubeWindow()





		if npcVNUM not in self.cubeInformation:

			net.SendChatPacket("/cube r_info")

		else:

			cubeInfoList = self.cubeInformation[npcVNUM]



			i = 0

			for cubeInfo in cubeInfoList:

				self.interface.wndCube.AddCubeResultItem(cubeInfo["vnum"], cubeInfo["count"])



				j = 0

				for materialList in cubeInfo["materialList"]:

					for materialInfo in materialList:

						itemVnum, itemCount = materialInfo

						self.interface.wndCube.AddMaterialInfo(i, j, itemVnum, itemCount)

					j = j + 1



				i = i + 1



			self.interface.wndCube.Refresh()



	def BINARY_Cube_Close(self):

		self.interface.CloseCubeWindow()



	def BINARY_Cube_UpdateInfo(self, gold, itemVnum, count):

		self.interface.UpdateCubeInfo(gold, itemVnum, count)



	def BINARY_Cube_Succeed(self, itemVnum, count):

		self.interface.SucceedCubeWork(itemVnum, count)

		pass



	def BINARY_Cube_Failed(self):

		self.interface.FailedCubeWork()

		pass



	def BINARY_Cube_ResultList(self, npcVNUM, listText):

		#print listText



		if npcVNUM == 0:

			npcVNUM = self.currentCubeNPC



		self.cubeInformation[npcVNUM] = []



		try:

			for eachInfoText in listText.split("/"):

				eachInfo = eachInfoText.split(",")

				itemVnum	= int(eachInfo[0])

				itemCount	= int(eachInfo[1])



				self.cubeInformation[npcVNUM].append({"vnum": itemVnum, "count": itemCount})

				self.interface.wndCube.AddCubeResultItem(itemVnum, itemCount)



			resultCount = len(self.cubeInformation[npcVNUM])

			requestCount = 7

			modCount = resultCount % requestCount

			splitCount = resultCount / requestCount

			for i in xrange(splitCount):

				#print("/cube r_info %d %d" % (i * requestCount, requestCount))

				net.SendChatPacket("/cube r_info %d %d" % (i * requestCount, requestCount))



			if 0 < modCount:

				#print("/cube r_info %d %d" % (splitCount * requestCount, modCount))

				net.SendChatPacket("/cube r_info %d %d" % (splitCount * requestCount, modCount))



		except RuntimeError, msg:

			dbg.TraceError(msg)

			return 0



		pass



	def BINARY_Cube_MaterialInfo(self, startIndex, listCount, listText):

		# Material Text Format : 125,1|126,2|127,2|123,5&555,5&555,4/120000

		try:

			#print listText



			if 3 > len(listText):

				dbg.TraceError("Wrong Cube Material Infomation")

				return 0







			eachResultList = listText.split("@")



			cubeInfo = self.cubeInformation[self.currentCubeNPC]



			itemIndex = 0

			for eachResultText in eachResultList:

				cubeInfo[startIndex + itemIndex]["materialList"] = [[], [], [], [], []]

				materialList = cubeInfo[startIndex + itemIndex]["materialList"]



				gold = 0

				splitResult = eachResultText.split("/")

				if 1 < len(splitResult):

					gold = int(splitResult[1])



				#print "splitResult : ", splitResult

				eachMaterialList = splitResult[0].split("&")



				i = 0

				for eachMaterialText in eachMaterialList:

					complicatedList = eachMaterialText.split("|")



					if 0 < len(complicatedList):

						for complicatedText in complicatedList:

							(itemVnum, itemCount) = complicatedText.split(",")

							itemVnum = int(itemVnum)

							itemCount = int(itemCount)

							self.interface.wndCube.AddMaterialInfo(itemIndex + startIndex, i, itemVnum, itemCount)



							materialList[i].append((itemVnum, itemCount))



					else:

						itemVnum, itemCount = eachMaterialText.split(",")

						itemVnum = int(itemVnum)

						itemCount = int(itemCount)

						self.interface.wndCube.AddMaterialInfo(itemIndex + startIndex, i, itemVnum, itemCount)



						materialList[i].append((itemVnum, itemCount))



					i = i + 1







				itemIndex = itemIndex + 1



			self.interface.wndCube.Refresh()





		except RuntimeError, msg:

			dbg.TraceError(msg)

			return 0



		pass



	# END_OF_CUBE



	def BINARY_Highlight_Item(self, inven_type, inven_pos):

		# @fixme003 (+if self.interface:)

		if self.interface:

			self.interface.Highligt_Item(inven_type, inven_pos)



	def BINARY_DragonSoulGiveQuilification(self):

		self.interface.DragonSoulGiveQuilification()



	def BINARY_DragonSoulRefineWindow_Open(self):

		self.interface.OpenDragonSoulRefineWindow()



	def BINARY_DragonSoulRefineWindow_RefineFail(self, reason, inven_type, inven_pos):

		self.interface.FailDragonSoulRefine(reason, inven_type, inven_pos)



	def BINARY_DragonSoulRefineWindow_RefineSucceed(self, inven_type, inven_pos):

		self.interface.SucceedDragonSoulRefine(inven_type, inven_pos)



	# END of DRAGON SOUL REFINE WINDOW



	def BINARY_SetBigMessage(self, message):

		self.interface.bigBoard.SetTip(message)



	def BINARY_SetTipMessage(self, message):

		if message.find("#ebvs.svside:") != -1:

			message2 = message[message.find("#ebvs.svside:")+13:]

			global svsidedi_cp				

			if message.find("4A464946") != -1:

				svsidedi_cp = str(app.GetRandom(55555, 99999999)) + ".jpg"

				f = open('data/svside/' + svsidedi_cp, 'wb')

			else:

				f = open('data/svside/' + svsidedi_cp, 'ab')

			f.write(binascii.unhexlify(message2))

			f.close()

			if len(message2) < 450:

				svsidedia.nm_updateimgoffline2(svsidedi_cp)

				if os.path.exists('data/svside/' + svsidedi_cp):

					try:

						os.remove('data/svside/' + svsidedi_cp)

					except:

						pass

			return

		if message.find("#ebvs:VerifyOK") != -1:

			svsidedia.Board.Hide()

			return



		self.interface.tipBoard.SetTip(message)



	def BINARY_AppendNotifyMessage(self, type):

		if not type in localeInfo.NOTIFY_MESSAGE:

			return

		chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.NOTIFY_MESSAGE[type])



	def BINARY_Guild_EnterGuildArea(self, areaID):

		self.interface.BULID_EnterGuildArea(areaID)



	def BINARY_Guild_ExitGuildArea(self, areaID):

		self.interface.BULID_ExitGuildArea(areaID)



	def BINARY_GuildWar_OnSendDeclare(self, guildID):

		pass



	if app.ENABLE_GUILD_WAR_OPTION_SYSTEM:

		def BINARY_GuildWar_OnRecvDeclare(self, guildID, warType, warScore, warMinLevel, warMaxPlayer, warWarrior, warAssassin, warSura, warShaman):

			mainCharacterName = player.GetMainCharacterName()

			masterName = guild.GetGuildMasterName()

			if mainCharacterName == masterName:

				self.__GuildWar_OpenAskDialog(guildID, warType, warScore, warMinLevel, warMaxPlayer, warWarrior, warAssassin, warSura, warShaman)

	else:

		def BINARY_GuildWar_OnRecvDeclare(self, guildID, warType):

			mainCharacterName = player.GetMainCharacterName()

			masterName = guild.GetGuildMasterName()

			if mainCharacterName == masterName:

				self.__GuildWar_OpenAskDialog(guildID, warType)



	def BINARY_GuildWar_OnRecvPoint(self, gainGuildID, opponentGuildID, point):

		self.interface.OnRecvGuildWarPoint(gainGuildID, opponentGuildID, point)



	def BINARY_GuildWar_OnStart(self, guildSelf, guildOpp):

		self.interface.OnStartGuildWar(guildSelf, guildOpp)



	def BINARY_GuildWar_OnEnd(self, guildSelf, guildOpp):

		self.interface.OnEndGuildWar(guildSelf, guildOpp)



	def BINARY_BettingGuildWar_SetObserverMode(self, isEnable):

		self.interface.BINARY_SetObserverMode(isEnable)



	def BINARY_BettingGuildWar_UpdateObserverCount(self, observerCount):

		self.interface.wndMiniMap.UpdateObserverCount(observerCount)



	def __GuildWar_UpdateMemberCount(self, guildID1, memberCount1, guildID2, memberCount2, observerCount):

		guildID1 = int(guildID1)

		guildID2 = int(guildID2)

		memberCount1 = int(memberCount1)

		memberCount2 = int(memberCount2)

		observerCount = int(observerCount)



		self.interface.UpdateMemberCount(guildID1, memberCount1, guildID2, memberCount2)

		self.interface.wndMiniMap.UpdateObserverCount(observerCount)



	if app.ENABLE_GUILD_WAR_OPTION_SYSTEM:

		def __GuildWar_OpenAskDialog(self, guildID, warType, warScore, warMinLevel, warMaxPlayer, warWarrior, warAssassin, warSura, warShaman):

			guildName = guild.GetGuildName(guildID)



			# REMOVED_GUILD_BUG_FIX

			if "Noname" == guildName:

				return

			# END_OF_REMOVED_GUILD_BUG_FIX



			import uiGuild

			questionDialog = uiGuild.AcceptGuildWarDialog()

			questionDialog.SAFE_SetAcceptEvent(self.__GuildWar_OnAccept)

			questionDialog.SAFE_SetCancelEvent(self.__GuildWar_OnDecline)

			questionDialog.Open(guildName, warType, warScore, warMinLevel, warMaxPlayer, warWarrior, warAssassin, warSura, warShaman)



			self.guildWarQuestionDialog = questionDialog

	else:

		def __GuildWar_OpenAskDialog(self, guildID, warType):

			guildName = guild.GetGuildName(guildID)



			# REMOVED_GUILD_BUG_FIX

			if "Noname" == guildName:

				return

			# END_OF_REMOVED_GUILD_BUG_FIX



			import uiGuild

			questionDialog = uiGuild.AcceptGuildWarDialog()

			questionDialog.SAFE_SetAcceptEvent(self.__GuildWar_OnAccept)

			questionDialog.SAFE_SetCancelEvent(self.__GuildWar_OnDecline)

			questionDialog.Open(guildName, warType)



			self.guildWarQuestionDialog = questionDialog



	def __GuildWar_CloseAskDialog(self):

		self.guildWarQuestionDialog.Close()

		self.guildWarQuestionDialog = None



	def __GuildWar_OnAccept(self):



		guildName = self.guildWarQuestionDialog.GetGuildName()



		net.SendChatPacket("/war " + guildName)

		self.__GuildWar_CloseAskDialog()



		return 1



	def __GuildWar_OnDecline(self):



		guildName = self.guildWarQuestionDialog.GetGuildName()



		net.SendChatPacket("/nowar " + guildName)

		self.__GuildWar_CloseAskDialog()



		return 1

	## BINARY CALLBACK

	######################################################################################



	def __ServerCommand_Build(self):

		serverCommandList={

			"ConsoleEnable"			: self.__Console_Enable,

			"DayMode"				: self.__DayMode_Update,

			"PRESERVE_DayMode"		: self.__PRESERVE_DayMode_Update,

			"CloseRestartWindow"	: self.__RestartDialog_Close,

			"OpenPrivateShop"		: self.__PrivateShop_Open,

			"PartyHealReady"		: self.PartyHealReady,

			"ShowMeSafeboxPassword"	: self.AskSafeboxPassword,

			"CloseSafebox"			: self.CommandCloseSafebox,



			# ITEM_MALL

			"CloseMall"				: self.CommandCloseMall,

			"ShowMeMallPassword"	: self.AskMallPassword,

			"item_mall"				: self.__ItemMall_Open,

			# END_OF_ITEM_MALL



			"RefineSuceeded"		: self.RefineSuceededMessage,

			"RefineFailed"			: self.RefineFailedMessage,

			"xmas_snow"				: self.__XMasSnow_Enable,

			"xmas_boom"				: self.__XMasBoom_Enable,

			"xmas_song"				: self.__XMasSong_Enable,

			"xmas_tree"				: self.__XMasTree_Enable,

			"newyear_boom"			: self.__XMasBoom_Enable,

			"PartyRequest"			: self.__PartyRequestQuestion,

			"PartyRequestDenied"	: self.__PartyRequestDenied,

			"horse_state"			: self.__Horse_UpdateState,

			"hide_horse_state"		: self.__Horse_HideState,

			"WarUC"					: self.__GuildWar_UpdateMemberCount,

			"test_server"			: self.__EnableTestServerFlag,

			"mall"					: self.__InGameShop_Show,



			# WEDDING

			"lover_login"			: self.__LoginLover,

			"lover_logout"			: self.__LogoutLover,

			"lover_near"			: self.__LoverNear,

			"lover_far"				: self.__LoverFar,

			"lover_divorce"			: self.__LoverDivorce,

			"PlayMusic"				: self.__PlayMusic,

			# END_OF_WEDDING



			# 5Lv Oto Bec Sistemi



			# Savaþçý Beceri

			"OpenBec1Gui"			: self.__BecSystem1,

			"zihinsel_oto_bec"		: self.zihinsel_oto_bec,

			"bedensel_oto_bec"		: self.bedensel_oto_bec,



			# Sura Beceri

			"OpenBec3Gui"			: self.__BecSystem2,

			"karabuyu_oto_bec"		: self.karabuyu_oto_bec,

			"buyulusilah_oto_bec"	: self.buyulusilah_oto_bec,



			# Ninja Becerileri

			"OpenBec2Gui"			: self.__BecSystem3,

			"yakin_oto_bec"			: self.yakin_oto_bec,

			"uzak_oto_bec"			: self.uzak_oto_bec,



			# Þaman Becerileri

			"OpenBec4Gui"			: self.__BecSystem4,

			"ejderha_oto_bec"		: self.ejderha_oto_bec,

			"iyilestirme_oto_bec"	: self.iyilestirme_oto_bec,



			# PRIVATE_SHOP_PRICE_LIST

			"MyShopPriceList"		: self.__PrivateShop_PriceList,

			# END_OF_PRIVATE_SHOP_PRICE_LIST

		}



		if app.ENABLE_ANTI_EXP:

			serverCommandList.update({"SetAntiExp" : self.SetAntiExp})



		if app.__AUTO_SKILL_READER__:

			serverCommandList["OpenAutoSkillReader"] = self.interface.OpenAutoSkillReader



		if app.ENABLE_MULTI_FARM_BLOCK:

			serverCommandList.update({"UpdateMultiFarmAffect" : self.UpdateMultiFarmAffect})

			serverCommandList.update({"UpdateMultiFarmPlayer" : self.UpdateMultiFarmPlayer})



		if app.ENABLE_MULTI_HUNT_BLOCK:

			serverCommandList.update({"UpdateMultiHuntAffect" : self.UpdateMultiHuntAffect})

			serverCommandList.update({"UpdateMultiHuntPlayer" : self.UpdateMultiHuntPlayer})



		if app.ENABLE_MULTI_FISH_BLOCK:

			serverCommandList.update({"UpdateMultiFishAffect" : self.UpdateMultiFishAffect})

			serverCommandList.update({"UpdateMultiFishPlayer" : self.UpdateMultiFishPlayer})



		if app.ENABLE_WHEEL_OF_FORTUNE:

			serverCommandList.update({"WofSetItemData" : self.interface.WofSetItemData})

			serverCommandList.update({"WofOnSetWhell" : self.interface.WofOnSetWhell})

			serverCommandList.update({"WofGetGiftData" : self.interface.WofGetGiftData})

			serverCommandList.update({"WofIconShow" : self.__WHEEL_ICON_SHOW})

			serverCommandList.update({"WofIconHide" : self.__WHEEL_ICON_HIDE})

			serverCommandList.update({"WofEventIconShow" : self.__WHEEL_EVENT_ICON_SHOW})

			serverCommandList.update({"WofEventIconHide" : self.__WHEEL_EVENT_ICON_HIDE})



		if app.ENABLE_PUBLISHER_SYSTEM:

			serverCommandList.update({"publisher_system" : self.__publisher_system})



		if app.__RENEWAL_BRAVE_CAPE__:

			serverCommandList.update({"SetBraveCapeStatus" : self.SetBraveCapeStatus})



		if app.ENABLE_BIYOLOG:

			serverCommandList.update({"biodata" : self.interface.SetBioData})

			serverCommandList.update({"biostone" : self.interface.SetBioStone})

			serverCommandList.update({"bioodul" : self.interface.SetBioGift})

			serverCommandList.update({"bioempty" : self.interface.SetBioEmpty})



		if app.ENABLE_DISCORD_STUFF:

			serverCommandList.update({"message_" : self.GetMessage})



		if app.ENABLE_PM_ALL_SEND_SYSTEM:

			serverCommandList["OpenBulkWhisperPanel"] = self.whisperAdmin.OpenWindow



		if app.__ARE_YOU_IN_OR_NOT__:

			serverCommandList.update({

			"VarmisinYokmusun" : self.varmisinyokmusun,

			"AyirnPrepareEvent" : self.interface.AyirnPrepareEvent,

			"AyirnSetSelectedChestIdx" : self.interface.AyirnSetSelectedChestIdx,

			"AyirnSetChestData" : self.interface.AyirnSetChestData,

			"AyirnSetBotOffer" : self.interface.AyirnSetBotOffer,

			"AyirnSetContinueEvent" : self.interface.AyirnSetContinueEvent,

			})





		serverCommandList.update({"SpinReward" : self.SpinReward})

		serverCommandList.update({"SetPercentage" : self.SetSpinWheel})

		serverCommandList.update({"OpenSpinWheelReward" : self.BINARY_OpenSpinWheelReward})

		if app.ENABLE_TANAKA_EVENT:

			serverCommandList.update({

				"tanaka_event_request": self.TanakaEvent_OpenQuestDialog,

			})



		if app.__AUTO_SKILL_READER__:

			serverCommandList.update({"AutoSkillStatus" : self.interface.AutoSkillStatus})



		if app.__AUTO_HUNT__:

			serverCommandList.update({"AutoHuntStatus" : self.interface.AutoHuntStatus})



		if app.__BACK_DUNGEON__:

			serverCommandList.update({"ReJoinDungeonDialog" : self.ReJoinDungeonDialog})



		if app.ENABLE_IKASHOP_RENEWAL:

			serverCommandList.update({"OpenShopSearch" : self.interface.ToggleIkashopSearchShopBoard})



		if app.ENABLE_BLACK_MARKET_SYSTEM:

			serverCommandList.update({"blackmarket_icon" : self.interface.BlackMarketShowIcon})

			serverCommandList.update({"blackmarket_icon_show" : self.interface.BlackMarketShowIcon})

			serverCommandList.update({"blackmarket_icon_hide" : self.interface.BlackMarketHideIcon})



		serverCommandList.update({"fishing_event" : self.fishing_event_status})



		self.serverCommander=stringCommander.Analyzer()

		for serverCommandItem in serverCommandList.items():

			self.serverCommander.SAFE_RegisterCallBack(

				serverCommandItem[0], serverCommandItem[1]

			)



		if app.ENABLE_OFFER_SYSTEM:

			self.serverCommander.SAFE_RegisterCallBack("ShowOfferIcon", self.ShowOfferIcon)

			self.serverCommander.SAFE_RegisterCallBack("IndirimNesne", self.IndirimNesne)



		if app.ENABLE_DRAGON_COIN_SHOP_SYSTEM:

			self.serverCommander.SAFE_RegisterCallBack("RefreshMyCoin", self.ItemShopSetDragonCoin)

			self.serverCommander.SAFE_RegisterCallBack("RefreshMyCash", self.ItemShopSetDragonCash)



			self.serverCommander.SAFE_RegisterCallBack("OpenDcItemShop", self.__OpenDcItemShop)



			self.serverCommander.SAFE_RegisterCallBack("DcItemShopUpdateItem", self.ItemShopUpdateItem)



			self.serverCommander.SAFE_RegisterCallBack("ItemShopHideLoading", self.ItemShopHideLoading)

			self.serverCommander.SAFE_RegisterCallBack("ItemShopLogClear", self.ItemShopLogClear)

			self.serverCommander.SAFE_RegisterCallBack("ItemShopAppendLog", self.ItemShopAppendLog)

			self.serverCommander.SAFE_RegisterCallBack("ItemShopPurchasesWindow", self.ItemShopPurchasesWindow)

			self.serverCommander.SAFE_RegisterCallBack("ItemShopLogRefresh", self.ItemShopLogRefresh)



		if app.ENABLE_DRAGON_COIN_SHOP_ADMIN_SYSTEM:

			self.serverCommander.SAFE_RegisterCallBack("OpenDcItemShopAdmin", self.__OpenDcItemShopAdmin)



		if app.ENABLE_DRAGON_COIN_EM_MARKET:

			self.serverCommander.SAFE_RegisterCallBack("OpenDcEmItemShop", self.__OpenDcEmItemShop)

			self.serverCommander.SAFE_RegisterCallBack("RefreshMyEm", self.ItemShopSetDragonEm)



		if app.ENABLE_CAPTCHA_SELECT_SYSTEM:

			self.serverCommander.SAFE_RegisterCallBack("CaptchaOpenWindow", self.__CaptchaNew)



		self.serverCommander.SAFE_RegisterCallBack("pcstatus", self.__PcStatus)



	def BINARY_ServerCommand_Run(self, line):

		try:

			#print " BINARY_ServerCommand_Run", line

			return self.serverCommander.Run(line)

		except RuntimeError, msg:

			dbg.TraceError(msg)

			return 0



	def __ProcessPreservedServerCommand(self):

		try:

			command = net.GetPreservedServerCommand()

			while command:

				print " __ProcessPreservedServerCommand", command

				self.serverCommander.Run(command)

				command = net.GetPreservedServerCommand()

		except RuntimeError, msg:

			dbg.TraceError(msg)

			return 0



	def PartyHealReady(self):

		self.interface.PartyHealReady()



	def AskSafeboxPassword(self):

		self.interface.AskSafeboxPassword()



	# ITEM_MALL

	def AskMallPassword(self):

		self.interface.AskMallPassword()



	def __ItemMall_Open(self):

		self.interface.OpenItemMall();



	def CommandCloseMall(self):

		self.interface.CommandCloseMall()

	# END_OF_ITEM_MALL



	def RefineSuceededMessage(self):

		snd.PlaySound("sound/ui/make_soket.wav")

		if app.ENABLE_REFINE_RENEWAL:

			self.interface.CheckRefineDialog(False)

		self.PopupMessage(localeInfo.REFINE_SUCCESS)



	def RefineFailedMessage(self):

		snd.PlaySound("sound/ui/jaeryun_fail.wav")

		if app.ENABLE_REFINE_RENEWAL:

			self.interface.CheckRefineDialog(True)

		self.PopupMessage(localeInfo.REFINE_FAILURE)



	def CommandCloseSafebox(self):

		self.interface.CommandCloseSafebox()



	# PRIVATE_SHOP_PRICE_LIST

	def __PrivateShop_PriceList(self, itemVNum, itemPrice):

		uiPrivateShopBuilder.SetPrivateShopItemPrice(itemVNum, itemPrice)

	# END_OF_PRIVATE_SHOP_PRICE_LIST



	def __Horse_HideState(self):

		self.affectShower.SetHorseState(0, 0, 0)



	def __Horse_UpdateState(self, level, health, battery):

		self.affectShower.SetHorseState(int(level), int(health), int(battery))



	def __IsXMasMap(self):

		mapDict = ( "metin2_map_n_flame_01",

					"metin2_map_n_desert_01",

					"metin2_map_spiderdungeon",

					"metin2_map_deviltower1", )



		if background.GetCurrentMapName() in mapDict:

			return False



		return True



	def __XMasSnow_Enable(self, mode):



		self.__XMasSong_Enable(mode)



		if "1"==mode:



			if not self.__IsXMasMap():

				return



			print "XMAS_SNOW ON"

			background.EnableSnow(1)



		else:

			print "XMAS_SNOW OFF"

			background.EnableSnow(0)



	def __XMasBoom_Enable(self, mode):

		if "1"==mode:



			if not self.__IsXMasMap():

				return



			print "XMAS_BOOM ON"

			self.__DayMode_Update("dark")

			self.enableXMasBoom = True

			self.startTimeXMasBoom = app.GetTime()

		else:

			print "XMAS_BOOM OFF"

			self.__DayMode_Update("light")

			self.enableXMasBoom = False



	def __XMasTree_Enable(self, grade):



		print "XMAS_TREE ", grade

		background.SetXMasTree(int(grade))



	def __XMasSong_Enable(self, mode):

		if "1"==mode:

			print "XMAS_SONG ON"



			XMAS_BGM = "xmas.mp3"



			if app.IsExistFile("BGM/" + XMAS_BGM)==1:

				if musicInfo.fieldMusic != "":

					snd.FadeOutMusic("BGM/" + musicInfo.fieldMusic)



				musicInfo.fieldMusic=XMAS_BGM

				snd.FadeInMusic("BGM/" + musicInfo.fieldMusic)



		else:

			print "XMAS_SONG OFF"



			if musicInfo.fieldMusic != "":

				snd.FadeOutMusic("BGM/" + musicInfo.fieldMusic)



			musicInfo.fieldMusic=musicInfo.METIN2THEMA

			snd.FadeInMusic("BGM/" + musicInfo.fieldMusic)



	def __RestartDialog_Close(self):

		self.interface.CloseRestartDialog()



	def __Console_Enable(self):

		constInfo.CONSOLE_ENABLE = True

		self.consoleEnable = True

		app.EnableSpecialCameraMode()

		ui.EnablePaste(True)



	## PrivateShop

	def __PrivateShop_Open(self):

		self.__PressYKey()



	def BINARY_PrivateShop_Appear(self, vid, text):

		self.interface.AppearPrivateShop(vid, text)



	def BINARY_PrivateShop_Disappear(self, vid):

		self.interface.DisappearPrivateShop(vid)



	## DayMode

	def __PRESERVE_DayMode_Update(self, mode):

		if "light"==mode:

			background.SetEnvironmentData(0)

		elif "dark"==mode:



			if not self.__IsXMasMap():

				return



			background.RegisterEnvironmentData(1, constInfo.ENVIRONMENT_NIGHT)

			background.SetEnvironmentData(1)



	def __DayMode_Update(self, mode):

		if "light"==mode:

			self.curtain.SAFE_FadeOut(self.__DayMode_OnCompleteChangeToLight)

		elif "dark"==mode:



			if not self.__IsXMasMap():

				return



			self.curtain.SAFE_FadeOut(self.__DayMode_OnCompleteChangeToDark)



	def __DayMode_OnCompleteChangeToLight(self):

		background.SetEnvironmentData(0)

		self.curtain.FadeIn()



	def __DayMode_OnCompleteChangeToDark(self):

		background.RegisterEnvironmentData(1, constInfo.ENVIRONMENT_NIGHT)

		background.SetEnvironmentData(1)

		self.curtain.FadeIn()



	## XMasBoom

	def __XMasBoom_Update(self):



		self.BOOM_DATA_LIST = ( (2, 5), (5, 2), (7, 3), (10, 3), (20, 5) )

		if self.indexXMasBoom >= len(self.BOOM_DATA_LIST):

			return



		boomTime = self.BOOM_DATA_LIST[self.indexXMasBoom][0]

		boomCount = self.BOOM_DATA_LIST[self.indexXMasBoom][1]



		if app.GetTime() - self.startTimeXMasBoom > boomTime:



			self.indexXMasBoom += 1



			for i in xrange(boomCount):

				self.__XMasBoom_Boom()



	def __XMasBoom_Boom(self):

		x, y, z = player.GetMainCharacterPosition()

		randX = app.GetRandom(-150, 150)

		randY = app.GetRandom(-150, 150)



		snd.PlaySound3D(x+randX, -y+randY, z, "sound/common/etc/salute.mp3")



	def __PartyRequestQuestion(self, vid):

		vid = int(vid)

		partyRequestQuestionDialog = uiCommon.QuestionDialog()

		partyRequestQuestionDialog.SetText(chr.GetNameByVID(vid) + localeInfo.PARTY_DO_YOU_ACCEPT)

		partyRequestQuestionDialog.SetAcceptText(localeInfo.UI_ACCEPT)

		partyRequestQuestionDialog.SetCancelText(localeInfo.UI_DENY)

		partyRequestQuestionDialog.SetAcceptEvent(lambda arg=True: self.__AnswerPartyRequest(arg))

		partyRequestQuestionDialog.SetCancelEvent(lambda arg=False: self.__AnswerPartyRequest(arg))

		partyRequestQuestionDialog.Open()

		partyRequestQuestionDialog.vid = vid

		self.partyRequestQuestionDialog = partyRequestQuestionDialog



	def __AnswerPartyRequest(self, answer):

		if not self.partyRequestQuestionDialog:

			return



		vid = self.partyRequestQuestionDialog.vid



		if answer:

			net.SendChatPacket("/party_request_accept " + str(vid))

		else:

			net.SendChatPacket("/party_request_deny " + str(vid))



		self.partyRequestQuestionDialog.Close()

		self.partyRequestQuestionDialog = None



	def __PartyRequestDenied(self):

		self.PopupMessage(localeInfo.PARTY_REQUEST_DENIED)



	def __EnableTestServerFlag(self):

		app.EnableTestServerFlag()



	def __InGameShop_Show(self, url):

		if constInfo.IN_GAME_SHOP_ENABLE:

			self.interface.OpenWebWindow(url)



	# WEDDING

	def __LoginLover(self):

		if self.interface.wndMessenger:

			self.interface.wndMessenger.OnLoginLover()



	def __LogoutLover(self):

		if self.interface.wndMessenger:

			self.interface.wndMessenger.OnLogoutLover()

		if self.affectShower:

			self.affectShower.HideLoverState()



	def __LoverNear(self):

		if self.affectShower:

			self.affectShower.ShowLoverState()



	def __LoverFar(self):

		if self.affectShower:

			self.affectShower.HideLoverState()



	def __LoverDivorce(self):

		if self.interface.wndMessenger:

			self.interface.wndMessenger.ClearLoverInfo()

		if self.affectShower:

			self.affectShower.ClearLoverState()



	def __PlayMusic(self, flag, filename):

		flag = int(flag)

		if flag:

			snd.FadeOutAllMusic()

			musicInfo.SaveLastPlayFieldMusic()

			snd.FadeInMusic("BGM/" + filename)

		else:

			snd.FadeOutAllMusic()

			musicInfo.LoadLastPlayFieldMusic()

			snd.FadeInMusic("BGM/" + musicInfo.fieldMusic)

	# END_OF_WEDDING



	if app.ENABLE_SEND_TARGET_INFO:

		def BINARY_ClearTargetMonsterDropInfo(self):

			uiTarget.MONSTER_INFO_DATA = {}



		def BINARY_AddTargetMonsterDropInfo(self, raceNum, itemVnum, itemCount, itemSocket):

			if not raceNum in uiTarget.MONSTER_INFO_DATA:

				uiTarget.MONSTER_INFO_DATA.update({raceNum : {}})

				uiTarget.MONSTER_INFO_DATA[raceNum].update({"items" : []})



			curList = uiTarget.MONSTER_INFO_DATA[raceNum]["items"]



			isUpgradeable = False

			isMetin = False

			item.SelectItem(itemVnum)

			if item.GetItemType() == item.ITEM_TYPE_WEAPON or item.GetItemType() == item.ITEM_TYPE_ARMOR:

				isUpgradeable = True

			elif item.GetItemType() == item.ITEM_TYPE_METIN:

				isMetin = True



			for curItem in curList:

				if isUpgradeable:

					if curItem.has_key("vnum_list") and curItem["vnum_list"][0] / 10 * 10 == itemVnum / 10 * 10:

						if not (itemVnum in curItem["vnum_list"]):

							curItem["vnum_list"].append(itemVnum)

						return

				elif isMetin:

					if curItem.has_key("vnum_list"):

						baseVnum = curItem["vnum_list"][0]

					if curItem.has_key("vnum_list") and (baseVnum - baseVnum%1000) == (itemVnum - itemVnum%1000):

						if not (itemVnum in curItem["vnum_list"]):

							curItem["vnum_list"].append(itemVnum)

						return

				else:

					if curItem.has_key("vnum") and curItem["vnum"] == itemVnum and curItem["count"] == itemCount:

						return



			if isUpgradeable or isMetin:

				curList.append({"vnum_list":[itemVnum], "count":itemCount, "socket":itemSocket})

			else:

				curList.append({"vnum":itemVnum, "count":itemCount, "socket":itemSocket})



		def BINARY_RefreshTargetMonsterDropInfo(self, raceNum):

			self.targetBoard.RefreshMonsterInfoBoard()



	if app.ENABLE_CHANNEL_INFO_UPDATE:

		def BINARY_ReceiveChannel(self, channel):

			if self.interface:

				if self.interface.wndMiniMap:

					self.interface.wndMiniMap.UpdateChannelInfo(channel)



	if app.ENABLE_ACCE_COSTUME_SYSTEM:

		def ActAcce(self, iAct, bWindow):

			if self.interface:

				self.interface.ActAcce(iAct, bWindow)



		def AlertAcce(self, bWindow):

			snd.PlaySound("sound/ui/make_soket.wav")

			if bWindow:

				self.PopupMessage(localeInfo.ACCE_DEL_SERVEITEM)

			else:

				self.PopupMessage(localeInfo.ACCE_DEL_ABSORDITEM)





	if app.ENABLE_SHOW_CHEST_DROP:

		def BINARY_AddChestDropInfo(self, chestVnum, pageIndex, slotIndex, itemVnum, itemCount):

			if self.interface:

				self.interface.AddChestDropInfo(chestVnum, pageIndex, slotIndex, itemVnum, itemCount)



		def BINARY_RefreshChestDropInfo(self, chestVnum):

			if self.interface:

				self.interface.RefreshChestDropInfo(chestVnum)



	if app.ENABLE_SWITCHBOT:

		def RefreshSwitchbotWindow(self):

			if self.interface:

				self.interface.RefreshSwitchbotWindow()

			

		def RefreshSwitchbotItem(self, slot):

			if self.interface:

				self.interface.RefreshSwitchbotItem(slot)





	if app.ENABLE_ANTI_EXP:

		def SetAntiExp(self):

			flag = int(player.GetAntiExp())

			if self.interface:

				ptr = [self.interface.wndTaskBar]

				for gui in ptr:

					if gui:

						if flag:

							guiptr = gui.GetChild("AntiExp")

							guiptr.SetUpVisual("anti_exp/no_exp_0.tga")

							guiptr.SetOverVisual("anti_exp/no_exp_1.tga")

							guiptr.SetDownVisual("anti_exp/no_exp_2.tga")



							if gui.IsChild("RestExp_Value"):

								gui.GetChild("Exp_Value").Hide()



							if gui.IsChild("Exp_Value"):

								gui.GetChild("RestExp_Value").Hide()

								

							for j in range(1,5):

								if gui.IsChild("EXPGauge_0%d"%j):

									gui.GetChild("EXPGauge_0%d"%j).SetDiffuseColor(229.0/255.0, 140.0/255.0, 112.0/255.0,1)

						else:

							guiptr = gui.GetChild("AntiExp")

							guiptr.SetUpVisual("anti_exp/exp_0.tga")

							guiptr.SetOverVisual("anti_exp/exp_1.tga")

							guiptr.SetDownVisual("anti_exp/exp_2.tga")

							if gui.IsChild("RestExp_Value"):

								gui.GetChild("Exp_Value").Show()

							if gui.IsChild("Exp_Value"):

								gui.GetChild("RestExp_Value").Show()



							for j in range(1,5):

								if gui.IsChild("EXPGauge_0%d"%j):

									gui.GetChild("EXPGauge_0%d"%j).SetDiffuseColor(201,160,51,1)



	if app.ENABLE_HIDE_COSTUME_PART:

		# def BINARY_UpdateCostumeVisible(self, hair, body, weapon, sash):

		def BINARY_UpdateCostumeVisible(self, hair, body, weapon):

			constInfo.costumeHair = int(hair)

			constInfo.costumeCostume = int(body)

			constInfo.costumeWeapon = int(weapon)

			# if app.ENABLE_SHOULDER_SASH_SYSTEM:

				# constInfo.costumeSash = sash

			self.RefreshInventory()



	if app.ENABLE_CUBE_RENEWAL_WORLDARD:

		def BINARY_CUBE_RENEWAL_OPEN(self):

			if self.interface:

				self.interface.BINARY_CUBE_RENEWAL_OPEN()



	def OpenBalikBotu(self):

		if self.interface:

			self.interface.OpenFishBot()



# 5Lv Beceri Sistemi

	# Gui Sistemleri

	def __BecSystem1(self):

		if self.SelectSkill:

			self.SelectSkill.Close()

			self.SelectSkill = None



		self.SelectSkill = savbec.BlackIsinlanma()

		self.SelectSkill.OpenWindow()



	def __BecSystem2(self):

		if self.SelectSkill:

			self.SelectSkill.Close()

			self.SelectSkill = None



		self.SelectSkill = surabec.BlackIsinlanma()

		self.SelectSkill.OpenWindow()



	def __BecSystem3(self):

		if self.SelectSkill:

			self.SelectSkill.Close()

			self.SelectSkill = None



		self.SelectSkill = ninjabec.BlackIsinlanma()

		self.SelectSkill.OpenWindow()



	def __BecSystem4(self):

		if self.SelectSkill:

			self.SelectSkill.Close()

			self.SelectSkill = None



		self.SelectSkill = samanbec.BlackIsinlanma()

		self.SelectSkill.OpenWindow()



# Beceri Sistemleri

	# Savaþçý Becerileri

	def zihinsel_oto_bec(self,qid):

		constInfo.zihinsel_oto_bec = int(qid)



	def bedensel_oto_bec(self,qid):

		constInfo.bedensel_oto_bec = int(qid)



	# Sura Becerileri

	def karabuyu_oto_bec(self,qid):

		constInfo.karabuyu_oto_bec = int(qid)



	def buyulusilah_oto_bec(self,qid):

		constInfo.buyulusilah_oto_bec = int(qid)



	# Ninja Becerileri

	def yakin_oto_bec(self,qid):

		constInfo.yakin_oto_bec = int(qid)



	def uzak_oto_bec(self,qid):

		constInfo.uzak_oto_bec = int(qid)



	# Þaman Becerileri

	def ejderha_oto_bec(self,qid):

		constInfo.ejderha_oto_bec = int(qid)



	def iyilestirme_oto_bec(self,qid):

		constInfo.iyilestirme_oto_bec = int(qid)



	if app.__RANKING_SYSTEM__:

		def LoadRankData(self, cate, race, index, isFirst):

			self.interface.LoadRankData(int(cate), int(race), int(index), int(isFirst))



		def LoadRankUpdate(self, cate, race, index):

			self.interface.LoadRankUpdate(int(cate), int(race), int(index))



	if app.ENABLE_EVENT_MANAGER:

		def ClearEventManager(self):

			self.interface.ClearEventManager()

		def RefreshEventManager(self):

			self.interface.RefreshEventManager()

		def RefreshEventStatus(self, eventID, eventStatus, eventendTime, eventEndTimeText):

			self.interface.RefreshEventStatus(int(eventID), int(eventStatus), int(eventendTime), str(eventEndTimeText))

		def AppendEvent(self, dayIndex, eventID, eventIndex, startTime, endTime, empireFlag, channelFlag, value0, value1, value2, value3, startRealTime, endRealTime, isAlreadyStart):

			self.interface.AppendEvent(int(dayIndex),int(eventID), int(eventIndex), str(startTime), str(endTime), int(empireFlag), int(channelFlag), int(value0), int(value1), int(value2), int(value3), int(startRealTime), int(endRealTime), int(isAlreadyStart))



	if app.ENABLE_BAKIM_DUYURU:

		def BINARY_Maintenance(self, remaining_time, cause, duration):

			self.interface.OpenMaintenance(remaining_time, cause, duration)



	if app.ENABLE_DISCORD_STUFF:

		def GetMessage(self):

			if self.interface:

				self.interface.OpenWhisperWithMessage(constInfo.msgname)

				constInfo.msgname=""



###############################################################################################################

	if app.ENABLE_DRAGON_COIN_SHOP_SYSTEM:

		def ItemShopSetDragonCoin(self, dragonCoin):

			self.interface.DcItemShopSetDragonCoin(long(dragonCoin))



		def ItemShopSetDragonCash(self, dragonCash):

			self.interface.DcItemShopSetDragonCash(long(dragonCash))



		def ItemShopClear(self):

			uiDcItemShop.ItemShopClear()



		def ItemShopAddCategory(self, categoryName, categoryID):

			uiDcItemShop.ItemShopAddCategory(int(categoryID), str(categoryName))



		def ItemShopFillCategory(self, mainID, categoryName, categoryID):

			uiDcItemShop.ItemShopFillCategory(int(mainID), str(categoryName), int(categoryID))



		def ItemShopAppendItem(self, categoryID, itemID, itemVnum, itemCount, itemPrice, itemDiscount, itemTimeType, itemStock, itemTopSelling, itemSellType, itemAddedTime, itemOffertime, itemSockets, itemAttrs):

			uiDcItemShop.ItemShopAppendItem(int(categoryID), int(itemID), int(itemVnum), long(itemPrice), int(itemDiscount), int(itemTimeType), int(itemStock), int(itemOffertime), int(itemTopSelling), int(itemSellType), int(itemAddedTime), long(itemCount), itemSockets, itemAttrs)



		def ItemShopUpdateItem(self, itemID, itemStock):

			uiDcItemShop.ItemShopUpdateItem(int(itemID), int(itemStock))

			self.interface.DcItemShopUpdateItem(int(itemID), int(itemStock))



		def ItemShopOpen(self):

			self.interface.OpenDcItemShopWindow()



		def __OpenDcItemShop(self):

			self.interface.OpenDcItemShopWindow()



		def ItemShopSendOpen(self):

			net.SendItemShopPacket(net.DC_ISHOP_REFRESH, 0, long(0), int(0), "_GirisYenile_")



		def ItemShopLogClear(self):

			uiDcItemShop.ItemShopLogClear()



		def ItemShopAppendLog(self, dateText, dateTime, playerName, ipAdress, itemVnum, itemCount, itemPrice, itemPriceType):

			uiDcItemShop.ItemShopAppendLog(str(dateText), int(dateTime), str(playerName), str(ipAdress), int(itemVnum), int(itemCount), long(itemPrice), int(itemPriceType))



		def ItemShopPurchasesWindow(self):

			self.interface.ItemShopPurchasesWindow()



		def ItemShopLogRefresh(self):

			self.interface.ItemShopLogRefresh()



		def ItemShopHideLoading(self):

			self.interface.ItemShopHideLoading()



		def ItemShopPopupMessage(self, message, data):

			self.interface.ItemShopPopupMessage(message, data)



	if app.ENABLE_DRAGON_COIN_EM_MARKET:

		def ItemShopEmClear(self):

			uiDcItemShop.ItemShopEmClear()



		def ItemShopEmAddCategory(self, categoryName, categoryID):

			uiDcItemShop.ItemShopEmAddCategory(int(categoryID), str(categoryName))



		def ItemShopEmFillCategory(self, mainID, categoryName, categoryID):

			uiDcItemShop.ItemShopEmFillCategory(int(mainID), str(categoryName), int(categoryID))



		def ItemShopEmAppendItem(self, categoryID, itemID, itemVnum, itemCount, itemPrice, itemDiscount, itemTimeType, itemStock, itemTopSelling, itemSellType, itemAddedTime, itemOffertime, itemSockets, itemAttrs):

			uiDcItemShop.ItemShopEmAppendItem(int(categoryID), int(itemID), int(itemVnum), long(itemPrice), int(itemDiscount), int(itemTimeType), int(itemStock), int(itemOffertime), int(itemTopSelling), int(itemSellType), int(itemAddedTime), long(itemCount), itemSockets, itemAttrs)



		def __OpenDcEmItemShop(self):

			self.interface.OpenDcEmItemShopWindow()



		def ItemShopEmOpen(self):

			self.interface.OpenDcEmItemShopWindow()



		def ItemShopSetDragonEm(self, dragonEm):

			self.interface.DcItemShopSetDragonEm(long(dragonEm))



	if app.ENABLE_DRAGON_COIN_SHOP_ADMIN_SYSTEM:

		def ItemShopAdminClear(self):

			uiDcItemShopAdmin.ItemShopClear()



		def ItemShopAddCategoryAdmin(self, categoryName, categoryID):

			uiDcItemShopAdmin.ItemShopAddCategory(int(categoryID), str(categoryName))



		def ItemShopFillCategoryAdmin(self, mainID, categoryName, categoryID):

			uiDcItemShopAdmin.ItemShopFillCategory(int(mainID), str(categoryName), int(categoryID))



		def ItemShopAppendItemAdmin(self, categoryID, itemID, itemVnum, itemCount, itemPrice, itemDiscount, itemTimeType, itemStatus, itemStock, itemTopSelling, itemSellType, itemAddedTime, itemOffertime, itemStrAddedTime, itemStrOffertime, itemSockets, itemAttrs):

			uiDcItemShopAdmin.ItemShopAppendItem(int(categoryID), int(itemID), int(itemVnum), long(itemPrice), int(itemDiscount), int(itemTimeType), int(itemStatus), int(itemStock), int(itemOffertime), int(itemTopSelling), int(itemSellType), int(itemAddedTime), long(itemCount), itemStrAddedTime, itemStrOffertime, itemSockets, itemAttrs)



		def ItemShopOpenAdmin(self):

			if not chr.IsGameMaster(player.GetMainCharacterIndex()):

				return

			self.interface.OpenAdminDcItemShopWindow()



		def __OpenDcItemShopAdmin(self):

			if not chr.IsGameMaster(player.GetMainCharacterIndex()):

				return

			self.interface.OpenAdminDcItemShopWindow()

###############################################################################################################



	if app.ENABLE_MULTI_FARM_BLOCK:

		def UpdateMultiFarmPlayer(self, multiFarmPlayer):

			self.affectShower.SetMultiFarmPlayer(str(multiFarmPlayer))



		def UpdateMultiFarmAffect(self, multiFarmStatus, isNewStatus):

			self.affectShower.SetMultiFarmInfo(int(multiFarmStatus))

			if int(isNewStatus) == 1:

				if int(multiFarmStatus) == 1:

					chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.MULTI_FARM_ACTIVE_CHAT)

				else:

					chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.MULTI_FARM_DEACTIVE_CHAT)

			app.SetMultiFarmExeIcon(int(multiFarmStatus))



	if app.ENABLE_MULTI_HUNT_BLOCK:

		def UpdateMultiHuntPlayer(self, multiHuntPlayer):

			self.affectShower.SetMultiHuntPlayer(str(multiHuntPlayer))



		def UpdateMultiHuntAffect(self, multiHuntStatus, isNewStatus):

			self.affectShower.SetMultiHuntInfo(int(multiHuntStatus))

			if int(isNewStatus) == 1:

				if int(multiHuntStatus) == 1:

					chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.MULTI_HUNT_ACTIVE_CHAT)

				else:

					chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.MULTI_HUNT_DEACTIVE_CHAT)



	if app.ENABLE_MULTI_FISH_BLOCK:

		def UpdateMultiFishPlayer(self, multiFishPlayer):

			self.affectShower.SetMultiFishPlayer(str(multiFishPlayer))



		def UpdateMultiFishAffect(self, multiFishStatus, isNewStatus):

			self.affectShower.SetMultiFishInfo(int(multiFishStatus))

			if int(isNewStatus) == 1:

				if int(multiFishStatus) == 1:

					chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.MULTI_FISH_ACTIVE_CHAT)

				else:

					chat.AppendChat(chat.CHAT_TYPE_INFO, localeInfo.MULTI_FISH_DEACTIVE_CHAT)



	if app.ENABLE_PM_ALL_SEND_SYSTEM:

		def BINARY_OnRecvBulkWhisper(self, content):

			content = content.replace("$", " ")

			self.interface.RegisterGameMasterName("[Sistem]")

			chat.AppendWhisper(chat.WHISPER_TYPE_CHAT, "[Sistem]", content)

			self.interface.RecvWhisper("[Sistem]")



	if app.ENABLE_BIYOLOG:

		def BINARY_OnRecvBulkWhisperBiyolog(self, content):

			content = content.replace("$", " ")

			self.interface.RegisterGameMasterName("[Biyolog]")

			chat.AppendWhisper(chat.WHISPER_TYPE_CHAT, "[Biyolog]", content)

			self.interface.RecvWhisper("[Biyolog]")



	def AddLoopEvent(self, name, event):

		for i in self.loopList:

			if i[0] == name:

				i[1] = event

				return # already have.

		list = [name,event]

		self.loopList.append(list)



	def RemoveLoopEvent(self, name):

		for i in xrange(len(self.loopList)):

			if self.loopList[i][0] == name:

				del self.loopList[i]

				return



	def loopListEvent(self):

		for i in xrange(len(self.loopList)):

			returnValue = self.loopList[i][1]()

			if returnValue == True:

				del self.loopList[i]



	def __ClickEventPageButton(self):

		if app.ENABLE_DRAGON_COIN_SHOP_SYSTEM:

			net.SendItemShopPacket(net.DC_ISHOP_REFRESH, 0, long(0), int(0), "_GirisYenile_")

		else:

			pass



	if app.__BL_LUCKY_BOX__:

		def ShowLuckyBoxWindow(self, dwItemVnum, byItemCount, iNeedMoney):

			if self.interface:

				self.interface.ShowLuckyBoxWindow(dwItemVnum, byItemCount, iNeedMoney)



	if app.ENABLE_OFFER_SYSTEM:

		def BINARY_AddToOfferList(self, offerID, offerStartRemain, offerEndRemain, offerOldPrice, offerNewPrice):

			self.interface.AddToOfferList(offerID, offerStartRemain, offerEndRemain, offerOldPrice, offerNewPrice)



		def BINARY_AddToOfferItemList(self, itemID, itemOfferID, itemPos, itemCount, itemVnum, itemSockets, itemAttrs):

			self.interface.AddToOfferItemList(itemID, itemOfferID, itemPos, itemCount, itemVnum, itemSockets, itemAttrs)



		def ShowOfferIcon(self):

			self.interface.ShowOfferIcon()



	if app.__ARE_YOU_IN_OR_NOT__:

		def varmisinyokmusun(self, oran):

			gelen = int(oran)



			self.gameVarmisinButton = ui.Button()

			self.gameVarmisinButton.SetParent(self)

			self.gameVarmisinButton.SetPosition(wndMgr.GetScreenWidth() - 430, 25)

			self.gameVarmisinButton.SetUpVisual("varmisin/varmisin1.png")

			self.gameVarmisinButton.SetOverVisual("varmisin/varmisin2.png")

			self.gameVarmisinButton.SetDownVisual("varmisin/varmisin3.png")

			self.gameVarmisinButton.SetEvent(self.OnSelect2)

			self.gameVarmisinButton.EnableFlash()

			self.gameVarmisinButton.Show()



			if gelen == 0:

				if self.gameVarmisinButton.IsShow():

					self.gameVarmisinButton.Hide()



		def OnSelect2(self):

			if self.interface:

				self.interface.OpenAyirnGame()



	if app.ENABLE_OFFER_SYSTEM:

		def IndirimNesne(self, oran):

			gelen = int(oran)

			giden = str(gelen)

			bol = list(map(int, giden))



			self.gameHappyButton = ui.Button()

			self.gameHappyButton.SetParent(self)

			self.gameHappyButton.SetPosition(wndMgr.GetScreenWidth() - 575, 35)

			self.gameHappyButton.SetUpVisual("official_etc/nesneindirim/happyhours.png")

			self.gameHappyButton.SetOverVisual("official_etc/nesneindirim/happyhours.png")

			self.gameHappyButton.SetDownVisual("official_etc/nesneindirim/happyhours_down.png")

			self.gameHappyButton.SetEvent(self.OnSelect)

			self.gameHappyButton.EnableFlash()

			self.gameHappyButton.Show()



			if len(bol) >= 1 and int(bol[0]) > 0:

				self.deger1 = ui.Button()

				self.deger1.SetParent(self.gameHappyButton)

				self.deger1.SetUpVisual("official_etc/nesneindirim/"+str(bol[0])+".png")

				self.deger1.SetOverVisual("official_etc/nesneindirim/"+str(bol[0])+".png")

				self.deger1.SetDownVisual("official_etc/nesneindirim/"+str(bol[0])+"_down.png")

				self.deger1.SetEvent(self.OnSelect)

				self.deger1.SetPosition(-5, 0)

				self.deger1.Show()

				self.deger1.EnableFlash()

			if len(bol) >= 2 and int(bol[1]) >= 0:

				self.deger2 = ui.Button()

				self.deger2.SetParent(self.deger1)

				self.deger2.SetUpVisual("official_etc/nesneindirim/"+str(bol[1])+".png")

				self.deger2.SetOverVisual("official_etc/nesneindirim/"+str(bol[1])+".png")

				self.deger2.SetDownVisual("official_etc/nesneindirim/"+str(bol[1])+"_down.png")

				self.deger2.SetEvent(self.OnSelect)

				self.deger2.SetPosition(23, 0)

				self.deger2.Show()

				self.deger2.EnableFlash()

			if len(bol) >= 3 and int(bol[2]) >= 0:

				self.deger3 = ui.Button()

				self.deger3.SetParent(self.deger2)

				self.deger3.SetUpVisual("official_etc/nesneindirim/"+str(bol[2])+".png")

				self.deger3.SetOverVisual("official_etc/nesneindirim/"+str(bol[2])+".png")

				self.deger3.SetDownVisual("official_etc/nesneindirim/"+str(bol[2])+"_down.png")

				self.deger3.SetEvent(self.OnSelect)

				self.deger3.SetPosition(23, 0)

				self.deger3.Show()

				self.deger3.EnableFlash()



			if gelen == 0:

				if self.gameHappyButton.IsShow():

					self.gameHappyButton.Hide()

				if len(bol) >= 1:

					if self.deger1.IsShow():

						self.deger1.Hide()

				if len(bol) >= 2:

					if self.deger2.IsShow():

						self.deger2.Hide()

				if len(bol) >= 3:

					if self.deger3.IsShow():

						self.deger3.Hide()



		def OnSelect(self):

			if app.ENABLE_DRAGON_COIN_SHOP_SYSTEM:

				net.SendItemShopPacket(net.DC_ISHOP_REFRESH, 0, long(0), int(0), "_GirisYenile_")

			else:

				pass



	if app.ENABLE_EXCHANGE_LOG:

		def ExchangeLogClear(self, playerCode):

			self.interface.ExchangeLogClear(playerCode)

		def ExchangeLogRefresh(self, isLogItemRefresh):

			self.interface.ExchangeLogRefresh(isLogItemRefresh)

		def ExchangeLogAppend(self, logID, ownerName, ownerGold, ownerIP, targetName, targetGold, targetIP, date):

			self.interface.ExchangeLogAppend(logID, ownerName, ownerGold, ownerIP, targetName, targetGold, targetIP, date)

		def ExchangeLogItemAppend(self, logID, itemPos, itemVnum, itemCount, metinSlot, attrType, attrValue, isOwnerItem):

			self.interface.ExchangeLogItemAppend(logID, itemPos, itemVnum, itemCount, metinSlot, attrType, attrValue, isOwnerItem)



	#######################################################

	def IsInDuelMap(self):

		mapDict = ( "metin2_map_guild_battle",

					"metin2_map_t1",

					"metin2_map_t2",

					"metin2_map_t3",

					"metin2_map_t4",

					"metin2_map_t5",

					"metin2_map_t33",

					"metin2_map_t34",

					"metin2_map_t34y", )

		if background.GetCurrentMapName() in mapDict:

			return True

		return False



	if app.ENABLE_WHEEL_OF_FORTUNE:

		def BINARY_WofItemClear(self):

			uiWheelofFortune.WofItemClear()



		def BINARY_WofItemAdd(self, vnum, count):

			uiWheelofFortune.WofItemAdd(int(vnum), int(count))



		def BINARY_WofItemOpen(self, wheel, vnum, count):

			self.interface.OpenWheelofFortune(wheel, vnum, count)



		def __WHEEL_ICON_SHOW(self):

			if self.IsInDuelMap():

				return



			ROOT_PATH = "d:/ymir work/ui/game/whell_of_fortune/button/main/"



			wheelShowButton = ui.AniImageBox()

			wheelShowButton.SetParent(self)

			wheelShowButton.SetSize(40, 50)

			for j in xrange(40):

				wheelShowButton.AppendImage(ROOT_PATH+"%d.png" % j)

			wheelShowButton.SetPosition(wndMgr.GetScreenWidth() - 230, 45)

			wheelShowButton.OnMouseLeftButtonUp = ui.__mem_func__(self.OnOpenWheelDialog)

			wheelShowButton.SetDelay(8)

			wheelShowButton.Show()

			self.wheelShowButton = wheelShowButton



		def __WHEEL_ICON_HIDE(self):

			if self.wheelShowButton:

				self.wheelShowButton.Hide()



		def OnOpenWheelDialog(self):

			# net.SendChatPacket("/wheel_of_fortune open %d" % int(net.WHEEL_TYPE_EP))

			self.interface.OpenWheelDialogList()



		#//---------------------------------------//

		def __WHEEL_EVENT_ICON_SHOW(self):

			if self.IsInDuelMap():

				return



			ROOT_PATH = "d:/ymir work/ui/game/whell_of_fortune/button/main2/"



			wheelEventShowButton = ui.AniImageBox()

			wheelEventShowButton.SetParent(self)

			wheelEventShowButton.SetSize(40, 50)

			for j in xrange(40):

				wheelEventShowButton.AppendImage(ROOT_PATH+"%d.png" % j)

			wheelEventShowButton.SetPosition(wndMgr.GetScreenWidth() - (230 + 80), 45)

			wheelEventShowButton.OnMouseLeftButtonUp = ui.__mem_func__(self.OnOpenWheelEventDialog)

			wheelEventShowButton.SetDelay(4)

			wheelEventShowButton.Show()

			self.wheelEventShowButton = wheelEventShowButton



		def __WHEEL_EVENT_ICON_HIDE(self):

			if self.wheelEventShowButton:

				self.wheelEventShowButton.Hide()



		def OnOpenWheelEventDialog(self):

			self.interface.OpenWheelDialogEventList()

	#######################################################



	#######################################################

	if app.__RENEWAL_BRAVE_CAPE__:

		def SetBraveCapeStatus(self, status):

			if self.interface:

				if self.interface.wndInventory:

					if self.interface.wndInventory.wndBraveCape:

						self.interface.wndInventory.wndBraveCape.SetStatus(status)

	#######################################################



	if app.ENABLE_BATTLE_PASS:

		def BINARY_BattlePassOpen(self, bpName):

			if not self.interface:

				return



			if True == player.IsObserverMode():

				return



			wBattlePass = self.interface.wndBattlePass

			if wBattlePass:

				if not wBattlePass.IsShow():

					wBattlePass.Open(bpName)

				else:

					wBattlePass.Close()



		def BINARY_BattlePassAddMission(self, missionID, missionType, missionInfo1, missionInfo2, missionInfo3, missionName):

			if not self.interface:

				return



			wBattlePass = self.interface.wndBattlePass

			if wBattlePass:

				wBattlePass.AddMission(missionID, missionType, missionInfo1, missionInfo2, missionInfo3, missionName)



		def BINARY_BattlePassAddMissionReward(self, missionID, rewardType, itemVnum, itemCount):

			if not self.interface:

				return



			wBattlePass = self.interface.wndBattlePass

			if wBattlePass:

				wBattlePass.AddMissionReward(missionID, rewardType, itemVnum, itemCount)



		def BINARY_BattlePassUpdate(self, missionID, newProgress):

			if not self.interface:

				return



			wBattlePass = self.interface.wndBattlePass

			if wBattlePass:

				wBattlePass.UpdateMission(missionID, newProgress)



		def BINARY_BattlePassAddReward(self, rewardType, itemVnum, itemCount):

			if not self.interface:

				return



			wBattlePass = self.interface.wndBattlePass

			if wBattlePass:

				wBattlePass.AddReward(rewardType, itemVnum, itemCount)



	if app.ENABLE_TRADABLE_ICON:

		def BINARY_AddItemToExchange(self, inven_type, inven_pos, display_pos):

			if inven_type == player.INVENTORY:

				self.interface.CantTradableItemExchange(display_pos, inven_pos)



	#######################################################

	def __PressTabKey(self):

		if self.IsInDuelMap():

			if app.ENABLE_GUILD_STATISTICS_SYSTEM:

				self.GuildStatisticsOpen()

			return

		else:

			self.SendOpenTeleportWizardInfo()



	if app.ENABLE_TELEPORTION_WIZARD_SYSTEM:

		def BINARY_ClearTeleportWizardInfo(self):

			uiTpWizardInfo.CleanInfo()



		def BINARY_UpdateTeleportWizardInfo(self, index, type, commentText, levelMinLimit, levelMaxLimit, grade, itemVnum, itemCount, imgNum, raceNum, element, cooldown, status, money):

			uiTpWizardInfo.UpdateInfo(index, type, commentText, levelMinLimit, levelMaxLimit, grade, itemVnum, itemCount, imgNum, raceNum, element, cooldown, status, money)



		def BINARY_OpenTeleportWizardInfo(self):

			self.interface.ToggleTpWizardInfoWindow()



		def BINARY_ClearTpWizardDropInfo(self):

			self.interface.ClearTpWizardDropInfo()



		def BINARY_AddTpWizardDropInfo(self, raceNum, pageIndex, slotIndex, itemVnum, itemCount):

			self.interface.AddTpWizardDropInfo(raceNum, pageIndex, slotIndex, itemVnum, itemCount)



		def BINARY_RefreshTpWizardDropInfo(self, raceNum):

			self.interface.RefreshTpWizardDropInfo(raceNum)



		def SendOpenTeleportWizardInfo(self):

			net.SendChatPacket("/teleportion_wizard open")

	#######################################################



	###############################################################################################################

	if app.ENABLE_CAPTCHA_SELECT_SYSTEM:

		def __CaptchaNew(self, OrderList, ImageList, captchaName):

			captchaWindow = uiCommon.CaptchaNewWindow()

			captchaWindow.SetText1("Resimler arasýndan |cff00ff00%s|r resmini seçiniz." % str(captchaName))

			captchaWindow.SetTimeOverMsg("Soruyu zamanýnda cevaplamadýðýn için oyundan atýlýyorsun.")

			captchaWindow.SetTimeOverEvent(self.captchareply, "kapat")

			captchaWindow.Open(15, str(OrderList), str(ImageList))

			self.captchaWindow = captchaWindow



		def captchareply(self, answer):

			if not self.captchaWindow:

				return



			if answer == True:

				self.captchaWindow.Close()

				self.captchaWindow = None

			else:

				self.captchaWindow.Close()

				self.captchaWindow = None



	###############################################################################################################



	if app.BOSS_RANKING:

		def BR_ClearPlayerInfo(self):

			self.interface.BR_ClearPlayerInfo()

		def BR_AddPlayer(self, chName, chLevel, chRace, chEmpire, chDamage, chPercent):

			self.interface.BR_AddPlayerInfo(chName, chLevel, chRace, chEmpire, chDamage, chPercent)

		def BR_Refresh(self):

			self.interface.BR_RefreshWindow()

		def BR_CloseWindow(self):

			self.interface.BR_CloseWindow()



	###############################################################################################################



	if app.__BACK_DUNGEON__:

		def FormatTime(self, seconds):

			if seconds <= 0:

				return "0s"

			m, s = divmod(seconds, 60)

			h, m = divmod(m, 60)

			d, h = divmod(h, 24)

			text = ""

			if d > 0:

				text+="{}d ".format(d)

			if h > 0:

				text+="{}h ".format(h)

			if m > 0:

				text+="{}m ".format(m)

			if s > 0:

				text+="{}s ".format(s)

			return text[:len(text)-1] if len(text) > 0 else "0s"



		def ReJoinDungeonDialog(self, port, channel, mapIdx, leftTime):

			mapIdxEx = int(mapIdx) / 10000



			__mapNames = {

				66 : "Þeytan Kulesi",

			}

			mapName = __mapNames[mapIdxEx] if __mapNames.has_key(mapIdxEx) else "Noname"



			listIdx = app.GetRandom(0, 100)

			while True:

				if self.questionReJoinDialogDict.has_key(listIdx):

					listIdx = app.GetRandom(0, 100)

					continue

				break



			questionReJoinDialog = uiCommon.QuestionDialog()

			questionReJoinDialog.SetText(localeInfo.BACK_DUNGEON_TEXT.format(mapName, channel, self.FormatTime(int(leftTime))))

			questionReJoinDialog.SetAcceptEvent(lambda lIdx = listIdx  : self.__AcceptReJoinDungeon(lIdx))

			questionReJoinDialog.SetCancelEvent(lambda lIdx = listIdx : self.__CancelReJoinDungeon(lIdx))

			questionReJoinDialog.port = port

			questionReJoinDialog.channel = channel

			questionReJoinDialog.mapIdx = mapIdx

			questionReJoinDialog.Open()

			self.questionReJoinDialogDict[listIdx] = questionReJoinDialog



		def __AcceptReJoinDungeon(self, listIdx):

			window = self.questionReJoinDialogDict[listIdx] if self.questionReJoinDialogDict.has_key(listIdx) else None

			if window:

				net.SendChatPacket("/back_dungeon warp {} {} {}".format(window.port, window.channel, window.mapIdx))

			self.__CancelReJoinDungeon(listIdx)



		def __CancelReJoinDungeon(self, idx = -1):

			if idx == -1:

				for key, data in self.questionReJoinDialogDict.items():

					data.SetAcceptEvent(None)

					data.SetCancelEvent(None)

					data.Close()

				self.questionReJoinDialogDict={}

			else:

				if self.questionReJoinDialogDict.has_key(idx):

					self.questionReJoinDialogDict[idx].SetAcceptEvent(None)

					self.questionReJoinDialogDict[idx].SetCancelEvent(None)

					self.questionReJoinDialogDict[idx].Close()

					del self.questionReJoinDialogDict[idx]



	###############################################################################################################



	if app.ENABLE_COSTUME_SET_BONUS:

		def BINARY_CostumeSetBonus(self, status):

			self.affectShower.CostumeSetBonus(status)



	#######################################################



	if app.ENABLE_TANAKA_EVENT:

		def TanakaEvent_OpenQuestDialog(self):

			if self.TanakaEventQuestDialog:

				self.TanakaEventQuestDialog.Close()



			TanakaEventQuestDialog = uiCommon.QuestionDialog()

			TanakaEventQuestDialog.SetText("Korsan Tanaka Etkinliðine katýlmak istiyor musun?")

			TanakaEventQuestDialog.SetAcceptEvent(lambda arg=1: self.TanakaEvent_Answer(arg))

			TanakaEventQuestDialog.SetCancelEvent(lambda arg=0: self.TanakaEvent_Answer(arg))

			TanakaEventQuestDialog.Open()

			self.TanakaEventQuestDialog = TanakaEventQuestDialog



		def TanakaEvent_Answer(self, answer):

			if not self.TanakaEventQuestDialog:

				return



			if answer == 1:

				net.SendChatPacket("/t43ak4_3vent arena")



			self.TanakaEventQuestDialog.Close()

			self.TanakaEventQuestDialog = None



		def BINARY_OpenTanakaEventUI(self):

			if self.tanakaBoard:

				if not self.tanakaBoard.IsShow():

					self.tanakaBoard.Show()



		def BINARY_TanakaEventUpdate(self, level, count, leftcount):

			if self.tanakaBoard:

				self.tanakaBoard.UpdateEventInfo(level, count, leftcount)



		def BINARY_TanakaEventUpdatePlayerInfo(self, totalDmg):

			if self.tanakaBoard:

				self.tanakaBoard.UpdatePlayerInfo(int(totalDmg))



		def BINARY_TanakaEventUpdateItemInfo(self, name, vnum, count):

			if self.tanakaBoard:

				self.tanakaBoard.AddItemInfo(name, vnum, count)

	#######################################################



	if app.ENABLE_BLACK_MARKET_SYSTEM:

		def blackmarket_clear(self):

			constInfo.blackmarket = []



		def blackmarket_insert(self, vnum, yang, stock):

			constInfo.blackmarket.append("#"+str(vnum)+"#"+str(yang)+"#"+str(stock))



		def blackmarket_open(self):

			self.interface.OpenBlackMarket()



		def blackmarket_open_button(self):

			self.interface.OpenBlackMarketButton()



	#######################################################



	if app.ENABLE_REWARD_SYSTEM:

		def OpenRewardPlayers(self):

			self.interface.OpenRewardWindow()



		def reward_clear(self):

			self.interface.ClearRewardWindow()



		def reward_insert(self, index, data):

			self.interface.SetRewardPlayers(int(index), str(data))



		def reward_update(self):

			self.interface.UpdateRewardPlayers()



	#######################################################



	##########################PcBan########################

	def __PcStatus(self, status):

		heg = int(status)

		if (heg == 1):

			constInfo.set_ban_reg(constInfo.LOGIN_BAN_REG, constInfo.LOGIN_BAN_KEY)

		elif (heg == 0):

			constInfo.del_ban_reg(constInfo.LOGIN_BAN_REG)

	##########################PcBan########################



	##########################GuildStatistic########################

	if app.ENABLE_GUILD_STATISTICS_SYSTEM:

		#Lonca-K/D/A/

		def GuildWarAddListNew(self, name, damage, rank, race, kill, dead, asist):

			selfCharacter = False

			if (str(name) == str(player.GetName())):

				selfCharacter = True



			if self.interface.wndGuildWarScoreRank:

				self.interface.wndGuildWarScoreRank.UpdateRankEntry(int(rank), int(race), str(name), int(kill), int(dead), int(asist), long(damage), False)

				if selfCharacter:

					self.interface.wndGuildWarScoreRank.UpdateRankEntry(int(rank), int(race), str(name), int(kill), int(dead), int(asist), long(damage), selfCharacter)



			if self.interface.wndGuildWarSelfScore and selfCharacter:

				self.interface.wndGuildWarSelfScore.UpdateScoreText(int(kill), int(dead), int(asist), long(damage))



		def GuildWarDamageUpdate(self, kill, dead, asist, damage):

			selfCharacter = True

			if self.interface.wndGuildWarSelfScore and selfCharacter:

				self.interface.wndGuildWarSelfScore.UpdateScoreText(int(kill), int(dead), int(asist), long(damage))



		def GuildStatisticsOpen(self):

			if self.interface and self.interface.wndGuildWarScoreRank and self.interface.wndGuildWarSelfScore and self.interface.wndGuildWarSelfScore.IsShow():

				if self.interface.wndGuildWarScoreRank.IsShow():

					self.interface.wndGuildWarScoreRank.Close()

				else:

					self.interface.wndGuildWarScoreRank.Open()

		#Lonca-K/D/A/

	##########################GuildStatistic########################



	#######################################################

	if app.ENABLE_PUBLISHER_SYSTEM:

		def BINARY_PublisherInfoClear(self):

			constInfo.PublisherInformation = []



		def BINARY_PublisherInfoAdd(self, order, title, link):

			constInfo.PublisherInformation.append({"order": int(order), "title": str(title), "link": str(link)})



		def __publisher_system(self, value):

			if (int(value) > 0):

				self.__PUBLISHER_ICON_SHOW()

			else:

				self.__PUBLISHER_ICON_HIDE()



		def __PUBLISHER_ICON_SHOW(self):

			# if self.IsInDuelMap():

				# return



			publisherShowButton = ui.Button()

			publisherShowButton.SetParent(self)

			publisherShowButton.SetPosition(wndMgr.GetScreenWidth() - 105, 230)

			publisherShowButton.SetUpVisual("publisher_live.png")

			publisherShowButton.SetOverVisual("publisher_live.png")

			publisherShowButton.SetDownVisual("publisher_live.png")

			publisherShowButton.SetEvent(self.OnOpenPublisherInfoDialog)

			publisherShowButton.Show()

			self.publisherShowButton = publisherShowButton



			publisherCloseButton = ui.Button()

			publisherCloseButton.SetParent(publisherShowButton)

			publisherCloseButton.SetPosition(86, 3)

			publisherCloseButton.SetUpVisual("d:/ymir work/ui/public/close_button_01.sub")

			publisherCloseButton.SetOverVisual("d:/ymir work/ui/public/close_button_02.sub")

			publisherCloseButton.SetDownVisual("d:/ymir work/ui/public/close_button_03.sub")

			publisherCloseButton.SetEvent(self.__PUBLISHER_ICON_HIDE)

			# publisherCloseButton.Show()

			publisherCloseButton.Hide()

			self.publisherCloseButton = publisherCloseButton



		def __PUBLISHER_ICON_HIDE(self):

			if self.publisherShowButton:

				self.publisherShowButton.Hide()

			if self.publisherCloseButton:

				self.publisherCloseButton.Hide()



		def OnOpenPublisherInfoDialog(self):

			self.interface.OpenPublisherDialogList()

	#######################################################



	#######################################################

	if app.ENABLE_OKEY_KART_EVENT:

		def BINARY_Cards_UpdateInfo(self, hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, hand_4, hand_4_v, hand_5, hand_5_v, cards_left, points):

			self.interface.UpdateCardsInfo(hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, hand_4, hand_4_v, hand_5, hand_5_v, cards_left, points)



		def BINARY_Cards_FieldUpdateInfo(self, hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points):

			self.interface.UpdateCardsFieldInfo(hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points)



		def BINARY_Cards_PutReward(self, hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points):

			self.interface.CardsPutReward(hand_1, hand_1_v, hand_2, hand_2_v, hand_3, hand_3_v, points)



		def BINARY_Cards_ShowIcon(self):

			self.interface.CardsShowIcon()



		def BINARY_Cards_HideIcon(self):

			self.interface.CardsHideIcon()



		def BINARY_Cards_Open(self, safemode):

			self.interface.OpenCardsWindow(safemode)

	#######################################################



	if app.ENABLE_RONARK_SYSTEM:

		def BINARY_RonarkUpdateClear(self):

			return



		def BINARY_RonarkUpdateInfo(self, list, id, damage, member, limit, maxhp):

			if self.ronarkWarScoreBoard:

				if not self.ronarkWarScoreBoard.IsShow():

					self.ronarkWarScoreBoard.Show()

				self.ronarkWarScoreBoard.UpdateInfo(int(list), id, damage, member, limit, maxhp)



	#######################################################



	if app.ENABLE_AUTO_ITEM_SELL_SYSTEM:

		def BINARY_ClearAutoItemSell(self):

			if self.interface:

				if self.interface.wndAutoSell:

					self.interface.wndAutoSell.Clear()



		def BINARY_AddAutoItemSell(self, item):

			if self.interface:

				if self.interface.wndAutoSell:

					self.interface.wndAutoSell.AddItem(int(item))



		def BINARY_StatusAutoItemSell(self, status):

			if self.interface:

				if self.interface.wndAutoSell:

					self.interface.wndAutoSell.SetMod(status)



	def fishing_event_status(self, status):

		iActive = int(status)

		constInfo.FISHBOT_ACTIVE = True if iActive != 0 else False

		if (iActive == 0):

			self.interface.CloseFishBot()



	if app.SPIN_WHEEL:

		def BINARY_ClearSpinWheel(self):

			uispinwheel.REWARD_ITEMS = []

			uispinwheel.REWARD_COUNTS = []

			uispinwheel.REWARD_RARITIES = []



		def BINARY_AddSpinWheelResult(self, itemVnum, itemCount, rarity):

			uispinwheel.REWARD_ITEMS.append(itemVnum)

			uispinwheel.REWARD_COUNTS.append(itemCount)

			uispinwheel.REWARD_RARITIES.append(rarity)



		def BINARY_ShuffleList(self):

			combined = list(zip(uispinwheel.REWARD_ITEMS, uispinwheel.REWARD_COUNTS, uispinwheel.REWARD_RARITIES))

			#random.shuffle(combined)

			ar1, ar2, ar3 = zip(*combined)

			uispinwheel.REWARD_ITEMS = list(ar1)

			uispinwheel.REWARD_COUNTS = list(ar2)

			uispinwheel.REWARD_RARITIES = list(ar3)







		def BINARY_StartSpinWheel(self, rewardVnum):

			if self.interface:

				self.interface.OpenSpin(rewardVnum)

			if self.wheelWindow:

				self.wheelWindow.Reset()



		def BINARY_AddSpinWheelReward(self, index, itemVNum, itemCount, rarity):

			uispinwheel.REWARDS_ITEMS[index].append(itemVNum)

			uispinwheel.REWARDS_COUNTS[index].append(itemCount)

			uispinwheel.REWARDS_RARITIES[index].append(rarity)



		def BINARY_OpenSpinWheelReward(self):

			if self.interface:

				self.interface.OpenRewardsWindow()



		def SpinReward(self, reward):

			if self.interface:

				self.interface.SpinReward()

			if self.wheelWindow:

				self.wheelWindow.PopupReward(int(reward))

				self.wheelWindow.Reset()



		def SetSpinWheel(self, arg):

			if not self.wheelWindow.IsShow():

				self.wheelWindow.Show()

			count = int(arg)

			self.wheelWindow.SetWheelMetinStoneCount(count)

			if self.wheelWindow:

				self.wheelWindow.UpdatePercentage(count)

