# Field.SumInWords — сумма прописью

Это формат XML-файла макета (хранение и обмен), а не интерфейс конструктора: в форме макета то же настраивается на закладках — темы макет.*, наборы.*, запросы.*.

Подраздел темы «Типы значений Field.*» (см. topic: xml.ТипыЗначенийField).

Выводит числовое значение прописью с указанием валюты. Например: `Пятнадцать тысяч рублей 00 копеек`.

```xml
<Value pw_type="Field.SumInWords">
  <NumberField pw_type="Field.Dataset"
               DatasetKey="..." DatasetFieldKey="..."
               DatasetFieldName="СуммаДокумента"/>
  <CurrencyField pw_type="Field.Dataset"
                 DatasetKey="..." DatasetFieldKey="..."
                 DatasetFieldName="Валюта"/>
  <CurrencyDefault>RUB</CurrencyDefault>
  <NoFractions>false</NoFractions>
  <FormatString/>
  <Parameters/>
</Value>
```

| Элемент | Описание |
|---|---|
| `<NumberField>` | Источник числового значения суммы — структура `Field.Dataset` |
| `<CurrencyField>` | Источник валюты — структура `Field.Dataset`. Если не указан, используется `CurrencyDefault` |
| `<CurrencyDefault>` | Валюта по умолчанию в ISO 4217: `RUB`, `USD`, `EUR`, `KZT` и др. |
| `<NoFractions>` | `true` — не выводить копейки / центы |
| `<FormatString>` | Строка форматирования (переопределяет стандартный вывод) |
| `<Parameters>` | Дополнительные параметры функции прописью |

---

См. также: xml.ТипыЗначенийField
