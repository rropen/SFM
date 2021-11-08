import logging
from datetime import datetime, timedelta
from statistics import median
from sfm.config import get_settings
from sfm.routes.work_items import crud
from sfm.routes.metrics import crud as metrics_crud
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
from sfm.logger import create_logger


app_settings = get_settings()


logger = create_logger(__name__)

router = APIRouter()


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
    return metrics_crud.get_deployments_crud(db, project_name, project_id)


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
    return metrics_crud.lead_time_to_change_crud(db, project_name, project_id)


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
    return metrics_crud.time_to_restore_crud(db, project_name, project_id)


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
    return metrics_crud.change_failure_rate_crud(db, project_name, project_id)
