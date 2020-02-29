# @author Jeremy F.
# MIT License
import pychromecast
from flask import Flask, request, render_template, redirect
from secrets import DIFM_KEY

############# SETTINGS ###############
debug = True
show_audio_only_devices = False
difm_key = DIFM_KEY  # your API key for di.fm
difm_channels = {
        "Lounge":"lounge_hi",
        "Future Bass": "futurebass_hi",
        "Synthwave":"synthwave_hi",
        "Deep Tech":"deeptech_hi",
        "Liquid DnB":"liquiddnb_hi",
        "Electroswing":"electroswing_hi",
        "Atmospheric Breaks":"atmosphericbreaks_hi",
        "Breaks": "breaks_hi",
        "Vocal House": "vocalhouse_hi",
        "Vocal Trance": "vocaltrance_hi",
        "Chillout":"chillout_hi",
        "Trance":"trance_hi",
        "Progressive":"progressive_hi",
        "Chillout Dreams":"chilloutdreams_hi",
        "Space Dreams":"spacedreams_hi",
        "Vocal Chillout":"vocalchillout_hi",
        "Melodic Progressive":"melodicprogressive_hi",
        "Chillstep":"chillstep_hi",
        "Ambient":"ambient_hi",
        "Epic Trance":"epictrance_hi",
        "Classic Trance":"classictrance_hi",
        "Eurodance":"eurodance_hi",
        "Club Sounds":"clubsounds_hi",
        "Vocal Lounge":"vocalounge_hi",
        "Electro House":"electrohouse_hi",
        "Disco House":"discohouse_hi"
}

audio_model_names = ["Google Home", "Google Home Mini", "Google Cast Group", "Insignia NS-CSPGASP2", "Insignia NS-CSPGASP"]
######################################

######## GLOBALS #####################
ccs = pychromecast.get_chromecasts(tries=3, retry_wait=2, timeout=10)
chomecast_names = []
app = Flask(__name__)
######################################


def stop(device):
    if debug: print("Stopping device: " + device)
    if device in chomecast_names:
        cast = next(cc for cc in ccs if cc.device.friendly_name == device)
        mc = cast.media_controller
        mc.stop()
    else:
        print("Bad device")

def stop_all_audio():
    if debug: print("Stopping audio on all playing devices")
    for device in chomecast_names:
        cast = next(cc for cc in ccs if cc.device.friendly_name == device)
        mc = cast.media_controller
        if mc.status.player_state == "PLAYING" and cast.device.model_name in audio_model_names:
            mc.stop()


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


@app.route('/process', methods=['POST'])
def process():
    type = None
    try:
        type = request.form.get("t")
    except:
        pass

    if type != None and type not in ["update", "stopall", "manual", "fav", "volume"]:
        return redirect("/?error=bad_type")

    if type == "update":
        update_chromecast_devices()

    elif type == "stopall":
        stop_all_audio()

    elif type == "manual" or type == "fav":
        try:
            device = request.form.get('device')
            channel = request.form.get('channel')
            if device not in chomecast_names:
                return redirect("/?error=bad_device")
            if channel not in difm_channels.values():
                return redirect("/?error=unsupported_channel")
            cast(device, channel)
        except Exception as e:
            return redirect("/?error="+str(e))

    elif type == "volume":
        try:
            device = request.form.get('device')
            if device not in chomecast_names:
                return redirect("/?error=bad_device")
            volume = request.form.get('volume')
            set_volume(device, volume)
        except Exception as e:
           return redirect("/?error="+str(e))

    return redirect("/")

@app.route('/')
def main():
    try:
        error = request.args.get("error")
    except:
        error = None
    return render_template("index.html", channels=difm_channels, chromecasts=chomecast_names, error=error)


if __name__ == "__main__":
    update_chromecast_devices()
    app.run(host="0.0.0.0", port=5000, debug=debug)
