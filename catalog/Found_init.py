from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Found_Data import *

engine = create_engine('sqlite:///found.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

session.query(FoundationCName).delete()
session.query(FName).delete()
session.query(User).delete()

# Create sample users data
U1 = User(name="divya kanna",
          email="divyakanna@gmail.com")
session.add(U1)
session.commit()
print ("Successfully Add User")
C1 = FoundationCName(name="MAYBELLINE",
                     user_id=1)
session.add(C1)
session.commit()

C2 = FoundationCName(name="LAKME",
                     user_id=1)
session.add(C2)
session.commit

C3 = FoundationCName(name="L'OREAL",
                     user_id=1)
session.add(C3)
session.commit()

C4 = FoundationCName(name="M.A.C",
                     user_id=1)
session.add(C4)
session.commit()

C5 = FoundationCName(name="REVLON",
                     user_id=1)
session.add(C5)
session.commit()

C6 = FoundationCName(name="WET&WILD",
                     user_id=1)
session.add(C6)
session.commit()

F1 = FName(name="MAYBELLINE",
           shade="Natural",
           quantity="50ml",
           skintype="Normal",
           price="280"
           date=datetime.datetime.now(),
           foundationcnameid=1, user_id=1)
session.add(F1)
session.commit()

F2 = FName(name="LAKME"
           shade="Honey",
           quantity="100ml",
           skintype="Dry",
           price="220",
           date=datetime.datetime.now(),
           foundationcnameid=2, user_id=1)
session.add(F2)
session.commit()

F3 = FName(name="L'OREAL",
           shade="Warm Natural",
           quantity="100ml",
           skintype="All",
           price="300",
           date=datetime.datetime.now(),
           foundationcnameid=3, user_id=1)
session.add(F3)
session.commit()

F4 = FName(name="M.A.C",
           shade="Golden Honey",
           quantity="50ml",
           skintype="Normal",
           price="450",
           date=datetime.datetime.now(),
           foundationcnameid=4, user_id=1)
session.add(F4)
session.commit()

F5 = FName(name="REVLON",
           shade="Cool Honey",
           quantity="100ml",
           skintype="All",
           price="230",
           date=datetime.datetime.now(),
           foundationcnameid=5, user_id=1)
session.add(F5)
session.commit()

F6 = FName(name="WET&WILD",
           shade="Natural Tan",
           quantity="100ml",
           skintype="Oil",
           price="350",
           date=datetime.datetime.now(),
           foundationcnameid=6, user_id=1)
session.add(F6)
session.commit()

print("Your database has been inserted!")
