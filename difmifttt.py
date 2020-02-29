# @author Jeremy F.
# MIT License
import pychromecast
from flask import Flask, request, jsonify
from secrets import DIFM_KEY, API_KEY

############# SETTINGS ###############
debug = True
show_audio_only_devices = False
difm_key = DIFM_KEY  # your API key for di.fm
difm_channels = {
        "lounge": "lounge_hi",
        "future bass": "futurebass_hi",
        "synthwave": "synthwave_hi",
        "deep tech": "deeptech_hi",
        "liquid dnb": "liquiddnb_hi",
        "electroswing": "electroswing_hi",
        "atmospheric breaks": "atmosphericbreaks_hi",
        "breaks": "breaks_hi",
        "vocal house": "vocalhouse_hi",
        "vocal trance": "vocaltrance_hi",
        "chillout": "chillout_hi",
        "trance": "trance_hi",
        "progressive":"progressive_hi",
        "chillout dreams":"chilloutdreams_hi",
        "space dreams":"spacedreams_hi",
        "vocal chillout":"vocalchillout_hi",
        "melodic Progressive":"melodicprogressive_hi",
        "chillstep":"chillstep_hi",
        "ambient":"ambient_hi",
        "epic trance":"epictrance_hi",
        "classic trance":"classictrance_hi",
        "eurodance":"eurodance_hi",
        "club Sounds":"clubsounds_hi",
        "vocal lounge":"vocalounge_hi",
        "electro house":"electrohouse_hi",
        "disco house":"discohouse_hi"
}

audio_model_names = ["Google Home", "Google Home Mini", "Google Cast Group", "Insignia NS-CSPGASP2", "Insignia NS-CSPGASP"]
######################################

######## GLOBALS #####################
# This does an update on app start
ccs = pychromecast.get_chromecasts(tries=3, retry_wait=2, timeout=10)
chomecast_names = []
app = Flask(__name__)
######################################
OK_RES = {"status": "ok"}
default_volume = 0.25


def log_error(msg):
    print("ERR: " + msg)
    return jsonify({"status": "error", "msg": msg})


def stop(device):
    if debug: print("Stopping device: " + device)
    if device in chomecast_names:
        cast = next(cc for cc in ccs if cc.device.friendly_name == device)
        mc = cast.media_controller
        mc.stop()
    else:
        print("Bad device")


def stop_all_audio():
    if debug:
        print("Stopping audio on all playing devices")
    for device in chomecast_names:
        cast = next(cc for cc in ccs if cc.device.friendly_name == device)
        mc = cast.media_controller
        if (mc.status.player_state == "PLAYING" or mc.status.player_state == "UNKNOWN") and cast.device.model_name in audio_model_names:
            mc.stop()
        else:
            print("DEVICE: " + cast.device.friendly_name + " IS: " + mc.status.player_state)


def cast(device, channel):
    if debug: print("Casting channel " + channel + " to " + device)
    cast = next(cc for cc in ccs if cc.device.friendly_name == device)
    cast.wait()
    mc = cast.media_controller
    mc.play_media("http://prem1.di.fm:80/" + channel + "?" + difm_key, "audio/mpeg")
    mc.block_until_active()


def update_chromecast_devices():
    if debug: print("Updating available chromecast device list")
    global ccs
    global chomecast_names
    ccs = pychromecast.get_chromecasts()

    for cc in ccs:
        print(cc.device.model_name)

    if show_audio_only_devices:
        chomecast_names = sorted([cc.device.friendly_name for cc in ccs if cc.device.model_name in audio_model_names])
    else:
        chomecast_names = sorted([cc.device.friendly_name for cc in ccs])


def set_volume(device, volume):
    if debug: print("Setting volume on " + device + " to " + str(float(volume)))
    cast = next(cc for cc in ccs if cc.device.friendly_name == device)
    cast.wait()
    cast.set_volume(float(volume))


def text2int(textnum):
    numwords = {}
    units = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
    ]

    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

    scales = ["hundred", "thousand", "million", "billion", "trillion"]

    numwords["and"] = (1, 0)
    for idx, word in enumerate(units):    numwords[word] = (1, idx)
    for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
    for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


@app.route('/api/<command>', methods=['POST'])
def process(command):
    req = request.json
    if debug:
        print(req)
    if 'key' not in req:
        return log_error("key not in request"), 401
    if req['key'] != API_KEY:
        return log_error("bad api key"), 401

    if command is not None and command not in ["stop", "play", "volume"]:
        return log_error("bad command"), 400

    if command == "stop":
        stop_all_audio()
        return jsonify(OK_RES), 200

    if command == "play":
        device = "Almost All"
        if 'channel' in req:
            channel = req['channel'].lower()
            channel = channel.replace("brakes", "breaks")  # google assistant is only so good
            channel = channel.strip()  # for some reason sometimes theres a leading space
        else:
            channel = "lounge"
        if device not in chomecast_names:
            print(chomecast_names)
            return log_error("device not available: " + device), 400
        if channel not in difm_channels:
            return log_error("Channel not available: " + channel), 400
        cast(device, difm_channels[channel])
        set_volume(device, default_volume)
        return jsonify(OK_RES), 200

    if command == "volume":
        device = "Almost All"
        if device not in chomecast_names:
            return log_error("device not available: " + device), 400
        if 'volume' in req:
            volume = req['volume']
        else:
            volume = default_volume

        if(isinstance(volume, str) ):  # google assistant will give us "five" instead of 5, but give you "25" if you ask for 25. wtf
            if(RepresentsInt(volume)):
                volume = int(volume)
            else:
                volume = text2int(volume)

        if volume > 1:
            volume = volume/100.0  # if it comes from google assistant, it will be "25"
        set_volume(device, volume)
        return jsonify(OK_RES), 200

    return log_error("bad command"), 400


if __name__ == "__main__":
    update_chromecast_devices()
    app.run(host="0.0.0.0", port=5001, debug=debug)
