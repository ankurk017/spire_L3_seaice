# This script is to plot rgb (not as lon-lat on XY axis) on numeric axis and helps to write manually the pixel locations in a text file. This text file for the training dataset is being saved (manually) in the same folder as that of the dataset (/nas/rstor/akumar/USA/PhD/Planet_Work/PSScenes/Level0/4files_by_classes/Aerosols)
# files

import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from xml.dom import minidom

import glob
import pandas as pd
import datetime as dt
import os
import datetime
from os.path import exists
import planet_utils.planet as pl
import progressbar
import xmltodict

# import planet as pl


class b:
    OK = "\033[92m"  # GREEN
    WARNING = "\033[96m"  # YELLOW
    FAIL = "\033[91m"  # RED
    RESET = "\033[0m"  # RESET COLOR


def mouse_event(event):
    print("x: {} and y: {}".format(np.round(event.xdata), np.round(event.ydata)))
    # global ix, iy
    ix, iy = event.xdata, event.ydata

    # global coords
    coords.append((ix, iy))
    pd.DataFrame(coords).to_csv("test_events.txt")
    print(coords)
    print(value_to_print)
    return coords


def ask_input_from_user(class_ids):
    input_for_training = input(
        f"{b.OK}  Enter the class code: 1: Aerosols, 2: Clouds, 3: Urban, 4: Vegetation {b.RESET} \n ENTER CODE:    "
    )
    check_input = np.logical_and(
        int(input_for_training) >= 1, int(input_for_training) <= 4
    )
    if check_input:
        print(f"You selected {class_ids[int(input_for_training)]}")
    else:
        print(f"{b.FAIL} You entered the wrong input.{b.RESET}")
        raise TypeError("Input from 1 to 4 is allowed")
    return input_for_training


def coords_to_text(
    coords,
    reflectance=None,
    planet_filename=None,
    output_filename="test_train.txt",
    reset=False,
):
    # Writing coords to training sheet
    print(len(coords))
    if len(coords) <= 1:
        raise IOError("No coords available to write.")
    else:
        None

    def check_coords(check_diff):
        return np.logical_and(check_diff > 0, check_diff < 1000)

    print(
        f"{b.FAIL} ============== Error in input reflectance. ============="
    ) if reflectance is None else None
    coords = np.array(coords)
    class_names = coords[:, -1]
    coords = coords[:, :-1].astype(float)
    coordinates = np.reshape(np.round(coords), (-1, 4))
    xy_check = np.logical_and(
        check_coords(coordinates[:, 1] - coordinates[:, 3]),
        check_coords(coordinates[:, 2] - coordinates[:, 0]),
    )

    print(
        f"{b.FAIL} Discarding {np.where(~xy_check)[0].shape[0]} out of {coordinates.shape[0]} input training samples {b.RESET}"
    )

    coordinates_check = coordinates[xy_check, :]
    coords_pd = pd.DataFrame(coordinates_check, columns=[
                             "x1", "y1", "x2", "y2"])

    # print(f"{b.OK} Below are the training pixels being written to training text file: {output_filename} {b.RESET}")
    # print(coordinates_check)

    training_pixels = np.sum(
        np.multiply(
            coordinates_check[:, 2] - coordinates_check[:, 0],
            coordinates_check[:, 1] - coordinates_check[:, 3],
        )
    )
    print(
        f"Number of training pixels selected: {b.FAIL}{training_pixels.astype(int)}{b.RESET}"
    )

    coordinates_check[:, 1] = size[0] - coordinates_check[:, 1]
    coordinates_check[:, 3] = size[0] - coordinates_check[:, 3]

    # coords_pd.insert(4, "Class", [class_ids[int(input_for_training)]]*coords_pd.shape[0], False)
    print("FROM BACKEND")
    coords_pd.insert(4, "Class", np.array(class_names)[::2][xy_check], False)
    coords_pd.insert(5, "Times", dt.datetime.now().strftime("%Y%m%d_%H%M"))
    if reset:
        if exists(output_filename):
            # print('### !!!!! DELETING PREVIOUS TRAINING FILE !!!!! ####')
            current_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
            if len(coords) >= 2:
                os.system(
                    f"mv {output_filename} {output_filename}_{current_time}")
                print(
                    f"{b.WARNING}### !!!!! MOVED OLD TRAINING FILE TO {output_filename}.{current_time} !!!!! ####{b.RESET}"
                )
                coords_pd.to_csv(output_filename, index=False)
            else:
                print(
                    "You have not selected any training datasets. HAVE NOT CHANGED ANYTHING !!!"
                )

        else:
            print("? Starting a new training file .")
            coords_pd.to_csv(output_filename, index=False)
    else:
        print("## APPENDING TRAINING DATASET")
        coords_pd.to_csv(output_filename, index=False, mode="a", header=False)
    print(f"{b.OK}New training file is available here: {output_filename}{b.RESET}")
    print("=================================================|")
    write_reflectance_to_text(reflectance, output_filename)
    write_metadata_to_text(planet_filename, output_filename)
    return coords_pd


def write_metadata_to_text(input_filename, output_filename):
    prefix = input_filename.replace("_clip.tif", "")
    xmldoc = prefix + "_metadata_clip.xml"
    with open(xmldoc) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())

    xml_metadata = data_dict["ps:EarthObservation"]["gml:using"][
        "eop:EarthObservationEquipment"
    ]["eop:acquisitionParameters"]["ps:Acquisition"]

    def get_metadata(metadata):
        return float(xml_metadata[metadata]["#text"])

    incidenceAngle = get_metadata("eop:incidenceAngle")
    illuminationAzimuthAngle = get_metadata("opt:illuminationAzimuthAngle")
    illuminationElevationAngle = get_metadata("opt:illuminationElevationAngle")
    azimuthAngle = get_metadata("ps:azimuthAngle")
    spaceCraftViewAngle = get_metadata("ps:spaceCraftViewAngle")
    acquisitionHour = int(
        xml_metadata["ps:acquisitionDateTime"].split("T")[1][:2])
    metadata = pd.DataFrame(
        [
            incidenceAngle,
            illuminationAzimuthAngle,
            illuminationElevationAngle,
            azimuthAngle,
            spaceCraftViewAngle,
            acquisitionHour,
        ]
    ).T
    metadata.columns = [
        "incidenceAngle",
        "illuminationAzimuthAngle",
        "illuminationElevationAngle",
        "azimuthAngle",
        "spaceCraftViewAngle",
        "acquisitionHour",
    ]
    output_metadata_filename = ".".join(
        output_filename.split(".")[:-1]) + ".metadata"
    metadata.to_csv(output_metadata_filename, index=False)
    print(
        f"{b.OK}New Metadata file is available here: {output_metadata_filename}{b.RESET}"
    )


def write_reflectance_to_text(reflectance, training_filename=None):
    training_file = pd.read_csv(training_filename)
    pixel_id = training_file[["x1", "y1", "x2", "y2"]].values
    pixel_id = pixel_id.astype(int)
    print("Write from reflectance to text code")
    bgrnc = []  # blue-green-red-nir-coordinates
    for fig_id in progressbar.progressbar(range(pixel_id.shape[0])):
        blue_ref = slice_planet_by_train_coords(
            reflectance["blue"], pixel_id[fig_id, :]
        ).ravel()
        green_ref = slice_planet_by_train_coords(
            reflectance["green"], pixel_id[fig_id, :]
        ).ravel()
        red_ref = slice_planet_by_train_coords(
            reflectance["red"], pixel_id[fig_id, :]
        ).ravel()
        nir_ref = slice_planet_by_train_coords(
            reflectance["nir"], pixel_id[fig_id, :]
        ).ravel()
        class_ref = [training_file["Class"][fig_id]] * green_ref.shape[0]
        bgrnc.append(
            np.stack((blue_ref, green_ref, red_ref, nir_ref, class_ref)).T)
    output_ref_filename = ".".join(
        training_filename.split(".")[:-1]) + ".train_ref"
    reflectance_training = pd.DataFrame(np.vstack(bgrnc))
    reflectance_training.columns = ["blue", "green", "red", "nir", "class"]
    reflectance_training.to_csv(output_ref_filename, index=False)
    print(
        f"{b.OK}New training reflectance file is available here: {output_ref_filename}{b.RESET}"
    )


def get_rgb(input_filename, factor=5):
    blue, green, red, nir, location = get_reflectance_from_planet(
        input_filename, factor=factor
    )
    rgb = np.stack((pl.equalize(red), pl.equalize(
        green), pl.equalize(blue)), axis=2)
    size = pl.get_pixel_size(input_filename)
    reflectance = {"blue": blue, "green": green, "red": red, "nir": nir}
    return rgb, size, reflectance, location


def get_reflectance_from_planet(input_filename, factor=5):
    print(rf"{b.OK} === Factor of {factor} === {b.RESET}")
    prefix = input_filename.replace("_clip.tif", "")
    pfile = prefix + "_clip.tif"
    xmldoc = minidom.parse(prefix + "_metadata_clip.xml")

    coeff = pl.get_coeffs(xmldoc)
    location = pl.get_location(xmldoc)
    blue, green, red, nir = pl.get_reflectance(pfile, coeff, factor=factor)
    return blue, green, red, nir, location


def check_exist(*args, **kwargs):
    if not exists(args[0]):
        raise IOError("{:s} does not exist.".format(args[0]))
    return None


def plot_planet_rgb(axs, planet_file_name):
    global coords, size

    rgb, size, reflectance, location = get_rgb(planet_file_name, factor=1)
    print(location)
    coords = []

    axs.imshow(rgb[::5, ::5, :], extent=(0, size[1], 0, size[0]))
    # axs.set_xticks([0, size[1]/2, size[1]])
    # axs.set_yticks([0, size[0]/2, size[0]])
    rgb = None
    axs.set_title(rf"Select training samples ", color="red")
    return reflectance


def slice_planet_by_train_coords(bands, trains_coords):
    return (
        bands[
            trains_coords[1]: trains_coords[3], trains_coords[0]: trains_coords[2], :
        ]
        if len(bands.shape) == 3
        else bands[
            trains_coords[1]: trains_coords[3], trains_coords[0]: trains_coords[2]
        ]
    )
