# -*- coding: utf-8 -*-
"""
🌍 KLOUD GLOBAL DATA SOURCES - MASTER INDEX
===============================================
5000+ Free Open Data Sources from 200+ Countries

This is the master file that combines all regional data sources
into a single unified interface for the Kloud platform.

MODULES INCLUDED:
- europe_sources.py                  (1000+ sources - 20 West European countries)
- eastern_europe_balkans_sources.py  (600+ sources - 19 Eastern European countries)
- americas_sources.py                (600+ sources - 16 American countries)
- caribbean_central_america_sources.py (300+ sources - 28 Caribbean & Central American countries)
- asia_china_sources.py              (800+ sources - 7 East Asian countries)
- asia_oceania_global_sources.py     (600+ sources - 15 countries + global orgs)
- india_south_asia_sources.py        (800+ sources - 5 South Asian countries)
- central_asia_caucasus_sources.py   (300+ sources - 8 Central Asian & Caucasus countries)
- africa_middle_east_sources.py      (600+ sources - 30+ countries)
- pacific_islands_sources.py         (200+ sources - 20+ Pacific Island nations)

TOTAL: 5000+ Open Data Sources from 200+ Countries

CATEGORIES COVERED:
- Government & Statistics
- Universities & Research
- Hospitals & Healthcare
- Banks & Financial Markets
- Industry & Manufacturing
- Technology & Innovation
- News & Media
- Culture & Museums
- Sport & Entertainment
- Tourism & Travel
- Energy & Environment
- Transport & Infrastructure
- Telecom & Communication
- International Organizations

Author: Kloud Cloud Team
Version: 2.0.0
Last Updated: December 2024
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import importlib
import sys
from pathlib import Path

# Add data_sources directory to path
data_sources_dir = Path(__file__).parent
if str(data_sources_dir) not in sys.path:
    sys.path.insert(0, str(data_sources_dir))

# ============================================================
# UNIFIED ENUMS AND DATACLASS
# ============================================================

class SourceCategory(Enum):
    """All available source categories"""
    GOVERNMENT = "government"
    UNIVERSITY = "university"
    HOSPITAL = "hospital"
    BANK = "bank"
    INDUSTRY = "industry"
    NEWS = "news"
    CULTURE = "culture"
    RATING = "rating"
    RESEARCH = "research"
    STATISTICS = "statistics"
    ENVIRONMENTAL = "environmental"
    TRANSPORT = "transport"
    ENERGY = "energy"
    TELECOM = "telecom"
    TECHNOLOGY = "technology"
    SPORT = "sport"
    ENTERTAINMENT = "entertainment"
    TOURISM = "tourism"
    EVENTS = "events"
    LIFESTYLE = "lifestyle"
    INTERNATIONAL = "international"

class Region(Enum):
    """Geographic regions"""
    EUROPE = "europe"
    NORTH_AMERICA = "north_america"
    SOUTH_AMERICA = "south_america"
    EAST_ASIA = "east_asia"
    SOUTH_ASIA = "south_asia"
    SOUTHEAST_ASIA = "southeast_asia"
    OCEANIA = "oceania"
    MIDDLE_EAST = "middle_east"
    NORTH_AFRICA = "north_africa"
    SUB_SAHARAN_AFRICA = "sub_saharan_africa"
    GLOBAL = "global"

@dataclass
class DataSource:
    """Unified data source structure"""
    url: str
    name: str
    category: SourceCategory
    country: str
    description: str = ""
    api_available: bool = False
    license: str = "Public"
    region: Optional[Region] = None

# ============================================================
# COUNTRY MAPPINGS
# ============================================================

COUNTRY_TO_REGION = {
    # Europe
    "DE": Region.EUROPE, "FR": Region.EUROPE, "GB": Region.EUROPE, 
    "IT": Region.EUROPE, "ES": Region.EUROPE, "NL": Region.EUROPE,
    "CH": Region.EUROPE, "AT": Region.EUROPE, "PL": Region.EUROPE,
    "BE": Region.EUROPE, "SE": Region.EUROPE, "NO": Region.EUROPE,
    "DK": Region.EUROPE, "FI": Region.EUROPE, "IE": Region.EUROPE,
    "PT": Region.EUROPE, "GR": Region.EUROPE, "CZ": Region.EUROPE,
    "HU": Region.EUROPE, "RO": Region.EUROPE, "UA": Region.EUROPE,
    "SK": Region.EUROPE, "BG": Region.EUROPE, "RS": Region.EUROPE,
    "HR": Region.EUROPE, "SI": Region.EUROPE, "BA": Region.EUROPE,
    "AL": Region.EUROPE, "MK": Region.EUROPE, "ME": Region.EUROPE,
    "XK": Region.EUROPE, "MD": Region.EUROPE, "BY": Region.EUROPE,
    "LT": Region.EUROPE, "LV": Region.EUROPE, "EE": Region.EUROPE,
    
    # Americas
    "US": Region.NORTH_AMERICA, "CA": Region.NORTH_AMERICA,
    "MX": Region.NORTH_AMERICA, "BR": Region.SOUTH_AMERICA,
    "AR": Region.SOUTH_AMERICA, "CL": Region.SOUTH_AMERICA,
    "CO": Region.SOUTH_AMERICA, "PE": Region.SOUTH_AMERICA,
    "VE": Region.SOUTH_AMERICA, "EC": Region.SOUTH_AMERICA,
    
    # Caribbean
    "CU": Region.NORTH_AMERICA, "JM": Region.NORTH_AMERICA,
    "HT": Region.NORTH_AMERICA, "DO": Region.NORTH_AMERICA,
    "PR": Region.NORTH_AMERICA, "BS": Region.NORTH_AMERICA,
    "TT": Region.NORTH_AMERICA, "BB": Region.NORTH_AMERICA,
    
    # Central America
    "GT": Region.NORTH_AMERICA, "HN": Region.NORTH_AMERICA,
    "SV": Region.NORTH_AMERICA, "NI": Region.NORTH_AMERICA,
    "CR": Region.NORTH_AMERICA, "PA": Region.NORTH_AMERICA,
    "BZ": Region.NORTH_AMERICA,
    
    # East Asia
    "CN": Region.EAST_ASIA, "JP": Region.EAST_ASIA, "KR": Region.EAST_ASIA,
    "TW": Region.EAST_ASIA, "HK": Region.EAST_ASIA, "MN": Region.EAST_ASIA,
    
    # South Asia
    "IN": Region.SOUTH_ASIA, "PK": Region.SOUTH_ASIA, "BD": Region.SOUTH_ASIA,
    "LK": Region.SOUTH_ASIA, "NP": Region.SOUTH_ASIA,
    
    # Southeast Asia
    "SG": Region.SOUTHEAST_ASIA, "MY": Region.SOUTHEAST_ASIA,
    "ID": Region.SOUTHEAST_ASIA, "TH": Region.SOUTHEAST_ASIA,
    "VN": Region.SOUTHEAST_ASIA, "PH": Region.SOUTHEAST_ASIA,
    
    # Oceania
    "AU": Region.OCEANIA, "NZ": Region.OCEANIA,
    "FJ": Region.OCEANIA, "PG": Region.OCEANIA, "SB": Region.OCEANIA,
    "VU": Region.OCEANIA, "NC": Region.OCEANIA, "WS": Region.OCEANIA,
    "TO": Region.OCEANIA, "PF": Region.OCEANIA, "GU": Region.OCEANIA,
    "PW": Region.OCEANIA, "FM": Region.OCEANIA, "MH": Region.OCEANIA,
    "KI": Region.OCEANIA, "NR": Region.OCEANIA, "TV": Region.OCEANIA,
    "CK": Region.OCEANIA, "NU": Region.OCEANIA, "AS": Region.OCEANIA,
    
    # Central Asia & Caucasus
    "KZ": Region.EAST_ASIA, "UZ": Region.EAST_ASIA,
    "TJ": Region.EAST_ASIA, "KG": Region.EAST_ASIA,
    "TM": Region.EAST_ASIA, "GE": Region.MIDDLE_EAST,
    "AM": Region.MIDDLE_EAST, "AZ": Region.MIDDLE_EAST,
    
    # Middle East
    "SA": Region.MIDDLE_EAST, "AE": Region.MIDDLE_EAST, "IL": Region.MIDDLE_EAST,
    "TR": Region.MIDDLE_EAST, "JO": Region.MIDDLE_EAST, "QA": Region.MIDDLE_EAST,
    "KW": Region.MIDDLE_EAST, "BH": Region.MIDDLE_EAST, "OM": Region.MIDDLE_EAST,
    "IR": Region.MIDDLE_EAST, "IQ": Region.MIDDLE_EAST, "LB": Region.MIDDLE_EAST,
    
    # North Africa
    "EG": Region.NORTH_AFRICA, "MA": Region.NORTH_AFRICA, 
    "DZ": Region.NORTH_AFRICA, "TN": Region.NORTH_AFRICA, "LY": Region.NORTH_AFRICA,
    
    # Sub-Saharan Africa
    "ZA": Region.SUB_SAHARAN_AFRICA, "NG": Region.SUB_SAHARAN_AFRICA,
    "KE": Region.SUB_SAHARAN_AFRICA, "GH": Region.SUB_SAHARAN_AFRICA,
    "TZ": Region.SUB_SAHARAN_AFRICA, "ET": Region.SUB_SAHARAN_AFRICA,
    "UG": Region.SUB_SAHARAN_AFRICA, "RW": Region.SUB_SAHARAN_AFRICA,
    "SN": Region.SUB_SAHARAN_AFRICA, "CI": Region.SUB_SAHARAN_AFRICA,
    "MU": Region.SUB_SAHARAN_AFRICA, "BW": Region.SUB_SAHARAN_AFRICA,
    "NA": Region.SUB_SAHARAN_AFRICA, "ZM": Region.SUB_SAHARAN_AFRICA,
    "ZW": Region.SUB_SAHARAN_AFRICA,
    
    # Global/International
    "INTL": Region.GLOBAL, "GLOBAL": Region.GLOBAL,
    "AFRICA": Region.SUB_SAHARAN_AFRICA, "ME": Region.MIDDLE_EAST,
}

COUNTRY_NAMES = {
    # Europe
    "DE": "Germany", "FR": "France", "GB": "United Kingdom", 
    "IT": "Italy", "ES": "Spain", "NL": "Netherlands",
    "CH": "Switzerland", "AT": "Austria", "PL": "Poland",
    "BE": "Belgium", "SE": "Sweden", "NO": "Norway",
    "DK": "Denmark", "FI": "Finland", "IE": "Ireland",
    "PT": "Portugal", "GR": "Greece", "CZ": "Czech Republic",
    "SK": "Slovakia", "HU": "Hungary", "RO": "Romania",
    "UA": "Ukraine", "BG": "Bulgaria", "RS": "Serbia",
    "HR": "Croatia", "SI": "Slovenia", "BA": "Bosnia and Herzegovina",
    "AL": "Albania", "MK": "North Macedonia", "ME": "Montenegro",
    "XK": "Kosovo", "MD": "Moldova", "BY": "Belarus",
    "LT": "Lithuania", "LV": "Latvia", "EE": "Estonia",
    
    # Americas
    "US": "United States", "CA": "Canada", "MX": "Mexico",
    "BR": "Brazil", "AR": "Argentina", "CL": "Chile",
    "CO": "Colombia", "PE": "Peru",
    
    # Caribbean
    "CU": "Cuba", "JM": "Jamaica", "HT": "Haiti",
    "DO": "Dominican Republic", "PR": "Puerto Rico",
    "BS": "Bahamas", "TT": "Trinidad and Tobago", "BB": "Barbados",
    
    # Central America
    "GT": "Guatemala", "HN": "Honduras", "SV": "El Salvador",
    "NI": "Nicaragua", "CR": "Costa Rica", "PA": "Panama", "BZ": "Belize",
    
    # Asia
    "CN": "China", "JP": "Japan", "KR": "South Korea",
    "TW": "Taiwan", "HK": "Hong Kong", "SG": "Singapore",
    "IN": "India", "PK": "Pakistan", "BD": "Bangladesh",
    "LK": "Sri Lanka", "NP": "Nepal", "MY": "Malaysia",
    "ID": "Indonesia", "TH": "Thailand", "VN": "Vietnam",
    "PH": "Philippines",
    
    # Oceania
    "AU": "Australia", "NZ": "New Zealand",
    "FJ": "Fiji", "PG": "Papua New Guinea", "SB": "Solomon Islands",
    "VU": "Vanuatu", "NC": "New Caledonia", "WS": "Samoa",
    "TO": "Tonga", "PF": "French Polynesia", "GU": "Guam",
    "PW": "Palau", "FM": "Micronesia", "MH": "Marshall Islands",
    "KI": "Kiribati", "NR": "Nauru", "TV": "Tuvalu",
    "CK": "Cook Islands", "NU": "Niue", "AS": "American Samoa",
    
    # Central Asia & Caucasus
    "KZ": "Kazakhstan", "UZ": "Uzbekistan", "TJ": "Tajikistan",
    "KG": "Kyrgyzstan", "TM": "Turkmenistan", "GE": "Georgia",
    "AM": "Armenia", "AZ": "Azerbaijan",
    
    # Middle East
    "SA": "Saudi Arabia", "AE": "UAE", "IL": "Israel",
    "TR": "Turkey", "JO": "Jordan", "QA": "Qatar",
    "KW": "Kuwait", "BH": "Bahrain", "OM": "Oman",
    
    # Africa
    "ZA": "South Africa", "NG": "Nigeria", "EG": "Egypt",
    "KE": "Kenya", "MA": "Morocco", "GH": "Ghana",
    "TZ": "Tanzania", "ET": "Ethiopia", "UG": "Uganda",
    "RW": "Rwanda", "SN": "Senegal", "DZ": "Algeria",
    "TN": "Tunisia", "MU": "Mauritius", "BW": "Botswana",
    
    # International
    "INTL": "International",
}

# ============================================================
# DATA SOURCE LOADER
# ============================================================

class GlobalDataSources:
    """
    Master class for accessing all global data sources.
    Lazy-loads regional modules on demand.
    """
    
    def __init__(self):
        self._all_sources: List[DataSource] = []
        self._loaded = False
        
    def _load_all_sources(self):
        """Load all regional source modules"""
        if self._loaded:
            return
            
        try:
            # Try to import regional modules
            from europe_sources import ALL_EUROPE_SOURCES
            self._all_sources.extend(ALL_EUROPE_SOURCES)
        except ImportError:
            pass
            
        try:
            from americas_sources import ALL_AMERICAS_SOURCES
            self._all_sources.extend(ALL_AMERICAS_SOURCES)
        except ImportError:
            pass
            
        try:
            from asia_oceania_global_sources import ALL_ASIA_OCEANIA_GLOBAL_SOURCES
            self._all_sources.extend(ALL_ASIA_OCEANIA_GLOBAL_SOURCES)
        except ImportError:
            pass
            
        try:
            from africa_middle_east_sources import ALL_AFRICA_MIDDLE_EAST_SOURCES
            self._all_sources.extend(ALL_AFRICA_MIDDLE_EAST_SOURCES)
        except ImportError:
            pass
            
        try:
            from india_south_asia_sources import ALL_INDIA_SOUTH_ASIA_SOURCES
            self._all_sources.extend(ALL_INDIA_SOUTH_ASIA_SOURCES)
        except ImportError:
            pass
        
        try:
            from asia_china_sources import ALL_ASIA_CHINA_SOURCES
            self._all_sources.extend(ALL_ASIA_CHINA_SOURCES)
        except ImportError:
            pass
        
        try:
            from central_asia_caucasus_sources import ALL_CENTRAL_ASIA_CAUCASUS_SOURCES
            self._all_sources.extend(ALL_CENTRAL_ASIA_CAUCASUS_SOURCES)
        except ImportError:
            pass
        
        try:
            from eastern_europe_balkans_sources import ALL_EASTERN_EUROPE_BALKANS_SOURCES
            self._all_sources.extend(ALL_EASTERN_EUROPE_BALKANS_SOURCES)
        except ImportError:
            pass
        
        try:
            from caribbean_central_america_sources import ALL_CARIBBEAN_CENTRAL_AMERICA_SOURCES
            self._all_sources.extend(ALL_CARIBBEAN_CENTRAL_AMERICA_SOURCES)
        except ImportError:
            pass
        
        try:
            from pacific_islands_sources import ALL_PACIFIC_SOURCES
            self._all_sources.extend(ALL_PACIFIC_SOURCES)
        except ImportError:
            pass
            
        self._loaded = True
        
    @property
    def all_sources(self) -> List[DataSource]:
        """Get all data sources"""
        self._load_all_sources()
        return self._all_sources
        
    def get_by_country(self, country_code: str) -> List[DataSource]:
        """Get sources for a specific country"""
        return [s for s in self.all_sources if s.country == country_code.upper()]
        
    def get_by_region(self, region: Region) -> List[DataSource]:
        """Get sources for a specific region"""
        return [s for s in self.all_sources 
                if COUNTRY_TO_REGION.get(s.country) == region]
                
    def get_by_category(self, category: SourceCategory) -> List[DataSource]:
        """Get sources for a specific category"""
        return [s for s in self.all_sources if s.category == category]
        
    def get_api_sources(self) -> List[DataSource]:
        """Get only sources with API access"""
        return [s for s in self.all_sources if s.api_available]
        
    def search(self, query: str) -> List[DataSource]:
        """Search sources by name, description, or URL"""
        query = query.lower()
        return [s for s in self.all_sources 
                if query in s.name.lower() or 
                   query in s.description.lower() or 
                   query in s.url.lower()]
                   
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the data sources"""
        sources = self.all_sources
        
        # Count by category
        by_category = {}
        for cat in SourceCategory:
            count = len([s for s in sources if s.category == cat])
            if count > 0:
                by_category[cat.value] = count
                
        # Count by region
        by_region = {}
        for region in Region:
            count = len(self.get_by_region(region))
            if count > 0:
                by_region[region.value] = count
                
        # Count by country
        countries = set(s.country for s in sources)
        
        return {
            "total_sources": len(sources),
            "api_sources": len(self.get_api_sources()),
            "countries_covered": len(countries),
            "by_category": by_category,
            "by_region": by_region,
        }

# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

# Global instance
_global_sources = GlobalDataSources()

def get_all_sources() -> List[DataSource]:
    """Get all data sources from all regions"""
    return _global_sources.all_sources

def get_sources_by_country(country_code: str) -> List[DataSource]:
    """Get sources for a specific country code (e.g., 'US', 'DE', 'JP')"""
    return _global_sources.get_by_country(country_code)

def get_sources_by_region(region: Region) -> List[DataSource]:
    """Get sources for a specific region"""
    return _global_sources.get_by_region(region)

def get_sources_by_category(category: SourceCategory) -> List[DataSource]:
    """Get sources for a specific category"""
    return _global_sources.get_by_category(category)

def get_api_sources() -> List[DataSource]:
    """Get only sources with API access"""
    return _global_sources.get_api_sources()

def search_sources(query: str) -> List[DataSource]:
    """Search sources by name, description, or URL"""
    return _global_sources.search(query)

def get_statistics() -> Dict[str, Any]:
    """Get comprehensive statistics about all data sources"""
    return _global_sources.get_statistics()

def get_country_name(code: str) -> str:
    """Get full country name from country code"""
    return COUNTRY_NAMES.get(code.upper(), code)

def get_country_region(code: str) -> Optional[Region]:
    """Get region for a country code"""
    return COUNTRY_TO_REGION.get(code.upper())

# ============================================================
# EXPORT FOR API
# ============================================================

def to_json_serializable(sources: List[DataSource]) -> List[Dict]:
    """Convert sources to JSON-serializable format"""
    return [
        {
            "url": s.url,
            "name": s.name,
            "category": s.category.value,
            "country": s.country,
            "country_name": get_country_name(s.country),
            "description": s.description,
            "api_available": s.api_available,
            "license": s.license,
            "region": get_country_region(s.country).value if get_country_region(s.country) else None
        }
        for s in sources
    ]

# ============================================================
# MAIN - STATISTICS DISPLAY
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🌍 KLOUD GLOBAL DATA SOURCES")
    print("=" * 60)
    
    stats = get_statistics()
    
    print(f"\n📊 OVERVIEW:")
    print(f"   Total Sources: {stats['total_sources']}")
    print(f"   API Sources: {stats['api_sources']}")
    print(f"   Countries: {stats['countries_covered']}")
    
    print(f"\n🗂️ BY CATEGORY:")
    for cat, count in sorted(stats['by_category'].items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")
        
    print(f"\n🌏 BY REGION:")
    for region, count in sorted(stats['by_region'].items(), key=lambda x: -x[1]):
        print(f"   {region}: {count}")
        
    print("\n" + "=" * 60)
    print("✅ Global Data Sources initialized successfully!")
    print("=" * 60)

