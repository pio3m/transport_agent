import os
import json
import requests
from typing import Dict, Any
from datetime import datetime, date, timedelta


class LLMAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set LLM_API_KEY environment variable or pass it to the constructor.")
        
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def parse_transport_request(self, prompt: str) -> Dict[str, Any]:
        """
        Send the transport request prompt to OpenAI API and get structured data in return.
        
        Args:
            prompt (str): The transport request text to parse
            
        Returns:
            Dict[str, Any]: Structured data extracted from the prompt
        """
        system_message = """
        Jesteś ekspertem w analizie zleceń transportowych. Twoim zadaniem jest wyciągnięcie ustrukturyzowanych 
        danych z tekstu opisującego zlecenie transportowe. Zwróć dane w formacie JSON zawierające następujące pola:
        
        1. vehicle_type: Typ pojazdu (bus / solówka / naczepa / brak)
        2. cargo_items: Lista ładunków, każdy zawierający:
           - width: szerokość w metrach
           - length: długość w metrach
           - height: wysokość w metrach
           - quantity: ilość sztuk
        3. pickup_postal_code: Kod pocztowy miejsca odbioru
        4. delivery_postal_code: Kod pocztowy miejsca dostawy
        5. pickup_date: Data odbioru (format YYYY-MM-DD), uwzględnij określenia jak "jutro", "za 3 dni" itp.
        6. delivery_date: Data dostawy (format YYYY-MM-DD)
        7. is_urgent: Czy zlecenie jest pilne (true/false)
        8. is_stackable: Czy ładunki można piętrować (true/false)
        
        Odpowiadaj TYLKO w prawidłowym formacie JSON, bez dodatkowych komentarzy.
        """
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,  # Niska temperatura dla bardziej deterministycznych odpowiedzi
            "response_format": {"type": "json_object"}  # Wymuszenie odpowiedzi w JSON
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Ekstrahuj odpowiedź w formacie JSON
            parsed_json_str = result["choices"][0]["message"]["content"]
            parsed_data = json.loads(parsed_json_str)
            
            # Przetwarzanie dat względnych (jutro, za X dni)
            self._process_dates(parsed_data)
            
            return parsed_data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing JSON response: {str(e)}")
    
    def _process_dates(self, data: Dict[str, Any]) -> None:
        """
        Process relative dates in the parsed data.
        
        Args:
            data (Dict[str, Any]): The parsed data containing date information
        """
        today = datetime.now().date()
        
        # Funkcja pomocnicza do przetwarzania pojedynczej daty
        def process_date(date_str):
            if not date_str:
                return None
            
            try:
                # Jeśli to już format daty YYYY-MM-DD, zwróć jako obiekt date
                return date.fromisoformat(date_str)
            except ValueError:
                pass
            
            # Przetwarzanie dat względnych
            date_str = date_str.lower()
            if "jutro" in date_str:
                return today + timedelta(days=1)
            elif "pojutrze" in date_str:
                return today + timedelta(days=2)
            elif "za " in date_str and " dni" in date_str:
                # Próba wyciągnięcia liczby dni, np. "za 3 dni"
                try:
                    days_part = date_str.split("za ")[1].split(" dni")[0]
                    days = int(days_part)
                    return today + timedelta(days=days)
                except (IndexError, ValueError):
                    pass
            
            # Jeśli nie udało się przetworzyć, zwróć oryginalną wartość
            return date_str
        
        # Przetwórz daty w danych
        if "pickup_date" in data and data["pickup_date"]:
            processed_date = process_date(data["pickup_date"])
            if isinstance(processed_date, date):
                data["pickup_date"] = processed_date.isoformat()
        
        if "delivery_date" in data and data["delivery_date"]:
            processed_date = process_date(data["delivery_date"])
            if isinstance(processed_date, date):
                data["delivery_date"] = processed_date.isoformat()