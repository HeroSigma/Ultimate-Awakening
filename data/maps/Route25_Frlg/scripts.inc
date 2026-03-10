Route25_Frlg_MapScripts::
	.byte 0

Route25_EventScript_SeaCottageSign::
	msgbox Route25_Text_SeaCottageSign, MSGBOX_SIGN
	end

Route25_EventScript_Man::
	msgbox Route25_Text_AreYouHereAlone, MSGBOX_NPC
	end

Route25_Text_SeaCottageSign::
	.string "SEA COTTAGE\n"
	.string "BILL lives here!$"

Route25_Text_AreYouHereAlone::
	.string "Hello, are you here alone?\p"
	.string "If you're out at CERULEAN's cape…\n"
	.string "Well, it should be as a couple.$"

