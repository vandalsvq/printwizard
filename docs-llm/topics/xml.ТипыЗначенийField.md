# Типы значений Field.*

Это формат XML-файла макета (хранение и обмен), а не интерфейс конструктора: в форме макета то же настраивается на закладках — темы макет.*, наборы.*, запросы.*.

Каждый параметр области (`Area.Parameter`) и поле набора данных содержат элемент `<Value>`, тип которого определяется атрибутом `pw_type`. Ниже описаны все возможные структуры значений.

---

Подробности — в отдельных темах:
- Field.Dataset — поле из набора данных (см. topic: xml.Field.Dataset)
- Field.Description — составное представление (см. topic: xml.Field.Description)
- Field.SumInWords — сумма прописью (см. topic: xml.Field.SumInWords)
- Field.QRCode — QR-код (см. topic: xml.Field.QRCode)
- Field.Function — произвольный алгоритм (см. topic: xml.Field.Function)
- Field.Attribute — дополнительное свойство (БСП) (см. topic: xml.Field.Attribute)
- Field.ContactInfo — контактная информация (БСП) (см. topic: xml.Field.ContactInfo)

См. также: xml.Field.Dataset, xml.Field.Description, xml.Field.SumInWords, xml.Field.QRCode, xml.Field.Function, xml.Field.Attribute, xml.Field.ContactInfo
