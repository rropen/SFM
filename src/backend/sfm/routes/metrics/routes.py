import logging
from datetime import datetime, timedelta
from statistics import median
from sfm.config import get_settings
from sfm.routes.work_items import crud
from sfm.routes.projects import crud as proj_crud
from sfm.dependencies import get_db
from sfm.models import (
    WorkItem,
    Project,
    DeploymentData,
    LeadTimeData,
    ChangeFailureRateData,
    TimeToRestoreData,
)
from typing import List, Optional
from sqlmodel import Session, select, and_
from fastapi import APIRouter, HTTPException, Depends, Path, Header, Request
from sfm.database import engine
from sfm.utils import unix_time_seconds, project_selector
from opencensus.ext.azure.log_exporter import AzureLogHandler

app_settings = get_settings()

logging.basicConfig(
    filename="logs.log",
    level=logging.DEBUG,
    format="%(asctime)s %(pathname)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)
# logger.addHandler(
#     AzureLogHandler(connection_string=app_settings.AZURE_LOGGING_CONN_STR)
# )

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
        performance = "Daily"
    elif median(weekly_deployed) >= 1:
        performance = "Weekly"
    elif median(monthly_deploys) >= 1:
        performance = "Monthly"
    else:
        performance = "Yearly"

    # print("DEPLOYMENT FREQUENCY VALUE:", median(days_deployed))

    # print("DEPLOYMENT FREQUENCY:", deploy_frequency)

    return performance

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


def combine_deploys(deployment_dates):  # [date, date, date]
    if deployment_dates == []:
        logger.debug('func="combine_deploys" debug="deployment_dates was empty"')
        return []
    initial_date = min(deployment_dates)  # date
    total_days = (datetime.now().date() - initial_date).days  # number of days
    grouped_deploys = []
    for iter_day in range(0, total_days + 1):  # loops through every day
        day = initial_date + timedelta(days=iter_day)  # date
        if day in deployment_dates:
            grouped_deploys.append(
                [unix_time_seconds(day), deployment_dates.count(day)]
            )  # counts number dates that repeat in list and puts it with UNIX
            # [[date, num], [date, num]]
        else:
            grouped_deploys.append(
                [unix_time_seconds(day), 0]
            )  # if not in list then deployment must not have happened on this day, add 0

    return grouped_deploys


def lead_times_per_day(commit_dates, lead_times):  # [date, date, date]
    initial_date = min(commit_dates)  # date

    total_days = (datetime.now().date() - initial_date).days  # number of days
    daily_commits = []
    daily_lead_times = []

    for iter_day in range(0, total_days + 1):  # loops through every day
        day = initial_date + timedelta(days=iter_day)  # date

        indicies = [i for i, date in enumerate(commit_dates) if date == day]

        day_lead_times = []
        for index in indicies:
            day_lead_times.append(lead_times[index])

        if day in commit_dates:
            daily_commits.append(
                [unix_time_seconds(day), commit_dates.count(day)]
            )  # counts number dates that repeat in list and puts it with UNIX
            daily_lead_times.append(
                [unix_time_seconds(day), (median(day_lead_times)) / 60]
            )  # convert seconds in db to minutes for return
        else:
            daily_commits.append(
                [unix_time_seconds(day), 0]
            )  # if not in list then deployment must not have happened on this day, add 0
            daily_lead_times.append([unix_time_seconds(day), 0])

    return [daily_commits, daily_lead_times]


def group_failures(deployments):
    if deployments == []:
        logger.debug('func="group_failures" debug="deployments is empty"')
        return []
    deployment_dates = [deploy.end_time.date() for deploy in deployments]
    failed_deployment_dates = [
        deploy.end_time.date() for deploy in deployments if deploy.failed is True
    ]
    initial_date = min(deployment_dates)  # date

    total_days = (datetime.now().date() - initial_date).days  # number of days
    daily_failure_rate = []

    for iter_day in range(0, total_days + 1):  # loops through every day
        day = initial_date + timedelta(days=iter_day)  # date

        if day in failed_deployment_dates:
            num_failed_deploys = failed_deployment_dates.count(day)
            num_deploys = deployment_dates.count(day)
            daily_failure_rate.append(
                [unix_time_seconds(day), num_failed_deploys / num_deploys]
            )  # calcs failure rate and puts it with UNIX
        else:
            daily_failure_rate.append(
                [unix_time_seconds(day), 0]
            )  # if not in list then failure must not have happened on this day, add 0

    return daily_failure_rate


def group_restores(db, closed_prod_defects):
    if closed_prod_defects == []:
        logger.debug('func="group_restores" debug="closed_prod_defects is empty"')
        return []
    restore_dates = [restore.end_time.date() for restore in closed_prod_defects]
    initial_date = min(restore_dates)  # date

    total_days = (datetime.now().date() - initial_date).days  # number of days
    daily_restores = []

    for iter_day in range(0, total_days + 1):  # loops through every day
        day = initial_date + timedelta(days=iter_day)  # date

        if day in restore_dates:
            median_restore_time = (
                median(
                    [
                        defect.duration_open
                        for defect in closed_prod_defects
                        if (defect.end_time.date() == day)
                    ]
                )
                / 3600
            )
            daily_restores.append(
                [unix_time_seconds(day), median_restore_time]
            )  # calcs median restore time for that day and puts it with UNIX
        else:
            daily_restores.append(
                [unix_time_seconds(day), 0]
            )  # if not in list then restore must not have happened on this day, add 0

    return daily_restores


@router.get("/deployments", response_model=DeploymentData)
def get_deployments(
    project_id: Optional[int] = None,
    project_name: Optional[str] = None,
    # all_deployments: Optional[bool] = True,
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
    logger.info('method="GET" path="metrics/deployments"')

    project = project_selector(db, project_name, project_id)

    if project:
        # return specific project deployment frequency json object
        project_name = project.name
        deployments = [
            item for item in project.work_items if (item.category == "Deployment")
        ]

        deployment_dates = [deploy.end_time.date() for deploy in deployments]
        grouped_deploys = combine_deploys(deployment_dates)
        performance = calc_frequency(deployments)

        deployment_data = {
            "project_name": project_name,
            "deployment_dates": grouped_deploys,
            "performance": performance,
            "deployment_dates_description": "",
            "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
        }

        return deployment_data

    # elif not all_deployments:
    #     projects = proj_crud.get_all(db)
    #     group_deployments = []
    #     for project in projects:
    #         project_name = project.name
    #         deployments = []
    #         deployment_dates = []
    #         for work_item in project.work_items:
    #             if work_item.category == "Deployment":
    #                 deployments.append(work_item)
    #                 deployment_dates.append(work_item.end_time.date())

    #         grouped_deploys = combine_deploys(deployment_dates)
    #         performance = calc_frequency(deployments)
    #         group_deployments.append(
    #             {
    #                 "project_name": project_name,
    #                 "deployment_dates": grouped_deploys,
    #                 "performance": performance,
    #                 "deployment_dates_description": "",
    #                 "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
    #             }
    #         )
    #
    #     return group_deployments

    else:
        all_items = crud.get_all(db)
        deployments = [item for item in all_items if (item.category == "Deployment")]
        project_name = "all"
        deployment_dates = [deploy.end_time.date() for deploy in deployments]

        grouped_deploys = combine_deploys(deployment_dates)
        performance = calc_frequency(deployments)

        deployment_data = {
            "project_name": project_name,
            "deployment_dates": grouped_deploys,
            "performance": performance,
            "deployment_dates_description": "",
            "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
        }

        return deployment_data


@router.get("/LeadTimeToChange", response_model=LeadTimeData)
def get_lead_time_to_change(
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
    logger.info('method="GET" path="metrics/LeadTimeToChange"')

    project = project_selector(db, project_name, project_id)

    if project:
        pull_requests = [
            item for item in project.work_items if (item.category == "Pull Request")
        ]
        if not pull_requests:
            logger.warning(
                'method="GET" path="metrics/LeadTimeToChange" warning="No pull requests to main with specified project"'
            )
            # raise HTTPException(
            #     status_code=404,
            #     detail="No pull requests to main associated with specified project",
            # )
        project_name = project.name

    else:
        all_items = crud.get_all(db)
        pull_requests = [
            item for item in all_items if (item.category == "Pull Request")
        ]
        if not pull_requests:
            logger.warning(
                'method="GET" path="metrics/LeadTimeToChange" warning="No pull requests to main in record for any project"'
            )
        project_name = "all"

    if not pull_requests:
        median_time_to_deploy = -1
        performance = "No pull requests to main"
        daily_commits = []
        daily_lead_times = []

    else:
        lead_times = []
        commit_dates = []
        for request in pull_requests:
            for commit in request.commits:
                lead_times.append(commit.time_to_pull)
                commit_dates.append(commit.date.date())

        [daily_commits, daily_lead_times] = lead_times_per_day(commit_dates, lead_times)

        # calculate median time in minutes
        median_time_to_deploy = int(median(lead_times) / 60)

        if median_time_to_deploy < (24 * 60):  # Less than one day
            performance = "One Day"
        elif (median_time_to_deploy >= (24 * 60)) and (
            median_time_to_deploy < (7 * 24 * 60)
        ):  # between one day and one week
            performance = "One Week"
        elif (median_time_to_deploy >= (7 * 24 * 60)) and (
            median_time_to_deploy < (7 * 24 * 60 * 4)
        ):  # between one week and one month
            performance = "One Month"
        elif median_time_to_deploy >= (7 * 24 * 60 * 4):  # greater than one month
            performance = "Greater than One Month"

    lead_time_dict = {
        "lead_time": median_time_to_deploy,
        "time_units": "minutes",
        "performance": performance,
        "daily_commits": daily_commits,
        "daily_lead_times": daily_lead_times,
        "project_name": project_name,
        "lead_time_description": "median lead time for a commit to get pulled to main branch in minutes",
        "performance_description": "Elite = less than one day, High = between one day and one week, Medium = bewtween one week and one month, Low = greater than one month",
        "daily_commits_description": "List of lists, where each sublist consits of [unix date, number of commits on that date]",
        "daily_lead_times_description": "List of lists, where each sublist consits of [unix date, median lead time to deploy for commits occuring on that date]",
    }

    return lead_time_dict


@router.get("/TimeToRestore", response_model=TimeToRestoreData)
def get_time_to_restore(
    project_id: Optional[int] = None,
    project_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    ## Get Time to Restore Metric

    Get json data describing time to restore metric

    ---

    #### Either **project_id** or **project_name** being present causes returned items to only be associated with specified project. *If neither field is present, return data for all projects*
    - **project_id**: sets project data to be used for calculation
    - **project_name**: sets project data to be used for calculation

    """
    logger.info('method="GET" path="metrics/TimeToRestore"')

    project = project_selector(db, project_name, project_id)
    performance = None

    if project:
        closed_prod_defects = db.exec(
            select(WorkItem).where(
                and_(
                    WorkItem.project_id == project.id,
                    WorkItem.category == "Production Defect",
                    WorkItem.end_time != None,  # noqa: E711
                )
            )
        ).all()  # noqa: E711
        recent_prod_defects = [
            defect
            for defect in closed_prod_defects
            if defect.end_time >= (datetime.now() - timedelta(days=84))
        ]
        recent_prod_defect_times = [item.duration_open for item in recent_prod_defects]
        if recent_prod_defect_times != []:
            time_to_restore = median(recent_prod_defect_times) / 3600
        else:
            time_to_restore = -1
            performance = "No closed production defects exist in the last 3 months"

        daily_time_to_restore = group_restores(db, closed_prod_defects)

        project_name = project.name
    else:
        closed_prod_defects = db.exec(
            select(WorkItem).where(
                and_(
                    WorkItem.category == "Production Defect",
                    WorkItem.end_time != None,  # noqa: E711
                )
            )
        ).all()
        recent_prod_defects = [
            defect
            for defect in closed_prod_defects
            if defect.end_time >= (datetime.now() - timedelta(days=84))
        ]
        recent_prod_defect_times = [item.duration_open for item in recent_prod_defects]
        if recent_prod_defect_times != []:
            time_to_restore = median(recent_prod_defect_times) / 3600
        else:  # pragma: no cover (logic gets tested when single project specified)
            time_to_restore = -1
            performance = "No closed production defects in last 3 months"
            logger.warning(
                'method="GET" path="metrics/TimeToRestore" warning="No closed production defects exist in the last 3 months"'
            )

        daily_time_to_restore = group_restores(db, closed_prod_defects)
        project_name = "all"

    if not performance:
        if time_to_restore < 1:
            performance = "Less than one hour"
        elif time_to_restore < 24:
            performance = "Less than one day"
        elif time_to_restore < 24 * 7:
            performance = "Less than one week"
        else:
            performance = "Between one week and one month"

    time_to_restore_dict = {
        "time_to_restore": time_to_restore,  # only for last 3 months
        "performance": performance,
        "daily_times_to_restore": daily_time_to_restore,
        "project_name": project_name,
        "time_to_restore_description": "median time to restore service in hours (time from bug noticed to pull request to main with fix) over the past three months ",
        "performance_description": "Elite = less than one hour, High = less than one day, Medium = less than one week, Low = between one week and one month",
        "daily_times_to_restore_description": "list of lists, where each item in the list consists of [unix date, median time to restore for all bugs logged on that date in hours]",
    }

    return time_to_restore_dict


@router.get("/ChangeFailureRate", response_model=ChangeFailureRateData)
def get_change_failure_rate(
    project_id: Optional[int] = None,
    project_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    ## Get Change Failure Rate Metric

    Get json data describing change failure rate metric

    ---

    #### Either **project_id** or **project_name** being present causes returned items to only be associated with specified project. *If neither field is present, return data for all projects*
    - **project_id**: sets project data to be used for calculation
    - **project_name**: sets project data to be used for calculation

    """
    project = project_selector(db, project_name, project_id)

    if project:
        deployments = db.exec(
            select(WorkItem).where(
                and_(
                    WorkItem.project_id == project.id,
                    WorkItem.category == "Pull Request",
                    WorkItem.end_time >= (datetime.now() - timedelta(days=84)),
                )
            )
        ).all()  # last 3 months for metric calculation
        all_deployments = db.exec(
            select(WorkItem).where(
                and_(
                    WorkItem.project_id == project.id,
                    WorkItem.category == "Pull Request",
                )
            )
        ).all()  # all time for daily calculation for charts
        project_name = project.name
    else:
        deployments = db.exec(
            select(WorkItem).where(
                and_(
                    WorkItem.category == "Pull Request",
                    WorkItem.end_time >= (datetime.now() - timedelta(days=84)),
                )
            )
        ).all()  # last 3 months for metric calculation
        all_deployments = db.exec(
            select(WorkItem).where(WorkItem.category == "Pull Request")
        ).all()  # all time for daily calculation for charts
        project_name = "all"

    failed_deploys = [deploy for deploy in deployments if deploy.failed is True]

    if len(deployments) == 0:
        change_failure_rate = 0
    else:
        change_failure_rate = len(failed_deploys) / len(deployments)

    daily_failure_rate = group_failures(all_deployments)

    change_failure_rate_dict = {
        "change_failure_rate": change_failure_rate,
        "daily_change_failure_rate": daily_failure_rate,
        "project_name": project_name,
        "change_failure_rate_description": "Number of failed deployments per total number of deployments",
        "daily_change_failure_rate_description": "list of lists, where each item in the list consists of [unix date, change failure rate for deployments released on that date]",
    }

    return change_failure_rate_dict
