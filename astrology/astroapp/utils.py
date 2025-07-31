import swisseph as swe
import datetime
import pytz

# Set the path to your ephemeris files
swe.set_ephe_path('/tmp')  # or the actual path on your system

def get_zodiac_sign_and_ascendant(dt, latitude, longitude):
    dt_utc = dt.astimezone(pytz.UTC)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)

    flag = swe.FLG_SWIEPH | swe.FLG_SPEED
    planet_pos = swe.calc_ut(jd, swe.SUN, flag)[0]
    sun_longitude = planet_pos[0]

    zodiac_signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    sun_sign_index = int(sun_longitude // 30)
    sun_sign = zodiac_signs[sun_sign_index]

    sidereal_time = swe.sidtime(jd)
    lon_for_calc = -longitude
    houses, ascmc = swe.houses(jd, latitude, lon_for_calc, b'A')
    ascendant_long = ascmc[0]
    asc_sign_index = int(ascendant_long // 30)
    ascendant_sign = zodiac_signs[asc_sign_index]

    return sun_sign, ascendant_sign
