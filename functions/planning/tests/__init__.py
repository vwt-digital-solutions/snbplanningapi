import json
import unittest

from functions.planning.main import generate_planning


class TestPlanning(unittest.TestCase):

    def test_generate_planning(self):
        with open('tests/data/engineers.json') as json_file:
            engineers = json.load(json_file)

        with open('tests/data/workitems.json') as json_file:
            work_items = json.load(json_file)

        with open('tests/data/carlocations.json') as json_file:
            car_locations = json.load(json_file)

        generate_planning(20, False, False, work_items=work_items, car_locations=car_locations, engineers=engineers)


if __name__ == '__main__':
    unittest.main()
