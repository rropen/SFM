from datetime import datetime, timedelta
from time import mktime
from statistics import median
from sfm.routes.work_items import crud
from sfm.routes.projects import crud as proj_crud
from sfm.models import WorkItem, Project, MetricData, LeadTimeData
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


@router.get("/deployments", response_model=List[MetricData])
def get_deployments(
    project_id: Optional[int] = None,
    project_name: Optional[str] = None,
    all_deployments: Optional[bool] = True,
    db: Session = Depends(get_db),
):
    """
    ## Get Deployment Metric Info

    Get json data related to the deployments for a project or organization

    ---

    Query Parameters:
    - **all_deployments**: If *True*, all deployments will be returned for the org. If *False*, return deployments grouped by project.

    #### Either **project_id** or **project_name** being present causes returned items to only be associated with specified project. *If neither field is present, return data for all projects*
    - **project_id**: sets project for data
    - **project_name**: sets project the WorkItem belongs to

    """
    project = None
    if project_name and not project_id:
        project = db.exec(select(Project).where(Project.name == project_name)).first()
        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"No project found with the specified name: {project_name}",
            )
    elif project_id and not project_name:
        project = db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"No project found with the specified id: {project_id}",
            )
    elif project_id and project_name:
        project = db.exec(
            select(Project).where(
                and_(Project.id == project_id, Project.name == project_name)
            )
        ).first()
        if not project:
            raise HTTPException(
                status_code=404,
                detail="Either the project_name and project_id do not match, or there is not a project with the specified details. Try passing just one of the parameters instead of both.",
            )

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

        deployment_data = [
            {
                "project_name": project_name,
                "deployment_dates": deployment_dates,
                "deployment_frequency": deploy_frequency,
            }
        ]

        return deployment_data

    elif not all_deployments:
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

        return group_deployments

    else:
        all_items = crud.get_all(db)
        deployments = [item for item in all_items if (item.category == "Deployment")]
        project_name = "org"
        deployment_dates = [
            mktime(deploy.end_time.date().timetuple()) for deploy in deployments
        ]
        deploy_frequency = calc_frequency(deployments)

        deployment_data = [
            {
                "project_name": project_name,
                "deployment_dates": deployment_dates,
                "deployment_frequency": deploy_frequency,
            }
        ]

        return deployment_data


@router.get("/LeadTimeToChange", response_model=LeadTimeData)
def get_Lead_Time_To_Change(
    project_id: Optional[int] = None,
    project_name: Optional[str] = None,
    db: Session = Depends(get_db),
):

    """
    ## Get Lead Time to Change Metric

    Get json data describing lead time metric

    ---

    #### Either **project_id** or **project_name** being present causes returned items to only be associated with specified project. *If neither field is present, return data for all projects*
    - **project_id**: sets project data to be used for lead time calculation
    - **project_name**: sets project data to be used for lead time calculation

    """
    project = None
    if project_name and not project_id:
        project = db.exec(select(Project).where(Project.name == project_name)).first()
        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"No project found with the specified name: {project_name}",
            )
    elif project_id and not project_name:
        project = db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"No project found with the specified id: {project_id}",
            )
    elif project_id and project_name:
        project = db.exec(
            select(Project).where(
                and_(Project.id == project_id, Project.name == project_name)
            )
        ).first()
        if not project:
            raise HTTPException(
                status_code=404,
                detail="Either the project_name and project_id do not match, or there is not a project with the specified details. Try passing just one of the parameters instead of both.",
            )

    if project:
        pullRequests = [
            item for item in project.work_items if (item.category == "Pull Request")
        ]
        if not pullRequests:
            raise HTTPException(
                status_code=404,
                detail="No pull requests to main associated with specified project",
            )

    else:
        all_items = crud.get_all(db)
        pullRequests = [item for item in all_items if (item.category == "Pull Request")]
        if not pullRequests:
            raise HTTPException(
                status_code=404,
                detail="No pull requests to main in record for any project",
            )

    lead_times = []
    for request in pullRequests:
        for commit in request.commits:
            lead_times.append(commit.time_to_pull)

    # calculate median time in minutes
    print(median(lead_times))
    median_time_to_deploy = int(median(lead_times) / 60)

    if median_time_to_deploy < (24 * 60):  # Less than one day
        performance = "Elite"
    elif (median_time_to_deploy >= (24 * 60)) and (
        median_time_to_deploy < (7 * 24 * 60)
    ):  # between one day and one week
        performance = "High"
    elif (median_time_to_deploy >= (7 * 24 * 60)) and (
        median_time_to_deploy < (7 * 24 * 60 * 4)
    ):  # between one week and one month
        performance = "Medium"
    elif median_time_to_deploy >= (7 * 24 * 60 * 4):  # greater than one month
        performance = "Low"

    LeadTime_dict = {
        "lead_time": median_time_to_deploy,
        "time_units": "minutes",
        "performance": performance,
        "lead_time_description": "median lead time for a commit to get pulled to main branch in minutes",
        "performance_description": "Elite = less than one day, High = between one day and one week, Medium = bewtween one week and one month, Low = greater than one month",
    }

    return LeadTime_dict
