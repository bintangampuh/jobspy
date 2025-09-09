from database import engine, Base
import models

print("Attempting to create all database tables...")
Base.metadata.create_all(bind=engine)

print("Tables created successfully (if they did not already exist). Please check your Supabase dashboard.")