#!/usr/bin/env python

import unittest

import mock
from suds.sudsobject import Factory

from labmanager import api


def create_suds_type(name='FakeSudsObject', **kwargs):
    return Factory.object(name, kwargs)


class TestTypeConversions(unittest.TestCase):
    def test_convert_to_dict(self):
        # First just show the api for the factory object.
        suds_type = create_suds_type(foo='bar')
        self.assertEqual(suds_type.foo, 'bar')
        self.assertEqual(suds_type.__class__.__name__,
                         'FakeSudsObject')

        self.assertEqual(api.suds_to_dict_type(suds_type),
                         {'foo': 'bar'})


class TestLabManagerAPI(unittest.TestCase):
    def setUp(self):
        self.client = mock.Mock()
        self.lmapi = api.LabManager(self.client)

    # I'm not super interested in testing every single API call that's just a 1
    # to 1 mapping of the public soap API, so for now, at least one of each
    # type should be verified, specifically, one that returns a list of dicts,
    # one that returns a dict, and one that returns nothing.

    def test_list_all_configurations(self):
        # Just configure the mock to return the same value
        # for both the workspace and library type.
        self.client.service.ListConfigurations.return_value = [
            [create_suds_type(foo='bar')]
        ]

        all_configs = self.lmapi.list_all_configurations()

        self.assertEqual(all_configs, [{'foo': 'bar'}, {'foo': 'bar'}])
        expected_args = [((self.lmapi.WORKSPACE_CONFIGURATION,),),
                         ((self.lmapi.LIBRARY_CONFIGURATIONS,),)]
        self.assertEqual(
            self.client.service.ListConfigurations.call_args_list,
            expected_args)

    def test_show_one_configuration(self):
        self.client.service.GetConfiguration.return_value = \
            create_suds_type(foo='bar')
        one_configuration = self.lmapi.show_configuration(54)
        self.assertEqual(one_configuration, {'foo': 'bar'})
        self.client.service.GetConfiguration.assert_called_with(54)

    def test_deploy_configuration(self):
        self.lmapi.deploy_configuration(54, self.lmapi.FENCE_ALLOW_IN_AND_OUT)
        # TODO: This is not a complete tests.
        self.client.service.ConfigurationDeploy(
            54, False, self.lmapi.FENCE_ALLOW_IN_AND_OUT)

    def test_machine_perform_action(self):
        self.lmapi.perform_machine_action(self.lmapi.POWER_ON, 54)
        self.client.service.MachinePerformAction.assert_called_with(54, 1)


if __name__ == '__main__':
    unittest.main()
