import os
from datetime import datetime

from read_plate import read_plate
from util import compare_plate_results

MODEL = 'qwen3-vl'


def main():
    print(f"Starting read_plate.py using '{MODEL}' ...")
    paths = _get_image_paths('./cars')
    results = {}
    for path in paths:
        plate = read_plate(path, MODEL)
        results[path] = plate
        print(f'path: {path}, plate: {plate}')
    _write_result_to_file(results)
    compare_plate_results()


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
