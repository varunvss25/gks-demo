from parsers import extract_cfr_codes
def test_codes():
    t = "21 CFR 211.22(b) and 21 CFR 820.70"
    got = extract_cfr_codes(t)
    assert "211.22" in got and "820.70" in got
