import asyncio
import httpx

from src.vacancies_collector import AreasCollector, VacanciesCollector


async def main():
    area_names = ["Нижний Новгород", "Москва", "Казань"]
    grades = ["Junior", "Middle", "Senior"]
    professional_roles_ids = ["96", "10"]
    vacancies = ["Data Scientist", "Аналитика данных"]
    async with httpx.AsyncClient() as client:
        for grade in grades:
            num_of_vacancies = 0
            for vacancy in vacancies:
                for area_name in area_names:
                    area_id = await AreasCollector(area_name, client).get_area_id()
                    full_vacancy = f"{grade} {vacancy}"
                    num_of_vacancies += len(
                        await VacanciesCollector(
                            area_id, full_vacancy, professional_roles_ids, client
                        ).collect_vacancies()
                    )
            print(
                f"grade - {grade}\nvacancies - {', '.join(vacancies)}\nnumber - {num_of_vacancies}\n"
            )


if __name__ == "__main__":
    asyncio.run(main())
