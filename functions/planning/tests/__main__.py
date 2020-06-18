import json
import unittest

from functions.planning.main import generate_planning


class TestPlanning(unittest.TestCase):

    def test_generate_planning(self):
        """
        Check to see if the planning returns without errors
        """
        with open('tests/data/generic/engineers.json') as json_file:
            engineers = json.load(json_file)

        with open('tests/data/generic/workitems.json') as json_file:
            work_items = json.load(json_file)

        with open('tests/data/generic/carlocations.json') as json_file:
            car_locations = json.load(json_file)

        generate_planning(20, False, False, work_items=work_items, car_locations=car_locations, engineers=engineers)

    def test_priority_planning(self):
        """
        Check to see if a planning with some prioritized items returns a correct planning.
        """
        with open('tests/data/priority/engineers.json') as json_file:
            engineers = json.load(json_file)

        with open('tests/data/priority/workitems.json') as json_file:
            work_items = json.load(json_file)

        with open('tests/data/priority/carlocations.json') as json_file:
            car_locations = json.load(json_file)

        planned_workitems, unplanned_engineers, unplanned_workitems, metadata = \
            generate_planning(20,
                              False,
                              False,
                              work_items=work_items,
                              car_locations=car_locations,
                              engineers=engineers)

        self.assertEqual(unplanned_engineers, [])

        self.assertEqual(len(planned_workitems), 10)
        self.assertEqual(sorted([x['workitem'] for x in planned_workitems]), [1, 2, 6, 7, 8, 15, 16, 28, 29, 30])

        self.assertEqual(len(unplanned_workitems), 20)
        self.assertEqual(sorted(unplanned_workitems), [3, 4, 5, 9, 10, 11, 12, 13, 14, 17,
                                                       18, 19, 20, 21, 22, 23, 24, 25, 26, 27])


if __name__ == '__main__':
    unittest.main()
