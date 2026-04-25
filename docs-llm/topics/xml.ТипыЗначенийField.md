# Типы значений Field.*

Каждый параметр области (`Area.Parameter`) и поле набора данных содержат элемент `<Value>`, тип которого определяется атрибутом `pw_type`. Ниже описаны все возможные структуры значений.

---

### Field.Dataset — поле из набора данных

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
| `<FunctionName>` | Функция над датой — см. перечисление (см. topic: xml.Описание) |

---

### Field.Description — составное представление

Объединяет несколько полей в одну строку с префиксами и окончаниями. Используется когда в одной ячейке нужно вывести несколько реквизитов, например `ИНН: 7701234567, КПП: 770101001`.

```xml
<Value pw_type="Field.Description">
  <Row pw_type="Field.Description.Row" Number="1"
       Prefix="ИНН: " Ending=", ">
    <SourceField pw_type="Field.Dataset"
                 DatasetKey="..." DatasetFieldKey="..."
                 DatasetFieldName="ИНН"/>
  </Row>
  <Row pw_type="Field.Description.Row" Number="2"
       Prefix="КПП: " Ending="">
    <SourceField pw_type="Field.Dataset"
                 DatasetKey="..." DatasetFieldKey="..."
                 DatasetFieldName="КПП"/>
  </Row>
</Value>
```

Каждый элемент `Row` описывает одну часть составной строки:

| Атрибут / Элемент | Описание |
|---|---|
| `Number` | Порядковый номер части (1-based) |
| `Prefix` | Текст перед значением, например `"ИНН: "` |
| `Ending` | Текст после значения, например `", "` |
| `<SourceField>` | Источник значения — структура `Field.Dataset` |
| `<Format>` | Форматирование значения — структура `Format` |

---

##

... [truncated, используйте более узкий topic]