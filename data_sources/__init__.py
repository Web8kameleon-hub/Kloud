# -*- coding: utf-8 -*-
"""
🌍 KLOUD DATA SOURCES MODULE
===============================

Comprehensive collection of 5000+ free open data sources from 200+ countries.

Quick Start:
    from data_sources import get_all_sources, get_sources_by_country

    # Get all sources
    all_sources = get_all_sources()
    
    # Get sources by country
    us_sources = get_sources_by_country("US")
    de_sources = get_sources_by_country("DE")
    
    # Get sources by category
    from data_sources import get_sources_by_category, SourceCategory
    gov_sources = get_sources_by_category(SourceCategory.GOVERNMENT)
    
    # Get only API sources
    api_sources = get_api_sources()
    
    # Search
    results = search_sources("university")

Available Modules:
    - europe_sources: 1000+ sources from 20 West European countries
    - eastern_europe_balkans_sources: 600+ sources from 19 Eastern European countries
    - americas_sources: 600+ sources from 16 American countries
    - caribbean_central_america_sources: 300+ sources from 28 Caribbean & Central American countries
    - asia_china_sources: 800+ sources from 7 East Asian countries
    - asia_oceania_global_sources: 600+ sources from Asia, Oceania & Global organizations
    - india_south_asia_sources: 800+ sources from 5 South Asian countries
    - central_asia_caucasus_sources: 300+ sources from 8 Central Asian & Caucasus countries
    - africa_middle_east_sources: 600+ sources from 30+ African & Middle East countries
    - pacific_islands_sources: 200+ sources from 20+ Pacific Island nations
    - global_data_sources: Master index combining all sources

Categories:
    GOVERNMENT, UNIVERSITY, HOSPITAL, BANK, INDUSTRY, NEWS, 
    CULTURE, RESEARCH, STATISTICS, ENVIRONMENTAL, TRANSPORT,
    ENERGY, TELECOM, TECHNOLOGY, SPORT, ENTERTAINMENT, 
    TOURISM, EVENTS, LIFESTYLE, INTERNATIONAL

Regions:
    EUROPE, NORTH_AMERICA, SOUTH_AMERICA, EAST_ASIA, SOUTH_ASIA,
    SOUTHEAST_ASIA, OCEANIA, MIDDLE_EAST, NORTH_AFRICA, 
    SUB_SAHARAN_AFRICA, GLOBAL

Version: 3.0.0 - Full Global Coverage (200+ Countries)
"""

from .global_data_sources import (
    # Main functions
    get_all_sources,
    get_sources_by_country,
    get_sources_by_region,
    get_sources_by_category,
    get_api_sources,
    search_sources,
    get_statistics,
    get_country_name,
    get_country_region,
    to_json_serializable,
    
    # Classes
    GlobalDataSources,
    DataSource,
    SourceCategory,
    Region,
    
    # Mappings
    COUNTRY_TO_REGION,
    COUNTRY_NAMES,
)

__version__ = "3.0.0"
__author__ = "Kloud Cloud Team"
__all__ = [
    # Functions
    "get_all_sources",
    "get_sources_by_country",
    "get_sources_by_region",
    "get_sources_by_category",
    "get_api_sources",
    "search_sources",
    "get_statistics",
    "get_country_name",
    "get_country_region",
    "to_json_serializable",
    
    # Classes
    "GlobalDataSources",
    "DataSource",
    "SourceCategory",
    "Region",
    
    # Mappings
    "COUNTRY_TO_REGION",
    "COUNTRY_NAMES",
]

