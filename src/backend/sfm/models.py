from enum import Enum
from typing import List, Optional
from datetime import datetime, timedelta
from sqlmodel import Field, SQLModel, Relationship


class ProjectBase(SQLModel):
    name: str
    leadName: Optional[str] = None
    leadEmail: Optional[str] = None
    description: Optional[str] = None
    location: str
    repoUrl: str
    onPrem: bool


class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    projectAuthTokenHashed: str

    workItems: List["WorkItem"] = Relationship(back_populates="project")


class ProjectRead(ProjectBase):
    id: int


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    leadName: Optional[str] = None
    leadEmail: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    repoUrl: Optional[str] = None
    onPrem: Optional[bool] = None


class WorkItemCategory(str, Enum):
    deployment = "Deployment"
    issue = "Issue"
    pullRequest = "Pull Request"


class WorkItemBase(SQLModel):
    category: WorkItemCategory
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    durationOpen: Optional[timedelta] = None
    comments: Optional[str] = None

    projectId: Optional[int] = Field(default=None, foreign_key="project.id")


class WorkItem(WorkItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    project: Optional[Project] = Relationship(back_populates="workItems")
    commits: Optional["Commit"] = Relationship(back_populates="workItem")


class WorkItemRead(WorkItemBase):
    id: int


class WorkItemCreate(WorkItemBase):
    pass


class WorkItemUpdate(SQLModel):
    category: Optional[str] = None
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    # duration_open not needed as it can be calculated and stored if given start and end
    comments: Optional[str] = None

    projectId: Optional[int] = None


class MetricData(SQLModel):
    projectName: str
    deploymentDates: List
    performance: str
    deploymentDatesDescription: str
    performanceDescription: str


class LeadTimeData(SQLModel):
    lead_time: int
    time_units: str
    performance: str
    daily_commits: List
    daily_lead_times: List
    lead_time_description: str
    performance_description: str
    daily_commits_description: str
    daily_lead_times_description: str


class CommitBase(SQLModel):
    sha: str = Field(primary_key=True)
    date: Optional[datetime] = None
    message: Optional[str] = None
    author: Optional[str] = None
    workItemId: Optional[int] = Field(default=None, foreign_key="workitem.id")


class Commit(CommitBase, table=True):
    workItem: Optional[WorkItem] = Relationship(back_populates="commits")
    timeToPull: int


class CommitRead(CommitBase):
    pass


class CommitUpdate(SQLModel):
    date: Optional[datetime] = None
    message: Optional[str] = None
    author: Optional[str] = None


class CommitCreate(CommitBase):
    pass
