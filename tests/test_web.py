from fontbakery.callable import check
from fontbakery.callable import condition
from fontbakery.checkrunner import Section, PASS, FAIL, WARN
from fontbakery.fonts_profile import profile_factory

# profile_imports = ('fontbakery.profiles.universal',)
profile = profile_factory(default_section=Section("Roboto web v3"))

ROBOTO_PROFILE_CHECKS = [
    "com.roboto.fonts/check/vertical_metrics",
    "com.roboto.fonts/check/oblique_bits_not_set",
    "com.roboto.fonts/check/unique_id",
    "com.roboto.fonts/check/hinting",
]


@check(
    id="com.roboto.fonts/check/vertical_metrics",
)
def com_roboto_fonts_check_vertical_metrics(ttFont):
    """Check vertical metrics are correct"""
    failed = []
    expected = {
        # android requires this, and web fonts expect this
        ("head", "yMin"): -555,
        ("head", "yMax"): 2163,
        # test hhea ascent, descent, and lineGap to be equal to Roboto v1 values
        ("hhea", "descent"): -500,
        ("hhea", "ascent"): 1900,
        ("hhea", "lineGap"): 0,
        # test OS/2 vertical metrics to be equal to old OS/2 win values
        # since fsSelection bit 7 is now enabled
        ("OS/2", "sTypoDescender"): -512,
        ("OS/2", "sTypoAscender"): 1536,
        ("OS/2", "sTypoLineGap"): 102,
        ("OS/2", "usWinDescent"): 512,
        ("OS/2", "usWinAscent"): 1946,
    }
    for (table, k), v in expected.items():
        font_val = getattr(ttFont[table], k)
        if font_val != v:
            failed.append((table, k, v, font_val))
    if not failed:
        yield PASS, "Fonts have correct vertical metrics"
    else:
        msg = "\n".join(
            [
                f"- {tbl}.{k} is {font_val} it should be {v}"
                for tbl, k, v, font_val in failed
            ]
        )
        yield FAIL, f"Fonts have incorrect vertical metrics:\n{msg}"


@check(
    id="com.roboto.fonts/check/oblique_bits_not_set",
)
def com_roboto_fonts_check_oblique_bits_not_set(ttFont):
    """Check oblique bits are not set in fonts"""
    if ttFont['OS/2'].fsSelection & (1 << 9) != 0:
        yield FAIL, "fsSelection bit 9 (Oblique) must not be enabled"
    else:
        yield PASS, "fsSelection bit 9 is disabled"


@check(
    id="com.roboto.fonts/check/unique_id",
)
def com_roboto_fonts_check_unique_id(ttFont):
    """Check uniqueid is correct"""
    pass
    # Should be <familyname> <style> or just <familyname> for Reg fonts


@check(
    id="com.roboto.fonts/check/hinting",
)
def com_roboto_fonts_check_hinting(ttFont):
    """Check glyphs have hinting"""
    missing_hints = []
    for glyph_name in ttFont.getGlyphOrder():
        glyph = ttFont['glyf'][glyph_name]
        if glyph.numberOfContours <= 0:
            continue
        if len(glyph.program.bytecode) <= 0:
            missing_hints.append(glyph_name)
    if missing_hints:
        yield FAIL, f"Following glyphs are missing hinting {missing_hints}"
    else:
        yield PASS, "All glyphs are hinted"

profile.auto_register(globals())
profile.test_expected_checks(ROBOTO_PROFILE_CHECKS, exclusive=True)
