from sbs_utils.procedural.gui import gui_reroute_client
from sbs_utils.procedural.comms import comms_override, comms_receive, comms_info_card, comms_info_clear
from sbs_utils.procedural.gui.overlay import (
    overlay_lower_third, overlay_hero, overlay_banner, overlay_flash, overlay_clear)
from sbs_utils.procedural.announce import announce_headline
from sbs_utils.procedural.links import linked_to
from sbs_utils.procedural.roles import all_roles, role, any_role
from sbs_utils.procedural.query import to_object
from sbs_utils.procedural.grid import grid_objects
from sbs_utils.procedural.execution import get_shared_variable
from sbs_utils.faces import get_face
from sbs_utils.procedural.amd_doc import amd_document, amd_section
from sbs_utils.procedural.amd_mission import amd_mission_data
from sbs_utils.procedural.amd_dialogue import dialogue_scenes
from sbs_utils.procedural.hail import hail_set_speaker_resolver
from sbs_utils import fs
import io
import sbs



def here_info_panel_clear_comms(consoles="comms"):
    """ 
    This is helper function to clear the info panel message 
    """
    cc = role(f"console") & any_role(consoles)
    comms_info_clear(cc)

def here_comms_incoming_info_message(message, origin_id, selected_id=None, button=None, face=None, title=None, time = 0, consoles="comms"):
    """ This is a helper function to send a comms message as well as present a message in the info panel

    Args:
        message (str): _description_
        origin_id (ID): _description_
        selected_id (ID, optional): _description_. Defaults to None.
        button (str, optional): _description_. Defaults to None.
        face (str, optional): _description_. Defaults to None.
        title (str, optional): _description_. Defaults to None.
        time (int, optional): _description_. Defaults to 0.

    Returns:
        Promise: the Promise from the info panel button handler
    """

    if selected_id is None:
        selected_id = origin_id
    so = to_object(selected_id)
    if face is None:
        face = get_face(selected_id)
    

    with comms_override(origin_id, selected_id,face):
        msg = message
        if button is not None:
            msg = message  + " see info panel for interaction."
        comms_receive(msg, title=title)

    # The card (with its button/promise) is the RECORD - it has history and is
    # reconnect-safe, so it stays exactly as it was. The overlay is the ATTENTION
    # half: the whole bridge sees a hail arrive, not just the comms console that
    # happens to be looking at the info panel.
    overlay_lower_third("INCOMING TRANSMISSION",
                        announce_headline(title or message, 70),
                        to=origin_id, seconds=8)

    consoles = linked_to(origin_id, "consoles") & role(f"console") & any_role(consoles)

    return comms_info_card(consoles, message, title=title, face=face, button=button, time=time)

def here_scene(title, subtitle=None, ship=None, seconds=4):
    """A chapter card for a scene beat - the hero slot on every console of the
    player ship. Cinematic only: it carries no facts the comms log doesn't."""
    overlay_hero(title, subtitle=subtitle,
                 to=(ship if ship is not None else get_shared_variable("artemis_id")),
                 seconds=seconds)


def here_system_break(system_name, ship=None):
    """Sabotage punctuation: a hull-hit colour wash plus a banner naming the system
    that just went down. The damage itself is the record, so there is no twin."""
    to = ship if ship is not None else get_shared_variable("artemis_id")
    overlay_flash("#f006", to=to)
    overlay_banner(f"{system_name} OFFLINE", color="#f44", to=to, seconds=6)




# --- Dialogue -----------------------------------------------------------------
# Every message in the mission lives in dialogue/messages.amd. story.mast names a
# scene; the document carries the words, the title, and the recorded line.

# Which shared variable holds the AGENT whose face a voice wears. Only this is code:
# the display NAME comes from the document's Cast section, so a voice is named in one
# place. Ships are spawned mid-story, so this has to be looked up when the hail is
# offered rather than bound once at load.
HERE_VOICE_AGENTS = {
    "tsn_command":   "tsn_command",
    "ensign_rachel": "ensign_rachel",
    "medical_bay":   "medical_bay_doctor",
    "whale_watcher": "whale_watcher_id",
    "dauntless":     "dauntless_id",
    "odessa":        "odessa_id",
    "wolf_spider":   "wolf_spider",
    "hostages":      "ensign_rachel",
}

_here_cast = {}


def here_hail_speaker(key, ship_id=None):
    """A cast key -> the `{name, face}` card a hail draws.

    Registered with `hail_set_speaker_resolver`, which is why story.mast passes only
    `speaker=`/`scene=` - not a name and not a face - at 20 call sites.
    """
    node = _here_cast.get(key)
    name = (node or {}).get("display_text") or key
    agent = get_shared_variable(HERE_VOICE_AGENTS.get(key)) if key in HERE_VOICE_AGENTS else None
    return {"name": name, "face": get_face(agent) if agent is not None else None}


def here_dialogue_load():
    """Load dialogue/messages.amd, register the speaker resolver, return the scenes.

    Called once from story.mast's top level. `_here_cast` is module state and so
    survives into a second mission in the dev runner - harmless, because this reruns
    and replaces it, and `reset_mission_state` drops the resolver either way.
    """
    global _here_cast
    path = fs.get_mission_dir_filename("dialogue/messages.amd")
    with io.open(path, encoding="utf-8") as f:
        content = f.read()
    doc = amd_document(content, data_parser=amd_mission_data,
                       title="Here There Be Monsters")
    _here_cast = dialogue_scenes(amd_section(doc, "cast"))
    hail_set_speaker_resolver(here_hail_speaker)
    return dialogue_scenes(amd_section(doc, "messages"))
