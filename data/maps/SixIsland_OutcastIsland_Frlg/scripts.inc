SixIsland_OutcastIsland_Frlg_MapScripts::
	.byte 0

SixIsland_OutcastIsland_EventScript_Rocket::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_46, SixIsland_OutcastIsland_Text_RocketIntro, SixIsland_OutcastIsland_Text_RocketDefeat
	msgbox SixIsland_OutcastIsland_Text_RocketPostBattle, MSGBOX_AUTOCLOSE
	end

SixIsland_OutcastIsland_Text_RocketIntro::
	.string "There're no rare POKéMON around\n"
	.string "these parts! Not a one!\p"
	.string "That burns me up, man.\n"
	.string "I'll take it out on you!$"

SixIsland_OutcastIsland_Text_RocketDefeat::
	.string "…Huh?$"

SixIsland_OutcastIsland_Text_RocketPostBattle::
	.string "So listen, you haven't seen any\n"
	.string "rare POKéMON, have you?$"
