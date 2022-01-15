# -*- coding: utf-8 -*-

import map_scene
import logo_scene
import titlescreen_scene

from npcs import NPCMan, NPCWoman, NPCBoy, NPCOldMan
from party import party
from event_area import EventArea


sega_logo_scene = logo_scene.SegaLogoScene()

title_screen_scene = titlescreen_scene.TitleScreenScene()

ps3_town_dbl_scene = map_scene.MapScene(
	"ps3town-dbl", [
#	"test", [
		party,
		NPCMan(name="Jean", pos=(1024, 512), move_rect=(960, 352, 128, 224), event_string="Basic NPC dialog[end]"),
		NPCBoy(name="Pierre", pos=(832, 512), move_rect=(704, 384, 256, 256), event_string="Basic NPC dialog[end]"),
		NPCBoy(name="Pierre", pos=(512, 288), move_rect=(448, 256, 256, 128), event_string="Basic NPC dialog[end]"),
		NPCWoman(name="Marie", pos=(800, 480), move_rect=(448, 480, 512, 32), event_string="Basic NPC dialog[end]"),
		NPCWoman(name="Marie", pos=(256, 320), move_rect=(192, 256, 128, 128), event_string="Basic NPC dialog[end]"),
		NPCMan(name="Pierre", pos=(320, 512), move_rect=(192, 448, 256, 128), event_string="Basic NPC dialog[end]"),
		NPCOldMan(name="Pierre", pos=(512, 588), move_rect=(448, 576, 128, 64), event_string="Basic NPC dialog[end]"),
		NPCOldMan(name="Pierre", pos=(704, 704), move_rect=(576, 640, 256, 128), event_string="Basic NPC dialog[end]"),
		EventArea((10, 20, 40, 20), "[run_scene(2)]")
	], (840, 480))
