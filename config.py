from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT : str = 'development'
    # this is the default variable if it doesnt find any variable named 'ENVIRONMENT'

    GROQ_API_KEY : str 
    #this has no fallback default, if couldnt find the var then the app crashes

    model_config = SettingsConfigDict(env_file='.env')
    #model_config is an fixed built in parameter, must write it like that
    #this tell the model what file to look for

env_config = Settings()
#this is the object that contains all our sensitive info from the .env file'
#all scripts within the app can access this -> optimal













