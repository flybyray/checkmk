#!/usr/bin/env python3
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping, Sequence

import pytest

from cmk.base.plugins.agent_based import brocade_optical
from cmk.base.plugins.agent_based.agent_based_api.v1 import Metric, Result, Service, State
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult
from cmk.base.plugins.agent_based.utils import interfaces


@pytest.mark.parametrize(
    "params, expect_service",
    [
        (
            [(interfaces.DISCOVERY_DEFAULT_PARAMETERS)],
            True,
        ),
        (
            [
                {
                    "discovery_single": (False, {}),
                    "matching_conditions": (True, {}),
                },
                (interfaces.DISCOVERY_DEFAULT_PARAMETERS),
            ],
            False,
        ),
        (
            [
                {
                    "discovery_single": (
                        True,
                        {
                            "item_appearance": "alias",
                            "pad_portnumbers": True,
                        },
                    ),
                    "matching_conditions": (
                        False,
                        {"porttypes": ["6"], "portstates": ["1", "3"]},
                    ),
                },
                (interfaces.DISCOVERY_DEFAULT_PARAMETERS),
            ],
            True,
        ),
        (
            [
                {
                    "discovery_single": (
                        True,
                        {
                            "item_appearance": "index",
                            "pad_portnumbers": True,
                        },
                    ),
                    "matching_conditions": (
                        False,
                        {"match_desc": ["10GigabitEthernet"]},
                    ),
                },
                (interfaces.DISCOVERY_DEFAULT_PARAMETERS),
            ],
            True,
        ),
    ],
)
def test_discover_brocade_optical(
    params: Sequence[Mapping[str, object]], expect_service: bool
) -> None:
    section: brocade_optical.Section = {
        "1410": {
            "description": "10GigabitEthernet23/2",
            "operational_status": "1",
            "part": "57-0000076-01",
            "port_type": "6",
            "rx_light": (-36.9897, "Low-Alarm"),
            "serial": "ADF2094300014UN",
            "temp": (31.4882, "Normal"),
            "tx_light": (-1.4508, "Normal"),
            "type": "10GE LR 10km SFP+",
        }
    }
    services = [Service(item="1410", parameters={}, labels=[])]
    assert list(
        brocade_optical.discover_brocade_optical(
            params,
            section,
        )
    ) == (expect_service and services or [])


@pytest.mark.usefixtures("initialised_item_state")
@pytest.mark.parametrize(
    "item,params,section,expected",
    [
        (
            "001410",
            {},
            {
                "1410": {
                    "description": "10GigabitEthernet23/2",
                    "operational_status": "2",
                    "part": "57-0000076-01",
                    "port_type": "6",
                    "rx_light": (-36.9897, "Low-Alarm"),
                    "serial": "ADF2094300014UN",
                    "temp": (31.4882, "Normal"),
                    "tx_light": (-1.4508, "Normal"),
                    "type": "10GE LR 10km SFP+",
                }
            },
            [
                Result(
                    state=State.OK,
                    summary="[S/N ADF2094300014UN, P/N 57-0000076-01] Operational down",
                ),
                Metric("temp", 31.4882),
                Result(state=State.OK, summary="Temperature: 31.5°C"),
                Result(
                    state=State.OK,
                    notice="Configuration: prefer user levels over device levels (no levels found)",
                ),
                Result(state=State.OK, summary="TX Light -1.5 dBm (Normal)"),
                Metric("tx_light", -1.4508),
                Result(state=State.OK, summary="RX Light -37.0 dBm (Low-Alarm)"),
                Metric("rx_light", -36.9897),
            ],
        ),
        (
            "1409",
            {"rx_light": True, "tx_light": True, "lanes": True},
            {
                "1409": {
                    "description": "10GigabitEthernet23/1",
                    "lanes": {
                        1: {
                            "rx_light": (-2.2504, "Normal"),
                            "temp": (31.4531, "Normal"),
                            "tx_light": (-1.6045, "Normal"),
                        }
                    },
                    "operational_status": "1",
                    "part": "57-0000076-01",
                    "port_type": "6",
                    "rx_light": (-2.2504, "Normal"),
                    "serial": "ADF2094300014TL",
                    "temp": (None, None),
                    "tx_light": (-1.6045, "Normal"),
                    "type": "10GE LR 10km SFP+",
                }
            },
            [
                Result(
                    state=State.OK,
                    summary="[S/N ADF2094300014TL, P/N 57-0000076-01] Operational up",
                ),
                Result(state=State.OK, summary="TX Light -1.6 dBm (Normal)"),
                Metric("tx_light", -1.6045),
                Result(state=State.OK, summary="RX Light -2.3 dBm (Normal)"),
                Metric("rx_light", -2.2504),
                Result(state=State.OK, notice="Temperature (Lane 1) Temperature: 31.5°C"),
                Metric("port_temp_1", 31.4531),
                Result(state=State.OK, notice="TX Light (Lane 1) -1.6 dBm (Normal)"),
                Metric("tx_light_1", -1.6045),
                Result(state=State.OK, notice="RX Light (Lane 1) -2.3 dBm (Normal)"),
                Metric("rx_light_1", -2.2504),
            ],
        ),
    ],
)
def test_check_brocade_optical(
    item: str, params: Mapping[str, object], section: brocade_optical.Section, expected: CheckResult
) -> None:
    assert list(brocade_optical.check_brocade_optical(item, params, section)) == expected


# Disable auto-formatting here as it takes ages
# fmt: off
@pytest.mark.usefixtures("initialised_item_state")
@pytest.mark.parametrize('string_table, discovery_results, items_params_results', [
    (
        [
            [['1', '10GigabitEthernet1/1/1', '6', '1'],
             ['2', '10GigabitEthernet1/1/2', '6', '2'],
             ['3', '10GigabitEthernet1/1/3', '6', '1'],
             ['4', '10GigabitEthernet1/1/4', '6', '2'],
             ['5', '10GigabitEthernet1/1/5', '6', '1'],
             ['6', '10GigabitEthernet1/1/6', '6', '2'],
             ['7', '10GigabitEthernet1/1/7', '6', '1'],
             ['8', '10GigabitEthernet1/1/8', '6', '2'],
             ['9', '10GigabitEthernet1/1/9', '6', '1'],
             ['10', '10GigabitEthernet1/1/10', '6', '2'],
             ['11', '10GigabitEthernet1/1/11', '6', '1'],
             ['12', '10GigabitEthernet1/1/12', '6', '2'],
             ['13', '10GigabitEthernet1/1/13', '6', '2'],
             ['14', '10GigabitEthernet1/1/14', '6', '2'],
             ['15', '10GigabitEthernet1/1/15', '6', '2'],
             ['16', '10GigabitEthernet1/1/16', '6', '2'],
             ['17', '10GigabitEthernet1/1/17', '6', '2'],
             ['18', '10GigabitEthernet1/1/18', '6', '2'],
             ['19', '10GigabitEthernet1/1/19', '6', '2'],
             ['20', '10GigabitEthernet1/1/20', '6', '2'],
             ['21', '10GigabitEthernet1/1/21', '6', '2'],
             ['22', '10GigabitEthernet1/1/22', '6', '2'],
             ['23', '10GigabitEthernet1/1/23', '6', '2'],
             ['24', '10GigabitEthernet1/1/24', '6', '2'],
             ['25', '10GigabitEthernet1/1/25', '6', '2'],
             ['26', '10GigabitEthernet1/1/26', '6', '2'],
             ['27', '10GigabitEthernet1/1/27', '6', '2'],
             ['28', '10GigabitEthernet1/1/28', '6', '2'],
             ['29', '10GigabitEthernet1/1/29', '6', '2'],
             ['30', '10GigabitEthernet1/1/30', '6', '2'],
             ['31', '10GigabitEthernet1/1/31', '6', '2'],
             ['32', '10GigabitEthernet1/1/32', '6', '2'],
             ['33', '10GigabitEthernet1/1/33', '6', '2'],
             ['34', '10GigabitEthernet1/1/34', '6', '2'],
             ['35', '10GigabitEthernet1/1/35', '6', '2'],
             ['36', '10GigabitEthernet1/1/36', '6', '2'],
             ['37', '10GigabitEthernet1/1/37', '6', '2'],
             ['38', '10GigabitEthernet1/1/38', '6', '2'],
             ['39', '10GigabitEthernet1/1/39', '6', '2'],
             ['40', '10GigabitEthernet1/1/40', '6', '2'],
             ['41', '10GigabitEthernet1/1/41', '6', '2'],
             ['42', '10GigabitEthernet1/1/42', '6', '2'],
             ['43', '10GigabitEthernet1/1/43', '6', '2'],
             ['44', '10GigabitEthernet1/1/44', '6', '2'],
             ['45', '10GigabitEthernet1/1/45', '6', '2'],
             ['46', '10GigabitEthernet1/1/46', '6', '2'],
             ['47', '10GigabitEthernet1/1/47', '6', '2'],
             ['48', '10GigabitEthernet1/1/48', '6', '2'], ['49', 'Management', '6', '2'],
             ['65', '40GigabitEthernet1/2/1', '6', '1'],
             ['69', '40GigabitEthernet1/2/2', '6', '2'],
             ['73', '40GigabitEthernet1/2/3', '6', '2'],
             ['77', '40GigabitEthernet1/2/4', '6', '1'],
             ['81', '40GigabitEthernet1/2/5', '6', '2'],
             ['85', '40GigabitEthernet1/2/6', '6', '2'],
             ['129', '40GigabitEthernet1/3/1', '6', '1'],
             ['133', '40GigabitEthernet1/3/2', '6', '2'],
             ['137', '40GigabitEthernet1/3/3', '6', '2'],
             ['141', '40GigabitEthernet1/3/4', '6', '2'],
             ['145', '40GigabitEthernet1/3/5', '6', '2'],
             ['149', '40GigabitEthernet1/3/6', '6', '2'],
             ['257', '10GigabitEthernet2/1/1', '6', '1'],
             ['258', '10GigabitEthernet2/1/2', '6', '2'],
             ['259', '10GigabitEthernet2/1/3', '6', '1'],
             ['260', '10GigabitEthernet2/1/4', '6', '2'],
             ['261', '10GigabitEthernet2/1/5', '6', '1'],
             ['262', '10GigabitEthernet2/1/6', '6', '2'],
             ['263', '10GigabitEthernet2/1/7', '6', '1'],
             ['264', '10GigabitEthernet2/1/8', '6', '2'],
             ['265', '10GigabitEthernet2/1/9', '6', '1'],
             ['266', '10GigabitEthernet2/1/10', '6', '2'],
             ['267', '10GigabitEthernet2/1/11', '6', '1'],
             ['268', '10GigabitEthernet2/1/12', '6', '2'],
             ['269', '10GigabitEthernet2/1/13', '6', '2'],
             ['270', '10GigabitEthernet2/1/14', '6', '2'],
             ['271', '10GigabitEthernet2/1/15', '6', '2'],
             ['272', '10GigabitEthernet2/1/16', '6', '2'],
             ['273', '10GigabitEthernet2/1/17', '6', '2'],
             ['274', '10GigabitEthernet2/1/18', '6', '2'],
             ['275', '10GigabitEthernet2/1/19', '6', '2'],
             ['276', '10GigabitEthernet2/1/20', '6', '2'],
             ['277', '10GigabitEthernet2/1/21', '6', '2'],
             ['278', '10GigabitEthernet2/1/22', '6', '2'],
             ['279', '10GigabitEthernet2/1/23', '6', '2'],
             ['280', '10GigabitEthernet2/1/24', '6', '2'],
             ['281', '10GigabitEthernet2/1/25', '6', '2'],
             ['282', '10GigabitEthernet2/1/26', '6', '2'],
             ['283', '10GigabitEthernet2/1/27', '6', '2'],
             ['284', '10GigabitEthernet2/1/28', '6', '2'],
             ['285', '10GigabitEthernet2/1/29', '6', '2'],
             ['286', '10GigabitEthernet2/1/30', '6', '2'],
             ['287', '10GigabitEthernet2/1/31', '6', '2'],
             ['288', '10GigabitEthernet2/1/32', '6', '2'],
             ['289', '10GigabitEthernet2/1/33', '6', '2'],
             ['290', '10GigabitEthernet2/1/34', '6', '2'],
             ['291', '10GigabitEthernet2/1/35', '6', '2'],
             ['292', '10GigabitEthernet2/1/36', '6', '2'],
             ['293', '10GigabitEthernet2/1/37', '6', '2'],
             ['294', '10GigabitEthernet2/1/38', '6', '2'],
             ['295', '10GigabitEthernet2/1/39', '6', '2'],
             ['296', '10GigabitEthernet2/1/40', '6', '2'],
             ['297', '10GigabitEthernet2/1/41', '6', '2'],
             ['298', '10GigabitEthernet2/1/42', '6', '2'],
             ['299', '10GigabitEthernet2/1/43', '6', '2'],
             ['300', '10GigabitEthernet2/1/44', '6', '2'],
             ['301', '10GigabitEthernet2/1/45', '6', '2'],
             ['302', '10GigabitEthernet2/1/46', '6', '2'],
             ['303', '10GigabitEthernet2/1/47', '6', '2'],
             ['304', '10GigabitEthernet2/1/48', '6', '2'],
             ['321', '40GigabitEthernet2/2/1', '6', '1'],
             ['325', '40GigabitEthernet2/2/2', '6', '2'],
             ['329', '40GigabitEthernet2/2/3', '6', '2'],
             ['333', '40GigabitEthernet2/2/4', '6', '1'],
             ['337', '40GigabitEthernet2/2/5', '6', '2'],
             ['341', '40GigabitEthernet2/2/6', '6', '2'],
             ['385', '40GigabitEthernet2/3/1', '6', '1'],
             ['389', '40GigabitEthernet2/3/2', '6', '1'],
             ['393', '40GigabitEthernet2/3/3', '6', '2'],
             ['397', '40GigabitEthernet2/3/4', '6', '2'],
             ['401', '40GigabitEthernet2/3/5', '6', '2'],
             ['405', '40GigabitEthernet2/3/6', '6', '2'], ['3073', 'lg1', '6', '1'],
             ['3074', 'lg2', '6', '1'], ['3075', 'lg3', '6', '1'],
             ['3076', 'lg4', '6', '1'], ['3077', 'lg5', '6', '1'],
             ['3078', 'lg6', '6', '1'], ['3079', 'lg7', '6', '1'],
             ['16777217', 'v30', '135', '1']],
            [],
            [],
            [['28.5273 C Normal', '-002.2373 dBm Normal', '-002.4298 dBm Normal', '3.1'],
             ['28.8945 C Normal', '-002.2848 dBm Normal', '-002.3597 dBm Normal', '5.1'],
             ['29.3554 C Normal', '-002.2944 dBm Normal', '-002.8474 dBm Normal', '7.1'],
             ['28.2851 C Normal', '-002.2789 dBm Normal', '-002.7278 dBm Normal', '9.1'],
             ['26.0507 C Normal', '-002.2848 dBm Normal', '-004.1953 dBm Normal', '11.1'],
             ['25.5468 C Normal', '-002.2723 dBm Normal', '-002.3942 dBm Normal', '259.1'],
             ['26.5156 C Normal', '-002.2635 dBm Normal', '-002.4116 dBm Normal', '261.1'],
             ['27.7500 C Normal', '-002.2672 dBm Normal', '-002.2760 dBm Normal', '263.1'],
             ['25.4765 C Normal', '-002.2519 dBm Normal', '-002.1331 dBm Normal', '265.1'],
             ['26.9257 C Normal', '-002.2716 dBm Normal', '-002.5251 dBm Normal', '267.1'],
             ['', '', '', '321.1'], ['', '', '', '321.2'], ['', '', '', '321.3'],
             ['', '', '', '321.4'], ['', '', '', '333.1'], ['', '', '', '333.2'],
             ['', '', '', '333.3'], ['', '', '', '333.4']],
        ],
        [],
        [],
    ),
    (
        [
            [['1409', '10GigabitEthernet23/1', '6', '1'],
             ['1410', '10GigabitEthernet23/2', '6', '2'],
             ['1411', '10GigabitEthernet23/3', '6', '2'],
             ['1412', '10GigabitEthernet23/4', '6', '2'],
             ['1413', '10GigabitEthernet23/5', '6', '2'],
             ['1414', '10GigabitEthernet23/6', '6', '2'],
             ['1415', '10GigabitEthernet23/7', '6', '2'],
             ['1416', '10GigabitEthernet23/8', '6', '2'],
             ['1473', '10GigabitEthernet24/1', '6', '2'],
             ['1474', '10GigabitEthernet24/2', '6', '2'],
             ['1475', '10GigabitEthernet24/3', '6', '2'],
             ['1476', '10GigabitEthernet24/4', '6', '2'],
             ['1477', '10GigabitEthernet24/5', '6', '2'],
             ['1478', '10GigabitEthernet24/6', '6', '2'],
             ['1479', '10GigabitEthernet24/7', '6', '2'],
             ['1480', '10GigabitEthernet24/8', '6', '2'],
             ['1793', '10GigabitEthernet29/1', '6', '2'],
             ['1794', '10GigabitEthernet29/2', '6', '2'],
             ['1795', '10GigabitEthernet29/3', '6', '2'],
             ['1796', '10GigabitEthernet29/4', '6', '2'],
             ['1857', '10GigabitEthernet30/1', '6', '1'],
             ['1858', '10GigabitEthernet30/2', '6', '1'],
             ['1859', '10GigabitEthernet30/3', '6', '1'],
             ['1860', '10GigabitEthernet30/4', '6', '1'],
             ['1921', '10GigabitEthernet31/1', '6', '1'],
             ['1922', '10GigabitEthernet31/2', '6', '1'],
             ['1923', '10GigabitEthernet31/3', '6', '1'],
             ['1924', '10GigabitEthernet31/4', '6', '1'],
             ['1985', '10GigabitEthernet32/1', '6', '2'],
             ['1986', '10GigabitEthernet32/2', '6', '2'],
             ['1987', '10GigabitEthernet32/3', '6', '2'],
             ['1988', '10GigabitEthernet32/4', '6', '2'],
             ['2049', 'EthernetManagement1', '6', '1'], ['33554433', 'lb1', '24', '1'],
             ['67108864', 'tnl0', '150', '1'], ['67108865', 'tnl1', '150', '1'],
             ['67108866', 'tnl2', '150', '1'], ['67108867', 'tnl3', '150', '1'],
             ['67108868', 'tnl4', '150', '1'], ['67108869', 'tnl5', '150', '1'],
             ['67108870', 'tnl6', '150', '1'], ['67108871', 'tnl7', '150', '1'],
             ['67108872', 'tnl8', '150', '1'], ['67108873', 'tnl9', '150', '1'],
             ['67108874', 'tnl10', '150', '1'], ['67108875', 'tnl11', '150', '1'],
             ['67108876', 'tnl12', '150', '1'], ['67108877', 'tnl13', '150', '1'],
             ['67108878', 'tnl14', '150', '1'], ['67108879', 'tnl15', '150', '1'],
             ['67108880', 'tnl16', '150', '1'], ['67108881', 'tnl17', '150', '1'],
             ['67108882', 'tnl18', '150', '1'], ['67108883', 'tnl19', '150', '1'],
             ['67108884', 'tnl20', '150', '1'], ['67108885', 'tnl21', '150', '1'],
             ['67108886', 'tnl22', '150', '1'], ['67108887', 'tnl23', '150', '1'],
             ['67108888', 'tnl24', '150', '1'], ['67108889', 'tnl25', '150', '1'],
             ['67108890', 'tnl26', '150', '1'], ['67108891', 'tnl27', '150', '1'],
             ['67108892', 'tnl28', '150', '1'], ['67108893', 'tnl29', '150', '1'],
             ['67108894', 'tnl30', '150', '1'], ['67108895', 'tnl31', '150', '1'],
             ['67108896', 'tnl32', '150', '1'], ['67108897', 'tnl33', '150', '1'],
             ['67108898', 'tnl34', '150', '1'], ['67108899', 'tnl35', '150', '1'],
             ['67108900', 'tnl36', '150', '1'], ['67108901', 'tnl37', '150', '1'],
             ['67108902', 'tnl38', '150', '1'], ['67108903', 'tnl39', '150', '1'],
             ['67108904', 'tnl40', '150', '1'], ['67108905', 'tnl41', '150', '1'],
             ['67108906', 'tnl42', '150', '1'], ['67108907', 'tnl43', '150', '1'],
             ['67108908', 'tnl44', '150', '1'], ['67108909', 'tnl45', '150', '1'],
             ['67108910', 'tnl46', '150', '1'], ['67108911', 'tnl47', '150', '1'],
             ['67108912', 'tnl48', '150', '1'], ['67108913', 'tnl49', '150', '1'],
             ['67108914', 'tnl50', '150', '1'], ['67108915', 'tnl51', '150', '1'],
             ['67108916', 'tnl52', '150', '1'], ['67108917', 'tnl53', '150', '1'],
             ['67108918', 'tnl54', '150', '1'], ['67108919', 'tnl55', '150', '1'],
             ['67108920', 'tnl56', '150', '1'], ['67108921', 'tnl57', '150', '1'],
             ['67108922', 'tnl58', '150', '1'], ['67108923', 'tnl59', '150', '1'],
             ['67108924', 'tnl60', '150', '1'], ['67108925', 'tnl61', '150', '1'],
             ['67108926', 'tnl62', '150', '1'], ['67108927', 'tnl63', '150', '1'],
             ['67108928', 'tnl64', '150', '1'], ['67108929', 'tnl65', '150', '1'],
             ['67108930', 'tnl66', '150', '1'], ['67108931', 'tnl67', '150', '1'],
             ['67108932', 'tnl68', '150', '1'], ['67108933', 'tnl69', '150', '1'],
             ['67108934', 'tnl70', '150', '1'], ['67108935', 'tnl71', '150', '1'],
             ['67108936', 'tnl72', '150', '1'], ['67108937', 'tnl73', '150', '1'],
             ['67108938', 'tnl74', '150', '1'], ['67108939', 'tnl75', '150', '1'],
             ['83886081', 'LAG1', '202', '1'], ['83886083', 'LAG3', '202', '1'],
             ['83886085', 'LAG5', '202', '2']],
            [['      N/A    ', '-001.6045 dBm: Normal', '-002.2504 dBm: Normal', '1409'],
             ['31.4882 C: Normal', '-001.4508 dBm: Normal', '-036.9897 dBm: Low-Alarm', '1410'],
             ['31.4531 C: Normal', '-001.4194 dBm: Normal', '-033.9794 dBm: Low-Alarm', '1411'],
             [
                 '29.5703 C: Normal', '-031.5490 dBm: Low-Alarm', '-036.9897 dBm: Low-Alarm',
                 '1412'
             ],
             [
                 '28.7187 C: Normal', '-033.0102 dBm: Low-Alarm', '-214748.3647 dBm: Low-Alarm',
                 '1413'
             ],
             [
                 '31.5898 C: Normal', '-214748.3647 dBm: Low-Alarm',
                 '-214748.3647 dBm: Low-Alarm', '1414'
             ],
             [
                 '27.6054 C: Normal', '-214748.3647 dBm: Low-Alarm',
                 '-214748.3647 dBm: Low-Alarm', '1415'
             ],
             [
                 '28.6132 C: Normal', '-214748.3647 dBm: Low-Alarm',
                 '-214748.3647 dBm: Low-Alarm', '1416'
             ],
             [
                 '31.5078 C: Normal', '-214748.3647 dBm: Low-Alarm', '-019.2081 dBm: Low-Alarm',
                 '1473'
             ],
             [
                 '28.5000 C: Normal', '-029.5860 dBm: Low-Alarm', '-214748.3647 dBm: Low-Alarm',
                 '1474'
             ],
             [
                 '28.9414 C: Normal', '-032.2184 dBm: Low-Alarm', '-214748.3647 dBm: Low-Alarm',
                 '1475'
             ],
             [
                 '30.2695 C: Normal', '-029.2081 dBm: Low-Alarm', '-214748.3647 dBm: Low-Alarm',
                 '1476'
             ],
             [
                 '29.5664 C: Normal', '-214748.3647 dBm: Low-Alarm',
                 '-214748.3647 dBm: Low-Alarm', '1477'
             ],
             [
                 '33.2578 C: Normal', '-031.5490 dBm: Low-Alarm', '-214748.3647 dBm: Low-Alarm',
                 '1478'
             ],
             [
                 '28.3906 C: Normal', '-214748.3647 dBm: Low-Alarm',
                 '-214748.3647 dBm: Low-Alarm', '1479'
             ],
             [
                 '30.1679 C: Normal', '-035.2287 dBm: Low-Alarm', '-214748.3647 dBm: Low-Alarm',
                 '1480'
             ],
             [
                 '30.7304 C: Normal', '-214748.3647 dBm: Low-Alarm', '-040.0000 dBm: Low-Alarm',
                 '1793'
             ],
             [
                 '29.0546 C: Normal', '-214748.3647 dBm: Low-Alarm',
                 '-214748.3647 dBm: Low-Alarm', '1794'
             ],
             [
                 '33.4609 C: Normal', '-214748.3647 dBm: Low-Alarm', '-040.0000 dBm: Low-Alarm',
                 '1795'
             ],
             [
                 '31.5429 C: Normal', '-214748.3647 dBm: Low-Alarm',
                 '-214748.3647 dBm: Low-Alarm', '1796'
             ],
             ['31.7695 C: Normal', '001.4924 dBm: Normal', '-004.6711 dBm: High-Alarm', '1857'],
             ['34.8203 C: Normal', '001.7943 dBm: Normal', '-005.2841 dBm: High-Warn', '1858'],
             ['34.1445 C: Normal', '001.7117 dBm: Normal', '-004.4117 dBm: High-Warn', '1859'],
             ['33.2734 C: Normal', '001.9810 dBm: Normal', '-003.8048 dBm: High-Alarm', '1860'],
             ['28.9570 C: Normal', '002.0002 dBm: Normal', '-015.6224 dBm: Normal', '1921'],
             ['30.7734 C: Normal', '000.9642 dBm: Normal', '-015.2143 dBm: Normal', '1922'],
             ['32.6914 C: Normal', '001.7545 dBm: Normal', '-014.8811 dBm: Normal', '1923'],
             ['32.5000 C: Normal', '001.3653 dBm: Normal', '-015.4515 dBm: Normal', '1924'],
             [
                 '27.4179 C: Normal', '-214748.3647 dBm: Low-Alarm',
                 '-214748.3647 dBm: Low-Alarm', '1985'
             ],
             [
                 '29.5898 C: Normal', '-214748.3647 dBm: Low-Alarm',
                 '-214748.3647 dBm: Low-Alarm', '1986'
             ],
             [
                 '32.8593 C: Normal', '-214748.3647 dBm: Low-Alarm', '-035.2287 dBm: Low-Alarm',
                 '1987'
             ],
             [
                 '29.7226 C: Normal', '-214748.3647 dBm: Low-Alarm',
                 '-214748.3647 dBm: Low-Alarm', '1988'
             ]],
            [['10GE LR 10km SFP+', '57-0000076-01', 'ADF2094300014TL', '1409'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF2094300014UN', '1410'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF2094300014UL', '1411'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF2094300014UP', '1412'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF2094600003A9', '1413'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF2094400005FT', '1414'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF2094600003AF', '1415'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF209450000MT2', '1416'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADA111253005111', '1473'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF2094500003VL', '1474'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF2094500003UJ', '1475'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF20945000041J', '1476'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF2094400005FS', '1477'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF2094500003VD', '1478'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF2094500003VH', '1479'],
             ['10GE LR 10km SFP+', '57-0000076-01', 'ADF2094400012DM', '1480'],
             ['10GBASE-ZRD 1538.20nm (XFP)', 'FTRX-3811-349-F1', 'AG601D6', '1793'],
             ['10GBASE-ZRD 1537.40nm (XFP)', 'FIM31060/210W50', 'SNG031', '1794'],
             ['10GBASE-ZRD 1536.60nm (XFP)', 'FTRX-3811-351-F1', 'AG601Y8', '1795'],
             ['10GBASE-ZRD 1535.80nm (XFP)', 'XFP-DWLR08-52', 'UL30HQ4', '1796'],
             ['10GBASE-ZRD 1535.05nm (XFP)', 'FTRX-3811-353-F1', 'AGA07AJ', '1857'],
             ['10GBASE-ZRD 1534.25nm (XFP)', 'FTRX-3811-354-F1', 'AG800UB', '1858'],
             ['10GBASE-ZRD 1533.45nm (XFP)', 'FIM31060/210W55', 'PRG041', '1859'],
             ['10GBASE-ZRD 1532.70nm (XFP)', 'FIM31060/210W56', 'SPG153', '1860'],
             ['10GBASE-ZRD 1538.20nm (XFP)', 'FIM31060/210W49', 'PHG011', '1921'],
             ['10GBASE-ZRD 1537.40nm (XFP)', 'FIM31060/210W50', 'PHG020', '1922'],
             ['10GBASE-ZRD 1536.60nm (XFP)', 'FIM31060/210W51', 'PRG015', '1923'],
             ['10GBASE-ZRD 1535.80nm (XFP)', 'XFP-DWLR08-52', 'UL30HQ5', '1924'],
             ['10GBASE-ZRD 1535.05nm (XFP)', 'FTRX-3811-353-F1', 'AFS0064', '1985'],
             ['10GBASE-ZRD 1534.25nm (XFP)', 'XFP-DWLR08-54', 'UKR0NE8', '1986'],
             ['10GBASE-ZRD 1533.45nm (XFP)', 'FTRX-3811-355-F1', 'AG705BX', '1987'],
             ['10GBASE-ZRD 1532.70nm (XFP)', 'FIM31060/210W56', 'SPG084', '1988']],
            [],
        ],
        [
            Service(item='1409', parameters={}, labels=[]),
            Service(item='1857', parameters={}, labels=[]),
            Service(item='1858', parameters={}, labels=[]),
            Service(item='1859', parameters={}, labels=[]),
            Service(item='1860', parameters={}, labels=[]),
            Service(item='1921', parameters={}, labels=[]),
            Service(item='1922', parameters={}, labels=[]),
            Service(item='1923', parameters={}, labels=[]),
            Service(item='1924', parameters={}, labels=[]),
        ],
        [
            (
                '1409',
                {},
                [
                    Result(state=State.OK,
                           summary='[S/N ADF2094300014TL, P/N 57-0000076-01] Operational up',
                           details='[S/N ADF2094300014TL, P/N 57-0000076-01] Operational up'),
                    Result(state=State.OK,
                           summary='TX Light -1.6 dBm (Normal)',
                           details='TX Light -1.6 dBm (Normal)'),
                    Metric('tx_light', -1.6045),
                    Result(state=State.OK,
                           summary='RX Light -2.3 dBm (Normal)',
                           details='RX Light -2.3 dBm (Normal)'),
                    Metric('rx_light', -2.2504),
                ],
            ),
            (
                '1857',
                {},
                [
                    Result(state=State.OK,
                           summary='[S/N AGA07AJ, P/N FTRX-3811-353-F1] Operational up',
                           details='[S/N AGA07AJ, P/N FTRX-3811-353-F1] Operational up'),
                    Metric('temp', 31.7695),
                    Result(state=State.OK,
                           summary='Temperature: 31.8°C',
                           details='Temperature: 31.8°C'),
                    Result(
                        state=State.OK,
                        notice=
                        'Configuration: prefer user levels over device levels (no levels found)'),
                    Result(state=State.OK,
                           summary='TX Light 1.5 dBm (Normal)',
                           details='TX Light 1.5 dBm (Normal)'),
                    Metric('tx_light', 1.4924),
                    Result(state=State.OK,
                           summary='RX Light -4.7 dBm (High-Alarm)',
                           details='RX Light -4.7 dBm (High-Alarm)'),
                    Metric('rx_light', -4.6711),
                ],
            ),
            (
                '1858',
                {},
                [
                    Result(state=State.OK,
                           summary='[S/N AG800UB, P/N FTRX-3811-354-F1] Operational up',
                           details='[S/N AG800UB, P/N FTRX-3811-354-F1] Operational up'),
                    Metric('temp', 34.8203),
                    Result(state=State.OK,
                           summary='Temperature: 34.8°C',
                           details='Temperature: 34.8°C'),
                    Result(
                        state=State.OK,
                        notice=
                        'Configuration: prefer user levels over device levels (no levels found)'),
                    Result(state=State.OK,
                           summary='TX Light 1.8 dBm (Normal)',
                           details='TX Light 1.8 dBm (Normal)'),
                    Metric('tx_light', 1.7943),
                    Result(state=State.OK,
                           summary='RX Light -5.3 dBm (High-Warn)',
                           details='RX Light -5.3 dBm (High-Warn)'),
                    Metric('rx_light', -5.2841),
                ],
            ),
            (
                '1859',
                {},
                [
                    Result(state=State.OK,
                           summary='[S/N PRG041, P/N FIM31060/210W55] Operational up',
                           details='[S/N PRG041, P/N FIM31060/210W55] Operational up'),
                    Metric('temp', 34.1445),
                    Result(state=State.OK,
                           summary='Temperature: 34.1°C',
                           details='Temperature: 34.1°C'),
                    Result(
                        state=State.OK,
                        notice=
                        'Configuration: prefer user levels over device levels (no levels found)'),
                    Result(state=State.OK,
                           summary='TX Light 1.7 dBm (Normal)',
                           details='TX Light 1.7 dBm (Normal)'),
                    Metric('tx_light', 1.7117),
                    Result(state=State.OK,
                           summary='RX Light -4.4 dBm (High-Warn)',
                           details='RX Light -4.4 dBm (High-Warn)'),
                    Metric('rx_light', -4.4117),
                ],
            ),
            (
                '1860',
                {},
                [
                    Result(state=State.OK,
                           summary='[S/N SPG153, P/N FIM31060/210W56] Operational up',
                           details='[S/N SPG153, P/N FIM31060/210W56] Operational up'),
                    Metric('temp', 33.2734),
                    Result(state=State.OK,
                           summary='Temperature: 33.3°C',
                           details='Temperature: 33.3°C'),
                    Result(
                        state=State.OK,
                        notice=
                        'Configuration: prefer user levels over device levels (no levels found)'),
                    Result(state=State.OK,
                           summary='TX Light 2.0 dBm (Normal)',
                           details='TX Light 2.0 dBm (Normal)'),
                    Metric('tx_light', 1.981),
                    Result(state=State.OK,
                           summary='RX Light -3.8 dBm (High-Alarm)',
                           details='RX Light -3.8 dBm (High-Alarm)'),
                    Metric('rx_light', -3.8048),
                ],
            ),
            (
                '1922',
                {},
                [
                    Result(state=State.OK,
                           summary='[S/N PHG020, P/N FIM31060/210W50] Operational up',
                           details='[S/N PHG020, P/N FIM31060/210W50] Operational up'),
                    Metric('temp', 30.7734),
                    Result(state=State.OK,
                           summary='Temperature: 30.8°C',
                           details='Temperature: 30.8°C'),
                    Result(
                        state=State.OK,
                        notice=
                        'Configuration: prefer user levels over device levels (no levels found)'),
                    Result(state=State.OK,
                           summary='TX Light 1.0 dBm (Normal)',
                           details='TX Light 1.0 dBm (Normal)'),
                    Metric('tx_light', 0.9642),
                    Result(state=State.OK,
                           summary='RX Light -15.2 dBm (Normal)',
                           details='RX Light -15.2 dBm (Normal)'),
                    Metric('rx_light', -15.2143),
                ],
            ),
            (
                '1923',
                {},
                [
                    Result(state=State.OK,
                           summary='[S/N PRG015, P/N FIM31060/210W51] Operational up',
                           details='[S/N PRG015, P/N FIM31060/210W51] Operational up'),
                    Metric('temp', 32.6914),
                    Result(state=State.OK,
                           summary='Temperature: 32.7°C',
                           details='Temperature: 32.7°C'),
                    Result(
                        state=State.OK,
                        notice=
                        'Configuration: prefer user levels over device levels (no levels found)'),
                    Result(state=State.OK,
                           summary='TX Light 1.8 dBm (Normal)',
                           details='TX Light 1.8 dBm (Normal)'),
                    Metric('tx_light', 1.7545),
                    Result(state=State.OK,
                           summary='RX Light -14.9 dBm (Normal)',
                           details='RX Light -14.9 dBm (Normal)'),
                    Metric('rx_light', -14.8811),
                ],
            ),
            (
                '1924',
                {},
                [
                    Result(state=State.OK,
                           summary='[S/N UL30HQ5, P/N XFP-DWLR08-52] Operational up',
                           details='[S/N UL30HQ5, P/N XFP-DWLR08-52] Operational up'),
                    Metric('temp', 32.5),
                    Result(state=State.OK,
                           summary='Temperature: 32.5°C',
                           details='Temperature: 32.5°C'),
                    Result(
                        state=State.OK,
                        notice=
                        'Configuration: prefer user levels over device levels (no levels found)'),
                    Result(state=State.OK,
                           summary='TX Light 1.4 dBm (Normal)',
                           details='TX Light 1.4 dBm (Normal)'),
                    Metric('tx_light', 1.3653),
                    Result(state=State.OK,
                           summary='RX Light -15.5 dBm (Normal)',
                           details='RX Light -15.5 dBm (Normal)'),
                    Metric('rx_light', -15.4515),
                ],
            ),
        ],
    )
])
# fmt: on
def test_regression(
    string_table,
    discovery_results,
    items_params_results,
):
    section = brocade_optical.parse_brocade_optical(string_table)

    assert (
        list(
            brocade_optical.discover_brocade_optical(
                [(interfaces.DISCOVERY_DEFAULT_PARAMETERS)],
                section,
            )
        )
        == discovery_results
    )

    for item, par, res in items_params_results:
        assert (
            list(
                brocade_optical.check_brocade_optical(
                    item,
                    (par),
                    section,
                )
            )
            == res
        )
