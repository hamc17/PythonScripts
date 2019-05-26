from helper import *
import os


"""
Script to convert mp4 or wma/wmv files to mp3
Copies existing tags where possible
"""

if __name__ == "__main__":
    try:
        with open("extension_list.txt", "rt") as el:
            extension_list = [l.strip() for l in el.readlines()]
        print("Remove existing files with extension in "
              "{0} after conversion? y/n".format(extension_list))
        while True:
            remove = input()
            if remove == "y":
                remove = True
                break
            if remove == "n":
                remove = False
                break
            print("y/n")
        files_plus_ext = getFilesAndExtensions()
        for f in files_plus_ext:
            res = chdirIfMatch(f, extension_list)
            if res:
                file_path, file_ext = res
                mp3_file_path = convertToMP3(file_path, file_ext)
                if mp3_file_path:
                    addTagsToMP3(file_path, mp3_file_path, file_ext)
                if remove:
                    print("Removing existing file at: {0}".format(file_path))
                    os.remove(file_path)
    except FileNotFoundError:
        print("Supply a list of media file extensions,"
              "one per line e.g. \nm4a\nwma")
