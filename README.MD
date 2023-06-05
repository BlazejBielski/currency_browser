# Currency Browser

## Krótki opis projektu.
1. Zastosowane technologie:
   - python
   - django
   - drf
   - chart.js (front)
2. Zadanie można było rozwiązać na wiele różnych sposobów, pierwotnie projekt był oparty na czystym Django, ostatecznie projekt korzysta z drf i przekazuje dane do skryptu wyświetlającego wykresy na bazie chart.js
3. W aplikacji currency jest customowa migracja, która zaczytuje do bazy danych wszystkie waluty znajdujące się w tabeli A NBP. Zastosowano to rozwiązanie po to, żeby przy odpaleniu aplikacji nie witał użytkownika pusty ekran.
4. Starałem się, aby nazwy funkcji były deskryptywne.
5. Rozwiązanie nie jest przeznaczone na produkcję. Optymalnie byłoby wczytać np. ostatnie 20 lat kursów walut i ściągać tylko brakujące dane. Projekt należałoby też skonteneryzować. Niemniej mam nadzieję, że wyczerpuje on znamiona projektu pokazowego na stanowisko Python Developera.