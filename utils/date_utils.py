import re
from datetime import datetime, date, timedelta

def polish_weekday_to_index(weekday_name: str) -> int:
    weekdays = {
        "poniedziałek": 0,
        "wtorek": 1,
        "środa": 2,
        "czwartek": 3,
        "piątek": 4,
        "sobota": 5,
        "niedziela": 6
    }
    return weekdays.get(weekday_name.lower(), -1)

def process_polish_date(date_str: str, reference_date: date = None) -> str:
    if not date_str:
        return date_str

    if reference_date is None:
        reference_date = datetime.now().date()

    try:
        return date.fromisoformat(date_str).isoformat()
    except ValueError:
        pass

    date_str = date_str.lower().strip()

    if "jutro" in date_str:
        return (reference_date + timedelta(days=1)).isoformat()
    elif "pojutrze" in date_str:
        return (reference_date + timedelta(days=2)).isoformat()
    elif "następnego dnia" in date_str or "następny dzień" in date_str:
        return (reference_date + timedelta(days=2)).isoformat()
    elif "za tydzień" in date_str:
        return (reference_date + timedelta(weeks=1)).isoformat()
    elif "za dwa tygodnie" in date_str:
        return (reference_date + timedelta(weeks=2)).isoformat()
    elif match := re.search(r"za (\d+) dni", date_str):
        days = int(match.group(1))
        return (reference_date + timedelta(days=days)).isoformat()
    elif match := re.search(r"w przyszł[ayą] (poniedziałek|wtorek|środę|czwartek|piątek|sobotę|niedzielę)", date_str):
        target_day = polish_weekday_to_index(match.group(1))
        if target_day >= 0:
            # Zawsze przesuwamy do kolejnego tygodnia
            days_ahead = ((target_day - reference_date.weekday()) + 7) % 7
            days_ahead = days_ahead + 7 if days_ahead == 0 else days_ahead + 7
            return (reference_date + timedelta(days=days_ahead)).isoformat()
    elif match := re.search(r"w (poniedziałek|wtorek|środę|czwartek|piątek|sobotę|niedzielę)", date_str):
        target_day = polish_weekday_to_index(match.group(1))
        if target_day >= 0:
            days_ahead = (target_day - reference_date.weekday() + 7) % 7 or 7
            return (reference_date + timedelta(days=days_ahead)).isoformat()

    return date_str
