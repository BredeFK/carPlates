import os
from datetime import datetime

from car import Car
from car_details import fetch_car_details
from database import create_tables, get_car_by_plate, insert_car
from read_plate import read_plate

MODEL = 'qwen3-vl'
DB_PATH = 'cars.db'


def main():
    create_tables(DB_PATH)
    results = _fetch_plates()
    car_details = _fetch_details(results)
    for car_detail in car_details:
        print(car_detail)
    # _write_result_to_file(results)
    # compare_plate_results()


def _fetch_plates() -> dict[str, str]:
    print(f"Starting read_plate.py using '{MODEL}' ...")
    paths = _get_image_paths('./cars')
    results = {}
    for path in paths:
        plate = read_plate(path, MODEL)
        results[path] = plate
        print(f'path: {path}, plate: {plate}')
    return results


def _fetch_details(results: dict[str, str]) -> list[Car]:
    car_detail_list: list[Car | str] = []
    for path in results:
        plate = results[path]
        if plate is not None:
            try:
                car_detail = get_car_by_plate(DB_PATH, plate)
                if car_detail is None:
                    car_detail = fetch_car_details(plate)
                    insert_car(DB_PATH, car_detail)
                else:
                    print(f'{plate} is already in the database')
                    car_detail_list.append(car_detail)
            except Exception as e:
                car_detail_list.append(f"Something went wrong with plate {plate}: {str(e)}")
    return car_detail_list


def _format_path_name(image_path: str) -> str:
    return image_path.replace('\\', '/')


def _get_image_paths(directory: str) -> list[str]:
    image_paths: list[str] = []
    for filename in os.listdir(directory):
        image_paths.append(_format_path_name(os.path.join(directory, filename)))
    return image_paths


def _write_result_to_file(results: dict[str, str]) -> None:
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    file_name: str = _format_path_name(f'result_{MODEL}_{timestamp}.csv')
    if not os.path.exists("results") or not os.path.isdir("results"):
        os.mkdir("results")

    file_path: str = os.path.join("results", file_name)
    with open(file_path, 'w', newline='') as csvfile:
        csvfile.write('PATH,RESULT\n')
        for path in results:
            result = results[path]
            csvfile.write(f"{path},{result}\n")


if __name__ == "__main__":
    main()
