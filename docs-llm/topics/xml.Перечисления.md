# Перечисления

Это формат XML-файла макета (хранение и обмен), а не интерфейс конструктора: в форме макета то же настраивается на закладках — темы макет.*, наборы.*, запросы.*.

Одно и то же значение зовётся по-разному в контракте и в интерфейсе: в XML лежит `Single`, в конструкторе то же значение называется `БезПовторений`, а в выпадающем списке подписано «Без повторений». Колонка **В конструкторе** даёт имя, под которым значение живёт в конструкторе, и следом в кавычках — подпись из списка, если она отличается от имени. Ассистент отвечает пользователю про интерфейс, а читает контракт, поэтому здесь и то и другое.

Подробности — в отдельных темах:
- Kind — вид объекта (см. topic: xml.Kind)
- Dataset.Type — тип набора (см. topic: xml.Dataset.Type)
- Area.Method — способ вывода (см. topic: xml.Area.Method)
- Area.Settings — настройка вывода (см. topic: xml.Area.Settings)
- Filter.Item.ComparisonTypes — виды сравнения (см. topic: xml.Filter.Item.ComparisonTypes)
- QRCode.Type — тип QR-кода (см. topic: xml.QRCode.Type)
- Event.Name — события жизненного цикла (см. topic: xml.Event.Name)
- Query.ResultType — тип результата запроса (см. topic: xml.Query.ResultType)
- Parameter.Type — тип входного параметра (см. topic: xml.Parameter.Type)
- Field.Dataset.Functions — функции дат (см. topic: xml.Field.Dataset.Functions)

См. также: xml.Kind, xml.Dataset.Type, xml.Area.Method, xml.Area.Settings, xml.Filter.Item.ComparisonTypes, xml.QRCode.Type, xml.Event.Name, xml.Query.ResultType, xml.Parameter.Type, xml.Field.Dataset.Functions
