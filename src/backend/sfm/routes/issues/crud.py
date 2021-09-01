from sfm.models import Meeting
from sqlalchemy.orm import Session

def get_all(db: Session, skip: int = 0, limit: int = 25):
    """Get all the meetings and return the them."""

    return db.query(Meeting).offset(skip).limit(limit).all()

def group_cost(db: Session):
    """Finds the cost of meetings with the same group ID"""
    meetings = db.query(Meeting).all()

    meeting_list = []
    for m in meetings: 
        print("Title: {}".format(m.title))
        print("Comments: {}".format(m.comment))
        meeting_list.append(m.title)
        
    return meeting_list

def create_meeting(db: Session, meeting_data):
    """Take data from request and create a new meeting in the database."""
    meeting = Meeting()
    meeting.meetingId = meeting_data.meetingId
    meeting.totalCost = meeting_data.totalCost
    meeting.time = meeting_data.time
    meeting.date = meeting_data.date
    meeting.employeeNumber = meeting_data.employeeNumber
    meeting.meetingGroup = meeting_data.meetingGroup
    meeting.powerpointSlides = meeting_data.powerpointSlides
    meeting.comment = meeting_data.comment
    meeting.title = meeting_data.title
    meeting.groupCost = meeting_data.groupCost

    db.add(meeting)
    db.commit()

    # Check the new record
    new_meeting = db.query(Meeting).filter_by(id=meeting.id).first()
    if new_meeting.meetingId == meeting_data.meetingId:
        return True  # successfully created record
    else:
        return False  # didn't store correctly


def delete_meeting(db: Session, item_id):
    """Take a meetingId (not primary key "id") and remove the row from the database."""
    db.query(Meeting).filter_by(meetingId=item_id).delete()
    db.commit()

    # Check our work
    row = db.query(Meeting).filter_by(meetingId=item_id).first()
    if row:
        return False  # Row didn't successfully delete or another one exists
    else:
        return True  # We were successful
