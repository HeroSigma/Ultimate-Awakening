Route13_Frlg_MapScripts::
	.byte 0

Route13_EventScript_TrainerTips1::
	msgbox Route13_Text_LookToLeftOfThatPost, MSGBOX_SIGN
	end

Route13_EventScript_TrainerTips2::
	msgbox Route13_Text_SelectToSwitchItems, MSGBOX_SIGN
	end

Route13_EventScript_RouteSign::
	msgbox Route13_Text_RouteSign, MSGBOX_SIGN
	end

Route13_Text_LookToLeftOfThatPost::
	.string "TRAINER TIPS\p"
	.string "Look, look!\n"
	.string "Look to the left of that post!$"

Route13_Text_SelectToSwitchItems::
	.string "TRAINER TIPS\p"
	.string "Use SELECT to switch items in the\n"
	.string "ITEMS window.$"

Route13_Text_RouteSign::
	.string "ROUTE 13\n"
	.string "North to SILENCE BRIDGE$"

