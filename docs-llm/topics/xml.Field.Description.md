# Field.Description — составное представление

Это формат XML-файла макета (хранение и обмен), а не интерфейс конструктора: в форме макета то же настраивается на закладках — темы макет.*, наборы.*, запросы.*.

Подраздел темы «Типы значений Field.*» (см. topic: xml.ТипыЗначенийField).

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

См. также: xml.ТипыЗначенийField
