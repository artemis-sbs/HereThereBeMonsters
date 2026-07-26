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
from sbs_utils.fs import get_mission_audio_file
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

def here_receive_info_message(message, origin_id, selected_id=None, face=None, title=None, time=0, audio=None):
    """ Receive a message on the INfo panel in comms

    Args:
        message (str): _description_
        origin_id (ID): _description_
        selected_id (ID, optional): _description_. Defaults to None.
        face (str, optional): _description_. Defaults to None.
        title (str, optional): _description_. Defaults to None.
        time (int, optional): _description_. Defaults to 0.
        audio (str, optional): _description_. Defaults to None.
    """
    if selected_id is None:
        selected_id = origin_id
    so = to_object(selected_id)
    if face is None:
        face = get_face(selected_id)
    if title is None and so is None:
        title = so.name

    with comms_override(origin_id, selected_id, face):
        comms_receive(message, title)
    # All Stations
    consoles = linked_to(origin_id, "consoles")
    choice = comms_info_card(consoles, message, title=title, face=face, time=time)

    # Subtitles. The audio plays over a main screen that otherwise shows nothing,
    # so put the speaker + line over the live view for as long as the card lasts.
    # The full text stays on the card; this is a headline.
    overlay_lower_third(announce_headline(title or "", 40),
                        announce_headline(message, 90),
                        to=origin_id, seconds=(time if time and time > 0 else 12))

    # play Audio file
    if audio is not None and get_shared_variable("HTBM_AUDIO_FILE_ENABLED", False):
        sbs.play_audio_file(0, get_mission_audio_file(audio), 1.0,1.0)


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


