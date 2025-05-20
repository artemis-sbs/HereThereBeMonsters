from sbs_utils.procedural.gui import gui_console_clients, gui_info_panel_send_message
from sbs_utils.procedural.comms import comms_override, comms_receive
from sbs_utils.procedural.links import linked_to
from sbs_utils.procedural.roles import all_roles
from sbs_utils.procedural.query import to_object
from sbs_utils.procedural.execution import get_shared_variable
from sbs_utils.faces import get_face
from sbs_utils.fs import get_mission_audio_file
import sbs



def here_info_panel_clear_comms():
    """ 
    This is helper function to clear the info panel message 
    """
    cc = gui_console_clients("comms")
    gui_info_panel_send_message(cc,path="message")
    gui_info_panel_send_message(cc,path="ship_data", time=0)

def here_comms_incoming_info_message(message, origin_id, selected_id=None, button=None, face=None, title=None, time = 0):
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
    if title is None and so is None:
        title = so.name

    with comms_override(origin_id, selected_id,face, title):
        msg = message
        if button is not None:
            msg = message  + " see info panel for interaction."
        comms_receive(msg)

    consoles = linked_to(origin_id, "consoles") & all_roles("console, comms")

    return gui_info_panel_send_message(consoles, message, title=title, face=face, button=button, time=time)

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

    with comms_override(origin_id, selected_id, face, title):
        comms_receive(message)
    # All Stations
    consoles = linked_to(origin_id, "consoles")
    choice = gui_info_panel_send_message(consoles, message, title=title, face=face, time=time)

    # play Audio file
    if audio is not None and get_shared_variable("HTBM_AUDIO_FILE_ENABLED", False):
        sbs.play_audio_file(0, get_mission_audio_file(audio), 1.0,1.0)
