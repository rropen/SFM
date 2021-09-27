import pytest
from time import mktime
from sfm.routes.metrics import routes
from sqlmodel import Session, select
from sfm.models import Project, WorkItem
from tests.conftest import hashed_token1
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# Test calc_frequency function
def test_calc_frequency(db: Session):

    day_proj = Project(
        **{
            "name": "Test Project for Daily Deploys",
            "lead_name": "Deploy Deployer",
            "lead_email": "commit-deploy@dora.com",
            "description": "A test project for testing",
            "location": "githubville",
            "repo_url": "github.com/DoraEnterprises",
            "on_prem": False,
            "project_auth_token_hashed": hashed_token1,
        }
    )
    week_proj = Project(
        **{
            "name": "Test Project for Weekly Deploys",
            "lead_name": "Deploy Deployer",
            "lead_email": "commit-deploy@dora.com",
            "description": "A test project for testing",
            "location": "githubville",
            "repo_url": "github.com/DoraEnterprises",
            "on_prem": False,
            "project_auth_token_hashed": hashed_token1,
        }
    )
    month_proj = Project(
        **{
            "name": "Test Project for Montly Deploys",
            "lead_name": "Deploy Deployer",
            "lead_email": "commit-deploy@dora.com",
            "description": "A test project for testing",
            "location": "githubville",
            "repo_url": "github.com/DoraEnterprises",
            "on_prem": False,
            "project_auth_token_hashed": hashed_token1,
        }
    )
    year_proj = Project(
        **{
            "name": "Test Project for Yearly Deploys",
            "lead_name": "Deploy Deployer",
            "lead_email": "commit-deploy@dora.com",
            "description": "A test project for testing",
            "location": "githubville",
            "repo_url": "github.com/DoraEnterprises",
            "on_prem": False,
            "project_auth_token_hashed": hashed_token1,
        }
    )
    db.add_all([day_proj, week_proj, month_proj, year_proj])
    db.commit()
    db.refresh(day_proj)
    db.refresh(week_proj)
    db.refresh(month_proj)
    db.refresh(year_proj)

    daily_deploys = []
    weekly_deploys = []
    monthly_deploys = []
    yearly_deploys = []
    start_date = datetime.now() - timedelta(days=84)
    for day in range(0, 84):
        daily_deploys.append(
            WorkItem(
                **{
                    "category": "Deployment",
                    "start_time": None,
                    "end_time": start_date + timedelta(days=day),
                    "duration_open": None,
                    "comments": "Test description for test work item in the database",
                    "project_id": day_proj.id,
                }
            )
        )
        if (day % 3) == 0:
            weekly_deploys.append(
                WorkItem(
                    **{
                        "category": "Deployment",
                        "start_time": None,
                        "end_time": start_date + timedelta(days=day),
                        "duration_open": None,
                        "comments": "Test description for test work item in the database",
                        "project_id": week_proj.id,
                    }
                )
            )
        elif (day % 20) == 0:
            monthly_deploys.append(
                WorkItem(
                    **{
                        "category": "Deployment",
                        "start_time": None,
                        "end_time": start_date + timedelta(days=day),
                        "duration_open": None,
                        "comments": "Test description for test work item in the database",
                        "project_id": month_proj.id,
                    }
                )
            )

    yearly_deploys.append(
        WorkItem(
            **{
                "category": "Deployment",
                "start_time": None,
                "end_time": start_date,
                "duration_open": None,
                "comments": "Test description for test work item in the database",
                "project_id": year_proj.id,
            }
        )
    )

    db.add_all(daily_deploys)
    db.add_all(weekly_deploys)
    db.add_all(monthly_deploys)
    db.add_all(yearly_deploys)
    db.commit()

    assert routes.calc_frequency(day_proj.work_items) == "Daily"
    assert routes.calc_frequency(week_proj.work_items) == "Weekly"
    assert routes.calc_frequency(month_proj.work_items) == "Monthly"
    assert routes.calc_frequency(year_proj.work_items) == "Yearly"


# Test combine_deploys function
def test_combine_deploys():
    deployment_list = [
        datetime(2021, 5, 31).date(),
        datetime(2021, 5, 31).date(),
        datetime(2021, 5, 31).date(),
        datetime(2021, 6, 1).date(),
        datetime(2021, 6, 3).date(),
    ]

    result = routes.combine_deploys(deployment_list)[:4]
    print(result)
    expected_result = [
        [mktime(datetime(2021, 5, 31).date().timetuple()), 3],
        [mktime(datetime(2021, 6, 1).date().timetuple()), 1],
        [mktime(datetime(2021, 6, 2).date().timetuple()), 0],
        [mktime(datetime(2021, 6, 3).date().timetuple()), 1],
    ]
    print(expected_result)
    assert result == expected_result


# Test lead_times_per_day function
def test_lead_time_per_day():
    commit_list = [
        datetime(2021, 5, 31).date(),
        datetime(2021, 5, 31).date(),
        datetime(2021, 5, 31).date(),
        datetime(2021, 6, 1).date(),
        datetime(2021, 6, 3).date(),
    ]
    lead_time = [60, 120, 180, 240, 300]

    result = routes.lead_times_per_day(commit_list, lead_time)
    result[0] = result[0][:4]
    result[1] = result[1][:4]
    print(result)

    expected_result = [
        [
            [mktime(datetime(2021, 5, 31).date().timetuple()), 3],
            [mktime(datetime(2021, 6, 1).date().timetuple()), 1],
            [mktime(datetime(2021, 6, 2).date().timetuple()), 0],
            [mktime(datetime(2021, 6, 3).date().timetuple()), 1],
        ],
        [
            [mktime(datetime(2021, 5, 31).date().timetuple()), 2.0],
            [mktime(datetime(2021, 6, 1).date().timetuple()), 4.0],
            [mktime(datetime(2021, 6, 2).date().timetuple()), 0.0],
            [mktime(datetime(2021, 6, 3).date().timetuple()), 5.0],
        ],
    ]
    print(expected_result)
    assert result == expected_result


# Test get "/deployments" endpoint
def test_get_deployments(client: TestClient, db: Session):
    """Testing that the endpoint works as expected"""
    response = client.get("/metrics/deployments", params={"project_id": "2"})
    assert response is not None
    assert response.status_code == 200

    result = response.json()
    result[0]["deployment_dates"] = result[0]["deployment_dates"][:6]

    deploy_dates = [
        datetime(2021, 5, 31),  # Week 1
        datetime(2021, 6, 1),  # Week 2
        datetime(2021, 6, 2),  # Week 10
        datetime(2021, 6, 3),  # Week 11
        datetime(2021, 6, 4),
        datetime(2021, 6, 5),  # Week 12
    ]
    time_shift = timedelta(days=32)
    deploy_dates = [deploy + time_shift for deploy in deploy_dates]
    deployment_dates = [
        [mktime(deploy_dates[0].date().timetuple()), 1],  # Week 1
        [mktime(deploy_dates[1].date().timetuple()), 0],  # Week 2
        [mktime(deploy_dates[2].date().timetuple()), 0],  # Week 10
        [mktime(deploy_dates[3].date().timetuple()), 0],  # Week 11
        [mktime(deploy_dates[4].date().timetuple()), 0],
        [mktime(deploy_dates[5].date().timetuple()), 0],  # Week 12
    ]

    expected_result = [
        {
            "project_name": "Test Project 2",
            "deployment_dates": deployment_dates,
            "performance": "Monthly",
            "deployment_dates_description": "",
            "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
        }
    ]

    assert result == expected_result

    """Test if given project name"""
    response2 = client.get(
        "/metrics/deployments", params={"project_name": "Test Project 2"}
    )
    assert response2 is not None
    assert response2.status_code == 200

    result2 = response2.json()
    result2[0]["deployment_dates"] = result2[0]["deployment_dates"][:6]

    assert result2 == expected_result

    """Test if given project_id AND project_name"""
    response3 = client.get(
        "/metrics/deployments",
        params={"project_id": "2", "project_name": "Test Project 2"},
    )
    assert response3 is not None
    assert response3.status_code == 200

    result3 = response3.json()
    result3[0]["deployment_dates"] = result3[0]["deployment_dates"][:6]

    assert result3 == expected_result

    response4 = client.get("/metrics/deployments")
    assert response4 is not None
    assert response4.status_code == 200

    result4 = response4.json()

    expected_result4 = [
        {
            "project_name": "org",
            "deployment_dates": [
                [1625198400.0, 2],
                [1625284800.0, 0],
                [1625371200.0, 0],
                [1625457600.0, 0],
                [1625544000.0, 0],
                [1625630400.0, 0],
                [1625716800.0, 0],
                [1625803200.0, 2],
                [1625889600.0, 0],
                [1625976000.0, 0],
                [1626062400.0, 0],
                [1626148800.0, 0],
                [1626235200.0, 1],
                [1626321600.0, 0],
                [1626408000.0, 1],
                [1626494400.0, 0],
                [1626580800.0, 1],
                [1626667200.0, 0],
                [1626753600.0, 1],
                [1626840000.0, 0],
                [1626926400.0, 0],
                [1627012800.0, 1],
                [1627099200.0, 1],
                [1627185600.0, 0],
                [1627272000.0, 0],
                [1627358400.0, 1],
                [1627444800.0, 1],
                [1627531200.0, 0],
                [1627617600.0, 1],
                [1627704000.0, 1],
                [1627790400.0, 1],
                [1627876800.0, 0],
                [1627963200.0, 0],
                [1628049600.0, 0],
                [1628136000.0, 0],
                [1628222400.0, 1],
                [1628308800.0, 0],
                [1628395200.0, 0],
                [1628481600.0, 1],
                [1628568000.0, 0],
                [1628654400.0, 0],
                [1628740800.0, 0],
                [1628827200.0, 1],
                [1628913600.0, 0],
                [1629000000.0, 1],
                [1629086400.0, 0],
                [1629172800.0, 1],
                [1629259200.0, 0],
                [1629345600.0, 0],
                [1629432000.0, 1],
                [1629518400.0, 0],
                [1629604800.0, 1],
                [1629691200.0, 0],
                [1629777600.0, 0],
                [1629864000.0, 0],
                [1629950400.0, 0],
                [1630036800.0, 1],
                [1630123200.0, 1],
                [1630209600.0, 0],
                [1630296000.0, 1],
                [1630382400.0, 1],
                [1630468800.0, 0],
                [1630555200.0, 0],
                [1630641600.0, 1],
                [1630728000.0, 0],
                [1630814400.0, 1],
                [1630900800.0, 0],
                [1630987200.0, 0],
                [1631073600.0, 0],
                [1631160000.0, 0],
                [1631246400.0, 1],
                [1631332800.0, 1],
                [1631419200.0, 3],
                [1631505600.0, 1],
                [1631592000.0, 1],
                [1631678400.0, 0],
                [1631764800.0, 0],
                [1631851200.0, 2],
                [1631937600.0, 0],
                [1632024000.0, 1],
                [1632110400.0, 1],
                [1632196800.0, 0],
                [1632283200.0, 0],
                [1632369600.0, 1],
                [1632456000.0, 0],
                [1632542400.0, 0],
                [1632628800.0, 0],
            ],
            "performance": "Daily",
            "deployment_dates_description": "",
            "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
        }
    ]
    assert result4 == expected_result4

    """Testing if you set all_deployments to false"""
    response5 = client.get("/metrics/deployments", params={"all_deployments": "false"})
    assert response5 is not None
    assert response5.status_code == 200

    result5 = response5.json()

    expected_result5 = [
        {
            "project_name": "Test Project 1",
            "deployment_dates": [
                [1625198400.0, 1],
                [1625284800.0, 0],
                [1625371200.0, 0],
                [1625457600.0, 0],
                [1625544000.0, 0],
                [1625630400.0, 0],
                [1625716800.0, 0],
                [1625803200.0, 1],
                [1625889600.0, 0],
                [1625976000.0, 0],
                [1626062400.0, 0],
                [1626148800.0, 0],
                [1626235200.0, 1],
                [1626321600.0, 0],
                [1626408000.0, 1],
                [1626494400.0, 0],
                [1626580800.0, 1],
                [1626667200.0, 0],
                [1626753600.0, 1],
                [1626840000.0, 0],
                [1626926400.0, 0],
                [1627012800.0, 1],
                [1627099200.0, 1],
                [1627185600.0, 0],
                [1627272000.0, 0],
                [1627358400.0, 1],
                [1627444800.0, 1],
                [1627531200.0, 0],
                [1627617600.0, 1],
                [1627704000.0, 1],
                [1627790400.0, 1],
                [1627876800.0, 0],
                [1627963200.0, 0],
                [1628049600.0, 0],
                [1628136000.0, 0],
                [1628222400.0, 1],
                [1628308800.0, 0],
                [1628395200.0, 0],
                [1628481600.0, 1],
                [1628568000.0, 0],
                [1628654400.0, 0],
                [1628740800.0, 0],
                [1628827200.0, 1],
                [1628913600.0, 0],
                [1629000000.0, 1],
                [1629086400.0, 0],
                [1629172800.0, 1],
                [1629259200.0, 0],
                [1629345600.0, 0],
                [1629432000.0, 1],
                [1629518400.0, 0],
                [1629604800.0, 1],
                [1629691200.0, 0],
                [1629777600.0, 0],
                [1629864000.0, 0],
                [1629950400.0, 0],
                [1630036800.0, 1],
                [1630123200.0, 1],
                [1630209600.0, 0],
                [1630296000.0, 1],
                [1630382400.0, 1],
                [1630468800.0, 0],
                [1630555200.0, 0],
                [1630641600.0, 1],
                [1630728000.0, 0],
                [1630814400.0, 0],
                [1630900800.0, 0],
                [1630987200.0, 0],
                [1631073600.0, 0],
                [1631160000.0, 0],
                [1631246400.0, 1],
                [1631332800.0, 0],
                [1631419200.0, 2],
                [1631505600.0, 1],
                [1631592000.0, 1],
                [1631678400.0, 0],
                [1631764800.0, 0],
                [1631851200.0, 1],
                [1631937600.0, 0],
                [1632024000.0, 1],
                [1632110400.0, 1],
                [1632196800.0, 0],
                [1632283200.0, 0],
                [1632369600.0, 1],
                [1632456000.0, 0],
                [1632542400.0, 0],
                [1632628800.0, 0],
            ],
            "performance": "Daily",
            "deployment_dates_description": "",
            "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
        },
        {
            "project_name": "Test Project 2",
            "deployment_dates": [
                [1625198400.0, 1],
                [1625284800.0, 0],
                [1625371200.0, 0],
                [1625457600.0, 0],
                [1625544000.0, 0],
                [1625630400.0, 0],
                [1625716800.0, 0],
                [1625803200.0, 1],
                [1625889600.0, 0],
                [1625976000.0, 0],
                [1626062400.0, 0],
                [1626148800.0, 0],
                [1626235200.0, 0],
                [1626321600.0, 0],
                [1626408000.0, 0],
                [1626494400.0, 0],
                [1626580800.0, 0],
                [1626667200.0, 0],
                [1626753600.0, 0],
                [1626840000.0, 0],
                [1626926400.0, 0],
                [1627012800.0, 0],
                [1627099200.0, 0],
                [1627185600.0, 0],
                [1627272000.0, 0],
                [1627358400.0, 0],
                [1627444800.0, 0],
                [1627531200.0, 0],
                [1627617600.0, 0],
                [1627704000.0, 0],
                [1627790400.0, 0],
                [1627876800.0, 0],
                [1627963200.0, 0],
                [1628049600.0, 0],
                [1628136000.0, 0],
                [1628222400.0, 0],
                [1628308800.0, 0],
                [1628395200.0, 0],
                [1628481600.0, 0],
                [1628568000.0, 0],
                [1628654400.0, 0],
                [1628740800.0, 0],
                [1628827200.0, 0],
                [1628913600.0, 0],
                [1629000000.0, 0],
                [1629086400.0, 0],
                [1629172800.0, 0],
                [1629259200.0, 0],
                [1629345600.0, 0],
                [1629432000.0, 0],
                [1629518400.0, 0],
                [1629604800.0, 0],
                [1629691200.0, 0],
                [1629777600.0, 0],
                [1629864000.0, 0],
                [1629950400.0, 0],
                [1630036800.0, 0],
                [1630123200.0, 0],
                [1630209600.0, 0],
                [1630296000.0, 0],
                [1630382400.0, 0],
                [1630468800.0, 0],
                [1630555200.0, 0],
                [1630641600.0, 0],
                [1630728000.0, 0],
                [1630814400.0, 1],
                [1630900800.0, 0],
                [1630987200.0, 0],
                [1631073600.0, 0],
                [1631160000.0, 0],
                [1631246400.0, 0],
                [1631332800.0, 1],
                [1631419200.0, 1],
                [1631505600.0, 0],
                [1631592000.0, 0],
                [1631678400.0, 0],
                [1631764800.0, 0],
                [1631851200.0, 1],
                [1631937600.0, 0],
                [1632024000.0, 0],
                [1632110400.0, 0],
                [1632196800.0, 0],
                [1632283200.0, 0],
                [1632369600.0, 0],
                [1632456000.0, 0],
                [1632542400.0, 0],
                [1632628800.0, 0],
            ],
            "performance": "Monthly",
            "deployment_dates_description": "",
            "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
        },
    ]

    assert result5 == expected_result5


# Test get "/LeadTimeToChange" endpoint
