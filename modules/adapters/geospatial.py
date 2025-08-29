"""
Geospatial utilities and parcel analysis helpers.
Stub implementation for future integration with mapping services.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import math


@dataclass
class Coordinates:
    """Geographic coordinates."""
    
    latitude: float
    longitude: float
    
    def __post_init__(self):
        """Validate coordinates."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Invalid longitude: {self.longitude}")
    
    def distance_to(self, other: 'Coordinates') -> float:
        """
        Calculate distance to another coordinate in kilometers.
        Uses Haversine formula.
        """
        return haversine_distance(self.latitude, self.longitude, other.latitude, other.longitude)


@dataclass
class Address:
    """Street address information."""
    
    street: str
    city: str
    region: str  # State, Province, Emirate, etc.
    country: str
    postal_code: Optional[str] = None
    
    def __str__(self) -> str:
        """Format address as string."""
        parts = [self.street, self.city, self.region, self.country]
        if self.postal_code:
            parts.append(self.postal_code)
        return ", ".join(filter(None, parts))


@dataclass
class ParcelInfo:
    """Land parcel information."""
    
    parcel_id: str
    coordinates: Coordinates
    address: Address
    area_sqm: float
    zoning: Optional[str] = None
    ownership_type: Optional[str] = None  # "freehold", "leasehold", etc.
    
    # Derived properties
    municipality: Optional[str] = None
    district: Optional[str] = None
    land_use: Optional[str] = None


@dataclass
class NearbyAmenity:
    """Nearby amenity or point of interest."""
    
    name: str
    category: str  # "school", "hospital", "transport", "retail", etc.
    coordinates: Coordinates
    distance_m: float
    description: Optional[str] = None


class GeospatialProvider(ABC):
    """Abstract base class for geospatial data providers."""
    
    @abstractmethod
    def geocode_address(self, address: str) -> Optional[Coordinates]:
        """Convert address to coordinates."""
        pass
    
    @abstractmethod
    def reverse_geocode(self, coordinates: Coordinates) -> Optional[Address]:
        """Convert coordinates to address."""
        pass
    
    @abstractmethod
    def get_parcel_info(self, coordinates: Coordinates) -> Optional[ParcelInfo]:
        """Get parcel information for coordinates."""
        pass
    
    @abstractmethod
    def find_nearby_amenities(
        self,
        coordinates: Coordinates,
        radius_m: float = 1000,
        categories: Optional[List[str]] = None
    ) -> List[NearbyAmenity]:
        """Find amenities within radius of coordinates."""
        pass


class StubGeospatialProvider(GeospatialProvider):
    """
    Stub implementation of geospatial provider.
    Returns mock data for development and testing.
    """
    
    # Mock coordinates for major cities
    CITY_COORDINATES = {
        "amman": Coordinates(31.9454, 35.9284),
        "dubai": Coordinates(25.2048, 55.2708),
        "abu_dhabi": Coordinates(24.4539, 54.3773),
        "sharjah": Coordinates(25.3463, 55.4209),
        "toronto": Coordinates(43.6532, -79.3832),
        "vancouver": Coordinates(49.2827, -123.1207),
    }
    
    def geocode_address(self, address: str) -> Optional[Coordinates]:
        """Mock geocoding - returns coordinates for known cities."""
        address_lower = address.lower()
        
        for city, coords in self.CITY_COORDINATES.items():
            if city in address_lower:
                # Add small random offset to simulate exact address
                lat_offset = (hash(address) % 1000) / 100000  # ±0.01 degrees
                lng_offset = (hash(address[::-1]) % 1000) / 100000
                
                return Coordinates(
                    latitude=coords.latitude + lat_offset,
                    longitude=coords.longitude + lng_offset
                )
        
        return None
    
    def reverse_geocode(self, coordinates: Coordinates) -> Optional[Address]:
        """Mock reverse geocoding."""
        # Find closest city
        closest_city = None
        min_distance = float('inf')
        
        for city, city_coords in self.CITY_COORDINATES.items():
            distance = coordinates.distance_to(city_coords)
            if distance < min_distance:
                min_distance = distance
                closest_city = city
        
        if closest_city and min_distance < 50:  # Within 50km
            # Mock address based on city
            city_info = {
                "amman": ("Jordan", "Amman Governorate"),
                "dubai": ("UAE", "Dubai"),
                "abu_dhabi": ("UAE", "Abu Dhabi"),
                "sharjah": ("UAE", "Sharjah"),
                "toronto": ("Canada", "Ontario"),
                "vancouver": ("Canada", "British Columbia"),
            }
            
            country, region = city_info.get(closest_city, ("Unknown", "Unknown"))
            
            return Address(
                street=f"{hash(str(coordinates)) % 999 + 1} Mock Street",
                city=closest_city.title(),
                region=region,
                country=country
            )
        
        return None
    
    def get_parcel_info(self, coordinates: Coordinates) -> Optional[ParcelInfo]:
        """Mock parcel information."""
        address = self.reverse_geocode(coordinates)
        if not address:
            return None
        
        # Generate mock parcel data
        parcel_hash = hash(f"{coordinates.latitude}_{coordinates.longitude}")
        
        return ParcelInfo(
            parcel_id=f"PARCEL_{abs(parcel_hash) % 10000:04d}",
            coordinates=coordinates,
            address=address,
            area_sqm=500 + (abs(parcel_hash) % 2000),  # 500-2500 sqm
            zoning=self._mock_zoning(address.city),
            ownership_type="freehold" if abs(parcel_hash) % 2 == 0 else "leasehold",
            municipality=address.city,
            district=f"District {abs(parcel_hash) % 5 + 1}"
        )
    
    def _mock_zoning(self, city: str) -> str:
        """Generate mock zoning classification."""
        city_lower = city.lower()
        
        if "dubai" in city_lower or "abu_dhabi" in city_lower:
            zones = ["G_PLUS_4", "G_PLUS_9", "HIGH_RISE", "MIXED_USE"]
        elif "amman" in city_lower:
            zones = ["R1", "R2", "R3", "C1", "MU1"]
        else:
            zones = ["RESIDENTIAL", "COMMERCIAL", "MIXED_USE"]
        
        return zones[hash(city) % len(zones)]
    
    def find_nearby_amenities(
        self,
        coordinates: Coordinates,
        radius_m: float = 1000,
        categories: Optional[List[str]] = None
    ) -> List[NearbyAmenity]:
        """Mock nearby amenities."""
        if categories is None:
            categories = ["school", "hospital", "transport", "retail", "mosque"]
        
        amenities = []
        
        for i, category in enumerate(categories):
            # Generate mock amenity at random location within radius
            angle = (hash(f"{coordinates}_{category}") % 360) * math.pi / 180
            distance = (hash(f"{category}_{coordinates}") % int(radius_m * 0.8)) + radius_m * 0.1
            
            # Calculate offset coordinates
            lat_offset = (distance / 111000) * math.cos(angle)  # 111km per degree
            lng_offset = (distance / 111000) * math.sin(angle) / math.cos(math.radians(coordinates.latitude))
            
            amenity_coords = Coordinates(
                latitude=coordinates.latitude + lat_offset,
                longitude=coordinates.longitude + lng_offset
            )
            
            amenities.append(NearbyAmenity(
                name=f"Mock {category.title()} {i+1}",
                category=category,
                coordinates=amenity_coords,
                distance_m=distance,
                description=f"Mock {category} facility"
            ))
        
        return amenities


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    
    Args:
        lat1, lon1: Latitude and longitude of first point (degrees)
        lat2, lon2: Latitude and longitude of second point (degrees)
    
    Returns:
        Distance in kilometers
    """
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    earth_radius_km = 6371
    
    return c * earth_radius_km


class GeospatialService:
    """Service for geospatial operations and analysis."""
    
    def __init__(self, provider: Optional[GeospatialProvider] = None):
        """Initialize with geospatial provider."""
        self.provider = provider or StubGeospatialProvider()
    
    def analyze_location(
        self,
        address_or_coordinates,
        analysis_radius_m: float = 1000
    ) -> Dict[str, Any]:
        """
        Comprehensive location analysis.
        
        Args:
            address_or_coordinates: Address string or Coordinates object
            analysis_radius_m: Radius for amenity analysis
            
        Returns:
            Dictionary with location analysis results
        """
        # Get coordinates
        if isinstance(address_or_coordinates, str):
            coordinates = self.provider.geocode_address(address_or_coordinates)
            if not coordinates:
                return {"error": "Could not geocode address"}
        else:
            coordinates = address_or_coordinates
        
        # Get parcel info
        parcel_info = self.provider.get_parcel_info(coordinates)
        
        # Find nearby amenities
        amenities = self.provider.find_nearby_amenities(
            coordinates, analysis_radius_m
        )
        
        # Analyze amenity accessibility
        amenity_analysis = self._analyze_amenities(amenities)
        
        return {
            "coordinates": {
                "latitude": coordinates.latitude,
                "longitude": coordinates.longitude
            },
            "parcel_info": {
                "parcel_id": parcel_info.parcel_id if parcel_info else "Unknown",
                "area_sqm": parcel_info.area_sqm if parcel_info else 0,
                "zoning": parcel_info.zoning if parcel_info else "Unknown",
                "municipality": parcel_info.municipality if parcel_info else "Unknown",
                "address": str(parcel_info.address) if parcel_info else "Unknown"
            },
            "amenities": {
                "total_count": len(amenities),
                "by_category": amenity_analysis["by_category"],
                "accessibility_score": amenity_analysis["accessibility_score"],
                "nearest_amenities": [
                    {
                        "name": a.name,
                        "category": a.category,
                        "distance_m": round(a.distance_m),
                        "walking_minutes": round(a.distance_m / 83)  # ~5km/h walking speed
                    }
                    for a in sorted(amenities, key=lambda x: x.distance_m)[:5]
                ]
            },
            "analysis_radius_m": analysis_radius_m
        }
    
    def _analyze_amenities(self, amenities: List[NearbyAmenity]) -> Dict[str, Any]:
        """Analyze amenity accessibility and distribution."""
        by_category = {}
        for amenity in amenities:
            if amenity.category not in by_category:
                by_category[amenity.category] = []
            by_category[amenity.category].append(amenity.distance_m)
        
        # Calculate accessibility score (0-100)
        score = 0
        max_score = 100
        
        # Points for having essential amenities nearby
        essential_categories = ["school", "hospital", "transport", "retail"]
        for category in essential_categories:
            if category in by_category:
                nearest_distance = min(by_category[category])
                if nearest_distance <= 500:  # Within 500m
                    score += 25
                elif nearest_distance <= 1000:  # Within 1km  
                    score += 15
                elif nearest_distance <= 2000:  # Within 2km
                    score += 5
        
        accessibility_score = min(score, max_score)
        
        return {
            "by_category": {cat: len(distances) for cat, distances in by_category.items()},
            "accessibility_score": accessibility_score
        }
    
    def calculate_commute_analysis(
        self,
        from_coordinates: Coordinates,
        to_addresses: List[str]
    ) -> Dict[str, Any]:
        """
        Mock commute time analysis.
        In production, would integrate with routing APIs.
        """
        commute_times = {}
        
        for address in to_addresses:
            to_coords = self.provider.geocode_address(address)
            if to_coords:
                distance_km = from_coordinates.distance_to(to_coords)
                # Mock commute time (assuming average 30 km/h in city)
                commute_minutes = distance_km * 2  # Conservative estimate
                commute_times[address] = {
                    "distance_km": round(distance_km, 1),
                    "commute_minutes": round(commute_minutes),
                    "commute_category": "short" if commute_minutes <= 30 else "medium" if commute_minutes <= 60 else "long"
                }
        
        return commute_times


# Global service instance
_geospatial_service = None


def get_geospatial_service(provider: Optional[GeospatialProvider] = None) -> GeospatialService:
    """Get global geospatial service instance."""
    global _geospatial_service
    if _geospatial_service is None:
        _geospatial_service = GeospatialService(provider)
    return _geospatial_service


def analyze_location(
    address_or_coordinates,
    analysis_radius_m: float = 1000
) -> Dict[str, Any]:
    """
    Convenience function for location analysis.
    
    Args:
        address_or_coordinates: Address string or Coordinates object
        analysis_radius_m: Analysis radius in meters
        
    Returns:
        Location analysis results
    """
    service = get_geospatial_service()
    return service.analyze_location(address_or_coordinates, analysis_radius_m)