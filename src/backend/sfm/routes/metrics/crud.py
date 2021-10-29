import logging
from datetime import datetime, timedelta
from statistics import median
from sfm.config import get_settings
from sfm.routes.work_items import crud
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
from sfm.utils import unix_time_seconds, project_selector
from opencensus.ext.azure.log_exporter import AzureLogHandler

app_settings = get_settings()

logging.basicConfig(
    filename="logs.log",
    level=logging.DEBUG,
    format="%(asctime)s %(pathname)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(
        connection_string="InstrumentationKey=" + app_settings.AZURE_LOGGING_CONN_STR
    )
)

router = APIRouter()


def calc_frequency(
    deployments: List,
):  # generates deployment frequency based on only deployments in the last 3 months
    three_months_ago = datetime.now() - timedelta(days=84)  # 3 months ~= 12 weeks
    recent_deploy_dates = [
        deployment.end_time
        for deployment in deployments
        if (deployment.end_time >= three_months_ago)
    ]

    days_deployed = (
        []
    )  # list of 12 integers that represent the number of days that a deployment occured during each of the 12 weeks
    weekly_deployed = (
        []
    )  # list of 12 integers(1,0) that represent if a deploy happened during that week
    week_start = three_months_ago
    for i in range(12):  # 12 weeks in 3 months
        week_end = week_start + timedelta(days=7)
        deploys_in_week = []
        for (
            deploy_date
        ) in recent_deploy_dates:  # the last 3 months (12 weeks) of deployments
            if (
                (deploy_date >= week_start)
                and (deploy_date < week_end)
                and (
                    deploy_date.date() not in deploys_in_week
                )  # count each day 1 time even if multiple deployments occur on that day
            ):
                # only one deploy per day counts, track deploys
                deploys_in_week.append(deploy_date.date())

        days_deployed.append(len(deploys_in_week))

        # set integer (0 or 1) for if a week contained at least 1 deployment
        if deploys_in_week:
            weekly_deployed.append(1)
        else:
            weekly_deployed.append(0)

        week_start += timedelta(days=7)

    monthly_deploys = (
        []
    )  # list of 3 integers (0 or 1) that represent if a deploy happened during that month
    for i in range(0, 12, 4):
        if any(weekly_deployed[i : i + 4]):
            monthly_deploys.append(1)
        else:
            monthly_deploys.append(0)

    if median(days_deployed) >= 3:
        performance = "Daily"
    elif median(weekly_deployed) >= 1:
        performance = "Weekly"
    elif median(monthly_deploys) >= 1:
        performance = "Monthly"
    else:
        performance = "Yearly"

    return performance


def combine_deploys(deployment_dates):  # deployment_dates: [date, date, date]
    if deployment_dates == []:
        logger.debug('func="combine_deploys" debug="deployment_dates was empty"')
        return []
    initial_date = min(deployment_dates)
    total_days = (datetime.now().date() - initial_date).days
    grouped_deploys = []
    for iter_day in range(0, total_days + 1):
        day = initial_date + timedelta(days=iter_day)

        # if the current day has a deployment, store number of deployments on that day with the unix time
        # for days with no deployment, store a 0 with the unix time
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


def lead_times_per_day(
    commit_dates, lead_times
):  # commit_dates: [date, date, ...], lead_times: [int, int, ...]
    initial_date = min(commit_dates)

    total_days = (datetime.now().date() - initial_date).days
    daily_commits = []
    daily_lead_times = []

    for iter_day in range(0, total_days + 1):
        day = initial_date + timedelta(days=iter_day)

        indicies = [i for i, date in enumerate(commit_dates) if date == day]
        # return list of indices of commits in commit_dates where commit date == day
        # multiple commits could happen on a single day

        day_lead_times = []
        for index in indicies:
            day_lead_times.append(lead_times[index])

        # if there are commits on a given day, store the number commits on that date with the unix time
        # for days without a commit, pair a 0 with the unix date
        if day in commit_dates:
            daily_commits.append(
                [unix_time_seconds(day), commit_dates.count(day)]
            )  # counts number dates that repeat in list and pair it with UNIX dates
            daily_lead_times.append(
                [unix_time_seconds(day), int((median(day_lead_times)) / 60)]
            )  # convert seconds in db to minutes for return
        else:
            daily_commits.append(
                [unix_time_seconds(day), 0]
            )  # if not in list then deployment must not have happened on this day, add 0
            daily_lead_times.append([unix_time_seconds(day), 0])

    return [daily_commits, daily_lead_times]


def group_failures(
    deployments,
):  # deployments: [{deploy}, {deploy}, ...] where {deploy} is a WorkItem object that meets criteria to be a deployment
    if deployments == []:
        logger.debug('func="group_failures" debug="deployments is empty"')
        return []
    deployment_dates = [deploy.end_time.date() for deploy in deployments]
    failed_deployment_dates = [
        deploy.end_time.date() for deploy in deployments if deploy.failed is True
    ]
    initial_date = min(deployment_dates)

    total_days = (datetime.now().date() - initial_date).days
    daily_failure_rate = []

    for iter_day in range(0, total_days + 1):
        day = initial_date + timedelta(days=iter_day)

        if day in failed_deployment_dates:
            num_failed_deploys = failed_deployment_dates.count(day)
            num_deploys = deployment_dates.count(day)
            daily_failure_rate.append(
                [unix_time_seconds(day), num_failed_deploys / num_deploys]
            )  # calcs failure rate and puts it with UNIX time
        else:
            daily_failure_rate.append(
                [unix_time_seconds(day), 0]
            )  # if not in list then failure must not have happened on this day, add 0

    return daily_failure_rate


def group_restores(
    closed_prod_defects,
):  # closed_prod_defects: [{defect}, {defect}, ...] where {defect} is a WorkItem that meets the criteria of a Production Defect
    if closed_prod_defects == []:
        logger.debug('func="group_restores" debug="closed_prod_defects is empty"')
        return []
    restore_dates = [restore.end_time.date() for restore in closed_prod_defects]
    initial_date = min(restore_dates)

    total_days = (datetime.now().date() - initial_date).days
    daily_restores = []

    for iter_day in range(0, total_days + 1):
        day = initial_date + timedelta(days=iter_day)

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
            )  # median of duration open time for production defects that were resolved on the current day
            daily_restores.append(
                [unix_time_seconds(day), median_restore_time]
            )  # store median restore time for that day and puts it with UNIX
        else:
            daily_restores.append(
                [unix_time_seconds(day), 0]
            )  # if not in list then restore must not have happened on this day, add 0

    return daily_restores


def get_deployments_crud(db, project_name, project_id):
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
            "deployment_dates_description": "List of lists, where each sublist consits of [unix date, number of deploys on that date]",
            "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
        }

        return deployment_data

    else:  # if project not specified, use all
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
            "deployment_dates_description": "List of lists, where each sublist consits of [unix date, number of deploys on that date]",
            "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
        }

        return deployment_data


def lead_time_to_change_crud(db, project_name, project_id):
    project = project_selector(db, project_name, project_id)

    if project:
        pull_requests = [
            item for item in project.work_items if (item.category == "Pull Request")
        ]
        if not pull_requests:
            logger.warning(
                'method="GET" path="metrics/LeadTimeToChange" warning="No pull requests to main with specified project"'
            )

        project_name = project.name

    else:  # if project not specified, use all
        all_items = crud.get_all(db)
        pull_requests = [
            item for item in all_items if (item.category == "Pull Request")
        ]
        if not pull_requests:
            logger.warning(
                'method="GET" path="metrics/LeadTimeToChange" warning="No pull requests to main in record for any project"'
            )
        project_name = "all"

    if not pull_requests:  # if no pull requests exist, return -1
        median_time_to_deploy = -1
        performance = "No pull requests to main"
        daily_commits = []
        daily_lead_times = []

    else:  # when pull requests do exist..
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


def time_to_restore_crud(db, project_name, project_id):

    project = project_selector(db, project_name, project_id)
    performance = None

    if project:
        closed_prod_defects = db.exec(
            select(WorkItem).where(
                and_(
                    WorkItem.project_id == project.id,
                    WorkItem.category == "Production Defect",
                    WorkItem.end_time
                    != None,  # noqa: E711 # end_time != None means defect is closed
                )
            )
        ).all()
        project_name = project.name
    else:
        closed_prod_defects = db.exec(
            select(WorkItem).where(
                and_(
                    WorkItem.category == "Production Defect",
                    WorkItem.end_time
                    != None,  # noqa: E711 # end_time != None means defect is closed
                )
            )
        ).all()
        project_name = "all"

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
        logger.warning(
            'method="GET" path="metrics/TimeToRestore" warning="No closed production defects exist in the last 3 months"'
        )

    daily_time_to_restore = group_restores(closed_prod_defects)

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


def change_failure_rate_crud(db, project_name, project_id):

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
