from enum import Enum
from typing import List, Optional
from datetime import datetime, timedelta
from pyasn1_modules.rfc2459 import IssuerAltName
from sqlmodel import Field, SQLModel, Relationship


class ProjectBase(SQLModel):
    name: str = Field(..., index=False)
    lead_name: Optional[str] = Field(default=None, index=False)
    lead_email: Optional[str] = Field(default=None, index=False)
    description: Optional[str] = Field(default=None, index=False)
    location: Optional[str] = Field(default=None, index=False)
    repo_url: str = Field(..., index=False)
    on_prem: Optional[bool] = Field(default=None, index=False)


class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_auth_token_hashed: str = Field(..., index=False)

    work_items: List["WorkItem"] = Relationship(back_populates="project")


class ProjectRead(ProjectBase):
    id: int


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(SQLModel):
    name: Optional[str] = Field(default=None, index=False)
    lead_name: Optional[str] = Field(default=None, index=False)
    lead_email: Optional[str] = Field(default=None, index=False)
    description: Optional[str] = Field(default=None, index=False)
    location: Optional[str] = Field(default=None, index=False)
    repo_url: Optional[str] = Field(default=None, index=False)
    on_prem: Optional[bool] = Field(default=None, index=False)


class WorkItemCategory(str, Enum):
    deployment = "Deployment"
    issue = "Issue"
    pull_request = "Pull Request"
    production_defect = "Production Defect"


class WorkItemBase(SQLModel):
    category: WorkItemCategory = Field(..., index=False)
    issue_num: Optional[int] = Field(default=None, index=False)
    start_time: Optional[datetime] = Field(default=None, index=False)
    end_time: Optional[datetime] = Field(default=None, index=False)
    duration_open: Optional[int] = Field(default=None, index=False)
    comments: Optional[str] = Field(default=None, index=False)
    failed: Optional[bool] = Field(default=None, index=False)
    project_id: Optional[int] = Field(
        default=None, foreign_key="project.id", index=False
    )


class WorkItem(WorkItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    project: Optional[Project] = Relationship(back_populates="work_items")
    commits: Optional["Commit"] = Relationship(back_populates="work_item")


class WorkItemRead(WorkItemBase):
    id: int = Field(..., index=False)


class WorkItemCreate(WorkItemBase):
    pass


class WorkItemUpdate(SQLModel):
    category: Optional[str] = Field(default=None, index=False)
    issue_num: Optional[int] = Field(default=None, index=False)
    start_time: Optional[datetime] = Field(default=None, index=False)
    end_time: Optional[datetime] = Field(default=None, index=False)
    # duration_open not needed as it can be calculated and stored if given start and end
    comments: Optional[str] = Field(default=None, index=False)
    failed: Optional[bool] = Field(default=None, index=False)
    project_id: Optional[int] = Field(default=None, index=False)


class DeploymentData(SQLModel):
    project_name: str
    deployment_dates: List
    performance: str
    deployment_dates_description: str
    performance_description: str


class LeadTimeData(SQLModel):
    lead_time: int
    time_units: str
    performance: str
    daily_commits: List
    daily_lead_times: List
    project_name: str
    lead_time_description: str
    performance_description: str
    daily_commits_description: str
    daily_lead_times_description: str


class TimeToRestoreData(SQLModel):
    time_to_restore: float
    performance: str
    daily_times_to_restore: List
    project_name: str
    time_to_restore_description: str
    performance_description: str
    daily_times_to_restore_description: str


class ChangeFailureRateData(SQLModel):
    change_failure_rate: float
    daily_change_failure_rate: List
    project_name: str
    change_failure_rate_description: str


class CommitBase(SQLModel):
    sha: str = Field(..., index=False)
    date: Optional[datetime] = Field(default=None, index=False)
    message: Optional[str] = Field(default=None, index=False)
    author: Optional[str] = Field(default=None, index=False)
    work_item_id: Optional[int] = Field(
        default=None, foreign_key="workitem.id", index=False
    )


class Commit(CommitBase, table=True):
    id: int = Field(primary_key=True)
    work_item: Optional[WorkItem] = Relationship(back_populates="commits")
    time_to_pull: int = Field(..., index=False)


class CommitRead(CommitBase):
    pass


class CommitUpdate(SQLModel):
    date: Optional[datetime] = Field(default=None, index=False)
    message: Optional[str] = Field(default=None, index=False)
    author: Optional[str] = Field(default=None, index=False)


class CommitCreate(CommitBase):
    pass


class ProductionDefect(SQLModel):
    issue: int = Field(..., index=False)
    start_time: datetime = Field(..., index=False)
    end_time: Optional[datetime] = Field(default=None, index=False)
    deployment_id: int = Field(..., foreign_key="workItem.id", index=False)
