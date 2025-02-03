import pytest
from backend.service.location_verification.location_verification import (
    ACCEPTABLE_RADIUS_METERS,
    TARGET_LATITUDE,
    TARGET_LONGITUDE,
    haversine,
    verify_location,
)


def test_haversine_identical_coordinates():
    assert (
        haversine(43.2588581564085, -79.92097591189501, 43.2588581564085, -79.92097591189501) == 0
    )


def test_haversine_known_distance():
    # Coordinates roughly 1km apart
    lat1, lon1 = 43.25, -79.92
    lat2, lon2 = 43.26, -79.92
    distance = haversine(lat1, lon1, lat2, lon2)
    assert 1111.9 < distance < 1112  # Allowing a small margin of error


def test_haversine_antipodal_points():
    # Antipodal point to (0, 0) is (0, 180)
    distance = haversine(0, 0, 0, 180)
    assert 20015086 < distance < 20015088  # Half the Earth's circumference in meters


def test_verify_location_exact_target():
    assert verify_location(TARGET_LATITUDE, TARGET_LONGITUDE, 0) is True


def test_verify_location_within_radius():
    lat, lon = 43.2595, -79.9210  # Slightly different but within 100m radius
    assert verify_location(lat, lon, 0) is True


def test_verify_location_outside_radius():
    lat, lon = 43.2700, -79.9300  # Farther than 100m radius
    assert verify_location(lat, lon, 0) is False


def test_verify_location_on_boundary_with_accuracy():
    lat, lon = 43.2595, -79.9210  # Just at the edge of acceptable range
    distance = haversine(lat, lon, TARGET_LATITUDE, TARGET_LONGITUDE)
    required_accuracy = distance - ACCEPTABLE_RADIUS_METERS
    assert verify_location(lat, lon, required_accuracy) is True


def test_verify_location_just_outside_even_with_accuracy():
    lat, lon = 43.2700, -79.9300
    distance = haversine(lat, lon, TARGET_LATITUDE, TARGET_LONGITUDE)
    accuracy = ACCEPTABLE_RADIUS_METERS - 1  # Slightly less than required to be within range
    assert verify_location(lat, lon, accuracy) is False
