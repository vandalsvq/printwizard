# Field.ContactInfo — контактная информация (БСП)

Это формат XML-файла макета (хранение и обмен), а не интерфейс конструктора: в форме макета то же настраивается на закладках — темы макет.*, наборы.*, запросы.*.

Подраздел темы «Типы значений Field.*» (см. topic: xml.ТипыЗначенийField).

Значение контактной информации объекта из подсистемы БСП («Контактная информация»): телефон, адрес, email и т.п.

```xml
<Value pw_type="Field.ContactInfo"
       KindParentId="..."
       KindParentName="Контрагенты"
       KindId="..."
       KindName="ЮридическийАдрес"
       KindDescription="Юридический адрес">
  <KindIdDev>ЮридическийАдрес</KindIdDev>
  <KindNamePredefined/>
  <SourceField pw_type="Field.Dataset"
               DatasetKey="..." DatasetFieldKey="..."
               DatasetFieldName="Контрагент"/>
  <PeriodField pw_type="Field.Dataset"
               DatasetKey="..." DatasetFieldKey="..."
               DatasetFieldName="Дата"/>
</Value>
```

| Атрибут / Элемент | Описание |
|---|---|
| `KindParentId` / `KindParentName` | Владелец вида контактной информации |
| `KindId` / `KindName` | Идентификатор и имя вида (например `ЮридическийАдрес`) |
| `KindDescription` | Представление для пользователя |
| `<SourceField>` | Поле-объект, для которого запрашивается контактная информация |
| `<PeriodField>` | Поле с датой актуальности (опционально) |

---

См. также: xml.ТипыЗначенийField
