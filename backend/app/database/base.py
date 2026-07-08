# Import all the models so that Base.metadata can see them
from app.database.session import Base
from app.models.user import User
from app.models.upload import Upload
from app.models.transcript import Transcript
from app.models.analysis import AnalysisResult
from app.models.feedback import Feedback
from app.models.report import Report
