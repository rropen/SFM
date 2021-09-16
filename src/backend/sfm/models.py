from enum import Enum
from typing import List, Optional
from datetime import datetime, timedelta
from sqlmodel import Field, SQLModel, Relationship


class ProjectBase(SQLModel):
    name: str
    lead_name: Optional[str] = None
    lead_email: Optional[str] = None
    description: Optional[str] = None
    location: str
    repo_url: str
    on_prem: bool


class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_auth_token_hashed: str

    work_items: List["WorkItem"] = Relationship(back_populates="project")


class ProjectRead(ProjectBase):
    id: int


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    lead_name: Optional[str] = None
    lead_email: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    repo_url: Optional[str] = None
    on_prem: Optional[bool] = None


class WorkItemCategory(str, Enum):
    deployment = "Deployment"
    issue = "Issue"
    pull_request = "Pull Request"


class WorkItemBase(SQLModel):
    category: WorkItemCategory
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_open: Optional[timedelta] = None
    comments: Optional[str] = None

    project_id: Optional[int] = Field(default=None, foreign_key="project.id")


class WorkItem(WorkItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    project: Optional[Project] = Relationship(back_populates="work_items")
    commits: Optional["Commit"] = Relationship(back_populates="work_item")


class WorkItemRead(WorkItemBase):
    id: int


class WorkItemCreate(WorkItemBase):
    pass


class WorkItemUpdate(SQLModel):
    category: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    # duration_open not needed as it can be calculated and stored if given start and end
    comments: Optional[str] = None

    project_id: Optional[int] = None


class ChartData(SQLModel):
    deployment_dates: Optional[List] = None
    deployment_frequency: Optional[str] = None


class LeadTimeData(SQLModel):
    lead_time: Optional[float] = None
    color: Optional[str] = None


class CommitBase(SQLModel):
    sha: str = Field(primary_key=True)
    date: Optional[datetime] = None
    time_to_pull: Optional[int] = None
    message: Optional[str] = None
    author: Optional[str] = None
    work_item_id: Optional[int] = Field(default=None, foreign_key="workitem.id")


class Commit(CommitBase, table=True):
    work_item: Optional[WorkItem] = Relationship(back_populates="commits")


class CommitRead(CommitBase):
    pass


class CommitUpdate(SQLModel):
    date: Optional[datetime] = None
    time_to_pull: Optional[int] = None
    message: Optional[str] = None
    author: Optional[str] = None


class CommitCreate(CommitBase):
    pass
