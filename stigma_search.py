import os
import sys
import subprocess
from subprocess import CalledProcessError
from multiprocessing import Process
import json
import concurrent.futures
from termcolor import cprint
from time import sleep


# configuration
STIGMA_PATH = "./Stigma.py"
APK_PATH = "./apks" 
DEBUG = True




# uses nodejs to get app id from query
def get_app_id(query):
    try:
        result = subprocess.check_output(["node", "./app_id_script.js", query], text=True)
        result = json.loads(result)
        return result[0]["appId"] if result else None
    except Exception as e:
        cprint(f"Error getting app id for {query}", "red", attrs=["bold"])
        return None

# checks if app already exists in apk directory
def app_exists(app_id):
    if app_id in subprocess.check_output(["ls", f"{APK_PATH}"], text=True):
        cprint(f"{app_id} already exists in {APK_PATH}")
        cprint("Skipping download...", "yellow", attrs=["bold"])
        return True
    else:
        return False
    

def extract_xapk(app_id):
    if os.path.exists(f"{APK_PATH}/{app_id}.xapk"):
        cprint(f"XAPK detected for {app_id}", "yellow", attrs=["bold"])
        cprint("Extracting...", "green", attrs=["bold"])
        subprocess.run(["unzip", f"{APK_PATH}/{app_id}.xapk", "-d", f"{APK_PATH}/{app_id}"], check=True)
        subprocess.run(["mv", "-v", f"{APK_PATH}/{app_id}/{app_id}.apk", f"{APK_PATH}/{app_id}.apk"], check=True)
        subprocess.run(["rm", "-rf", f"{APK_PATH}/{app_id}", f"{APK_PATH}/{app_id}.xapk"], check=True)
    else:
        cprint("No XAPK detected", "green", attrs=["bold"])

# uses apkeep to download apk
def download_apk(app):
    app_id = get_app_id(app)
    if not app_id:
        cprint(f"Error getting app id for {app}", "red", attrs=["bold"])
        return

    cprint(f"Found app: {app}", "green", attrs=["bold"])

    if app_exists(app_id): 
        return

    cprint("Downloading with apkeep...", "green", attrs=["bold"])
    subprocess.run(["apkeep", "-a", app_id, APK_PATH], check=True)

    # check if xapk file
    extract_xapk(app_id)

    cprint(f"Done downloading {app}", "green", attrs=["bold"])

    # start converting
    subprocess.run(["jadx", f"{app_id}.apk"], check=True)
    search(app_id)

def search(app): 

    cprint(f"Started searchin for 'login' keyword", "green", attrs=["bold"])

    subprocess.run(["cd", f"{app}/sources/com"], check=True)

    subprocess.run(["grep", "-R", "'login'"], check=True)





def main():
    # check if ANDROID_HOME is set
    global ANDROID_HOME
    
    try:
        ANDROID_HOME = os.environ["ANDROID_HOME"]
    except KeyError:
        cprint("ANDROID_HOME environment variable not set", "red", attrs=["bold"])
        cprint("Input path to Android SDK (e.g. '~/Android/Sdk'): ", "yellow", attrs=["bold"], end="")
        ANDROID_HOME = input()
        if ANDROID_HOME == "":
            cprint("Defaulting to '~/Android/Sdk'", "green", attrs=["bold"])
            ANDROID_HOME = "~/Android/Sdk"
        else:
            cprint(f"Using {ANDROID_HOME}", "green", attrs=["bold"])


    # set apps
    cprint("Enter the names of the apps you want to download, separated by comma:", "green", attrs=["bold"], end=" ")
    apps = input().split(",")
    apps = [app.strip() for app in apps]

    if not os.path.exists(f"{APK_PATH}"):
        subprocess.run(["mkdir", f"{APK_PATH}"])
        cprint("Created apk directory", "green", attrs=["bold"])

    # if not os.path.exists(f"{MODIFIED_APK_PATH}"):
    #     subprocess.run(["mkdir", f"{MODIFIED_APK_PATH}"])
    #     cprint("Created modified apk directory", "green", attrs=["bold"])

    # for app in apps:
    #     download_apk(app)

        

    apks = os.listdir(APK_PATH)








    # # create a ProcessPoolExecutor (for parallel processing)
    # with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    #     executor.map(process_apk, apks)

    # modified_apks = os.listdir(MODIFIED_APK_PATH)

    # # check if "stigma" avd exists with avdmanager
    # if "stigma" not in subprocess.check_output([f"{ANDROID_HOME}/cmdline-tools/latest/bin/avdmanager", "list", "avd"], text=True):
    #     cprint("Stigma avd not found, creating...", "yellow", attrs=["bold"])
    #     subprocess.run([f"{ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager", "system-images;android-29;google_apis;x86"], check=True)
    #     subprocess.run([f"{ANDROID_HOME}/cmdline-tools/latest/bin/avdmanager", "create", "avd", "-n", "stigma", "-k", "system-images;android-29;google_apis;x86", "-d", "pixel_3a"], check=True)

    # try:
    #     for apk in modified_apks:
    #         emulate(apk)
    # except Exception as e:
    #     cprint(e, "red", attrs=["bold"])



    # delete_apks()
    cprint("Done", "green", attrs=["bold"])
    sys.exit(0)

if __name__ == "__main__":
    main()