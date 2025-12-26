from app.domain.repositories import AbstractSurveyRepository
from app.use_cases.registration import RegistrationService

class SurveyService:
    def __init__(self, survey_repo: AbstractSurveyRepository, registration_service: RegistrationService):
        self.survey_repo = survey_repo
        self.registration_service = registration_service

    async def process_survey_answer(self, user_id: int, answer: str):
        # Save answer
        await self.survey_repo.save_answer(user_id, answer)
        # Complete registration
        await self.registration_service.complete_registration(user_id)
