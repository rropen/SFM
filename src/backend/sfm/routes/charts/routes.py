from datetime import datetime
from dateutil.relativedelta import relativedelta
from statistics import median
from sfm.routes.work_items import crud
from sfm.models import WorkItemRead, WorkItemCreate, WorkItemUpdate, Project
from typing import List, Optional
from sqlmodel import Session, select, and_
from fastapi import APIRouter, HTTPException, Depends, Path, Header, Request
from sfm.database import engine


# Create a database connection we can use
def get_db():
    with Session(engine) as db:
        yield db


router = APIRouter()


@router.get("/")
def get_work_items(
    category: str,
    project_id: Optional[int] = None,
    project_name: Optional[str] = None,
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
        deployments = [
            item for item in project.work_items if (item.category == "Deployment")
        ]
        # ^^^ We will return the dates of this back to the front end to display on charts. We need to only grab
        #     the last three months of deployments for our "Current Status" metric
        three_months_ago = datetime.now() - relativedelta(months=3)
        recent_deploy_dates = [
            deployment.end_time
            for deployment in deployments
            if (deployment.end_time >= three_months_ago)
        ]

        deploy_frequency = "Yearly"  # for now

        weekly_deploys = []
        week_start = three_months_ago
        for i in range(12):  # 12 weeks in 3 months
            week_end = week_start + relativedelta(days=7)
            deploys_in_week = filter(
                lambda deploy_date: (
                    deploy_date >= week_start and deploy_date <= week_end
                ),
                recent_deploy_dates,
            )
            weekly_deploys.append(len(list(deploys_in_week)))

            week_start += relativedelta(days=7)

        for i, week in enumerate(weekly_deploys):
            print(i, "th Week had:", week, "deploys")

        if median(weekly_deploys) >= 3:
            deploy_frequency = "Daily"

        print("DEPLOYMENT FREQUENCY VALUE:", median(weekly_deploys))

        print("DEPLOYMENT FREQUENCY:", deploy_frequency)

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

    else:
        # return all project deployment frequency data in json object
        # projects = db.exec(select(Project)).all()
        pass

    return str(deploy_frequency)
