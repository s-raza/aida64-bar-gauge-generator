
import win32com.client
import winreg
import time
import subprocess
import configparser
from pprint import pprint

PLAY_FONT_CHAR = "4"
PAUSE_FONT_CHAR = ";"
STOP_FONT_CHAR = "<"
CROSS_FONT_CHAR = "r"


class iTunesMonitorBase:
    def __init__(self):
        self.itunes_app = None
        self.last_icon = ""
        self.last_text = ""

    def _is_itunes_running(self):
        try:
            output = subprocess.check_output('tasklist /FI "IMAGENAME eq iTunes.exe"', shell=True)
            return "iTunes.exe" in output.decode()
        except subprocess.CalledProcessError:
            return False

    def _get_itunes_com_object(self):
        try:
            itunes = win32com.client.Dispatch("iTunes.Application")
            return itunes
        except (win32com.client.pywintypes.com_error, AttributeError):
            return None

    def _release_com_object(self):
        if self.itunes_app:
            try:
                win32com.client.pythoncom.CoUninitialize()
            except Exception as e:
                print(f"Error during CoUninitialize: {e}")
            self.itunes_app = None
            print("iTunes COM object released.")

    def get_displayable_properties(self, track_object):
        displayable_properties = {}
        all_attributes = dir(track_object)
        for attr_name in all_attributes:
            if not attr_name.startswith('_') and not callable(getattr(track_object, attr_name, None)):
                try:
                    value = getattr(track_object, attr_name)
                    if attr_name not in ['AddRef', 'QueryInterface', 'Release', 'GetIDsOfNames', 'GetTypeInfo', 'GetTypeInfoCount', 'Invoke']:
                        displayable_properties[attr_name] = str(value)
                except Exception as e:
                    print(f"Could not retrieve property '{attr_name}': {e}")
        return displayable_properties

    def save_info(self, icon_char, text_string, data_dict):
        raise NotImplementedError("This method must be implemented by a subclass.")

class iTunesToRegistry(iTunesMonitorBase):
    def __init__(self, icon_value_name="Str1", text_value_name="Str2", registry_path="Software\\FinalWire\\AIDA64\\ImportValues"):
        super().__init__()
        self.registry_path = registry_path
        self.icon_value_name = icon_value_name
        self.text_value_name = text_value_name

    def save_info(self, icon_char, text_string, data_dict):
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.registry_path)
            winreg.SetValueEx(key, self.icon_value_name, 0, winreg.REG_SZ, icon_char)
            winreg.SetValueEx(key, self.text_value_name, 0, winreg.REG_SZ, text_string)
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error writing to registry: {e}")

class iTunesToINI(iTunesMonitorBase):
    def __init__(self, ini_file_path="itunes_data.ini"):
        super().__init__()
        self.ini_file_path = ini_file_path

    def save_info(self, icon_char, text_string, data_dict):
        config = configparser.ConfigParser()
        data_dict['IconChar'] = icon_char
        data_dict['SongText'] = text_string
        config['CurrentTrack'] = data_dict
        try:
            with open(self.ini_file_path, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        except Exception as e:
            print(f"Error writing to INI file: {e}")

class iTunesSaveInfo:
    def __init__(self, use_ini=True, **kwargs):
        if use_ini:
            self.monitor = iTunesToINI(kwargs.get("ini_file_path", "itunes_data.ini"))
        else:
            self.monitor = iTunesToRegistry(
                kwargs.get("icon_value_name", "Str1"),
                kwargs.get("text_value_name", "Str2")
            )
        self.current_song_info = None

    def _get_current_status(self, itunes_is_present):
        if not itunes_is_present:
            return CROSS_FONT_CHAR, "iTunes", {"Status": "Not Running"}

        try:
            player_state = self.monitor.itunes_app.PlayerState
            current_track = self.monitor.itunes_app.CurrentTrack
            
            data_dict = self.monitor.get_displayable_properties(current_track)
            song_name = data_dict.get('Name', 'Unknown')
            text_string = song_name
            
            if song_artist := data_dict.get('Artist'):
                song_artist = f"[{song_artist}]"
                text_string = f"{song_name} {song_artist}"

            if player_state == 1 and current_track:
                return PLAY_FONT_CHAR, text_string, data_dict
            elif player_state != 1 and current_track:
                return PAUSE_FONT_CHAR, text_string, data_dict
            else:
                return STOP_FONT_CHAR, "iTunes", {"Status": "Stopped"}

        except Exception as e:
            print(f"Error getting iTunes state: {e}")
            return CROSS_FONT_CHAR, "iTunes", {"Status": "Error"}

    def _reconnect_to_itunes(self):
        print("iTunes is running. Attempting to connect...")
        connect_attempts = 0
        max_attempts = 30
        while not self.monitor.itunes_app and connect_attempts < max_attempts:
            self.monitor.itunes_app = self.monitor._get_itunes_com_object()
            if not self.monitor.itunes_app:
                time.sleep(0.1)
                connect_attempts += 1
        if self.monitor.itunes_app:
            print("Successfully connected to iTunes.")
            return True
        else:
            print("Failed to get iTunes COM object after multiple attempts. Retrying later...")
            return False

    def run(self, itunes_check_interval=10, update_interval=0.1):
        itunes_is_present = False
        while True:
            try:
                is_running_now = self.monitor._is_itunes_running()

                if not is_running_now:
                    if itunes_is_present:
                        self.monitor._release_com_object()
                    itunes_is_present = False
                
                if is_running_now and not itunes_is_present:
                    if self._reconnect_to_itunes():
                        itunes_is_present = True
                    else:
                        time.sleep(itunes_check_interval)
                        continue
                
                icon_char, text_string, data_dict = self._get_current_status(itunes_is_present)
                
                if icon_char != self.monitor.last_icon or text_string != self.monitor.last_text:
                    print(f"Updating status: {icon_char} {text_string}")
                    self.monitor.save_info(icon_char, text_string, data_dict)
                    self.monitor.last_icon = icon_char
                    self.monitor.last_text = text_string

                sleep_time = update_interval if itunes_is_present else itunes_check_interval
                time.sleep(sleep_time)

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                itunes_is_present = False
                self.monitor._release_com_object()
                time.sleep(itunes_check_interval)

if __name__ == "__main__":
    manager = iTunesSaveInfo(use_ini=False)
    try:
        manager.run()
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Cleaning up...")
        manager.monitor.save_info(CROSS_FONT_CHAR, "iTunes", {"Status": "Not Running"})
        manager.monitor._release_com_object()
        print("Cleanup complete. Exiting.")