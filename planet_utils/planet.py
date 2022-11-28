import rasterio
import numpy as np
from xml.dom import minidom
from skimage.exposure import equalize_hist
import pandas as pd

def check_xmlfile_type(xml_filename):
    """_summary_

    Args:
        xml_filename (_type_): _description_

    Returns:
        _type_: _description_
    """
    if type(xml_filename).__name__ == "Document":
        xml_filename = xml_filename
    elif type(xml_filename).__name__ == "str":
        xml_filename = minidom.parse(xml_filename)
    else:
        IOError("Wrong type of input data")
    return xml_filename


def get_coeffs(xml_filename):
    """_summary_

    Args:
        xml_filename (_type_): _description_

    Returns:
        _type_: _description_
    """
    xml_filename = (
        xml_filename
        if type(xml_filename).__name__ == "Document"
        else minidom.parse(xml_filename)
    )
    nodes = xml_filename.getElementsByTagName("ps:bandSpecificMetadata")
    coeffs = {}
    for node in nodes:
        bn = node.getElementsByTagName("ps:bandNumber")[0].firstChild.data
        if bn in ["1", "2", "3", "4"]:
            i = int(bn)
            value = node.getElementsByTagName("ps:reflectanceCoefficient")[
                0
            ].firstChild.data
            coeffs[i] = float(value)
    return coeffs


def get_location(xml_filename):
    """_summary_

    Args:
        xml_filename (_type_): _description_

    Returns:
        _type_: _description_
    """
    xml_filename = (
        xml_filename
        if type(xml_filename).__name__ == "Document"
        else minidom.parse(xml_filename)
    )
    location = xml_filename.getElementsByTagName("ps:geographicLocation")

    def extract_element(corner):
        return [
            location[0]
            .getElementsByTagName("ps:" + corner)[0]
            .getElementsByTagName("ps:" + loc)[0]
            .firstChild.data
            for loc in np.array(("longitude", "latitude"))
        ]

    tl = extract_element("topLeft")
    tr = extract_element("topRight")
    bl = extract_element("bottomLeft")
    br = extract_element("bottomRight")
    bounding_boxes = np.array(
        [(float(values[0]), float(values[1]))
         for values in np.array((tl, tr, bl, br))]
    )
    return pd.DataFrame(
        bounding_boxes, columns=["lon", "lat"], index=["TL", "TR", "BL", "BR"]
    )


def equalize(data, factor=2):
    """_summary_

    Args:
        data (_type_): _description_
        factor (int, optional): _description_. Defaults to 2.

    Returns:
        _type_: _description_
    """
    imagery = np.interp(data, (0, 1), (0, 255))
    imagery = equalize_hist(imagery)
    return imagery


def get_reflectance(filename, coeff, factor=5):
    with rasterio.open(filename) as src:
        band_blue_radiance = src.read(1)[::factor, ::factor]
    with rasterio.open(filename) as src:
        band_green_radiance = src.read(2)[::factor, ::factor]
    with rasterio.open(filename) as src:
        band_red_radiance = src.read(3)[::factor, ::factor]
    with rasterio.open(filename) as src:
        band_nir_radiance = src.read(4)[::factor, ::factor]
    return (
        band_blue_radiance * coeff[1],
        band_green_radiance * coeff[2],
        band_red_radiance * coeff[3],
        band_nir_radiance * coeff[4],
    )


def get_reflectance1(filename, coeff, factor=5):
    """_summary_

    Args:
        filename (_type_): _description_
        coeff (_type_): _description_
        factor (int, optional): _description_. Defaults to 5.

    Returns:
        _type_: _description_
    """
    #    print(
    #        f"{b.FAIL} WILL BE DEPRICIATED. USE get_reflectance TO AVOID THIS ERROR {b.RESET}"
    #    )
    with rasterio.open(filename) as src:
        band_blue_radiance = src.read(1)[::factor, ::factor]
    with rasterio.open(filename) as src:
        band_green_radiance = src.read(2)[::factor, ::factor]
    with rasterio.open(filename) as src:
        band_red_radiance = src.read(3)[::factor, ::factor]
    with rasterio.open(filename) as src:
        band_nir_radiance = src.read(4)[::factor, ::factor]
    return (
        band_blue_radiance * coeff[1],
        band_green_radiance * coeff[2],
        band_red_radiance * coeff[3],
        band_nir_radiance * coeff[4],
    )


def get_DN(filename):
    """_summary_

    Args:
        filename (_type_): _description_

    Returns:
        _type_: _description_
    """
    with rasterio.open(filename) as src:
        band_blue_radiance = src.read(1)
    with rasterio.open(filename) as src:
        band_green_radiance = src.read(2)
    with rasterio.open(filename) as src:
        band_red_radiance = src.read(3)
    with rasterio.open(filename) as src:
        band_nir_radiance = src.read(4)
    return band_blue_radiance, band_green_radiance, band_red_radiance, band_nir_radiance


def get_pixel_size(filename):
    """_summary_

    Args:
        filename (_type_): _description_

    Returns:
        _type_: _description_
    """
    with rasterio.open(filename) as src:
        band_blue_radiance = src.read(1)
    return band_blue_radiance.shape
