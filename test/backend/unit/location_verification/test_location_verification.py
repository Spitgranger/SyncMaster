import pytest
from backend.service.location_verification.location_verification import (
    haversine,
    verify_location,
)

from ..constants import TEST_SITE_ID


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


def test_verify_location_within_radius(database_with_site):
    lat, lon = 43.2595, -79.9210  # Slightly different but within 100m radius
    assert verify_location(lat, lon, 0, TEST_SITE_ID) is True


def test_verify_location_outside_radius(database_with_site):
    lat, lon = 43.2700, -79.9300  # Farther than 100m radius
    assert verify_location(lat, lon, 0, TEST_SITE_ID) is False


def test_verify_location_on_boundary_with_accuracy(database_with_site):
    lat, lon = 43.2598, -79.9210  # Just at the edge of acceptable range
    assert verify_location(lat, lon, 5, TEST_SITE_ID) is True


def test_verify_location_just_outside_even_with_accuracy(database_with_site):
    lat, lon = 443.2598, -79.9210
    assert verify_location(lat, lon, 4, TEST_SITE_ID) is False
