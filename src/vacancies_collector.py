import asyncio
import httpx

API_HH_URL = "https://api.hh.ru"


class AreasCollector:
    def __init__(self, area_name: str, http_client: httpx.AsyncClient):
        self._area_name = area_name
        self._http_client = http_client
        self._area_url = f"{API_HH_URL}/areas"
        self._country_id = 113
        self.region_id = None

    async def get_area_id(self) -> str:
        all_areas = (
            await self._http_client.get(f"{self._area_url}/{self._country_id}")
        ).json()
        self.find_area(all_areas, self._area_name)
        return self.region_id

    def find_area(self, all_areas: list | dict, area_name: str) -> None:
        if isinstance(all_areas, dict):
            if all_areas["name"] == area_name:
                self.region_id = all_areas["id"]
            else:
                self.find_area(all_areas.get("areas"), area_name)
        elif isinstance(all_areas, list):
            for area in all_areas:
                self.find_area(area, area_name)


class VacanciesCollector:
    def __init__(
        self,
        area_id: str,
        vacancy: str,
        professional_roles_ids: list[str],
        http_client: httpx.AsyncClient,
    ):
        self._area_id = area_id
        self._vacancy = vacancy
        self._professional_roles_ids = professional_roles_ids
        self._http_client = http_client
        self._vacancies_url = f"{API_HH_URL}/vacancies"
        self._per_page = 100
        self._pages = 20

    async def get_vacancies(self, vacancy: str, role: str, page: int):
        result = None
        for _ in range(10):
            result = await self._http_client.get(
                self._vacancies_url,
                params={
                    "area": self._area_id,
                    "per_page": self._per_page,
                    "professional_roles": role,
                    "text": vacancy,
                    "page": page,
                },
            )
            if result.status_code != 400:
                return result
        return result

    async def collect_vacancies(self):
        result = []
        for role in self._professional_roles_ids:
            tasks = [
                self.get_vacancies(self._vacancy, role, i) for i in range(self._pages)
            ]
            current_results = await asyncio.gather(*tasks, return_exceptions=True)
            result.extend(
                request.json().get("items")
                for request in current_results
                if not isinstance(request, Exception) and request.status_code == 200
            )
        return sum(result, [])
