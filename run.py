import configparser
import os

from bs4 import BeautifulSoup
import pandas as pd
from dateutil.parser import parse


def get_data(file_to_open=None):
    if file_to_open is None:
        file_to_open = input_filename

    with open(file_to_open, encoding="utf8") as fp:
        soup = BeautifulSoup(fp, 'lxml')

    return soup


def get_features_data(soup):
    features = soup.find_all(
        'li',
        class_='has-leaf'
    )

    for feature in features:
        feature_description = feature.find('div', class_='test-heading')
        feature_tests = feature.find('div', class_='test-content')
        feature_test_items = feature_tests.find_all('div', {'class': 'scenario'})
        get_test_case_data(
            feature_description.find('span', class_='test-name').text,
            feature_test_items)
        item = {
            'title': feature_description.find('span', class_='test-name').text,
            'status': feature_description.find('span', class_='test-status').text,
            'total_count': str(get_total_scenarios_count_for_feature(feature_test_items)),
            'pass_count': str(get_passed_scenarios_count_for_feature(feature_test_items)),
            'failed_count': str(get_failed_scenarios_count_for_feature(feature_test_items)),
        }
        features_data.append(item)


def get_total_scenarios_count_for_feature(feature_scenarios):
    total_count = 0
    for scenario in feature_scenarios:
        if 'outline' in scenario['class']:
            total_count = total_count + len(scenario.find_all('li', {'class': 'scenario'}))
        else:
            total_count = total_count + 1
    return total_count


def get_failed_scenarios_count_for_feature(feature_scenarios):
    failed_count = 0
    for scenario in feature_scenarios:
        if 'outline' in scenario['class']:
            failed_count = failed_count + len(scenario.find_all(
                'li',
                {'class': 'scenario', 'status': 'Fail'}
            ))
        else:
            if 'fail' in scenario['status']:
                failed_count = failed_count + 1
    return failed_count


def get_passed_scenarios_count_for_feature(feature_scenarios):
    passed_count = 0
    for scenario in feature_scenarios:
        if 'outline' in scenario['class']:
            passed_count = passed_count + len(scenario.find_all(
                'li',
                {'class': 'scenario', 'status': 'Pass'}
            ))
        else:
            if 'pass' in scenario['status']:
                passed_count = passed_count + 1
    return passed_count


def get_test_case_data(feature_name, feature_scenarios):
    priority_values = ['@P1', '@P2', '@P3', '@P4', '@p1', '@p2', '@p3', '@p4']
    for scenario in feature_scenarios:
        if 'outline' in scenario['class']:
            scenario_outlines = scenario.find_all('li', {'class': 'scenario'})

            for scenario_outlines_count, scenario_outline in enumerate(scenario_outlines):
                priority = ""
                tags = ""
                found_priorities = scenario_outline.find('span', class_='category label',
                                                         text=lambda t: t in priority_values)
                if found_priorities:
                    priority = found_priorities.text.replace("@", "")
                found_tags = scenario_outline.find_all(
                    'span',
                    class_='category label',
                    text=lambda t: jira_project_key_prefix_for_tags in t
                )
                if found_tags:
                    tags = ", ".join([element.text.replace("@", "") for element in found_tags])
                item = {
                    "feature_name": feature_name,
                    "scenario_name": scenario_outline.find(
                        'div',
                        {'class': 'step-name'}
                    ).find(
                        text=True, recursive=False
                    ).strip(),
                    "scenario_status": scenario_outline.find(
                        'div',
                        {'class': 'step-name'}
                    ).find('span')["title"],
                    "Priority": priority,
                    "Tags": tags
                }
                scenario_data.append(item)
                if scenario_outlines_count == 0:
                    first_scenario_only_data.append(item)
        else:
            priority = ""
            tags = ""
            found_priorities = scenario.find(
                'span',
                class_='category label',
                text=lambda t: t in priority_values
            )
            if found_priorities:
                priority = found_priorities.text.replace("@", "")
            found_tags = scenario.find_all(
                'span',
                class_='category label',
                text=lambda t: jira_project_key_prefix_for_tags in t
            )
            if found_tags:
                tags = ", ".join([element.text.replace("@", "") for element in found_tags])
            item = {
                "feature_name": feature_name,
                "scenario_name": scenario.find(
                    'div',
                    {'class': 'scenario-name'}
                ).find(
                    text=True,
                    recursive=False
                ).strip(),
                "scenario_status": scenario.find(
                    'div',
                    {'class': 'scenario-name'}
                ).find('span')["title"],
                "Priority": priority,
                "Tags": tags
            }
            scenario_data.append(item)
            first_scenario_only_data.append(item)
    return


def export_data(report_time_stamp, path_to_save=''):
    workbook_name = os.path.join('exported_data', path_to_save,
                                 f"Report - {report_time_stamp.strftime('%d_%m_%Y_%H_%M_%S')}.xlsx")
    json_name = os.path.join('exported_data', path_to_save,
                             f"data_{report_time_stamp.strftime('%d_%m_%Y_%H_%M_%S')}.json")
    df1 = pd.DataFrame(features_data)
    df2 = pd.DataFrame(scenario_data)
    df3 = pd.DataFrame(first_scenario_only_data)
    writer = pd.ExcelWriter(workbook_name, engine='xlsxwriter')
    df1.to_excel(writer, sheet_name='Feature Details')
    df2.to_excel(writer, sheet_name='Scenario Details')
    df3.to_excel(writer, sheet_name='First Scenario Details')
    writer.close()

    df2.to_json(json_name, orient='records')


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("./config/report_config.ini")
    input_filename = config["REPORT"]['filename']
    input_directory_to_search = config["REPORT"]['directory_to_search']
    jira_project_key_prefix_for_tags = config["REPORT"]['jira_project_key_prefix_for_tags']

    features_data = []
    scenario_data = []
    first_scenario_only_data = []
    REPORT_TIME_STAMP = ''

    for root, dirs, files in os.walk(input_directory_to_search):
        for file in files:
            if file == input_filename:
                data_from_html_file = get_data(os.path.join(root, file))
                REPORT_TIME_STAMP = parse(data_from_html_file.find(
                    'span', {'class': 'suite-start-time'}
                ).text.strip())
                get_features_data(data_from_html_file)
    export_data(REPORT_TIME_STAMP)
