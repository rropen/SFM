import pytest
from time import mktime
from sfm.routes.metrics import routes
from sfm.routes.utilities.routes import random_sha
from sqlmodel import Session, select
from sfm.models import Project, WorkItem, Commit
from tests.conftest import hashed_token1
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sfm.utils import unix_time_seconds

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
            "name": "Test Project for Monthly Deploys",
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
        [unix_time_seconds(datetime(2021, 5, 31).date()), 3],
        [unix_time_seconds(datetime(2021, 6, 1).date()), 1],
        [unix_time_seconds(datetime(2021, 6, 2).date()), 0],
        [unix_time_seconds(datetime(2021, 6, 3).date()), 1],
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
            [unix_time_seconds(datetime(2021, 5, 31).date()), 3],
            [unix_time_seconds(datetime(2021, 6, 1).date()), 1],
            [unix_time_seconds(datetime(2021, 6, 2).date()), 0],
            [unix_time_seconds(datetime(2021, 6, 3).date()), 1],
        ],
        [
            [unix_time_seconds(datetime(2021, 5, 31).date()), 2.0],
            [unix_time_seconds(datetime(2021, 6, 1).date()), 4.0],
            [unix_time_seconds(datetime(2021, 6, 2).date()), 0.0],
            [unix_time_seconds(datetime(2021, 6, 3).date()), 5.0],
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
    time_shift = datetime.now().date() - datetime(2021, 8, 19).date()
    deploy_dates = [deploy + time_shift for deploy in deploy_dates]
    deployment_dates = [
        [unix_time_seconds(deploy_dates[0].date()), 1],  # Week 1
        [unix_time_seconds(deploy_dates[1].date()), 0],  # Week 2
        [unix_time_seconds(deploy_dates[2].date()), 0],  # Week 10
        [unix_time_seconds(deploy_dates[3].date()), 0],  # Week 11
        [unix_time_seconds(deploy_dates[4].date()), 0],
        [unix_time_seconds(deploy_dates[5].date()), 0],  # Week 12
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
    result4[0]["deployment_dates"] = result4[0]["deployment_dates"][:6]
    print(result4)
    deployment_dates = [
        [unix_time_seconds(deploy_dates[0].date()), 2],  # Week 1
        [unix_time_seconds(deploy_dates[1].date()), 0],  # Week 2
        [unix_time_seconds(deploy_dates[2].date()), 0],  # Week 10
        [unix_time_seconds(deploy_dates[3].date()), 0],  # Week 11
        [unix_time_seconds(deploy_dates[4].date()), 0],
        [unix_time_seconds(deploy_dates[5].date()), 0],  # Week 12
    ]

    expected_result4 = [
        {
            "project_name": "org",
            "deployment_dates": deployment_dates,
            "performance": "Daily",
            "deployment_dates_description": "",
            "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
        }
    ]
    print(expected_result4)
    assert result4 == expected_result4

    """Testing if you set all_deployments to false"""
    response5 = client.get("/metrics/deployments", params={"all_deployments": "false"})
    assert response5 is not None
    assert response5.status_code == 200

    result5 = response5.json()
    print(result5)
    print(result5[:])
    for i in range(0, len(result5)):
        result5[i]["deployment_dates"] = result5[i]["deployment_dates"][:6]

    deployment_dates = [
        [unix_time_seconds(deploy_dates[0].date()), 1],  # Week 1
        [unix_time_seconds(deploy_dates[1].date()), 0],  # Week 2
        [unix_time_seconds(deploy_dates[2].date()), 0],  # Week 10
        [unix_time_seconds(deploy_dates[3].date()), 0],  # Week 11
        [unix_time_seconds(deploy_dates[4].date()), 0],
        [unix_time_seconds(deploy_dates[5].date()), 0],  # Week 12
    ]

    expected_result5 = [
        {
            "project_name": "Test Project 1",
            "deployment_dates": deployment_dates,
            "performance": "Daily",
            "deployment_dates_description": "",
            "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
        },
        {
            "project_name": "Test Project 2",
            "deployment_dates": deployment_dates,
            "performance": "Monthly",
            "deployment_dates_description": "",
            "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
        },
        {
            "project_name": "Test Project with no WorkItems",
            "deployment_dates": [],
            "performance": "Yearly",
            "deployment_dates_description": "",
            "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
        },
    ]
    print(result5)
    assert result5 == expected_result5


# Test get "/LeadTimeToChange" endpoint
def test_get_lead_time_endpoint(client: TestClient, db: Session):
    response = client.get("/metrics/LeadTimeToChange")
    assert response is not None
    assert response.status_code == 200

    day_proj = Project(
        **{
            "name": "Test Project for Commits",
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
            "name": "Test Project for Commits",
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
            "name": "Test Project for Commits",
            "lead_name": "Deploy Deployer",
            "lead_email": "commit-deploy@dora.com",
            "description": "A test project for testing",
            "location": "githubville",
            "repo_url": "github.com/DoraEnterprises",
            "on_prem": False,
            "project_auth_token_hashed": hashed_token1,
        }
    )
    gtmonth_proj = Project(
        **{
            "name": "Test Project for Commits",
            "lead_name": "Deploy Deployer",
            "lead_email": "commit-deploy@dora.com",
            "description": "A test project for testing",
            "location": "githubville",
            "repo_url": "github.com/DoraEnterprises",
            "on_prem": False,
            "project_auth_token_hashed": hashed_token1,
        }
    )
    db.add(day_proj)
    db.add(week_proj)
    db.add(month_proj)
    db.add(gtmonth_proj)
    db.commit()
    db.refresh(day_proj)
    db.refresh(week_proj)
    db.refresh(month_proj)
    db.refresh(gtmonth_proj)

    day_work = WorkItem(
        **{
            "category": "Pull Request",
            "end_time": datetime(2021, 6, 11),
            "project_id": day_proj.id,
        }
    )
    week_work = WorkItem(
        **{
            "category": "Pull Request",
            "end_time": datetime(2021, 6, 11),
            "project_id": week_proj.id,
        }
    )
    month_work = WorkItem(
        **{
            "category": "Pull Request",
            "end_time": datetime(2021, 6, 11),
            "project_id": month_proj.id,
        }
    )
    gtmonth_work = WorkItem(
        **{
            "category": "Pull Request",
            "end_time": datetime(2021, 6, 11),
            "project_id": gtmonth_proj.id,
        }
    )
    db.add_all([day_work, week_work, month_work, gtmonth_work])
    db.commit()
    db.refresh(day_work)
    db.refresh(week_work)
    db.refresh(month_work)
    db.refresh(gtmonth_work)

    daily_commits = []
    weekly_commits = []
    monthly_commits = []
    gtmonth_commits = []
    end_date = datetime(2021, 6, 11)
    for day in range(0, 40):
        date = end_date - timedelta(days=day)
        if day <= 1:
            daily_commits.append(
                Commit(
                    **{
                        "sha": random_sha(day),
                        "date": date,
                        "message": "Test commit message for testing commits in the database",
                        "author": "Mr. Commiter",
                        "work_item_id": day_work.id,
                        "time_to_pull": int((day_work.end_time - date).total_seconds()),
                    }
                )
            )
        elif day > 1 and day <= 7:
            weekly_commits.append(
                Commit(
                    **{
                        "sha": random_sha(day),
                        "date": date,
                        "message": "Test commit message for testing commits in the database",
                        "author": "Mr. Commiter",
                        "work_item_id": week_work.id,
                        "time_to_pull": int(
                            (week_work.end_time - date).total_seconds()
                        ),
                    }
                )
            )
        elif day > 7 and day <= 30:
            monthly_commits.append(
                Commit(
                    **{
                        "sha": random_sha(day),
                        "date": date,
                        "message": "Test commit message for testing commits in the database",
                        "author": "Mr. Commiter",
                        "work_item_id": month_work.id,
                        "time_to_pull": int(
                            (month_work.end_time - date).total_seconds()
                        ),
                    }
                )
            )
    date = end_date - timedelta(days=day)
    gtmonth_commits.append(
        Commit(
            **{
                "sha": random_sha(day),
                "date": date,
                "message": "Test commit message for testing commits in the database",
                "author": "Mr. Commiter",
                "work_item_id": gtmonth_work.id,
                "time_to_pull": int((gtmonth_work.end_time - date).total_seconds()),
            }
        )
    )

    db.add_all(daily_commits)
    db.add_all(weekly_commits)
    db.add_all(monthly_commits)
    db.add_all(gtmonth_commits)
    db.commit()

    db.refresh(day_work)
    db.refresh(week_work)
    db.refresh(month_work)
    db.refresh(gtmonth_work)

    """Test Metrics Calculate correctly"""
    day_response = client.get(
        "/metrics/LeadTimeToChange", params={"project_id": f"{day_proj.id}"}
    )
    day_result = day_response.json()
    assert day_result["performance"] == "One Day"

    week_response = client.get(
        "/metrics/LeadTimeToChange", params={"project_id": f"{week_proj.id}"}
    )
    week_result = week_response.json()
    assert week_result["performance"] == "One Week"

    month_response = client.get(
        "/metrics/LeadTimeToChange", params={"project_id": f"{month_proj.id}"}
    )
    month_result = month_response.json()
    assert month_result["performance"] == "One Month"

    gtmonth_response = client.get(
        "/metrics/LeadTimeToChange", params={"project_id": f"{gtmonth_proj.id}"}
    )
    gtmonth_result = gtmonth_response.json()
    assert gtmonth_result["performance"] == "Greater than One Month"

    """Test giving project_name returns correctly"""
    day_response = client.get(
        "/metrics/LeadTimeToChange", params={"project_name": f"{day_proj.name}"}
    )
    day_result = day_response.json()
    assert day_result["performance"] == "One Day"

    """Test giving project_name and project_id returns correctly"""
    day_response = client.get(
        "/metrics/LeadTimeToChange",
        params={"project_name": f"{day_proj.name}", "project_id": f"{day_proj.id}"},
    )
    day_result = day_response.json()
    assert day_result["performance"] == "One Day"

    """Test giving a project with no workItems raises exception"""
    with pytest.raises(Exception) as ex:
        client.get(
            "/metrics/LeadTimeToChange",
            params={"project_name": "Test Project with no WorkItems"},
        )
        assert (
            ex.value.message
            == "No pull requests to main associated with specified project"
        )

    """Test giving a project name with no matching project raises exception"""
    response = client.get(
        "/metrics/LeadTimeToChange", params={"project_name": "Gibberish"}
    )
    assert response.status_code == 404

    """Test giving a project id with no matching project raises exception """
    response = client.get("/metrics/LeadTimeToChange", params={"project_id": "7777"})
    assert response.status_code == 404

    """Test get request when no pull requests exist in database"""
    pull_requests = db.exec(
        select(WorkItem).where(WorkItem.category == "Pull Request")
    ).all()
    for item in pull_requests:
        db.delete(item)
    db.commit()

    response = client.get("/metrics/LeadTimeToChange")
    assert response.status_code == 404
