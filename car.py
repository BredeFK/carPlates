import re
from dataclasses import dataclass
from datetime import datetime, date

NORWAY_PLATE_REGEX = re.compile(r"^[A-ZÆØÅ]{2}\d{4,5}$")


@dataclass
class Car:
    plate: str
    first_registered_in_norway: date
    vehicle_category: str
    dimension: Dimensions
    manufacturer_name: str
    brand: str
    model_name: str
    driving_side: str
    color_name: str
    color_description: str
    fuel_type: str
    fuel_consumption_liter_per_10km: float
    wltp_combined_range_km: int
    transmission_type: str
    maximum_speed_kmh: int
    inspection_due_date: date
    last_inspection_approved_date: date
    owner_registration_start_timestamp: datetime


@dataclass
class Dimensions:
    width: int
    height: int
    length: int


def plate_is_valid(plate: str) -> bool:
    if not plate:
        return False
    clean_plate = plate.replace(' ', '').replace('-', '')
    return bool(NORWAY_PLATE_REGEX.fullmatch(clean_plate))


def parse_car_from_json(json_data: dict) -> Car:
    fuel_consumption_liter_per_10km: float | None = None
    wltp_combined_range_km: int | None = None

    root = json_data['kjoretoydataListe'][0]
    technical_approval = root['godkjenning']['tekniskGodkjenning']
    general = technical_approval['tekniskeData']["generelt"]
    color = technical_approval['tekniskeData']['karosseriOgLasteplan']['rFarge'][0]
    environment_and_fuel_group = technical_approval['tekniskeData']['miljodata']['miljoOgdrivstoffGruppe'][0]

    plate = root['kjoretoyId'].get('kjennemerke')
    first_registered_in_norway = root['forstegangsregistrering'].get('registrertForstegangNorgeDato')
    vehicle_category = technical_approval['kjoretoyklassifisering'].get('beskrivelse')

    dimensions_raw = technical_approval['tekniskeData']['dimensjoner']
    dimensions = Dimensions(dimensions_raw.get('bredde'), dimensions_raw.get('hoyde'), dimensions_raw.get('lengde'))

    manufacturer_name = general['fabrikant'][0].get('fabrikantNavn')
    brand = general['merke'][0].get('merke')
    model_name = general['handelsbetegnelse'][0]

    driving_side = technical_approval['tekniskeData']['karosseriOgLasteplan'].get('kjoringSide')
    color_name = color.get('kodeNavn')
    color_description = color.get('kodeBeskrivelse')

    fuel_type = environment_and_fuel_group['drivstoffKodeMiljodata'].get('kodeNavn')
    if str(fuel_type).lower() == 'elektrisk':
        wltp_combined_range_km = environment_and_fuel_group['forbrukOgUtslipp'][0]['wltpKjoretoyspesifikk'].get(
            'rekkeviddeKmBlandetkjoring') or None
    else:
        fuel_consumption_liter_per_100km = environment_and_fuel_group['forbrukOgUtslipp'][0].get(
            'forbrukBlandetKjoring') or None
        fuel_consumption_liter_per_10km = float(fuel_consumption_liter_per_100km) / 10

    transmission_type = technical_approval['tekniskeData']['motorOgDrivverk']['girkassetype'].get('kodeNavn')

    maximum_speed_kmh = technical_approval['tekniskeData']['motorOgDrivverk'].get('maksimumHastighet')[0]
    inspection_due_date = root['periodiskKjoretoyKontroll'].get('kontrollfrist')
    last_inspection_approved_date = root['periodiskKjoretoyKontroll'].get('sistGodkjent')

    owner_registration_start_timestamp = root['registrering'].get('fomTidspunkt')

    return Car(plate, first_registered_in_norway, vehicle_category, dimensions, manufacturer_name, brand, model_name,
               driving_side, color_name, color_description, fuel_type, fuel_consumption_liter_per_10km,
               wltp_combined_range_km,
               transmission_type, int(maximum_speed_kmh), inspection_due_date, last_inspection_approved_date,
               owner_registration_start_timestamp)
