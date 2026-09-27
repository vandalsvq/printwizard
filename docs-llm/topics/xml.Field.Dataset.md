# Field.Dataset — поле из набора данных

Это формат XML-файла макета (хранение и обмен), а не интерфейс конструктора: в форме макета то же настраивается на закладках — темы макет.*, наборы.*, запросы.*.

Подраздел темы «Типы значений Field.*» (см. topic: xml.ТипыЗначенийField).

Самый распространённый тип. Указывает на конкретное поле конкретного набора.

```xml
<Value pw_type="Field.Dataset"
       DatasetKey="d1e2f3a4-..."
       DatasetFieldKey="f1-..."
       DatasetFieldName="Номенклатура"
       IsRowField="true"
       IsQueryField="false"
       IsFunction="false">
  <!-- опционально: вложенный реквизит ссылочного поля -->
  <QueryField>Наименование</QueryField>
  <!-- опционально: функция над датой -->
  <FunctionName>BegOfMonth</FunctionName>
  <Datatypes>СправочникСсылка.Номенклатура</Datatypes>
</Value>
```

| Атрибут / Элемент | Описание |
|---|---|
| `DatasetKey` | UUID набора данных |
| `DatasetFieldKey` | UUID поля внутри набора |
| `DatasetFieldName` | Имя поля (для читаемости) |
| `IsRowField` | `true` — поле принадлежит строке коллекции (`Collection`) |
| `IsQueryField` | `true` — поле является вложенным реквизитом ссылочного поля |
| `IsFunction` | `true` — к значению применяется функция даты |
| `AggregateFunction` | Агрегатная функция: `Sum`, `Count`, `CountDistinct`, `Max`, `Min`, `Avg`, `RunningTotal`, `PageTotal`, `PercentOfTotal`. `RunningTotal` / `PageTotal` / `PercentOfTotal` — построчные накопительные значения; `PageTotal` сбрасывается на каждой логической странице и доступен только для табличных макетов |
| `JoinKey` | UUID соединения (если поле из правого набора соединения) |
| `<QueryField>` | Имя вложенного реквизита (например `Наименование` у поля `Контрагент`) |
| `<FunctionName>` | Функция над датой — см. перечисление (см. topic: xml.Field.Dataset.Functions) |

---

См. также: xml.ТипыЗначенийField, xml.Field.Dataset.Functions
