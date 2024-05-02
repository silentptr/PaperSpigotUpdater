from urllib.request import urlopen, urlretrieve
from urllib.error import HTTPError
import json
import hashlib
import os
import subprocess

# =================================
# SET REQUIRED VARS HERE
# =================================

# path to java (doesn't always have to be full path)
java_path = "C:\\Program Files\\Eclipse Adoptium\\jdk-21.0.3.9-hotspot\\bin\\java.exe"
# amount of ram for server in gigabytes
ram_size = 4
# version of minecraft
version = "1.20.6"

# =================================
# =================================
# =================================

url = "https://api.papermc.io/v2/projects/paper/versions/" + version + "/builds/"

try:
    response = urlopen(url)
except HTTPError as err:
    if err.code == 404:
        print("There is not a Paper Spigot release for that version.")
    else:
        print("An error occured while checking version.")
    exit()

data_json = json.loads(response.read())
builds = data_json["builds"]
build_num = -1
build_jar = ""
build_hash = ""

for build in builds:
    if build["build"] > build_num:
        build_num = build["build"]
        build_jar = build["downloads"]["application"]["name"]
        build_hash = build["downloads"]["application"]["sha256"]

if build_num == -1:
    print("No builds available for " + version + ".")
    exit()

print("Latest build for " + version + " is " + build_jar + ".")

files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
    if f.startswith("paper") and f.endswith(".jar") and f != build_jar:
        print("Deleting " + f + "...")
        os.remove(f)

if os.path.exists(build_jar) == False:
    print("Downloading JAR...")
    try:
        urlretrieve(url + "/" + str(build_num) + "/downloads/" + build_jar, build_jar)
    except:
        print("Failed to downloar JAR file.")
        exit()
else:
    print("JAR file already downloaded.")

print("Checking checksum...")

sha = hashlib.sha256()
with open(build_jar, "rb") as file:
    while True:
        data = file.read(4096)
        if len(data) == 0:
            break
        else:
            sha.update(data)
if build_hash != sha.hexdigest():
    print("Checksum does not match.")
    exit()

print("\nDone.")

# run it now

jvm_args = "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true -jar " + build_jar + " --nogui"
full_cmd = '"' + java_path + '"' + " -Xms" + str(ram_size) + "G -Xmx" + str(ram_size) + "G " + jvm_args

if os.name == "nt":
    os.system("CLS")
subprocess.run(full_cmd, shell=True)