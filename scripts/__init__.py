"""Helper functions for hotfixing fonts"""
import os
import shutil
from datetime import datetime as date
from fontTools.ttLib import TTFont, newTable

__all__ = ["update_attribs", "update_names",
        "disable_oblique_bits", "update_font_version", "update_gasp", "mkdir",
        "update_psname_and_fullname", "android_and_cros_vert_metrics",]


def update_psname_and_fullname(ttfont, include_year=False):
    family_name = ttfont['name'].getName(16, 3, 1, 1033) or \
                  ttfont['name'].getName(1, 3, 1, 1033)
    style_name = ttfont['name'].getName(17, 3, 1, 1033) or \
                 ttfont['name'].getName(2, 3, 1, 1033)
    full_name = family_name.toUnicode() + " " + style_name.toUnicode()
    if full_name == "Roboto Regular":
        full_name = "Roboto"
    if full_name == "Roboto Condensed Regular":
        full_name = "Roboto Condensed"
    if include_year:
        year = date.today().year
        unique_id = f"Google:{full_name}:{year}"
        ttfont['name'].setName(unique_id, 3,3,1,1033)
    else:
        ttfont['name'].setName(full_name, 3,3,1,1033)
    ttfont['name'].setName(full_name, 4,3,1,1033)


def update_attribs(font, **kwargs):
    for table in font.keys():
        for k in kwargs:
            if hasattr(font[table], k):
                print(f"Setting {k} to {kwargs[k]}")
                setattr(font[table], k, kwargs[k])


def update_names(font, rm_private=True, **kwargs):
    nametable = font["name"]
    for k in kwargs:
        print(f"Setting {k} to {kwargs[k]}")
        nametable.setName(kwargs[k], *tuple(map(int, k.split(","))))

    if not rm_private:
        return
    for name_id in range(256, 400):
        font['name'].removeNames(name_id)


def disable_oblique_bits(font):
    if font['OS/2'].fsSelection & 512 == 512:
        font['OS/2'].fsSelection ^= 512


def enable_bold_bits(font):
    # Enable Bold bits for Black styles
    if "Black" in font_path and "fvar" not in font:
        if "Italic" in font_path:
            font["OS/2"].fsSelection |= 32
        else:
            font["OS/2"].fsSelection ^= 64 | 32
        font["head"].macStyle |= 1


def update_font_version(font):
    version_record = 'Version %s; %d' % (round(font['head'].fontRevision, 3), date.today().year)
    font['name'].setName(version_record, 5, 3, 1, 1033)


def update_gasp(font, gasp_ranges):
    gasp_tbl = newTable("gasp")
    gasp_tbl.gaspRange = gasp_ranges
    font['gasp'] = gasp_tbl


def mkdir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.mkdir(path)


android_and_cros_vert_metrics = {
    "ascent": 1900,
    "descent": -500,
    "lineGap": 0,
    "sTypoAscender": 2146,
    "sTypoDescender": -555,
    "sTypoLineGap": 0,
    "usWinAscent": 2146,
    "usWinDescent": 555,
    "yMin": -555,
    "yMax": 2163,
}

