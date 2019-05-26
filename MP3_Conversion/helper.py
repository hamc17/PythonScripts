import os
import glob
import filetype
import mutagen
import json
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4
from mutagen.asf import ASFTags
from mutagen.asf import ASF

EXTENSION_MAPPING = None
CONVERSION_TABLE = None


def setExtensionMapping():
    global EXTENSION_MAPPING
    global CONVERSION_TABLE
    with open("./extension_mapping.json") as json_file:
        m = json.load(json_file)
        EXTENSION_MAPPING = {}
        for e in m.items():
            k, v = e
            for j in v.items():
                kj, vj = j
                EXTENSION_MAPPING[vj] = k
        CONVERSION_TABLE = dict(m)


def getFilesAndExtensions():
    """Walks current directory, gets list of media files and extensions

    Returns:
        list -- List of tuples, file path and file extension
    """

    paths = os.walk(os.curdir)
    files_plus_ext = []
    print("Retrieving files and their extensions")
    for p in paths:
        files = ["{0}/{1}".format(
            os.path.abspath(p[0]), file_name) for file_name in p[2]]
        for file_name in p[2]:
            file_abs_path = "{0}/{1}".format(os.path.abspath(p[0]), file_name)
            file_ext = filetype.guess(file_abs_path)
            if file_ext is not None:
                files_plus_ext.append((file_abs_path, file_ext.extension))
    return files_plus_ext


def chdirIfMatch(f, extension_list):
    """Changes to the directory of the given file if the extension
       is in the extension list

    Arguments:
        f {tuple} -- The file path and file extension
        extension_list {list} -- The valid extensions

    Returns:
        tuple -- If the file matches the extension list
    """

    print("Current file: {0}".format(f[0]))
    file_path, file_ext = f
    if file_ext in extension_list:
        print("Extension matches: {0}".format(file_ext))
        file_dir = os.path.abspath(os.path.join(file_path, os.pardir))
        if os.curdir != file_dir:
            os.chdir(file_dir)
        return (file_path, file_ext)
    else:
        return


def convertToMP3(file_path, file_ext):
    """Converts the given file to mp3

    Arguments:
        file_path {str} -- Absolute path to the file
        file_ext {str} -- The file extension

    Returns:
        str -- The resulting mp3 path if it doesn't already exist
    """

    mp3_filename = os.path.splitext(
        os.path.basename(file_path))[0] + ".mp3"
    if not os.path.isfile(mp3_filename):
        AudioSegment.from_file(file_path).export(mp3_filename, format="mp3")
        print("Converted {0} from {1} to mp3".format(file_path, file_ext))
        return mp3_filename


def addTagsToMP3(file_path, mp3_file_path, file_ext):
    """Gets the existing tags from the mp4 file and saves them to the mp3

    Arguments:
        mp4_file_path {str} -- Path for MP4 file
        mp3_file_path {str} -- Path for MP3 file
    """

    original_file_tags = None
    mp3_tags = EasyID3(mp3_file_path)
    if file_ext == "m4a":
        original_file_tags = EasyMP4(file_path)
        for k, v in original_file_tags.items():
            found_tag = EXTENSION_MAPPING.get(k, None)
            if found_tag is not None:
                resulting_tag = CONVERSION_TABLE[found_tag]["mp3"]
                mp3_tags[resulting_tag] = [v]
                print("Added tag {0}:{1} to mp3 {2}".format(
                        resulting_tag, v, mp3_file_path))
    elif file_ext in ["wma", "wmv"]:
        original_file_tags = ASF(file_path).tags
        for k, v in original_file_tags.items():
            found_tag = EXTENSION_MAPPING.get(k, None)
            if found_tag is not None:
                resulting_tag = CONVERSION_TABLE[found_tag]["mp3"]
                if file_ext in["wma", "wmv"]:
                    if resulting_tag == "composer":
                        if mp3_tags.get(resulting_tag, None):
                            mp3_tags[resulting_tag] = ["{0}, {1}"].format(
                                mp3_tags[resulting_tag][0], v[0].value)
                        else:
                            mp3_tags[resulting_tag] = [v[0].value]
                    else:
                        mp3_tags[resulting_tag] = [v[0].value]
                print("Added tag {0}:{1} to mp3 {2}".format(
                        resulting_tag, v[0], mp3_file_path))
    else:
        return
    mp3_tags.save(mp3_file_path)
    print("MP3 tags saved to {0}".format(mp3_file_path))

setExtensionMapping()
