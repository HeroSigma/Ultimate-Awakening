Route17_Frlg_MapScripts::
	.byte 0

Route17_EventScript_ItemsNotice::
	msgbox Route17_Text_WatchOutForDiscardedItems, MSGBOX_SIGN
	end

Route17_EventScript_TrainerTips1::
	msgbox Route17_Text_SameSpeciesGrowDifferentRates, MSGBOX_SIGN
	end

Route17_EventScript_TrainerTips2::
	msgbox Route17_Text_PressBToStayInPlace, MSGBOX_SIGN
	end

Route17_EventScript_RouteSign::
	msgbox Route17_Text_RouteSign, MSGBOX_SIGN
	end

Route17_EventScript_BallsNotice::
	msgbox Route17_Text_DontThrowGameThrowBalls, MSGBOX_SIGN
	end

Route17_EventScript_CyclingRoadSign::
	msgbox Route17_Text_CyclingRoadSign, MSGBOX_SIGN
	end

Route17_Text_WatchOutForDiscardedItems::
	.string "It's a notice.\p"
	.string "Watch out for discarded items.$"

Route17_Text_SameSpeciesGrowDifferentRates::
	.string "TRAINER TIPS\p"
	.string "All POKéMON are unique.\p"
	.string "Even POKéMON of the same species\n"
	.string "and level grow at different rates.$"

Route17_Text_PressBToStayInPlace::
	.string "TRAINER TIPS\p"
	.string "Press the B Button to stay in place\n"
	.string "while on a slope.$"

Route17_Text_RouteSign::
	.string "ROUTE 17\n"
	.string "CELADON CITY - FUCHSIA CITY$"

Route17_Text_DontThrowGameThrowBalls::
	.string "It's a notice!\p"
	.string "Don't throw the game, throw POKé\n"
	.string "BALLS instead!$"

Route17_Text_CyclingRoadSign::
	.string "CYCLING ROAD\n"
	.string "Slope ends here!$"

