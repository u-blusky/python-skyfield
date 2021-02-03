from skyfield import framelib
from skyfield.api import Topos, load, wgs84
from skyfield.constants import ERAD
from skyfield.positionlib import Geocentric

def test_radec_and_altaz_angles_and_rates():
    # HORIZONS test data in Skyfield repository: authorities/radec-altaz-rates
    ts = load.timescale()
    t = ts.utc(2021, 2, 3)
    top = wgs84.latlon(35.1844866, 248.347300, elevation_m=2106.9128)
    planets = load('de421.bsp')
    a = (planets['earth'] + top).at(t).observe(planets['mars']).apparent()
    # ra, dec, distance = a.radec('date')
    # print(ra._degrees)
    # print(dec._degrees)
    frame = framelib.true_equator_and_equinox_of_date
    dec, ra, distance = a.frame_latlon(frame)
    arcseconds = 3600.0
    assert abs((ra.degrees - 40.75836) * arcseconds) < 0.04
    assert abs((dec.degrees - 17.16791) * arcseconds) < 0.005
    # 2021-Feb-03 00:00 *    40.75836  17.16791 75.15571  25.61352 131.8839  65.2758   663.55    548.66

def test_frame_round_trip():
    # Does a frame's rotation and twist get applied in the right
    # directions?  Let's test whether the position and velocity of an
    # ITRS vector (ERAD,0,0) are restored to the proper orientation.
    top = Topos(latitude_degrees=0, longitude_degrees=0)
    ts = load.timescale()
    t = ts.utc(2020, 11, 27, 15, 34)  # Arbitrary time; LST ~= 20.03.
    p = top.at(t)

    r = p.frame_xyz(framelib.itrs)
    assert max(abs(r.m - [ERAD, 0, 0])) < 4e-8 # meters

    r, v = p.frame_xyz_and_velocity(framelib.itrs)
    assert max(abs(r.m - [ERAD, 0, 0])) < 4e-8 # meters
    assert max(abs(v.km_per_s)) < 3e-15 # km/s

def test_from_frame_method():
    ts = load.timescale()
    t = ts.utc(2020, 11, 27, 15, 34)
    g1 = Geocentric([1,2,3], [4,5,6], t=t)
    r, v = g1.frame_xyz_and_velocity(framelib.itrs) # which we trust: see above

    g2 = Geocentric.from_time_and_frame_vectors(t, framelib.itrs, r, v)
    assert max(abs(g2.position.au - [1,2,3])) < 2e-14
    assert max(abs(g2.velocity.au_per_d - [4,5,6])) < 3e-14

    # Make sure original vectors were not harmed (for example, by "+=").
    assert list(g1.position.au) == [1,2,3]
    assert list(g1.velocity.au_per_d) == [4,5,6]

def test_frame_without_spin():
    ts = load.timescale()
    t = ts.utc(2020, 11, 27, 15, 34)
    g = Geocentric([1,2,3], [4,5,6], t=t)

    # Simply test whether "None" spin raises an exception in either direction.
    f = framelib.true_equator_and_equinox_of_date
    r, v = g.frame_xyz_and_velocity(f)
    Geocentric.from_time_and_frame_vectors(t, f, r, v)

def test_tirs_at_least_runs():
    # TODO: find an external source for a TIRS vector to test against.
    # For now, just make sure it doesn't raise an exception.
    ts = load.timescale()
    t = ts.utc(2020, 11, 27, 15, 34)
    g = Geocentric([1,2,3], [4,5,6], t=t)
    g.frame_xyz_and_velocity(framelib.tirs)
