from datetime import datetime, timedelta
from time import mktime
from dateutil.relativedelta import relativedelta
from statistics import median
from sfm.routes.work_items import crud
from sfm.routes.projects import crud as proj_crud
from sfm.models import WorkItem, Project, ChartData, WorkItemCategory
from typing import List, Optional
from sqlmodel import Session, select, and_
from fastapi import APIRouter, HTTPException, Depends, Path, Header, Request
from sfm.database import engine


# Create a database connection we can use
def get_db():
    with Session(engine) as db:
        yield db


router = APIRouter()


def calc_frequency(
    deployments: List,
):  # generates the DORA metric based on only deployments in the last 3 months
    three_months_ago = datetime.now() - timedelta(days=84)
    recent_deploy_dates = [
        deployment.end_time
        for deployment in deployments
        if (deployment.end_time >= three_months_ago)
    ]

    deploy_frequency = "Yearly"  # for now

    days_deployed = (
        []
    )  # list of 12 integers that represent the number of days during that week a deployment occurred
    weekly_deployed = (
        []
    )  # list of 12 integers(1,0) that represent if a deploy happened during that week
    week_start = three_months_ago
    for i in range(12):  # 12 weeks in 3 months
        week_end = week_start + timedelta(days=7)
        deploys_in_week = []
        for deploy_date in recent_deploy_dates:
            if (
                (deploy_date >= week_start)
                and (deploy_date < week_end)
                and (deploy_date.date() not in deploys_in_week)
            ):
                # only one deploy per day counts
                deploys_in_week.append(deploy_date)

        days_deployed.append(len(deploys_in_week))

        if deploys_in_week:
            weekly_deployed.append(1)
        else:
            weekly_deployed.append(0)

        week_start += timedelta(days=7)

    monthly_deploys = []
    # list of 3 integers that represent if a deploy happened during that month
    # for i, week in enumerate(weekly_deployed):
    #     monthly_deploys[i % 3] += week

    for i in range(0, 12, 4):
        if any(weekly_deployed[i : i + 4]):
            monthly_deploys.append(1)
        else:
            monthly_deploys.append(0)

    # print("DAILY DEPLOYS:", days_deployed)
    # print("WEEKLY DEPLOYS:", weekly_deployed)
    # print("MONTHLY DEPLOYS:", monthly_deploys)

    # for i, week in enumerate(days_deployed):
    #    print(i + 1, "th Week had:", week, "deploys")

    if median(days_deployed) >= 3:
        deploy_frequency = "Daily"
    elif median(weekly_deployed) >= 1:
        deploy_frequency = "Weekly"
    elif median(monthly_deploys) >= 1:
        deploy_frequency = "Monthly"
    else:
        deploy_frequency = "Yearly"

    # print("DEPLOYMENT FREQUENCY VALUE:", median(days_deployed))

    # print("DEPLOYMENT FREQUENCY:", deploy_frequency)

    return deploy_frequency

    # Google Pseudocode:
    # 1. Grab deployments from the past 3 months from today's date.
    #   - Calculate Monthly deploys
    #   - Calculate Weekly deploys
    #   - Calculate Daily deploys
    # 2. Get median values for each category of deploys
    # 3. Go through Calc logic
    #   - If the **median** number of monthly deploys over the past 3 months is greater than 1 then "monthly"
    #       - If less than 1, then "yearly"
    #   - If the **median** number of *days per week* where a deployment occured is greater than 3, then "daily"
    #   - If the **median** number of *deployments per month* for the past 3 months is greater than
    # deployInWeek = deployments.split(weeks or weekdays)
    # deployFreq = average(deployInWeek)
    # jsonData.append({"week-range": deployFreq})


@router.get("/", response_model=List[ChartData])
def get_deployments(
    category: WorkItemCategory,
    project_id: Optional[int] = None,
    project_name: Optional[str] = None,
    group_projects: Optional[bool] = False,
    db: Session = Depends(get_db),
):
    """
    ## Get Chart Info

    Get the json data needed to produce an SFM chart on frontend
    Data should be formatted as a timeseries(?)
    """
    project = None
    if project_name and not project_id:
        project = db.exec(select(Project).where(Project.name == project_name)).first()
        if not project:
            return False
    elif project_id and not project_name:
        project = db.get(Project, project_id)
        if not project:
            return False
    elif project_id and project_name:
        project = db.exec(
            select(Project).where(
                and_(Project.id == project_id, Project.name == project_name)
            )
        ).first()
        if not project:
            return False

    if project:
        # return specific project deployment frequency json object
        project_name = project.name
        deployments = [
            item for item in project.work_items if (item.category == "Deployment")
        ]
        deployment_dates = [deploy.end_time.date() for deploy in deployments]
        deploy_frequency = calc_frequency(deployments)

    elif group_projects:
        print("Test in loop")
        projects = proj_crud.get_all(db)
        group_deployments = []
        for project in projects:
            project_name = project.name
            deployments = []
            deployment_dates = []
            for work_item in project.work_items:
                if work_item.category == "Deployment":
                    deployments.append(work_item)
                    deployment_dates.append(work_item.end_time.date())

            deploy_frequency = calc_frequency(deployments)
            group_deployments.append(
                {
                    "project_name": project_name,
                    "deployment_dates": deployment_dates,
                    "deployment_frequency": deploy_frequency,
                }
            )

    else:
        all_items = crud.get_all(db)
        deployments = [item for item in all_items if (item.category == "Deployment")]
        project_name = "org"
        deployment_dates = [deploy.end_time.date() for deploy in deployments]
        deploy_frequency = calc_frequency(deployments)

    if not group_projects:
        chart_data = [
            {
                "project_name": project_name,
                "deployment_dates": deployment_dates,
                "deployment_frequency": deploy_frequency,
            }
        ]
    else:
        chart_data = group_deployments

    return chart_data


@router.get("/test/", response_model=List[ChartData])
def get_deployments_test(
    category: WorkItemCategory,
    project_id: Optional[int] = None,
    project_name: Optional[str] = None,
    group_projects: Optional[bool] = False,
    db: Session = Depends(get_db),
):
    """
    ## Get Chart Info (Dates return in UNIX time, naive format)

    Get the json data needed to produce an SFM chart on frontend
    """
    project = None
    if project_name and not project_id:
        project = db.exec(select(Project).where(Project.name == project_name)).first()
        if not project:
            return False
    elif project_id and not project_name:
        project = db.get(Project, project_id)
        if not project:
            return False
    elif project_id and project_name:
        project = db.exec(
            select(Project).where(
                and_(Project.id == project_id, Project.name == project_name)
            )
        ).first()
        if not project:
            return False

    if project:
        # return specific project deployment frequency json object
        project_name = project.name
        deployments = [
            item for item in project.work_items if (item.category == "Deployment")
        ]
        deployment_dates = [
            mktime(deploy.end_time.date().timetuple()) for deploy in deployments
        ]
        deploy_frequency = calc_frequency(deployments)

    elif group_projects:
        print("Test in loop")
        projects = proj_crud.get_all(db)
        group_deployments = []
        for project in projects:
            project_name = project.name
            deployments = []
            deployment_dates = []
            for work_item in project.work_items:
                if work_item.category == "Deployment":
                    deployments.append(work_item)
                    deployment_dates.append(
                        mktime(work_item.end_time.date().timetuple())
                    )

            deploy_frequency = calc_frequency(deployments)
            group_deployments.append(
                {
                    "project_name": project_name,
                    "deployment_dates": deployment_dates,
                    "deployment_frequency": deploy_frequency,
                }
            )

    else:
        all_items = crud.get_all(db)
        deployments = [item for item in all_items if (item.category == "Deployment")]
        project_name = "org"
        deployment_dates = [
            mktime(deploy.end_time.date().timetuple()) for deploy in deployments
        ]
        deploy_frequency = calc_frequency(deployments)

    if not group_projects:
        chart_data = [
            {
                "project_name": project_name,
                "deployment_dates": deployment_dates,
                "deployment_frequency": deploy_frequency,
            }
        ]
    else:
        chart_data = group_deployments

    for obj in chart_data:
        for date in obj["deployment_dates"]:
            print(datetime.utcfromtimestamp(int(date)).strftime("%Y-%m-%d %H:%M:%S"))

    return chart_data


"""
@router.get("/LeadTimeToChange", response_model=LeadTimeData)
def get_pull_request(
    category: str,
    project_id: Optional[int] = None,
    project_name: Optional[str] = None,
    db: Session = Depends(get_db),
):

    project = None
    if project_name and not project_id:
        project = db.exec(select(Project).where(Project.name == project_name)).first()
        if not project:
            return False
    elif project_id and not project_name:
        project = db.get(Project, project_id)
        if not project:
            return False
    elif project_id and project_name:
        project = db.exec(
            select(Project).where(
                and_(Project.id == project_id, Project.name == project_name)
            )
        ).first()
        if not project:
            return False

    if project:
        # return specific project deployment frequency json object
        pullRequests = [
            item for item in project.work_items if (item.category == "Pull Request")
        ]
        lead_times = [pullRequest.commit_median_merge_time for pullRequest in pullRequests]

        #deploy_frequency = calc_frequency(deployments, deployment_dates)

    else:
        # return all project deployment frequency data in json object
        all_items = crud.get_all(db)
        pullRequests = [item for item in all_items if (item.category == "Pull Request")]
        lead_times = [pullRequest.commit_median_merge_time for pullRequest in pullRequests]

        #deploy_frequency = calc_frequency(deployments, deployment_dates)

    #calculate median time in minutes
    #median_time_to_deploy = int((median(commits_time_to_deploy) % 3600) // 60)

    LeadTime_dict = {
        "lead_time" : lead_time,
        "time_units" : "minutes",
        "performance" : performance,
        "lead_time_description" : "median lead time for a commit to get pulled to main branch in minutes",
        "performance_description" : "Elite = less than an hour, High = less than one day, Medium = less than one week, Low = Between one week and one month, Abismal = Greater than one month",
    }

    return LeadTime_dict
"""
