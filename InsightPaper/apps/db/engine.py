from sqlmodel import create_engine
import settings

engine = create_engine(settings.VP_DATABASE)
