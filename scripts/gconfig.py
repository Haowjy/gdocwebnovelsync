import json
import os
from pathlib import Path

# todo: maybe switch to mongodb...

parent = Path(".")
config_path = parent / Path("config.json")

with config_path.open(mode='r') as file:
    config = json.load(file)

def getBrowser():
    return config["settings"]["browser"]

def newStory(series_name, royalroad=None, scribblehub=None, webnovel=None, wattpad=None):
    new_local_series_id = len(config["stories"])
    config["stories"].append({
        "series_name": series_name,
        "local_series_id": new_local_series_id,
        "general": {
        },
        "chapters":[]
    })

    for platformKey, platformValue in {"royalroad":royalroad, "scribblehub":scribblehub, "webnovel":webnovel, "wattpad":wattpad}.items():
        if(platformValue is not None):
            config["stories"][new_local_series_id]["general"][platformKey] = {"series_id": str(platformValue)}
    # print(config)
    with config_path.open(mode='w') as file:
        json.dump(config, file, indent=4)

def registerChapterLocally(local_series_id, filename, royalroad=None, scribblehub=None, webnovel=None, wattpad=None):
    "returns the local chapter id"
    local_chapter_id = len(config["stories"][local_series_id]['chapters'])
    config["stories"][local_series_id]['chapters'].append({"local_file":filename})
    for platformKey, platformValue in {"royalroad":royalroad, "scribblehub":scribblehub, "webnovel":webnovel, "wattpad":wattpad}.items():
        if(platformValue is not None):
            try:
                config["stories"][local_series_id]["chapters"][local_chapter_id][platformKey] = platformValue
            except:
                print(f"WARNING: Something went wrong with {platformKey}")
    with config_path.open(mode='w') as file:
        json.dump(config, file, indent=4)
    return local_chapter_id


def getStoryInfo(story_input):
    try:
        local_series_id = int(story_input)
        return config["stories"][local_series_id]
    except:
        for story_json in config["stories"]:
            if story_json.lower().strip() == story_input.lower().strip():
                return story_json
        raise Exception(f"Invalid Story {story_input}")
    # print(local_series_id)
    