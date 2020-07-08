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

    with open('tests/data/{0}/availabilities.json'.format(directory)) as json_file:
        availabilities = json.load(json_file)

    return engineers, work_items, car_locations, availabilities


class TestPlanning(unittest.TestCase):

    def test_generate_planning(self):
        """
        Check to see if the planning returns without errors.
        """
        engineers, work_items, car_locations, availabilities = load_data_from_files('generic')

        generate_planning(20, False, False, work_items=work_items, car_locations=car_locations, engineers=engineers)

    def test_priority_planning(self):
        """
        Check to see if a planning with some prioritized items returns a correct planning.
        """
        engineers, work_items, car_locations, availabilities = load_data_from_files('priority')

        planned_workitems, unplanned_engineers, unplanned_workitems, metadata = \
            generate_planning(20,
                              False,
                              False,
                              work_items=work_items,
                              car_locations=car_locations,
                              engineers=engineers)

        self.assertEqual(unplanned_engineers, [])

        self.assertEqual(len(planned_workitems), 10)
        self.assertEqual(len(unplanned_workitems), 20)

    def test_home_address_planning(self):
        engineers, work_items, car_locations, availabilities = load_data_from_files('home_addresses')

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
        engineers, work_items, car_locations, availabilities = load_data_from_files('niet_gereed')

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

    def test_availabilities(self):
        engineers, work_items, car_locations, availabilities = load_data_from_files('availabilities')

        planned_workitems, unplanned_engineers, unplanned_workitems, metadata = \
            generate_planning(5,
                              False,
                              False,
                              work_items=work_items,
                              car_locations=car_locations,
                              engineers=engineers,
                              availabilities=availabilities)

        # Engineer 7 has an incompatible schedule with any of the workitems
        self.assertIn(7, unplanned_engineers)

        # Workitem 1 is in the afternoon, the only engineer available by then is engineer 8
        self.assertIn({'engineer': 8, 'workitem': 1}, planned_workitems)

        # Workitem 5 does not have a specified start and end time, but they should be planned anyway.
        self.assertIn(5, [planning_item['workitem'] for planning_item in planned_workitems])

        # Engineer 3 has an appointment overlapping with every workitem, so they should be unplanned:
        self.assertIn(3, unplanned_engineers)

        # Engineer 2 has an appointment and is only available for workitem 5 (which does not have a specified end_time):
        self.assertIn({'engineer': 2, 'workitem': 5}, planned_workitems)

        return True


if __name__ == '__main__':
    unittest.main()
