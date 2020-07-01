import json
import unittest

from functions.planning.main import generate_planning


def load_data_from_files(directory):
    with open('tests/data/{0}/engineers.json'.format(directory)) as json_file:
        engineers = json.load(json_file)

    with open('tests/data/{0}/workitems.json'.format(directory)) as json_file:
        work_items = json.load(json_file)

    with open('tests/data/{0}/carlocations.json'.format(directory)) as json_file:
        car_locations = json.load(json_file)

    return engineers, work_items, car_locations


class TestPlanning(unittest.TestCase):

    def test_generate_planning(self):
        """
        Check to see if the planning returns without errors.
        """
        engineers, work_items, car_locations = load_data_from_files('generic')

        generate_planning(20, False, False, work_items=work_items, car_locations=car_locations, engineers=engineers)

    def test_priority_planning(self):
        """
        Check to see if a planning with some prioritized items returns a correct planning.
        """
        engineers, work_items, car_locations = load_data_from_files('priority')

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

    def test_home_address_planning(self):
        engineers, work_items, car_locations = load_data_from_files('home_addresses')

        planned_workitems, unplanned_engineers, unplanned_workitems, metadata = \
            generate_planning(20,
                              False,
                              False,
                              work_items=work_items,
                              car_locations=car_locations,
                              engineers=engineers)

        self.assertEqual(unplanned_engineers, [])
        self.assertEqual(len(planned_workitems), 10)

    def test_niet_gereed_planning(self):
        engineers, work_items, car_locations = load_data_from_files('niet_gereed')

        planned_workitems, unplanned_engineers, unplanned_workitems, metadata = \
            generate_planning(5,
                              False,
                              False,
                              work_items=work_items,
                              car_locations=car_locations,
                              engineers=engineers)

        self.assertEqual(unplanned_engineers, [])
        self.assertEqual(len(unplanned_workitems), 1)
        self.assertEqual(unplanned_workitems[0], 5)
        self.assertEqual(len(planned_workitems), 10)


if __name__ == '__main__':
    unittest.main()
