from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

# Placeholder model to for inital backend config
class IssueBase(SQLModel):
    issueTitle: str 
    date: datetime 
    time: Optional[datetime] 
    repo: str 

class Issue(IssueBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) 

class IssueRead(IssueBase):
    id: int

class IssueCreate(IssueBase):
    pass

class IssueUpdate(SQLModel):
    issueTitle: Optional[str] = None
    date: Optional[datetime] = None
    repo: Optional[str] = None
    time: Optional[datetime] = None
