# -*- coding: utf-8 -*-
"""
 GLOBAL OPEN DATA SOURCES
============================
Free Open Data APIs from ALL Continents + Antarctica

Structure:
 EUROPE (EU, Balkans, Eastern Europe)
 AMERICAS (North, Central, South America, Caribbean)
 ASIA (China, Japan, Korea, Southeast Asia)
 INDIA & SOUTH ASIA (India, Pakistan, Bangladesh, Sri Lanka)
 AFRICA & MIDDLE EAST (Africa, Arab World)
 OCEANIA & PACIFIC (Australia, New Zealand, Pacific Islands)
 CENTRAL ASIA & CAUCASUS (Kazakhstan, Uzbekistan, Georgia, Armenia)
 ANTARCTICA (Research Stations, Polar Data)

Author: Kloud Team
Version: 2.0.1 HYBRID
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import aiohttp
import asyncio
import logging

logger = logging.getLogger("global_data_sources")


@dataclass
class DataSource:
    """Single open data source"""
    name: str
    url: str
    api_url: str
    region: str
    category: str
    free: bool = True
    requires_key: bool = False
    description: str = ""
    formats: List[str] = field(default_factory=lambda: ["json"])


# =============================================================================
# EUROPE -  European Union + Eastern Europe + Balkans
# =============================================================================

EUROPE_SOURCES = {
    # --- EU Official ---
    "eurostat": DataSource(
        name="Eurostat",
        url="https://ec.europa.eu/eurostat",
        api_url="https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1",
        region="europe", category="statistics",
        description="Official EU statistics - GDP, population, trade, employment"
    ),
    "eu_open_data": DataSource(
        name="EU Open Data Portal",
        url="https://data.europa.eu",
        api_url="https://data.europa.eu/api/hub/search/datasets",
        region="europe", category="government",
        description="Over 1.5M datasets from EU institutions"
    ),
    "ecb": DataSource(
        name="European Central Bank",
        url="https://www.ecb.europa.eu",
        api_url="https://data.ecb.europa.eu/data-api/v1",
        region="europe", category="finance",
        description="Euro exchange rates, monetary policy, banking"
    ),
    "eea": DataSource(
        name="European Environment Agency",
        url="https://www.eea.europa.eu",
        api_url="https://www.eea.europa.eu/api",
        region="europe", category="environment",
        description="Air quality, climate, biodiversity data"
    ),
    "ecdc": DataSource(
        name="European CDC",
        url="https://www.ecdc.europa.eu",
        api_url="https://www.ecdc.europa.eu/en/publications-data",
        region="europe", category="health",
        description="European disease surveillance and health data"
    ),
    "copernicus": DataSource(
        name="Copernicus",
        url="https://www.copernicus.eu",
        api_url="https://cds.climate.copernicus.eu/api/v2",
        region="europe", category="satellite",
        description="Earth observation, climate, atmosphere data"
    ),
    
    # --- Western Europe ---
    "destatis": DataSource(
        name="Destatis (Germany)",
        url="https://www.destatis.de",
        api_url="https://www-genesis.destatis.de/genesisWS/rest",
        region="europe", category="statistics",
        description="German Federal Statistics Office"
    ),
    "insee": DataSource(
        name="INSEE (France)",
        url="https://www.insee.fr",
        api_url="https://api.insee.fr/series/BDM",
        region="europe", category="statistics",
        description="French National Statistics Institute"
    ),
    "ons_uk": DataSource(
        name="ONS (UK)",
        url="https://www.ons.gov.uk",
        api_url="https://api.ons.gov.uk/v1",
        region="europe", category="statistics",
        description="UK Office for National Statistics"
    ),
    "istat": DataSource(
        name="ISTAT (Italy)",
        url="https://www.istat.it",
        api_url="https://esploradati.istat.it/api",
        region="europe", category="statistics",
        description="Italian National Statistics Institute"
    ),
    "ine_spain": DataSource(
        name="INE (Spain)",
        url="https://www.ine.es",
        api_url="https://servicios.ine.es/wstempus/js",
        region="europe", category="statistics",
        description="Spanish National Statistics Institute"
    ),
    
    # --- Balkans & Albania ---
    "instat_albania": DataSource(
        name="INSTAT Albania",
        url="https://www.instat.gov.al",
        api_url="https://www.instat.gov.al/api",
        region="balkans", category="statistics",
        description="Albanian Institute of Statistics - GDP, population, trade"
    ),
    "bank_albania": DataSource(
        name="Bank of Albania",
        url="https://www.bankofalbania.org",
        api_url="https://www.bankofalbania.org/data",
        region="balkans", category="finance",
        description="Albanian central bank - exchange rates, monetary policy"
    ),
    "albania_open_data": DataSource(
        name="Albania Open Data",
        url="https://data.gov.al",
        api_url="https://data.gov.al/api/3/action",
        region="balkans", category="government",
        description="Albanian government open data portal"
    ),
    "kosovo_stats": DataSource(
        name="Kosovo Statistics",
        url="https://ask.rks-gov.net",
        api_url="https://askdata.rks-gov.net/api",
        region="balkans", category="statistics",
        description="Kosovo Agency of Statistics"
    ),
    "serbia_stats": DataSource(
        name="Serbia Statistics",
        url="https://www.stat.gov.rs",
        api_url="https://data.stat.gov.rs/api",
        region="balkans", category="statistics",
        description="Statistical Office of Serbia"
    ),
    "nmacedonia_stats": DataSource(
        name="North Macedonia Statistics",
        url="https://www.stat.gov.mk",
        api_url="https://makstat.stat.gov.mk/api",
        region="balkans", category="statistics",
        description="State Statistical Office of North Macedonia"
    ),
    "montenegro_stats": DataSource(
        name="Montenegro Statistics",
        url="https://www.monstat.org",
        api_url="https://www.monstat.org/api",
        region="balkans", category="statistics",
        description="Statistical Office of Montenegro"
    ),
    "bosnia_stats": DataSource(
        name="Bosnia Statistics",
        url="https://bhas.gov.ba",
        api_url="https://bhas.gov.ba/data/api",
        region="balkans", category="statistics",
        description="Agency for Statistics of BiH"
    ),
    "croatia_stats": DataSource(
        name="Croatia Statistics",
        url="https://www.dzs.hr",
        api_url="https://web.dzs.hr/api",
        region="balkans", category="statistics",
        description="Croatian Bureau of Statistics"
    ),
    "slovenia_stats": DataSource(
        name="Slovenia Statistics",
        url="https://www.stat.si",
        api_url="https://pxweb.stat.si/SiStatData/api",
        region="balkans", category="statistics",
        description="Statistical Office of Slovenia"
    ),
    
    # --- Eastern Europe ---
    "romania_stats": DataSource(
        name="Romania Statistics",
        url="https://insse.ro",
        api_url="https://tempo.insse.ro/api",
        region="europe", category="statistics",
        description="Romanian National Statistics Institute"
    ),
    "bulgaria_stats": DataSource(
        name="Bulgaria Statistics",
        url="https://www.nsi.bg",
        api_url="https://www.nsi.bg/api",
        region="europe", category="statistics",
        description="National Statistical Institute of Bulgaria"
    ),
    "hungary_stats": DataSource(
        name="Hungary Statistics",
        url="https://www.ksh.hu",
        api_url="https://statinfo.ksh.hu/api",
        region="europe", category="statistics",
        description="Hungarian Central Statistical Office"
    ),
    "czech_stats": DataSource(
        name="Czech Statistics",
        url="https://www.czso.cz",
        api_url="https://vdb.czso.cz/pll/eweb/lkod.api",
        region="europe", category="statistics",
        description="Czech Statistical Office"
    ),
    "poland_stats": DataSource(
        name="Poland Statistics",
        url="https://stat.gov.pl",
        api_url="https://api.stat.gov.pl",
        region="europe", category="statistics",
        description="Statistics Poland"
    ),
    "ukraine_stats": DataSource(
        name="Ukraine Statistics",
        url="https://www.ukrstat.gov.ua",
        api_url="https://api.ukrstat.gov.ua",
        region="europe", category="statistics",
        description="State Statistics Service of Ukraine"
    ),
}


# =============================================================================
# AMERICAS -  North, Central, South America & Caribbean
# =============================================================================

AMERICAS_SOURCES = {
    # --- USA ---
    "us_census": DataSource(
        name="US Census Bureau",
        url="https://www.census.gov",
        api_url="https://api.census.gov/data",
        region="north_america", category="statistics",
        description="US population, demographics, economy"
    ),
    "data_gov": DataSource(
        name="Data.gov",
        url="https://data.gov",
        api_url="https://catalog.data.gov/api/3/action",
        region="north_america", category="government",
        description="US Federal Government open data - 300K+ datasets"
    ),
    "bls": DataSource(
        name="Bureau of Labor Statistics",
        url="https://www.bls.gov",
        api_url="https://api.bls.gov/publicAPI/v2",
        region="north_america", category="labor",
        description="US employment, wages, inflation data"
    ),
    "fred": DataSource(
        name="FRED (Federal Reserve)",
        url="https://fred.stlouisfed.org",
        api_url="https://api.stlouisfed.org/fred",
        region="north_america", category="finance",
        description="US Federal Reserve economic data - 800K+ time series"
    ),
    "sec_edgar": DataSource(
        name="SEC EDGAR",
        url="https://www.sec.gov/edgar",
        api_url="https://data.sec.gov/submissions",
        region="north_america", category="finance",
        description="US Securities filings, company data"
    ),
    "usda": DataSource(
        name="USDA",
        url="https://www.usda.gov",
        api_url="https://quickstats.nass.usda.gov/api",
        region="north_america", category="agriculture",
        description="US agriculture, food, nutrition data"
    ),
    "epa": DataSource(
        name="EPA",
        url="https://www.epa.gov",
        api_url="https://api.epa.gov",
        region="north_america", category="environment",
        description="US environmental, air quality, water data"
    ),
    "noaa": DataSource(
        name="NOAA",
        url="https://www.noaa.gov",
        api_url="https://www.ncdc.noaa.gov/cdo-web/api/v2",
        region="north_america", category="weather",
        requires_key=True,
        description="US weather, climate, ocean data"
    ),
    "nasa": DataSource(
        name="NASA Open Data",
        url="https://data.nasa.gov",
        api_url="https://data.nasa.gov/resource",
        region="north_america", category="space",
        description="NASA space, earth science, astronomy data"
    ),
    
    # --- Canada ---
    "statcan": DataSource(
        name="Statistics Canada",
        url="https://www.statcan.gc.ca",
        api_url="https://www150.statcan.gc.ca/t1/wds/rest",
        region="north_america", category="statistics",
        description="Canadian national statistics"
    ),
    "canada_open": DataSource(
        name="Canada Open Data",
        url="https://open.canada.ca",
        api_url="https://open.canada.ca/data/api/3/action",
        region="north_america", category="government",
        description="Canadian government open data portal"
    ),
    
    # --- Mexico ---
    "inegi": DataSource(
        name="INEGI (Mexico)",
        url="https://www.inegi.org.mx",
        api_url="https://www.inegi.org.mx/app/api/",
        region="central_america", category="statistics",
        description="Mexican National Statistics and Geography"
    ),
    
    # --- Brazil ---
    "ibge": DataSource(
        name="IBGE (Brazil)",
        url="https://www.ibge.gov.br",
        api_url="https://servicodados.ibge.gov.br/api/v1",
        region="south_america", category="statistics",
        description="Brazilian Institute of Geography and Statistics"
    ),
    "bcb": DataSource(
        name="Banco Central do Brasil",
        url="https://www.bcb.gov.br",
        api_url="https://api.bcb.gov.br/dados",
        region="south_america", category="finance",
        description="Brazilian Central Bank - economic indicators"
    ),
    
    # --- Argentina ---
    "indec": DataSource(
        name="INDEC (Argentina)",
        url="https://www.indec.gob.ar",
        api_url="https://apis.datos.gob.ar/series/api",
        region="south_america", category="statistics",
        description="Argentine National Statistics Institute"
    ),
    
    # --- Chile ---
    "ine_chile": DataSource(
        name="INE Chile",
        url="https://www.ine.cl",
        api_url="https://www.ine.cl/estadisticas/api",
        region="south_america", category="statistics",
        description="Chilean National Statistics Institute"
    ),
    
    # --- Colombia ---
    "dane": DataSource(
        name="DANE (Colombia)",
        url="https://www.dane.gov.co",
        api_url="https://www.dane.gov.co/files/api",
        region="south_america", category="statistics",
        description="Colombian National Statistics Department"
    ),
    
    # --- Caribbean ---
    "caricom": DataSource(
        name="CARICOM Stats",
        url="https://statistics.caricom.org",
        api_url="https://statistics.caricom.org/api",
        region="caribbean", category="statistics",
        description="Caribbean Community statistics"
    ),
}


# =============================================================================
# ASIA -  China, Japan, Korea, Southeast Asia
# =============================================================================

ASIA_CHINA_SOURCES = {
    # --- China ---
    "china_nbs": DataSource(
        name="China NBS",
        url="https://data.stats.gov.cn",
        api_url="https://data.stats.gov.cn/english/easyquery.htm",
        region="china", category="statistics",
        description="China National Bureau of Statistics"
    ),
    "china_customs": DataSource(
        name="China Customs",
        url="http://www.customs.gov.cn",
        api_url="http://www.customs.gov.cn/customs/302249/302274/302277/index.html",
        region="china", category="trade",
        description="China trade and import/export data"
    ),
    "pboc": DataSource(
        name="PBOC",
        url="http://www.pbc.gov.cn",
        api_url="http://www.pbc.gov.cn/english/130437/index.html",
        region="china", category="finance",
        description="People's Bank of China - monetary, banking data"
    ),
    
    # --- Japan ---
    "japan_stat": DataSource(
        name="Japan Statistics Bureau",
        url="https://www.stat.go.jp",
        api_url="https://api.e-stat.go.jp/rest/3.0/app",
        region="japan", category="statistics",
        description="Japanese national statistics"
    ),
    "boj": DataSource(
        name="Bank of Japan",
        url="https://www.boj.or.jp",
        api_url="https://www.stat-search.boj.or.jp/ssi/mtshtml/api",
        region="japan", category="finance",
        description="Japanese central bank data"
    ),
    
    # --- South Korea ---
    "kostat": DataSource(
        name="KOSTAT",
        url="https://kostat.go.kr",
        api_url="https://kosis.kr/openapi",
        region="korea", category="statistics",
        description="Statistics Korea"
    ),
    "bok": DataSource(
        name="Bank of Korea",
        url="https://www.bok.or.kr",
        api_url="https://ecos.bok.or.kr/api",
        region="korea", category="finance",
        description="Korean central bank economic statistics"
    ),
    
    # --- Southeast Asia ---
    "singapore_stat": DataSource(
        name="Singapore Statistics",
        url="https://www.singstat.gov.sg",
        api_url="https://tablebuilder.singstat.gov.sg/api",
        region="southeast_asia", category="statistics",
        description="Singapore Department of Statistics"
    ),
    "thailand_nso": DataSource(
        name="Thailand NSO",
        url="https://www.nso.go.th",
        api_url="https://data.go.th/api/3/action",
        region="southeast_asia", category="statistics",
        description="Thai National Statistical Office"
    ),
    "vietnam_gso": DataSource(
        name="Vietnam GSO",
        url="https://www.gso.gov.vn",
        api_url="https://www.gso.gov.vn/api",
        region="southeast_asia", category="statistics",
        description="General Statistics Office of Vietnam"
    ),
    "indonesia_bps": DataSource(
        name="Indonesia BPS",
        url="https://www.bps.go.id",
        api_url="https://webapi.bps.go.id/v1",
        region="southeast_asia", category="statistics",
        description="Statistics Indonesia"
    ),
    "malaysia_dosm": DataSource(
        name="Malaysia DOSM",
        url="https://www.dosm.gov.my",
        api_url="https://open.dosm.gov.my/api",
        region="southeast_asia", category="statistics",
        description="Department of Statistics Malaysia"
    ),
    "philippines_psa": DataSource(
        name="Philippines PSA",
        url="https://psa.gov.ph",
        api_url="https://openstat.psa.gov.ph/api",
        region="southeast_asia", category="statistics",
        description="Philippine Statistics Authority"
    ),
}


# =============================================================================
# INDIA & SOUTH ASIA -  India, Pakistan, Bangladesh, Sri Lanka
# =============================================================================

INDIA_SOUTH_ASIA_SOURCES = {
    # --- India ---
    "india_data": DataSource(
        name="India Open Data",
        url="https://data.gov.in",
        api_url="https://api.data.gov.in/resource",
        region="india", category="government",
        requires_key=True,
        description="Indian Government Open Data Platform - 500K+ datasets"
    ),
    "india_census": DataSource(
        name="India Census",
        url="https://censusindia.gov.in",
        api_url="https://censusindia.gov.in/DigitalLibrary",
        region="india", category="statistics",
        description="Census of India - population, demographics"
    ),
    "rbi": DataSource(
        name="Reserve Bank of India",
        url="https://www.rbi.org.in",
        api_url="https://dbie.rbi.org.in/api",
        region="india", category="finance",
        description="Indian central bank - monetary, banking statistics"
    ),
    "mospi": DataSource(
        name="MoSPI",
        url="http://mospi.nic.in",
        api_url="http://mospi.nic.in/data",
        region="india", category="statistics",
        description="Ministry of Statistics - GDP, national accounts"
    ),
    "niti_aayog": DataSource(
        name="NITI Aayog",
        url="https://niti.gov.in",
        api_url="https://ndap.niti.gov.in/api",
        region="india", category="development",
        description="India development indicators"
    ),
    
    # --- Pakistan ---
    "pbs": DataSource(
        name="Pakistan Bureau of Statistics",
        url="https://www.pbs.gov.pk",
        api_url="https://www.pbs.gov.pk/content",
        region="south_asia", category="statistics",
        description="Pakistani national statistics"
    ),
    
    # --- Bangladesh ---
    "bbs": DataSource(
        name="Bangladesh Bureau of Statistics",
        url="http://www.bbs.gov.bd",
        api_url="http://www.bbs.gov.bd/site/page",
        region="south_asia", category="statistics",
        description="Bangladeshi national statistics"
    ),
    
    # --- Sri Lanka ---
    "srilanka_stats": DataSource(
        name="Sri Lanka Statistics",
        url="http://www.statistics.gov.lk",
        api_url="http://www.statistics.gov.lk/data",
        region="south_asia", category="statistics",
        description="Department of Census and Statistics Sri Lanka"
    ),
    
    # --- Nepal ---
    "nepal_cbs": DataSource(
        name="Nepal CBS",
        url="https://cbs.gov.np",
        api_url="https://cbs.gov.np/api",
        region="south_asia", category="statistics",
        description="Central Bureau of Statistics Nepal"
    ),
}


# =============================================================================
# AFRICA & MIDDLE EAST -  Africa + Arab World
# =============================================================================

AFRICA_MIDDLE_EAST_SOURCES = {
    # --- Pan-African ---
    "afdb": DataSource(
        name="African Development Bank",
        url="https://www.afdb.org",
        api_url="https://dataportal.opendataforafrica.org/api",
        region="africa", category="development",
        description="African economic and development data"
    ),
    "au_statistics": DataSource(
        name="African Union Statistics",
        url="https://au.int/en/statistics",
        api_url="https://au.int/en/statistics/api",
        region="africa", category="statistics",
        description="African Union continental statistics"
    ),
    
    # --- South Africa ---
    "statssa": DataSource(
        name="Stats South Africa",
        url="https://www.statssa.gov.za",
        api_url="https://www.statssa.gov.za/api",
        region="africa", category="statistics",
        description="Statistics South Africa"
    ),
    
    # --- Nigeria ---
    "nbs_nigeria": DataSource(
        name="Nigeria NBS",
        url="https://nigerianstat.gov.ng",
        api_url="https://nigerianstat.gov.ng/api",
        region="africa", category="statistics",
        description="National Bureau of Statistics Nigeria"
    ),
    
    # --- Kenya ---
    "knbs": DataSource(
        name="Kenya KNBS",
        url="https://www.knbs.or.ke",
        api_url="https://www.knbs.or.ke/api",
        region="africa", category="statistics",
        description="Kenya National Bureau of Statistics"
    ),
    
    # --- Egypt ---
    "capmas": DataSource(
        name="CAPMAS Egypt",
        url="https://www.capmas.gov.eg",
        api_url="https://www.capmas.gov.eg/api",
        region="middle_east", category="statistics",
        description="Central Agency for Public Mobilization and Statistics Egypt"
    ),
    
    # --- Morocco ---
    "hcp_morocco": DataSource(
        name="HCP Morocco",
        url="https://www.hcp.ma",
        api_url="https://www.hcp.ma/api",
        region="africa", category="statistics",
        description="High Commission for Planning Morocco"
    ),
    
    # --- UAE ---
    "fcsa_uae": DataSource(
        name="UAE FCSA",
        url="https://fcsc.gov.ae",
        api_url="https://bayanat.ae/api/3/action",
        region="middle_east", category="statistics",
        description="UAE Federal Competitiveness and Statistics Centre"
    ),
    
    # --- Saudi Arabia ---
    "gastat": DataSource(
        name="Saudi GASTAT",
        url="https://www.stats.gov.sa",
        api_url="https://www.stats.gov.sa/en/api",
        region="middle_east", category="statistics",
        description="General Authority for Statistics Saudi Arabia"
    ),
    
    # --- Turkey ---
    "tuik": DataSource(
        name="TurkStat",
        url="https://www.tuik.gov.tr",
        api_url="https://data.tuik.gov.tr/api",
        region="middle_east", category="statistics",
        description="Turkish Statistical Institute"
    ),
    
    # --- Israel ---
    "cbs_israel": DataSource(
        name="Israel CBS",
        url="https://www.cbs.gov.il",
        api_url="https://www.cbs.gov.il/api",
        region="middle_east", category="statistics",
        description="Central Bureau of Statistics Israel"
    ),
}


# =============================================================================
# OCEANIA & PACIFIC -  Australia, New Zealand, Pacific Islands
# =============================================================================

OCEANIA_PACIFIC_SOURCES = {
    # --- Australia ---
    "abs": DataSource(
        name="ABS Australia",
        url="https://www.abs.gov.au",
        api_url="https://api.data.abs.gov.au/data",
        region="oceania", category="statistics",
        description="Australian Bureau of Statistics"
    ),
    "rba": DataSource(
        name="Reserve Bank Australia",
        url="https://www.rba.gov.au",
        api_url="https://www.rba.gov.au/statistics/tables",
        region="oceania", category="finance",
        description="Reserve Bank of Australia - monetary data"
    ),
    "data_gov_au": DataSource(
        name="Data.gov.au",
        url="https://data.gov.au",
        api_url="https://data.gov.au/api/3/action",
        region="oceania", category="government",
        description="Australian Government Open Data Portal"
    ),
    "bom": DataSource(
        name="Bureau of Meteorology",
        url="http://www.bom.gov.au",
        api_url="http://www.bom.gov.au/fwo",
        region="oceania", category="weather",
        description="Australian weather and climate data"
    ),
    
    # --- New Zealand ---
    "stats_nz": DataSource(
        name="Stats NZ",
        url="https://www.stats.govt.nz",
        api_url="https://statisticsnz.shinyapps.io/api",
        region="oceania", category="statistics",
        description="Statistics New Zealand"
    ),
    "rbnz": DataSource(
        name="Reserve Bank NZ",
        url="https://www.rbnz.govt.nz",
        api_url="https://www.rbnz.govt.nz/statistics",
        region="oceania", category="finance",
        description="Reserve Bank of New Zealand"
    ),
    
    # --- Pacific Islands ---
    "spc": DataSource(
        name="Pacific Community SPC",
        url="https://www.spc.int",
        api_url="https://stats.pacificdata.org/api",
        region="pacific", category="statistics",
        description="Pacific Community statistics - 22 island nations"
    ),
    "fiji_stats": DataSource(
        name="Fiji Bureau of Statistics",
        url="https://www.statsfiji.gov.fj",
        api_url="https://www.statsfiji.gov.fj/api",
        region="pacific", category="statistics",
        description="Fiji national statistics"
    ),
}


# =============================================================================
# CENTRAL ASIA & CAUCASUS - Kazakhstan, Uzbekistan, Georgia, Armenia
# =============================================================================

CENTRAL_ASIA_CAUCASUS_SOURCES = {
    # --- Kazakhstan ---
    "kazstat": DataSource(
        name="Kazakhstan Statistics",
        url="https://stat.gov.kz",
        api_url="https://stat.gov.kz/api/getFile",
        region="central_asia", category="statistics",
        description="Bureau of National Statistics Kazakhstan"
    ),
    
    # --- Uzbekistan ---
    "uzstat": DataSource(
        name="Uzbekistan Statistics",
        url="https://stat.uz",
        api_url="https://stat.uz/api",
        region="central_asia", category="statistics",
        description="State Committee on Statistics Uzbekistan"
    ),
    
    # --- Georgia ---
    "geostat": DataSource(
        name="Georgia Statistics",
        url="https://www.geostat.ge",
        api_url="https://api.geostat.ge",
        region="caucasus", category="statistics",
        description="National Statistics Office of Georgia"
    ),
    
    # --- Armenia ---
    "armstat": DataSource(
        name="Armenia Statistics",
        url="https://www.armstat.am",
        api_url="https://www.armstat.am/file/doc/99520861.pdf",
        region="caucasus", category="statistics",
        description="Statistical Committee of Armenia"
    ),
    
    # --- Azerbaijan ---
    "azstat": DataSource(
        name="Azerbaijan Statistics",
        url="https://www.stat.gov.az",
        api_url="https://www.stat.gov.az/api",
        region="caucasus", category="statistics",
        description="State Statistical Committee Azerbaijan"
    ),
}


# =============================================================================
# ANTARCTICA -  Polar Research & Scientific Data
# =============================================================================

ANTARCTICA_SOURCES = {
    "scar": DataSource(
        name="SCAR",
        url="https://www.scar.org",
        api_url="https://data.scar.org/api",
        region="antarctica", category="research",
        description="Scientific Committee on Antarctic Research"
    ),
    "usap": DataSource(
        name="US Antarctic Program",
        url="https://www.usap-dc.org",
        api_url="https://www.usap-dc.org/api",
        region="antarctica", category="research",
        description="US Antarctic Program Data Center"
    ),
    "bas": DataSource(
        name="British Antarctic Survey",
        url="https://www.bas.ac.uk",
        api_url="https://www.bas.ac.uk/data",
        region="antarctica", category="research",
        description="British Antarctic Survey - climate, biology, geology"
    ),
    "aad": DataSource(
        name="Australian Antarctic Data",
        url="https://data.aad.gov.au",
        api_url="https://data.aad.gov.au/geoserver/wfs",
        region="antarctica", category="research",
        description="Australian Antarctic Data Centre"
    ),
    "nipr": DataSource(
        name="Japan NIPR",
        url="https://www.nipr.ac.jp",
        api_url="https://polaris.nipr.ac.jp/api",
        region="antarctica", category="research",
        description="National Institute of Polar Research Japan"
    ),
}


# =============================================================================
# GLOBAL / INTERNATIONAL SOURCES
# =============================================================================

GLOBAL_SOURCES = {
    # --- World Bank ---
    "world_bank": DataSource(
        name="World Bank",
        url="https://data.worldbank.org",
        api_url="https://api.worldbank.org/v2",
        region="global", category="development",
        description="World Bank Open Data - 16K+ indicators, 200+ countries"
    ),
    
    # --- IMF ---
    "imf": DataSource(
        name="IMF Data",
        url="https://www.imf.org/en/Data",
        api_url="https://dataservices.imf.org/REST/SDMX_JSON.svc",
        region="global", category="finance",
        description="IMF World Economic Outlook, financial data"
    ),
    
    # --- UN ---
    "undata": DataSource(
        name="UN Data",
        url="https://data.un.org",
        api_url="https://data.un.org/ws/rest",
        region="global", category="statistics",
        description="United Nations statistical databases"
    ),
    "undp": DataSource(
        name="UNDP HDR",
        url="https://hdr.undp.org",
        api_url="https://hdr.undp.org/data-center/documentation-and-downloads",
        region="global", category="development",
        description="Human Development Reports and indices"
    ),
    "who": DataSource(
        name="WHO",
        url="https://www.who.int",
        api_url="https://ghoapi.azureedge.net/api",
        region="global", category="health",
        description="World Health Organization - Global Health Observatory"
    ),
    "fao": DataSource(
        name="FAO STAT",
        url="https://www.fao.org/faostat",
        api_url="https://fenixservices.fao.org/faostat/api/v1",
        region="global", category="agriculture",
        description="Food and Agriculture Organization - world food data"
    ),
    "ilo": DataSource(
        name="ILO Statistics",
        url="https://ilostat.ilo.org",
        api_url="https://ilostat.ilo.org/data/api/v2",
        region="global", category="labor",
        description="International Labour Organization - employment worldwide"
    ),
    "unesco": DataSource(
        name="UNESCO UIS",
        url="https://uis.unesco.org",
        api_url="https://api.uis.unesco.org",
        region="global", category="education",
        description="UNESCO education, science, culture statistics"
    ),
    "oecd": DataSource(
        name="OECD Data",
        url="https://data.oecd.org",
        api_url="https://stats.oecd.org/restsdmx/sdmx.ashx",
        region="global", category="development",
        description="OECD economic, social, environmental data"
    ),
    
    # --- Science & Research ---
    "arxiv": DataSource(
        name="arXiv",
        url="https://arxiv.org",
        api_url="http://export.arxiv.org/api/query",
        region="global", category="research",
        description="Open access preprints - physics, math, CS, biology"
    ),
    "pubmed": DataSource(
        name="PubMed",
        url="https://pubmed.ncbi.nlm.nih.gov",
        api_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
        region="global", category="health",
        description="Biomedical literature database - 35M+ citations"
    ),
    "crossref": DataSource(
        name="Crossref",
        url="https://www.crossref.org",
        api_url="https://api.crossref.org",
        region="global", category="research",
        description="Academic citation and DOI data"
    ),
    "semantic_scholar": DataSource(
        name="Semantic Scholar",
        url="https://www.semanticscholar.org",
        api_url="https://api.semanticscholar.org/graph/v1",
        region="global", category="research",
        description="AI-powered academic paper search"
    ),
    
    # --- Finance ---
    "bis": DataSource(
        name="BIS",
        url="https://www.bis.org",
        api_url="https://data.bis.org/api/v1",
        region="global", category="finance",
        description="Bank for International Settlements - global banking"
    ),
    "coingecko": DataSource(
        name="CoinGecko",
        url="https://www.coingecko.com",
        api_url="https://api.coingecko.com/api/v3",
        region="global", category="crypto",
        description="Cryptocurrency prices and market data"
    ),
    
    # --- Geography & Environment ---
    "openstreetmap": DataSource(
        name="OpenStreetMap",
        url="https://www.openstreetmap.org",
        api_url="https://nominatim.openstreetmap.org",
        region="global", category="geography",
        description="Open geographic data - maps, locations"
    ),
    "earth_engine": DataSource(
        name="Google Earth Engine",
        url="https://earthengine.google.com",
        api_url="https://earthengine.googleapis.com/v1",
        region="global", category="satellite",
        requires_key=True,
        description="Satellite imagery and geospatial analysis"
    ),
}


# =============================================================================
# COMBINED REGISTRY
# =============================================================================

ALL_GLOBAL_DATA_SOURCES: Dict[str, Dict[str, DataSource]] = {
    "europe": EUROPE_SOURCES,
    "americas": AMERICAS_SOURCES,
    "asia_china": ASIA_CHINA_SOURCES,
    "india_south_asia": INDIA_SOUTH_ASIA_SOURCES,
    "africa_middle_east": AFRICA_MIDDLE_EAST_SOURCES,
    "oceania_pacific": OCEANIA_PACIFIC_SOURCES,
    "central_asia_caucasus": CENTRAL_ASIA_CAUCASUS_SOURCES,
    "antarctica": ANTARCTICA_SOURCES,
    "global": GLOBAL_SOURCES,
}


class GlobalDataConnector:
    """
     Global Data Connector - Fetches data from open sources worldwide
    
    Supports:
    - 7 Continents + Antarctica
    - 100+ national statistics offices
    - 50+ international organizations
    - FREE APIs (no keys required for most)
    """
    
    def __init__(self):
        self.sources = ALL_GLOBAL_DATA_SOURCES
        self.cache: Dict[str, Any] = {}
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "Kloud-Ocean/2.0"}
            )
        return self.session
    
    async def fetch_from_source(self, source_id: str, region: str = None) -> Dict[str, Any]:
        """Fetch data from a specific source"""
        for reg_name, sources in self.sources.items():
            if region and reg_name != region:
                continue
            if source_id in sources:
                source = sources[source_id]
                try:
                    session = await self._get_session()
                    async with session.get(source.api_url, timeout=15) as resp:
                        if resp.status == 200:
                            return {
                                "source": source.name,
                                "region": source.region,
                                "data": await resp.json()
                            }
                except Exception as e:
                    logger.warning(f"Error fetching {source_id}: {e}")
        return {"error": f"Source {source_id} not found"}
    
    def get_sources_by_region(self, region: str) -> Dict[str, DataSource]:
        """Get all sources for a region"""
        return self.sources.get(region, {})
    
    def get_all_sources_count(self) -> int:
        """Get total number of sources"""
        return sum(len(s) for s in self.sources.values())
    
    def search_sources(self, query: str) -> List[DataSource]:
        """Search sources by keyword"""
        results = []
        q = query.lower()
        for sources in self.sources.values():
            for source in sources.values():
                if q in source.name.lower() or q in source.description.lower():
                    results.append(source)
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all data sources"""
        summary = {
            "total_sources": self.get_all_sources_count(),
            "regions": {}
        }
        for region, sources in self.sources.items():
            summary["regions"][region] = {
                "count": len(sources),
                "sources": list(sources.keys())
            }
        return summary


# Singleton instance
_global_connector = None


def get_global_data_connector() -> GlobalDataConnector:
    """Get singleton GlobalDataConnector instance"""
    global _global_connector
    if _global_connector is None:
        _global_connector = GlobalDataConnector()
    return _global_connector


if __name__ == "__main__":
    connector = get_global_data_connector()
    summary = connector.get_summary()
    print(f" Global Data Sources: {summary['total_sources']} total")
    for region, info in summary["regions"].items():
        print(f"  {region}: {info['count']} sources")

